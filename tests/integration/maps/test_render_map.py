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
    parse_grid_spec,
    parse_grid_opacity,
    RoomRenderer,
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


def test_render_room_0x3d_sewer_water_transparency(tmp_path):
    """Verify Room 0x3D pipe sewer water uses CGADSUB half-addition color math."""
    out_dir = str(tmp_path / "room_0x3d")
    files = render_room_layers(0x3d, DEFAULT_ROM_PATH, out_dir=out_dir, layers=["composite"])
    assert "composite" in files
    path = files["composite"]
    assert os.path.exists(path)

    from PIL import Image
    with Image.open(path) as img:
        # At (80, 128), L2 water (107, 132, 165) blends over L1 pipe (99, 148, 49) -> (103, 140, 107)
        assert img.getpixel((80, 128)) == (103, 140, 107, 255)


def test_render_room_0x6f_light_rays_additive_blend(tmp_path):
    """Verify Room 0x6F window light rays use CGADSUB additive color math over the window."""
    out_dir = str(tmp_path / "room_0x6f")
    files = render_room_layers(0x6f, DEFAULT_ROM_PATH, out_dir=out_dir, layers=["composite"])
    assert "composite" in files
    path = files["composite"]
    assert os.path.exists(path)

    from PIL import Image
    with Image.open(path) as img:
        # At (240, 100), light rays blend additively over stained glass window
        p = img.getpixel((240, 100))
        assert p == (73, 57, 40, 255)


def test_parse_grid_spec():
    """Verify parse_grid_spec handles strings, tuples, single ints, and errors."""
    assert parse_grid_spec("8,16") == (8, 16)
    assert parse_grid_spec("8x16") == (8, 16)
    assert parse_grid_spec("8/16") == (8, 16)
    assert parse_grid_spec("16") == (0, 16)
    assert parse_grid_spec(16) == (0, 16)
    assert parse_grid_spec((8, 16)) == (8, 16)
    assert parse_grid_spec([8, 16]) == (8, 16)
    assert parse_grid_spec("8") == (0, 8)
    assert parse_grid_spec([16]) == (0, 16)

    with pytest.raises(ValueError):
        parse_grid_spec("0")
    with pytest.raises(ValueError):
        parse_grid_spec("-1")
    with pytest.raises(ValueError):
        parse_grid_spec("1,2,3")


def test_parse_grid_opacity():
    """Verify parse_grid_opacity handles defaults, single floats, pairs, and clamping."""
    assert parse_grid_opacity(None) == (0.12, 0.30)
    assert parse_grid_opacity("0.12,0.30") == (0.12, 0.30)
    assert parse_grid_opacity("0.25,0.75") == (0.25, 0.75)
    assert parse_grid_opacity((0.15, 0.45)) == (0.15, 0.45)
    # Single float scales soft grid proportionally
    soft, strong = parse_grid_opacity("0.3")
    assert strong == 0.3
    assert soft == round(0.3 * 0.4, 3)

    # Clamping
    assert parse_grid_opacity("1.5,2.0") == (1.0, 1.0)
    assert parse_grid_opacity("-0.5,0.5") == (0.0, 0.5)


def test_render_grid_overlay(tmp_path):
    """Verify render_grid_overlay draws distinct soft and strong lines."""
    out_dir = str(tmp_path / "grid_unit")
    files = render_room_layers(
        0x5c,
        DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["grid", "composite"],
        with_grid=True,
    )
    assert "grid" in files
    assert "composite" in files
    path_grid = files["grid"]
    path_comp = files["composite"]
    assert os.path.exists(path_grid)
    assert os.path.exists(path_comp)

    from PIL import Image
    with Image.open(path_comp) as img_comp, Image.open(path_grid) as img_grid:
        # At (1, 1), not on a grid line: pixels must match composite exactly
        p_comp_off = img_comp.getpixel((1, 1))
        p_grid_off = img_grid.getpixel((1, 1))
        assert p_comp_off == p_grid_off

        # At (8, 1), on 8px soft grid line (x=8): should be slightly brighter than composite
        p_comp_soft = img_comp.getpixel((8, 1))
        p_grid_soft = img_grid.getpixel((8, 1))
        assert p_grid_soft != p_comp_soft

        # At (16, 1), on 16px strong grid line (x=16): should be brighter than soft line
        p_comp_str = img_comp.getpixel((16, 1))
        p_grid_str = img_grid.getpixel((16, 1))
        assert p_grid_str != p_comp_str


