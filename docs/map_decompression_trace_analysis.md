# Empirical Reverse Engineering: Secret of Evermore Map Decompression Pipeline

> [!IMPORTANT]
> **Zero-Trust Trace Methodology**  
> All logic documented here is derived directly from 65c816 disassembly trace logs captured in Mesen2 under `/Users/v/Library/Application Support/Mesen2/Debugger/` for **Room `0x33` (Prehistoria - Strong Heart's Exterior)**.  
> No speculative heuristics from legacy tools are assumed without line-by-line assembly verification.

---

## Pipeline Overview

The Secret of Evermore room-rendering pipeline executes across five distinct stages across three ROM payload blocks:

```mermaid
flowchart TD
    ROM_Blob["ROM Map Blob ($ADB50C)"] --> Stage1["Stage 1: Header & Trigger Parsing"]
    Stage1 --> Block1["Block 1: LZSS Bitstream ($8C988D)"]
    Block1 --> Stage2["Stage 2: Delta Accumulator ($908E85)"]
    Stage2 --> Stage3["Stage 3: CHR Tile Graphics DMA ($8CC88C)"]
    Stage1 --> Block2["Block 2: 2D Context-Predictive Markov Bitstream ($8C9BD0)"]
    Stage1 --> Block3["Block 3: LZSS Metatile VRAM Words ($8C988D)"]
    Block2 --> Stage4["Stage 4: Layer 1 Grid Assembly ($7F0000, 20x16)"]
    Block3 --> Stage5["Stage 5: Metatile VRAM Word Table ($7F0280)"]
    Stage4 & Stage5 --> Stage6["Stage 6: PPU VRAM Tilemap Streaming ($909460)"]

    subgraph Memory_Destinations ["WRAM / VRAM Sinks"]
        Stage2 -->|97 Unique Tile IDs| WRAM_7FC300["WRAM $7FC300 (Delta Buffer)"]
        Stage3 -->|4bpp CHR Patterns| VRAM_CHR["SNES VRAM CHR Slots"]
        Stage4 -->|320 Metatile IDs| WRAM_7F0000["WRAM $7F0000 (Layer 1 Grid, 20x16)"]
        Stage5 -->|VRAM Tilemap Words| WRAM_7F0280["WRAM $7F0280 (Metatile Lookup Table)"]
        Stage6 -->|Screen Viewport (18 cols)| VRAM_MAP["SNES VRAM Tilemap ($0000+)"]
    end
```

> [!NOTE]
> **100% Empirically Verified Pipeline**
> All stages from raw ROM blob to final SNES VRAM tilemap words have been traced and verified bit-for-bit against Mesen2 trace logs for **Room `0x33` (Prehistoria - Strong Heart's Exterior)**.

---

# Trace 1: The Delta Accumulator Loop

**Trace File:** `strongheart_exterior_decode_tiles?__breakpoint_execute_rom=108E85.txt`  
**Breakpoint:** Execute ROM address `0x108E85` (SNES address `$908E85`)  
**Purpose:** In-place conversion of raw signed/unsigned 16-bit deltas into absolute tile IDs.

### 1.1 Assembly Trace

```assembly
; Entry state:
;   A = 0x0000
;   X = 0x0060 (Loop counter: 96 iterations = 97 entries)
;   Y = 0x0000 (Byte offset)
;   [$3A] = Points to WRAM $7FC300

loop_accumulate:
    908E85  CLC                            ; Clear carry before addition
    908E86  ADC [$3A],Y [$7FC300 + Y]      ; Add 16-bit delta from WRAM
    908E88  STA [$3A],Y [$7FC300 + Y]      ; Store accumulated sum in-place
    908E8A  INY                            ; Increment Y by 2 bytes (16-bit word)
    908E8B  INY
    908E8C  DEX                            ; Decrement counter
    908E8D  BPL loop_accumulate            ; Branch if X >= 0
```

### 1.2 Pseudocode Translation

```python
def stage3_accumulate_deltas(deltas: list[int]) -> list[int]:
    """
    Simulates the in-place 16-bit accumulation loop at $908E85.
    Overflow wraps strictly at 16-bit boundary (0x10000).
    """
    accumulated = []
    running_sum = 0
    for delta in deltas:
        running_sum = (running_sum + delta) & 0xFFFF
        accumulated.append(running_sum)
    return accumulated
```

### 1.3 Empirical Verification

| WRAM Offset | Raw Delta Input | Trace Register `A` | Python Output | Status |
|---|---|---|---|:---:|
| `+$00` | `0x0000` | `0x0000` (Line 31) | `0x0000` | ✅ Exact match |
| `+$02` | `0x0282` | `0x0282` (Line 42) | `0x0282` | ✅ Exact match |
| `+$04` | `0x0145` | `0x03C7` (Line 53) | `0x03C7` | ✅ Exact match |
| `+$06` | `0x0001` | `0x03C8` (Line 61) | `0x03C8` | ✅ Exact match |
| `+$08` | `0x0001` | `0x03C9` (Line 70) | `0x03C9` | ✅ Exact match |
| `+$0A` | `0xFEBC` | `0x0285` (Line 80) | `0x0285` | ✅ Exact match |
| `+$0C` | `0x0001` | `0x0286` (Line 89) | `0x0286` | ✅ Exact match |
| `+$0E` | `0x012A` | `0x03B0` (Line 98) | `0x03B0` | ✅ Exact match |
| `+$10` | `0x0001` | `0x03B1` (Line 108) | `0x03B1` | ✅ Exact match |

---

# Trace 2: The Master Decompression Dispatcher & LZSS Decompressor

**Trace File:** `strongheart_exterior_read_7fc300_twice__breakpoint_read_bu=7FC300.txt`  
**Breakpoint:** Read Bus address `$7FC300` (hit at instruction `908E86`)  
**Subroutine Address:** `$8C988D` (ROM file offset `0x0C988D`)  
**Purpose:** Master decompression dispatcher. Reads the 1-byte `sub_flag` method tag and dispatches to the corresponding decompression engine.  
**Destination Buffers:** WRAM `$7FC300` (Block 1), `$7F0000` (Block 2), `$7F0280` (Block 3)  
**Sliding Window:** 4,096 bytes at WRAM `$7FA000..$7FAFFF` (used when method is LZSS)

### 2.1 Dispatcher Routine ($8C988D)

Every compressed payload block begins with a 3-byte subheader:
- **Byte 0 (`sub_flag`)**: Decompression algorithm index (multiplied by 2 for jump table index).
- **Bytes 1–2 (`decomp_size`)**: Expected decompressed output size in bytes.

```assembly
; Master Dispatcher Entry at $8C988D:
8C988D  LDY #$0000
8C9890  LDA [$36],Y     ; Read sub_flag (method tag)
8C9892  INY
8C9893  AND #$00FF
8C9896  ASL             ; tag * 2 (table stride)
8C9897  TAX             ; Index into dispatch table
8C9898  LDA [$36],Y     ; Read 16-bit decomp_size
8C989A  INY
8C989B  INY
8C989C  STA $34         ; Store target size
8C989E  JMP ($98A1,X)   ; Dispatch to algorithm handler!

; Dispatch Table at $8C98A1:
;   Index 0 ($98A1): $98B1 (Uncompressed copy)
;   Index 3 ($98A7): $98C9 (LZSS Sliding Window Decompressor)
;   Index 7 ($98AF): $9B65 (2D Context-Predictive Markov Bitstream Decoder)
```

### 2.2 Algorithm 3: LZSS Sliding-Window Decompressor ($8C98C9)

Used for **Payload Block 1** (delta tile palette in 115 of 127 rooms; the remaining 12 rooms use Algorithm 0 Uncompressed Copy `$8C98B1`) and **Payload Block 3** (metatile VRAM words table across all rooms).

```assembly
; Setup sliding window buffer at $7FA000
8C98EA  LDA #$A000
8C98ED  STA $08         ; Window write pointer ($7FA000)
8C98EF  LDA #$A000
8C98F2  CLC
8C98F3  ADC #$1000      ; Window bound ($7FB000)
8C98F6  STA $0C

; Bitstream read loop
8C98FD  REP #$20
8C9903  LDA $8C9A46,X   ; Load bitmask (0x8000 >> bit_index)
8C9907  STA $0E
8C9909  LDA [$2A],Y     ; Read 16-bit word from ROM bitstream
8C990B  XBA
8C990C  BIT $0E         ; Test flag bit
8C990E  BEQ lz_reference; If 0 -> LZ reference token
                        ; If 1 -> Literal byte

literal_byte:
    8C991F  JMP ($9B12,X)   ; Unaligned bit-extraction table for literal byte
    8C9928  STA ($02)       ; Write literal byte to destination ($7FC300)
    8C992A  STA ($08)       ; Write literal byte to history window ($7FA000)
    8C992E  INC $02         ; Increment output pointer
    8C9930  INC $08         ; Increment window pointer (modulo 4096)
    8C993D  JMP $8C98FD     ; Next token

lz_reference:
    8C994F  ASL
    8C9951  JMP ($9A66,X)   ; Unaligned bit-extraction table for 16-bit token
    8C99CB  CMP #$FEE0
    8C99D0  LSR A
    8C99D1  LSR A
    8C99D2  LSR A
    8C99D3  LSR A           ; Token >> 4 gives window offset
    8C99D4  BEQ lz_exit     ; If offset == 0 -> END OF STREAM SENTINEL
    8C99D7  ADC #$9FFF      ; Window pointer = (offset - 1) relative to $7FA000
    8C99DA  TAX             ; X = window source address
    8C99DC  AND #$000F
    8C99DF  ADC #$0002      ; Length = (Token & 0x0F) + 2
    8C99E2  TAY             ; Y = copy length counter

lz_copy_loop:
    8C99E5  LDA $0000,X     ; Read from history window
    8C99E8  STA ($02)       ; Write to output
    8C99EA  STA ($08)       ; Write to current window position
    8C99EE  INC $02
    8C99F0  INC $08
    8C99FD  INX
    8C99FE  DEY
    8C99FF  BNE lz_copy_loop
    8C9A01  JMP $8C98FD

lz_exit:
    8C98E9  RTL             ; Return from subroutine
```

### 2.2 Pseudocode Translation

```python
class LZSSDecompressor:
    def __init__(self, rom_data: bytes, stream_offset: int):
        self.data = rom_data
        self.ptr = stream_offset
        self.bit_buf = 0
        self.bits_left = 0
        self.window = bytearray(0x1000) # 4096-byte circular buffer
        self.win_ptr = 0
        self.output = bytearray()

    def read_bit(self) -> int:
        if self.bits_left == 0:
            self.bit_buf = self.data[self.ptr]
            self.ptr += 1
            self.bits_left = 8
        bit = (self.bit_buf >> 7) & 1
        self.bit_buf = (self.bit_buf << 1) & 0xFF
        self.bits_left -= 1
        return bit

    def read_bits(self, count: int) -> int:
        val = 0
        for _ in range(count):
            val = (val << 1) | self.read_bit()
        return val

    def decompress(self) -> bytearray:
        while True:
            flag = self.read_bit()
            if flag == 1:
                # Literal byte
                byte = self.read_bits(8)
                self.output.append(byte)
                self.window[self.win_ptr] = byte
                self.win_ptr = (self.win_ptr + 1) & 0xFFF
            else:
                # 16-bit LZ Reference
                token = self.read_bits(16)
                offset = token >> 4
                if offset == 0:
                    # End of stream sentinel
                    break
                length = (token & 0x0F) + 2
                src = (offset - 1) & 0xFFF
                for _ in range(length):
                    byte = self.window[src]
                    src = (src + 1) & 0xFFF
                    self.output.append(byte)
                    self.window[self.win_ptr] = byte
                    self.win_ptr = (self.win_ptr + 1) & 0xFFF
        return self.output
```

### 2.3 Empirical Verification

Running the pseudocode decompressor on raw ROM bytes at `0x2DB53C` yields 220 bytes.  
Converting the output to 16-bit words produces:
`0x0000, 0x0282, 0x0145, 0x0001, 0x0001, 0xFEBC, 0x0001, 0x012A, 0x0001...`  
**This matches byte-for-byte with the inputs read by Trace 1.**

# Trace 3: The 2D Context-Predictive Markov Bitstream Decoder & Grid Assembly

**Trace File:** `strongheart_exterior__breakpoint_bus=7f0000.txt`  
**Breakpoint:** Write Bus address `$7F0000` (hit at instruction `8C9C3A`)  
**Subroutine Address:** `$8C9BD0` (ROM file offset `0x0C9BD0`)  
**Source Stream:** ROM `$ADB5E7` (Payload Block 2, `sub_flag = 0x07`, `decomp_size = 640`)  
**Destination:** WRAM `$7F0000` (Layer 1 Grid, 20x16 = 320 words)  
**Prediction State Table:** WRAM `$7F0280..$7F08FF` (Markov transition cache, initialized at `$8C9B87`)

### 3.1 2D Context Prediction Model Architecture

The map grid is compressed using an adaptive **2D Markov predictive bitstream decoder**. For every cell $(x, y)$, the decoder uses two contexts:
- **`$26` (Above)**: Metatile ID of the cell directly above $(x, y-1)$
- **`$12` (Left)**: Metatile ID of the cell directly to the left $(x-1, y)$

The transition cache at `$7F0280 + tid` maintains 4 prediction slots per metatile:
`[Above_Prediction_1, Left_Prediction_1, Above_Prediction_2, Left_Prediction_2]`.

Tokens are variable-length prefix codes:
- **`1` (1 bit, Opcode `0x10..0x1F` $\to$ `$8C9C55`)**: Predicted by tile above (`Above_Prediction_1`).
- **`000` (3 bits, Opcode `0x00..0x03` $\to$ `$8C9C62`)**: Predicted by tile to the left (`Left_Prediction_1`).
- **`00100` (5 bits, Opcode `0x04` $\to$ `$8C9C75`)**: Secondary prediction from above (`Above_Prediction_2`).
- **`00101` (5 bits, Opcode `0x05` $\to$ `$8C9C88`)**: Secondary prediction from left (`Left_Prediction_2`).
- **`0011` (4 bits, Opcode `0x06..0x07` $\to$ `$8C9C30`)**: Next sequential new metatile (`next_seq_tile += 8`).
- **`01` (2 bits, Opcode `0x08..0x0F` $\to$ `$8C9C9B`)**: Literal metatile index read directly from the bitstream (`tile_bits` bits).

### 3.2 Metatile VRAM Tilemap Words (Payload Block 3)

**Subroutine:** `$90919E` $\to$ `JSL $8C988D` (LZSS)  
**Source Stream:** ROM `$ADB69E + 3` (ROM file offset `0x2DB6A1`)  
**Output:** 1,182 bytes of raw 16-bit SNES VRAM tilemap words.  
The engine uploads these words into VRAM at `$2000`, then at `$9091F7` reads them back into `$7F0280` as the metatile VRAM word lookup table (`metatile_to_vram[0x0280 + i * 8] = word`).

### 3.3 Final PPU Tilemap Streaming ($909460)

During rendering, subroutine `$909460` iterates over the active viewport (18 columns of rows 0..15):
```assembly
909460  LDY $0000,X [$7F0000 + offset] ; Read Metatile ID (e.g. $0280)
909463  LDA ($26),Y [$7F0280 + offset] ; Lookup corresponding VRAM Word ($30C0)
909465  STA VMDATAL                    ; Stream to SNES PPU VRAM!
```

### 3.4 WRAM Memory Map for Room 0x33 ($20 \times 16 = 320$ tiles)

| WRAM Address Range | Size | Content | Format |
|---|---|---|---|
| `$7F0000 .. $7F027F` | 640 bytes (320 words) | **Layer 1 Metatile Grid** | Row-major $20 \times 16$ 16-bit metatile offsets (`0x0280, 0x0288...`) |
| `$7F0280 .. $7F08FF` | 1,664 bytes | **Metatile VRAM Word Table & Markov Cache** | 8 bytes per metatile: VRAM tilemap word + prediction context slots |
| `$7FA000 .. $7FAFFF` | 4,096 bytes | **LZSS Sliding Window** | Circular byte buffer |
| `$7FC300 .. $7FC3C1` | 194 bytes (97 words) | **Delta CHR Tile Palette** | Raw unpacked tile ID deltas for `$EE0000` lookup |

---

# Trace 4: Resource Lookup & VRAM CHR Upload

**Trace File:** `strongheart_exterior_decode_tiles_fist_call__breakpoint_bus=ee0000.txt`  
**Breakpoint:** Bus read on `$EE0000`  
**Subroutine Address:** `$8CC88C`  
**Purpose:** Given a Tile ID, resolve its 24-bit **CHR graphics** pointer from `$EE0000` and stream pixel data to VRAM.

> [!NOTE]
> **This table resolves compressed pixel data (4bpp CHR), NOT tilemap words.**
> The `$EE0000` lookup determines WHERE in ROM the tile's graphic pattern lives, so the engine can DMA it into VRAM character slots. The VRAM tilemap words (char index + palette + flip flags) that reference those character slots originate from **Payload Block 3** (`$ADB69E`), decompressed via LZSS into `$7F0280`.

### 4.1 Assembly Trace Breakdown

```assembly
; Resolve pointer from $EE0000 table:
;   tile_id in register A
8CC892  STA $14 [$000014]       ; Store tile index
8CC894  ASL                     ; tile_id * 2
8CC895  ADC $14                 ; tile_id * 3 (24-bit pointer stride)
8CC897  TAX
8CC898  LDA $EE0000,X           ; Read 16-bit address (low/high)
8CC89C  STA $12
8CC8A1  LDA $EE0002,X           ; Read 8-bit bank byte
8CC8A4  STA $14
; Result: Source pointer = $14:$12 (e.g. $80:BBFD)

; Configure DMA Channel 1:
8CC958  STA $4315 [DAS1L]       ; DMA transfer size (words * 2)
8CC969  STA $4312 [A1T1L]       ; DMA source address
8CC976  STA $4314 [A1B1]        ; DMA source bank
8CC97C  STX $4310 [DMAP1]       ; DMA mode ($1801 = CPU to VMDATAL $2118)
8CC981  STA $420B [MDMAEN]      ; Trigger DMA transfer

; Zero-fill padding for partial tiles ($8CCC62):
8CCC62  ASL
8CCC6D  LDA #$2100              ; Direct Page = $2100 (hardware registers)
8CCC70  TCD
; Repeated STX $18 writes zeroes into VMDATA ($2118) to pad unused tile block
```

### 4.2 Pseudocode Translation

```python
def resolve_tile_rom_pointer(rom: bytes, tile_id: int) -> int:
    """
    Simulates the $EE0000 resource table lookup at $8CC892.
    Formula: EE0000 + (tile_id * 3) -> 24-bit SNES address -> ROM file offset.
    """
    table_base_rom = 0x2E0000 # SNES $EE0000 in HiROM file offset
    entry_offset = table_base_rom + (tile_id * 3)
    
    addr_low = rom[entry_offset]
    addr_high = rom[entry_offset + 1]
    bank = rom[entry_offset + 2]
    
    snes_addr = (bank << 16) | (addr_high << 8) | addr_low
    # Convert SNES address to ROM file offset
    return snes_addr & 0x3FFFFF
```


---

# Trace 5: VRAM Tilemap Analysis & WRAM-to-VRAM Verification

**Source Data:** Mesen2 PPU VRAM Hex Dump for Room `0x33`  
**Dump Format:** 16-bit little-endian words, 32 entries per row (64 bytes/row)  
**Verification Result:** **100% bit-for-bit consistent** with decompressed WRAM Layer 1 metatiles.

### 5.1 SNES VRAM Tilemap Format

In SNES PPU architecture, background tilemap entries are 16-bit little-endian words formatted as:

$$\text{Bitfield: } \underbrace{v}_{\text{b15}} \, \underbrace{h}_{\text{b14}} \, \underbrace{p}_{\text{b13}} \, \underbrace{ppp}_{\text{b12..10}} \, \underbrace{cccccccccc}_{\text{b9..0}}$$

- **`v` (Bit 15):** Vertical Flip
- **`h` (Bit 14):** Horizontal Flip
- **`p` (Bit 13):** Background Tile Priority ($1 = \text{High}$, $0 = \text{Low}$)
- **`ppp` (Bits 12–10):** Palette Index ($0 \dots 7$)
- **`cccccccccc` (Bits 9–0):** 8x8 Character Tile Number ($0 \dots 1023$)

### 5.2 Decoded Dump Layout

A standard SNES tilemap buffer has a fixed row stride of **32 words (64 bytes)**:
- **Columns 0–17 (Active Viewport):** Populated with active map tiles matching Room 0x33's $20 \times 16$ tile grid ($320 \times 256$ pixels).
- **Columns 18–19 (Off-camera Buffer):** Populated on scroll when the camera moves right; initially zeroed.
- **Columns 20–31 (Padding/Margin):** 12 unused offscreen margin entries per row ($32 - 20 = 12$ entries = 24 zero bytes `00 00 ...`).
- **Rows 00–15:** The 16 vertical rows of Room 0x33.
- **Row 16+:** Unallocated VRAM buffer space below the room boundary.

### 5.3 Empirical Metatile-to-VRAM 1-to-1 Mapping

Each metatile in Bank `$7F` is assigned an 8-byte aligned offset starting at `$0280` (`$0280, $0288, $0290, $0298...`).
The 16-bit VRAM tilemap word for each metatile is directly extracted from **Payload Block 3** (`$ADB69E + 3`), where each entry maps 1:1 to an on-screen SNES PPU background tile:

| Metatile Offset (`$7F0000`) | VRAM Word | Hex Flags | Char Index | Palette | Priority | H-Flip | V-Flip | Visual Role / Note |
|---|---|---|---|:---:|:---:|:---:|:---:|---|
| `0x0280` | `0x30C0` | `0x30` | `0x0C0` | 4 | 1 | 0 | 0 | Canopy / foliage pattern A |
| `0x0288` | `0x30C2` | `0x30` | `0x0C2` | 4 | 1 | 0 | 0 | Canopy / foliage pattern B |
| `0x0298` | `0x30CC` | `0x30` | `0x0CC` | 4 | 1 | 0 | 0 | Canopy lower edge A |
| `0x02A0` | `0x30CE` | `0x30` | `0x0CE` | 4 | 1 | 0 | 0 | Canopy lower edge B |
| `0x02B0` | `0x708C` | `0x70` | `0x08C` | 4 | 1 | **1** | 0 | Canopy corner |
| `0x02B8` | `0xB0A8` | `0xB0` | `0x0A8` | 4 | 1 | 0 | **1** | Canopy underside |
| `0x0488` | `0x350E` | `0x35` | `0x10E` | 5 | 1 | 0 | 0 | Hut / tree left side |
| `0x04C8` | `0x750E` | `0x75` | `0x10E` | 5 | 1 | **1** | 0 | Hut / tree right side (H-Flip mirror of `0x0488`) |
| `0x04A0` | `0x3524` | `0x35` | `0x124` | 5 | 1 | 0 | 0 | Tree branch left |
| `0x04B0` | `0x7524` | `0x75` | `0x124` | 5 | 1 | **1** | 0 | Tree branch right (H-Flip mirror of `0x04A0`) |
| `0x05B0` | `0x1544` | `0x15` | `0x144` | 5 | 0 | 0 | 0 | Trunk interior left (Low priority) |
| `0x05E0` | `0x5544` | `0x55` | `0x144` | 5 | 0 | **1** | 0 | Trunk interior right (H-Flip mirror of `0x05B0`) |

> [!TIP]
> **Graphic Compression via Hardware Mirroring**  
> Notice how symmetrical structures (such as Strong Heart's giant hut tree) re-use the exact same character tile patterns (`0x10E`, `0x124`, `0x144`, `0x146`, `0x164`), toggling bit 14 (`H-Flip`) for the right half. This halves the required VRAM CHR space.

### 5.4 Verification Against PPU VRAM Dump

Streaming the active 18 columns of rows 00–15 through the table produces a **100% bit-for-bit match** against the Mesen2 PPU VRAM tilemap dump:

```text
Row 00: C0 30 C2 30 C0 30 C2 30 C0 30 C2 30 C0 30 C2 30 C0 30 C2 30 C0 30 C2 30 C0 30 C2 30 C0 30 C2 30 C0 30 C2 30
Row 01: CC 30 CE 30 CC 30 C0 30 C2 30 CE 30 CC 30 CE 30 CC 30 CE 30 CC 30 CE 30 CC 30 CE 30 CC 30 CE 30 C2 30 CE 30
Row 02: C0 30 C2 30 C0 30 CC 30 CE 30 8C 70 A8 B0 CC 30 8E B0 C6 B0 C6 B0 A4 B0 AC B0 E8 B0 C0 30 C2 30 CE 30 C0 30
Row 03: C0 30 C2 30 CC 30 CE 30 CC 30 A0 70 A0 30 E8 F0 EA 34 EC 74 EA 74 00 A8 00 A8 A6 B0 E4 30 E8 B0 C0 30 C2 30
Row 04: CC 30 CE 30 8E B0 E6 30 E8 F0 C4 2C 00 A8 EE 34 00 35 02 75 00 75 EE 74 00 A8 48 68 E2 F0 00 A8 E4 70 CC 30
Row 05: C2 30 A8 70 00 A8 E2 B0 00 A8 04 35 06 35 08 35 0A 35 0C 75 0A 75 08 75 06 75 04 75 A6 30 C6 30 C0 30 C2 30
Row 06: CE 30 CC 30 A4 30 AA 30 AC 30 0E 35 20 35 22 35 24 35 26 75 24 75 22 75 20 75 0E 75 00 A8 E2 B0 E8 B0 CC 30
Row 07: CE 30 E6 30 8E B0 C8 30 CA 30 28 35 2A 35 2C 35 2E 35 40 75 2E 75 2C 75 2A 75 28 75 00 A8 00 A8 E2 30 E4 70
Row 08: C2 30 E4 30 00 A8 00 A8 00 A8 42 35 44 15 46 15 48 35 4A 75 48 75 46 55 44 55 42 75 00 A8 A6 B0 C6 B0 C0 30
Row 09: CE 30 C2 30 A6 F0 00 A8 00 A8 00 A8 4C 15 4E 15 60 35 62 75 60 75 4E 55 4C 55 00 A8 00 A8 00 A8 00 A8 E4 70
Row 10: C2 30 E4 30 00 A8 00 A8 00 A8 00 A8 64 15 66 15 68 15 00 A8 68 55 66 55 64 55 00 A8 00 A8 00 A8 00 A8 E8 B0
Row 11: CE 30 C2 30 A4 70 A2 B0 00 A8 00 A8 00 A8 6C 15 6E 15 00 A8 6E 55 6C 55 00 A8 00 A8 00 A8 00 A8 00 A8 A0 B0
Row 12: CC 30 CE 30 C0 70 AE 70 00 A8 E0 2C 00 A8 E2 30 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 E2 70 00 A8 00 A8 AE 30
Row 13: C0 30 C0 30 C2 30 C2 30 A4 70 E8 70 00 A8 E4 70 E8 70 00 A8 E8 30 C6 30 E8 70 00 A8 E4 70 A4 30 AC 30 A4 70
Row 14: C0 30 C2 30 C0 30 C0 30 C2 30 A8 70 E8 30 C0 30 C2 30 8E 30 C0 30 C0 30 C2 30 C6 30 C0 30 C2 30 C0 30 C2 30
Row 15: CC 30 CE 30 CC 30 CC 30 CE 30 C0 30 C2 30 C0 30 C2 30 C0 30 CC 30 CC 30 CE 30 C0 30 CC 30 CE 30 CC 30 CE 30
```

---

# Trace 6: Multi-Layer Planar Architecture, Hardware Division & Room 0x38 Verification

**Subroutine Addresses:** `$909180..$909245` (Metatile Table Initialization) and `$909460` (PPU Tilemap Streaming)  
**Hardware Registers:** SNES Math Unit `$4204..$4206` (Dividend/Divisor), `$4214` (Quotient), PPU `VMDATA` (`$2118`)  
**Verified Maps:** Room `0x33` ($20 \times 16$, Strong Heart's Exterior) and Room `0x38` ($83 \times 91$, Prehistoria South Jungle)

---

### 6.1 The 3-Slice Planar Layout of Payload Block 3

Earlier hypotheses assumed that Payload Block 3 held only a single layer of VRAM tilemap words. Reverse-engineering of subroutine `$909180..$909245` revealed that **Block 3 contains multi-layer graphics and collision data packed in a planar structure**:

1. **Hardware Division by 6 (`$9091B0`):**
   When Block 3 finishes LZSS decompression (`JSL $8C988D`), the decompressed byte count $S$ is loaded into the SNES hardware math registers:
   ```assembly
   9091B0  STA $4204          ; Set 16-bit dividend = decompressed byte count S
   9091B5  LDA #$0006
   9091B8  STA $4206          ; Set 8-bit divisor = 6 bytes per metatile definition
   ; 16-cycle hardware wait loop
   9091C5  LDA $4214          ; Read 16-bit quotient = N (metatile count)
   9091C8  STA $18            ; $18 = N
   ```
   Each metatile definition in Block 3 requires exactly **6 bytes (3 16-bit words)**:
   - **Slice 0 (Words $0 \dots N-1$):** **Layer 1 (Canopy / BG2)** SNES VRAM tilemap words.
   - **Slice 1 (Words $N \dots 2N-1$):** **Layer 2 (Terrain / BG1)** SNES VRAM tilemap words.
   - **Slice 2 (Words $2N \dots 3N-1$):** **Collision & Passability Attributes** (walkability, elevation, solid barriers).

2. **WRAM Distribution Loop (`$9091D0..$909245`):**
   The SNES engine unpacks these 3 planar arrays into an 8-byte record per metatile starting at `$7F0000 + base_metatile`:
   - `+$00`: Slice 0 word (Layer 1 / Canopy VRAM tilemap entry)
   - `+$02`: Slice 1 word (Layer 2 / Terrain VRAM tilemap entry)
   - `+$04`: Slice 2 word (Collision & passability attributes)
   - `+$06`: Markov prediction context slot

```
Block 3 LZSS Decompressed Stream (Planar, 3N words):
+-------------------------+-------------------------+-------------------------+
| Slice 0: Words 0..N-1   | Slice 1: Words N..2N-1  | Slice 2: Words 2N..3N-1 |
| (Layer 1 / Canopy)      | (Layer 2 / Terrain)     | (Collision Attributes)  |
+-------------------------+-------------------------+-------------------------+
             |                         |                         |
             v                         v                         v
Bank $7F WRAM Record for Metatile i (8 bytes per entry at $7F0000 + base_metatile + i * 8):
+----------------+----------------+----------------+----------------+
| +$00: Layer 1  | +$02: Layer 2  | +$04: Collision| +$06: Markov   |
|   VRAM Word    |   VRAM Word    |   Attribute    |   Cache Slot   |
+----------------+----------------+----------------+----------------+
```

---

### 6.2 Metatile ID as Direct WRAM Bank `$7F` Memory Offset

A critical discovery in the decompression architecture is that **the 16-bit values in the 2D Markov grid are not sequential indices ($0, 1, 2\dots$), but direct byte offsets in SNES WRAM Bank `$7F`**:

$$\text{base\_metatile} = \text{width\_tiles} \times \text{height\_tiles} \times 2$$
$$\text{Metatile ID}_i = \text{base\_metatile} + (i \times 8)$$

- The 2D Markov grid decompresses into `$7F0000 .. $7F0000 + \text{base\_metatile} - 1`.
- The metatile record table immediately follows at `$7F0000 + \text{base\_metatile}`.
- In Room 0x33 ($20 \times 16$): $\text{base\_metatile} = 20 \times 16 \times 2 = 640 = \text{0x0280}$. Metatile IDs are `0x0280, 0x0288, 0x0290...`.
- In Room 0x38 ($83 \times 91$): $\text{base\_metatile} = 83 \times 91 \times 2 = 15106 = \text{0x3B02}$. Metatile IDs are `0x3B02, 0x3B0A, 0x3B12...`.

During rendering (`$909460`), the CPU loads the metatile ID straight into index register `Y`:
```assembly
909460  LDY $0000,X [$7F0000 + cell_offset] ; Y = base_metatile + (i * 8)
909463  LDA ($26),Y                         ; Direct lookup at $7F0000 + Y ($26 = $7F0000)
909465  STA VMDATAL                         ; Stream directly to PPU VRAM register ($2118)
```
This zero-overhead design eliminates table lookup translations entirely during active gameplay rendering.

---

### 6.3 Deterministic Engine Payload Layout & Block Resolution ($908F60..$909180)

Disassembly of the SNES engine's map loader routine at `$908F60..$909180` reveals that the ROM layout is **100% deterministic with explicit 16-bit length headers**. The engine executes **zero heuristic linear scanning**:

```
ROM Room Blob ($8B):
  +$00: 13-byte Map Header ($00..$0C)
  +$0D: Step-On Trigger Table: [step_len: 2 bytes] + [step_len bytes records]
  +...: B-Trigger Table: [b_len: 2 bytes] + [b_len bytes records]
  +...: Tile Families Table: [fam_count: 1 byte] + [fam_count * 2 bytes]
  +...: Section 1 (CHR Descriptors): [desc_count: 1 byte] + [desc_count * 3 bytes]
  +...: Block 1 (Tile Palette): [b1_len: 2 bytes] + [b1_len bytes data]
  +...: Section 2: [sec2_count: 1 byte] + [sec2_len: 2 bytes] + [sec2_len bytes data]
  +...: Section 3: [sec3_count: 1 byte] + [sec3_count * 2 bytes]
  +...: Block 2 (Markov Grid): [b2_len: 2 bytes] + [b2_len bytes data]
  +...: Section 4: [sec4_len: 2 bytes] + [sec4_len bytes data]
  +...: Block 3 (Metatile Table): [b3_len: 2 bytes] + [b3_len bytes data]
```

#### 1. Header & Trigger Tables
- **Map Header (`$00..$0C`)**:
  - `$00`: `origin_x` (stored at `$0F86`, added to Player Tile X during trigger checks)
  - `$01`: `origin_y` (stored at `$0F88`, added to Player Tile Y during trigger checks)
  - `$02`: `width_tiles` (stored at `$08EE`; stride in bytes = $W \times 2$ at `$0F46`; map X end = $W \times 16$ at `$7E23ED`)
  - `$03`: `height_tiles` (stored at `$08F0`; map Y end = $H \times 16$ at `$7E23EF`)
  - `$04..$07`: PPU registers `$212C` (TM), `$212D` (TS), `$2131` (CGADSUB), `$2130` (CGWSEL)
  - `$08`: `effect_variant` (stored at `$7E241F`, indexes effect table at `$908E74`)
  - `$09..$0A`: 16-bit parameter stored at `$0F84`
  - `$0B..$0C`: 16-bit padding (skipped)
- **Step-on Triggers (`$0D`)**: `step_len = read16(rom, blob + 13)`. Records begin at `blob + 15` (`$1064`).
- **B-Triggers**: `b_len_off = blob + 15 + step_len`. `b_len = read16(rom, b_len_off)`. Records begin at `b_len_off + 2` (`$1069`).

#### 2. Trigger Evaluation Check ($8FACCE..$8FAD08)
The engine shifts player pixel coordinates right by 4 bits (`LSR A` $\times 4$), converting pixels to metatiles ($1:16$). Trigger bounding boxes (6 bytes: `y_min, x_min, y_max, x_max, script_id`) are checked via:
$$y_{min} \le (Y_{pix} \gg 4) + origin\_y < y_{max} \quad \text{AND} \quad x_{min} \le (X_{pix} \gg 4) + origin\_x < x_{max}$$

#### 3. Deterministic Payload Block Pointers
Following B-triggers:
1. **Tile Families**: `fam_off = b_len_off + 2 + b_len`. `fam_count = rom[fam_off]`.
2. **Section 1 (CHR Descriptors)**: `pos_desc = fam_off + 1 + fam_count * 2`. `desc_count = rom[pos_desc]`.
3. **Block 1 (Delta Tile Palette)**:
   - Starts at `pos_after_desc = pos_desc + 1 + desc_count * 3`.
   - Length: `b1_len = read16(rom, pos_after_desc)`.
   - Subheader at `pos_after_desc + 2`: `[sub_flag: 1 byte][decomp_size: 2 bytes]`.
   - Handled via dispatcher `$8C988D`:
     - **In 115 rooms:** `sub_flag == 0x03` $\to$ LZSS (`$8C98C9`)
     - **In 12 rooms:** `sub_flag == 0x00` $\to$ Uncompressed copy (`$8C98B1`)
   - 16-bit in-place delta accumulator (`$908E85`) accumulates into WRAM `$7FC300`.
4. **Intermediate Section 2**:
   - `sec2 = pos_after_desc + 2 + b1_len`.
   - Count `rom[sec2]`, length `sec2_len = read16(rom, sec2 + 1)`.
5. **Intermediate Section 3**:
   - `sec3 = sec2 + 3 + sec2_len`.
   - Count $K = \text{rom}[sec3]$ of 2-byte descriptors.
6. **Block 2 (2D Markov Metatile Grid)**:
   - Starts at `b2_off = sec3 + 1 + K * 2`.
   - Length: `b2_len = read16(rom, b2_off)`.
   - Subheader at `b2_off + 2`: `sub_flag == 0x07`, `decomp_size == width_tiles * height_tiles * 2`.
   - Decompressed via 2D Markov decoder (`$8C9BD0`) directly into WRAM `$7F0000`.
7. **Intermediate Section 4**:
   - `sec4 = b2_off + 2 + b2_len`.
   - Length: `sec4_len = read16(rom, sec4)`.
8. **Block 3 (3-Slice Planar Metatile Table)**:
   - Starts at `b3_off = sec4 + 2 + sec4_len`.
   - Length: `b3_len = read16(rom, b3_off)`.
   - Subheader at `b3_off + 2`: `[sub_flag: 1 byte][decomp_size: 2 bytes]`.
   - Handled via dispatcher `$8C988D`:
     - **In 126 rooms:** `sub_flag == 0x03` $\to$ LZSS (`$8C98C9`)
     - **In Room 0x15 (Brian's Test Ground):** `sub_flag == 0x00` $\to$ Uncompressed copy (`$8C98B1`) of 12 bytes ($N = 2$ metatiles).
   - Decompressed bytes $S$ are divided by 6 (`STA $4206` at `$9091B8`) to obtain metatile count $N = S / 6$:
     - **Slice 0 ($N$ words):** Layer 1 VRAM tilemap words
     - **Slice 1 ($N$ words):** Layer 2 VRAM tilemap words
     - **Slice 2 ($N$ words):** Collision and passability attributes

> [!NOTE]
> **100% Deterministic Empirical Verification:**
> This deterministic offset formula resolves Block 1, Block 2, and Block 3 across **all 127 vanilla rooms (0x00 through 0x7E)** with **127 passed, 0 failed**, requiring zero heuristic scanning.

---

### 6.4 Empirical Validation: Room 0x38 (Prehistoria South Jungle)

Room `0x38` is the expansive starting jungle of the Prehistoria era:

- **Dimensions:** $83 \times 91$ metatiles ($1328 \times 1456$ pixels).
- **Origin Offset:** `(17, 11)`.
- **Display Configuration:** `TM = 0x17` (BG1, BG2, BG3, OBJ active on main screen).
- **Triggers:** 2 Step-on triggers, 31 B-triggers.
- **Tile Families:** 7 families (`0x0006, 0x0008, 0x000A, 0x000C, 0x000E, 0x0010, 0x0012`).
- **Tile Palette:** 126 unique metatile CHR IDs delta-accumulated from Block 1.
- **Block 2 (Markov Grid):** 15,106 decompressed bytes ($83 \times 91 \times 2$), `base_metatile = 0x3B02`.
- **Block 3 (Metatile Table):** 3,900 decompressed bytes $\implies N = 650$ metatiles (1,950 total words).
  - **Slice 0 (650 words):** Layer 1 (Canopy / BG2)
  - **Slice 1 (650 words):** Layer 2 (Terrain / BG1)
  - **Slice 2 (650 words):** Collision Attributes

#### Comparison Against Mesen2 4,096-Byte PPU VRAM Dump

A live emulator VRAM dump captured at camera viewport `(row 3, col 33)` spans two 32-tile wide screens (64 rows $\times$ 32 words = 4,096 bytes):

```
+-------------------------------------------------------------------+
| Screen 1 (Rows 00..31): BG2 Canopy Layer                          |
| - Rows 00..03: Canopy border fill (0x2944)                        |
| - Rows 04..14: Active jungle canopy foliage                       |
| - Rows 15..25: Transparent air / sky (0xA800)                     |
| - Rows 26..31: Lower canopy margin                                |
+-------------------------------------------------------------------+
| Screen 2 (Rows 32..63): BG1 Terrain Layer                         |
| - Rows 32..35: Dirt / grass base fill (0x040A)                    |
| - Rows 36..46: Jungle trails (0x0C2C, 0x054A, 0x054C, 0x4482)    |
| - Rows 47..63: Offscreen VRAM margin                              |
+-------------------------------------------------------------------+
```

- **Screen 1 (Canopy / BG2):**
  Matches `slice0` words from `tools/dump_room.py 0x38 --layer 1` bit-for-bit:
  - Fill tiles: `0x2944` (Palette 2, Char `0x144`).
  - Transparent overlay regions: `0xA800` (Palette 2, Priority 1, transparent character slot).
- **Screen 2 (Terrain / BG1):**
  Matches `slice1` words from `tools/dump_room.py 0x38 --layer 2` bit-for-bit:
  - Base terrain: `0x040A` (Palette 1, Char `0x00A`).
  - Path and foliage transitions: `0x0C2C, 0x054A, 0x054C, 0x4482, 0x11A4`.

---

## Standalone Python Extraction Tool & Integration Tests

The extractor [**`tools/dump_room.py`**](file:///Users/v/Documents/GitHub/everscript/tools/dump_room.py) provides complete extraction of multi-layer room data directly from raw ROM:

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

### Automated Integration Tests (`tests/integration/maps/`)

Regression testing against verified emulator memory dumps lives under `tests/integration/maps/`:
- [`test_room_0x33_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x33_vram.py): Room 0x33 (Strong Heart's Exterior, $20 \times 16$)
- [`test_room_0x34_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x34_vram.py): Room 0x34 (Strong Heart's Hut, $18 \times 18$)
- [`test_room_0x38_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x38_vram.py): Room 0x38 (South Jungle, $83 \times 91$)
- [`test_room_0x25_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x25_vram.py): Room 0x25 (Fire Eyes' Village, $63 \times 58$)
- [`test_room_0x26_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x26_vram.py): Room 0x26 (West Area with Defend, $19 \times 18$)
- [`test_room_0x36_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x36_vram.py): Room 0x36 (Volcano Fire Pits, $25 \times 25$)
- [`test_room_0x51_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x51_vram.py): Room 0x51 (Village Huts & Blimp's Hut, $50 \times 56$)
- [`test_room_0x5b_vram.py`](file:///Users/v/Documents/GitHub/everscript/tests/integration/maps/test_room_0x5b_vram.py): Room 0x5B (East Jungle, $72 \times 48$)

Run the full integration test suite via:
```bash
.venv/bin/pytest tests/integration/maps/ -v
```

---

## The Inverse Pipeline: Encoding

Everything on this page decodes a room blob. [**`tools/encode_room.py`**](file:///Users/v/Documents/GitHub/everscript/tools/encode_room.py) does the reverse -- turns a room model back into the bytes the engine loads -- and is the write path a future map editor uses. See [**`docs/map_encoding.md`**](file:///Users/v/Documents/GitHub/everscript/docs/map_encoding.md) for the container layout, the LZSS and Markov encoders, and the object-area packing.




