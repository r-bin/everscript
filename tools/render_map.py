#!/usr/bin/env python3
"""
Secret of Evermore Map Graphics PNG Renderer
-------------------------------------------
Renders room map layers directly to PNG images based on empirically verified
65c816 CHR tile graphics decompression ($8CC88C, $8CC9C0) and CGRAM palette
extraction ($90D020, $9CC322).

Output Layers:
  - Layer 1: Canopy / foreground overlay (RGBA with transparency)
  - Layer 2: Terrain / background base (RGBA)
  - Composite: Full composite with Layer 2 underneath and Layer 1 alpha-blended on top
  - Collision (optional): Visual color-coded collision & passability map
  - Triggers (optional): Trigger bounding boxes annotated over the composite
"""

import sys
import os
import argparse
import zlib
import struct
from typing import List, Tuple, Dict, Optional, Union, Any

# Ensure repository root is in sys.path so we can import tools.dump_room
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.dump_room import dump_room, DEFAULT_ROM_PATH, MAX_ROOMS

RGBA = Tuple[int, int, int, int]


# ---------------------------------------------------------------------------
# 1. Palette Extraction & CGRAM Building ($90D020 / $9CC322)
# ---------------------------------------------------------------------------

def extract_tile_family_palette(rom: bytes, family_id: int) -> List[RGBA]:
    """
    Extracts 16 RGBA colors for a single tile family from ROM $9CC322 (0x1CC322).
    Color 0 is transparent (Alpha = 0). Colors 1..15 are opaque (Alpha = 255).
    """
    base_addr = 0x1CC322 + (family_id * 32)
    colors: List[RGBA] = []

    for i in range(16):
        c16 = rom[base_addr + i * 2] | (rom[base_addr + i * 2 + 1] << 8)
        r5 = (c16 >> 0) & 0x1F
        g5 = (c16 >> 5) & 0x1F
        b5 = (c16 >> 10) & 0x1F

        # SNES 5-bit to 8-bit expansion: (c << 3) | (c >> 2)
        r8 = (r5 << 3) | (r5 >> 2)
        g8 = (g5 << 3) | (g5 >> 2)
        b8 = (b5 << 3) | (b5 >> 2)
        a8 = 0 if i == 0 else 255

        colors.append((r8, g8, b8, a8))

    return colors


def build_room_cgram_palettes(rom: bytes, tile_families: List[int]) -> List[List[RGBA]]:
    """
    Constructs the 8 CGRAM background sub-palettes for a room.
    - Palette 0: Fallback transparent / black.
    - Palettes 1..7: Mapped 1:1 to tile_families[0..6] (Color 16 in CGRAM = Palette 1).
    """
    palettes: List[List[RGBA]] = []

    # Palette 0: System / HUD default
    palettes.append([(0, 0, 0, 0 if i == 0 else 255) for i in range(16)])

    # Palettes 1..7 from room tile families
    for idx in range(7):
        if idx < len(tile_families):
            palettes.append(extract_tile_family_palette(rom, tile_families[idx]))
        else:
            palettes.append([(0, 0, 0, 0 if i == 0 else 255) for i in range(16)])

    return palettes


# ---------------------------------------------------------------------------
# 2. CHR Tile Graphics Decompression ($8CC88C / $8CC9C0)
# ---------------------------------------------------------------------------

