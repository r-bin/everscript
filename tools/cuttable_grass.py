#!/usr/bin/env python3
"""
Cuttable Grass Patch Identification
------------------------------------
Identifies the terrain tiles a weapon can cut away, from the room's own ROM
payload.  Supersedes the CHR-tile / collision-word heuristics described in
docs/cuttable_grass_mechanics.md §2.1-§2.3 (see "Correction" below).

Mechanism (confirmed empirically, see "Evidence")
-------------------------------------------------
A room blob's compressed payload contains an extra section directly after
Block 2 (the Markov metatile grid) and directly before Block 3 (the 3-slice
metatile table).  `tools.dump_room` previously skipped straight from one to
the other; the bytes in between are a **metatile swap table**:

    [section_len : 2]          number of payload bytes that follow
    [source_count: 1]          number of DISTINCT source metatile IDs
    repeated until section_len is consumed:
        [steps  : 1]           always 0x01 in vanilla - meaning unconfirmed
        [word   : 2] ...       metatile-ID animation sequence
        [0x0000 : 2]           sequence terminator

In every vanilla record the sequence is exactly two words: `[source, cut]`.
`source` is the intact metatile ID as it appears in the room's metatile grid;
`cut` is the metatile ID stamped in its place once the tile is destroyed.

So: **a terrain tile is cuttable iff its metatile ID appears as the `source`
word of a record in this table.**  No collision-word test, no CHR-tile test,
no Section 3 object is involved.

Evidence
--------
1. Runtime, Mesen2 CPU trace `cutting_grass_2.txt` (Room 0x38, Fr 102103-102156,
   the player cutting a grass patch with the spear):
     - Routine $90A6EF walks up to 6 pending "tile swap" slots (round-robin via
       $8E0FD0).  Per slot it reads the next word of the sequence with
       `LDA [$8B],Y` where $8B = $9E8000 = this room's blob base and Y is the
       per-slot cursor at $8E0FD2,X; it stamps that word into the live WRAM
       metatile grid at $7F0000 + $8E1002,X, then advances the cursor by 2.
       A word of $0000 ends the sequence (`STZ $0FD2,X` at $90A734).
     - The seven cursors observed pointed at $9E96E4, $9E96E6, $9E9700,
       $9E9702, $9E970E, $9E9710, $9E971C, $9E971E - i.e. exactly into the
       records of the table described above, inside room 0x38's own blob
       (blob base $9E8000, section at $9E96E0).
     - Per-slot tile coordinates are held at $8E1032,X (x) and $8E1033,X (y).
       The seven cut tiles were (26,17) (27,17) (28,17) (27,18) (28,18)
       (27,19) (28,19); their pre-cut metatile IDs 0x3B02/0x3B22/0x3B32/0x3B42
       became 0x633A/0x634A - matching this table's records exactly.
     - No write anywhere in either trace touches the collision-word mirror.
       Cutting does not patch collision; it only swaps the metatile ID.
2. Static, whole-ROM: the section is non-empty in exactly 7 of the 127 vanilla
   rooms - 0x05, 0x07, 0x36, 0x38, 0x41, 0x5B, 0x69 - which is precisely the
   set of rooms docs/cuttable_grass_mechanics.md §6 lists as the cuttable-grass
   rooms.  The other 120 rooms carry an empty section (`section_len == 1`,
   `source_count == 0`).
3. In all 7 rooms the distinct source IDs form a contiguous run starting at the
   room's `base_metatile` (indices 0..N-1), and `source_count` equals the number
   of distinct sources.  Both hold with no exceptions, so they are used as
   integrity checks rather than as the identification rule itself.

Correction to docs/cuttable_grass_mechanics.md
----------------------------------------------
MISMATCH: §2.1 (CHR tile #0x001), §2.2 (collision words 0x801F/0x821F/0x901F)
and §2.3 (1x1 Section 3 object with a LOOT_SNIFF B-trigger) do NOT describe
cuttable grass terrain.  The §6 per-room counts (0x38=15, 0x5B=14, 0x41=21,
0x69=27, 0x36=4, 0x05=13, 0x07=12) count 1x1 Section 3 objects, not cuttable
tiles.  The real per-room cuttable tile counts from the swap table are
0x38=152, 0x69=86, 0x41=54, 0x5B=41, 0x05=31, 0x36=17, 0x07=5.
TODO: whether those 1x1 Section 3 objects are *also* cuttable is unverified -
they use a different word encoding than metatile IDs and no trace covers them,
so they are deliberately NOT merged into the result here.
TODO: the per-record `steps` byte is 0x01 in every vanilla record; its meaning
(hit count? animation delay? sequence length?) is unknown.
"""

