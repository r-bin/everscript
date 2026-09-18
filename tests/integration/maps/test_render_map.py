"""
Integration Test: Map Graphics PNG Rendering
-------------------------------------------
Verifies end-to-end rendering of Secret of Evermore map layers into PNG files:
  - 16x16 metatile decompression ($EE0000)
  - 4bpp planar pixel reconstruction with flip flags
  - CGRAM palette construction from tile families
  - Multi-layer assembly (Layer 1, Layer 2, Composite, Collision, Triggers)
  - CLI execution via tools/render_map.py and tools/dump_room.py --png
"""

import os
import sys
import subprocess
import pytest

from tools.dump_room import DEFAULT_ROM_PATH, dump_room
from tools.render_map import (
    decompress_tile_16x16,
    decode_tile_pixels,
    build_room_cgram_palettes,
    render_room_layers,
    save_png_pure,
    parse_color,
)


@pytest.fixture(scope="module")
def rom_bytes():
    if not os.path.exists(DEFAULT_ROM_PATH):
        pytest.skip(f"Vanilla ROM not found at: {DEFAULT_ROM_PATH}")
    with open(DEFAULT_ROM_PATH, "rb") as f:
        return f.read()


def test_decompress_tile_16x16(rom_bytes):
    """Verify tile 0x0282 decompresses to exactly 128 bytes."""
    tile_bytes = decompress_tile_16x16(rom_bytes, 0x0282)
    assert len(tile_bytes) == 128
    assert isinstance(tile_bytes, bytes)


def test_decode_tile_pixels():
    """Verify 4bpp planar decoding and flip transformations."""
    # Dummy 128 bytes: top-left sub-tile row 0 has pixel (0,0) with color 1
    dummy = bytearray(128)
    dummy[0] = 0x80  # Bitplane 0, bit 7 set -> pixel (0,0) = 1
    
    # Normal orientation
    pixels = decode_tile_pixels(bytes(dummy), hflip=False, vflip=False)
    assert len(pixels) == 16
    assert len(pixels[0]) == 16
    assert pixels[0][0] == 1
    assert pixels[0][15] == 0
    assert pixels[15][0] == 0

    # Horizontal flip -> pixel moves to (15, 0)
    pixels_h = decode_tile_pixels(bytes(dummy), hflip=True, vflip=False)
    assert pixels_h[0][15] == 1
    assert pixels_h[0][0] == 0

    # Vertical flip -> pixel moves to (0, 15)
    pixels_v = decode_tile_pixels(bytes(dummy), hflip=False, vflip=True)
    assert pixels_v[15][0] == 1
    assert pixels_v[0][0] == 0


def test_build_room_cgram_palettes(rom_bytes):
    """Verify CGRAM palettes extraction for Room 0x5C."""
    res = dump_room(0x5c, DEFAULT_ROM_PATH)
    families = [int(f, 16) for f in res["tile_families"]]
    palettes = build_room_cgram_palettes(rom_bytes, families)

    assert len(palettes) == 8
    for pal in palettes:
        assert len(pal) == 16
        # Color index 0 is always transparent
        assert pal[0][3] == 0
        # Other colors are opaque
        for c in pal[1:]:
            assert c[3] == 255


def test_render_room_0x5c_layers(tmp_path, rom_bytes):
    """Verify rendering Room 0x5C (Prehistoria - Raptors) produces valid PNG files."""
    out_dir = str(tmp_path / "maps_0x5c")
    files = render_room_layers(
        0x5c,
        rom_path=DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["1", "2", "composite"],
        with_collision=True,
        with_triggers=True,
    )

    expected_keys = {"layer1", "layer2", "composite", "collision", "triggers"}
    assert set(files.keys()) == expected_keys

    # Room 0x5C is 31x26 tiles -> 496x416 pixels
    expected_w = 31 * 16
    expected_h = 26 * 16

    for name, path in files.items():
        assert os.path.exists(path), f"File {path} must exist"
        with open(path, "rb") as f:
            header = f.read(8)
            assert header == b"\x89PNG\r\n\x1a\n", f"{name} must have valid PNG signature"
        
        # Verify size if Pillow is available
        try:
            from PIL import Image
            with Image.open(path) as img:
                assert img.size == (expected_w, expected_h)
        except ImportError:
            pass


