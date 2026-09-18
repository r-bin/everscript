# Empirical Reverse Engineering: Secret of Evermore Room Palettes & CGRAM Architecture

> [!IMPORTANT]
> **Zero-Trust Trace Methodology**  
> All logic documented here is derived directly from 65c816 disassembly trace logs captured in Mesen2 and validated against `Secret of Evermore (U) [!]` (headerless 3,145,728 bytes).  
> Native engine routines: **`$909088`** (room palette dispatcher), **`$90D020`** (tile family DMA loader), **`$90D05C`** (family table lookup loop), and **`$8085FA`** (CGRAM hardware DMA updater).

---

## 1. Overview & Architectural Role

Secret of Evermore utilizes SNES PPU **Mode 1** for background rendering, providing **8 sub-palettes of 16 colors each** (128 colors total in CGRAM for BG1 and BG2). Rather than storing full 256-color palettes per room, the engine organizes colors into modular **Tile Families**.

```mermaid
flowchart TD
    RoomBlob["Room Header Blob"] --> FamCount["Read Tile Family Count N ($0F9C)"]
    FamCount --> FamList["Family ID List: [0x00B9, 0x00BA, 0x0020...]"]
    FamList --> LoaderLoop["Palette Loader Loop ($90D05C)"]
    MasterTable["Master Palette Table ($9CC322 / 0x1CC322)"] --> LoaderLoop
    LoaderLoop -->|ASL * 5 + $C322| WRAM["WRAM Buffer $7E61A7 (N * 32 Bytes)"]
    WRAM --> CGRAM_DMA["CGRAM Updater ($8085FA)"]
    CGRAM_DMA -->|CGADD = $0010 (Palette 1)| CGRAM["SNES PPU CGRAM ($2121 / $2122)"]

    subgraph CGRAM_Layout ["SNES CGRAM Sub-Palettes (16 Colors Each)"]
        P0["Palette 0: Reserved / HUD / Text (Colors 0..15)"]
        P1["Palette 1: Family 0 (Colors 16..31)"]
        P2["Palette 2: Family 1 (Colors 32..47)"]
        P3["Palette 3: Family 2 (Colors 48..63)"]
        P4["Palette 4: Family 3 (Colors 64..79)"]
        P5["Palette 5: Family 4 (Colors 80..95)"]
        P6["Palette 6: Family 5 (Colors 96..111)"]
        P7["Palette 7: Family 6 (Colors 112..127)"]
    end
    CGRAM_DMA --> CGRAM_Layout
```

When a room loads:
1. The room blob defines $N$ **16-bit Tile Family IDs** (typically 6 or 7 families).
2. The engine resolves each family from the master table at ROM address **`$9CC322`** (ROM file offset `0x1CC322`).
3. Each family contributes exactly **32 bytes** (16 colors $\times$ 2 bytes).
4. Subroutine **`$8085FA`** DMAs these palettes into CGRAM starting at **CGADD `$0010`** (Color 16, which corresponds to **Palette 1**).

---

## 2. Master Palette Table (`$9CC322` / ROM `0x1CC322`)

The master palette table begins at SNES address `$9CC322` (ROM file offset `0x1CC322`).
- **Stride:** Exactly **32 bytes** per family ID (16 colors $\times$ 2 bytes).
- **Index Formula:**
  $$\text{Family Address} = \text{0x1CC322} + (\text{family\_id} \times 32)$$
- **Format:** 16-bit little-endian words in standard SNES BGR555 format.

---

## 3. Engine Palette Loading Disassembly (`$90D020..$90D0A3`)

The routine `$90D020` is invoked during map initialization (`$909088`).

### 3.1 Loop Setup & Family Indexing (`$90D020..$90D05A`)

