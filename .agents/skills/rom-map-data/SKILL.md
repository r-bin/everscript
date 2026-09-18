---
name: rom-map-data
description: Experimental guide on reverse-engineering Secret of Evermore map data, tilemap layouts, collision layers, and tileset compression from the ROM.
---

# ROM Map Data & Tilemap Architecture (Experimental)

Understanding how Secret of Evermore stores, decompresses, and renders map data is an ongoing reverse-engineering effort. This guide outlines the current state of knowledge regarding ROM map pointers, tilemaps, collision layers, and external tooling.

---

## 1. Room Header Structure

Each of the 116 maps in the game is referenced via a master **Map Pointer Table** in ROM:
- The pointer table uses a **4-byte stride** per room (`table + room_id * 4`), with each entry containing a 24-bit pointer plus 1 padding byte.
- A standard map header is **13 bytes** (offsets `$00..$0C`), immediately followed by trigger tables at offset `$0D`:

| Offset | Size | Field | Description |
|---|---|---|---|
| `$00` | 1 | `trig_off_x` | Trigger origin X offset (tile coordinates) |
| `$01` | 1 | `trig_off_y` | Trigger origin Y offset (tile coordinates) |
| `$02` | 1 | `width_tiles` | Map width in 16×16 metatiles |
| `$03` | 1 | `height_tiles` | Map height in 16×16 metatiles |
| `$04` | 1 | `display_tm` | SNES PPU `$212C` (TM — Main Screen Designation) |
| `$05` | 1 | `subscreen_ts` | SNES PPU `$212D` (TS — Sub Screen Designation) |
| `$06` | 1 | `color_math` | SNES PPU `$2131` (CGADSUB — Color Math Designation) |
| `$07` | 1 | `color_window` | SNES PPU `$2130` (CGWSEL — Color Addition Select) |
| `$08` | 1 | `effect_variant` | Room visual effect variant |
| `$09..$0C` | 4 | *(unknown)* | Unparsed; purpose not yet reverse-engineered |

---

## 2. Coordinate Spaces

Evermore operates across two distinct coordinate planes:

| Coordinate Plane | Scale | Typical Usage |
|---|---|---|
| **Pixel Coordinates** | 1:1 ($256 \times 224$ screen space) | Sprite rendering, projectile hits, camera tracking |
| **Tile Coordinates** | 1:8 or 1:16 ($X_{pix} / 8$, $Y_{pix} / 8$) | Step-on trigger rects `[x0, y0 : x1, y1]`, spawn points |

When analyzing room dumps from `script_all`:
```
(22) CHANGE MAP = 0x38 @ [ 0x0180 | 0x02C0 ]: "South Jungle / Start"
```
The spawn coordinates `0x0180` and `0x02C0` are raw pixel values. Divided by 8, these correspond to tile coordinates `(48, 88)`.

---

## 3. Map Compression & Payload Architecture

Secret of Evermore uses a multi-stage payload architecture across three compressed ROM blocks, fully documented in [**`docs/map_decompression_trace_analysis.md`**](file:///Users/v/Documents/GitHub/everscript/docs/map_decompression_trace_analysis.md):

1. **Master Map Pointer Table (`$9FFDE7` / ROM `0x1FFDE7`)**:
   - 4-byte stride per room ID (`table + room_id * 4`) pointing to 24-bit SNES address of the room blob.
   - The room blob begins with a **13-byte header** (see §1) containing trigger origin offsets, map dimensions, PPU display configuration registers (`TM`, `TS`, `CGADSUB`, `CGWSEL`), effect variant, and 4 unknown bytes. Trigger tables follow immediately at offset `$0D`.

2. **Payload Block 1 (Delta Tile Palette)**:
   - Starts **deterministically** immediately after the payload descriptor array: `pos + 3 + (rom[pos] * 3)`.
   - **In 115 rooms:** `sub_flag == 0x03` $\to$ decompressed via **LZSS** (`$8C98C9`) into WRAM `$7FC300`.
   - **In 12 rooms:** `sub_flag == 0x00` $\to$ raw **uncompressed copy** (`$8C98B1`) into WRAM `$7FC300`.
   - In-place **16-bit delta accumulator** (`$908E85`) converts relative deltas into unique 16×16 CHR graphic IDs.
   - Subroutine `$8CC88C` looks up graphic pointers in the **`$EE0000` table** (`tile_id * 3`) and DMAs 4bpp pixel patterns to SNES VRAM character slots.

3. **Sub-Block Resolution Algorithm (127/127 Verified)**:
   - Intermediate data blocks (CHR uploads, palettes) cause variable offsets between blocks.
   - The engine dynamically identifies:
     - **Block 2 (Markov Grid)**: Scans forward for `sub_flag == 0x07` where decompressed size matches `width_tiles * height_tiles * 2`.
     - **Block 3 (Metatile VRAM Table)**: Scans forward after Block 2 for `sub_flag == 0x03` where decompressed size $S > 0$ and $S \pmod 6 == 0$.
   - Tested and confirmed working across **100% of all 127 vanilla rooms**.

4. **Payload Block 2 (2D Markov Metatile Grid)**:
   - Header tag `0x00`, sub-flag `0x07` $\to$ decompressed via a custom **2D Context-Predictive Markov Bitstream Decoder** (`$8C9BD0`).
   - Variable-length prefix codes predict the next metatile from the cell **above** (`$26`) and to the **left** (`$12`).
   - Unpacks directly into WRAM **`$7F0000`** as a `width_tiles x height_tiles` grid of 16-bit metatile offsets.
   - **Metatile ID as Direct WRAM Bank `$7F` Offset**:
     - The base offset of the metatile table is dynamically calculated: `base_metatile = width_tiles * height_tiles * 2`.
     - Metatiles are aligned on 8-byte boundaries: `ID = base_metatile + (index * 8)`.
     - For Room 0x33 ($20 \times 16$): `base_metatile = 640 = 0x0280`. Grid at `$7F0000..$7F027F`, table at `$7F0280`.
     - For Room 0x38 ($83 \times 91$): `base_metatile = 15106 = 0x3B02`. Grid at `$7F0000..$7F3B01`, table at `$7F3B02`.

5. **Payload Block 3 (3-Slice Planar Multi-Layer Metatile Table)**:
   - Header tag `0x00`, sub-flag `0x03` $\to$ decompressed via **LZSS** (`$8C988D`).
   - Decompressed size is always a multiple of 6 bytes: $S = 6N$ bytes ($3N$ 16-bit words, where $N = \text{metatile\_count}$).
   - Routine `$9091B0..$909245` divides total words by 3 using hardware math registers (`STA $4206`) and unpacks data into **3 planar slices**:
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
4. **Open Research Questions**:
   - Full decoding of the Slice 2 collision attribute bitmask (determining how elevation levels, stairs, water, and pits interact with player collision).
   - Dynamic tile animation triggers (e.g. scrolling waterfall or bubbling swamp tiles).

