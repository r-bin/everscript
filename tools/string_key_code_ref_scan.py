#!/usr/bin/env python3
"""
Throwaway, one-off analysis script (NOT a tracked/shipped tool) — written for
docs/rom-extension-wishlist.md item 6, "Patch complexity assessment" pass.
Do not confuse with scratch/string_key_null_scan.py (a different, earlier
script from a prior pass — that one reads the string_key table's *contents*;
this one searches the whole ROM image for *code byte patterns that might
reference the table's base address*, $91D000).

WHAT THIS SCRIPT IS AND IS NOT
-------------------------------
This is a static byte-pattern scan of the raw ROM file, NOT a disassembly.
There is no 65816 disassembler available in this environment (checked: not
in requirements.txt, not pip-installable offline) and no live
emulator/Mesen2 session. A byte sequence that happens to match an opcode +
the literal address $91D000 is a CANDIDATE that the CPU might execute as
that instruction — it is not proof. The same 4-byte sequence could occur
inside unrelated data (e.g. another pointer table, graphics data, text) by
pure coincidence, or as a real pointer to $91D000 stored as *data* rather
than consumed as an *instruction operand*. Every hit reported below must be
read with that caveat; only live Mesen2 tracing (read/write breakpoints on
$91D000..$91F32D during a full playthrough) can actually confirm which, if
any, of these are the real opcode-handler references for text()/subtext()/
install_string() (opcodes 0x51/0x52/0x8c per compiler/ast_everscript.py and
in/core/.../06_strings.evs, 04_map_manipulation.evs).

METHOD
------
1. STRONG heuristic — absolute-long / absolute-long-indexed addressing:
   opcode byte immediately followed by the 3-byte little-endian operand
   00 D0 91 (i.e. bytes matching $91D000 encoded as a 65816 24-bit
   absolute-long operand). Candidate opcodes, matching the task's own list
   plus the natural full set of long/long-indexed opcodes for this
   addressing mode family (65816 opcode table, standard/external
   reference — not itself derived from this repo):
     LDA long        0xAF      LDA long,X      0xBF
     STA long        0x8F      CMP long        0xCF
     ADC long        0x6F      ADC long,X      0x7F
     ORA long        0x0F      ORA long,X      0x1F
     AND long        0x2F      AND long,X      0x3F
     EOR long        0x4F      EOR long,X      0x5F
     CMP long,X      0xDF      SBC long        0xEF
     SBC long,X      0xFF
     JSL             0x22      JML             0x5C
   The task's own framing (a base address that gets "+ index" added to
   compute a pointer) makes LDA long,X (0xBF) and ADC-family patterns the
   most plausible strong candidates; the rest are included for completeness
   and reported with the same "candidate, not proof" caveat.

2. WEAK heuristic — split/decomposed immediate-load form: a 16-bit
   immediate load of the low word, LDA #$D000 (0xA9 00 D0 — this assumes
   16-bit accumulator/M=0, which is a common but not universal state),
   occurring within a small window (16 bytes, per the task's own spec) of a
   bank-byte reference to $91 (0xA9 91 as an *8-bit* immediate load, or a
   bare 0x91 byte adjacent to a PHB/PLB opcode: PHB=0x8B, PLB=0xAB). This
   heuristic is explicitly weaker and noisier (a lone 0x91 byte is common
   in unrelated code/data), and is reported completely separately from the
   strong hits, never merged into the same count.

For every hit this script reports: ROM file offset, translated SNES address
(via this repo's own documented HiROM formula, .github/rom-map.md §1:
file_offset = (bank & 0x3F) << 16 | address_low16, inverted here to go
file->SNES: bank = (file_offset >> 16) | 0x80 for the $80..$BF fast-ROM
mirror, since all candidate hits in the ROM's first 3 MB fall in the
$80..$BF / $C0..$FF code+data region under that mapping), and ~16 bytes of
surrounding context as hex, with a best-effort (manual, non-authoritative)
label of the few opcodes this script's author is confident about.

BASE-RATE SANITY CHECK
-----------------------
ROM is 3,145,728 bytes. A fixed 3-byte target pattern (00 D0 91) has a
1-in-16,777,216 (2^24) chance per aligned position under a uniform-random
byte assumption; naive expected count over ~3.1M start positions is
3145728 / 16777216 ~= 0.19 "random" 3-byte coincidences overall (the task
description's own "~0.5 expected" figure is in the same order of magnitude;
small differences come from how the window is counted). Any 4-byte hit
(opcode + 00 D0 91) is rarer still by a further /256. A small number of
raw hits is therefore meaningful signal on its own, and each one's
plausibility as *real code* (vs. buried in an already-documented data
table) is assessed by eye against .github/rom-map.md and the skills below.
"""
import pathlib

