# Secret of Evermore Map Editor Architecture & ROM Limitations

This document synthesizes our empirical reverse-engineering of the *Secret of Evermore* map pipeline into an architectural specification for a **custom map editor and injector**. It addresses technical feasibility, hardware constraints, ROM limits, and in-place patching workflows.

---

## 1. Map Data Architecture Overview

A Secret of Evermore map is not a single flat bitmap; it is a **multi-stage, multi-tier composite** structured into three primary data layers:

```mermaid
flowchart TD
    ROM_Ptr["Map Pointer Table ($9FFDE7)\nIndexed by room_id * 4"] --> Header["1. Room Header (13 bytes)\nOrigin, W×H (tiles), PPU Mode 1 Regs"]
    Header --> Triggers["2. Trigger Tables\nStep-on (0x0B) & B-Triggers (0x0C)"]
    Header --> Families["3. Tile Families List\nCHR Banks Loaded to VRAM ($0000..$5FFF)"]
    Header --> B1["4. Block 1: Palette Deltas\nDelta Accumulator → WRAM $7FC300 (CGRAM)"]
    Header --> Sec2["5. Section 2: Animated Tiles\nV-Blank DMA Queue ($90A0D0)"]
    Header --> B2["6. Block 2: Metatile Layout Grid\n2D Markov Bitstream ($8C9B65) → WRAM $7F0000"]
    Header --> B3["7. Block 3: Planar Metatile Table\nLZSS ($8C98C9) → WRAM $7F0280\nSlice 0: L1 Canopy | Slice 1: L2 Terrain | Slice 2: Collision"]
    Header --> Sec3["8. Section 3: Dynamic Objects\nDescriptors ($90A5D0) → Runtime VRAM Stamping"]
```

---

## 2. Tiles and Palette Limitations: Can We Mix Water and Lava?

### 2.1 The SNES Mode 1 Hardware Budget
*Secret of Evermore* runs in standard **SNES Mode 1** (Layer 1: 16-color 4bpp, Layer 2: 16-color 4bpp, Layer 3: 4-color 2bpp status bar):
- **CGRAM (Color RAM):** 8 background palettes (Palettes 0..7). Each palette has 16 colors (Color 0 = transparent, Colors 1..15 = opaque), giving **120 unique simultaneous background colors**.
- **Shared Palettes:** Layer 1 (foreground/canopy) and Layer 2 (terrain) share these same 8 palettes.
- **VRAM CHR Storage:** 64 KB total VRAM ($0000..$7FFF words).
  - BG1 Tilemap: 2 KB – 4 KB
  - BG2 Tilemap: 2 KB – 4 KB
  - CHR Character Tiles (8×8 4bpp pixels): Remaining ~56 KB (~1,792 unique 8×8 tiles).

### 2.2 Tile Families
Every room header defines a list of up to 7–8 **Tile Family IDs** (e.g. `0x0020`, `0x0091`, `0x00C4`). Each tile family represents a compressed graphics bank containing specific 8×8 character patterns and 16×16 metatile building blocks.
- **Limitation:** You cannot load arbitrary individual tiles from across the entire game into one room. You must assemble the map from the tile families currently loaded into VRAM.

### 2.3 Can We Mix Water and Lava in the Same Map?
**Yes, but subject to two strict constraints: CGRAM Palettes and Animated DMA Slots.**

1. **Palette Budget (Pass):**
   - Water tiles require cool blue/cyan tones (typically assigned to Palette 2 or 3).
   - Lava tiles require warm red/orange/yellow tones (typically assigned to Palette 4 or 5).
   - If the room's remaining palette slots accommodate the base terrain (e.g., 2 palettes for rock/cave) while leaving 1 palette for water and 1 for lava, the SNES PPU can render both simultaneously without conflict.

2. **Animated Tile DMA Budget (The Real Bottleneck):**
   - Both water ripples and flowing lava in Evermore are **not static tiles**; they are **Animated CHR Tiles** registered in Section 2.
   - During V-Blank, the engine runs a DMA transfer queue (`$90A0D0..$90A1A0`) that updates animated CHR character patterns in VRAM every few frames.
   - **V-Blank Bandwidth Limit:** The SNES V-Blank interval can only transfer ~6 KB per frame. The Evermore engine allocates safe bandwidth for **4 to 8 animated tiles per room**.
   - If water and lava are both animated at the same time, their animation frames will compete for Section 2 slots. If exceeded, the engine drops frames, causes sprite tearing, or crashes the DMA transfer.
   - *Workaround:* Render one fluid as static/semi-static (or budget 2 frames of water + 2 frames of lava) to stay within the 8-tile DMA limit.