from typing import Dict, List, Set, Tuple

# Record framing, per the layout documented above.
SEQUENCE_TERMINATOR = 0x0000


def _as_int(value) -> int:
    """dump_room stores grids as '0xABCD' strings; accept either form."""
    return int(value, 16) if isinstance(value, str) else int(value)


def parse_grass_swap_section(rom: bytes, offset: int) -> dict:
    """
    Parse the metatile swap table that sits between Block 2 and Block 3 of a
    room blob.

    Args:
        rom:    ROM byte buffer.
        offset: ROM file offset of the section header, i.e. the byte directly
                after Block 2's payload (`b2_off + 2 + b2_payload_len`).

    Returns:
        {
          "rom_offset":    int,
          "section_len":   int,   # header word: payload byte count
          "source_count":  int,   # header byte: number of distinct sources
          "records":       [ {"steps": int, "source": int, "sequence": [int]} ],
          "swaps":         {source_metatile_id: cut_metatile_id},
          "truncated":     bool,  # True if a record ran past the section end
        }
        For a room without cuttable grass this is an empty table
        (section_len == 1, source_count == 0, no records).
    """
    section_len = rom[offset] | (rom[offset + 1] << 8)
    end = min(offset + 2 + section_len, len(rom))
    source_count = rom[offset + 2] if offset + 2 < len(rom) else 0

    records: List[dict] = []
    truncated = False
    p = offset + 3
    while p < end:
        steps = rom[p]
        q = p + 1
        sequence: List[int] = []
        while True:
            if q + 2 > end:
                truncated = True
                break
            word = rom[q] | (rom[q + 1] << 8)
            q += 2
            if word == SEQUENCE_TERMINATOR:
                break
            sequence.append(word)
        if truncated:
            break
        p = q
        if sequence:
            records.append({
                "steps": steps,
                "source": sequence[0],
                "sequence": sequence[1:],
            })

    # First-match-wins: duplicate source records exist (e.g. 22 of room 0x38's
    # 94 records repeat an earlier source).  Which one the engine picks is not
    # established, so keep the first and leave the rest in `records`.
    swaps: Dict[int, int] = {}
    for rec in records:
        if rec["source"] not in swaps:
            swaps[rec["source"]] = rec["sequence"][-1] if rec["sequence"] else rec["source"]

    return {
        "rom_offset": offset,
        "section_len": section_len,
        "source_count": source_count,
        "records": records,
        "swaps": swaps,
        "truncated": truncated,
    }


def cuttable_metatile_ids(room_data: dict) -> Set[int]:
    """The set of metatile IDs this room treats as cuttable terrain."""
    table = room_data.get("cuttable_grass_table") or {}
    # dump_room stores a hex-string-keyed "swaps" for readability plus an
    # int-keyed "swaps_int"; parse_grass_swap_section returns only "swaps".
    swaps = table.get("swaps_int") or table.get("swaps") or {}
    return {_as_int(k) for k in swaps}


def find_cuttable_grass_tiles(room_data: dict) -> Set[Tuple[int, int]]:
    """
    Returns the set of room-local (tile_x, tile_y) coordinates whose terrain
    metatile is cuttable, for a room dumped by tools.dump_room.dump_room().

    Empty for the 120 vanilla rooms that carry no swap table.
    """
    sources = cuttable_metatile_ids(room_data)
    if not sources:
        return set()

    tiles: Set[Tuple[int, int]] = set()
    for y, row in enumerate(room_data.get("layer1_metatile_ids", [])):
        for x, value in enumerate(row):
            if _as_int(value) in sources:
                tiles.add((x, y))
    return tiles


def check_table_invariants(room_data: dict) -> List[str]:
    """
    Re-check the two structural invariants observed across all 7 vanilla
    cuttable-grass rooms.  Returns a list of human-readable mismatch strings
    (empty when the table looks well-formed).  Intended for ROM-hack sanity
    checking, not as part of the identification path.
    """
    table = room_data.get("cuttable_grass_table") or {}
    problems: List[str] = []
    if table.get("truncated"):
        problems.append("record ran past the declared section length")

    sources = sorted(cuttable_metatile_ids(room_data))
    if not sources:
        return problems

    declared = table.get("source_count", 0)
    if declared != len(sources):
        problems.append(
            f"header source_count {declared} != {len(sources)} distinct source IDs")

    base = _as_int(room_data.get("base_metatile", 0))
    indices = [(s - base) // 8 for s in sources]
    if indices != list(range(len(indices))):
        problems.append(
            f"source metatile indices are not the contiguous run 0..{len(indices) - 1}: {indices}")
    return problems
