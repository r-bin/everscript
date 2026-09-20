# Room Blob Encoding

The write path for room data: [`tools/encode_room.py`](file:///Users/v/Documents/GitHub/everscript/tools/encode_room.py) turns a decoded room back into the byte blob the engine loads. It is the inverse of [`tools/dump_room.py`](file:///Users/v/Documents/GitHub/everscript/tools/dump_room.py) (see [`docs/map_decompression_trace_analysis.md`](file:///Users/v/Documents/GitHub/everscript/docs/map_decompression_trace_analysis.md) for the decode side), and is the mechanism a future map editor uses to write an edited map back into the ROM.

> **Status.** The container layout and both compression encoders are verified against all 127 vanilla rooms (see [§4 Verification](#4-verification)). Anything not established that way is marked **UNVERIFIED**, per `AGENTS.md` §1.

---

## 1. Container layout

`dump_room.py` used to *locate* Blocks 2 and 3 by scanning for their dispatcher header signature, because the layout between them wasn't understood. It is now: every section carries its own length, so the whole chain is walkable from the header with no searching. `dump_room.parse_blob_layout()` is the single source of truth for this, and `encode_room.py` writes the identical layout back.

```
+$00            header[13]
+$0D            step_len:2, step-on records (6 bytes each)
                b_len:2,    B-trigger records (6 bytes each)
payload         tile_family_count:1, families (2 bytes each)
extras          extra_count:1, CHR descriptors (3 bytes each)
block1          payload_len:2, sub_flag:1, decomp_size:2, data
section2        count:1, len:2, animated-tile descriptors
section3        object_count:1, object offsets (2 bytes each)
block2          payload_len:2, sub_flag:1, decomp_size:2, data
section4        len:2, $0FC4:1, metatile swap records (docs/cuttable_grass_mechanics.md)
block3          payload_len:2, sub_flag:1, decomp_size:2, data
object_area     object records and their stamping blocks
```

`payload_len` counts the sub_flag byte, the decomp_size word, and the data: `3 + len(data)`.

### 1.1 The bug this fixed

The old signature scan for Block 3 only accepted `sub_flag == 0x03` (LZSS). **Room `0x15`'s Block 3 is `sub_flag == 0x00`** (uncompressed, 12 bytes) — the scan skipped past it and locked onto an unrelated block 127 bytes later, so `dump_room` reported **10 920 metatiles for a room that has 2**. `parse_blob_layout()` reads the length fields instead of guessing, so this is fixed for both the reader and the writer.

### 1.2 Compression sub_flags

Per the engine's dispatcher at `$8C98A1`:

| `sub_flag` | Algorithm |
|---|---|
| `0x00` | Uncompressed copy (`$8C98B1`) |
| `0x03` | LZSS sliding window (`$8C98C9`) |
| `0x07` | 2D context-predictive Markov bitstream (`$8C9B65`) |

Blocks 1 and 3 occur with both `0x00` and `0x03` in vanilla rooms — either is legal to emit. Block 2 is `0x07` in all 127 rooms; the grid is always Markov-encoded.

---

## 2. Encoders

### 2.1 LZSS (`lzss_compress`)

Inverse of `dump_room.LZSSDecompressor` (`$8C98C9`). Token format:

```
bit 1              -> 8-bit literal follows
bit 0              -> 16-bit token: offset = token >> 4 (0 ends the stream),
                      length = (token & 0x0F) + 2,
                      source read from window index (offset - 1) & 0xFFF
```

The subtlety is **self-overlapping matches**: the decoder writes each copied byte back into its 4 KB window as it goes, so a match can read bytes it has just produced (e.g. compressing a long run of one byte). The match-length probe in `lzss_compress` simulates that write-as-you-read behaviour explicitly; treating the window as static during the search corrupts any match longer than its own distance.

The compressor is a greedy longest-match search with a hash-chain index (`max_candidates` recent positions per 3-byte key), not an optimal parse — it isn't guaranteed to find the shortest possible encoding, only a correct and usually-smaller one.

### 2.2 Markov grid (`encode_markov_grid`)

Inverse of `dump_room.decompress_markov_grid` (`$8C9BD0`). The decoder keeps, per metatile ID, a 4-slot context `[above0, left1, above2, left3]`, and at each cell reads one of six prefix-free tokens:

| Token | Bits | Meaning |
|---|---|---|
| `1` | 1 | `table[above][0]` |
| `000` | 3 | `table[left][1]` |
| `0011` | 4 | the next sequential metatile (and widens the literal field) |
| `00100` | 5 | `table[above][2]` |
| `00101` | 5 | `table[left][3]` |
| `01` + `tile_bits` | 2 + N | literal metatile index |

The encoder runs the identical context model forward and picks the cheapest token that reproduces the wanted value, with one rule: when the value *is* the next sequential metatile it always emits `0011`, because that is the only token that widens `tile_bits` — and the literal token needs that width to address newly-introduced metatiles. This means **a grid must introduce new metatile IDs in ascending sequential order** (as the original decompressor's own output always does); introducing one out of order raises `ValueError` rather than silently emitting an unrepresentable stream.

Verified to reproduce the **exact original bitstream, byte-for-byte, for all 127 vanilla rooms** — encoding an untouched grid costs nothing.

### 2.3 Block 1 (`encode_block1`) and Block 3 (`encode_block3`)

Block 1 is a CHR tile palette stored as 16-bit deltas that the engine accumulates at `$908E85`; `dump_room` reports the accumulated values, so `encode_block1` differentiates them back before compressing.

Block 3 is the three planar slices — Layer 1 words, Layer 2 words, collision words — concatenated in that order, each slice `metatile_count` words long.

### 2.4 Choosing the smallest encoding (`_wrap`)

Every block encoder picks whichever of {raw, LZSS} is smaller, and — critically — **reuses the original payload untouched when its decoded content hasn't changed**, even if the original happens to be smaller than anything this LZSS implementation would produce for the same bytes. Without that check, re-encoding a room an editor didn't actually touch could still grow it by a few bytes purely from this compressor's implementation not matching whatever the original tool was.

### 2.5 Object area (`build_object_area`, `_pack_overlapping`)

Objects are `max_state:1` + 5-byte states `[width, tile_x, tile_y, target_off:2]`; each state points at a stamping block `[target_width, target_height, metatiles...]`. Offsets are relative to the start of the object area.

Vanilla rooms **overlap** stamping blocks that share a suffix/prefix — room `0x09` has 15 of its 24 blocks overlapping their neighbour; room `0x06` has 434- and 1298-byte blocks overlapping by dozens of bytes. `_pack_overlapping` reproduces this with the standard shortest-common-superstring heuristic: drop blocks fully contained in another, then repeatedly merge the pair with the largest suffix/prefix overlap. Skipping this step doesn't corrupt anything, but the object area alone accounts for **8 954 of the 12 136 bytes** the full rebuild saves across the ROM (see §4.2) — most of a room's redundancy lives here, not in the compressed blocks.

---

## 3. Writing a blob into a ROM (`write_room_into_rom`)

Rooms are reached through a 4-byte pointer table at `$9FFDE7` (`MAP_LIST_ADDR`). Two modes:

- **In place** (`at_offset` omitted): only legal when the rebuilt blob is no larger than the room's current footprint; raises otherwise rather than clobbering the next room's data. §4.2 shows this always succeeds for an unmodified re-encode.
- **Relocated** (`at_offset` given): writes the blob elsewhere and repoints the table entry. Refuses to cross a HiROM bank boundary, since the loader walks a blob using 16-bit offsets from its own bank's base.

---

## 4. Verification

### 4.1 Byte-exact round-trip

`model_from_rom()` extracts a lossless model; `build_blob()` serialises it. For every one of the 127 vanilla rooms, `build_blob(model_from_rom(rom, room_id))` reproduces the **original bytes exactly**:

```bash
python3 tools/encode_room.py --verify
# byte-exact round-trip: 127/127 rooms
```

This is the proof that the container layout in §1 is understood, not merely parsed.

### 4.2 Full rebuild, size and content

`rebuild_model()` re-encodes every block from decoded content — the path an editor takes after changing something. Checked for all 127 rooms:

- **Never larger than the original.** Total across all 127 rooms: **-12 136 bytes** (the rebuild is smaller, from tighter object-area packing and this LZSS implementation beating the original tool on some blocks); **zero rooms grow**.
- **Decodes back identically.** Re-parsing a rebuilt blob reproduces the same metatile grid, the same three metatile-table slices, and the same object list.

```bash
python3 tools/encode_room.py --verify-rebuild
# re-encoded round-trip:  127/127 rooms
```

### 4.3 End-to-end

`tests/integration/maps/test_encode_room.py::test_rebuilt_room_matches_when_dumped_again` closes the loop for a sample of rooms: decode → `rebuild_model()` → `write_room_into_rom()` → write to a `.smc` file → `dump_room()` the result → compare every field against the original decode. A companion test confirms neighbouring rooms are byte-identical after an in-place write.

Run the suite:

```bash
.venv/bin/pytest tests/integration/maps/test_encode_room.py -v
```

---

## 5. CLI

```bash
# Inspect a room's blob as the lossless model would serialise it
python3 tools/encode_room.py 0x38

# Re-encode every block from decoded content, LZSS where it helps
python3 tools/encode_room.py 0x38 --rebuild --compress --out room38.bin

# Full-ROM checks
python3 tools/encode_room.py --verify           # byte-exact round-trip
python3 tools/encode_room.py --verify-rebuild   # re-encoded round-trip
```

---

## 6. Open questions

- **UNVERIFIED:** the per-record `steps` byte format elsewhere in Section 4 (see `docs/cuttable_grass_mechanics.md`) is untouched by this module; it is copied through as opaque bytes.
- **UNVERIFIED:** whether the game enforces any constraint on Section 3 payload size beyond the space physically available before the next room blob — relevant when relocating is not an option.
- **UNVERIFIED:** the LZSS encoder here is not proven to match whatever produced the vanilla data byte-for-byte on *new* content — only that its output decodes correctly and is smaller.
