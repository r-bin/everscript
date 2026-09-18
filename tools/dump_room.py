#!/usr/bin/env python3
"""
Secret of Evermore Room Map Extractor
------------------------------------
Extracts room map header, dimensions, Layer 1 tile IDs, Layer 2 tile IDs,
collision attributes, and SNES VRAM tilemap words directly from the ROM
based on empirically verified 65c816 decompression logic.

Pipeline (all stages verified bit-for-bit against Mesen2 trace logs):
  Block 1: LZSS/copy ($8C988D) → delta accumulator ($908E85) → CHR tile palette
  Block 2: 2D Markov ($8C9BD0) → metatile grid ($7F0000)
  Block 3: LZSS ($8C988D) → 3-slice planar table ($7F0280):
           Slice 0 = Layer 1 VRAM words, Slice 1 = Layer 2 VRAM words,
           Slice 2 = collision/passability attributes

Block Discovery (§6.3 of map_decompression_trace_analysis.md):
  The compressed payload section contains a variable number of sub-blocks
  (tile uploads, palette loads, CHR decompressions, etc.) whose outer
  framing is not fully reverse-engineered.  The engine's higher-level
  dispatcher processes them sequentially, but the three blocks we need
  are identified by their dispatcher header signatures:
    Block 2: sub_flag == 0x07  AND  decomp_size == width*height*2
    Block 1: sub_flag in {0x00, 0x03}  occurring before Block 2
    Block 3: sub_flag == 0x03  AND  decomp_size % 6 == 0  after Block 2
  This signature scan is verified against all 127 vanilla rooms.
"""

import sys
import os
import argparse
import json

MAP_LIST_ADDR = 0x1FFDE7 # ROM file offset for SNES $9FFDE7 (HiROM)
MAX_ROOMS = 127          # SoETilesViewer MAX_MAPS
DEFAULT_ROM_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Secret of Evermore (U) [!].smc")

class LZSSDecompressor:
    """
    65c816 LZSS sliding-window decompressor routine at $8C98C9.
    Uses a 4096-byte circular window at WRAM $7FA000..$7FAFFF.
    Dispatch table index 3 (sub_flag=0x03).
    """
    def __init__(self, data: bytes, offset: int):
        self.data = data
        self.byte_ptr = offset
        self.bit_buf = 0
        self.bits_left = 0
        self.window = bytearray(0x1000) # 4KB history buffer
        self.win_ptr = 0
        self.output = bytearray()

    def get_bit(self) -> int:
        if self.bits_left == 0:
            if self.byte_ptr < len(self.data):
                self.bit_buf = self.data[self.byte_ptr]
                self.byte_ptr += 1
            else:
                self.bit_buf = 0
            self.bits_left = 8
        bit = (self.bit_buf >> 7) & 1
        self.bit_buf = (self.bit_buf << 1) & 0xFF
        self.bits_left -= 1
        return bit

    def get_bits(self, n: int) -> int:
        res = 0
        for _ in range(n):
            res = (res << 1) | self.get_bit()
        return res

    def decompress(self, target_size: int = None) -> bytearray:
        while True:
            if target_size is not None and len(self.output) >= target_size:
                break
            flag = self.get_bit()
            if flag == 1:
                # Literal byte
                b = self.get_bits(8)
                self.output.append(b)
                self.window[self.win_ptr] = b
                self.win_ptr = (self.win_ptr + 1) & 0xFFF
            else:
                # 16-bit LZ reference
                token = self.get_bits(16)
                offset = token >> 4
                if offset == 0:
                    # End-of-stream sentinel
                    break
                length = (token & 0x0F) + 2
                src = (offset - 1) & 0xFFF
                for _ in range(length):
                    b = self.window[src]
                    src = (src + 1) & 0xFFF
                    self.output.append(b)
                    self.window[self.win_ptr] = b
                    self.win_ptr = (self.win_ptr + 1) & 0xFFF
        return self.output

def snes2rom(snes_addr: int) -> int:
    """Translate SNES 24-bit FastROM/HiROM address to ROM file offset."""
    return snes_addr & 0x3FFFFF