def decompress_tile_16x16(rom: bytes, tile_id: int) -> bytes:
    """
    Decompresses a 16x16 metatile graphic (128 bytes, 4 sub-tiles of 8x8 in 4bpp)
    from the master $EE0000 table in Secret of Evermore ROM.
    """
    ptr_addr = 0x2E0000 + (tile_id * 3)
    data_addr = (rom[ptr_addr] | (rom[ptr_addr + 1] << 8) | (rom[ptr_addr + 2] << 16)) & 0x3FFFFF
    tile_info = rom[data_addr]

    decomp = bytearray(128)

    # Mode 1: Uncompressed word copy ($8CC8B0)
    if not (tile_info & 0x80):
        word_count = min((tile_info & 0x7F) + 1, 64)
        src = data_addr + 1
        decomp[:word_count * 2] = rom[src : src + word_count * 2]
        last_word = decomp[word_count * 2 - 2 : word_count * 2] if word_count > 0 else b"\x00\x00"
        for i in range(word_count * 2, 128, 2):
            decomp[i : i + 2] = last_word
        return bytes(decomp)

    # Mode 2: Dual-stream compressed ($8CC9C0)
    data_offset = tile_info & 0x7F
    data_ptr = data_addr + data_offset
    cmd_ptr = data_addr + 1
    cmd_second_half = False
    out_pos = 0

    def read4() -> int:
        nonlocal cmd_ptr, cmd_second_half
        val = rom[cmd_ptr]
        if cmd_second_half:
            res = val & 0x0F
            cmd_ptr += 1
        else:
            res = (val >> 4) & 0x0F
        cmd_second_half = not cmd_second_half
        return res

    while out_pos < 128:
        indicators = rom[data_ptr]
        data_ptr += 1
        for _ in range(8):
            if not (indicators & 0x80):
                # Uncompressed word literal
                decomp[out_pos] = rom[data_ptr]
                decomp[out_pos + 1] = rom[data_ptr + 1]
                data_ptr += 2
                out_pos += 2
            else:
                mode = read4()
                if mode == 0:
                    decomp[out_pos : out_pos + 2] = b"\x00\x00"
                    out_pos += 2
                elif mode == 1:
                    decomp[out_pos : out_pos + 2] = b"\xFF\x00"
                    out_pos += 2
                elif mode == 2:
                    decomp[out_pos : out_pos + 2] = b"\x00\xFF"
                    out_pos += 2
                elif mode == 3:
                    decomp[out_pos : out_pos + 2] = b"\xFF\xFF"
                    out_pos += 2
                elif mode == 4:
                    decomp[out_pos] = rom[data_ptr]; data_ptr += 1
                    decomp[out_pos + 1] = 0x00
                    out_pos += 2
                elif mode == 5:
                    decomp[out_pos] = rom[data_ptr]; data_ptr += 1
                    decomp[out_pos + 1] = 0xFF
                    out_pos += 2
                elif mode == 6:
                    decomp[out_pos] = 0x00
                    decomp[out_pos + 1] = rom[data_ptr]; data_ptr += 1
                    out_pos += 2
                elif mode == 7:
                    decomp[out_pos] = 0xFF
                    decomp[out_pos + 1] = rom[data_ptr]; data_ptr += 1
                    out_pos += 2
                elif mode == 8:
                    v = rom[data_ptr]; data_ptr += 1
                    decomp[out_pos] = v
                    decomp[out_pos + 1] = v
                    out_pos += 2
                elif 9 <= mode <= 12:
                    count = (mode - 9 + 1) + (read4() if mode == 12 else 0)
                    for _ in range(count):
                        if out_pos < 2:
                            decomp[out_pos : out_pos + 2] = b"\x00\x00"
                        else:
                            decomp[out_pos] = decomp[out_pos - 2]
                            decomp[out_pos + 1] = decomp[out_pos - 1]
                        out_pos += 2
                        if out_pos >= 128:
                            break
                elif mode == 13:
                    prev = decomp[out_pos - 2] if out_pos >= 2 else 0
                    decomp[out_pos] = prev
                    decomp[out_pos + 1] = rom[data_ptr]; data_ptr += 1
                    out_pos += 2
                elif mode == 14:
                    decomp[out_pos] = rom[data_ptr]; data_ptr += 1
                    prev = decomp[out_pos - 1] if out_pos >= 2 else 0
                    decomp[out_pos + 1] = prev
                    out_pos += 2
                elif mode == 15:
                    v = rom[data_ptr]; data_ptr += 1
                    decomp[out_pos] = v
                    decomp[out_pos + 1] = v ^ 0xFF
                    out_pos += 2

            if out_pos >= 128:
                break
            indicators = (indicators << 1) & 0xFF

    return bytes(decomp)


def decode_tile_pixels(tile_bytes: bytes, hflip: bool = False, vflip: bool = False) -> List[List[int]]:
    """
    Converts 128-byte 4bpp planar tile into a 16x16 2D array of palette color indices (0..15).
    Applies 16x16 horizontal and vertical hardware flip mirroring if specified.
    """
    assert len(tile_bytes) == 128
    pixels = [[0] * 16 for _ in range(16)]

    # 4 sub-tiles: (0,0)=top-left, (1,0)=top-right, (0,1)=bottom-left, (1,1)=bottom-right
    for sub_y in range(2):
        for sub_x in range(2):
            sub_idx = sub_x + (sub_y * 2)
            base = sub_idx * 32
            for row in range(8):
                b0 = tile_bytes[base + row * 2 + 0]
                b1 = tile_bytes[base + row * 2 + 1]
                b2 = tile_bytes[base + row * 2 + 16]
                b3 = tile_bytes[base + row * 2 + 17]
                for col in range(8):
                    mask = 1 << (7 - col)
                    p = ((1 if b0 & mask else 0) |
                         ((1 if b1 & mask else 0) << 1) |
                         ((1 if b2 & mask else 0) << 2) |
                         ((1 if b3 & mask else 0) << 3))
                    px = (sub_x * 8) + col
                    py = (sub_y * 8) + row
                    out_x = 15 - px if hflip else px
                    out_y = 15 - py if vflip else py
                    pixels[out_y][out_x] = p

    return pixels


