#!/usr/bin/env python3
"""
tools/dump_spc.py - Secret of Evermore SPC700 Music & Soundbank Dumper

Reconstructs exact SPC700 64KB Audio RAM snapshots directly from the SNES ROM
and exports standard, playable .spc files compatible with Snes9x, Mesen, Foobar2000,
VLC, and Game Music Emu.

Authoritative ROM Sources:
- $81:80DC: Core Wolfgang v3 Driver binary (6,112 bytes -> SPC $0700)
- $81:9900: Master Song Count (70 songs, indices 0x00..0x46)
- $81:9903: Master Song Pointer Table (71 24-bit SNES pointers)
- $8A:A7BE: Song 0 (Master Global Soundbank & Driver Tables)
- $8A/$8B:  Songs 0x01..0x46 (Sequence data & exclusive sample banks)
"""

import sys
import os
import struct

SONG_NAMES = {
    0x00: "Silence_Base_Bank",
    0x01: "Boss_Drums_Thraxx",
    0x02: "Prehistoria_Boss",
    0x03: "Event_Cutscene_1",
    0x04: "Event_Cutscene_2",
    0x05: "Prehistoria_Ambient_StrongHeart",
    0x06: "Prehistoria_Ambient_Jungle",
    0x07: "Swamp_Ambient",
    0x08: "Jungle_Ambient",
    0x09: "Bugmuck_Ambient_Melody",
    0x0a: "Prehistoria_Cave_Ambient",
    0x0b: "Prehistoria_Volcano_Ambient",
    0x0c: "Unused_Song_0x0c",
    0x0d: "Antiqua_Ambient",
    0x0e: "Halls_Collapsing_Bridge",
    0x0f: "Antiqua_Desert_Theme",
    0x10: "Standard_Boss_Theme",
    0x11: "Cave_Ambient_Piano",
    0x12: "Antiqua_Pyramid_Ambient",
    0x13: "Antiqua_Market_Ambient",
    0x14: "Antiqua_City_Theme",
    0x15: "Event_Cutscene_3",
    0x16: "Omnitopia_Space_Noise",
    0x17: "Event_Fanfare",
    0x18: "Boss_Jungle_Raptors",
    0x19: "Fanfare_Victory",
    0x1a: "Nobilia_Market_Theme",
    0x1b: "Water_Ambient_Seagulls",
    0x1c: "Crustacia_Harbor_Theme",
    0x1d: "Antiqua_Plains_Ambient",
    0x1e: "Wind_Ambient_Birds_2",
    0x1f: "Omnitopia_Space_Theme",
    0x20: "Nobilia_Inn_Guitar",
    0x21: "Pyramid_Theme",
    0x22: "Thraxx_Bridge_Collapse",
    0x23: "Waterfall_Ambient",
    0x24: "Gothica_Dark_Forest",
    0x25: "Mystery_Podunk_Theme",
    0x26: "Unused_Song_0x26",
    0x27: "Ambient_Silence",
    0x28: "Boss_Arena_Vigor",
    0x29: "Vigor_Rolling_Scene",
    0x2a: "Antiqua_Temple_Ambient",
    0x2b: "Puppet_Show",
    0x2c: "Boss_Mini_Minitaur",
    0x2d: "Gothica_Dungeon_Theme",
    0x2e: "Halls_2",
    0x2f: "Act3_Gothica_Exterior",
    0x30: "Ebon_Keep",
    0x31: "Gothica_Interior_Ambient",
    0x32: "Halls_3",
    0x33: "Wind_Ambient_Birds",
    0x34: "Gothica_Town_Theme",
    0x35: "Gothica_Castle_Theme",
    0x36: "Wing_Ambient_Void_Desert",
    0x37: "Gothica_Ambient_1",
    0x38: "Gothica_Ambient_Melody",
    0x39: "Sewer_Ambient_Water",
    0x3a: "Omnitopia_Elevator_Room",
    0x3b: "Omnitopia_Control_Room",
    0x3c: "Fanfare_Item_Gourd",
    0x3d: "Jungle_Ambient_Birds",
    0x3e: "Omnitopia_Hangar_Ambient",
    0x3f: "Nobilia_Market_Transaction",
    0x40: "Omnitopia_Labs_Ambient",
    0x41: "Pig_Race_Theme",
    0x42: "Wind_Ambient_Plane",
    0x43: "Omnitopia_Machine_Ambient",
    0x44: "Boss_Carltron_Bossrush",
    0x45: "Alarm_Red_Alert",
    0x46: "Unused_Orphaned_Song_0x46",
}

def load_rom_song_blocks(rom, offset, aram):
    """Parses a song descriptor package and writes blocks into SPC700 ARAM."""
    count = rom[offset] | (rom[offset + 1] << 8)
    curr = offset + 2
    for _ in range(count):
        length = rom[curr] | (rom[curr + 1] << 8)
        src_addr = rom[curr + 2] | (rom[curr + 3] << 8)
        src_bank = rom[curr + 4]
        spc_dest = rom[curr + 5] | (rom[curr + 6] << 8)
        src_rom = (src_bank & 0x3F) * 0x10000 + src_addr
        if length > 0 and src_rom + length <= len(rom):
            aram[spc_dest:spc_dest + length] = rom[src_rom:src_rom + length]
        curr += 7

