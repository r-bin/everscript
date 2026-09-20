---
name: rom-map-data
description: Secret of Evermore map data in ROM -- room blob layout, the three compressed payload blocks, the collision word bitfield, and which document answers which question. Start here for anything about map/room binary format.
---

# ROM Map Data & Tilemap Architecture

How Secret of Evermore stores, decompresses, re-encodes, and renders map data. The format is
**fully decoded in both directions** -- `tools/encode_room.py` round-trips every one of the 127
rooms byte-exactly -- so treat what follows as established fact, not a work in progress, except
where a line is explicitly marked UNVERIFIED.

## 0. Which document answers which question

This skill is the map-data index. The detail lives in `docs/`:

| Question | Document |
|---|---|
| Where is each room in ROM? How big? Which rooms use elevation planes? | [.github/rom-map.md](file:///Users/v/Documents/GitHub/everscript/.github/rom-map.md) -- all 127 blobs, offsets, sizes, compression flags |
| How was the decompression pipeline reverse-engineered? | [docs/map_decompression_trace_analysis.md](file:///Users/v/Documents/GitHub/everscript/docs/map_decompression_trace_analysis.md) |
| How do I write a room *back* to the ROM? | [docs/map_encoding.md](file:///Users/v/Documents/GitHub/everscript/docs/map_encoding.md) -- container layout, LZSS + Markov encoders, the never-grows guarantee |
| What does a collision word mean? Planes, drift, entity gates? | [docs/map_collision_mechanics.md](file:///Users/v/Documents/GitHub/everscript/docs/map_collision_mechanics.md) |
| How does cuttable grass work? | [docs/cuttable_grass_mechanics.md](file:///Users/v/Documents/GitHub/everscript/docs/cuttable_grass_mechanics.md) |
| How are Section 3 objects structured? | [docs/map_objects.md](file:///Users/v/Documents/GitHub/everscript/docs/map_objects.md) |
| How do I turn a room into a PNG? Mode 1 compositing? | [docs/map_rendering_pipeline.md](file:///Users/v/Documents/GitHub/everscript/docs/map_rendering_pipeline.md) |
| How are CHR tile graphics decompressed? | [docs/map_tile_graphics_decompression.md](file:///Users/v/Documents/GitHub/everscript/docs/map_tile_graphics_decompression.md) |
| How are palettes built? | [docs/map_palette_extraction.md](file:///Users/v/Documents/GitHub/everscript/docs/map_palette_extraction.md) |
| What would a map editor look like? What's still missing? | [docs/map_editor_design.md](file:///Users/v/Documents/GitHub/everscript/docs/map_editor_design.md), [docs/map_editor_architecture_and_limitations.md](file:///Users/v/Documents/GitHub/everscript/docs/map_editor_architecture_and_limitations.md) |

---

## 1. Room Header & Trigger Table Structure

Each of the 127 maps in the game (`0x00` through `0x7E`) is referenced via the master **Map Pointer Table** in ROM (`$9FFDE7` / ROM file `0x1FFDE7`). The table entry at `0x7F` is **not** a room -- see `.github/rom-map.md` §2 for the check that proves it:
- The pointer table uses a **4-byte stride** per room (`table + room_id * 4`), with each entry containing a 24-bit pointer plus 1 padding byte.
- The room blob begins with a **13-byte header** (offsets `$00..$0C`), read by the engine loader at `$908F80..$909050`:

| Offset | Size | Field | Engine Destination / Mechanism | Description |
|---|---|---|---|---|
| `$00` | 1 | `origin_x` | `STA $0F86` | Trigger origin X offset (added to Player Tile X in trigger checks) |
| `$01` | 1 | `origin_y` | `STA $0F88` | Trigger origin Y offset (added to Player Tile Y in trigger checks) |
| `$02` | 1 | `width_tiles` | `STA $08EE` | Map width in 16×16 metatiles (`$0F46` = stride $W \times 2$, `$7E23ED` = max X $W \times 16$) |
| `$03` | 1 | `height_tiles` | `STA $08F0` | Map height in 16×16 metatiles (`$7E23EF` = max Y $H \times 16$) |
| `$04` | 1 | `display_tm` | `STA $212C`, `STA $0F80` | SNES PPU Main Screen Designation |
| `$05` | 1 | `subscreen_ts` | `STA $212D`, `STA $0F81` | SNES PPU Sub Screen Designation |
| `$06` | 1 | `color_math` | `STA $2131`, `STA $0F82` | SNES PPU CGADSUB (Color Math Designation) |
| `$07` | 1 | `color_window` | `STA $2130`, `STA $0F83` | SNES PPU CGWSEL (Color Addition Select) |
| `$08` | 1 | `effect_variant` | `STA $7E241F` | Room visual effect variant (indexes effect jump table at `$908E74`) |
| `$09..$0A`| 2 | `word_0f84` | `STA $0F84` | 16-bit parameter loaded via `REP #$21; LDA [$8B],Y` |
| `$0B..$0C`| 2 | `padding_0b` | *(skipped)* | 2 bytes skipped by `INY; INY` |

### Trigger Tables (Offset `$0D`)

- **Offset `$0D`**: 16-bit word `step_len` stored at `$1062` (total byte length of step-on trigger table).
- **Offset `$0F`**: Start of step-on trigger records (`$1064 = blob + 15`), 6 bytes per entry:
  - `Byte 0`: `y_min` (tested against Player Y)
  - `Byte 1`: `x_min` (tested against Player X)
  - `Byte 2`: `y_max` (tested against Player Y)
  - `Byte 3`: `x_max` (tested against Player X)
  - `Bytes 4..5`: 16-bit little-endian `script_id`
- **Offset `$0F + step_len`**: 16-bit word `b_len` stored at `$1067` (total byte length of B-trigger table).
- **Offset `$0F + step_len + 2`**: Start of B-trigger records (`$1069`), 6 bytes per entry with identical coordinate fields.

---

## 2. Coordinate Spaces & Trigger Evaluation

Evermore operates across two distinct coordinate planes:

| Coordinate Plane | Scale | Typical Usage |
|---|---|---|
| **Pixel Coordinates** | 1:1 ($256 \times 224$ screen space) | Sprite rendering, projectile hits, camera tracking |
| **Tile Coordinates** | 1:16 ($X_{pix} / 16$, $Y_{pix} / 16$) | 16×16 metatile grid, step-on triggers, B-triggers |

> [!IMPORTANT]
> **Metatile Scale is Strictly 1:16 (Never 1:8)**  
> The engine evaluation routine at `$8FACCE..$8FACE4` performs four consecutive arithmetic right shifts (`LSR A` $\times 4$) on player pixel coordinates, strictly dividing by 16:
> $$\text{Tile X} = X_{pix} \gg 4, \quad \text{Tile Y} = Y_{pix} \gg 4$$
> For example, spawn coordinates `0x0180` and `0x02C0` (384, 704 pixels) correspond to tile coordinates `(24, 44)`.

### Engine Trigger In-Bounds Check (`$8FACEF..$8FAD08`)

A trigger activates when the player coordinates satisfy:
$$y_{min} \le (\text{Tile Y} + origin\_y) < y_{max} \quad \text{AND} \quad x_{min} \le (\text{Tile X} + origin\_x) < x_{max}$$

---

## 3. Map Compression & Deterministic Payload Architecture

Secret of Evermore uses a multi-stage payload architecture across three compressed ROM blocks, fully documented in [**`docs/map_decompression_trace_analysis.md`**](file:///Users/v/Documents/GitHub/everscript/docs/map_decompression_trace_analysis.md).

The SNES engine loader (`$908F60..$909180`) resolves all payload sub-blocks **100% deterministically without linear heuristic scanning**:

1. **Master Map Pointer Table (`$9FFDE7` / ROM `0x1FFDE7`)**:
   - 4-byte stride per room ID (`table + room_id * 4`) pointing to 24-bit SNES address of the room blob.
   - The room blob begins with a 13-byte header and trigger tables (see §1).

2. **Tile Families & CHR Descriptors**:
   - Begins at `fam_off = blob + 15 + step_len + 2 + b_len`:
     - `rom[fam_off]`: Count $N$ of 16-bit tile families, followed by $N \times 2$ bytes.
   - Immediately following at `pos_desc = fam_off + 1 + N * 2`:
     - `rom[pos_desc]`: Count $M$ of 3-byte CHR tile graphics descriptors (`JSL $90D50F`), followed by $M \times 3$ bytes.

3. **Payload Block 1 (Delta Tile Palette)**:
   - Starts at `pos_after_desc = pos_desc + 1 + M * 3`.
   - `b1_len = read16(rom, pos_after_desc)` (16-bit block length).
   - Subheader at `pos_after_desc + 2`: `[sub_flag: 1 byte][decomp_size: 2 bytes][data...]`.
     - **In 115 rooms:** `sub_flag == 0x03` $\to$ decompressed via **LZSS** (`$8C98C9`) into WRAM `$7FC300`.
     - **In 12 rooms:** `sub_flag == 0x00` $\to$ raw **uncompressed copy** (`$8C98B1`) into WRAM `$7FC300`.
   - In-place **16-bit delta accumulator** (`$908E85`) converts deltas into absolute 16×16 CHR graphic IDs.
   - Subroutine `$8CC88C` looks up graphic pointers in the **`$EE0000` table** (`tile_id * 3`) and DMAs 4bpp pixel patterns to SNES VRAM character slots.

4. **Intermediate Descriptors to Block 2**:
   - Section 2 at `sec2 = pos_after_desc + 2 + b1_len`:
     - `rom[sec2]`: Count $P$, followed by `L_2 = read16(rom, sec2 + 1)`, followed by $L_2$ bytes.
   - Section 3 at `sec3 = sec2 + 3 + L_2`:
     - `K = rom[sec3]`: Count of 2-byte descriptors, followed by $K \times 2$ bytes.

5. **Payload Block 2 (2D Markov Metatile Grid)**:
   - Starts at `b2_off = sec3 + 1 + K * 2`.
   - `b2_len = read16(rom, b2_off)` (16-bit block length).
   - Subheader: `sub_flag == 0x07`, `decomp_size == width_tiles * height_tiles * 2`.
   - Decompressed via **2D Context-Predictive Markov Bitstream Decoder** (`$8C9BD0`) directly into WRAM **`$7F0000`**.
   - **Metatile ID as Direct WRAM Bank `$7F` Offset**:
     - `base_metatile = width_tiles * height_tiles * 2`.
     - Metatiles are aligned on 8-byte boundaries: `ID = base_metatile + (index * 8)`.

6. **Payload Block 3 (3-Slice Planar Multi-Layer Metatile Table)**:
   - Intermediate Section 4 at `sec4 = b2_off + 2 + b2_len`:
     - `L_4 = read16(rom, sec4)`, followed by $L_4$ bytes.
   - Block 3 starts deterministically at `b3_off = sec4 + 2 + L_4`:
     - `b3_len = read16(rom, b3_off)` (16-bit block length).
     - Subheader: `[sub_flag: 1 byte][decomp_size: 2 bytes]`.
     - **In 126 rooms:** `sub_flag == 0x03` $\to$ decompressed via **LZSS** (`$8C988D`).
     - **In Room 0x15 (Brian's Test Ground):** `sub_flag == 0x00` $\to$ raw **uncompressed copy** of 12 bytes (2 metatiles).
   - Routine `$9091B0..$909245` divides decompressed bytes by 6 using hardware math registers (`STA $4206`) and unpacks data into **3 planar slices**:
     - **Slice 0 (Words $0 \dots N-1$)**: **Layer 1 (Canopy / BG2)** SNES VRAM tilemap words.
     - **Slice 1 (Words $N \dots 2N-1$)**: **Layer 2 (Terrain / BG1)** SNES VRAM tilemap words.
     - **Slice 2 (Words $2N \dots 3N-1$)**: **Collision & Passability Attributes** (walkable ground, solid barriers, elevation levels).
   - In WRAM, each metatile receives an 8-byte entry starting at `$7F0000 + base_metatile + (i * 8)`:
     - `+$00`: Layer 1 VRAM tilemap word (16-bit)
     - `+$02`: Layer 2 VRAM tilemap word (16-bit)
     - `+$04`: Collision / passability attributes (16-bit)
     - `+$06`: Markov prediction context slot (16-bit)

6. **Tilemap Streaming (`$909460`)**:
   - Reads metatile offsets from `$7F0000 + (r * width + c) * 2`.
   - Uses the metatile ID directly as an indexed indirect offset:
     ```assembly
     909460  LDY $0000,X [$7F0000 + offset] ; Load Metatile ID (base_metatile + i * 8)
     909463  LDA ($26),Y                    ; Lookup VRAM tilemap word directly in Bank $7F
     909465  STA VMDATAL                    ; Stream to SNES PPU VRAM register ($2118)
     ```

---

## 4. Reverse-Engineering Tools & Verification Suite

1. **`tools/dump_room.py` Extractor**:
   - Located at [**`tools/dump_room.py`**](file:///Users/v/Documents/GitHub/everscript/tools/dump_room.py). Pure-Python decompressor extracting map headers, tile palettes, metatile grids, and VRAM tilemaps directly from clean ROM bytes:
     ```bash
     # Inspect map metadata, metatiles, and VRAM words:
     python3 tools/dump_room.py 0x33
     python3 tools/dump_room.py 0x38

     # Export Layer 1 (Canopy/BG2) raw SNES VRAM tilemap bytes (matching emulator PPU dumps):
     python3 tools/dump_room.py 0x33 --vram-bytes
     python3 tools/dump_room.py 0x38 --vram-bytes --layer 1

     # Export Layer 2 (Terrain/BG1) raw SNES VRAM tilemap bytes:
     python3 tools/dump_room.py 0x38 --vram-bytes --layer 2

     # Export VRAM words with optional 32-tile buffer row padding:
     python3 tools/dump_room.py 0x33 --vram-words --pad-32
     ```
2. **Automated Integration Tests (`tests/integration/maps/`)**:
   - The test suite validates decoded VRAM tilemap words and bytes against ground-truth Mesen2 PPU dumps:
     - [`test_room_0x33_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x33_vram.py): Room 0x33 (Strong Heart's Exterior, $20 \times 16$)
     - [`test_room_0x34_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x34_vram.py): Room 0x34 (Strong Heart's Hut, $18 \times 18$)
     - [`test_room_0x38_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x38_vram.py): Room 0x38 (South Jungle, $83 \times 91$)
     - [`test_room_0x25_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x25_vram.py): Room 0x25 (Fire Eyes' Village, $63 \times 58$)
     - [`test_room_0x26_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x26_vram.py): Room 0x26 (West Area with Defend, $19 \times 18$)
     - [`test_room_0x36_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x36_vram.py): Room 0x36 (Volcano Fire Pits, $25 \times 25$)
     - [`test_room_0x51_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x51_vram.py): Room 0x51 (Village Huts & Blimp's Hut, $50 \times 56$)
     - [`test_room_0x5b_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x5b_vram.py): Room 0x5B (East Jungle, $72 \times 48$)
   - Run via:
     ```bash
     .venv/bin/pytest tests/integration/maps/ -v
     ```
3. **Mesen2 PPU Viewer**:
   - Inspect VRAM tilemaps (BG1/BG2) and CGRAM palettes in real time to capture new ground-truth dumps.
4. **`tools/encode_room.py` Writer** -- the inverse of the extractor:
   ```bash
   python3 tools/encode_room.py --verify           # byte-exact round-trip, all 127 rooms
   python3 tools/encode_room.py --verify-rebuild   # re-encoded round-trip, all 127 rooms
   python3 tools/encode_room.py 0x38 --rebuild --compress --out room38.bin
   ```
   See `docs/map_encoding.md`. `rebuild_model()` + `write_room_into_rom()` is the write path a
   map editor uses; a rebuilt blob is never larger than the original for any vanilla room.

5. **Resolved since this skill was first written** (do not re-derive these):
   - **Slice 2 collision bitmask: fully decoded.** Bits 3..0 geometry, bits 5..4 **elevation
     plane** (not bits 15..12, as once assumed), bit 6 plane-transparency, bit 8 + bits 11..8
     entity gates, bit 13 always-walkable *and* the low nibble becomes a **drift direction**.
     Ported to `tools/collision.py` from `$909DE8`/`$8FA914`/`$8FAD9F`. See
     `docs/map_collision_mechanics.md`.
   - **Cuttable grass: fully decoded.** A metatile swap table in Section 4, driven by `$90A6EF`.
     See `docs/cuttable_grass_mechanics.md`.
   - **Payload block discovery is deterministic**, as §3 already described -- `dump_room.py` now
     uses `parse_blob_layout()` rather than the old signature scan, which mis-parsed room `0x15`.

6. **Still open**:
   - Collision word bits 12 and 15..14 (read by the sprite-priority routine `$8FC780`).
   - Dynamic tile animation triggers (e.g. scrolling waterfall or bubbling swamp tiles).

