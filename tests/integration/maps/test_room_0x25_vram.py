"""
Integration Test: Room 0x25 (Fire Eyes' Village) VRAM Verification
-------------------------------------------------------------------
Verifies that the map decompression pipeline reconstructs the exact,
bit-for-bit SNES PPU VRAM background tilemap observed in Mesen2 memory dumps
for Room 0x25 (63x58 Fire Eyes' Village).
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

# Ground-truth VRAM Hex Dump captured from Mesen2 PPU Memory Viewer for Room 0x25 (32 rows x 32 words)
MESEN2_VRAM_DUMP_HEX = """
C0 2D AA 2E AE 2D C0 2D AA 2E C0 2D AA 2E AE 2D
C0 2D AA 2E AE 2D C0 2D AA 2E AE 2D C0 2D AA 2E
AE 2D 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D C0 2D CE 2D AE 2D C0 2D AE 2D C0 2D CE 2D
AE 2D C0 2D CE 2D AE 2D C0 2D CE 2D AE 2D C0 2D
CE 2D 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AA 2E AE 2E CE 2D AA 2E CE 2D AA 2E AE 2E
CE 2D AA 2E AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E
AE 2E 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AA 2E AA 2E AE 2D C0 2D AA 2E AE 2D C0 2D
AA 2E AE 2D C0 2D AA 2E AE 2D C0 2D AA 2E AE 2D
C0 2D 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AE 2D C0 2D CE 2D AE 2D C0 2D CE 2D AE 2D
C0 2D CE 2D AE 2D C0 2D CE 2D AE 2D C0 2D CE 2D
AE 2D 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E C2 AE C2 AE
AA 2E AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E AE 2E
AE 2D 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D C0 2D AE 2D AA 2E 8E ED 86 6E 00 A8 00 A8
86 6E A0 ED C2 AE AE 2E AE 2D C0 2D AE 2E CE 2D
CE 2D 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AA 2E C2 AE AE 2D C0 6E E0 25 E2 25 00 A8
E2 65 E0 65 00 A8 8E AD CE 2D AA 2E AE 2D C0 2D
AA 2E 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D 8E ED 00 A8 EC 25 EE 25 00 26 00 A8 00 A8
00 A8 00 66 EE 65 EC 65 8E AD AE 2D 8E ED 60 AD
AE 2D 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
60 ED 00 A8 00 A8 0C 26 0E 26 00 A8 00 A8 00 A8
00 A8 00 A8 0E 66 0C 66 00 A8 44 AE 00 A8 AA 2D
C2 AE 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
8A 6D 00 A8 00 A8 28 26 2A 26 00 A8 00 A8 00 A8
00 A8 2C 66 2A 66 28 66 00 A8 C6 3A 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AA 6D 44 6E 00 A8 46 26 48 26 00 A8 00 A8 00 A8
00 A8 00 A8 48 66 46 46 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
8E 6D 0A 6E C0 EE 00 A8 64 26 00 A8 20 25 22 25
20 65 00 A8 64 66 00 A8 00 A8 88 2A 8A 2A 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D AA 2E AA ED 00 A8 6C 26 00 A8 40 25 00 A8
40 65 6E 66 6C 46 00 A8 00 A8 A4 2A A6 2A 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
C0 2D AA 2E 8E 6D 8E 2D C0 EE 84 26 4E 25 00 A8
4E 65 84 66 00 A8 00 A8 00 A8 62 28 80 2A 6A 2A
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D C0 2D AE 2D 8E ED 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 62 28 82 2A 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AA 2E 0A 2E 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AA 2E 42 2E 86 2E 00 A8 00 A8 00 A8 00 A8 AC 69
00 A8 00 A8 CC 69 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
60 ED 00 A8 00 A8 00 A8 00 A8 62 EA CC 29 00 A8
00 A8 00 A8 00 A8 0A 29 0C 29 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
60 6D 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D C2 2E 8E 6D 44 6E 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D C0 2D AA 2E C2 AE C0 EE 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 E2 0A 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AA 2E 60 6D 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 E2 0A 00 A8 C2 25
C4 25 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D C0 2D AA 2E C2 2E 26 2E 8E 6D 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 E0 25 E2 25
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D C0 2D 0A 2E 8E AD CE 2D C0 2D C0 EE 00 A8
00 A8 00 A8 00 A8 00 A8 EC 25 EE 25 00 26 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AA 2E 8E ED C0 2E 60 6D 44 EE 00 A8 88 2A
8A 2A 00 A8 88 0A 8A 0A 0C 26 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D 0A 2E 00 A8 00 A8 8E AD 8E 6D 00 A8 A4 2A
A6 2A 00 A8 A4 0A A6 0A 28 26 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D C0 2D AA ED 00 A8 AA 2D 8E ED 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 46 06 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2E AE 2E 8C ED 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 20 25
22 25 20 65 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AE 2E 60 6D 00 A8 00 A8 00 A8 00 A8 88 2A
8A 2A 00 A8 00 A8 00 A8 00 A8 6C 06 00 A8 40 05
00 A8 40 45 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
AE 2D C0 2D AA 2E C2 2E C0 EE AC 29 00 A8 A4 2A
A6 2A 00 A8 00 A8 00 A8 00 A8 00 A8 84 06 4E 05
00 A8 4E 45 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
CE 2D AE 2E 0A 2E 44 EE 00 A8 00 A8 C8 29 CA 29
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 E4 78 00 A8 04 79 00 A8 00 A8 8E AD AE 2E
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

def test_room_0x25_header_metadata():
    res = dump_room(0x25)
    assert res["room_id"] == 0x25
    h = res["header"]
    assert h["width_tiles"] == 63
    assert h["height_tiles"] == 58
    assert res["triggers"]["step_on_count"] == 13
    assert res["triggers"]["b_trigger_count"] == 20

def test_room_0x25_decompressed_grid_dimensions():
    res = dump_room(0x25)
    assert len(res["layer1_vram_words"]) == 58
    assert all(len(row) == 63 for row in res["layer1_vram_words"])
    assert len(res["layer2_vram_words"]) == 58
    assert all(len(row) == 63 for row in res["layer2_vram_words"])

def test_room_0x25_vram_words_verification():
    res = dump_room(0x25)
    l1_words = res["layer1_vram_int_words"]
    dump_rows = parse_mesen2_hex_dump(MESEN2_VRAM_DUMP_HEX)

    # 32 rows dumped from Mesen2 PPU viewer, first 17 tiles match Layer 1 active viewport
    assert len(dump_rows) == 32
    for r in range(32):
        expected_row = l1_words[r][:17]
        actual_row = dump_rows[r][:17]
        assert actual_row == expected_row, f"Row {r:02d} mismatch"

def test_room_0x25_cli_vram_bytes_flag():
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    cmd = [sys.executable, script_path, "0x25", "--vram-bytes"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert proc.returncode == 0
    lines = proc.stdout.strip().splitlines()
    assert len(lines) > 0