---

## 3. Dynamic Objects: How Many Are Supported?

Dynamic objects (Section 3) are used for gourds, chests, cuttable grass, sewer gates, bridges, and pressure plates.

| Boundary Layer | ROM / Engine Constraint | Practical Limit |
|---|---|---|
| **Header Counter** | Byte at `obj_sec_off` | Max **255 objects** mathematically (`$00..$FF`). |
| **Pointer Table** | Word array at `fa2 + i * 2` | 2 bytes per object. 255 objects would take 510 bytes. |
| **Section 3 Buffer** | Variable payload between Block 3 and room end | Rooms allocate ~256 to 768 bytes for Section 3. |
| **WRAM Object State Array** | Stamping state table in WRAM | Vanilla rooms never exceed **30–45 objects**. |

### Practical Limit for Custom Maps
- Rooms with simple objects (e.g. 1×1 grass patches, gourds): **up to 40 objects** safely.
- Complex multi-state objects (e.g. collapsing bridges, 4-state gates): **15–25 objects**.
- Exceeding ~45 objects risks overflowing the allocated Section 3 sub-block in ROM or exceeding the WRAM object state buffer.

---

## 4. Map Size Constraints: How Big Can Maps Be?

A common misconception is that a map's dimensions determine its decompressed footprint directly. In Evermore, maps use a **Two-Level Indirection Architecture**:

```
Level 1: The Grid (Block 2)          Level 2: The Dictionary (Block 3)
W × H Array of Metatile Indices       Table of Unique Metatile Definitions
(e.g., 106 × 125 = 13,250 cells)     (e.g., 575 unique metatiles × 6 bytes)
```

### 4.1 Header Limits
- Header byte 2 = `width_tiles` (1 byte, `0..255`).
- Header byte 3 = `height_tiles` (1 byte, `0..255`).
- **Theoretical Maximum Dimensions:** $255 \times 255$ metatiles ($4,080 \times 4,080$ pixels).

### 4.2 WRAM Buffer Constraints (Bank $7F)
When a room loads, the engine decompresses:
1. **Block 3 (The Metatile Dictionary):**
   - Decompressed size = $\text{metatile\_count} \times 6$ bytes (2 bytes L1 + 2 bytes L2 + 2 bytes Collision).
   - In vanilla, `metatile_count` is typically 300 to 700 tiles (**1.8 KB to 4.2 KB**).
   - Destination: WRAM `$7F0280`.
2. **Block 2 (The Layout Grid):**
   - Decompressed size = $W \times H \times 2$ bytes.
   - For Room `0x4B` (the largest vanilla map, $106 \times 125$): $13,250 \times 2 = \mathbf{26.5\text{ KB}}$.
   - Destination: WRAM `$7F0000` / dynamic heap.

### 4.3 What is the Practical Maximum Map Size?
- WRAM Bank `$7F` has 64 KB ($7F0000..$7FFFFF).
- Reserving space for the Block 3 metatile table (~4 KB) and engine scratch buffers leaves **~32 KB to 40 KB for the grid**.
- At 2 bytes per cell, this permits maps of up to **16,000 to 20,000 metatiles**.
- Examples: **$128 \times 128$**, **$160 \times 100$**, or **$200 \times 80$**.
- Room `0x4B` ($106 \times 125 = 13,250$ metatiles) already pushes the vanilla engine close to its comfortable ceiling.

---

## 5. In-Place Patching of Single Tiles vs. Recompression

### Can we patch single tiles in an existing map without recompressing?
**In the raw ROM stream: NO. But at the Engine/Pipeline level: YES, via three distinct methods.**

```
                      Single-Tile Modification Methods
                                    │
       ┌────────────────────────────┼────────────────────────────┐
       ▼                            ▼                            ▼
Method 1: Section 3 Stamping  Method 2: WRAM Script Writes  Method 3: Pipeline Repointing
Zero-compression override     Runtime poke to $7F0280       Decompress → Edit → Repoint
```