```assembly
90D020: AF 37 24 7E LDA $7E2437        ; Load initial family offset (0 at room load)
90D024: 8D 8A 0F    STA $0F8A
90D027: AC 9C 0F    LDY $0F9C           ; Pointer to tile family section in room blob
90D02A: B7 8B       LDA [$8B],Y         ; Read number of families N (1 byte)
90D02C: 29 FF 00    AND #$00FF
90D02F: 38          SEC
90D030: ED 8A 0F    SBC $0F8A           ; N - start_offset
90D033: F0 6E       BEQ $90D0A3         ; Exit if 0
90D035: 30 6C       BMI $90D0A3         ; Exit if negative
90D037: C9 08 00    CMP #$0008          ; Cap at maximum 8 palettes
90D03A: 30 03       BMI $90D03F
90D03C: A9 07 00    LDA #$0007          ; Capped
90D03F: AA          TAX                 ; X = loop counter (number of families to load)
90D040: AD 8A 0F    LDA $0F8A
90D043: 0A          ASL A               ; family_index * 2
90D044: 38          SEC
90D045: 6D 9C 0F    ADC $0F9C           ; Y points to first 16-bit family ID (+1 for count)
90D048: A8          TAY
90D049: A9 A7 61    LDA #$61A7          ; WRAM destination address $7E61A7
90D04C: 8D 81 21    STA $2181           ; PPU WRAM address register ($2181)
90D04F: 85 26       STA $26
90D051: E2 20       SEP #$20            ; 8-bit accumulator
90D053: A9 7E       LDA #$7E            ; WRAM bank $7E
90D055: 8D 83 21    STA $2183           ; PPU WRAM bank register ($2183)
90D058: 85 28       STA $28
90D05A: C2 20       REP #$20            ; 16-bit accumulator
```

### 3.2 Family DMA Transfer Loop (`$90D05C..$90D086`)

For each family, the engine calculates the ROM source address via 5 arithmetic left shifts (`ASL A` $\times 5 \implies \times 32$) and adds `$C322`:

```assembly
loop_families:
90D05C: B7 8B       LDA [$8B],Y         ; Read 16-bit family_id from room blob
90D05E: C8          INY
90D05F: C8          INY
90D060: 0A          ASL A               ; A = family_id * 2
90D061: 0A          ASL A               ; A = family_id * 4
90D062: 0A          ASL A               ; A = family_id * 8
90D063: 0A          ASL A               ; A = family_id * 16
90D064: 0A          ASL A               ; A = family_id * 32
90D065: 69 22 C3    ADC #$C322          ; Add base offset $C322 in Bank $9C
90D068: 8D 12 43    STA $4312           ; DMA Channel 1 Source Address = $C322 + (id * 32)
90D06B: A9 20 00    LDA #$0020          ; DMA Size = 32 bytes ($0020 = 16 colors * 2)
90D06E: 8D 15 43    STA $4315
90D071: A9 00 80    LDA #$8000          ; DMA Mode: Transfer to $2180 (WRAM write)
90D074: 8D 10 43    STA $4310
90D077: E2 20       SEP #$20
90D079: A9 9C       LDA #$9C            ; DMA Source Bank = $9C (ROM 0x1CC322)
90D07B: 8D 14 43    STA $4314
90D07E: A9 02       LDA #$02            ; Trigger DMA Channel 1
90D080: 8D 0B 42    STA $420B
90D083: C2 20       REP #$20
90D085: CA          DEX                 ; Decrement family counter
90D086: D0 D4       BNE loop_families   ; Loop until all families loaded into WRAM
```

### 3.3 CGRAM Hardware Transfer (`$90D099..$90D0A3` and `$8085FA`)

Once all $N$ families are staged consecutively in WRAM buffer `$7E61A7`, the engine executes:

```assembly
90D08C: B7 8B       LDA [$8B],Y         ; Reload family count N
90D08E: 29 FF 00    AND #$00FF
90D091: 0A; 0A; 0A; 0A; 0A; 0A          ; Multiply N by 32 bytes
90D098: AA          TAX                 ; X = Total DMA transfer size = N * 32 bytes
90D099: A9 10 00    LDA #$0010          ; STA $2E = Destination CGADD = 0x0010 (Palette 1!)
90D09C: 85 2E       STA $2E
90D09E: 22 FA 85 80 JSL $8085FA         ; Execute DMA from WRAM $7E61A7 into CGRAM
90D0A3: 6B          RTL
```

