#!/usr/bin/env python3
"""
tools/dump_spc.py - Secret of Evermore SPC700 music dumper

Builds a playable .spc for every music track by doing what the game does:
the ROM's own sound driver is run in a small SPC700 interpreter while this
script plays the 65816 side of the port protocol. The snapshot is taken the
moment the driver acknowledges the "play" command, so a player starts the
track from its first tick.

Verified against the 72 reference rips in "Secret of Evermore (EMU)": every
named track lines up with its reference (time-aligned spectrogram cosine
0.92-0.995, offset 0.0 s for most; see --emu-dir).

ROM facts (verified by disassembly of bank $8C and by running the driver):
- $81:80DC  IPL block list: [len:16][dest:16] data..., len 0 ends. One block:
            $17E0 bytes of driver -> SPC $0700, entered at $0700.
- $81:9900  music count ($46), $81:9901 sound-effect count ($5A).
- $81:9903  71 x 24-bit pointers to packages. Package = [count:16] then
            count x [len:16][src:24][spc_dest:16]. Every read walks bank upper
            halves only: past $xx:FFFF it continues at the next bank's $8000.
- $81:99D8  music -> package table (music M uses package M+1).
- $81:9A1E  sound effect -> package table (0 = none needed).
- Commands ($8C:81FD): $2143 = command, $2142 = rolling counter (never 0),
            $2140/41 = parameter. The driver echoes the counter on $2142.
    $0E        jump to the IPL ROM (clears SPC $01-$EF), then a package is
               streamed ($8C:805B) and the driver restarts at $0700
    $02        sent after every package upload
    $1C $8080, $1A $0000   sent before a music change ($8C:828F)
    $06 M      play music M
    $04 S      play sound effect S ($8C:82E3)
    $28 V      music volume ($8C:8619 fades it)
  Boot ($8C:801F): IPL driver, $0E + package 0, $02.
  Music M ($8C:828F): $1C, $1A, [$0E + package M+1, $02 if not loaded], $06 M.

The reference rips use another build of the same driver (relocated code and
zero page), so ARAM is compared by sound, not by bytes. Sample and sequence
data match the references byte for byte.
"""

import argparse
import ctypes
import datetime
import glob
import os
import re
import struct
import sys
import wave

DEFAULT_ROM = "Secret of Evermore (U) [!].smc"
DEFAULT_EMU_DIR = "/Users/v/Downloads/Secret of Evermore (EMU)"

DRIVER_BLOCK = 0x0180DC
MUSIC_COUNT = 0x019900
PACKAGE_POINTERS = 0x019903
MUSIC_PACKAGE = 0x0199D8
SFX_PACKAGE = 0x019A1E

CMD_PLAY_SFX, CMD_PLAY_MUSIC, CMD_UPLOAD = 0x04, 0x06, 0x0E
CMD_AFTER_UPLOAD, CMD_STOP_A, CMD_STOP_B, CMD_VOLUME = 0x02, 0x1C, 0x1A, 0x28

# Music id -> reference track name, each confirmed by compare_all against the
# reference rips. None = nothing to dump.
MUSIC = {
    0x00: "01 Main Title", 0x01: "19 Battle with Thraxx", 0x02: "33 In the Arena",
    0x03: "63 Escape from Evermore", 0x04: "64 Return to Podunk",
    0x05: "12 Village on the Plateau", 0x06: "24 Within the Volcano",
    0x07: "22 Swamplands", 0x08: "10 Southern Jungle", 0x09: "17 Bugmuck Tar Pits",
    0x0A: "29 Desert of Doom", 0x0B: "53 Queen Bluegarden", 0x0C: "56 High in the Sky",
    0x0D: "59 Control Room", 0x0E: "38 Hall of Collosia", 0x0F: "36 Horace Highwater",
    0x10: "23 Major Enemy", 0x11: "18 Merchant in the Cave",
    0x12: "21 Elephant Graveyard", 0x13: "28 Pirates of Crustacia",
    0x14: "30 Lively Nobilia Marketplace", 0x15: "02 Menu", 0x16: "05 Machinery",
    0x17: "99 Game Over", 0x18: "11 Raptor Attack!", 0x19: "08 Victory Fanfare",
    0x1A: "99 Good Night", 0x1B: "27 The Seashore", 0x1C: "03 Many Years Ago...",
    0x1D: "60 The Professor's Room", 0x1E: "32 Quiet Plaza",
    0x1F: "57 Omnitopia Surface", 0x20: "31 Storekeepers", 0x21: "37 Great Pyramid",
    0x22: "41 Underground Path", 0x23: "20 Hidden River", 0x24: "65 Staff Roll",
    0x25: "04 A Boy and His Dog", 0x26: "99 Engine Rumble",
    # Package 0x28 carries samples for sound effects; its sequence is empty
    # (F2 7F FA 00 F0) and the driver keys nothing on.
    0x27: None,
    # No reference rip. Sounds close to Major Enemy (0x10) but is not it.
    0x28: "xx Unused 0x28",
    0x29: "35 Palace Fountains", 0x2A: "13 Fire Eyes", 0x2B: "48 Puppet Show",
    0x2C: "07 Minor Minion", 0x2D: "09 Distant Wind", 0x2E: "40 Death of a Minotaur",
    0x2F: "42 Fields of Gothica", 0x30: "51 City of Ebony", 0x31: "26 Over the Waterfall",
    0x32: "39 Darkness of the Temple", 0x33: "50 Dark Forest", 0x34: "43 City of Ivory",
    0x35: "58 Omnitopia Hallways", 0x36: "15 Quicksand Fields",
    0x37: "54 Tinker Tinderbox", 0x38: "52 Deserted Castle", 0x39: "49 Dank Dungeon",
    0x3A: "46 Regal Castle", 0x3B: "44 Freak Show!!!", 0x3C: "06 Item Fanfare",
    0x3D: "14 Northern Jungle", 0x3E: "47 Lonely Halls", 0x3F: "61 Dark Greenhouse",
    0x40: "34 Vigor the Indestructible!", 0x41: "45 Racing Pigs!",
    0x42: "55 Collapse of Ivor Tower", 0x43: "25 Volcano Pipes",
    0x44: "62 Final Battle ~ Carltron", 0x45: "99 Intruder Alarm",
}