#### Why Raw ROM Stream In-Place Patching Fails
- Block 2 uses **2D Markov Bitstream compression** (`$8C9B65`).
- Block 3 uses **LZSS sliding-window compression** (`$8C98C9`).
- Both are variable-bit-length streaming algorithms. Flipping a single bit or changing one byte mid-stream invalidates all downstream bit-shifts, breaks sliding window back-references, and corrupts every subsequent tile on the map.

#### How to Achieve Single-Tile Edits Cleanly:

1. **Method 1: Section 3 Dynamic Object Stamping (Zero Compression)**
   - *How vanilla does it:* Invisible bridges (Revealer spell), opened doors, cut bushes, and dynamic staircases do not modify the base tilemap; they use a Section 3 object record.
   - An object with $1 \times 1$ footprint can stamp ANY metatile word over any background coordinate on room load (`State 0`).
   - *Pros:* Zero recompression needed. Can be added as a patch record.

2. **Method 2: Script VM / WRAM Overwrite at Runtime**
   - The map layout is fully decompressed into WRAM on room entry.
   - An Everscript enter script can write directly to WRAM:
     ```csharp
     // Overwrite tile in WRAM grid after decompression
     <0x7F0000 + (y * width + x) * 2> = 0x0123;
     ```
   - *Pros:* Instant, programmatic control; can change tiles dynamically based on story flags.

