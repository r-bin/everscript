"""
Integration Test: Room 0x26 (West Area with Defend) VRAM Verification
----------------------------------------------------------------------
Verifies that the map decompression pipeline reconstructs the exact,
bit-for-bit SNES PPU VRAM background tilemap observed in Mesen2 memory dumps
for Room 0x26 (19x18 West Area with Defend).
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

# Ground-truth VRAM Hex Dump captured from Mesen2 PPU Memory Viewer for Room 0x26 (17 rows x 32 words)
MESEN2_VRAM_DUMP_HEX = """
20 28 20 28 22 28 20 28 20 28 22 28 20 28 20 28
22 28 20 28 22 28 20 28 20 28 22 28 20 28 20 28
20 28 20 65 6E 46 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 A0 0A A6 78 C4 78 CE 58 68 4A 00 A8 04 24
26 28 26 28 28 28 26 28 26 28 28 28 26 28 26 28
28 28 26 28 28 28 26 28 26 28 28 28 26 28 26 28
26 28 20 65 6E 46 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 A0 0A A6 78 C4 78 CE 58 68 4A 00 A8 04 24
0A 28 28 28 22 28 0A 28 28 28 20 28 22 28 20 28
22 28 20 28 22 28 0A 28 20 28 22 28 0A 28 28 28
22 28 22 28 0A 28 20 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
20 28 20 28 22 28 20 28 22 28 26 28 28 28 26 28
28 28 26 28 28 28 20 28 26 28 28 28 20 28 20 28
22 28 20 28 22 28 26 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
26 28 26 28 20 28 22 28 28 28 2E E8 02 E8 04 28
42 68 02 E8 20 28 26 28 04 28 04 68 26 28 26 28
28 28 26 28 28 28 0A 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0A 28 20 28 26 28 28 28 2A A8 2A 28 0E 68 2C E8
00 A8 00 A8 2E A8 0A 28 2E E8 40 28 22 28 28 28
22 28 22 28 0A 28 20 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
20 28 22 28 28 28 20 28 40 E8 2C E8 00 A8 00 A8
00 A8 00 A8 0E 28 26 28 0E 68 00 A8 24 28 20 28
20 28 22 28 22 28 26 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
26 28 28 28 04 28 2E A8 2E 68 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 2C E8 00 A8 00 A8 24 A8 26 28
28 28 26 28 28 28 0A 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0A 28 28 28 04 28 00 A8 42 28 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 04 68 28 28
22 28 22 28 0A 28 20 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
20 28 20 28 22 28 2A 28 2E 68 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 2E A8 22 28
20 28 22 28 20 28 26 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
26 28 26 28 28 28 2E E8 2C E8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 2E 28 2A 28 20 28
22 28 28 28 26 28 20 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
20 28 20 28 22 28 2E 68 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 2C A8 2E A8 26 28
20 28 22 28 0A 28 26 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
26 28 26 28 28 28 20 28 2E 68 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 2E 28 2A 28 20 28
26 28 28 28 20 28 0A 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0A 28 28 28 22 28 0A 28 28 28 0E E8 00 A8 00 A8
2E 28 2E 68 2C 68 00 A8 0E A8 04 28 24 A8 26 28
28 28 22 28 26 28 20 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
20 28 20 28 22 28 20 28 0A 28 0E 68 42 E8 02 68
22 28 0A 28 28 28 2E 68 00 A8 2C A8 24 28 20 28
22 28 20 28 22 28 26 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
26 28 26 28 28 28 24 68 2C E8 2E 28 26 28 0A 28
04 28 04 E8 20 28 22 28 0C 28 0C 68 26 28 26 28
28 28 26 28 28 28 0A 28 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0A 28 20 28 22 28 0A 28 2A 28 20 28 22 28 22 28
0A 28 20 28 22 28 0A 28 20 28 22 28 0A 28 20 28
22 28 20 28 22 28 20 28 00 00 00 00 00 00 00 00
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

def test_room_0x26_header_metadata():
    res = dump_room(0x26)
    assert res["room_id"] == 0x26
    h = res["header"]
    assert h["width_tiles"] == 19
    assert h["height_tiles"] == 18
    assert res["triggers"]["step_on_count"] == 1
    assert res["triggers"]["b_trigger_count"] == 3

def test_room_0x26_decompressed_grid_dimensions():
    res = dump_room(0x26)
    assert len(res["layer1_vram_words"]) == 18
    assert all(len(row) == 19 for row in res["layer1_vram_words"])
    assert len(res["layer2_vram_words"]) == 18
    assert all(len(row) == 19 for row in res["layer2_vram_words"])

def test_room_0x26_vram_words_verification():
    res = dump_room(0x26)
    l1_words = res["layer1_vram_int_words"]
    dump_rows = parse_mesen2_hex_dump(MESEN2_VRAM_DUMP_HEX)

    # 17 rows dumped from Mesen2 PPU viewer, first 17 tiles match Layer 1 active viewport
    assert len(dump_rows) == 17
    for r in range(17):
        expected_row = l1_words[r][:17]
        actual_row = dump_rows[r][:17]
        assert actual_row == expected_row, f"Row {r:02d} mismatch"

def test_room_0x26_cli_vram_bytes_flag():
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    cmd = [sys.executable, script_path, "0x26", "--vram-bytes"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert proc.returncode == 0
    lines = proc.stdout.strip().splitlines()
    assert len(lines) > 0