# Reference tracks that are not a plain music id: (name, music, volume, sfx).
EXTRAS = [
    # Distant Wind at music volume $30 (the reference matches at that level).
    ("16 Windy Cave", 0x2D, 0x30, None),
    ("99 Explosion", None, None, 0x42),
    ("99 Applause", None, None, 0x56),
    ("99 Takeoff!", None, None, 0x3B),
]


# ---------------------------------------------------------------------------
# ROM packages
# ---------------------------------------------------------------------------

def read_upper(rom, cur, n):
    """Reads n bytes the way the game's copy loops do: bank upper halves only."""
    out = bytearray()
    while n > 0:
        k = min(n, ((cur | 0xFFFF) + 1) - cur)
        out += rom[cur:cur + k]
        n -= k
        cur += k
        if (cur & 0xFFFF) == 0:
            cur += 0x8000
    if (cur & 0xFFFF) == 0:
        cur += 0x8000
    return out, cur


def package_records(rom, package):
    """[(spc_dest, bytes)] of one package, in upload order."""
    p = PACKAGE_POINTERS + package * 3
    cur = (rom[p] | rom[p + 1] << 8 | rom[p + 2] << 16) & 0x3FFFFF
    head, cur = read_upper(rom, cur, 2)
    records = []
    for _ in range(head[0] | head[1] << 8):
        r, cur = read_upper(rom, cur, 7)
        length = r[0] | r[1] << 8
        src = (r[2] | r[3] << 8 | r[4] << 16) & 0x3FFFFF
        data, _ = read_upper(rom, src, length)
        records.append((r[5] | r[6] << 8, data))
    return records


def driver_blocks(rom):
    """[(spc_dest, bytes)] of the IPL block list at $81:80DC, and the entry point."""
    blocks, cur = [], DRIVER_BLOCK
    while True:
        length = rom[cur] | rom[cur + 1] << 8
        dest = rom[cur + 2] | rom[cur + 3] << 8
        if length == 0:
            return blocks, dest
        blocks.append((dest, rom[cur + 4:cur + 4 + length]))
        cur += 4 + length


# ---------------------------------------------------------------------------
# SPC700 interpreter: CPU, timers and the DSP register file (no audio)
# ---------------------------------------------------------------------------

FN, FV, FP, FB, FH, FI, FZ, FC = 0x80, 0x40, 0x20, 0x10, 0x08, 0x04, 0x02, 0x01

# Approximate cycles per opcode; only used to clock the timers.
CYCLES = [
    2, 8, 4, 5, 3, 4, 3, 6, 2, 6, 5, 4, 5, 4, 6, 8, 2, 8, 4, 5, 4, 5, 5, 6, 5, 5, 6, 5, 2, 2, 4, 6,
    2, 8, 4, 5, 3, 4, 3, 6, 2, 6, 5, 4, 5, 4, 5, 4, 2, 8, 4, 5, 4, 5, 5, 6, 5, 5, 6, 5, 2, 2, 3, 8,
    2, 8, 4, 5, 3, 4, 3, 6, 2, 6, 4, 4, 5, 4, 6, 6, 2, 8, 4, 5, 4, 5, 5, 6, 5, 5, 4, 5, 2, 2, 4, 3,
    2, 8, 4, 5, 3, 4, 3, 6, 2, 6, 4, 4, 5, 4, 5, 5, 2, 8, 4, 5, 4, 5, 5, 6, 5, 5, 5, 5, 2, 2, 3, 6,
    2, 8, 4, 5, 3, 4, 3, 6, 2, 6, 5, 4, 5, 2, 4, 5, 2, 8, 4, 5, 4, 5, 5, 6, 5, 5, 5, 5, 2, 2, 12, 5,
    3, 8, 4, 5, 3, 4, 3, 6, 2, 6, 4, 4, 5, 2, 4, 4, 2, 8, 4, 5, 4, 5, 5, 6, 5, 5, 5, 5, 2, 2, 3, 4,
    3, 8, 4, 5, 4, 5, 4, 7, 2, 5, 6, 4, 5, 2, 4, 9, 2, 8, 4, 5, 5, 6, 6, 7, 4, 5, 5, 5, 2, 2, 6, 3,
    2, 8, 4, 5, 3, 4, 3, 6, 2, 4, 5, 3, 4, 3, 4, 3, 2, 8, 4, 5, 4, 5, 5, 6, 3, 4, 5, 4, 2, 2, 4, 3,
]

IPL_ROM = bytes.fromhex(
    "CDEFBDE800C61DD0FC8FAAF48FBBF578CCF4D0FB2F19EBF4D0FC7EF4D00BE4F5CBF4"
    "D700FCD0F3AB0110EF7EF410EBBAF6DA00BAF4C4F4DD5DD0DB1F0000C0FF")
IPL_WAIT_PC = 0xFFCF    # IPL loop waiting for the $CC that starts a transfer


