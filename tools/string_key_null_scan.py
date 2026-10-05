#!/usr/bin/env python3
"""
Throwaway, one-off analysis script (NOT a tracked/shipped tool — see
docs/rom-extension-wishlist.md item 6 for context).

Reads the full vanilla string_key pointer table straight out of the ROM
file's raw bytes and reports which of the 3002 entries are null (0x000000),
which are non-null duplicates of another entry's pointer, and which are
unique non-null pointers — split by the two ranges this repo's projects
already treat differently (0x0000..0x0545 "vanilla-critical" vs
0x0546..0x232b "Kaizo already reclaims").

Table geometry (per compiler/ast_everscript.py's StringKey class):
  - SNES address of entry N:  0x91d000 + N   (N is the index itself, in
    3-byte steps: N = 0x0000, 0x0003, 0x0006, ... 0x232b)
  - Each entry is 3 raw bytes (a 24-bit ROM pointer; MSB of the pointer,
    i.e. bit 23 / (value >> 16) & 0x80, flags dictionary/byte-pair text
    compression — irrelevant to null-detection, only stripped when
    de-duplicating pointers below).

File-offset mapping (HiROM, verified against this repo's own
.github/rom-map.md §2 table — e.g. SNES $ABF4F1 -> file 0x2BF4F1, which is
(0xAB & 0x3F) << 16 | 0xF4F1 = 0x2B0000 + 0xF4F1 = 0x2BF4F1, confirming the
formula below against real entries already in that table):

  file_offset = (bank & 0x3F) << 16 | address_low16

For 0x91d000: bank=0x91, addr=0xD000 -> (0x91 & 0x3F) << 16 | 0xD000
  = 0x11 << 16 | 0xD000 = 0x110000 + 0xD000 = 0x11D000

This matches the file offset already given in the task/doc (0x11D000), so
the formula is cross-checked, not assumed.
"""
import pathlib

ROM_PATH = pathlib.Path(__file__).resolve().parent.parent / "Secret of Evermore (U) [!].smc"
TABLE_FILE_OFFSET = 0x11D000  # file offset of string_key index 0x0000
INDEX_START = 0x0000
INDEX_END = 0x232B  # inclusive
INDEX_STEP = 3
KAIZO_RESERVED_START = 0x0546  # first index Kaizo/most projects reclaim
# Preserve boundary: 0x0000..0x0545 is treated as vanilla-critical by every
# project in this repo (per docs/rom-extension-wishlist.md item 6).


def read_table(rom_bytes: bytes):
    entries = []  # list of (index, raw_3_bytes, value_int)
    idx = INDEX_START
    while idx <= INDEX_END:
        off = TABLE_FILE_OFFSET + idx
        raw = rom_bytes[off:off + 3]
        value = raw[0] | (raw[1] << 8) | (raw[2] << 16)
        entries.append((idx, raw, value))
        idx += INDEX_STEP
    return entries


def analyze(entries):
    # value with compression-flag MSB (bit 23, i.e. value's top byte bit 7)
    # stripped, for duplicate-pointer comparison only.
    def stripped(v):
        return v & 0x7FFFFF

    target_counts = {}
    for _, _, v in entries:
        if v == 0:
            continue
        s = stripped(v)
        target_counts[s] = target_counts.get(s, 0) + 1

    null_entries = []
    dup_entries = []
    unique_entries = []
    for idx, raw, v in entries:
        if v == 0:
            null_entries.append(idx)
        else:
            s = stripped(v)
            if target_counts[s] > 1:
                dup_entries.append(idx)
            else:
                unique_entries.append(idx)

    return null_entries, dup_entries, unique_entries


def in_range(idx, lo, hi):
    return lo <= idx <= hi


def main():
    rom_bytes = ROM_PATH.read_bytes()
    assert len(rom_bytes) == 3145728, f"unexpected ROM size {len(rom_bytes)}"

    entries = read_table(rom_bytes)
    assert len(entries) == 3002, f"expected 3002 entries, got {len(entries)}"

    null_entries, dup_entries, unique_entries = analyze(entries)

    total = len(entries)
    print(f"Total entries: {total}")
    print(f"Null (0x000000) entries: {len(null_entries)}")
    print(f"Non-null duplicate-pointer entries: {len(dup_entries)}")
    print(f"Unique non-null pointer entries: {len(unique_entries)}")
    assert len(null_entries) + len(dup_entries) + len(unique_entries) == total

    # Split by vanilla-critical (0x0000..0x0545) vs Kaizo-reclaimed
    # (0x0546..0x232b) ranges.
    def count_in_range(lst, lo, hi):
        return sum(1 for idx in lst if in_range(idx, lo, hi))

    vc_lo, vc_hi = 0x0000, 0x0545
    kr_lo, kr_hi = KAIZO_RESERVED_START, INDEX_END

    vc_total = count_in_range([e[0] for e in entries], vc_lo, vc_hi)
    kr_total = count_in_range([e[0] for e in entries], kr_lo, kr_hi)

    vc_null = count_in_range(null_entries, vc_lo, vc_hi)
    vc_dup = count_in_range(dup_entries, vc_lo, vc_hi)
    vc_uniq = count_in_range(unique_entries, vc_lo, vc_hi)

    kr_null = count_in_range(null_entries, kr_lo, kr_hi)
    kr_dup = count_in_range(dup_entries, kr_lo, kr_hi)
    kr_uniq = count_in_range(unique_entries, kr_lo, kr_hi)

    print()
    print(f"Vanilla-critical range 0x{vc_lo:04x}..0x{vc_hi:04x} "
          f"({vc_total} slots):")
    print(f"  null={vc_null} ({vc_null/vc_total:.2%})  "
          f"dup={vc_dup} ({vc_dup/vc_total:.2%})  "
          f"unique={vc_uniq} ({vc_uniq/vc_total:.2%})")

    print(f"Kaizo-reclaimed range 0x{kr_lo:04x}..0x{kr_hi:04x} "
          f"({kr_total} slots):")
    print(f"  null={kr_null} ({kr_null/kr_total:.2%})  "
          f"dup={kr_dup} ({kr_dup/kr_total:.2%})  "
          f"unique={kr_uniq} ({kr_uniq/kr_total:.2%})")

    print()
    print(f"First 20 null indices: {[hex(i) for i in null_entries[:20]]}")
    print(f"Last 20 null indices: {[hex(i) for i in null_entries[-20:]]}")

    # Also report null indices specifically inside the vanilla-critical
    # range, since those are the most interesting/surprising if any exist.
    vc_null_indices = [i for i in null_entries if in_range(i, vc_lo, vc_hi)]
    print()
    print(f"Null indices within vanilla-critical range "
          f"(0x{vc_lo:04x}..0x{vc_hi:04x}): "
          f"{[hex(i) for i in vc_null_indices]}")


if __name__ == "__main__":
    main()
