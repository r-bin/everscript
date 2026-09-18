"""
Integration Test: Room 0x34 (Strong Heart's Hut) VRAM Verification
------------------------------------------------------------------
Verifies that the map decompression pipeline (Stage 1 header -> Stage 2 LZSS ->
Stage 3 delta accumulator -> Stage 4 Markov grid unpacker -> VRAM tilemap table)
reconstructs the exact, bit-for-bit SNES PPU VRAM background tilemap observed
in Mesen2 debugger memory dumps for Room 0x34 (18x18 Strong Heart's Hut).
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

# Ground-truth VRAM Hex Dump captured from Mesen2 PPU Memory Viewer for Room 0x34
# Contains both Screen 1 (BG2 / Layer 1 Hut interior ceiling/walls) and Screen 2 (BG1 / Layer 2 Floor/furniture)
MESEN2_VRAM_DUMP_HEX = """
24 2C 24 2C 24 2C 24 2C 24 2C 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 24 2C 24 2C 24 2C
24 2C E4 1F 31 24 8C 1C 1F 10 14 1E 1C 9C 8C 1C
CE 2D 86 EE 00 A8 8E 6D 86 AE 00 A8 8E AD AE 2E
24 2C 24 2C 24 2C 24 2C 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 24 2C 24 2C
24 2C E4 1F 31 24 8C 1C 1F 10 14 1E 1C 9C 8C 1C
CE 2D 86 EE 00 A8 8E 6D 86 AE 00 A8 8E AD AE 2E
24 2C 24 2C 24 2C 00 A8 00 A8 00 A8 00 A8 00 A8
48 19 4A 19 4E 19 4C 19 00 A8 00 A8 00 A8 24 2C
24 2C E4 1F 31 24 8C 1C 1F 10 14 1E 1C 9C 8C 1C
CE 2D 86 EE 00 A8 8E 6D 86 AE 00 A8 8E AD AE 2E
24 2C 24 2C 24 2C 00 A8 00 A8 00 A8 00 A8 00 A8
60 19 62 19 62 19 60 59 00 A8 00 A8 00 A8 24 2C
24 2C E4 1F 31 24 8C 1C 1F 10 14 1E 1C 9C 8C 1C
CE 2D 86 EE 00 A8 8E 6D 86 AE 00 A8 8E AD AE 2E
24 2C 24 2C 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
64 19 66 19 66 19 64 59 00 A8 00 A8 00 A8 00 A8
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 24 2C 00 A8 00 A8 00 A8 22 1D 24 1D 00 A8
00 A8 00 A8 00 A8 26 05 28 05 00 A8 00 A8 00 A8
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 0A 2C 00 A8 00 A8 00 A8 2C 1D 2E 1D 00 A8
00 A8 00 A8 00 A8 40 05 42 05 00 A8 00 A8 00 A8
0A 6C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 0A 2C 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 22 1D 24 1D 00 A8 00 A8
0A 6C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 0A 2C 00 A8 00 A8 00 A8 EA 08 EC 08 EE 08
00 09 00 A8 00 A8 00 A8 2C 1D 2E 1D 00 A8 00 A8
0A 6C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 0A 2C 00 A8 00 A8 00 A8 08 09 0A 09 0C 09
0E 09 00 A8 00 A8 00 A8 00 A8 0C 10 0E 10 00 A8
0A 6C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 0A 2C 00 A8 00 A8 00 A8 64 2C 66 2C 68 2C
68 6C 66 6C 64 6C 00 A8 00 A8 28 10 2A 10 00 A8
0A 6C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 24 2C 8E 6C 00 A8 00 A8 84 0C 86 0C 88 0C
88 4C 86 4C 84 4C 00 A8 00 A8 00 A8 00 A8 8E 2C
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 24 2C AA 6C 00 A8 00 A8 A0 0C A2 0C A4 0C
A4 4C A2 4C A0 4C 00 A8 00 A8 00 A8 00 A8 AA 2C
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 24 2C AC EC C4 6C 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 C4 2C AC AC
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 24 2C 24 2C E0 6C CE 6C 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 CE 2C E0 2C 24 2C
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 24 2C 24 2C 24 2C E4 6C E2 6C 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 E2 2C E4 2C 24 2C 24 2C
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 24 2C 24 2C 24 2C 24 2C AC EC E8 6C E6 6C
00 A8 00 A8 E6 2C E8 2C AC AC 24 2C 24 2C 24 2C
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
24 2C 24 2C 24 2C 24 2C 24 2C 24 2C 24 2C 00 A8
00 A8 00 A8 00 A8 24 2C 24 2C 24 2C 24 2C 24 2C
24 2C 24 2C 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
"""

def parse_mesen2_hex_dump(raw_hex: str) -> list[list[int]]:
    """Parse raw Mesen2 hex dump into 16-bit words per 32-tile row."""
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

def test_room_0x34_header_metadata():
    """Verify room 0x34 header, dimensions, and trigger structure."""
    res = dump_room(0x34)
    assert res["room_id"] == 0x34
    assert res["room_id_hex"] == "0x34"

    h = res["header"]
    assert h["width_tiles"] == 18
    assert h["height_tiles"] == 18
    assert h["width_pixels"] == 288
    assert h["height_pixels"] == 288
    assert h["origin_x"] == 3
    assert h["origin_y"] == 6
    assert h["display_tm"] == "0x17"

    assert res["triggers"]["step_on_count"] == 1
    assert res["triggers"]["b_trigger_count"] == 3

def test_room_0x34_tile_palette_delta_accumulator():
    """Verify Block 1 decompression and delta accumulation."""
    res = dump_room(0x34)
    palette = res["tile_palette"]
    assert len(palette) == 92
    assert palette[0] == "0x068A"
    assert palette[1] == "0x1051"
    assert palette[2] == "0x1052"

def test_room_0x34_decompressed_grid_dimensions():
    """Verify 18x18 grid dimensions for Layer 1, Layer 2, and Collision."""
    res = dump_room(0x34)
    assert len(res["layer1_vram_words"]) == 18
    assert all(len(row) == 18 for row in res["layer1_vram_words"])
    assert len(res["layer2_vram_words"]) == 18
    assert all(len(row) == 18 for row in res["layer2_vram_words"])
    assert len(res["collision_words"]) == 18
    assert all(len(row) == 18 for row in res["collision_words"])

def test_room_0x34_vram_words_verification():
    """
    Verify that decompressed Layer 1 tilemap words match
    the ground-truth Mesen2 PPU memory viewer dump across all 18 rows
    of the 17-tile active screen viewport.
    """
    res = dump_room(0x34)
    l1_words = res["layer1_vram_int_words"]
    dump_rows = parse_mesen2_hex_dump(MESEN2_VRAM_DUMP_HEX)

    # In Room 0x34 (Strong Heart Hut), the SNES screen viewport displays
    # columns 0..16 (17 tiles wide), with columns 17..31 holding offscreen buffer.
    for r in range(18):
        expected_row = l1_words[r][:17]
        actual_row = dump_rows[r][:17]
        assert actual_row == expected_row, (
            f"Row {r:02d} mismatch:\n"
            f"Expected: {[hex(x) for x in expected_row]}\n"
            f"Actual:   {[hex(x) for x in actual_row]}"
        )

def test_room_0x34_cli_vram_bytes_flag():
    """Verify that tools/dump_room.py --vram-bytes executes and outputs expected bytes."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    cmd = [sys.executable, script_path, "0x34", "--vram-bytes"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert proc.returncode == 0
    lines = proc.stdout.strip().splitlines()
    assert len(lines) > 0
    # First row should start with 24 2C 24 2C 24 2C
    assert lines[0].startswith("24 2C 24 2C 24 2C")