def read24(rom: bytes, offset: int) -> int:
    return rom[offset] | (rom[offset+1] << 8) | (rom[offset+2] << 16)

def read16(rom: bytes, offset: int) -> int:
    return rom[offset] | (rom[offset+1] << 8)

def decompress_markov_grid(rom_bytes: bytes, stream_offset: int, width: int, height: int, base_metatile: int = 0x0280) -> list[int]:
    """
    2D Context-Predictive Markov Bitstream Decoder ($8C9BD0).
    Dispatch table index 7 (sub_flag=0x07).
    Decodes the 2D metatile layout grid directly into WRAM format.
    """
    grid = [0] * (width * height)
    stride = width * 2
    table = {tid: [tid, tid, tid, tid] for tid in range(base_metatile, base_metatile + 0x0800, 8)}
    ptr = stream_offset
    bit_offset = 0

    def peek_5bits():
        b0 = rom_bytes[ptr] if ptr < len(rom_bytes) else 0
        b1 = rom_bytes[ptr+1] if ptr+1 < len(rom_bytes) else 0
        b2 = rom_bytes[ptr+2] if ptr+2 < len(rom_bytes) else 0
        return (((b0 << 16) | (b1 << 8) | b2) >> (19 - bit_offset)) & 0x1F

    def advance(n):
        nonlocal ptr, bit_offset
        bit_offset += n
        ptr += (bit_offset >> 3)
        bit_offset &= 7

    def read_bits(n):
        nonlocal ptr, bit_offset
        b0 = rom_bytes[ptr] if ptr < len(rom_bytes) else 0
        b1 = rom_bytes[ptr+1] if ptr+1 < len(rom_bytes) else 0
        b2 = rom_bytes[ptr+2] if ptr+2 < len(rom_bytes) else 0
        res = (((b0 << 16) | (b1 << 8) | b2) >> (24 - bit_offset - n)) & ((1 << n) - 1)
        advance(n)
        return res

    next_seq_tile = base_metatile
    above_tile = base_metatile
    left_tile = base_metatile
    tile_bits, tile_mask, tile_counter = 0, 1, 0

    for idx in range(width * height):
        byte_y = idx * 2
        op = peek_5bits()
        if op >= 16:  # Opcode 16..31: 1-bit token (1) -> above[0]
            advance(1)
            val = table[above_tile][0]
        elif op >= 8:  # Opcode 8..15: 2-bit token (01) -> literal tile index
            advance(2)
            t_idx = read_bits(tile_bits)
            val = base_metatile + t_idx * 8
        elif op >= 6:  # Opcode 6..7: 4-bit token (0011) -> next sequential tile
            advance(4)
            val = next_seq_tile
            next_seq_tile += 8
            if val not in table:
                table[val] = [val, val, val, val]
            tile_counter += 1
            if (tile_counter & tile_mask) != 0:
                tile_mask <<= 1
                tile_bits += 1
        elif op == 5:  # Opcode 5: 5-bit token (00101) -> left[3]
            advance(5)
            val = table[left_tile][3]
        elif op == 4:  # Opcode 4: 5-bit token (00100) -> above[2]
            advance(5)
            val = table[above_tile][2]
        else:  # Opcode 0..3: 3-bit token (000) -> left[1]
            advance(3)
            val = table[left_tile][1]

        grid[idx] = val

        if val not in table:
            table[val] = [val, val, val, val]

        # Update context model ($8C9BF3)
        if byte_y >= stride:
            if val != table[above_tile][2]:
                table[above_tile][2] = table[above_tile][0]
            table[above_tile][0] = val

        if val != table[left_tile][3]:
            table[left_tile][3] = table[left_tile][1]
        table[left_tile][1] = val
        left_tile = val

        next_byte_y = byte_y + 2
        if next_byte_y >= stride:
            above_tile = grid[(next_byte_y - stride) // 2]

    return grid


def _scan_sub_block(rom, start, end, sub_flag_match, size_match=None):
    """Scan ROM for a dispatcher sub-block header matching the given criteria.

    Sub-block header layout (5 bytes, per $8C988D dispatcher):
        [payload_len:2][sub_flag:1][decomp_size:2]
    The compressed stream starts immediately after at offset +5.

    Args:
        rom:            ROM byte buffer.
        start:          ROM file offset to begin scanning.
        end:            ROM file offset upper bound (exclusive).
        sub_flag_match: Set of acceptable sub_flag values (e.g. {0x03} or {0x00, 0x03}).
        size_match:     If not None, a callable(decomp_size) -> bool for validation.

    Returns:
        Tuple (offset, payload_len, sub_flag, decomp_size) or None.
    """
    for p in range(start, min(end, len(rom) - 5)):
        sub = rom[p + 2]
        if sub not in sub_flag_match:
            continue
        sz = rom[p + 3] | (rom[p + 4] << 8)
        if size_match is not None and not size_match(sz):
            continue
        payload_len = rom[p] | (rom[p + 1] << 8)
        return p, payload_len, sub, sz
    return None


def dump_room(room_id: int, rom_path: str = DEFAULT_ROM_PATH) -> dict:
    if not os.path.exists(rom_path):
        raise FileNotFoundError(f"ROM file not found at: {rom_path}")

    with open(rom_path, 'rb') as f:
        rom = f.read()

    # 1. Resolve room blob pointer from Map Table ($9FFDE7 + room_id * 4)
    table_entry_offset = MAP_LIST_ADDR + (room_id * 4)
    snes_blob_ptr = read24(rom, table_entry_offset)
    blob_offset = snes2rom(snes_blob_ptr)

    # 2. Header (13 bytes, offsets $00..$0C)
    header_bytes = rom[blob_offset:blob_offset+13]
    trig_off_x   = header_bytes[0]
    trig_off_y   = header_bytes[1]
    width_tiles  = header_bytes[2]
    height_tiles = header_bytes[3]
    display_tm   = header_bytes[4]
    subscreen_ts = header_bytes[5]
    color_math   = header_bytes[6]
    color_window = header_bytes[7]
    effect_variant = header_bytes[8]

    # 3. Trigger tables (offset $0D)
    step_len = read16(rom, blob_offset + 0x0D)
    step_records = []
    step_ptr = blob_offset + 0x0F
    for i in range(step_len // 6):
        r = rom[step_ptr + i*6 : step_ptr + (i+1)*6]
        step_records.append({
            "y1": r[0], "x1": r[1], "y2": r[2], "x2": r[3],
            "script_id": r[4] | (r[5] << 8)
        })

    b_len_offset = blob_offset + 0x0F + step_len
    b_len = read16(rom, b_len_offset)
    b_records = []
    b_ptr = b_len_offset + 2
    for i in range(b_len // 6):
        r = rom[b_ptr + i*6 : b_ptr + (i+1)*6]
        b_records.append({
            "y1": r[0], "x1": r[1], "y2": r[2], "x2": r[3],
            "script_id": r[4] | (r[5] << 8)
        })

    # 4. Tile family list
    payload_offset = b_ptr + b_len
    tile_count = rom[payload_offset]
    tile_families = []
    for i in range(tile_count):
        tid = read16(rom, payload_offset + 1 + i*2)
        tile_families.append(tid)

    total_tiles = width_tiles * height_tiles

    # ---------------------------------------------------------------
    # 5. Locate and decompress the three payload blocks
    # ---------------------------------------------------------------
    # The compressed payload section at `pos` contains a variable number
    # of sub-blocks whose outer framing is not fully reverse-engineered.
    # We identify the three blocks we need by their $8C988D dispatcher
    # header signatures, scanning the ROM linearly.
    #
    # Sub-block header: [payload_len:2][sub_flag:1][decomp_size:2][data...]
    # The engine's dispatch table ($8C98A1) maps sub_flag to algorithm:
    #   0x00 → uncompressed copy ($8C98B1)
    #   0x03 → LZSS sliding-window ($8C98C9)
    #   0x07 → 2D Markov bitstream ($8C9B65)
    #
    # Verified against all 127 vanilla rooms.

    pos = payload_offset + 1 + tile_count * 2
    scan_limit = pos + 0x8000  # 32KB scan window (max observed gap: ~15KB)

    # --- Block 2: Markov → 2D metatile grid → WRAM $7F0000 ---
    # Found first because it has the most specific signature:
    # sub_flag == 0x07 AND decomp_size == width * height * 2
    target_grid_bytes = total_tiles * 2
    b2 = _scan_sub_block(rom, pos, scan_limit,
                         sub_flag_match={0x07},
                         size_match=lambda sz: sz == target_grid_bytes)
    if b2 is None:
        raise ValueError(
            f"Room 0x{room_id:02X}: Block 2 (Markov grid) not found — "
            f"no sub_flag=0x07 with decomp_size={target_grid_bytes} within scan window")
    b2_off, b2_payload_len, b2_sub, b2_decomp = b2

    base_metatile = target_grid_bytes
    raw_metatiles = decompress_markov_grid(rom, b2_off + 5, width_tiles, height_tiles, base_metatile)

    # --- Block 1: Tile palette deltas → WRAM $7FC300 ---
    # Deterministic layout: pos has count of 3-byte CHR tile descriptors.
    # Block 1 subheader starts immediately after: pos + 3 + num_extra * 3.
    # Subheader: [sub_flag:1][decomp_size:2][data...]
    num_extra = rom[pos]
    b1_off = pos + 3 + num_extra * 3
    b1_sub = rom[b1_off]
    b1_decomp = read16(rom, b1_off + 1)
    b1_data = b1_off + 3

    if b1_sub == 0x03:
        # LZSS decompression ($8C98C9)
        d1 = LZSSDecompressor(rom, b1_data)
        block1_out = d1.decompress()
    elif b1_sub == 0x00:
        # Uncompressed copy ($8C98B1)
        block1_out = bytearray(rom[b1_data : b1_data + b1_decomp])
    else:
        raise ValueError(
            f"Room 0x{room_id:02X}: Block 1 unsupported sub_flag 0x{b1_sub:02X} at 0x{b1_off:06X}")

    # Apply 16-bit delta accumulator ($908E85) in-place
    accum_words = []
    running_acc = 0
    for i in range(0, len(block1_out) & ~1, 2):
        delta = block1_out[i] | (block1_out[i+1] << 8)
        running_acc = (running_acc + delta) & 0xFFFF
        accum_words.append(running_acc)

    # --- Block 3: LZSS → 3-slice planar metatile table → WRAM $7F0280 ---
    # Follows Block 2 in ROM.  sub_flag == 0x03, decomp_size is a positive multiple of 6.
    b2_end = b2_off + 2 + b2_payload_len
    b3 = _scan_sub_block(rom, b2_end, b2_end + 0x8000,
                         sub_flag_match={0x03},
                         size_match=lambda sz: sz > 0 and sz % 6 == 0)
    if b3 is None:
        raise ValueError(
            f"Room 0x{room_id:02X}: Block 3 (metatile table) not found — "
            f"no sub_flag=0x03 with decomp_size%%6==0 after Block 2 end at 0x{b2_end:06X}")
    b3_off, b3_payload_len, b3_sub, b3_decomp = b3

    d3 = LZSSDecompressor(rom, b3_off + 5)
    b3_out = d3.decompress(b3_decomp)

    # Hardware division by 6 ($9091B0): N = decomp_bytes / 6
    metatile_count = b3_decomp // 6
    words = [b3_out[i] | (b3_out[i+1] << 8) for i in range(0, len(b3_out) & ~1, 2)]
    slice0 = words[:metatile_count]                         # Layer 1 VRAM words
    slice1 = words[metatile_count:metatile_count * 2]       # Layer 2 VRAM words
    slice2 = words[metatile_count * 2:metatile_count * 3]   # Collision attributes

    # ---------------------------------------------------------------
    # 6. Assemble layer grids from metatile IDs + VRAM word slices
    # ---------------------------------------------------------------
    layer1_grid = []
    layer1_vram_words = []
    layer1_vram_int_words = []
    layer2_grid = []
    layer2_vram_words = []
    layer2_vram_int_words = []
    collision_grid = []
    collision_int_words = []
    for r in range(height_tiles):
        row_meta = []
        row_vram1 = []
        row_vram1_ints = []
        row_vram2 = []
        row_vram2_ints = []
        row_coll = []
        row_coll_ints = []
        for c in range(width_tiles):
            idx = r * width_tiles + c
            meta_id = raw_metatiles[idx]
            m_idx = (meta_id - base_metatile) // 8
            row_meta.append(f"0x{meta_id:04X}")
            w1 = slice0[m_idx] if 0 <= m_idx < len(slice0) else 0
            w2 = slice1[m_idx] if 0 <= m_idx < len(slice1) else 0
            w3 = slice2[m_idx] if 0 <= m_idx < len(slice2) else 0
            row_vram1.append(f"0x{w1:04X}")
            row_vram1_ints.append(w1)
            row_vram2.append(f"0x{w2:04X}")
            row_vram2_ints.append(w2)
            row_coll.append(f"0x{w3:04X}")
            row_coll_ints.append(w3)
        layer1_grid.append(row_meta)
        layer1_vram_words.append(row_vram1)
        layer1_vram_int_words.append(row_vram1_ints)
        layer2_grid.append(row_vram2)
        layer2_vram_words.append(row_vram2)
        layer2_vram_int_words.append(row_vram2_ints)
        collision_grid.append(row_coll)
        collision_int_words.append(row_coll_ints)

    result = {
        "room_id": room_id,
        "room_id_hex": f"0x{room_id:02X}",
        "rom_pointer_snes": f"0x{snes_blob_ptr:06X}",
        "rom_pointer_file": f"0x{blob_offset:06X}",
        "header": {
            "origin_x": trig_off_x,
            "origin_y": trig_off_y,
            "width_tiles": width_tiles,
            "height_tiles": height_tiles,
            "width_pixels": width_tiles * 16,
            "height_pixels": height_tiles * 16,
            "display_tm": f"0x{display_tm:02X}",
            "subscreen_ts": f"0x{subscreen_ts:02X}",
            "color_math_cgadsub": f"0x{color_math:02X}",
            "color_window_cgwsel": f"0x{color_window:02X}",
            "effect_variant": f"0x{effect_variant:02X}",
            "raw_hex": header_bytes.hex()
        },
        "size": {
            "width_tiles": width_tiles,
            "height_tiles": height_tiles,
            "width_pixels": width_tiles * 16,
            "height_pixels": height_tiles * 16,
            "total_tiles": total_tiles
        },
        "triggers": {
            "step_on_count": len(step_records),
            "step_on": step_records,
            "b_trigger_count": len(b_records),
            "b_trigger": b_records
        },
        "tile_families": [f"0x{tid:04X}" for tid in tile_families],
        "tile_palette": [f"0x{w:04X}" for w in accum_words],
        "tile_palette_count": len(accum_words),
        "payload_blocks": {
            "block1": {"sub_flag": f"0x{b1_sub:02X}", "decomp_size": b1_decomp,
                       "rom_offset": f"0x{b1_off:06X}"},
            "block2": {"sub_flag": f"0x{b2_sub:02X}", "decomp_size": b2_decomp,
                       "rom_offset": f"0x{b2_off:06X}"},
            "block3": {"sub_flag": f"0x{b3_sub:02X}", "decomp_size": b3_decomp,
                       "rom_offset": f"0x{b3_off:06X}"},
        },
        "metatile_count": metatile_count,
        "base_metatile": f"0x{base_metatile:04X}",
        "layer1_metatile_ids": layer1_grid,
        "layer1_vram_words": layer1_vram_words,
        "layer1_vram_int_words": layer1_vram_int_words,
        "layer1_status": "DECODED",
        "layer2_tile_ids": layer2_grid,
        "layer2_vram_words": layer2_vram_words,
        "layer2_vram_int_words": layer2_vram_int_words,
        "layer2_status": "DECODED",
        "collision_words": collision_grid,
        "collision_int_words": collision_int_words,
    }

    return result

def get_room_vram_words(room_id: int, rom_path: str = DEFAULT_ROM_PATH, layer: int = 1) -> list[list[int]]:
    """Returns 2D grid of 16-bit SNES VRAM tilemap words."""
    res = dump_room(room_id, rom_path)
    if layer == 1:
        return res["layer1_vram_int_words"]
    elif layer == 2:
        return res["layer2_vram_int_words"]
    raise ValueError(f"Invalid layer {layer}, expected 1 or 2")

def get_room_vram_bytes(room_id: int, rom_path: str = DEFAULT_ROM_PATH, layer: int = 1, pad_to_32: bool = False) -> bytes:
    """
    Returns little-endian VRAM tilemap bytes.
    If pad_to_32 is True, pads each row to 32 words (64 bytes), matching SNES VRAM buffers.
    """
    words_grid = get_room_vram_words(room_id, rom_path, layer)
    out = bytearray()
    for row in words_grid:
        for w in row:
            out.append(w & 0xFF)
            out.append((w >> 8) & 0xFF)
        if pad_to_32 and len(row) < 32:
            out.extend(b'\x00' * ((32 - len(row)) * 2))
    return bytes(out)

def main():
    parser = argparse.ArgumentParser(description="Extract Secret of Evermore map details and tile IDs.")
    parser.add_argument("room", nargs='?', help="Room ID (hex e.g. 0x33, decimal e.g. 51 or 33)")
    parser.add_argument("--rom", default=DEFAULT_ROM_PATH, help="Path to Secret of Evermore ROM")
    parser.add_argument("--json", action="store_true", help="Output full result as JSON")
    parser.add_argument("--vram-bytes", action="store_true", help="Output only VRAM tilemap bytes in hex format (little-endian: C0 30 C2 30 ...)")
    parser.add_argument("--vram-words", action="store_true", help="Output only VRAM tilemap words (0x30C0 0x30C2 ...)")
    parser.add_argument("--layer", type=int, default=1, choices=[1, 2], help="Layer to output for VRAM data (default: 1)")
    parser.add_argument("--pad-32", action="store_true", help="Pad rows to 32 tiles (64 bytes) matching SNES VRAM tilemap buffer width")
    parser.add_argument("--all", action="store_true", help="Decode all rooms and report results")
    args = parser.parse_args()

    if args.all:
        ok = 0
        fail = 0
        for rid in range(MAX_ROOMS):
            try:
                res = dump_room(rid, args.rom)
                s = res['size']
                pb = res['payload_blocks']
                print(f"Room 0x{rid:02X}: {s['width_tiles']:3d}x{s['height_tiles']:<3d}  "
                      f"{res['metatile_count']:4d} metatiles  "
                      f"{res['tile_palette_count']:3d} CHR IDs  "
                      f"B1({pb['block1']['sub_flag']})@{pb['block1']['rom_offset']}  "
                      f"B2@{pb['block2']['rom_offset']}  "
                      f"B3@{pb['block3']['rom_offset']}")
                ok += 1
            except Exception as e:
                print(f"Room 0x{rid:02X}: FAILED - {e}")
                fail += 1
        print(f"\n{ok} passed, {fail} failed out of {MAX_ROOMS} rooms")
        return

    if not args.room:
        parser.error("room is required unless --all is specified")

    raw = args.room.strip()
    if raw.startswith("0x") or raw.startswith("0X"):
        room_id = int(raw, 16)
    elif any(c in "abcdefABCDEF" for c in raw):
        room_id = int(raw, 16)
    else:
        val = int(raw)
        room_id = val

    if args.vram_bytes:
        raw_bytes = get_room_vram_bytes(room_id, args.rom, layer=args.layer, pad_to_32=args.pad_32)
        words_grid = get_room_vram_words(room_id, args.rom, layer=args.layer)
        row_width = 32 if args.pad_32 else len(words_grid[0])
        row_bytes_len = row_width * 2
        for r_idx in range(0, len(raw_bytes), row_bytes_len):
            chunk = raw_bytes[r_idx:r_idx + row_bytes_len]
            for sub_i in range(0, len(chunk), 16):
                sub = chunk[sub_i:sub_i+16]
                print(" ".join(f"{b:02X}" for b in sub))
        return

    if args.vram_words:
        words_grid = get_room_vram_words(room_id, args.rom, layer=args.layer)
        for r_idx, row in enumerate(words_grid):
            pad = [0] * (32 - len(row)) if args.pad_32 else []
            print(f"Row {r_idx:02d}: " + " ".join(f"0x{w:04X}" for w in (row + pad)))
        return

    res = dump_room(room_id, args.rom)

    if args.json:
        clean_res = dict(res)
        for key in ("layer1_vram_int_words", "layer2_vram_int_words", "collision_int_words"):
            clean_res.pop(key, None)
        print(json.dumps(clean_res, indent=2))
        return

    print("=" * 80)
    print(f"ROOM {res['room_id_hex']} ({res['room_id']}) - MAP DATA DUMP")
    print("=" * 80)
    print(f"ROM Address:     {res['rom_pointer_snes']} (File Offset: {res['rom_pointer_file']})")
    h = res['header']
    print(f"Dimensions:      {h['width_tiles']} x {h['height_tiles']} tiles ({h['width_pixels']} x {h['height_pixels']} px)")
    print(f"Origin Offset:   ({h['origin_x']}, {h['origin_y']})")
    print(f"Display Config:  TM={h['display_tm']} TS={h['subscreen_ts']} CGADSUB={h['color_math_cgadsub']} CGWSEL={h['color_window_cgwsel']}")
    print(f"Tile Families:   {', '.join(res['tile_families'])}")
    print(f"Triggers:        Step-on: {res['triggers']['step_on_count']}, B-Trigger: {res['triggers']['b_trigger_count']}")

    pb = res['payload_blocks']
    print(f"\nPayload Blocks:")
    print(f"  Block 1 (Palette):  sub={pb['block1']['sub_flag']} decomp={pb['block1']['decomp_size']} @ {pb['block1']['rom_offset']}")
    print(f"  Block 2 (Markov):   sub={pb['block2']['sub_flag']} decomp={pb['block2']['decomp_size']} @ {pb['block2']['rom_offset']}")
    print(f"  Block 3 (Table):    sub={pb['block3']['sub_flag']} decomp={pb['block3']['decomp_size']} @ {pb['block3']['rom_offset']}")
    print(f"  Metatiles: {res['metatile_count']}  base_metatile: {res['base_metatile']}")

    print("\n" + "=" * 80)
    print(f"TILE PALETTE ({res['tile_palette_count']} unique metatile CHR IDs, delta-accumulated from Block 1):")
    print("=" * 80)
    palette = res['tile_palette']
    for i in range(0, len(palette), 10):
        chunk = palette[i:i+10]
        line = " ".join(chunk)
        print(f"  [{i:3d}..{min(i+9, len(palette)-1):3d}] {line}")

    print("\n" + "=" * 80)
    print(f"LAYER 1 METATILE GRID ({h['width_tiles']} x {h['height_tiles']} WRAM $7F0000 Metatile Offsets):")
    print("=" * 80)
    for r_idx, row in enumerate(res['layer1_metatile_ids']):
        print(f"Row {r_idx:02d}: " + " ".join(row))

    print("\n" + "=" * 80)
    print(f"LAYER 1 VRAM TILEMAP WORDS ({h['width_tiles']} x {h['height_tiles']} SNES VRAM Tilemap Entries):")
    print("=" * 80)
    for r_idx, row in enumerate(res['layer1_vram_words']):
        print(f"Row {r_idx:02d}: " + " ".join(row))

    print("\n" + "=" * 80)
    print(f"LAYER 2 VRAM TILEMAP WORDS ({h['width_tiles']} x {h['height_tiles']}):")
    print("=" * 80)
    for r_idx, row in enumerate(res['layer2_vram_words']):
        print(f"Row {r_idx:02d}: " + " ".join(row))

if __name__ == "__main__":
    main()