3. **Method 3: Build Pipeline Decompress-Edit-Repoint (Recommended for Editors)**
   - Implemented end-to-end in [`tools/encode_room.py`](file:///Users/v/Documents/GitHub/everscript/tools/encode_room.py); see [`docs/map_encoding.md`](file:///Users/v/Documents/GitHub/everscript/docs/map_encoding.md) for the encoders and their verification.
     1. Decompress room blob using `tools/dump_room.py`.
     2. Edit the target metatile grid, collision word, or object in the decoded data.
     3. `rebuild_model()` re-encodes every block (LZSS or Markov, matching what the original used) and rebuilds the object area.
     4. `write_room_into_rom()` writes the blob in place when it fits — the rebuild is never larger than the original for any of the 127 vanilla rooms — or to free ROM space otherwise.
     5. Either way it updates the 4-byte table entry at `$9FFDE7 + room_id * 4`.
   - *Pros:* Completely clean; modifies the actual base map without wasting object slots or script execution time.

---

## 6. What Information / Components Are Missing for a Full Editor?

To build a standalone, interactive map editor, the following components are complete vs. remaining:

| Component | Status | Implementation Details |
|---|---|---|
| **Header Decoding** | ✅ **Complete** | 13-byte header, origin coordinates, PPU Mode 1 registers, effect variants. |
| **Map Pointer Table** | ✅ **Complete** | 24-bit pointer resolution from `$9FFDE7`. |
| **Step-on & B-Triggers** | ✅ **Complete** | 6-byte records decoded, visualized, and mapped to script IDs. |
| **Tile Families & CHR** | ✅ **Complete** | Tile family extraction, CHR decompression, 8×8 tile assembly. |
| **CGRAM Palettes** | ✅ **Complete** | Block 1 delta accumulator (`$7FC300`), 15-bit BGR555 color decoding. |
| **Block 3 Planar Slices** | ✅ **Complete** | LZSS decompression to Layer 1, Layer 2, and Collision attributes. |
| **Section 3 Dynamic Objects** | ✅ **Complete** | State descriptors, target dimensions ($W \times H$), metatile arrays. |
| **Section 2 Animated Tiles** | ✅ **Complete** | Animated tile IDs decoded; timing scripts documented. |
| **Collision Semantics** | ✅ **Complete** | Full bitfield decoded from `$909DE8` — plane, drift direction, entity gates. See `docs/map_collision_mechanics.md`. |
| **Cuttable Grass** | ✅ **Complete** | Metatile swap table decoded from `$90A6EF`. See `docs/cuttable_grass_mechanics.md`. |
| **Markov 2D Decompressor** | ✅ **Complete** | Exact bitstream reader (`$8C9B65`) in `tools/dump_room.py`. |
| **Markov 2D Compressor** | ✅ **Complete** | `tools/encode_room.py::encode_markov_grid` reproduces the original bitstream byte-for-byte for all 127 vanilla rooms. See `docs/map_encoding.md`. |
| **LZSS Compressor** | ✅ **Complete** | `tools/encode_room.py::lzss_compress`, including self-overlapping matches. |
| **Blob Write-Back** | ✅ **Complete** | `tools/encode_room.py::write_room_into_rom` — in-place or relocated, with map-table repointing. Verified never to grow a room's footprint on re-encode. |
| **Metatile Assembler UI** | 🔨 **Needs Tooling** | A GUI brush tool to compose 16×16 metatiles from 8×8 CHR character tiles. |
| **Entity Spawn Linking** | ℹ️ **Design Note** | Enemies/NPCs are not in map headers; they are spawned by **Everscript Enter Scripts** (`add_enemy(...)`). An editor must link with `.evs` source files. |

The remaining gap for a full editor is UI, not format understanding: every byte of the room blob can now be read, edited, re-encoded, and written back into a working ROM.

---

## 7. Is the Total Number of Maps Limited?

### 7.1 Vanilla Limit: 127 Rooms (`0x00..0x7E`)
- The vanilla ROM defines **127 rooms**, `0x00` through `0x7E` — not 128.
  The entry at index `0x7F` is not a room: its padding byte is `0xCC` where every real entry's is
  `0x00`, and the bytes it points at do not parse as a room blob (Block 2 reports `sub_flag 0x09`
  where the loader requires `0x07`). See [.github/rom-map.md](file:///Users/v/Documents/GitHub/everscript/.github/rom-map.md) §2,
  which lists all 127 and shows the check. `MAX_ROOMS = 127` in `tools/dump_room.py` is correct.
- The Map Pointer Table starts at `$9FFDE7` (`0x1FFDE7` in ROM file).
- The table is located near the end of Bank `$9F` (`$9F8000..$9FFFFF`), which terminates at `0x1FFFFF`.
- Space remaining in Bank `$9F`:
  $$0x1FFFFF - 0x1FFDE7 = 536\text{ bytes} \implies \frac{536}{4} = \mathbf{134\text{ entries}}$$
- Without relocation, you can add **7 additional rooms** (`0x7F..0x85`) before overflowing Bank `$9F`
  — `0x7F` itself being the first free slot, since it holds no room today.

### 7.2 Expanding Beyond 127 Rooms
Can the map table be expanded? **Yes, up to 256 rooms easily.**

1. **Engine Room Loading Hook (`$908F6A`):**
   ```assembly
   LDA $0ADB     ; Load Room ID (1 byte)
   ASL
   ASL           ; Room ID * 4
   TAX
   LDA $9FFDE7,X ; Read 24-bit pointer
   ```
   The engine does **not perform a bounds check** on `room_id`. It simply multiplies by 4 and indexes `$9FFDE7`.
2. **Relocating the Table via Asar Patch:**
   Move the pointer table to free ROM space (e.g., Bank `$40` or `$50`) and update the instruction:
   ```assembly
   org $908F6E
       LDA !NEW_MAP_TABLE,X
   ```
3. **Upper Limit:**
   Because `room_id` in WRAM (`$0ADB`) and in the `CHANGE MAP` bytecode instruction (`0x22 <room_id> <x> <y>`) is an 8-bit byte, the engine natively supports up to **256 maps (`0x00..0xFF`)** without altering bytecode structures.

---

## 8. Summary Checklist for Building a Map Editor

1. **Viewer / Export Pipeline:** Already functional via `tools/dump_room.py` and `tools/render_map.py` (composite PNG, per-plane collision contours, drift arrows, trigger overlays, full multi-layer composition).
2. **Editing Workflow:** already functional via `tools/encode_room.py`:
   - Modify the decompressed $W \times H$ metatile grid, collision words, triggers, or objects returned by `dump_room()`.
   - `rebuild_model()` re-encodes Block 2 with the verified Markov encoder, Blocks 1 and 3 with LZSS or raw (whichever is smaller, or the original payload if that section is unchanged), and rebuilds the object area with vanilla-style block overlap.
3. **Injection Workflow:** already functional via `write_room_into_rom()`:
   - Writes the rebuilt blob in place — proven never to overflow the room's original footprint across all 127 vanilla rooms — or relocates it to free ROM space and repoints the 4-byte table entry at `$9FFDE7` otherwise.
   - Still an editor's own responsibility: updating the room's Everscript enter script for any changed entity spawns.

See `docs/map_encoding.md` for the encoder internals and their verification.