ROM_PATH = pathlib.Path(__file__).resolve().parent.parent / "Secret of Evermore (U) [!].smc"

TARGET_LE = bytes([0x00, 0xD0, 0x91])  # $91D000 as a 3-byte little-endian operand

STRONG_OPCODES = {
    0xAF: "LDA long",
    0xBF: "LDA long,X",
    0x8F: "STA long",
    0xCF: "CMP long",
    0x6F: "ADC long",
    0x7F: "ADC long,X",
    0x0F: "ORA long",
    0x1F: "ORA long,X",
    0x2F: "AND long",
    0x3F: "AND long,X",
    0x4F: "EOR long",
    0x5F: "EOR long,X",
    0xDF: "CMP long,X",
    0xEF: "SBC long",
    0xFF: "SBC long,X",
    0x22: "JSL",
    0x5C: "JML",
}

# Already-documented ROM regions from this repo's own docs, used only to
# annotate hits (does this fall inside a range .github/rom-map.md or a
# skill already names?). File-offset ranges, HiROM fast-mirror ($80..$BF
# => file 0x000000..0x3FFFFF one-to-one with (bank&0x3F)<<16|addr).
KNOWN_REGIONS_FILE_OFFSET = [
    (0x11D000, 0x11F32D, "string_key pointer table itself ($91D000..$91F32D, item 6's own subject)"),
    (0x11F32D, 0x11F32D + 0x1000, "claimed dictionary tables region per soetilesviewer text.h ($91F32E onward) -- see Step 2"),
    (0x128000, 0x1BFFFF, "vanilla script VM bytecode banks $92..$9B (rom-map.md 'Key Subsystem Memory Banks')"),
    (0x0EB678, 0x0EB678 + 74 * 142, "character/monster stat table $8EB678 (soetilesviewer skill; upper bound unverified, guess of 142 entries)"),
    (0x1FFDE7, 0x1FFDE7 + 127 * 4 + 8, "Master Map Pointer Table $9FFDE7 (rom-map.md section 2)"),
]


def file_offset_to_snes(file_offset: int) -> str:
    """HiROM: file offset 0x000000..0x3FFFFF mirrors 1:1 onto fast banks
    $80..$FF address space in this repo's own documented model
    (.github/rom-map.md §1 table: $80:8000..$BF:FFFF and $C0:0000..$FF:FFFF
    both map file 0x000000..0x3FFFFF). We report the $80.. mirror (fast
    banks used for engine code) since that's the practically relevant one
    for "is this code."
    """
    bank = 0x80 + (file_offset >> 16)
    addr = file_offset & 0xFFFF
    # banks $80..$BF only cover $8000..$FFFF (upper half); for a raw file
    # offset within a bank whose low word is < 0x8000, HiROM fast banks
    # still map the full 64KB range 0000..FFFF (per rom-map.md, HiROM fast
    # is a full bank), so no masking needed for reporting purposes here.
    return f"${bank:02X}{addr:04X}"


def annotate(file_offset: int) -> str:
    for lo, hi, label in KNOWN_REGIONS_FILE_OFFSET:
        if lo <= file_offset < hi:
            return label
    return "(not inside any region this repo's docs/skills already name)"


def hexdump_context(data: bytes, center: int, before: int = 8, after: int = 12) -> str:
    start = max(0, center - before)
    end = min(len(data), center + after)
    chunk = data[start:end]
    hex_str = " ".join(f"{b:02X}" for b in chunk)
    marker_pos = center - start
    return f"offset -{center - start}..+{end - center - 1} around hit: {hex_str}  (hit starts at byte index {marker_pos} in this dump)"


def scan_strong(data: bytes):
    hits = []
    idx = data.find(TARGET_LE)
    while idx != -1:
        if idx >= 1:
            opcode_pos = idx - 1
            opcode = data[opcode_pos]
            if opcode in STRONG_OPCODES:
                hits.append((opcode_pos, opcode))
        idx = data.find(TARGET_LE, idx + 1)
    return hits


