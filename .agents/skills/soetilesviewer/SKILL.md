---
name: soetilesviewer
description: Explains the architecture, ROM resource tables, tile decompression, sprite formats, character stats, and script dumper logic in the sibling SoETilesViewer repository, along with guidelines on what can be learned and what requires empirical verification.
---

# SoETilesViewer: Architecture, ROM Formats & Reverse Engineering Insights

The sibling repository [**`SoETilesViewer`**](file:///Users/v/Documents/GitHub/SoETilesViewer) (by black-sliver & neagix) is a C++/Qt utility and disassembly dumper for *Secret of Evermore* (US/NTSC). It provides extensive, reverse-engineered insights into how the game stores graphics, palettes, sprites, texts, character stats, and room scripts in the ROM.

> [!CAUTION]
> **Zero-Trust Empirical Rule (`AGENTS.md`)**  
> While `SoETilesViewer` contains extensive correct ROM offsets and format definitions, **it is a third-party, unverified tool**. Some opcode names, sub-instructions, and heuristic guesses in `list-rooms.cpp` are incomplete or flawed.  
> - **Trust verified pointers & struct offsets** (e.g. `$9FFDE7`, `$EE0000`, `$8EB678`, `$EC0000`).
> - **Verify script bytecode interpretations** against Mesen2 disassembly traces before using them in `in/core/` or compiler tests.

---

## 1. Codebase Layout & Key Components

```
SoETilesViewer/
├── rom.h                 # HiROM/FastROM 24-bit address translator & file I/O
├── tile.h                # 16x16 background tile graphic decompressor ($EE0000)
├── spriteblock.h         # 16x16 ($EC0000) & 8x8 ($D80000) sprite block decompressor
├── spriteinfo.h          # Multi-chunk sprite frame layout assembler (0xCA0003)
├── characterdata.h       # 74-byte enemy & character stat table ($8EB678)
├── colormap.h            # SNES 15-bit BGR555 to 32-bit ARGB palette converter
├── text.h                # Dialog text dictionary decompression ($91D000)
├── mainwindow.cpp        # Qt UI orchestrator loading all game assets
└── SoEScriptDumper/
    ├── list-rooms.cpp    # CLI script dumper parsing room headers & bytecode
    ├── data.h            # Master map list, opcodes, memory addresses
    └── script_all        # Raw text output of all dumped room scripts
```

---

## 2. Critical ROM Resource Tables Discovered

| Resource | ROM Bus Address | File Offset (HiROM) | Format / Stride | Header / Source File |
|---|---|---|---|---|
| **Map Pointer Table (US)** | `$9FFDE7` | `0x1FFDE7` | 4-byte stride ($3 \text{ byte pointer} + 1 \text{ pad}$) per room | `SoEScriptDumper/data.h` |
| **Map Pointer Table (DE)** | `$A0FDE5` | `0x20FDE5` | 4-byte stride ($3 \text{ byte pointer} + 1 \text{ pad}$) per room | `SoEScriptDumper/data.h` |
| **16x16 Background Tiles** | `$EE0000` | `0x2E0000` | 24-bit pointer ($3 \text{ bytes}$) per tile ID | `tile.h` |
| **16x16 Sprite Blocks** | `$EC0000` | `0x2C0000` | 24-bit pointer ($3 \text{ bytes}$) per block | `spriteblock.h` |
| **8x8 Sprite Blocks** | `$D80000` | `0x180000` | 24-bit pointer ($3 \text{ bytes}$) per block | `spriteblock.h` |
| **Character / Monster Stats** | `$8EB678` | `0x0EB678` | 74 bytes per entity (142 entries) | `characterdata.h` |
| **Sprite Frame Chunks** | `$CA0003` | `0x0A0003` | Variable-length multi-chunk structs | `spriteinfo.h` |
| **Script Bytecode Base** | `$928000` | `0x128000` | Bytecode instruction stream | `SoEScriptDumper/data.h` |
| **Dialog Text Table** | `$91D000` | `0x11D000` | 24-bit pointer ($3 \text{ bytes}$) per string | `text.h` |

---

## 3. Graphic Decompression Algorithms

### 3.1 16x16 Background Tiles (`tile.h`)

Background metatiles are indexed by `Pointer = $EE0000 + (tile_id * 3)`.  
Each tile graphic decompresses into **128 bytes** (4 8x8 character tiles in 4bpp planar SNES format = $16 \times 16$ pixels).

1. **Header Byte (`tileInfo = read8(dataaddr)`):**
   - **Bit 7 (`tileInfo & 0x80`):** Compression flag ($1 = \text{compressed}$, $0 = \text{uncompressed}$).
   - **Bits 0–6 (`tileInfo & 0x7F`):**
     - If uncompressed: word count ($N = \text{bits} + 1$). Reads $N$ words and repeats the last word to fill 128 bytes.
     - If compressed: byte offset to the **Data Stream** (`dataPtr = dataaddr + offset`).
2. **Dual-Stream Compressed Architecture:**
   - **Command Stream (`cmdPtr = dataaddr + 1`):** Read as **4-bit nibbles** (`read4cmdBits()`).
   - **Data Stream (`dataPtr`):** Starts after the command stream at `dataaddr + (tileInfo & 0x7F)`.
   - **Control Byte (`compressionIndicators = read8(dataPtr++)`):** 8 bits processed MSB-first:
     - **Bit = 0:** Literal 16-bit word copied directly from `dataPtr`.
     - **Bit = 1:** Read 4-bit `mode` from Command Stream:
       - `0`: Write `0x0000`
       - `1`: Write `0x00FF`
       - `2`: Write `0xFF00`
       - `3`: Write `0xFFFF`
       - `4`: Write `0x00**` (`**` read from data)
       - `5`: Write `0xFF**` (`**` read from data)
       - `6`: Write `0x**00` (`**` read from data)
       - `7`: Write `0x**FF` (`**` read from data)
       - `8`: Write `0x****` (`**` read from data duplicated into both bytes)
       - `9..11`: Repeat last word 1, 2, or 3 times
       - `12`: Repeat last word $4 + \text{read4cmdBits()}$ times
       - `13`: Write `0x**RR` (`**` from data, `RR` = lower byte of last word)
       - `14`: Write `0xRR**` (`**` from data, `RR` = upper byte of last word)
       - `15`: Write `0x^^**` (`**` from data, `^^` = bitwise inverse `** ^ 0xFF`)

### 3.2 Sprite Blocks (`spriteblock.h`)

Sprites are composed of 16x16 blocks (indexed at `$EC0000`) and 8x8 blocks (indexed at `$D80000`):
- The 24-bit pointer has **Bit 23** as the compression flag: `compressed = dataaddr >> 23`.
- **Zero-Word Runlength Packing:** Uncompressed sprite blocks have many blank rows. When compressed, a single status bit per 16-bit word indicates whether the word is zero or literal. If `bit == 1`, 2 zero bytes are emitted without consuming ROM bytes.

---

## 4. Entity & Monster Stat Structure (`characterdata.h`)

The game stores all 142 characters, companions, bosses, and enemies in a contiguous array starting at `$8EB678`.  
Each record is exactly **74 bytes**:

```
Offset  Size  Field Name       Description
---------------------------------------------------------------------------------
+$00     3    nameptr          24-bit pointer to entity string name
+$03     2    unknown03        Internal engine flags
+$05     2    unknown05        Type / behavior class
+$07     2    flags            Entity capability flags (invulnerability, etc.)
+$09     2    palette          Default sprite palette index
+$0B     2    unknown0b        Unknown
+$0D     2    unknown0d        Unknown
+$0F     2    hp               Base maximum Hit Points
+$11     2    unknown11        Unknown
+$13     2    aggro_range      Detection distance in pixels
+$15     2    aggro_chance     Probability to engage (out of 256)
+$17     2    unknown17        Unknown
+$19     2    attack           Base physical attack power
+$1B     2    defense          Base physical defense
+$1D     2    magic_defense    Magic defense rating
+$1F     2    evade            Evasion rating
+$21     2    hit_rate         Accuracy rating
+$23     4    exp              Experience points awarded upon defeat
+$27     2    money            Talon / Jewel currency dropped
+$29     1    prize_chance     Drop rate probability for item slots
+$2A     2    unknown2a        Unknown
+$2C     2    charge_limit     Weapon charge level cap
+$2E     2    charge_rate      Speed of charge attack meter
+$30     2    attack_proc      Attack routine / script pointer
+$32     2    anim_stand       Standing animation frame table pointer
+$34     2    anim_walk        Walking animation frame table pointer
+$36     2    anim_run         Running animation frame table pointer
+$38     2    anim_atk0        Attack animation variant 0 pointer
+$3A     2    anim_atk1        Attack animation variant 1 pointer
+$3C     2    anim_atk2        Attack animation variant 2 pointer
+$3E     2    anim_atk3        Attack animation variant 3 pointer
+$40     2    anim_damage      Hit / flinch animation pointer
+$42     2    anim_death       Death animation pointer
+$44     2    anim_spoils      Item drop animation pointer
+$46     2    anim_block       Shield / guard animation pointer
```

> [!TIP]
> **Application to Kaizo Balancing:**  
> When rebalancing enemy HP, attack, defense, or boss EXP rewards for Kaizo difficulty, editing this 74-byte struct at `$8EB678 + (id * 74)` is the authoritative mechanism.

---

## 5. Text & Dialog Compression (`text.h`)

Text strings are referenced via a pointer table at `$91D000` ($3 \text{ bytes}$ per entry).
- **Bit 23 of pointer:** Compression flag.
- **Dictionary Compression:** The text engine uses multi-token byte-pair substitution:
  - If high bits `d & 0xC0 == 0xC0`: reads word from dictionary `$91F3EC` / `$91F66C`.
  - If `d == 0xC0`: reads 2-byte word from dictionary `$91F46C` / `$91F7D5`.
  - If `d & 0xC0 == 0x80`: 2-character lookup from `$91F32E`.
  - If `d & 0xC0 == 0x00`: single character lookup from `$91F3AE`.
  - Control codes encode dialog pauses (`[PAUSE:xx]`), linebreaks, and text box triggers.

---

## 6. What `SoETilesViewer` Does NOT Solve (The Map Decompression Gap)

While `SoETilesViewer` is capable of viewing isolated 16x16 tiles and sprites:
1. **It cannot decode room tilemap layouts:** `SoETilesViewer` does **not** implement:
   - The Block 1 / Block 3 LZSS sliding-window decompressor (`$8C988D`).
   - The 16-bit delta accumulator (`$908E85`) for resolving tile palettes.
   - The 2D Context-Predictive Markov Bitstream Decoder (`$8C9BD0`) for reconstructing the metatile grid.
   - The **3-Slice Planar Metatile Architecture** (`$9091B0..$909245`), where Block 3 decompresses into $3N$ words divided into 3 planar slices (Slice 0 = Layer 1 / Canopy, Slice 1 = Layer 2 / Terrain, Slice 2 = Collision).
   - The direct Bank `$7F` metatile memory layout (`base_metatile = width * height * 2`, stride = 8 bytes per metatile).
2. **It cannot render composite rooms:** Because it lacks map decompression logic, `SoETilesViewer` only displays raw unplaced tiles in an arbitrary grid, not assembled multi-layer rooms.
3. **The Solution in Everscript:** Full map decompression and composite rendering was solved empirically in this repository:
   - Full reverse-engineering documentation in [**`docs/map_decompression_trace_analysis.md`**](file:///Users/v/Documents/GitHub/everscript/docs/map_decompression_trace_analysis.md).
   - Standalone CLI extractor in [**`tools/dump_room.py`**](file:///Users/v/Documents/GitHub/everscript/tools/dump_room.py).
   - Automated integration tests with bit-for-bit emulator VRAM verification in [**`tests/integration/maps/`**](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/).

---

## 7. Everscript Room Map Extractor & Testing (`tools/dump_room.py`)

The Everscript map tooling provides direct access to decoded ROM map data:

```bash
# Dump map metadata, dimensions, triggers, and metatiles:
python3 tools/dump_room.py 0x33
python3 tools/dump_room.py 0x38

# Output raw SNES VRAM tilemap bytes (matching Mesen2 PPU dumps):
python3 tools/dump_room.py 0x33 --vram-bytes
python3 tools/dump_room.py 0x38 --vram-bytes --layer 1
python3 tools/dump_room.py 0x38 --vram-bytes --layer 2

# Output 16-bit VRAM tilemap words with 32-tile buffer row padding:
python3 tools/dump_room.py 0x33 --vram-words --pad-32

# Export full room model as JSON:
python3 tools/dump_room.py 0x33 --json
```

### Verification Test Suite (`tests/integration/maps/`)
- [`test_room_0x33_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x33_vram.py): Room 0x33 (Strong Heart's Exterior, $20 \times 16$)
- [`test_room_0x34_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x34_vram.py): Room 0x34 (Strong Heart's Hut, $18 \times 18$)
- [`test_room_0x38_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x38_vram.py): Room 0x38 (South Jungle, $83 \times 91$)
- [`test_room_0x25_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x25_vram.py): Room 0x25 (Fire Eyes' Village, $63 \times 58$)
- [`test_room_0x26_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x26_vram.py): Room 0x26 (West Area with Defend, $19 \times 18$)
- [`test_room_0x36_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x36_vram.py): Room 0x36 (Volcano Fire Pits, $25 \times 25$)
- [`test_room_0x51_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x51_vram.py): Room 0x51 (Village Huts & Blimp's Hut, $50 \times 56$)
- [`test_room_0x5b_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x5b_vram.py): Room 0x5B (East Jungle, $72 \times 48$)
- Run the suite via:
  ```bash
  .venv/bin/pytest tests/integration/maps/ -v
  ```