def create_spc_file(aram, song_id, song_title):
    """Assembles a standard SNES-SPC700 Sound File Data v0.30 binary."""
    spc = bytearray(0x10200)

    # 1. Header Magic
    magic = b"SNES-SPC700 Sound File Data v0.30\x1a\x1a"
    spc[0x00000:len(magic)] = magic

    # 2. Header Flags & Version
    spc[0x00023] = 0x1A  # ID666 Tag present (binary/text standard)
    spc[0x00024] = 30    # Version 30 (v0.30)

    # 3. CPU Registers
    # Program Counter: Wolfgang v3 entry point is $0700
    struct.pack_into("<H", spc, 0x00025, 0x0700)
    spc[0x00027] = 0x00  # A
    spc[0x00028] = 0x00  # X
    spc[0x00029] = 0x00  # Y
    spc[0x0002A] = 0x00  # PSW
    spc[0x0002B] = 0xEF  # SP (standard stack pointer)

    # 4. ID666 Metadata Tags
    def write_tag(offset, text, length):
        encoded = text.encode("latin1", errors="ignore")[:length]
        spc[offset:offset + len(encoded)] = encoded

    write_tag(0x0002E, f"{song_title} (Song {song_id:02x})", 32)   # Song Title
    write_tag(0x0004E, "Secret of Evermore", 32)                 # Game Title
    write_tag(0x0006E, "Everscript Dumper", 16)                  # Dumper Name
    write_tag(0x0007E, "Wolfgang v3 / Steve Aguirre", 32)        # Comments
    write_tag(0x0009E, "09/27/2026", 11)                         # Date
    write_tag(0x000A9, "180", 3)                                 # Seconds before fade
    write_tag(0x000AC, "10000", 5)                               # Fade length (ms)
    write_tag(0x000B1, "Jeremy Soule", 32)                       # Artist

    # 5. 64 KB SPC700 ARAM Dump ($00100..$100FF)
    spc[0x00100:0x10100] = aram

    # 6. DSP Registers ($10100..$1017F)
    # Default initial DSP registers: DIR = $1F (Sample directory at $1F00)
    spc[0x1015D] = 0x1F  # DSP $5D = DIR register
    spc[0x1010C] = 0x7F  # Main volume left
    spc[0x1011C] = 0x7F  # Main volume right

    return bytes(spc)

def dump_all_songs(rom_path="Secret of Evermore (U) [!].smc", out_dir="music_spc"):
    if not os.path.exists(rom_path):
        print(f"Error: ROM file not found: {rom_path}")
        sys.exit(1)

    with open(rom_path, "rb") as f:
        rom = f.read()

    os.makedirs(out_dir, exist_ok=True)

    # Read base driver binary at $81:80DC (ROM 0x0180DC)
    # Header: length (2 bytes), dest (2 bytes, $0700)
    driver_len = rom[0x0180DC] | (rom[0x0180DD] << 8)
    driver_dest = rom[0x0180DE] | (rom[0x0180DF] << 8)
    driver_code = rom[0x0180E0:0x0180E0 + driver_len]
    print(f"Loaded Wolfgang Driver: {driver_len} bytes -> SPC ${driver_dest:04X}")

    # Song pointer table at $81:9903 (ROM 0x019903)
    num_songs = rom[0x019900]
    print(f"Dumping {num_songs + 1} songs (0x00..0x{num_songs:02x}) into '{out_dir}/'...")

    for song_id in range(num_songs + 1):
        # Initialize fresh 64 KB ARAM
        aram = bytearray(65536)

        # 1. Install Wolfgang driver binary into $0700
        aram[driver_dest:driver_dest + driver_len] = driver_code

        # 2. Load Song 0 (Base driver tables and 82 universal sound effect samples)
        song0_ptr_idx = 0x019903
        song0_addr = rom[song0_ptr_idx] | (rom[song0_ptr_idx + 1] << 8)
        song0_bank = rom[song0_ptr_idx + 2]
        song0_rom = (song0_bank & 0x3F) * 0x10000 + song0_addr
        load_rom_song_blocks(rom, song0_rom, aram)

        # 3. Load target song blocks (if not Song 0)
        if song_id != 0:
            ptr_idx = 0x019903 + song_id * 3
            addr = rom[ptr_idx] | (rom[ptr_idx + 1] << 8)
            bank = rom[ptr_idx + 2]
            song_rom = (bank & 0x3F) * 0x10000 + addr
            load_rom_song_blocks(rom, song_rom, aram)

        # 4. Set communication registers for playback
        # Ports: $2140 = $06 (play command), $2142 = song_id
        aram[0x00F4] = 0x06     # CPUIO0
        aram[0x00F5] = 0x00     # CPUIO1
        aram[0x00F6] = song_id  # CPUIO2
        aram[0x00F7] = 0x00     # CPUIO3

        # 5. Build and save SPC file
        title = SONG_NAMES.get(song_id, f"Song_0x{song_id:02x}")
        filename = f"{song_id:02x}_{title}.spc"
        out_path = os.path.join(out_dir, filename)

        spc_bytes = create_spc_file(aram, song_id, title)
        with open(out_path, "wb") as f:
            f.write(spc_bytes)

    print(f"Successfully exported {num_songs + 1} SPC files to {out_dir}/")

if __name__ == "__main__":
    dump_all_songs()