def scan_all_target_occurrences(data: bytes):
    """Every raw occurrence of 00 D0 91 regardless of preceding byte, for
    completeness/transparency (base-rate cross-check)."""
    occ = []
    idx = data.find(TARGET_LE)
    while idx != -1:
        occ.append(idx)
        idx = data.find(TARGET_LE, idx + 1)
    return occ


def scan_weak(data: bytes, window: int = 16):
    """LDA #$D000 (0xA9 00 D0) within `window` bytes of a $91 bank-byte
    reference (0xA9 0x91 8-bit immediate, or 0x91 adjacent to PHB/PLB)."""
    weak_immediate = bytes([0xA9, 0x00, 0xD0])
    hits = []
    idx = data.find(weak_immediate)
    while idx != -1:
        lo = max(0, idx - window)
        hi = min(len(data), idx + 3 + window)
        window_bytes = data[lo:hi]
        # look for 0xA9 0x91 (LDA #$91, 8-bit immediate bank load) or a
        # bare 0x91 next to PHB(0x8B)/PLB(0xAB) inside the window.
        bank_hit = False
        reasons = []
        for i in range(len(window_bytes) - 1):
            if window_bytes[i] == 0xA9 and window_bytes[i + 1] == 0x91:
                bank_hit = True
                reasons.append(f"LDA #$91 (8-bit imm) at window offset {i}")
            if window_bytes[i] == 0x91 and i > 0 and window_bytes[i - 1] in (0x8B, 0xAB):
                bank_hit = True
                mnemonic = "PHB" if window_bytes[i - 1] == 0x8B else "PLB"
                reasons.append(f"{mnemonic} then 0x91 at window offset {i}")
        if bank_hit:
            hits.append((idx, reasons))
        idx = data.find(weak_immediate, idx + 1)
    return hits


def main():
    data = ROM_PATH.read_bytes()
    assert len(data) == 3145728, f"unexpected ROM size {len(data)}"

    print("=" * 78)
    print("ALL raw occurrences of byte pattern 00 D0 91 (little-endian $91D000)")
    print("=" * 78)
    all_occ = scan_all_target_occurrences(data)
    print(f"Total raw 3-byte pattern occurrences anywhere in the ROM: {len(all_occ)}")
    for off in all_occ:
        preceding = data[off - 1] if off >= 1 else None
        preceding_str = f"0x{preceding:02X}" if preceding is not None else "N/A (offset 0)"
        print(f"  file_offset=0x{off:06X}  SNES~{file_offset_to_snes(off)}  "
              f"preceding_byte={preceding_str}  "
              f"in_known_region={annotate(off)}")

    print()
    print("=" * 78)
    print("STRONG heuristic: opcode + absolute-long operand 00 D0 91")
    print("=" * 78)
    strong_hits = scan_strong(data)
    print(f"Strong hits: {len(strong_hits)}")
    for opcode_pos, opcode in strong_hits:
        file_off = opcode_pos
        snes = file_offset_to_snes(file_off)
        mnemonic = STRONG_OPCODES[opcode]
        region = annotate(file_off)
        print(f"\n  file_offset=0x{file_off:06X}  SNES~{snes}  opcode=0x{opcode:02X} ({mnemonic})")
        print(f"    known_region: {region}")
        print(f"    context: {hexdump_context(data, opcode_pos)}")

    print()
    print("=" * 78)
    print("WEAK heuristic: LDA #$D000 (A9 00 D0) within 16 bytes of a $91 bank-byte reference")
    print("=" * 78)
    weak_hits = scan_weak(data)
    print(f"Weak hits: {len(weak_hits)}")
    for idx, reasons in weak_hits:
        file_off = idx
        snes = file_offset_to_snes(file_off)
        region = annotate(file_off)
        print(f"\n  file_offset=0x{file_off:06X}  SNES~{snes}  (LDA #$D000 8-bit-lo-word pattern)")
        print(f"    known_region: {region}")
        print(f"    reasons: {reasons}")
        print(f"    context: {hexdump_context(data, idx, before=16, after=19)}")

    print()
    print("=" * 78)
    print("Summary")
    print("=" * 78)
    print(f"Raw 3-byte pattern occurrences: {len(all_occ)}")
    print(f"Strong (opcode+long-operand) hits: {len(strong_hits)}")
    print(f"Weak (split-immediate near bank-byte) hits: {len(weak_hits)}")


if __name__ == "__main__":
    main()
