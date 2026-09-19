---
name: ips-patch-format
description: Explains the binary IPS patch specification (headers, records, RLE compression, EOF) and how patch utilities apply and generate ROM diffs.
---

# The Binary IPS Patch Format

The **International Production System (IPS)** format is the standard format used in classic video game ROM hacking to distribute modifications without distributing copyrighted ROM data.

---

## 1. Binary Specification

An IPS file is a sequence of binary records bounded by a 5-byte header and a 3-byte trailer:

```
[5 Bytes: "PATCH"]
  ├── Record 1
  ├── Record 2
  ├── Record N (RLE or Standard)
  └── ...
[3 Bytes: "EOF"]
```

### 1.1 Header & Trailer
- **Header:** Exact ASCII string `PATCH` (`0x50 0x41 0x54 0x43 0x48`).
- **Trailer:** Exact ASCII string `EOF` (`0x45 0x4F 0x46`).

### 1.2 Standard Patch Record (5 Bytes + Data)
```
Offset (3 Bytes, Big-Endian) | Size (2 Bytes, Big-Endian) | Data Payload (Size Bytes)
```
- **Offset:** 24-bit integer specifying the exact target file offset where bytes will be written.
- **Size:** 16-bit integer ($1..65535$) specifying the number of payload bytes that follow.
- **Data:** Raw bytes to write directly to the target ROM.

### 1.3 Run-Length Encoded (RLE) Record (8 Bytes Total)
When a large block of repeating bytes needs to be written (e.g. zeroing out memory), IPS uses an RLE record:
```
Offset (3 Bytes) | Size = 0x0000 (2 Bytes) | RLE Count (2 Bytes) | Value (1 Byte)
```
- If the **Size** field is `0x0000`, the record is an RLE record.
- **RLE Count:** Number of times the single byte should be repeated.
- **Value:** The 1-byte value to repeat.

---

## 2. Limitations of the IPS Format

1. **16 MB Maximum Offset:** Because offsets are 24-bit, IPS cannot address offsets at or beyond $16\text{ MB}$ (`0x1000000`). This is sufficient for SNES (max $4\text{ MB}$ or $6\text{ MB}$).
2. **The "EOF" Collision Trap:** If a record coincidentally begins at offset `0x454F46` (the ASCII values for `E`, `O`, `F`), an IPS parser will mistakenly interpret the record offset as the end of the file. Compliant patch creators split such records into adjacent offsets to avoid this collision.

---

## 3. How IPS Utilities Function in Everscript

In this project, IPS handling is managed by:
- [utils/file_utils.py](file:///Users/v/Documents/GitHub/everscript/utils/file_utils.py): Converts `out/patch.clean.txt` to `out/everscript.ips` using `dump_txt_to_ips()`.
- [utils/ips_utils.py](file:///Users/v/Documents/GitHub/everscript/utils/ips_utils.py): Uses the `ips_util` library to create binary diffs and apply patches:
  ```python
  # Apply a patch to a target ROM
  ips_utils.apply_patch("Secret of Evermore (U) [!].smc", "out/everscript.ips")
  
  # Create a patch by comparing modified ROM to vanilla ROM
  ips_utils.create_rom_diff("vanilla.smc", "modified.smc", "output.ips")
  ```
- [ips2asar.py](file:///Users/v/Documents/GitHub/everscript/ips2asar.py): Reads IPS binary records and translates them into human-readable 65c816 assembly files for inspection.
