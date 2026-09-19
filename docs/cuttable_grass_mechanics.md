# Cuttable Grass Mechanics in Secret of Evermore

How the engine decides that a terrain tile can be cut away, where that data lives in the ROM, and how `tools/` identifies it.

> **Status:** the identification rule and the ROM layout below are confirmed by a Mesen2 CPU trace plus a whole-ROM structural check (see [§5 Evidence](#5-evidence)). Items that are *not* confirmed are marked **UNVERIFIED** and must not be presented as fact — see `AGENTS.md` §1.
>
> **This document replaces an earlier version that was wrong.** If you have read the "tri-part signature" (CHR tile `0x001` + collision word `0x801F` + a 1×1 Section 3 object with a `LOOT_SNIFF` B-trigger), discard it. [§6](#6-what-the-previous-version-got-wrong) explains what that signature actually described.

---

## 1. The rule

A terrain tile is cuttable **iff its metatile ID appears as a source entry in the room's metatile swap table.**

That is the whole rule. Collision words, CHR tile indices and Section 3 objects play no part in it.

The swap table is a per-room section of the room blob. It is non-empty in exactly **7 of the 127 vanilla rooms**:

| Room | Area | Records | Distinct sources | Cuttable tiles |
|---|---|---:|---:|---:|
| `0x38` | South Jungle | 94 | 72 | **152** |
| `0x69` | Volcano Path | 29 | 29 | **86** |
| `0x41` | North Jungle | 40 | 29 | **54** |
| `0x5B` | East Jungle | 21 | 17 | **41** |
| `0x05` | Antiqua Fields | 9 | 9 | **31** |
| `0x36` | Fire Pits | 5 | 5 | **17** |
| `0x07` | West of Crustacia | 8 | 7 | **5** |

The other 120 rooms carry an empty table (`section_len == 1`, `source_count == 0`) and have no cuttable terrain.

---

## 2. ROM layout: the metatile swap table

The room blob's payload contains an extra section **directly after Block 2** (the Markov metatile grid) and **directly before Block 3** (the 3-slice metatile table). Until this was found, `tools/dump_room.py` skipped straight from one to the other.

```
offset = b2_off + 2 + b2_payload_len          ; == end of Block 2

  [section_len   : 2]     payload byte count that follows
  [source_count  : 1]     number of DISTINCT source metatile IDs
  repeat until section_len is consumed:
      [steps     : 1]     0x01 in every vanilla record  -- UNVERIFIED meaning
      [word      : 2] …   metatile-ID animation sequence
      [0x0000    : 2]     sequence terminator
```

Every vanilla record's sequence is exactly two words, so every record is 7 bytes:

```
01  02 3B  3A 63  00 00      ; metatile 0x3B02 -> 0x633A when cut
01  0A 3B  42 63  00 00      ; metatile 0x3B0A -> 0x6342 when cut
```

- **First word** = the intact metatile ID, exactly as it appears in the room's metatile grid.
- **Following words** = the sequence stamped in its place, one word per animation step. The first step re-stamps the *original* ID (a no-op frame), the last is the cut graphic.
- `0x0000` ends the sequence.

### 2.1 Structural invariants

Both hold in all 7 rooms with no exceptions. `tools/cuttable_grass.py::check_table_invariants` re-checks them; they are integrity checks for ROM hacking, **not** part of the identification rule.

1. `source_count` equals the number of distinct source IDs.
2. The distinct source IDs form a contiguous run starting at the room's `base_metatile` — i.e. metatile indices `0 … N-1`. Cuttable metatiles are always the *first* entries of a room's tileset.

### 2.2 Duplicate source records

Rooms `0x38`, `0x41`, `0x5B` and `0x07` contain records whose source repeats an earlier record (22 of room `0x38`'s 94). **UNVERIFIED:** which record the engine selects. `tools/cuttable_grass.py` keeps the first and preserves the rest in `records`.

---

## 3. Runtime mechanics

### 3.1 The pending-swap queue

Cutting does not patch anything immediately. It enqueues the tile into a 24-slot queue in bank `$8E`, which routine **`$90A6EF`** drains.

| Address | Stride | Meaning |
|---|---|---|
| `$8E0FD0` | — | Round-robin batch cursor; advances by 8 each call, wraps at `0x30` |
| `$8E0FD2,X` | 2 | Cursor: byte offset from the room blob base to the next sequence word. `0x0000` = slot free |
| `$8E1002,X` | 2 | Destination byte offset into the WRAM metatile grid at `$7F0000` |
| `$8E1032,X` | 2 | Low byte = tile X |
| `$8E1033,X` | 2 | Low byte = tile Y |

`$90A6EF` runs once per frame and processes **4 slots per call** (`$42` counts down from 4, `X` += 2 per iteration), then advances `$8E0FD0` by 8 and wraps at `0x30`. Twenty-four slots in batches of four means **each slot advances one animation step every 6 frames** — which is exactly the spacing observed in the trace.

Per slot:

```asm
90A6F7  LDY $0FD2,X          ; sequence cursor; BEQ -> slot empty, skip
90A6FC  LDA [$8B],Y          ; $8B = room blob base ($9E8000 for room 0x38)
90A6FE  BEQ $90A734          ; word == 0 -> STZ $0FD2,X, slot done
90A702  INY / INY            ; advance cursor, store back
90A708  LDA $1002,X          ; destination grid offset
90A750  STA $7F0000,X        ; stamp the metatile ID into the live grid
```

### 3.2 WRAM layout touched by the swap

- **Metatile grid:** `$7F0000 + (tile_y * width_tiles + tile_x) * 2` holds a metatile ID.
- **Metatile definitions:** a metatile ID *is* its own WRAM byte offset. `$7F0000 + id` → Layer 1 VRAM word, `+2` → Layer 2 VRAM word, `+4` → collision word. Entries are 8 bytes, so `metatile_index = (id - base_metatile) / 8`.
- `base_metatile` therefore equals `width_tiles * height_tiles * 2` — the grid ends where the definition table begins.

### 3.3 Cutting does not change collision

**No write anywhere in either captured trace touches the collision words.** Cutting swaps the metatile ID only; the new metatile's own definition supplies the new collision word. Any tool or patch that tries to "restore passability" by writing the collision matrix is modelling the engine incorrectly.

### 3.4 Not yet traced

- **UNVERIFIED:** the weapon-hitbox code path that fills a queue slot. Both traces begin after the slots were already populated.
- **UNVERIFIED:** the meaning of the per-record `steps` byte (hit count? step delay? sequence length?). It is `0x01` in all 206 vanilla records.
- **UNVERIFIED:** whether cut tiles persist across a room reload, and if so where the flag lives.

---

## 4. Tooling

| Symbol | Location | Purpose |
|---|---|---|
| `parse_grass_swap_section(rom, offset)` | `tools/cuttable_grass.py` | Parses the section; returns records, `swaps`, header fields |
| `find_cuttable_grass_tiles(room_data)` | `tools/cuttable_grass.py` | `{(tile_x, tile_y)}` for a dumped room |
| `check_table_invariants(room_data)` | `tools/cuttable_grass.py` | Re-checks §2.1; returns mismatch strings |
| `room_data["cuttable_grass_table"]` | `tools/dump_room.py` | Parsed table, incl. `swaps` (hex keys) and `swaps_int` |
| `room_data["cuttable_grass_tiles"]` | `tools/dump_room.py` | Sorted `(x, y)` list |
| `room_data["cuttable_grass_warnings"]` | `tools/dump_room.py` | Invariant mismatches, empty when well-formed |

`tools/render_map.py` draws cuttable grass as a continuous 2px green contour with a soft green fill, in the same outlined style as the red wall boundary. Cuttable grass is excluded from the collision contour entirely: it is a temporary barrier, not map geometry, so it neither generates a red boundary nor punches a hole in a solid mass.

---

## 5. Evidence

### 5.1 Runtime

Mesen2 CPU trace `cutting_grass_2.txt`, room `0x38`, frames 102103–102156, player cutting grass with the spear.

- Seven slots were active. Their cursors pointed at `$9E96E4/E6`, `$9E9700/02`, `$9E970E/10`, `$9E971C/1E` — i.e. into the records of the table described in §2, inside room `0x38`'s own blob (base `$9E8000`, section at `$9E96E0`).
- Slot tile coordinates from `$8E1032,X`: (26,17) (27,17) (28,17) (27,18) (28,18) (27,19) (28,19).
- Pre-cut metatile IDs `0x3B02 / 0x3B22 / 0x3B32 / 0x3B42` became `0x633A / 0x634A`, matching the table's records exactly.
- Grid offsets `$7F0B3A…$7F0C8A` resolve to those coordinates under `(y * 83 + x) * 2`, and 83 is the room's `width_tiles`.
- Every one of the 7 coordinates is in the set `find_cuttable_grass_tiles(dump_room(0x38))` returns.

An earlier trace, `cutting_grass.txt`, shows the same routine and likewise never writes the collision words.

### 5.2 Static

The section was parsed for all 127 vanilla rooms. It is non-empty in exactly the 7 rooms listed in §1 and empty in the other 120, and both §2.1 invariants hold everywhere. The record stream consumes `section_len` exactly in every room — no truncation, no leftover bytes.

### 5.3 Visual

Room `0x38` was re-rendered and compared tile-by-tile against the composite. Every dark-green sprig tile on the walkable path carries the overlay; no path, canopy or cliff tile does.

---

## 6. What the previous version got wrong

The old "tri-part signature" described **1×1 Section 3 objects whose stamped word matches `(word & 0x03FF) == 0x0001`** — a different mechanism that happens to also exist in these rooms. Its per-room counts (`0x38`=15, `0x5B`=14, `0x41`=21, `0x69`=27, `0x36`=4, `0x05`=13, `0x07`=12) are counts of those objects, not of cuttable tiles.

Specifically:

- **§2.1, CHR tile `0x001`:** the cuttable tiles in room `0x38` carry Layer 1 word `0xA800` and Layer 2 words `0x45C0 / 0x05E0 / 0x05C2 / 0x45CE`. None of them match that mask.
- **§2.2, collision `0x801F / 0x821F / 0x901F`:** every cuttable tile in the traced cluster has collision word `0x001F`. Bit 15 is clear. The claim that cutting rewrites the collision word to `0x0010` is contradicted by §3.3.
- **§2.3, a paired `LOOT_SNIFF` B-trigger:** no B-trigger or script call appears anywhere in the cutting sequence.

**UNVERIFIED:** whether those 1×1 Section 3 objects are *also* cuttable by some other path. They use a different word encoding than metatile IDs and no trace covers them, so `tools/cuttable_grass.py` deliberately does not merge them into its result.

---

## 7. Adding custom cuttable tiles

1. Place the desired grass metatile in the room's metatile grid (Block 2).
2. Add a 7-byte record `01 <src_lo> <src_hi> <dst_lo> <dst_hi> 00 00` to the swap section and update `section_len` and `source_count`.
3. Keep §2.1 satisfied: the source must be within the contiguous run starting at `base_metatile`, which in practice means the cuttable graphics must occupy the first entries of the room's tileset.
4. Make sure `dst` is a valid metatile ID for the same tileset (`base_metatile + 8 * index`, `index < metatile_count`), or the engine will read garbage as the replacement's VRAM and collision words.
5. Run `tools/dump_room.py <room>` and check `cuttable_grass_warnings` is empty.

### Constraints

| Constraint | Limit | Consequence of exceeding |
|---|---|---|
| Section size | `section_len` is a 16-bit count, but the section is bounded by Block 3's start | Overrunning corrupts Block 3 and the metatile table with it |
| Concurrent swaps | 24 queue slots (`$8E0FD2` … `+0x2E`) | **UNVERIFIED** what happens when a 25th tile is cut in the same window |
| Tileset dependency | `dst` must exist in this room's Block 3 table | Out-of-range IDs read arbitrary WRAM as VRAM/collision words |
| Contiguity invariant | Sources must be indices `0 … N-1` | Tools flag it; engine behaviour with a gap is **UNVERIFIED** |