class SPC700:
    def __init__(self):
        self.ram = bytearray(0x10000)
        self.dsp = bytearray(128)
        self.a = self.x = self.y = 0
        self.sp, self.psw, self.pc = 0xEF, 0x02, 0xFFC0
        self.port_in = [0, 0, 0, 0]     # what the SPC reads at $F4-$F7
        self.port_out = [0, 0, 0, 0]    # what the 65816 reads at $2140-$2143
        self.control = 0x80
        self.dsp_addr = 0
        self.t_target = [0, 0, 0]
        self.t_counter = [0, 0, 0]
        self.t_div = [0, 0, 0]
        self.t_phase = [0, 0, 0]

    # ---- memory ----------------------------------------------------------
    def rd(self, a):
        a &= 0xFFFF
        if 0xF0 <= a <= 0xFF:
            if a == 0xF3:
                return self.dsp[self.dsp_addr & 0x7F]
            if a == 0xF2:
                return self.dsp_addr
            if 0xF4 <= a <= 0xF7:
                return self.port_in[a - 0xF4]
            if a >= 0xFD:
                v = self.t_counter[a - 0xFD]
                self.t_counter[a - 0xFD] = 0
                return v
            return 0
        if a >= 0xFFC0 and self.control & 0x80:
            return IPL_ROM[a - 0xFFC0]
        return self.ram[a]

    def wr(self, a, v):
        a &= 0xFFFF
        v &= 0xFF
        if 0xF0 <= a <= 0xFF:
            if a == 0xF1:
                for t in range(3):
                    if v & (1 << t) and not self.control & (1 << t):
                        self.t_counter[t] = self.t_div[t] = 0
                if v & 0x10:
                    self.port_in[0] = self.port_in[1] = 0
                if v & 0x20:
                    self.port_in[2] = self.port_in[3] = 0
                self.control = v
            elif a == 0xF2:
                self.dsp_addr = v
            elif a == 0xF3:
                if self.dsp_addr < 0x80:
                    self.dsp[self.dsp_addr] = 0 if self.dsp_addr == 0x7C else v
            elif 0xF4 <= a <= 0xF7:
                self.port_out[a - 0xF4] = v
            elif 0xFA <= a <= 0xFC:
                self.t_target[a - 0xFA] = v
        self.ram[a] = v

    def tick(self, cycles):
        for t in range(3):
            if not self.control & (1 << t):
                continue
            self.t_phase[t] += cycles
            period = 16 if t == 2 else 128
            while self.t_phase[t] >= period:
                self.t_phase[t] -= period
                self.t_div[t] = (self.t_div[t] + 1) & 0xFF
                if self.t_div[t] == self.t_target[t]:   # target 0 = 256
                    self.t_div[t] = 0
                    self.t_counter[t] = (self.t_counter[t] + 1) & 0x0F

    def rw(self, a):
        return self.rd(a) | (self.rd(a + 1) << 8)

    def dp(self, o):
        return (o & 0xFF) | (0x100 if self.psw & FP else 0)

    def rdw_dp(self, o):
        return self.rd(self.dp(o)) | (self.rd(self.dp((o + 1) & 0xFF)) << 8)

    def fetch(self):
        v = self.rd(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return v

    def fetchw(self):
        lo = self.fetch()
        return lo | (self.fetch() << 8)

    def push(self, v):
        self.ram[0x100 | self.sp] = v & 0xFF
        self.sp = (self.sp - 1) & 0xFF

    def pop(self):
        self.sp = (self.sp + 1) & 0xFF
        return self.ram[0x100 | self.sp]

    # ---- flags / ALU -----------------------------------------------------
    def nz(self, v):
        self.psw = (self.psw & ~(FN | FZ)) | (v & 0x80) | (0 if v & 0xFF else FZ)
        return v & 0xFF

    def nz16(self, v):
        self.psw = (self.psw & ~(FN | FZ)) | (FN if v & 0x8000 else 0) | (0 if v else FZ)

    def setf(self, f, cond):
        self.psw = (self.psw | f) if cond else (self.psw & ~f & 0xFF)

    def adc(self, a, b):
        c = self.psw & FC
        r = a + b + c
        self.setf(FV, (~(a ^ b) & (a ^ r)) & 0x80)
        self.setf(FH, ((a & 0xF) + (b & 0xF) + c) > 0xF)
        self.setf(FC, r > 0xFF)
        return self.nz(r)

    def cmp(self, a, b):
        self.setf(FC, a >= b)
        self.nz((a - b) & 0xFF)

    def alu(self, kind, a, b):
        if kind == 0:
            return self.nz(a | b)
        if kind == 1:
            return self.nz(a & b)
        if kind == 2:
            return self.nz(a ^ b)
        if kind == 3:
            self.cmp(a, b)
            return None
        if kind == 4:
            return self.adc(a, b)
        return self.adc(a, b ^ 0xFF)

    def shift(self, kind, v):
        """ASL ROL LSR ROR DEC INC, by row pair."""
        c = self.psw & FC
        if kind == 0:
            self.setf(FC, v & 0x80)
            return self.nz(v << 1)
        if kind == 1:
            self.setf(FC, v & 0x80)
            return self.nz((v << 1) | c)
        if kind == 2:
            self.setf(FC, v & 1)
            return self.nz(v >> 1)
        if kind == 3:
            self.setf(FC, v & 1)
            return self.nz((v >> 1) | (c << 7))
        return self.nz(v - 1 if kind == 4 else v + 1)

    def branch(self, cond):
        r = self.fetch()
        if cond:
            self.pc = (self.pc + (r - 256 if r & 0x80 else r)) & 0xFFFF
            return 2
        return 0

    def call(self, target):
        self.push(self.pc >> 8)
        self.push(self.pc)
        self.pc = target

    # ---- execute ---------------------------------------------------------
    def step(self):
        pc0 = self.pc
        op = self.fetch()
        self.tick(CYCLES[op] + (self.execute(op, pc0) or 0))

    def execute(self, op, pc0):
        hi, lo = op >> 4, op & 0xF
        X, Y = self.x, self.y
        if hi <= 0xB and 4 <= lo <= 9:          # OR AND EOR CMP ADC SBC
            kind, odd = hi >> 1, hi & 1
            if lo == 4:
                b = self.rd(self.dp(self.fetch() + (X if odd else 0)))
            elif lo == 5:
                b = self.rd(self.fetchw() + (X if odd else 0))
            elif lo == 6:
                b = self.rd(self.fetchw() + Y) if odd else self.rd(self.dp(X))
            elif lo == 7:
                o = self.fetch()
                b = self.rd(self.rdw_dp(o) + Y) if odd else self.rd(self.rdw_dp((o + X) & 0xFF))
            elif lo == 8 and odd:               # dp,#imm
                imm = self.fetch()
                d = self.dp(self.fetch())
                r = self.alu(kind, self.rd(d), imm)
                if r is not None:
                    self.wr(d, r)
                return None
            elif lo == 8:
                b = self.fetch()
            else:                               # dp,dp / (X),(Y)
                if odd:
                    b, d = self.rd(self.dp(Y)), self.dp(X)
                else:
                    b = self.rd(self.dp(self.fetch()))
                    d = self.dp(self.fetch())
                r = self.alu(kind, self.rd(d), b)
                if r is not None:
                    self.wr(d, r)
                return None
            r = self.alu(kind, self.a, b)
            if r is not None:
                self.a = r
            return None
        if lo == 1:                             # TCALL n
            self.call(self.rw(0xFFDE - 2 * hi))
            return None
        if lo == 2:                             # SET1 / CLR1
            d = self.dp(self.fetch())
            bit = 1 << (hi >> 1)
            v = self.rd(d)
            self.wr(d, (v & ~bit) if hi & 1 else (v | bit))
            return None
        if lo == 3:                             # BBS / BBC
            v = self.rd(self.dp(self.fetch()))
            bit = v & (1 << (hi >> 1))
            return self.branch(not bit if hi & 1 else bit)
        if lo == 0:
            if hi == 0:
                return None
            if not hi & 1:
                if hi == 2: self.psw &= ~FP & 0xFF
                elif hi == 4: self.psw |= FP
                elif hi == 6: self.psw &= ~FC & 0xFF
                elif hi == 8: self.psw |= FC
                elif hi == 0xA: self.psw |= FI
                elif hi == 0xC: self.psw &= ~FI & 0xFF
                else: self.psw &= ~(FV | FH) & 0xFF
                return None
            # BPL BMI BVC BVS BCC BCS BNE BEQ
            flag = (FN, FV, FC, FZ)[hi >> 2]
            return self.branch(bool(self.psw & flag) == bool(hi & 2))
        if op == 0xC4: self.wr(self.dp(self.fetch()), self.a); return None
        if op == 0xD4: self.wr(self.dp(self.fetch() + X), self.a); return None
        if op == 0xE4: self.a = self.nz(self.rd(self.dp(self.fetch()))); return None
        if op == 0xF4: self.a = self.nz(self.rd(self.dp(self.fetch() + X))); return None
        if op == 0xC5: self.wr(self.fetchw(), self.a); return None
        if op == 0xD5: self.wr(self.fetchw() + X, self.a); return None
        if op == 0xE5: self.a = self.nz(self.rd(self.fetchw())); return None
        if op == 0xF5: self.a = self.nz(self.rd(self.fetchw() + X)); return None
        if op == 0xC6: self.wr(self.dp(X), self.a); return None
        if op == 0xD6: self.wr(self.fetchw() + Y, self.a); return None
        if op == 0xE6: self.a = self.nz(self.rd(self.dp(X))); return None
        if op == 0xF6: self.a = self.nz(self.rd(self.fetchw() + Y)); return None
        if op == 0xC7: self.wr(self.rdw_dp((self.fetch() + X) & 0xFF), self.a); return None
        if op == 0xD7: self.wr(self.rdw_dp(self.fetch()) + Y, self.a); return None
        if op == 0xE7: self.a = self.nz(self.rd(self.rdw_dp((self.fetch() + X) & 0xFF))); return None
        if op == 0xF7: self.a = self.nz(self.rd(self.rdw_dp(self.fetch()) + Y)); return None
        if op == 0xC8: self.cmp(X, self.fetch()); return None
        if op == 0xD8: self.wr(self.dp(self.fetch()), X); return None
        if op == 0xE8: self.a = self.nz(self.fetch()); return None
        if op == 0xF8: self.x = self.nz(self.rd(self.dp(self.fetch()))); return None
        if op == 0xC9: self.wr(self.fetchw(), X); return None
        if op == 0xD9: self.wr(self.dp(self.fetch() + Y), X); return None
        if op == 0xE9: self.x = self.nz(self.rd(self.fetchw())); return None
        if op == 0xF9: self.x = self.nz(self.rd(self.dp(self.fetch() + Y))); return None
        if lo == 0xA:
            return self.execute_a(op, hi)
        if op == 0xCB: self.wr(self.dp(self.fetch()), Y); return None
        if op == 0xDB: self.wr(self.dp(self.fetch() + X), Y); return None
        if op == 0xEB: self.y = self.nz(self.rd(self.dp(self.fetch()))); return None
        if op == 0xFB: self.y = self.nz(self.rd(self.dp(self.fetch() + X))); return None
        if op == 0xCC: self.wr(self.fetchw(), Y); return None
        if op == 0xEC: self.y = self.nz(self.rd(self.fetchw())); return None
        if lo == 0xB or (lo == 0xC and not hi & 1):   # shifts / DEC / INC on memory
            d = self.dp(self.fetch() + (X if hi & 1 else 0)) if lo == 0xB else self.fetchw()
            self.wr(d, self.shift(hi >> 1, self.rd(d)))
            return None
        if lo == 0xC:
            if op == 0xDC: self.y = self.nz(Y - 1)
            elif op == 0xFC: self.y = self.nz(Y + 1)
            else: self.a = self.shift(hi >> 1, self.a)
            return None
        if lo == 0xD:
            if op == 0x0D: self.push(self.psw)
            elif op == 0x1D: self.x = self.nz(X - 1)
            elif op == 0x2D: self.push(self.a)
            elif op == 0x3D: self.x = self.nz(X + 1)
            elif op == 0x4D: self.push(X)
            elif op == 0x5D: self.x = self.nz(self.a)
            elif op == 0x6D: self.push(Y)
            elif op == 0x7D: self.a = self.nz(X)
            elif op == 0x8D: self.y = self.nz(self.fetch())
            elif op == 0x9D: self.x = self.nz(self.sp)
            elif op == 0xAD: self.cmp(Y, self.fetch())
            elif op == 0xBD: self.sp = X
            elif op == 0xCD: self.x = self.nz(self.fetch())
            elif op == 0xDD: self.a = self.nz(Y)
            elif op == 0xED: self.psw ^= FC
            else: self.y = self.nz(self.a)
            return None
        if lo == 0xE:
            return self.execute_e(op, X, Y)
        return self.execute_f(op, pc0, X, Y)

    def execute_a(self, op, hi):
        if not hi & 1:                          # OR1 AND1 EOR1 MOV1 NOT1
            w = self.fetchw()
            addr, bit = w & 0x1FFF, w >> 13
            m = (self.rd(addr) >> bit) & 1
            c = self.psw & FC
            if hi == 0: self.setf(FC, c | m)
            elif hi == 2: self.setf(FC, c | (m ^ 1))
            elif hi == 4: self.setf(FC, c & m)
            elif hi == 6: self.setf(FC, c & (m ^ 1))
            elif hi == 8: self.setf(FC, c ^ m)
            elif hi == 0xA: self.setf(FC, m)
            elif hi == 0xC: self.wr(addr, (self.rd(addr) & ~(1 << bit)) | (c << bit))
            else: self.wr(addr, self.rd(addr) ^ (1 << bit))
            return None
        o = self.fetch()
        if op == 0xFA:                          # MOV dp,dp (source first)
            v = self.rd(self.dp(o))
            self.wr(self.dp(self.fetch()), v)
            return None
        if op == 0xDA:                          # MOVW dp,YA
            self.wr(self.dp(o), self.a)
            self.wr(self.dp((o + 1) & 0xFF), self.y)
            return None
        w = self.rdw_dp(o)
        ya = (self.y << 8) | self.a
        if op in (0x1A, 0x3A):                  # DECW / INCW
            w = (w + (1 if op == 0x3A else -1)) & 0xFFFF
            self.wr(self.dp(o), w)
            self.wr(self.dp((o + 1) & 0xFF), w >> 8)
            self.nz16(w)
        elif op == 0x5A:                        # CMPW
            self.setf(FC, ya >= w)
            self.nz16((ya - w) & 0xFFFF)
        elif op in (0x7A, 0x9A):                # ADDW / SUBW
            b, cin = (w ^ 0xFFFF, 1) if op == 0x9A else (w, 0)
            r = ya + b + cin
            self.setf(FH, ((ya & 0xFFF) + (b & 0xFFF) + cin) > 0xFFF)
            self.setf(FV, (~(ya ^ b) & (ya ^ r)) & 0x8000)
            self.setf(FC, r > 0xFFFF)
            r &= 0xFFFF
            self.a, self.y = r & 0xFF, r >> 8
            self.nz16(r)
        else:                                   # MOVW YA,dp
            self.a, self.y = w & 0xFF, w >> 8
            self.nz16(w)
        return None

    def execute_e(self, op, X, Y):
        if op in (0x0E, 0x4E):                  # TSET1 / TCLR1
            a = self.fetchw()
            v = self.rd(a)
            self.nz((self.a - v) & 0xFF)
            self.wr(a, (v | self.a) if op == 0x0E else (v & ~self.a))
        elif op == 0x1E: self.cmp(X, self.rd(self.fetchw()))
        elif op == 0x3E: self.cmp(X, self.rd(self.dp(self.fetch())))
        elif op == 0x5E: self.cmp(Y, self.rd(self.fetchw()))
        elif op == 0x7E: self.cmp(Y, self.rd(self.dp(self.fetch())))
        elif op == 0x2E: return self.branch(self.a != self.rd(self.dp(self.fetch())))
        elif op == 0xDE: return self.branch(self.a != self.rd(self.dp(self.fetch() + X)))
        elif op == 0x6E:                        # DBNZ dp
            d = self.dp(self.fetch())
            v = (self.rd(d) - 1) & 0xFF
            self.wr(d, v)
            return self.branch(v != 0)
        elif op == 0xFE:                        # DBNZ Y
            self.y = (Y - 1) & 0xFF
            return self.branch(self.y != 0)
        elif op == 0x8E: self.psw = self.pop()
        elif op == 0xAE: self.a = self.pop()
        elif op == 0xCE: self.x = self.pop()
        elif op == 0xEE: self.y = self.pop()
        elif op == 0x9E:                        # DIV YA,X
            ya = (Y << 8) | self.a
            self.setf(FH, (X & 0xF) <= (Y & 0xF))
            self.setf(FV, Y >= X)
            if Y < (X << 1):
                a, y = ya // X, ya % X
            else:
                a = 255 - (ya - (X << 9)) // (256 - X)
                y = X + (ya - (X << 9)) % (256 - X)
            self.a, self.y = a & 0xFF, y & 0xFF
            self.nz(self.a)
        else:                                   # DAS
            if not self.psw & FC or self.a > 0x99:
                self.a = (self.a - 0x60) & 0xFF
                self.psw &= ~FC & 0xFF
            if not self.psw & FH or (self.a & 0xF) > 9:
                self.a = (self.a - 6) & 0xFF
            self.nz(self.a)
        return None

    def execute_f(self, op, pc0, X, Y):
        if op == 0x0F:                          # BRK
            self.call(self.rw(0xFFDE))
            self.push(self.psw)
            self.psw = (self.psw | FB) & ~FI & 0xFF
        elif op == 0x1F: self.pc = self.rw((self.fetchw() + X) & 0xFFFF)
        elif op == 0x2F: return self.branch(True)
        elif op == 0x3F: self.call(self.fetchw())
        elif op == 0x4F: self.call(0xFF00 | self.fetch())
        elif op == 0x5F: self.pc = self.fetchw()
        elif op in (0x6F, 0x7F):                # RET / RETI
            if op == 0x7F:
                self.psw = self.pop()
            lo = self.pop()
            self.pc = lo | (self.pop() << 8)
        elif op == 0x8F:                        # MOV dp,#imm
            imm = self.fetch()
            self.wr(self.dp(self.fetch()), imm)
        elif op == 0x9F: self.a = self.nz(((self.a >> 4) | (self.a << 4)) & 0xFF)
        elif op == 0xAF:
            self.wr(self.dp(X), self.a)
            self.x = (X + 1) & 0xFF
        elif op == 0xBF:
            self.a = self.nz(self.rd(self.dp(X)))
            self.x = (X + 1) & 0xFF
        elif op == 0xCF:                        # MUL YA
            r = Y * self.a
            self.a, self.y = r & 0xFF, r >> 8
            self.nz(self.y)
        elif op == 0xDF:                        # DAA
            if self.psw & FC or self.a > 0x99:
                self.a = (self.a + 0x60) & 0xFF
                self.psw |= FC
            if self.psw & FH or (self.a & 0xF) > 9:
                self.a = (self.a + 6) & 0xFF
            self.nz(self.a)
        else:                                   # SLEEP / STOP
            raise RuntimeError("SPC700 halted at $%04X" % pc0)
        return None


# ---------------------------------------------------------------------------
# The 65816 side of the port protocol
# ---------------------------------------------------------------------------

class SoundHost:
    """Drives the ROM's sound driver the way bank $8C does."""

    STEP_LIMIT = 3_000_000

    def __init__(self, rom):
        self.rom = rom
        self.spc = SPC700()
        blocks, entry = driver_blocks(rom)
        for dest, data in blocks:
            self.spc.ram[dest:dest + len(data)] = data
        self.restart(entry)

    def restart(self, entry=0x0700):
        """State after the IPL's JMP [$0000+X] into the driver."""
        s = self.spc
        s.ram[0], s.ram[1] = entry & 0xFF, entry >> 8
        s.a, s.x, s.y, s.sp, s.psw, s.pc = 0xCC, 0, 0, 0xEF, 0x02, entry
        s.port_out[:] = [0xCC, 0, 0, 0]
        s.port_in[:] = [0xCC, 0, entry & 0xFF, entry >> 8]
        self.counter = 1        # $9F: the driver writes 1 to $F6 at startup

    def run_until(self, cond):
        s = self.spc
        for _ in range(self.STEP_LIMIT):
            if cond():
                return
            s.step()
        raise TimeoutError("driver stuck at $%04X" % s.pc)

    def wait_ack(self):
        self.run_until(lambda: self.spc.port_out[2] == self.counter)

    def send(self, cmd, param=0):
        """$8C:81FD: wait for the last echo, then post the next command."""
        self.wait_ack()
        self.counter = (self.counter + 1) & 0xFF or 1
        self.spc.port_in[:] = [param & 0xFF, param >> 8, self.counter, cmd]

    def command(self, cmd, param=0):
        self.send(cmd, param)
        self.wait_ack()

    def upload(self, package):
        """$0E, the IPL transfer of one package ($8C:805B), then $02."""
        s = self.spc
        self.send(CMD_UPLOAD)
        self.run_until(lambda: s.pc == IPL_WAIT_PC and s.port_out[0] == 0xAA)
        for dest, data in package_records(self.rom, package):
            n = min(len(data), 0x10000 - dest)
            s.ram[dest:dest + n] = data[:n]
        self.restart()
        self.command(CMD_AFTER_UPLOAD)

    def boot(self):
        self.upload(0)

    def play_music(self, music, volume=None):
        self.command(CMD_STOP_A, 0x8080)
        self.command(CMD_STOP_B, 0x0000)
        self.upload(self.rom[MUSIC_PACKAGE + music])
        self.command(CMD_PLAY_MUSIC, music)
        if volume is not None:
            self.command(CMD_VOLUME, volume)

    def play_sfx(self, sfx):
        package = self.rom[SFX_PACKAGE + sfx]
        if package:
            self.command(CMD_STOP_A, 0x8080)
            self.command(CMD_STOP_B, 0x0000)
            self.upload(package)
        self.command(CMD_PLAY_SFX, sfx)

    def snapshot(self, title, seconds=180, fade_ms=10000):
        """The running state as an SPC v0.30 file."""
        s = self.spc
        spc = bytearray(0x10200)
        spc[0x00:0x21] = b"SNES-SPC700 Sound File Data v0.30"
        spc[0x21:0x25] = b"\x1a\x1a\x1a\x1e"    # ID666 present, version 30
        struct.pack_into("<HBBBBB", spc, 0x25, s.pc, s.a, s.x, s.y, s.psw, s.sp)

        def tag(offset, text, size):
            raw = text.encode("latin1", errors="replace")[:size]
            spc[offset:offset + len(raw)] = raw

        tag(0x2E, title, 32)
        tag(0x4E, "Secret of Evermore", 32)
        tag(0x6E, "everscript", 16)
        tag(0x9E, datetime.date.today().strftime("%m/%d/%Y"), 11)
        tag(0xA9, str(seconds), 3)
        tag(0xAC, str(fade_ms), 5)
        tag(0xB1, "Jeremy Soule", 32)

        ram = bytearray(s.ram)
        ram[0xF1], ram[0xF2] = s.control, s.dsp_addr
        ram[0xF4:0xF8] = bytes(s.port_in)       # players feed these to the SPC
        ram[0xFA:0xFD] = bytes(s.t_target)
        ram[0xFD:0x100] = bytes(s.t_counter)
        spc[0x100:0x10100] = ram
        dsp = bytearray(s.dsp)
        dsp[0x4C] = dsp[0x5C] = 0               # no pending KON / KOFF
        spc[0x10100:0x10180] = dsp
        spc[0x101C0:0x10200] = ram[0xFFC0:]     # RAM hidden under the IPL ROM
        return bytes(spc)


def track_list():
    """[(name, music, volume, sfx)] for everything the dumper writes."""
    tracks = [(name, m, None, None) for m, name in sorted(MUSIC.items()) if name]
    return tracks + EXTRAS


def dump_track(rom, music=None, volume=None, sfx=None, title=""):
    host = SoundHost(rom)
    host.boot()
    if music is not None:
        host.play_music(music, volume)
    if sfx is not None:
        host.play_sfx(sfx)
    return host.snapshot(title)


def file_stem(name):
    return re.sub(r"[^0-9A-Za-z]+", "_", name).strip("_")


# ---------------------------------------------------------------------------
# Rendering (libgme) and comparison
# ---------------------------------------------------------------------------

SAMPLE_RATE = 32000


def load_gme():
    for path in ("/opt/homebrew/lib/libgme.dylib", "/usr/local/lib/libgme.dylib",
                 "libgme.so.0", "libgme.so", "libgme.dylib"):
        try:
            lib = ctypes.CDLL(path)
        except OSError:
            continue
        lib.gme_open_data.restype = ctypes.c_char_p
        lib.gme_play.restype = ctypes.c_char_p
        return lib
    return None


def render(gme, spc_bytes, seconds, fade_seconds=0):
    """Interleaved stereo int16 samples as bytes."""
    emu = ctypes.c_void_p()
    err = gme.gme_open_data(spc_bytes, len(spc_bytes), ctypes.byref(emu), SAMPLE_RATE)
    if err:
        raise RuntimeError(err.decode())
    gme.gme_start_track(emu, 0)
    if fade_seconds:
        gme.gme_set_fade(emu, (seconds - fade_seconds) * 1000)
    count = SAMPLE_RATE * 2 * seconds
    buf = (ctypes.c_short * count)()
    gme.gme_play(emu, count, buf)
    gme.gme_delete(emu)
    return bytes(buf)


def write_wav(path, pcm):
    with wave.open(path, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SAMPLE_RATE)
        w.writeframes(pcm)


HOP = 512


def spectrogram(np, pcm, seconds):
    """Unit-normalised log-band spectrogram frames of the first `seconds`, and a
    mask of the frames that are not silent (within 50 dB of the loudest)."""
    x = np.frombuffer(pcm, dtype=np.int16).reshape(-1, 2).mean(axis=1) / 32768.0
    x = x[:SAMPLE_RATE * seconds]
    nfft = 2048
    frames = np.lib.stride_tricks.sliding_window_view(x, nfft)[::HOP] * np.hanning(nfft)
    mag = np.abs(np.fft.rfft(frames, axis=1))
    freqs = np.fft.rfftfreq(nfft, 1 / SAMPLE_RATE)
    edges = np.geomspace(80, 10000, 65)
    bands = np.stack([mag[:, (freqs >= a) & (freqs < b)].sum(1)
                      for a, b in zip(edges[:-1], edges[1:])], 1)
    energy = bands.sum(1)
    mask = (energy > energy.max() * 10 ** (-50 / 20)).astype(float)
    bands = np.log1p(bands * 20)
    bands -= bands.mean(1, keepdims=True)
    bands /= np.linalg.norm(bands, axis=1, keepdims=True) + 1e-6
    return bands * mask[:, None], mask


def aligned_similarity(np, a, b):
    """Best mean cosine of the frames both tracks sound in, over all time offsets
    where at least a third of the shorter track's sounding frames overlap."""
    (fa, ma), (fb, mb) = a, b
    n = len(fa) + len(fb) - 1
    size = 1 << (n - 1).bit_length()

    def xcorr(p, q):
        return np.fft.irfft(np.fft.rfft(p, size, axis=0) * np.fft.rfft(q[::-1], size, axis=0),
                            size, axis=0)[:n]

    corr = xcorr(fa, fb).sum(1)
    both = np.rint(xcorr(ma, mb))
    need = max(1.0, min(ma.sum(), mb.sum()) / 3)
    score = np.where(both >= need, corr / np.maximum(both, 1), -1)
    i = int(score.argmax())
    return float(score[i]), (i - (len(fb) - 1)) * HOP / SAMPLE_RATE


def compare_all(dumped, refs, seconds):
    """Scores every dump against every reference. A track is OK when it and its
    reference pick each other: the reference is the dump's best match, or the
    dump is the reference's best match (some pieces share a theme, e.g.
    Many Years Ago and Return to Podunk)."""
    import numpy as np
    ref_specs = {name: spectrogram(np, pcm, seconds) for name, pcm in refs.items()}
    scores = {}
    for name, pcm in dumped.items():
        spec = spectrogram(np, pcm, seconds)
        scores[name] = {r: aligned_similarity(np, spec, s) for r, s in ref_specs.items()}
    best_dump = {r: max(dumped, key=lambda d: scores[d][r][0]) for r in refs}

    print("\n%-30s %-6s %-7s  %-8s %s" % ("Track", "Score", "Offset", "Status", "Best other reference"))
    print("-" * 96)
    matched = with_ref = 0
    for name, row in scores.items():
        best_other = max((v[0], r) for r, v in row.items() if r != name)
        own = row.get(name)
        if own is None:
            status, own_text, lag_text = "no ref", "-", "-"
        else:
            with_ref += 1
            ok = own[0] > best_other[0] or best_dump[name] == name
            matched += ok
            status = "OK" if ok else "MISMATCH"
            own_text, lag_text = "%.3f" % own[0], "%+.1fs" % own[1]
        print("%-30s %-6s %-7s  %-8s %-28s %.3f" % (name[:30], own_text, lag_text, status,
                                                   best_other[1][:28], best_other[0]))
    print("-" * 96)
    print("%d of %d tracks match their reference." % (matched, with_ref))
    unused = sorted(set(refs) - set(dumped))
    if unused:
        print("References without a dump: %s" % ", ".join(unused))


def main():
    parser = argparse.ArgumentParser(description="Secret of Evermore SPC music dumper")
    parser.add_argument("--rom", default=DEFAULT_ROM, help="path to the SNES ROM")
    parser.add_argument("--out-dir", default="out", help="output directory")
    parser.add_argument("--emu-dir", default=DEFAULT_EMU_DIR, help="reference .spc rips to compare against")
    parser.add_argument("--duration", type=int, default=150, help="WAV length in seconds, fade included")
    parser.add_argument("--fade", type=int, default=8, help="WAV fade-out in seconds")
    parser.add_argument("--compare-seconds", type=int, default=40, help="audio compared per track")
    parser.add_argument("--no-wav", action="store_true", help="do not write .wav files")
    parser.add_argument("--no-compare", action="store_true", help="skip the reference comparison")
    args = parser.parse_args()

    with open(args.rom, "rb") as f:
        rom = f.read()
    if len(rom) % 0x8000 == 0x200:
        rom = rom[0x200:]
    if rom[MUSIC_COUNT] != 0x46:
        sys.exit("unexpected music count $%02X: not Secret of Evermore (U)?" % rom[MUSIC_COUNT])

    spc_dir = os.path.join(args.out_dir, "music_spc")
    wav_dir = os.path.join(args.out_dir, "music_wav")
    ref_wav_dir = os.path.join(args.out_dir, "reference_wav")
    os.makedirs(spc_dir, exist_ok=True)

    want_audio = not (args.no_wav and args.no_compare)
    gme = load_gme() if want_audio else None
    if want_audio and gme is None:
        print("libgme not found, writing .spc only (brew install game-music-emu)")
    render_secs = max(args.duration, args.compare_seconds)
    wav_bytes = SAMPLE_RATE * 4 * args.duration

    tracks = track_list()
    print("Dumping %d tracks to %s" % (len(tracks), spc_dir))
    dumped = {}
    for name, music, volume, sfx in tracks:
        spc = dump_track(rom, music, volume, sfx, name.split(" ", 1)[1])
        stem = file_stem(name)
        with open(os.path.join(spc_dir, stem + ".spc"), "wb") as f:
            f.write(spc)
        if gme:
            pcm = render(gme, spc, render_secs, args.fade)
            dumped[name] = pcm
            if not args.no_wav:
                os.makedirs(wav_dir, exist_ok=True)
                write_wav(os.path.join(wav_dir, stem + ".wav"), pcm[:wav_bytes])
        source = "music $%02X" % music if music is not None else "sfx $%02X" % sfx
        if volume is not None:
            source += " volume $%02X" % volume
        print("  %-30s %s" % (stem, source))

    if args.no_compare or not gme:
        return
    if not os.path.isdir(args.emu_dir):
        print("Reference directory not found, comparison skipped: %s" % args.emu_dir)
        return
    refs = {}
    for path in sorted(glob.glob(os.path.join(args.emu_dir, "*.spc"))):
        name = os.path.basename(path)[:-4]
        with open(path, "rb") as f:
            pcm = render(gme, f.read(), render_secs, args.fade)
        refs[name] = pcm
        if not args.no_wav:
            os.makedirs(ref_wav_dir, exist_ok=True)
            write_wav(os.path.join(ref_wav_dir, file_stem(name) + ".wav"), pcm[:wav_bytes])
    print("Rendered %d reference rips%s" % (len(refs), "" if args.no_wav else " to " + ref_wav_dir))
    compare_all(dumped, refs, args.compare_seconds)


if __name__ == "__main__":
    main()
