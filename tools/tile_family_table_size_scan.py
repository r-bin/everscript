#!/usr/bin/env python3
"""
Throwaway verification script for docs/rom-extension-wishlist.md item 7
("More tiles / tile families") -- second half of the investigation.

Purpose: characterize the actual SIZE of the master Tile Family (palette)
table at $9CC322 (ROM file offset 0x1CC322), per the disassembly-verified
32-bytes-per-family stride documented in docs/map_palette_extraction.md
Section 2/3. This does NOT re-derive the stride or the DMA mechanism --
those are already disassembly-verified in that doc. This script only asks:
how many distinct family_id values does vanilla actually reference, and
does the table look like it has any padding/free space near the highest
referenced entry (same methodology as scratch/string_key_null_scan.py used
for wishlist item 6).

Method:
1. Call tools/dump_room.dump_room() for all 127 vanilla rooms and collect
   every referenced tile_family id.
2. Report the max referenced id, and the implied table byte-span
   (0x1CC322 .. 0x1CC322 + (max_id+1)*32).
3. Read 256 bytes of raw ROM data starting right after the last referenced
   family's 32-byte block, and check whether it looks like more valid
   palette data (plausible BGR555 words, i.e. bit 15 clear) or something
   else (garbage / a different table / all-same-byte padding).
4. Also report how many of the 0..max_id range are actually referenced by
   at least one room (to see whether the id space is dense or sparse --
   sparseness would suggest rooms cherry-pick from a larger, mostly-unused
   pre-existing catalog rather than the catalog being sized exactly to
   what's used).

This is a static byte-pattern read of the raw ROM file plus this repo's own
tools/dump_room.py parser -- no live emulator, no disassembler. Not proof of
an engine-enforced table boundary, just evidence about what bytes physically
look like there and which ids vanilla content actually touches.
"""
import os
import sys

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(REPO_ROOT, "tools"))

from dump_room import dump_room, MAX_ROOMS  # noqa: E402

ROM_PATH = os.path.join(REPO_ROOT, "Secret of Evermore (U) [!].smc")
TABLE_BASE = 0x1CC322  # $9CC322, per docs/map_palette_extraction.md Section 2
STRIDE = 32


def main():
    rom = open(ROM_PATH, "rb").read()

    all_ids = set()
    per_room_counts = []
    for rid in range(MAX_ROOMS):
        res = dump_room(rid, ROM_PATH)
        fams = [int(x, 16) for x in res["tile_families"]]
        per_room_counts.append(len(fams))
        all_ids.update(fams)

    max_id = max(all_ids)
    min_id = min(all_ids)
    print(f"Rooms scanned: {MAX_ROOMS}")
    print(f"Distinct tile_family ids referenced across all rooms: {len(all_ids)}")
    print(f"Range referenced: {min_id} (0x{min_id:04X}) .. {max_id} (0x{max_id:04X})")
    print(f"Dense-id-space occupancy: {len(all_ids)}/{max_id - min_id + 1} "
          f"({100*len(all_ids)/(max_id - min_id + 1):.1f}%)")
    print(f"Per-room family count: min={min(per_room_counts)}, "
          f"max={max(per_room_counts)}, "
          f"rooms with count==7: {sum(1 for c in per_room_counts if c == 7)}, "
          f"rooms with count>7: {sum(1 for c in per_room_counts if c > 7)}")

    last_block_start = TABLE_BASE + max_id * STRIDE
    last_block_end = last_block_start + STRIDE
    print(f"\nHighest referenced family's 32-byte block: "
          f"file 0x{last_block_start:06X}..0x{last_block_end:06X}")

    # Read 256 bytes right after the highest *referenced* family's block.
    tail = rom[last_block_end:last_block_end + 256]
    print(f"\n256 bytes immediately after the highest-referenced family block "
          f"(file 0x{last_block_end:06X}):")
    for row in range(0, 256, 16):
        chunk = tail[row:row + 16]
        print("  " + " ".join(f"{b:02X}" for b in chunk))

    # Heuristic: does this tail data look like more valid BGR555 palette
    # words (bit 15 of every 16-bit LE word clear), the same shape check
    # used implicitly by extract_tile_family_palette()?
    words = [tail[i] | (tail[i+1] << 8) for i in range(0, len(tail) - 1, 2)]
    bit15_clear = sum(1 for w in words if (w & 0x8000) == 0)
    print(f"\nOf {len(words)} 16-bit LE words in that tail: "
          f"{bit15_clear} have bit15 clear (valid-BGR555-shaped), "
          f"{len(words) - bit15_clear} have bit15 set.")

    # Also check for a run of identical bytes (padding/free-space signal),
    # same methodology as the string_key free-space scan.
    run_len = 1
    best_run = (1, tail[0] if tail else None)
    for i in range(1, len(tail)):
        if tail[i] == tail[i - 1]:
            run_len += 1
            if run_len > best_run[0]:
                best_run = (run_len, tail[i])
        else:
            run_len = 1
    print(f"\nLongest identical-byte run in that 256-byte tail: "
          f"{best_run[0]} bytes of 0x{best_run[1]:02X}" if best_run[1] is not None
          else "no data")


if __name__ == "__main__":
    main()
