"""
Integration Test: dump_room.py Object Parsing and CLI Flags
------------------------------------------------------------
Verifies:
1. Extraction of object counts and state descriptors from room blobs (0x15, 0x34, 0x38).
2. CLI flags --header, --objects, and combined --header --objects.
"""

import os
import sys
import subprocess
import pytest

from tools.dump_room import dump_room, DEFAULT_ROM_PATH

SCRIPT_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
)


def test_room_0x15_objects_baseline():
    """Room 0x15 (Brian's Test Ground) should have 0 objects."""
    res = dump_room(0x15)
    assert res["object_count"] == 0
    assert res["objects"] == []


def test_room_0x34_objects_gourds():
    """Room 0x34 (Strong Heart's Hut) should have 3 loot gourds."""
    res = dump_room(0x34)
    assert res["object_count"] == 3
    assert len(res["objects"]) == 3

    # Gourd 0 at (5, 5)
    g0 = res["objects"][0]
    assert g0["object_index"] == 0
    assert g0["max_state"] == 1
    assert g0["relative_offset"] == "0x0000"
    assert len(g0["states"]) == 1
    assert g0["states"][0]["tile_x"] == 5
    assert g0["states"][0]["tile_y"] == 5
    assert g0["states"][0]["width"] == 1
    assert g0["states"][0]["metatile_id"] == "0x0012"

    # Gourd 1 at (12, 7)
    g1 = res["objects"][1]
    assert g1["object_index"] == 1
    assert g1["max_state"] == 1
    assert g1["relative_offset"] == "0x0006"
    assert len(g1["states"]) == 1
    assert g1["states"][0]["tile_x"] == 12
    assert g1["states"][0]["tile_y"] == 7

    # Gourd 2 at (11, 5)
    g2 = res["objects"][2]
    assert g2["object_index"] == 2
    assert g2["max_state"] == 1
    assert g2["relative_offset"] == "0x000C"
    assert len(g2["states"]) == 1
    assert g2["states"][0]["tile_x"] == 11
    assert g2["states"][0]["tile_y"] == 5


def test_room_0x38_objects_count():
    """Room 0x38 (South Jungle) should have 31 objects (gourds + sniff spots)."""
    res = dump_room(0x38)
    assert res["object_count"] == 31
    assert len(res["objects"]) == 31


def test_cli_header_flag():
    """--header should output room metadata and trigger/object info, but suppress grid dumps."""
    cmd = [sys.executable, SCRIPT_PATH, "0x34", "--header"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert proc.returncode == 0
    stdout = proc.stdout

    assert "ROOM 0x34 (52) - MAP DATA DUMP" in stdout
    assert "Dimensions:      18 x 18 tiles" in stdout
    assert "Objects:         3" in stdout
    assert "[OBJ 00]" in stdout
    # Suppressed sections:
    assert "TILE PALETTE" not in stdout
    assert "LAYER 1 METATILE GRID" not in stdout
    assert "LAYER 1 VRAM TILEMAP WORDS" not in stdout


def test_cli_objects_flag_large_room():
    """--objects should output the full MAP OBJECTS table even for rooms with >5 objects."""
    cmd = [sys.executable, SCRIPT_PATH, "0x38", "--header", "--objects"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert proc.returncode == 0
    stdout = proc.stdout

    assert "Objects:         31" in stdout
    assert "MAP OBJECTS (31 objects):" in stdout
    assert "[OBJ 00] Offset: 0x0000" in stdout
    assert "[OBJ 30] Offset: 0x00B4" in stdout
    # Suppressed sections due to --header
    assert "TILE PALETTE" not in stdout
    assert "LAYER 1 METATILE GRID" not in stdout


def test_cli_header_room_0x15():
    """--header on empty room 0x15 outputs Objects: 0 without error."""
    cmd = [sys.executable, SCRIPT_PATH, "0x15", "--header"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert proc.returncode == 0
    assert "Objects:         0" in proc.stdout

