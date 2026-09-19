---
name: snes-memory-mapping
description: Explains how ROM file offsets translate to the 24-bit SNES bus, memory bank layouts, and address constraints for strings and code in Secret of Evermore.
---

# SNES Memory Mapping & Evermore ROM Layout

Secret of Evermore uses a 24-bit SNES address space (banks `$00` through `$FF`, with offsets `$0000` through `$FFFF`). Understanding the exact relationship between byte offsets in a raw ROM file (e.g. in a hex editor) and CPU addresses on the SNES system bus is critical for authoring patches, allocating memory, and debugging crashes.

---

## 1. ROM Offset vs. SNES Bus Address

Secret of Evermore is mapped as a **HiROM (Mode 21)** game with extended banks:
- A clean vanilla ROM is **3 MB (24 Mbit)** in size (`0x000000..0x2FFFFF`).
- An expanded ROM (used by Everscript and modern romhacks) extends this to **4 MB (32 Mbit)** (`0x000000..0x3FFFFF`).

In HiROM mapping:
- ROM banks occupy the upper half of memory ($32\text{ KB}$ or full $64\text{ KB}$ depending on mirroring).
- FastROM mirror banks (`$80..$FF`) allow the 65c816 CPU to access memory at 3.58 MHz instead of 2.68 MHz.

```
ROM File Offset (Hex Editor)         SNES Bus Address (CPU View)
0x000000 - 0x037FFF   ────────►     $C00000 - $C37FFF (Slow ROM, Strings)
0x11D000 - 0x11F32D   ────────►     $91D000 - $91F32D (String Keys / Pointers)
0x128000 - 0x1BFFFF   ────────►     $928000 - $9BFFFF (Fast ROM, Vanilla Scripts)
0x300000 - 0x307FFF   ────────►     $B00000 - $B07FFF (Extended Strings)
0x308000 - 0x30FFFF   ────────►     $B08000 - $B0FFFF (Extended Script Code)
```

---

## 2. Dedicated Regions in Secret of Evermore

The Evermore engine has strict architectural constraints on where specific asset types can reside:

### 2.1 String Storage (`$C00000..$C37FFF` and `$B00000..$B07FFF`)
- Dialogue text and system strings are addressed through 24-bit pointers.
- Vanilla string data lives in banks `$C0`, `$C1`, `$C2`, `$C3` (offsets `$0000..$7FFF`).
- In an expanded ROM, extended strings are placed in bank `$B0` (`$0000..$7FFF`), corresponding to file offset `0x300000..0x307FFF`.
- Strings **cannot** be stored in the primary script banks without modifying the string decompression / rendering routines.

### 2.2 Script & Bytecode Storage (`$928000..$9BFFFF` and `$B08000..$B0FFFF`)
- Evermore's custom script interpreter executes bytecode directly from ROM.
- Vanilla room scripts occupy banks `$92` through `$9B` (offsets `$8000..$FFFF`), corresponding to file offsets `0x128000..0x1BFFFF`.
- In Everscript, additional custom code and functions are allocated into the extension region at file offset `0x308000..0x30FFFF` (`$B08000..$B0FFFF`).

### 2.3 String Key Table (`$91D000..$91F32D`)
- File offset `0x11D000..0x11F32D` contains an indexed table of 3-byte string pointers (indices `0x0000` to `0x232B`).
- Structure of each 3-byte entry:
  - 24-bit address pointing to the string location.
  - The Most Significant Bit (MSB `0x80`) indicates whether the string is compressed using Evermore's proprietary dictionary compression.

---

## 3. Bank Boundary Constraints ($64\text{ KB}$ Limits)

A major hardware constraint of the SNES 65c816 architecture is the **16-bit program counter (`PC`)**:
- When code or script executes, normal jumps and relative branches cannot cross a $64\text{ KB}$ boundary (`0x10000` boundary) without a long jump (`JML` / long call) that updates the Program Bank register (`PB`).
- In Everscript's linker (`compiler/linker.py`), the `MemoryManager` explicitly splits memory allocations by bank using `_split_by_bank()`:
  ```python
  first_bank = memory.start & 0xff0000
  last_bank = memory.end & 0xff0000
  ```
- **Rule:** Never attempt to compile a single continuous function or bytecode block that straddles a $64\text{ KB}$ boundary without bank-aware trampolines.

---

## 4. Quick Translation Formula

For an unheadered HiROM Evermore image:
1. **ROM File Offset $\to$ SNES Bus Address:**
   - For vanilla script banks: `Bus Address = 0x800000 + File Offset` (when offset $\ge$ `0x100000`).
   - For vanilla string banks: `Bus Address = 0xC00000 + File Offset`.
   - For extension script: `Bus Address = 0x800000 + File Offset` (File `0x308000` $\to$ `$B08000`).
2. **SNES Bus Address $\to$ ROM File Offset:**
   - If address begins with `$92..$9B` or `$B0`: `File Offset = Bus Address - 0x800000`.
   - If address begins with `$C0..$C3`: `File Offset = Bus Address - 0xC00000`.