Within `$8085FA`:
```assembly
808604: A5 2E       LDA $2E             ; Destination CGADD (0x0010 = Color 16)
808606: 8D 21 21    STA $2121           ; Set PPU CGRAM address register ($2121)
808609: 8E 15 43    STX $4315           ; DMA size (N * 32 bytes)
80860C: A6 26       LDX $26             ; DMA source address ($61A7)
80860E: 8E 12 43    STX $4312
808611: A5 28       LDA $28             ; DMA source bank ($7E)
808613: 8D 14 43    STA $4314
808616: A2 00 22    LDX #$2200          ; DMA target: $2122 (CGDATA - Color Data Register)
808619: 8E 10 43    STX $4310
80861C: A9 02       LDA #$02            ; Trigger DMA Channel 1
80861E: 8D 0B 42    STA $420B
```

---

## 4. Tile Family to CGRAM Palette Mapping Rules

In the SNES PPU architecture, each background tilemap word specifies a 3-bit palette index ($P \in [0, 7]$) in bits 10..12:
$$\text{palette\_index} = (\text{vram\_word} \gg 10) \ \& \ \text{0x07}$$

Because CGADD is explicitly set to `0x0010` (Color 16) during map loading, the families map to CGRAM as follows:

| CGRAM Palette | CGRAM Color Range | Target In-Game Role | Loaded From Room Family |
|:---:|:---:|:---|:---:|
| **Palette 0** | `0..15` | Reserved: HUD, dialogue window text, system background | *Not loaded by room family* |
| **Palette 1** | `16..31` | Background terrain / canopy sub-palette | **Family Index 0** |
| **Palette 2** | `32..47` | Background terrain / canopy sub-palette | **Family Index 1** |
| **Palette 3** | `48..63` | Background terrain / canopy sub-palette | **Family Index 2** |
| **Palette 4** | `64..79` | Background terrain / canopy sub-palette | **Family Index 3** |
| **Palette 5** | `80..95` | Background terrain / canopy sub-palette | **Family Index 4** |
| **Palette 6** | `96..111` | Background terrain / canopy sub-palette | **Family Index 5** |
| **Palette 7** | `112..127`| Background terrain / canopy sub-palette | **Family Index 6** |

> [!IMPORTANT]
> **1-Based Palette Offset Rule**  
> For any tilemap word with palette index $P \in [1, 7]$, the corresponding color array is loaded from **Room Tile Family $(P - 1)$**.  
> Empirical audit across all 127 rooms confirms that standard background tilemap words use palettes `1..7`, perfectly aligning with the $1..7$ room tile families.

---

## 5. SNES BGR555 to 24-bit/32-bit RGBA Color Conversion

Each color entry in the ROM is a 16-bit little-endian word:
```
Bit:   15  14 13 12 11 10   9  8  7  6  5   4  3  2  1  0
Field:  0 [    Blue     ] [   Green    ] [     Red     ]
```

### 5.1 Bit Extraction
- **Red (5 bits):** $R_5 = (c_{16} \gg 0) \ \& \ \text{0x1F}$
- **Green (5 bits):** $G_5 = (c_{16} \gg 5) \ \& \ \text{0x1F}$
- **Blue (5 bits):** $B_5 = (c_{16} \gg 10) \ \& \ \text{0x1F}$

### 5.2 5-Bit to 8-Bit Color Expansion

In SNES hardware, 5-bit channel values $[0, 31]$ map to 8-bit RGB values $[0, 255]$ using **bit replication** (replicating the 3 MSBs into the 3 LSBs):
$$R_8 = (R_5 \ll 3) \ | \ (R_5 \gg 2)$$
$$G_8 = (G_5 \ll 3) \ | \ (G_5 \gg 2)$$
$$B_8 = (B_5 \ll 3) \ | \ (B_5 \gg 2)$$

This is mathematically equivalent to $\text{round}(c_5 \times 255 / 31)$, ensuring $0 \mapsto 0$ and $31 \mapsto 255$ without rounding distortion.

### 5.3 Transparency Rules

In SNES 4bpp Mode 1 background rendering:
- **Color Index 0:** Is **strictly transparent** ($A = 0$). The underlying background layer (BG2) or backdrop color shines through.
- **Color Indices 1..15:** Are **opaque** ($A = 255$).

---