# ---------------------------------------------------------------------------
# 3. PNG Image Saving (Pillow with pure-Python zlib fallback)
# ---------------------------------------------------------------------------

def save_png_pure(pixels_rgba: bytes, width: int, height: int, filepath: str) -> None:
    """
    Writes RGBA raw bytes to a standard PNG file using pure Python (zlib + struct).
    Guarantees zero third-party pip dependencies.
    """
    def chunk(tag: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(tag + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", crc)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))

    row_bytes = width * 4
    scanlines = bytearray()
    for y in range(height):
        scanlines.append(0)  # Filter type 0: None
        start = y * row_bytes
        scanlines.extend(pixels_rgba[start : start + row_bytes])

    idat = chunk(b"IDAT", zlib.compress(bytes(scanlines), level=6))
    iend = chunk(b"IEND", b"")

    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    with open(filepath, "wb") as f:
        f.write(sig + ihdr + idat + iend)


def save_png(pixels_rgba: bytearray, width: int, height: int, filepath: str) -> None:
    """Saves RGBA bytearray to PNG, using PIL if installed or pure-Python fallback."""
    os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
    try:
        from PIL import Image
        img = Image.frombytes("RGBA", (width, height), bytes(pixels_rgba))
        img.save(filepath, format="PNG")
    except ImportError:
        save_png_pure(bytes(pixels_rgba), width, height, filepath)


COLOR_NAMES: Dict[str, RGBA] = {
    "black": (0, 0, 0, 255),
    "white": (255, 255, 255, 255),
    "transparent": (0, 0, 0, 0),
    "none": (0, 0, 0, 0),
    "clear": (0, 0, 0, 0),
    "red": (255, 0, 0, 255),
    "green": (0, 255, 0, 255),
    "blue": (0, 0, 255, 255),
    "yellow": (255, 255, 0, 255),
    "cyan": (0, 255, 255, 255),
    "magenta": (255, 0, 255, 255),
    "gray": (128, 128, 128, 255),
    "grey": (128, 128, 128, 255),
}


def parse_color(
    val: Union[str, Tuple[int, ...], List[int]],
    rom: bytes = b"",
    tile_families: Optional[List[str]] = None,
) -> RGBA:
    """
    Parses a color specification into an RGBA 4-tuple (0..255).

    Supported formats:
        - Tuple/List of 3 or 4 ints: (R, G, B) or (R, G, B, A)
        - Named colors: 'black' (default), 'white', 'transparent', 'none', 'clear', etc.
        - 'cgram' or 'rom': extract SNES CGRAM Color 0 from the first tile family.
        - Hex: '#RRGGBB', '#RRGGBBAA', '#RGB', '#RGBA', or without '#'.
        - Comma-separated: 'R,G,B' or 'R,G,B,A'.
    """
    if isinstance(val, (tuple, list)):
        if len(val) == 3:
            return (int(val[0]), int(val[1]), int(val[2]), 255)
        elif len(val) == 4:
            return (int(val[0]), int(val[1]), int(val[2]), int(val[3]))
        raise ValueError(f"Color tuple must have 3 or 4 elements, got {len(val)}")

    if not isinstance(val, str):
        raise TypeError(f"Color must be a string, tuple, or list, got {type(val).__name__}")

    s = val.strip().lower()

    if s in COLOR_NAMES:
        return COLOR_NAMES[s]

    if s in ("cgram", "rom"):
        fam0 = int(tile_families[0], 16) if (tile_families and len(tile_families) > 0) else 0
        base_addr = 0x1CC322 + (fam0 * 32)
        if rom and base_addr + 1 < len(rom):
            c16 = rom[base_addr] | (rom[base_addr + 1] << 8)
            r5 = (c16 >> 0) & 0x1F
            g5 = (c16 >> 5) & 0x1F
            b5 = (c16 >> 10) & 0x1F
            return (
                (r5 << 3) | (r5 >> 2),
                (g5 << 3) | (g5 >> 2),
                (b5 << 3) | (b5 >> 2),
                255,
            )
        return (0, 0, 0, 255)

    # Check for hex format
    hex_str = s[1:] if s.startswith("#") else s
    if all(c in "0123456789abcdef" for c in hex_str):
        if len(hex_str) == 3:
            r = int(hex_str[0] * 2, 16)
            g = int(hex_str[1] * 2, 16)
            b = int(hex_str[2] * 2, 16)
            return (r, g, b, 255)
        elif len(hex_str) == 4:
            r = int(hex_str[0] * 2, 16)
            g = int(hex_str[1] * 2, 16)
            b = int(hex_str[2] * 2, 16)
            a = int(hex_str[3] * 2, 16)
            return (r, g, b, a)
        elif len(hex_str) == 6:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            return (r, g, b, 255)
        elif len(hex_str) == 8:
            r = int(hex_str[0:2], 16)
            g = int(hex_str[2:4], 16)
            b = int(hex_str[4:6], 16)
            a = int(hex_str[6:8], 16)
            return (r, g, b, a)

    # Check for comma-separated numbers: "r, g, b" or "r, g, b, a"
    if "," in s:
        parts = [p.strip() for p in s.split(",")]
        if len(parts) == 3:
            return (int(parts[0]), int(parts[1]), int(parts[2]), 255)
        elif len(parts) == 4:
            return (int(parts[0]), int(parts[1]), int(parts[2]), int(parts[3]))

    raise ValueError(f"Unable to parse background color: {val!r}")


# ---------------------------------------------------------------------------
# 4. Layer & Composite Rendering Pipeline
# ---------------------------------------------------------------------------

class RoomRenderer:
    def __init__(
        self,
        room_data: dict,
        rom: bytes,
        bg_color: Union[str, RGBA] = "black",
    ):
        self.room_data = room_data
        self.rom = rom
        self.header = room_data["header"]
        self.w_tiles = self.header["width_tiles"]
        self.h_tiles = self.header["height_tiles"]
        self.w_pixels = self.w_tiles * 16
        self.h_pixels = self.h_tiles * 16

        # Build palettes
        families = [int(f, 16) for f in room_data["tile_families"]]
        self.palettes = build_room_cgram_palettes(rom, families)

        # Cache unique tiles from room's Block 1 tile palette + Section 2 animated tiles
        self.palette_tile_ids = [int(t, 16) for t in room_data["tile_palette"]]
        if "animated_tiles" in room_data:
            self.palette_tile_ids.extend([int(t, 16) for t in room_data["animated_tiles"]])

        self.tile_cache: Dict[int, bytes] = {}
        for tid in self.palette_tile_ids:
            if tid not in self.tile_cache:
                self.tile_cache[tid] = decompress_tile_16x16(rom, tid)

        # Backdrop Color (default black: (0, 0, 0, 255), customizable via bg_color)
        self.backdrop_color: RGBA = parse_color(
            bg_color,
            rom=rom,
            tile_families=room_data.get("tile_families", []),
        )

        # Cache decoded 16x16 pixel arrays: (tile_id, hflip, vflip) -> 16x16 list
        self.pixel_cache: Dict[Tuple[int, bool, bool], List[List[int]]] = {}

    def get_metatile_pixels(self, tile_id: int, hflip: bool, vflip: bool) -> List[List[int]]:
        key = (tile_id, hflip, vflip)
        if key not in self.pixel_cache:
            t_bytes = self.tile_cache.get(tile_id, b"\x00" * 128)
            self.pixel_cache[key] = decode_tile_pixels(t_bytes, hflip=hflip, vflip=vflip)
        return self.pixel_cache[key]

    def render_vram_layer(self, vram_words: List[List[int]]) -> bytearray:
        """Renders a 2D grid of 16-bit SNES VRAM tilemap words to an RGBA bytearray."""
        buf = bytearray(self.w_pixels * self.h_pixels * 4)

        for r in range(self.h_tiles):
            for c in range(self.w_tiles):
                w = vram_words[r][c]
                vflip = bool(w & 0x8000)
                hflip = bool(w & 0x4000)
                pal_idx = (w >> 10) & 0x07
                char_idx = w & 0x03FF

                # Map SNES character index to Block 1 tile ID
                # Formula: char_index = (k // 8) * 0x20 + (k % 8) * 2
                k = (char_idx // 0x20) * 8 + (char_idx % 0x20) // 2
                tile_id = self.palette_tile_ids[k] if 0 <= k < len(self.palette_tile_ids) else 0

                pixels = self.get_metatile_pixels(tile_id, hflip, vflip)
                palette = self.palettes[pal_idx]

                base_y = r * 16
                base_x = c * 16

                for py in range(16):
                    row_offset = (base_y + py) * self.w_pixels * 4
                    for px in range(16):
                        c_idx = pixels[py][px]
                        color = palette[c_idx]
                        if color[3] > 0:
                            p_off = row_offset + (base_x + px) * 4
                            buf[p_off] = color[0]
                            buf[p_off + 1] = color[1]
                            buf[p_off + 2] = color[2]
                            buf[p_off + 3] = color[3]

        return buf

    def composite_layers(self, l2_buf: bytearray, l1_buf: bytearray) -> bytearray:
        """
        Composites Layer 1 (BG1) and Layer 2 (BG2) using SNES Mode 1 hardware rules:
        - Evaluates Main Screen flags (display_tm & 0x01 / 0x02)
        - Evaluates Tile Priority bits (0x2000 in VRAM word)
        - Evaluates SNES Color Math (CGADSUB half-addition / subscreen blending)
        - Fills backdrop pixels with backdrop_color (default: black)
        """
        w_tiles = self.w_tiles
        h_tiles = self.h_tiles
        w_px = self.w_pixels
        h_px = self.h_pixels
        comp = bytearray(w_px * h_px * 4)

        tm = int(self.header.get("display_tm", "0x17"), 16)
        bg1_main = bool(tm & 0x01)
        bg2_main = bool(tm & 0x02)

        cgadsub = int(self.header.get("color_math_cgadsub", "0x00"), 16)
        half_math = bool(cgadsub & 0x40)
        bg1_math = bool(cgadsub & 0x01)

        ts = int(self.header.get("subscreen_ts", "0x00"), 16)
        sub_has_bg2 = bool(ts & 0x02)

        l1_grid = self.room_data.get("layer1_vram_int_words", [])
        l2_grid = self.room_data.get("layer2_vram_int_words", [])

        if not l1_grid or not l2_grid:
            comp = bytearray(l2_buf)
            total_pixels = w_px * h_px
            for i in range(0, total_pixels * 4, 4):
                a1 = l1_buf[i + 3]
                if a1 == 255:
                    comp[i : i + 4] = l1_buf[i : i + 4]
                elif a1 > 0:
                    alpha = a1 / 255.0
                    inv = 1.0 - alpha
                    comp[i] = int(l1_buf[i] * alpha + comp[i] * inv)
                    comp[i + 1] = int(l1_buf[i + 1] * alpha + comp[i + 1] * inv)
                    comp[i + 2] = int(l1_buf[i + 2] * alpha + comp[i + 2] * inv)
                    comp[i + 3] = 255
            return comp

        for ty in range(h_tiles):
            for tx in range(w_tiles):
                w1 = l1_grid[ty][tx]
                w2 = l2_grid[ty][tx]
                p1 = bool(w1 & 0x2000)
                p2 = bool(w2 & 0x2000)

                for py in range(16):
                    y = ty * 16 + py
                    row_off = y * w_px * 4
                    for px in range(16):
                        x = tx * 16 + px
                        i = row_off + x * 4

                        a1 = l1_buf[i + 3] if bg1_main else 0
                        a2 = l2_buf[i + 3] if bg2_main else 0

                        r1, g1, b1_c = l1_buf[i], l1_buf[i + 1], l1_buf[i + 2]
                        r2, g2, b2_c = l2_buf[i], l2_buf[i + 1], l2_buf[i + 2]

                        sub_a = l2_buf[i + 3] if sub_has_bg2 else 0

                        # Mode 1 priority:
                        # 1. BG1 Pri 1
                        # 2. BG2 Pri 1
                        # 3. BG1 Pri 0
                        # 4. BG2 Pri 0
                        if p1 and a1 > 0:
                            if bg1_math and sub_a > 0:
                                if half_math:
                                    comp[i] = (r1 + r2) // 2
                                    comp[i + 1] = (g1 + g2) // 2
                                    comp[i + 2] = (b1_c + b2_c) // 2
                                else:
                                    comp[i] = min(255, r1 + r2)
                                    comp[i + 1] = min(255, g1 + g2)
                                    comp[i + 2] = min(255, b1_c + b2_c)
                            else:
                                comp[i], comp[i + 1], comp[i + 2] = r1, g1, b1_c
                            comp[i + 3] = 255
                        elif p2 and a2 > 0:
                            comp[i], comp[i + 1], comp[i + 2], comp[i + 3] = r2, g2, b2_c, 255
                        elif (not p1) and a1 > 0:
                            if bg1_math and sub_a > 0:
                                if half_math:
                                    comp[i] = (r1 + r2) // 2
                                    comp[i + 1] = (g1 + g2) // 2
                                    comp[i + 2] = (b1_c + b2_c) // 2
                                else:
                                    comp[i] = min(255, r1 + r2)
                                    comp[i + 1] = min(255, g1 + g2)
                                    comp[i + 2] = min(255, b1_c + b2_c)
                            else:
                                comp[i], comp[i + 1], comp[i + 2] = r1, g1, b1_c
                            comp[i + 3] = 255
                        elif (not p2) and a2 > 0:
                            comp[i], comp[i + 1], comp[i + 2], comp[i + 3] = r2, g2, b2_c, 255
                        else:
                            # Backdrop
                            comp[i] = self.backdrop_color[0]
                            comp[i + 1] = self.backdrop_color[1]
                            comp[i + 2] = self.backdrop_color[2]
                            comp[i + 3] = self.backdrop_color[3]

        return comp

    def render_collision_overlay(self, collision_words: List[List[int]], base_comp: Optional[bytearray] = None) -> bytearray:
        """
        Renders collision attribute visualization. If base_comp is provided,
        overlays semi-transparent colored tiles on top of the composite.
        """
        buf = bytearray(base_comp) if base_comp else bytearray(self.w_pixels * self.h_pixels * 4)

        # Generate a distinct pastel palette for distinct collision attribute words
        unique_words = sorted(list(set(w for row in collision_words for w in row)))
        color_map: Dict[int, RGBA] = {}
        for idx, cw in enumerate(unique_words):
            if cw == 0:
                color_map[cw] = (0, 0, 0, 0)
            else:
                hue = (idx * 360 // max(len(unique_words), 1))
                # Simple distinct RGB generation from hue
                hi = (hue // 60) % 6
                f = (hue % 60) / 60.0
                q = int(255 * (1 - f))
                t = int(255 * f)
                if hi == 0: r, g, b = 255, t, 0
                elif hi == 1: r, g, b = q, 255, 0
                elif hi == 2: r, g, b = 0, 255, t
                elif hi == 3: r, g, b = 0, q, 255
                elif hi == 4: r, g, b = t, 0, 255
                else: r, g, b = 255, 0, q
                alpha = 140 if base_comp else 255
                color_map[cw] = (r, g, b, alpha)

        for r in range(self.h_tiles):
            for c in range(self.w_tiles):
                cw = collision_words[r][c]
                col = color_map.get(cw, (0, 0, 0, 0))
                if col[3] == 0:
                    continue
                base_y = r * 16
                base_x = c * 16
                for py in range(16):
                    row_offset = (base_y + py) * self.w_pixels * 4
                    for px in range(16):
                        p_off = row_offset + (base_x + px) * 4
                        # Draw grid border (1px) or solid cell
                        is_border = (py == 0 or py == 15 or px == 0 or px == 15)
                        if is_border and base_comp:
                            buf[p_off] = 255
                            buf[p_off + 1] = 255
                            buf[p_off + 2] = 255
                            buf[p_off + 3] = 200
                        else:
                            a = col[3] / 255.0
                            buf[p_off] = int(col[0] * a + buf[p_off] * (1 - a))
                            buf[p_off + 1] = int(col[1] * a + buf[p_off + 1] * (1 - a))
                            buf[p_off + 2] = int(col[2] * a + buf[p_off + 2] * (1 - a))
                            buf[p_off + 3] = 255

        return buf

    def render_triggers_overlay(self, base_comp: bytearray) -> bytearray:
        """Draws Step-on and B-trigger bounding boxes on top of the composite map."""
        buf = bytearray(base_comp)
        ox = self.header["origin_x"]
        oy = self.header["origin_y"]

        def draw_box(x1, y1, x2, y2, color: RGBA, fill_color: RGBA):
            # Clamp to map bounds
            x1 = max(0, min(x1, self.w_pixels - 1))
            x2 = max(0, min(x2, self.w_pixels))
            y1 = max(0, min(y1, self.h_pixels - 1))
            y2 = max(0, min(y2, self.h_pixels))

            for y in range(y1, y2):
                row_off = y * self.w_pixels * 4
                for x in range(x1, x2):
                    p_off = row_off + x * 4
                    is_border = (y == y1 or y == y2 - 1 or x == x1 or x == x2 - 1)
                    draw_c = color if is_border else fill_color
                    a = draw_c[3] / 255.0
                    buf[p_off] = int(draw_c[0] * a + buf[p_off] * (1 - a))
                    buf[p_off + 1] = int(draw_c[1] * a + buf[p_off + 1] * (1 - a))
                    buf[p_off + 2] = int(draw_c[2] * a + buf[p_off + 2] * (1 - a))
                    buf[p_off + 3] = 255

        # 1. Step-on triggers (Green)
        for t in self.room_data["triggers"]["step_on"]:
            px1 = (t["x1"] - ox) * 16
            py1 = (t["y1"] - oy) * 16
            px2 = (t["x2"] - ox) * 16
            py2 = (t["y2"] - oy) * 16
            draw_box(px1, py1, px2, py2, color=(0, 255, 60, 255), fill_color=(0, 255, 60, 80))

        # 2. B-triggers (Orange / Yellow)
        for t in self.room_data["triggers"]["b_trigger"]:
            px1 = (t["x1"] - ox) * 16
            py1 = (t["y1"] - oy) * 16
            px2 = (t["x2"] - ox) * 16
            py2 = (t["y2"] - oy) * 16
            draw_box(px1, py1, px2, py2, color=(255, 200, 0, 255), fill_color=(255, 200, 0, 100))

        return buf


def render_room_layers(
    room_id: int,
    rom_path: str = DEFAULT_ROM_PATH,
    out_dir: str = "out/maps",
    layers: Optional[List[str]] = None,
    with_collision: bool = False,
    with_triggers: bool = False,
    bg_color: Union[str, RGBA] = "black",
) -> Dict[str, str]:
    """
    Renders all layers for a given room ID and saves them as PNG files.

    Args:
        room_id:        Room ID (0..126).
        rom_path:       Path to Secret of Evermore (U) ROM file.
        out_dir:        Destination directory for output PNG files.
        layers:         List of layers to generate: '1', '2', 'composite', 'collision', 'triggers'.
                        Defaults to ['1', '2', 'composite'].
        with_collision: If True, also renders collision layer.
        with_triggers:  If True, also renders triggers overlay.
        bg_color:       Backdrop color for composite: 'black' (default), 'transparent',
                        'cgram', hex string (#RRGGBB / #RRGGBBAA), or RGBA tuple.

    Returns:
        Dictionary mapping layer name to output PNG file path.
    """
    if not os.path.exists(rom_path):
        raise FileNotFoundError(f"ROM file not found at: {rom_path}")

    with open(rom_path, "rb") as f:
        rom = f.read()

    room_data = dump_room(room_id, rom_path)
    renderer = RoomRenderer(room_data, rom, bg_color=bg_color)

    os.makedirs(out_dir, exist_ok=True)
    prefix = f"room_0x{room_id:02x}"
    output_files: Dict[str, str] = {}

    selected_layers = set(layers if layers else ["1", "2", "composite"])
    if with_collision:
        selected_layers.add("collision")
    if with_triggers:
        selected_layers.add("triggers")

    l1_buf: Optional[bytearray] = None
    l2_buf: Optional[bytearray] = None
    comp_buf: Optional[bytearray] = None

    # Render Layer 1 (Canopy)
    if "1" in selected_layers or "composite" in selected_layers or "triggers" in selected_layers or "collision" in selected_layers:
        l1_buf = renderer.render_vram_layer(room_data["layer1_vram_int_words"])
        if "1" in selected_layers:
            path_l1 = os.path.join(out_dir, f"{prefix}_layer1.png")
            save_png(l1_buf, renderer.w_pixels, renderer.h_pixels, path_l1)
            output_files["layer1"] = path_l1

    # Render Layer 2 (Terrain)
    if "2" in selected_layers or "composite" in selected_layers or "triggers" in selected_layers or "collision" in selected_layers:
        l2_buf = renderer.render_vram_layer(room_data["layer2_vram_int_words"])
        if "2" in selected_layers:
            path_l2 = os.path.join(out_dir, f"{prefix}_layer2.png")
            save_png(l2_buf, renderer.w_pixels, renderer.h_pixels, path_l2)
            output_files["layer2"] = path_l2

    # Render Composite (Layer 2 + Layer 1)
    if "composite" in selected_layers or "triggers" in selected_layers or "collision" in selected_layers:
        assert l1_buf is not None and l2_buf is not None
        comp_buf = renderer.composite_layers(l2_buf, l1_buf)
        if "composite" in selected_layers:
            path_comp = os.path.join(out_dir, f"{prefix}_composite.png")
            save_png(comp_buf, renderer.w_pixels, renderer.h_pixels, path_comp)
            output_files["composite"] = path_comp

    # Render Collision
    if "collision" in selected_layers:
        coll_buf = renderer.render_collision_overlay(room_data["collision_int_words"], base_comp=comp_buf)
        path_coll = os.path.join(out_dir, f"{prefix}_collision.png")
        save_png(coll_buf, renderer.w_pixels, renderer.h_pixels, path_coll)
        output_files["collision"] = path_coll

    # Render Triggers Overlay
    if "triggers" in selected_layers:
        assert comp_buf is not None
        trig_buf = renderer.render_triggers_overlay(comp_buf)
        path_trig = os.path.join(out_dir, f"{prefix}_triggers.png")
        save_png(trig_buf, renderer.w_pixels, renderer.h_pixels, path_trig)
        output_files["triggers"] = path_trig

    return output_files


# ---------------------------------------------------------------------------
# 5. CLI Interface
# ---------------------------------------------------------------------------

def parse_room_id(raw: str) -> int:
    raw = raw.strip()
    if raw.startswith("0x") or raw.startswith("0X"):
        return int(raw, 16)
    elif any(c in "abcdefABCDEF" for c in raw):
        return int(raw, 16)
    return int(raw)


def main():
    parser = argparse.ArgumentParser(
        description="Render Secret of Evermore map layers to PNG images."
    )
    parser.add_argument("room", nargs="?", help="Room ID (hex e.g. 0x5c, decimal e.g. 92)")
    parser.add_argument("--rom", default=DEFAULT_ROM_PATH, help="Path to Secret of Evermore ROM")
    parser.add_argument("--out-dir", "-o", default="out/maps", help="Output directory for PNGs (default: out/maps)")
    parser.add_argument(
        "--layer",
        choices=["1", "2", "composite", "all", "collision", "triggers"],
        default="all",
        help="Layer to render: 1, 2, composite, collision, triggers, or all (default: all)",
    )
    parser.add_argument("--collision", action="store_true", help="Include collision visualization layer")
    parser.add_argument("--triggers", action="store_true", help="Include triggers overlay on composite")
    parser.add_argument(
        "--bg-color",
        "--background",
        default="black",
        help="Backdrop color: 'black' (default), 'transparent', 'cgram', hex (#RRGGBB or #RRGGBBAA), or R,G,B (default: black)",
    )
    parser.add_argument("--all-rooms", action="store_true", help="Render all 127 vanilla rooms")

    args = parser.parse_args()

    if args.all_rooms:
        print(f"Rendering all {MAX_ROOMS} rooms into {args.out_dir}...")
        ok = 0
        fail = 0
        for rid in range(MAX_ROOMS):
            try:
                render_room_layers(
                    rid,
                    rom_path=args.rom,
                    out_dir=args.out_dir,
                    layers=["composite"],
                    bg_color=args.bg_color,
                )
                print(f"Room 0x{rid:02X}: OK")
                ok += 1
            except Exception as e:
                print(f"Room 0x{rid:02X}: FAILED - {e}")
                fail += 1
        print(f"\n{ok} passed, {fail} failed out of {MAX_ROOMS} rooms.")
        return

    if not args.room:
        parser.error("room ID is required unless --all-rooms is specified")

    room_id = parse_room_id(args.room)

    if args.layer == "all":
        layers = ["1", "2", "composite"]
    else:
        layers = [args.layer]

    print(f"Rendering Room 0x{room_id:02X}...")
    files = render_room_layers(
        room_id,
        rom_path=args.rom,
        out_dir=args.out_dir,
        layers=layers,
        with_collision=args.collision or (args.layer == "collision"),
        with_triggers=args.triggers or (args.layer == "triggers"),
        bg_color=args.bg_color,
    )

    print(f"Successfully generated {len(files)} image(s) in {args.out_dir}:")
    for name, path in files.items():
        print(f"  [{name:9s}] {path}")


if __name__ == "__main__":
    main()