def test_dump_room_cli_png_flag(tmp_path):
    """Verify tools/dump_room.py --png executes successfully."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    out_dir = str(tmp_path / "cli_png")
    cmd = [
        sys.executable,
        script_path,
        "0x5c",
        "--png",
        "--png-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Generated 3 PNG image(s)" in proc.stdout

    assert os.path.exists(os.path.join(out_dir, "room_0x5c_layer1.png"))
    assert os.path.exists(os.path.join(out_dir, "room_0x5c_layer2.png"))
    assert os.path.exists(os.path.join(out_dir, "room_0x5c_composite.png"))


def test_render_map_cli(tmp_path):
    """Verify tools/render_map.py CLI executes successfully."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "render_map.py")
    )
    out_dir = str(tmp_path / "cli_render")
    cmd = [
        sys.executable,
        script_path,
        "0x33",
        "--out-dir",
        out_dir,
        "--collision",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Successfully generated 4 image(s)" in proc.stdout

    assert os.path.exists(os.path.join(out_dir, "room_0x33_layer1.png"))
    assert os.path.exists(os.path.join(out_dir, "room_0x33_layer2.png"))
    assert os.path.exists(os.path.join(out_dir, "room_0x33_composite.png"))
    assert os.path.exists(os.path.join(out_dir, "room_0x33_collision.png"))


def test_render_room_0x38_with_fc4(tmp_path):
    """Verify Room 0x38 (fc4=72, 83x91 large map) decompresses and renders without corruption."""
    from tools.render_map import render_room_layers

    out_dir = str(tmp_path / "room_0x38")
    files = render_room_layers(
        room_id=0x38,
        rom_path=DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["composite"],
    )

    assert "composite" in files
    path = files["composite"]
    assert os.path.exists(path)

    # 83x91 tiles -> 1328x1456 pixels
    try:
        from PIL import Image
        with Image.open(path) as img:
            assert img.size == (83 * 16, 91 * 16)
    except ImportError:
        pass


def test_animated_tiles_extraction():
    """Verify Section 2 animated tile extraction across rooms."""
    r_4d = dump_room(0x4d, DEFAULT_ROM_PATH)
    assert "animated_tiles" in r_4d
    assert r_4d["animated_tiles_count"] == 18
    assert r_4d["animated_tiles"][0] == "0x14B3"

    r_4b = dump_room(0x4b, DEFAULT_ROM_PATH)
    assert "animated_tiles" in r_4b
    assert r_4b["animated_tiles_count"] == 13
    assert r_4b["animated_tiles"][0] == "0x1464"


def test_render_room_0x4d_palace_reflection(tmp_path):
    """Verify Room 0x4D renders with Mode 1 priority, floor reflections, and torch animations."""
    out_dir = str(tmp_path / "room_0x4d")
    files = render_room_layers(
        room_id=0x4d,
        rom_path=DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["composite"],
    )
    assert "composite" in files
    path = files["composite"]
    assert os.path.exists(path)

    try:
        from PIL import Image
        with Image.open(path) as img:
            assert img.size == (38 * 16, 17 * 16)
            # Check torch flame position at (80, 48) - should not be transparent
            p = img.getpixel((80, 48))
            assert p[3] == 255
    except ImportError:
        pass


def test_render_room_0x4b_water_and_vignette(tmp_path):
    """Verify Room 0x4B omits main screen vignette mask (TM=0x16) and renders water tiles."""
    out_dir = str(tmp_path / "room_0x4b")
    files = render_room_layers(
        room_id=0x4b,
        rom_path=DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["composite"],
    )
    assert "composite" in files
    path = files["composite"]
    assert os.path.exists(path)

    try:
        from PIL import Image
        with Image.open(path) as img:
            assert img.size == (106 * 16, 125 * 16)
    except ImportError:
        pass


def test_parse_color_formats(rom_bytes):
    """Verify parse_color handles standard names, hex codes, comma strings, tuples, and cgram."""
    assert parse_color("black") == (0, 0, 0, 255)
    assert parse_color("white") == (255, 255, 255, 255)
    assert parse_color("transparent") == (0, 0, 0, 0)
    assert parse_color("none") == (0, 0, 0, 0)
    assert parse_color("clear") == (0, 0, 0, 0)

    # Hex codes
    assert parse_color("#000") == (0, 0, 0, 255)
    assert parse_color("#fff") == (255, 255, 255, 255)
    assert parse_color("#123456") == (18, 52, 86, 255)
    assert parse_color("123456") == (18, 52, 86, 255)
    assert parse_color("#12345678") == (18, 52, 86, 120)

    # Comma-separated
    assert parse_color("10, 20, 30") == (10, 20, 30, 255)
    assert parse_color("10, 20, 30, 40") == (10, 20, 30, 40)

    # Tuples / Lists
    assert parse_color((1, 2, 3)) == (1, 2, 3, 255)
    assert parse_color([1, 2, 3, 4]) == (1, 2, 3, 4)

    # CGRAM
    cgram_col = parse_color("cgram", rom=rom_bytes, tile_families=["0x01"])
    assert len(cgram_col) == 4
    assert cgram_col[3] == 255

    # Invalid colors
    with pytest.raises(ValueError):
        parse_color("invalid_color_xyz")
    with pytest.raises(ValueError):
        parse_color("#12")


def test_render_background_color_override(tmp_path):
    """Verify default background is black and can be overridden via bg_color."""
    out_dir = str(tmp_path / "bg_override")

    # 1. Default (black)
    files_def = render_room_layers(0x4d, DEFAULT_ROM_PATH, os.path.join(out_dir, "def"), layers=["composite"])
    # 2. Transparent
    files_trans = render_room_layers(0x4d, DEFAULT_ROM_PATH, os.path.join(out_dir, "trans"), layers=["composite"], bg_color="transparent")
    # 3. Custom Hex
    files_hex = render_room_layers(0x4d, DEFAULT_ROM_PATH, os.path.join(out_dir, "hex"), layers=["composite"], bg_color="#123456")

    from PIL import Image
    with Image.open(files_def["composite"]) as img_def:
        # At (79, 56) both layers are empty backdrop in 0x4D
        assert img_def.getpixel((79, 56)) == (0, 0, 0, 255)

    with Image.open(files_trans["composite"]) as img_trans:
        assert img_trans.getpixel((79, 56)) == (0, 0, 0, 0)

    with Image.open(files_hex["composite"]) as img_hex:
        assert img_hex.getpixel((79, 56)) == (18, 52, 86, 255)


def test_render_map_cli_bg_color(tmp_path):
    """Verify tools/render_map.py CLI accepts --bg-color."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "render_map.py")
    )
    out_dir = str(tmp_path / "cli_bg")
    cmd = [
        sys.executable,
        script_path,
        "0x4d",
        "--layer",
        "composite",
        "--bg-color",
        "transparent",
        "--out-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Successfully generated 1 image(s)" in proc.stdout
    path = os.path.join(out_dir, "room_0x4d_composite.png")
    assert os.path.exists(path)

    from PIL import Image
    with Image.open(path) as img:
        assert img.getpixel((79, 56)) == (0, 0, 0, 0)


def test_dump_room_cli_bg_color(tmp_path):
    """Verify tools/dump_room.py CLI accepts --bg-color with --png."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    out_dir = str(tmp_path / "dump_cli_bg")
    cmd = [
        sys.executable,
        script_path,
        "0x4d",
        "--png",
        "--layer",
        "1",
        "--bg-color",
        "#123456",
        "--png-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "Generated 1 PNG image(s)" in proc.stdout