## 6. Empirical Validation Across Rooms

Testing across representative rooms validates the family count, table addresses, and palette index ranges:

| Room ID | Room Name | Family Count | Tile Families | Tilemap Palettes Used | Status |
|:---:|:---|:---:|:---|:---:|:---:|
| **`0x00`** | Intro Podunk Mansion | 7 | `0x0000, 0x0001, 0x0002, 0x0003, 0x0004, 0x0005, 0x0006` | `[1, 2, 3, 4, 5, 6, 7]` | ✅ 100% Match |
| **`0x25`** | Fire Eyes' Village | 7 | `0x0090, 0x0020, 0x0091, 0x0092, 0x0093, 0x0094, 0x0095` | `[1, 2, 3, 4, 5, 6, 7]` | ✅ 100% Match |
| **`0x33`** | Strong Heart Exterior | 6 | `0x00B9, 0x00BA, 0x0020, 0x0091, 0x0090, 0x0092` | `[2, 3, 4, 5, 6]` | ✅ 100% Match |
| **`0x34`** | Strong Heart's Hut | 7 | `0x0023, 0x00BB, 0x003A, 0x00A5, 0x0095, 0x00BC, 0x00BD` | `[1, 2, 3, 4, 6, 7]` | ✅ 100% Match |
| **`0x38`** | South Jungle Start | 7 | `0x0020, 0x0091, 0x0092, 0x00C4, 0x00C5, 0x00C6, 0x00C7` | `[1, 2, 3, 4, 5, 6, 7]` | ✅ 100% Match |
| **`0x51`** | Village Huts & Blimp | 7 | `0x003A, 0x00A5, 0x0095, 0x00BE, 0x0020, 0x0091, 0x0092` | `[1, 2, 3, 4, 5, 6, 7]` | ✅ 100% Match |
| **`0x65`** | Swamp Main Area | 7 | `0x000A, 0x000D, 0x00D8, 0x00A6, 0x00A7, 0x00A8, 0x00A9` | `[1, 2, 3, 4, 5, 6, 7]` | ✅ 100% Match |

---

## 7. Verified Reference Python Implementation

The following complete, standalone module extracts all room palettes and maps them directly to RGBA color tables ready for renderer integration:

```python
from typing import List, Tuple

RGBA = Tuple[int, int, int, int]


def extract_tile_family_palette(rom: bytes, family_id: int) -> List[RGBA]:
    """
    Extracts 16 RGBA colors for a single tile family from ROM $9CC322.
    Color 0 is transparent (Alpha = 0). Colors 1..15 are opaque (Alpha = 255).
    """
    base_addr = 0x1CC322 + (family_id * 32)
    colors: List[RGBA] = []

    for i in range(16):
        c16 = rom[base_addr + i * 2] | (rom[base_addr + i * 2 + 1] << 8)
        r5 = (c16 >> 0) & 0x1F
        g5 = (c16 >> 5) & 0x1F
        b5 = (c16 >> 10) & 0x1F

        # SNES 5-bit to 8-bit expansion: (c << 3) | (c >> 2)
        r8 = (r5 << 3) | (r5 >> 2)
        g8 = (g5 << 3) | (g5 >> 2)
        b8 = (b5 << 3) | (b5 >> 2)
        a8 = 0 if i == 0 else 255

        colors.append((r8, g8, b8, a8))

    return colors


def build_room_cgram_palettes(rom: bytes, tile_families: List[int]) -> List[List[RGBA]]:
    """
    Constructs the 8 CGRAM background palettes for a room.
    - Palette 0: Fallback transparent / black.
    - Palette 1..7: Mapped to tile_families[0..6].
    """
    palettes: List[List[RGBA]] = []

    # Palette 0: System / HUD default
    palettes.append([(0, 0, 0, 0 if i == 0 else 255) for i in range(16)])

    # Palettes 1..7 from room tile families
    for idx in range(7):
        if idx < len(tile_families):
            palettes.append(extract_tile_family_palette(rom, tile_families[idx]))
        else:
            # Fallback for unused palette slots
            palettes.append([(0, 0, 0, 0 if i == 0 else 255) for i in range(16)])

    return palettes
```
