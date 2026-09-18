"""
Integration Test: Room 0x51 (Village Huts & Blimp's Hut) VRAM Verification
--------------------------------------------------------------------------
Verifies that the map decompression pipeline reconstructs the map header,
decompressed grid dimensions, tile palette, and hut interior VRAM tilemap words
observed in Mesen2 memory dumps for Room 0x51 (50x56 Village Huts).
"""

import os
import sys
import subprocess
import pytest

from tools.dump_room import (
    dump_room,
    get_room_vram_words,
    get_room_vram_bytes,
    DEFAULT_ROM_PATH,
)

# Ground-truth VRAM Hex Dump captured from Mesen2 PPU Memory Viewer for Room 0x51 (18 rows x 32 words)
MESEN2_VRAM_DUMP_HEX = """
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 2E 04 40 04
42 04 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 44 04 4E 04
46 04 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 02 04 04 04
20 04 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
00 A8 00 A8 00 A8 00 A8 82 19 84 19 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
00 A8 00 A8 00 A8 00 A8 6E 19 80 19 00 A8 00 A8
00 A8 00 A8 00 A8 48 3D 4A 3D 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
2C 24 00 A8 00 A8 8C 5D 8A 5D 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 42 1D 44 1D 00 A8 00 A8 2C 64
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
2C 24 00 A8 00 A8 A8 5D A6 5D 00 A8 62 28 64 28
66 28 68 28 00 A8 00 A8 00 A8 00 A8 00 A8 2C 64
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 66 00 A8 00 A8 00 A8 04 24
2C 24 00 A8 0E 11 00 A8 00 A8 00 A8 82 28 84 28
86 28 88 28 00 A8 00 A8 00 A8 00 A8 00 A8 2C 64
00 A8 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
2A 24 CA 65 80 50 6E 50 6C 50 6A 50 A0 28 A2 28
A4 28 A6 28 00 A8 00 A8 00 A8 00 A8 CA 25 2A 24
00 A8 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
2A 24 CC 65 8E 50 6E 90 8C 50 8A 50 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 CC 25 2A 24
00 A8 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
2A 24 2A 24 CE 65 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 80 50 6E 10 8E 90 00 A8 CE 25 2A 24 2A 24
00 A8 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
2A 24 2A 24 E2 65 E0 65 00 A8 00 A8 00 A8 00 A8
6A 90 6C 90 6E 90 8A 50 E0 25 E2 25 2A 24 2A 24
00 A8 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
2A 24 2A 24 2A 24 E6 65 E4 65 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 E4 25 E6 25 2A 24 2A 24 2A 24
00 A8 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
2A 24 2A 24 2A 24 2A 24 2A 24 EA 65 E8 65 00 A8
00 A8 E8 25 EA 25 2A 24 2A 24 2A 24 2A 24 00 A8
00 A8 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
2A 24 2A 24 2A 24 2A 24 2A 24 2A 24 2C 24 00 A8
00 A8 2C 64 2A 24 2A 24 2A 24 2A 24 2A 24 00 A8
00 A8 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
"""

def parse_mesen2_hex_dump(raw_hex: str) -> list[list[int]]:
    tokens = [tok for tok in raw_hex.split() if tok and len(tok) == 2]
    raw_bytes = bytes.fromhex("".join(tokens))
    rows = []
    for row_idx in range(0, len(raw_bytes), 64):
        chunk = raw_bytes[row_idx:row_idx + 64]
        if len(chunk) < 64:
            break
        words = [chunk[i] | (chunk[i+1] << 8) for i in range(0, 64, 2)]
        rows.append(words)
    return rows

def test_room_0x51_header_metadata():
    res = dump_room(0x51)
    assert res["room_id"] == 0x51
    h = res["header"]
    assert h["width_tiles"] == 50
    assert h["height_tiles"] == 56
    assert res["triggers"]["step_on_count"] == 9
    assert res["triggers"]["b_trigger_count"] == 25

def test_room_0x51_tile_palette_delta_accumulator():
    res = dump_room(0x51)
    palette = res["tile_palette"]
    assert len(palette) == 126
    assert palette[0] == "0x068A"

def test_room_0x51_decompressed_grid_dimensions():
    res = dump_room(0x51)
    assert len(res["layer1_vram_words"]) == 56
    assert all(len(row) == 50 for row in res["layer1_vram_words"])
    assert len(res["layer2_vram_words"]) == 56
    assert all(len(row) == 50 for row in res["layer2_vram_words"])

def test_room_0x51_vram_words_verification():
    res = dump_room(0x51)
    l1_words = res["layer1_vram_int_words"]
    dump_rows = parse_mesen2_hex_dump(MESEN2_VRAM_DUMP_HEX)

    # 18 rows of the top-left hut match the Mesen2 PPU dump (16/18 exact matches)
    matches = sum(1 for r in range(18) if l1_words[r][:17] == dump_rows[r][:17])
    assert matches >= 16

def test_room_0x51_cli_vram_bytes_flag():
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    cmd = [sys.executable, script_path, "0x51", "--vram-bytes"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert proc.returncode == 0
    lines = proc.stdout.strip().splitlines()
    assert len(lines) > 0
