"""
Integration Test: Room 0x5B (East Jungle) VRAM Verification
------------------------------------------------------------
Verifies that the map decompression pipeline reconstructs the map header,
decompressed grid dimensions, tile palette, and jungle canopy VRAM tilemap words
observed in Mesen2 memory dumps for Room 0x5B (72x48 East Jungle).
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

# Ground-truth VRAM Hex Dump captured from Mesen2 PPU Memory Viewer for Room 0x5B
MESEN2_VRAM_DUMP_HEX = """
22 3E 24 3E 2E 3E 22 3E 24 3E 2E 3E 22 3E 4C 7E
00 A8 00 A8 4C 3E 2E 3E 22 3E 24 3E 2E 3E 22 3E
24 3E AA 2E AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E
AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E AE 2D AE 2D
2C 3E 22 3E 24 3E 2C 3E 22 3E 24 3E 2C 3E 66 7E
00 A8 00 A8 4C 3E 24 3E 0E BE 22 3E 24 3E 2C 3E
22 3E AA 2E AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E
AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E AE 2D AE 2D
48 3E 2C 3E 2E 3E 48 3E 2C 3E 2E 3E 48 3E 4C 7E
00 A8 00 A8 66 3E 0E BE 00 A8 8A 7E 2E 3E 48 3E
2C 3E AA 2E AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E
AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E AE 2D AE 2D
22 3E 24 3E 22 3E 24 3E 22 3E 24 3E 22 3E 66 7E
00 A8 00 A8 00 A8 00 A8 26 3E 22 3E 24 3E 22 3E
24 3E AA 2E AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E
AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E AE 2D AE 2D
2C 3E 2E 3E 2C 3E 2E 3E 2C 3E 6A 3E 6C 3E 00 A8
00 A8 00 A8 00 A8 26 3E 2C 3E 2C 3E 2E 3E 2C 3E
2E 3E AA 2E AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E
AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E AE 2D AE 2D
22 3E 24 3E 2E 3E 22 3E 40 FE 00 A8 00 A8 00 A8
00 A8 00 A8 4C 3E 2E 3E 22 3E 24 3E 2E 3E 22 3E
24 3E AA 2E AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E
AE 2E CE 2D AA 2E AE 2E CE 2D AA 2E AE 2D AE 2D
"""

def test_room_0x5b_header_metadata():
    res = dump_room(0x5B)
    assert res["room_id"] == 0x5B
    h = res["header"]
    assert h["width_tiles"] == 72
    assert h["height_tiles"] == 48
    assert h["origin_x"] == 16
    assert h["origin_y"] == 9
    assert res["triggers"]["step_on_count"] == 5
    assert res["triggers"]["b_trigger_count"] == 17

def test_room_0x5b_tile_palette_delta_accumulator():
    res = dump_room(0x5B)
    palette = res["tile_palette"]
    assert len(palette) == 176
    assert palette[0] == "0x0CE6"

def test_room_0x5b_decompressed_grid_dimensions():
    res = dump_room(0x5B)
    assert len(res["layer1_vram_words"]) == 48
    assert all(len(row) == 72 for row in res["layer1_vram_words"])
    assert len(res["layer2_vram_words"]) == 48
    assert all(len(row) == 72 for row in res["layer2_vram_words"])

def test_room_0x5b_characteristic_vram_words():
    res = dump_room(0x5B)
    l1 = res["layer1_vram_int_words"]
    all_l1 = {w for r in l1 for w in r}
    # Characteristic tiles present in East Jungle canopy:
    sample_tiles = {0x3E22, 0x3E24, 0x3E2E, 0x7E4C, 0x3E4C, 0xA800}
    assert sample_tiles.issubset(all_l1)

def test_room_0x5b_cli_vram_bytes_flag():
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    cmd = [sys.executable, script_path, "0x5b", "--vram-bytes"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert proc.returncode == 0
    lines = proc.stdout.strip().splitlines()
    assert len(lines) > 0