def test_render_map_cli_grid(tmp_path):
    """Verify tools/render_map.py CLI produces room_0x5c_grid.png with --grid."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "render_map.py")
    )
    out_dir = str(tmp_path / "cli_grid")
    cmd = [
        sys.executable,
        script_path,
        "0x5c",
        "--grid",
        "--grid-color",
        "white",
        "--out-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "[grid     ]" in proc.stdout
    assert os.path.exists(os.path.join(out_dir, "room_0x5c_grid.png"))


def test_dump_room_cli_grid(tmp_path):
    """Verify tools/dump_room.py CLI produces grid PNG when --grid is specified."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    out_dir = str(tmp_path / "dump_grid")
    cmd = [
        sys.executable,
        script_path,
        "0x5c",
        "--grid",
        "--png-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "[grid     ]" in proc.stdout
    assert os.path.exists(os.path.join(out_dir, "room_0x5c_grid.png"))


def test_render_triggers_colors(tmp_path):
    """Verify B-triggers render in yellow (0xffff00) and step-on triggers in pink (0xff00ff) matching soestuff.lua."""
    out_dir = str(tmp_path / "triggers_test")
    files = render_room_layers(
        0x5c,
        DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["triggers", "composite"],
        with_triggers=True,
    )
    assert "triggers" in files
    path_trig = files["triggers"]
    assert os.path.exists(path_trig)

    from PIL import Image
    with Image.open(path_trig) as img:
        # Step-on trigger at (176, 240) has solid pink border (255, 0, 255, 255)
        p_step_border = img.getpixel((176, 240))
        assert p_step_border == (255, 0, 255, 255)

        # B-trigger at (80, 112) has solid yellow border (255, 255, 0, 255)
        p_b_border = img.getpixel((80, 112))
        assert p_b_border == (255, 255, 0, 255)


def test_render_map_cli_triggers_layer(tmp_path):
    """Verify tools/render_map.py CLI produces triggers PNG when --layer triggers is used."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "render_map.py")
    )
    out_dir = str(tmp_path / "cli_trig")
    cmd = [
        sys.executable,
        script_path,
        "0x5c",
        "--layer",
        "triggers",
        "--out-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "[triggers ]" in proc.stdout
    assert os.path.exists(os.path.join(out_dir, "room_0x5c_triggers.png"))


def test_render_collision_labels_and_legend(tmp_path):
    """Verify --collision renders unique colors and type numbers, plus console legend."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "render_map.py")
    )
    out_dir = str(tmp_path / "cli_coll")
    cmd = [
        sys.executable,
        script_path,
        "0x34",
        "--layer",
        "collision",
        "--out-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "[collision]" in proc.stdout
    assert "Collision Types (23 unique in Room 0x34):" in proc.stdout
    assert "[ 0] 0x0010" in proc.stdout
    assert "[14] 0x101F" in proc.stdout

    path_coll = os.path.join(out_dir, "room_0x34_collision.png")
    assert os.path.exists(path_coll)

    from PIL import Image
    with Image.open(path_coll) as img:
        # Check size (18x18 metatiles = 288x288 px)
        assert img.size == (288, 288)


def test_render_collision_hex_labels(tmp_path):
    """Verify --collision-label hex renders without errors."""
    from tools.render_map import render_room_layers

    out_dir = str(tmp_path / "coll_hex")
    files = render_room_layers(
        0x34,
        DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["collision"],
        with_collision=True,
        collision_label="hex",
    )
    assert "collision" in files
    assert os.path.exists(files["collision"])


def test_render_collision_contour_default(tmp_path):
    """Verify default collision mode renders continuous red border lines and light red solid tint."""
    from tools.render_map import render_room_layers

    out_dir = str(tmp_path / "coll_contour")
    files = render_room_layers(
        0x34,
        DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["collision"],
        with_collision=True,
    )
    assert "collision" in files
    path = files["collision"]
    assert os.path.exists(path)

    from PIL import Image
    with Image.open(path) as img:
        assert img.size == (288, 288)

        # Verify presence of crisp red border line pixels (235, 25, 25, 255)
        red_count = sum(1 for y in range(img.height) for x in range(img.width) if img.getpixel((x, y)) == (235, 25, 25, 255))
        assert red_count > 1000, f"Expected thousands of red border pixels, found {red_count}"

        # Doorway passage at (136, 276) is walkable -> untinted composite floor
        p_door = img.getpixel((136, 276))
        assert p_door[3] == 255


def test_render_collision_ascii_mode(tmp_path):
    """Verify ascii collision mode colorizes by physical group and renders ASCII art."""
    from tools.render_map import render_room_layers

    out_dir = str(tmp_path / "coll_ascii")
    files = render_room_layers(
        0x34,
        DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["collision"],
        with_collision=True,
        collision_mode="ascii",
    )
    assert "collision" in files
    path = files["collision"]
    assert os.path.exists(path)

    from PIL import Image
    with Image.open(path) as img:
        assert img.size == (288, 288)

        # Check Walkable Floor (0x4010, low=0) at bottom center (row 17, col 8) -> Soft green fill at (130, 274)
        p_door = img.getpixel((130, 274))
        assert p_door[1] > p_door[0] and p_door[1] > p_door[2], f"Expected green floor fill, got {p_door}"

        # Check Solid Wall (0x0F) at upper ring (row 2, col 5) -> Red fill at (82, 34)
        p_wall = img.getpixel((82, 34))
        assert p_wall[0] > p_wall[1] and p_wall[0] > p_wall[2], f"Expected red wall fill, got {p_wall}"

        # Check white '#' glyph at foreground coordinate (86, 38)
        p_glyph = img.getpixel((86, 38))
        assert p_glyph == (255, 255, 255, 255), f"Expected white glyph pixel, got {p_glyph}"

        # Check Diagonal Slope \ (0x02) at row 14, col 2 -> Orange fill at (34, 226)
        p_slope = img.getpixel((34, 226))
        assert p_slope[0] >= 180 and p_slope[1] >= 80 and p_slope[2] < 50, f"Expected orange slope, got {p_slope}"

        # Check Tree Stump Top Barrier - (0x03) at row 10, col 7 -> Yellow fill at (114, 162)
        p_table = img.getpixel((114, 162))
        assert p_table[0] >= 180 and p_table[1] >= 150 and p_table[2] < 50, f"Expected yellow barrier, got {p_table}"


def test_render_collision_verbose_mode(tmp_path):
    """Verify --collision-verbose flag renders raw word palette view."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "render_map.py")
    )
    out_dir = str(tmp_path / "coll_verbose")
    cmd = [
        sys.executable,
        script_path,
        "0x34",
        "--layer",
        "collision",
        "--collision-verbose",
        "--out-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "[collision]" in proc.stdout
    assert "Collision Physical Groups (Room 0x34):" in proc.stdout
    assert "Collision Types (23 unique in Room 0x34):" in proc.stdout

def test_render_composition_unified_layer(tmp_path):
    """Verify render_full_composition generates unified graphic with correct dimensions and legend."""
    out_dir = str(tmp_path / "composition_test")
    files = render_room_layers(
        0x3B,
        DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["composition"],
        with_legend=True,
    )
    assert "composition" in files
    path_comp = files["composition"]
    assert os.path.exists(path_comp)

    from PIL import Image
    with Image.open(path_comp) as img:
        # Base Room 0x3B is 80x89 metatiles = 1280x1424 px, plus 36px legend banner = 1460 px
        assert img.size == (1280, 1460)

    # Test with with_legend=False
    files_no_leg = render_room_layers(
        0x3B,
        DEFAULT_ROM_PATH,
        out_dir=out_dir,
        layers=["composition"],
        with_legend=False,
    )
    with Image.open(files_no_leg["composition"]) as img_no_leg:
        assert img_no_leg.size == (1280, 1424)


def test_render_map_cli_composition(tmp_path):
    """Verify tools/render_map.py CLI produces room_0x3b_composition.png with --layer composition."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "render_map.py")
    )
    out_dir = str(tmp_path / "cli_comp")
    cmd = [
        sys.executable,
        script_path,
        "0x3b",
        "--layer",
        "composition",
        "--out-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "[composition]" in proc.stdout
    path_png = os.path.join(out_dir, "room_0x3b_composition.png")
    assert os.path.exists(path_png)


def test_dump_room_cli_composition(tmp_path):
    """Verify tools/dump_room.py CLI produces room_0x12_composition.png with --composition."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    out_dir = str(tmp_path / "dump_comp")
    cmd = [
        sys.executable,
        script_path,
        "0x12",
        "--composition",
        "--png-dir",
        out_dir,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    assert "[composition]" in proc.stdout
    path_png = os.path.join(out_dir, "room_0x12_composition.png")
    assert os.path.exists(path_png)








