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

from tools.dump_room import dump_room, DEFAULT_ROM_PATH, MAX_ROOMS, read16, read24, snes2rom

RGBA = Tuple[int, int, int, int]

# One contour colour per elevation plane (collision word bits 5..4, see
# tools/collision.py).  Plane 1 keeps the familiar red because 104 of the 127
# vanilla rooms are plane-1 only, so single-level rooms look unchanged.
PLANE_COLORS: Dict[int, Tuple[int, int, int]] = {
    0: (0, 170, 255),
    1: (235, 25, 25),
    2: (0, 255, 170),
    3: (190, 90, 255),
}


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


def parse_grid_spec(spec: Union[str, int, float, Tuple[int, int], List[int]]) -> Tuple[int, int]:
    """
    Parses a grid specification into (soft_step, strong_step).

    Supported formats:
        - "8,16", "8x16", "8/16", "8 16": 8px soft grid and 16px strong grid.
        - "16", 16: 16px strong grid only (soft_step = 0).
        - "8", 8: 8px strong grid only (soft_step = 0).
        - (8, 16) or [8, 16]: explicit tuple/list of step sizes.
    """
    if isinstance(spec, (int, float)):
        v = int(spec)
        if v <= 0:
            raise ValueError(f"Grid step size must be positive, got {spec}")
        return (0, v)

    if isinstance(spec, (tuple, list)):
        if len(spec) == 1:
            v = int(spec[0])
            if v <= 0:
                raise ValueError(f"Grid step size must be positive, got {spec[0]}")
            return (0, v)
        elif len(spec) == 2:
            s, st = int(spec[0]), int(spec[1])
            if s <= 0 or st <= 0:
                raise ValueError(f"Grid step sizes must be positive, got {spec}")
            return (min(s, st), max(s, st)) if s != st else (0, s)
        raise ValueError(f"Grid spec tuple/list must have 1 or 2 elements, got {len(spec)}")

    if isinstance(spec, str):
        clean = spec.replace("x", ",").replace("/", ",").replace(" ", ",").strip()
        if "," in clean:
            parts = [int(p.strip()) for p in clean.split(",") if p.strip()]
            if len(parts) == 2:
                s, st = parts[0], parts[1]
                if s <= 0 or st <= 0:
                    raise ValueError(f"Grid step sizes must be positive, got {spec}")
                return (min(s, st), max(s, st)) if s != st else (0, s)
            elif len(parts) == 1:
                v = parts[0]
                if v <= 0:
                    raise ValueError(f"Grid step size must be positive, got {spec}")
                return (0, v)
            raise ValueError(f"Invalid grid spec: {spec!r}")
        v = int(clean)
        if v <= 0:
            raise ValueError(f"Grid step size must be positive, got {spec}")
        return (0, v)

    raise TypeError(f"Grid spec must be string, int, tuple, or list, got {type(spec).__name__}")


def parse_grid_opacity(
    val: Union[str, float, int, Tuple[float, float], List[float], None],
    has_soft: bool = True,
) -> Tuple[float, float]:
    """
    Parses grid opacity into (soft_alpha, strong_alpha) where 0.0 <= alpha <= 1.0.

    Supported formats:
        - None: defaults to (0.12, 0.30).
        - Single float or int (e.g. 0.3 or "0.3"): strong_alpha = val, soft_alpha = val * 0.4.
        - Pair (e.g. "0.12,0.30" or (0.12, 0.30)): explicit (soft_alpha, strong_alpha).
    """
    if val is None:
        return (0.12, 0.30)

    if isinstance(val, (int, float)):
        v = max(0.0, min(1.0, float(val)))
        return (round(v * 0.4, 3), v) if has_soft else (0.0, v)

    if isinstance(val, (tuple, list)):
        if len(val) == 1:
            return parse_grid_opacity(val[0], has_soft)
        elif len(val) == 2:
            return (max(0.0, min(1.0, float(val[0]))), max(0.0, min(1.0, float(val[1]))))
        raise ValueError(f"Grid opacity tuple/list must have 1 or 2 elements, got {len(val)}")

    if isinstance(val, str):
        s = val.strip()
        if "," in s:
            parts = [float(p.strip()) for p in s.split(",") if p.strip()]
            if len(parts) == 2:
                return (max(0.0, min(1.0, parts[0])), max(0.0, min(1.0, parts[1])))
            elif len(parts) == 1:
                return parse_grid_opacity(parts[0], has_soft)
            raise ValueError(f"Invalid grid opacity: {val!r}")
        return parse_grid_opacity(float(s), has_soft)

    raise TypeError(f"Grid opacity must be string, float, tuple, or list, got {type(val).__name__}")


# ---------------------------------------------------------------------------
# 3.2. Bitmap Font for Overlay Labels (3x5 pixel glyphs)
# ---------------------------------------------------------------------------

FONT_3X5: Dict[str, List[str]] = {
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["111", "001", "111", "100", "111"],
    "3": ["111", "001", "111", "001", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "111", "001", "111"],
    "6": ["111", "100", "111", "101", "111"],
    "7": ["111", "001", "010", "010", "010"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "111"],
    "A": ["111", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["111", "100", "100", "100", "111"],
    "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "G": ["111", "100", "101", "101", "111"],
    "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"],
    "J": ["001", "001", "001", "101", "010"],
    "K": ["101", "110", "100", "110", "101"],
    "L": ["100", "100", "100", "100", "111"],
    "M": ["101", "111", "101", "101", "101"],
    "N": ["111", "101", "101", "101", "101"],
    "O": ["111", "101", "101", "101", "111"],
    "P": ["111", "101", "111", "100", "100"],
    "Q": ["111", "101", "101", "111", "001"],
    "R": ["110", "101", "110", "101", "101"],
    "S": ["111", "100", "111", "001", "111"],
    "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"],
    "V": ["101", "101", "101", "101", "010"],
    "W": ["101", "101", "101", "111", "101"],
    "X": ["101", "101", "010", "101", "101"],
    "Y": ["101", "101", "010", "010", "010"],
    "Z": ["111", "001", "010", "100", "111"],
    "?": ["111", "001", "010", "000", "010"],
    "-": ["000", "000", "111", "000", "000"],
    ":": ["000", "010", "000", "010", "000"],
    ".": ["000", "000", "000", "000", "010"],
    "/": ["001", "001", "010", "100", "100"],
    "\\": ["100", "100", "010", "001", "001"],
    "(": ["010", "100", "100", "100", "010"],
    ")": ["010", "001", "001", "001", "010"],
    "[": ["110", "100", "100", "100", "110"],
    "]": ["011", "001", "001", "001", "011"],
    "^": ["010", "101", "000", "000", "000"],
    "v": ["000", "000", "000", "101", "010"],
    "<": ["001", "010", "100", "010", "001"],
    ">": ["100", "010", "001", "010", "100"],
    "_": ["000", "000", "000", "000", "111"],
    " ": ["000", "000", "000", "000", "000"],
}


def draw_string_3x5(
    buf: bytearray,
    stride_px: int,
    x: int,
    y: int,
    text: str,
    color: RGBA = (255, 255, 255, 255),
    shadow: Optional[RGBA] = (0, 0, 0, 255),
) -> None:
    """Renders text starting at exact pixel (x, y) with optional shadow."""
    cx = x
    for ch in text.upper():
        glyph = FONT_3X5.get(ch, FONT_3X5.get("?", ["111", "001", "010", "000", "010"]))
        if shadow is not None:
            for gy in range(5):
                for gx in range(3):
                    if glyph[gy][gx] == "1":
                        sx, sy = cx + gx + 1, y + gy + 1
                        if 0 <= sx < stride_px:
                            off = (sy * stride_px + sx) * 4
                            if 0 <= off + 3 < len(buf):
                                buf[off] = shadow[0]
                                buf[off + 1] = shadow[1]
                                buf[off + 2] = shadow[2]
                                buf[off + 3] = shadow[3]
        for gy in range(5):
            for gx in range(3):
                if glyph[gy][gx] == "1":
                    sx, sy = cx + gx, y + gy
                    if 0 <= sx < stride_px:
                        off = (sy * stride_px + sx) * 4
                        if 0 <= off + 3 < len(buf):
                            buf[off] = color[0]
                            buf[off + 1] = color[1]
                            buf[off + 2] = color[2]
                            buf[off + 3] = color[3]
        cx += 4



def draw_label_in_rect(
    buf: bytearray,
    stride_px: int,
    height_px: int,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    text: str,
    color: RGBA = (255, 255, 255, 255),
    anchor: str = "top",
) -> None:
    """
    Draws a short index label just inside a corner of a bounding box, nudged so
    it stays on-screen for boxes that start off the map edge.  Used for the
    Section 3 object and trigger indices that cross-reference SoEScriptDumper's
    `script_all` listing.

    `anchor` picks the top-left or bottom-left corner.  Objects use "bottom" and
    triggers "top" so the two stay readable where their boxes coincide -- the
    3x5 font draws 'O' and '0' identically, so an "O5" prefix would be
    ambiguous against a hex trigger id.
    """
    if x2 - x1 < 6 or y2 - y1 < 6:
        return
    text_w = len(text) * 4 - 1
    x = max(2, min(x1 + 3, stride_px - text_w - 2))
    y = y2 - 9 if anchor == "bottom" else y1 + 3
    y = max(2, min(y, height_px - 8))
    draw_string_3x5(buf, stride_px, x, y, text, color=color)


def draw_text_3x5(
    buf: bytearray,
    stride_px: int,
    base_x: int,
    base_y: int,
    text: str,
    text_color: RGBA = (255, 255, 255, 255),
    shadow_color: Optional[RGBA] = (0, 0, 0, 255),
) -> None:
    """
    Renders 1-line or 2-line text centered within a 16x16 metatile box.
    Uses an optional 1px drop shadow (+1, +1) for maximum legibility.
    """
    lines = text.split("\n")
    total_h = len(lines) * 5 + (len(lines) - 1) * 1
    start_y = base_y + max(0, (16 - total_h) // 2)

    # First pass: drop shadow (+1, +1)
    if shadow_color is not None:
        for l_idx, line in enumerate(lines):
            line_w = len(line) * 3 + (len(line) - 1) * 1
            start_x = base_x + max(0, (16 - line_w) // 2)
            cy = start_y + l_idx * 6
            for c_idx, ch in enumerate(line.upper()):
                cx = start_x + c_idx * 4
                glyph = FONT_3X5.get(ch, FONT_3X5["?"])
                for gy in range(5):
                    for gx in range(3):
                        if glyph[gy][gx] == "1":
                            sx = cx + gx + 1
                            sy = cy + gy + 1
                            if 0 <= sx < stride_px and 0 <= sy:
                                off = (sy * stride_px + sx) * 4
                                if off + 3 < len(buf):
                                    buf[off] = shadow_color[0]
                                    buf[off + 1] = shadow_color[1]
                                    buf[off + 2] = shadow_color[2]
                                    buf[off + 3] = shadow_color[3]

    # Second pass: foreground text
    for l_idx, line in enumerate(lines):
        line_w = len(line) * 3 + (len(line) - 1) * 1
        start_x = base_x + max(0, (16 - line_w) // 2)
        cy = start_y + l_idx * 6
        for c_idx, ch in enumerate(line.upper()):
            cx = start_x + c_idx * 4
            glyph = FONT_3X5.get(ch, FONT_3X5["?"])
            for gy in range(5):
                for gx in range(3):
                    if glyph[gy][gx] == "1":
                        px = cx + gx
                        py = cy + gy
                        if 0 <= px < stride_px and 0 <= py:
                            off = (py * stride_px + px) * 4
                            if off + 3 < len(buf):
                                buf[off] = text_color[0]
                                buf[off + 1] = text_color[1]
                                buf[off + 2] = text_color[2]
                                buf[off + 3] = text_color[3]


# ---------------------------------------------------------------------------
# 3.3. ASCII Art Glyphs for Physical Collision Representation (7x7 bitmap)
# ---------------------------------------------------------------------------

GLYPHS_ASCII: Dict[str, List[str]] = {
    "#": [
        "0010100",
        "0010100",
        "1111111",
        "0010100",
        "1111111",
        "0010100",
        "0010100",
    ],
    "/": [
        "0000001",
        "0000010",
        "0000100",
        "0001000",
        "0010000",
        "0100000",
        "1000000",
    ],
    "\\": [
        "1000000",
        "0100000",
        "0010000",
        "0001000",
        "0000100",
        "0000010",
        "0000001",
    ],
    "|": [
        "0001000",
        "0001000",
        "0001000",
        "0001000",
        "0001000",
        "0001000",
        "0001000",
    ],
    "-": [
        "0000000",
        "0000000",
        "0000000",
        "1111111",
        "0000000",
        "0000000",
        "0000000",
    ],
    "D": [
        "1111000",
        "1100110",
        "1100011",
        "1100011",
        "1100011",
        "1100110",
        "1111000",
    ],
    "+": [
        "0001000",
        "0001000",
        "0001000",
        "1111111",
        "0001000",
        "0001000",
        "0001000",
    ],
    "?": [
        "0111100",
        "0000110",
        "0001100",
        "0011000",
        "0011000",
        "0000000",
        "0011000",
    ],
}


def draw_glyph_7x7(
    buf: bytearray,
    stride_px: int,
    base_x: int,
    base_y: int,
    glyph_rows: List[str],
    text_color: RGBA = (255, 255, 255, 255),
    shadow_color: Optional[RGBA] = (0, 0, 0, 255),
) -> None:
    """
    Renders a 7x7 bitmap glyph centered within a 16x16 metatile box.
    Uses a 1px drop shadow (+1, +1) for maximum legibility without distortion.
    """
    gw = len(glyph_rows[0])
    gh = len(glyph_rows)
    cx = base_x + max(0, (16 - gw) // 2)
    cy = base_y + max(0, (16 - gh) // 2)

    # First pass: drop shadow (+1, +1)
    if shadow_color is not None:
        for gy in range(gh):
            for gx in range(gw):
                if glyph_rows[gy][gx] == "1":
                    sx = cx + gx + 1
                    sy = cy + gy + 1
                    if 0 <= sx < stride_px and 0 <= sy:
                        off = (sy * stride_px + sx) * 4
                        if off + 3 < len(buf):
                            buf[off] = shadow_color[0]
                            buf[off + 1] = shadow_color[1]
                            buf[off + 2] = shadow_color[2]
                            buf[off + 3] = shadow_color[3]

    # Second pass: foreground glyph
    for gy in range(gh):
        for gx in range(gw):
            if glyph_rows[gy][gx] == "1":
                px = cx + gx
                py = cy + gy
                if 0 <= px < stride_px and 0 <= py:
                    off = (py * stride_px + px) * 4
                    if off + 3 < len(buf):
                        buf[off] = text_color[0]
                        buf[off + 1] = text_color[1]
                        buf[off + 2] = text_color[2]
                        buf[off + 3] = text_color[3]


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

        ts = int(self.header.get("subscreen_ts", "0x00"), 16)
        bg1_sub = bool(ts & 0x01)
        bg2_sub = bool(ts & 0x02)

        cgadsub = int(self.header.get("color_math_cgadsub", "0x00"), 16)
        sub_math = bool(cgadsub & 0x80)
        half_math = bool(cgadsub & 0x40)
        bg1_math = bool(cgadsub & 0x01)
        bg2_math = bool(cgadsub & 0x02)

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

                        a1 = l1_buf[i + 3]
                        a2 = l2_buf[i + 3]

                        c1 = (l1_buf[i], l1_buf[i + 1], l1_buf[i + 2])
                        c2 = (l2_buf[i], l2_buf[i + 1], l2_buf[i + 2])

                        # 1. Main Screen Layer Selection (Mode 1 priority: BG1 P1 > BG2 P1 > BG1 P0 > BG2 P0)
                        main_layer = None
                        main_color = None
                        if bg1_main and p1 and a1 > 0:
                            main_layer = 1
                            main_color = c1
                        elif bg2_main and p2 and a2 > 0:
                            main_layer = 2
                            main_color = c2
                        elif bg1_main and (not p1) and a1 > 0:
                            main_layer = 1
                            main_color = c1
                        elif bg2_main and (not p2) and a2 > 0:
                            main_layer = 2
                            main_color = c2

                        if main_layer is None:
                            # Backdrop
                            comp[i] = self.backdrop_color[0]
                            comp[i + 1] = self.backdrop_color[1]
                            comp[i + 2] = self.backdrop_color[2]
                            comp[i + 3] = self.backdrop_color[3]
                            continue

                        # 2. Subscreen Layer Selection (from subscreen-enabled layers, excluding main_layer)
                        sub_color = None
                        if bg1_sub and p1 and a1 > 0 and main_layer != 1:
                            sub_color = c1
                        elif bg2_sub and p2 and a2 > 0 and main_layer != 2:
                            sub_color = c2
                        elif bg1_sub and (not p1) and a1 > 0 and main_layer != 1:
                            sub_color = c1
                        elif bg2_sub and (not p2) and a2 > 0 and main_layer != 2:
                            sub_color = c2

                        # 3. Check if color math is enabled for the selected main screen layer
                        math_enabled = (main_layer == 1 and bg1_math) or (main_layer == 2 and bg2_math)

                        if math_enabled and sub_color is not None:
                            if sub_math:
                                comp[i] = max(0, main_color[0] - sub_color[0])
                                comp[i + 1] = max(0, main_color[1] - sub_color[1])
                                comp[i + 2] = max(0, main_color[2] - sub_color[2])
                            elif half_math:
                                comp[i] = (main_color[0] + sub_color[0]) // 2
                                comp[i + 1] = (main_color[1] + sub_color[1]) // 2
                                comp[i + 2] = (main_color[2] + sub_color[2]) // 2
                            else:
                                comp[i] = min(255, main_color[0] + sub_color[0])
                                comp[i + 1] = min(255, main_color[1] + sub_color[1])
                                comp[i + 2] = min(255, main_color[2] + sub_color[2])
                            comp[i + 3] = 255
                        else:
                            comp[i] = main_color[0]
                            comp[i + 1] = main_color[1]
                            comp[i + 2] = main_color[2]
                            comp[i + 3] = 255

        return comp

    def render_collision_overlay(
        self,
        collision_words: List[List[int]],
        base_comp: Optional[bytearray] = None,
        label_mode: Optional[str] = None,
        collision_mode: str = "contour",
        line_color: RGBA = (235, 25, 25, 255),
        solid_tint_alpha: float = 0.30,
    ) -> bytearray:
        """
        Renders collision attribute visualization. If base_comp is provided,
        overlays visualization on top of the composite map.

        Modes:
            - 'contour' / 'line' (default):
                * Crisp red border line between walkable and non-walkable terrain (no gaps).
                * Light red tint for areas that cannot be walked on (walls, obstacles, void).
                * Clean composite graphics for walkable areas (floors, paths, pipes, slides).
            - 'ascii':
                * Grouped physical passability colored tiles with 7x7 ASCII art glyphs (#, /, \\, |, -).
            - 'verbose' / 'raw':
                * Assigns a distinct pastel hue to every unique 16-bit word,
                  labeled with each word's sequential ID (0..N-1) or hex.
        """
        w_px, h_px = self.w_pixels, self.h_pixels
        buf = bytearray(base_comp) if base_comp else bytearray(w_px * h_px * 4)

        if collision_mode in ("contour", "line"):
            # Evaluated for the room's dominant elevation plane, using the
            # engine's own decoder ($909DE8, ported in tools/collision.py).
            # The unified composition layer shows every plane; this one shows
            # the plane most of the room's walkable space belongs to.
            from tools import collision as coll

            planes = coll.planes_used(collision_words)
            ref_plane = max(
                planes,
                key=lambda p: sum(1 for row in collision_words for cw in row
                                  if coll.passability(cw, p) != coll.SOLID),
            )
            solid = bytearray(w_px * h_px)
            for r in range(self.h_tiles):
                base_y = r * 16
                for c in range(self.w_tiles):
                    code = coll.passability(collision_words[r][c], ref_plane)
                    if code == coll.OPEN:
                        continue
                    rows = coll.GEOMETRY_ROWS[code]
                    base_x = c * 16
                    for py in range(16):
                        off = (base_y + py) * w_px + base_x
                        solid[off:off + 16] = rows[py]

            # Find boundary pixels where solid touches walkable
            border = bytearray(w_px * h_px)
            for y in range(h_px):
                y_off = y * w_px
                for x in range(w_px):
                    idx = y_off + x
                    if solid[idx] == 1:
                        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                            ny, nx = y + dy, x + dx
                            if 0 <= ny < h_px and 0 <= nx < w_px:
                                if solid[ny * w_px + nx] == 0:
                                    border[idx] = 1
                                    break

            # 2px thickness dilation for crisp continuous line
            thick_border = bytearray(border)
            for y in range(h_px):
                y_off = y * w_px
                for x in range(w_px):
                    if border[y_off + x] == 1:
                        for dy in (-1, 0, 1):
                            for dx in (-1, 0, 1):
                                ny, nx = y + dy, x + dx
                                if 0 <= ny < h_px and 0 <= nx < w_px:
                                    thick_border[ny * w_px + nx] = 1

            # Render to buffer
            tr, tg, tb = line_color[0], line_color[1], line_color[2]
            inv_tint = 1.0 - solid_tint_alpha
            for y in range(h_px):
                row_off = y * w_px * 4
                for x in range(w_px):
                    idx = y * w_px + x
                    p_off = row_off + x * 4
                    if thick_border[idx] == 1:
                        buf[p_off] = tr
                        buf[p_off + 1] = tg
                        buf[p_off + 2] = tb
                        buf[p_off + 3] = 255
                    elif solid[idx] == 1:
                        if base_comp:
                            buf[p_off] = int(220 * solid_tint_alpha + buf[p_off] * inv_tint)
                            buf[p_off + 1] = int(20 * solid_tint_alpha + buf[p_off + 1] * inv_tint)
                            buf[p_off + 2] = int(20 * solid_tint_alpha + buf[p_off + 2] * inv_tint)
                        else:
                            buf[p_off] = 220
                            buf[p_off + 1] = 20
                            buf[p_off + 2] = 20
                            buf[p_off + 3] = int(255 * solid_tint_alpha)

            return buf

        if collision_mode in ("verbose", "raw"):
            unique_words = sorted(list(set(w for row in collision_words for w in row)))
            color_map: Dict[int, RGBA] = {}
            for idx, cw in enumerate(unique_words):
                if cw == 0:
                    color_map[cw] = (0, 0, 0, 0)
                else:
                    hue = (idx * 360 // max(len(unique_words), 1))
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

            type_map = {w: i for i, w in enumerate(unique_words)}

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

                    if label_mode != "none":
                        if label_mode == "hex":
                            h_str = f"{cw:04X}"
                            label_text = f"{h_str[:2]}\n{h_str[2:]}"
                        else:
                            label_text = str(type_map[cw])
                        draw_text_3x5(buf, self.w_pixels, base_x, base_y, label_text)

            return buf

        # Fallback: 'ascii' physical semantic mode with 7x7 glyphs
        from tools import collision as coll

        for r in range(self.h_tiles):
            for c in range(self.w_tiles):
                cw = collision_words[r][c]
                # The geometry code the engine would use for an entity on this
                # tile's own plane -- bit 13 forces it open, which is what makes
                # pipes, slides and drift walkable (tools/collision.py).
                low = coll.passability(cw, coll.tile_plane(cw))
                base_y = r * 16
                base_x = c * 16

                glyph_char = None
                if low == 0x00:
                    col = (35, 175, 50, 75)     # Walkable Floor / pipe / slide / drift (Soft Green)
                    glyph_char = None
                elif low == 0x0F:
                    col = (210, 35, 35, 160)    # Solid Wall (Red)
                    glyph_char = "#"
                elif low in (0x01, 0x0A, 0x05, 0x0E):
                    col = (255, 140, 0, 180)    # Diagonal Slope / (Orange)
                    glyph_char = "/"
                elif low in (0x02, 0x09, 0x06, 0x0D):
                    col = (255, 140, 0, 180)    # Diagonal Slope \\ (Orange)
                    glyph_char = "\\"
                elif low in (0x07, 0x08):
                    col = (245, 195, 25, 180)   # Vertical Barrier | (Gold)
                    glyph_char = "|"
                elif low in (0x03, 0x0C, 0x04, 0x0B):
                    col = (240, 220, 40, 180)   # Horizontal Barrier - (Yellow)
                    glyph_char = "-"
                else:
                    col = (180, 80, 220, 180)   # Other directional boundary (Purple)
                    glyph_char = "?"

                # Draw cell pixels & border
                for py in range(16):
                    row_offset = (base_y + py) * self.w_pixels * 4
                    for px in range(16):
                        p_off = row_offset + (base_x + px) * 4
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

                if label_mode != "none":
                    if label_mode == "hex":
                        h_str = f"{cw:04X}"
                        draw_text_3x5(buf, self.w_pixels, base_x, base_y, f"{h_str[:2]}\n{h_str[2:]}")
                    elif label_mode == "index":
                        draw_text_3x5(buf, self.w_pixels, base_x, base_y, f"{low:X}")
                    else:  # ascii
                        if glyph_char and glyph_char in GLYPHS_ASCII:
                            draw_glyph_7x7(buf, self.w_pixels, base_x, base_y, GLYPHS_ASCII[glyph_char])

        return buf

    def render_triggers_overlay(self, base_comp: bytearray) -> bytearray:
        """Draws Step-on and B-trigger bounding boxes on top of the composite map."""
        buf = bytearray(base_comp)
        ox = self.header["origin_x"]
        oy = self.header["origin_y"]

        def draw_box(x1, y1, x2, y2, color: RGBA, fill_color: RGBA):
            if x2 < x1:
                x1, x2 = x2, x1
            if y2 < y1:
                y1, y2 = y2, y1
            # Clamp to map bounds
            x1 = max(0, min(x1, self.w_pixels))
            x2 = max(0, min(x2, self.w_pixels))
            y1 = max(0, min(y1, self.h_pixels))
            y2 = max(0, min(y2, self.h_pixels))
            if x1 >= x2 or y1 >= y2:
                return

            for y in range(y1, y2):
                row_off = y * self.w_pixels * 4
                for x in range(x1, x2):
                    p_off = row_off + x * 4
                    is_border = (y == y1 or y == y2 - 1 or x == x1 or x == x2 - 1)
                    draw_c = color if is_border else fill_color
                    a = draw_c[3] / 255.0
                    inv = 1.0 - a
                    a_base = buf[p_off + 3] / 255.0
                    if a_base == 0:
                        buf[p_off] = draw_c[0]
                        buf[p_off + 1] = draw_c[1]
                        buf[p_off + 2] = draw_c[2]
                        buf[p_off + 3] = draw_c[3]
                    elif a_base >= 0.999:
                        buf[p_off] = int(draw_c[0] * a + buf[p_off] * inv)
                        buf[p_off + 1] = int(draw_c[1] * a + buf[p_off + 1] * inv)
                        buf[p_off + 2] = int(draw_c[2] * a + buf[p_off + 2] * inv)
                    else:
                        out_a = a + inv * a_base
                        buf[p_off] = int((draw_c[0] * a + buf[p_off] * inv * a_base) / out_a)
                        buf[p_off + 1] = int((draw_c[1] * a + buf[p_off + 1] * inv * a_base) / out_a)
                        buf[p_off + 2] = int((draw_c[2] * a + buf[p_off + 2] * inv * a_base) / out_a)
                        buf[p_off + 3] = int(out_a * 255)

        # 1. B-triggers (Yellow, matching soestuff.lua 0xffff00: outline 0xFFFFFF00, fill 0x77FFFF00)
        for t in self.room_data["triggers"]["b_trigger"]:
            px1 = (t["x1"] - ox) * 16
            py1 = (t["y1"] - oy) * 16
            px2 = (t["x2"] - ox) * 16
            py2 = (t["y2"] - oy) * 16
            draw_box(px1, py1, px2, py2, color=(255, 255, 0, 255), fill_color=(255, 255, 0, 119))
            draw_label_in_rect(buf, self.w_pixels, self.h_pixels, px1, py1, px2, py2,
                               f"{t['script_id']:X}", (255, 255, 140, 255))

        # 2. Step-on triggers (Pink / Magenta, matching soestuff.lua 0xff00ff: outline 0xFFFF00FF, fill 0x77FF00FF)
        for t in self.room_data["triggers"]["step_on"]:
            px1 = (t["x1"] - ox) * 16
            py1 = (t["y1"] - oy) * 16
            px2 = (t["x2"] - ox) * 16
            py2 = (t["y2"] - oy) * 16
            draw_box(px1, py1, px2, py2, color=(255, 0, 255, 255), fill_color=(255, 0, 255, 119))
            draw_label_in_rect(buf, self.w_pixels, self.h_pixels, px1, py1, px2, py2,
                               f"{t['script_id']:X}", (255, 160, 255, 255))

        return buf

    def render_grid_overlay(
        self,
        base_buf: bytearray,
        spec: Union[str, int, Tuple[int, int]] = "8,16",
        color: Union[str, RGBA] = "white",
        opacity: Optional[Union[str, float, Tuple[float, float]]] = None,
    ) -> bytearray:
        """
        Renders a subtle grid overlay on top of base_buf (typically composite map):
        - Sub-tile soft grid (default: 8px, alpha ~ 0.12)
        - Metatile strong grid (default: 16px, alpha ~ 0.30)
        - Configurable step sizes, color, and opacities
        """
        soft_step, strong_step = parse_grid_spec(spec)
        has_soft = soft_step > 0
        soft_a, strong_a = parse_grid_opacity(opacity, has_soft=has_soft)
        parsed_c = parse_color(color) if not isinstance(color, tuple) else color
        cr, cg, cb = parsed_c[0], parsed_c[1], parsed_c[2]

        out = bytearray(base_buf)
        w_px, h_px = self.w_pixels, self.h_pixels
        inv_str = 1.0 - strong_a
        inv_sft = 1.0 - soft_a

        for y in range(h_px):
            row_off = y * w_px * 4
            if strong_step > 0 and y % strong_step == 0:
                # Entire horizontal line is strong
                for x in range(w_px):
                    idx = row_off + x * 4
                    a_base = out[idx + 3] / 255.0
                    if a_base == 0:
                        out[idx] = cr
                        out[idx + 1] = cg
                        out[idx + 2] = cb
                        out[idx + 3] = int(255 * strong_a)
                    elif a_base >= 0.999:
                        out[idx] = int(cr * strong_a + out[idx] * inv_str)
                        out[idx + 1] = int(cg * strong_a + out[idx + 1] * inv_str)
                        out[idx + 2] = int(cb * strong_a + out[idx + 2] * inv_str)
                    else:
                        out_a = strong_a + inv_str * a_base
                        out[idx] = int((cr * strong_a + out[idx] * inv_str * a_base) / out_a)
                        out[idx + 1] = int((cg * strong_a + out[idx + 1] * inv_str * a_base) / out_a)
                        out[idx + 2] = int((cb * strong_a + out[idx + 2] * inv_str * a_base) / out_a)
                        out[idx + 3] = int(out_a * 255)
            elif soft_step > 0 and y % soft_step == 0:
                # Horizontal line is soft, with strong intersections at metatile columns
                for x in range(w_px):
                    a = strong_a if (strong_step > 0 and x % strong_step == 0) else soft_a
                    inv = 1.0 - a
                    idx = row_off + x * 4
                    a_base = out[idx + 3] / 255.0
                    if a_base == 0:
                        out[idx] = cr
                        out[idx + 1] = cg
                        out[idx + 2] = cb
                        out[idx + 3] = int(255 * a)
                    elif a_base >= 0.999:
                        out[idx] = int(cr * a + out[idx] * inv)
                        out[idx + 1] = int(cg * a + out[idx + 1] * inv)
                        out[idx + 2] = int(cb * a + out[idx + 2] * inv)
                    else:
                        out_a = a + inv * a_base
                        out[idx] = int((cr * a + out[idx] * inv * a_base) / out_a)
                        out[idx + 1] = int((cg * a + out[idx + 1] * inv * a_base) / out_a)
                        out[idx + 2] = int((cb * a + out[idx + 2] * inv * a_base) / out_a)
                        out[idx + 3] = int(out_a * 255)
            else:
                # Vertical grid lines across this non-grid row
                if strong_step > 0:
                    for x in range(0, w_px, strong_step):
                        idx = row_off + x * 4
                        a_base = out[idx + 3] / 255.0
                        if a_base == 0:
                            out[idx] = cr
                            out[idx + 1] = cg
                            out[idx + 2] = cb
                            out[idx + 3] = int(255 * strong_a)
                        elif a_base >= 0.999:
                            out[idx] = int(cr * strong_a + out[idx] * inv_str)
                            out[idx + 1] = int(cg * strong_a + out[idx + 1] * inv_str)
                            out[idx + 2] = int(cb * strong_a + out[idx + 2] * inv_str)
                        else:
                            out_a = strong_a + inv_str * a_base
                            out[idx] = int((cr * strong_a + out[idx] * inv_str * a_base) / out_a)
                            out[idx + 1] = int((cg * strong_a + out[idx + 1] * inv_str * a_base) / out_a)
                            out[idx + 2] = int((cb * strong_a + out[idx + 2] * inv_str * a_base) / out_a)
                            out[idx + 3] = int(out_a * 255)
                if soft_step > 0:
                    for x in range(0, w_px, soft_step):
                        if strong_step > 0 and x % strong_step == 0:
                            continue
                        idx = row_off + x * 4
                        a_base = out[idx + 3] / 255.0
                        if a_base == 0:
                            out[idx] = cr
                            out[idx + 1] = cg
                            out[idx + 2] = cb
                            out[idx + 3] = int(255 * soft_a)
                        elif a_base >= 0.999:
                            out[idx] = int(cr * soft_a + out[idx] * inv_sft)
                            out[idx + 1] = int(cg * soft_a + out[idx + 1] * inv_sft)
                            out[idx + 2] = int(cb * soft_a + out[idx + 2] * inv_sft)
                        else:
                            out_a = soft_a + inv_sft * a_base
                            out[idx] = int((cr * soft_a + out[idx] * inv_sft * a_base) / out_a)
                            out[idx + 1] = int((cg * soft_a + out[idx + 1] * inv_sft * a_base) / out_a)
                            out[idx + 2] = int((cb * soft_a + out[idx + 2] * inv_sft * a_base) / out_a)
                            out[idx + 3] = int(out_a * 255)

        return out

    def render_full_composition(
        self,
        base_comp: bytearray,
        add_legend: bool = True,
    ) -> Tuple[bytearray, int, int]:
        """
        Renders one image carrying every piece of room information:

        1. Base visuals (Layer 2 terrain + Layer 1 canopy).
        2. Per-elevation-plane passability contours.  The engine evaluates
           collision relative to the plane the entity is standing on, so a room
           with bridges or tunnels has a different walkable map per plane
           (tools/collision.py).  Each plane gets its own colour; the room's
           dominant plane is a solid 2px line and the others are dotted, so
           overlapping levels read as crossing outlines rather than one blob.
        3. Soft tint on the dominant plane's solid walls and void.
        4. Forced-walkable tiles (collision bit 13) -- sewer pipes, volcano
           slides, desert drift.  Deliberately no direction arrows: the sliding
           direction comes from the entity's own facing, not from the map.
        5. Plane-transparent tiles (collision bit 6) -- bridge and overpass
           tiles you walk straight through while on another plane.
        6. Elevation-change tiles, where crossing swaps your plane.
        7. Entity-gated tiles (collision bit 8) -- solid for the boy, for the
           dog, or for everything except them.
        8. Cuttable grass (tools/cuttable_grass.py).
        9. Section 3 object stamps and trigger boxes, labelled with the indices
           SoEScriptDumper's `script_all` uses.
        10. Optional header banner and bottom legend.

        Nothing here keys off the room id or a hand-built word list; every
        classification is a documented bitfield of the collision word.
        """
        w_px = self.w_pixels
        h_px = self.h_pixels
        w_tiles = self.w_tiles
        h_tiles = self.h_tiles
        cw_grid = self.room_data["collision_int_words"]
        rid = self.room_data.get("room_id")

        from tools import collision as coll

        ox = self.header["origin_x"]
        oy = self.header["origin_y"]

        # 1. Cuttable grass: a temporary barrier, not map geometry, so it is
        #    excluded from every plane's contour (see tools/cuttable_grass.py).
        from tools.cuttable_grass import find_cuttable_grass_tiles
        cuttable_tiles: Set[Tuple[int, int]] = find_cuttable_grass_tiles(self.room_data)

        grass_px = bytearray(w_px * h_px)
        for (tx, ty) in cuttable_tiles:
            for py in range(16):
                row_off = (ty * 16 + py) * w_px + tx * 16
                grass_px[row_off:row_off + 16] = b"\x01" * 16

        # 2. Per-plane solid masks, evaluated exactly as $909DE8 would for an
        #    entity standing on that plane.
        planes = coll.planes_used(cw_grid)
        plane_solid: Dict[int, bytearray] = {}
        plane_walkable: Dict[int, int] = {}
        for p in planes:
            mask = bytearray(w_px * h_px)
            walkable = 0
            for r in range(h_tiles):
                base_y = r * 16
                row = cw_grid[r]
                for c in range(w_tiles):
                    code = coll.passability(row[c], p)
                    if code != coll.SOLID:
                        walkable += 1
                    if code == coll.OPEN:
                        continue
                    rows = coll.GEOMETRY_ROWS[code]
                    base_x = c * 16
                    for py in range(16):
                        off = (base_y + py) * w_px + base_x
                        mask[off:off + 16] = rows[py]
            plane_solid[p] = mask
            plane_walkable[p] = walkable

        main_plane = max(planes, key=lambda p: plane_walkable[p])
        solid = plane_solid[main_plane]

        # 3. Special-terrain sets, all straight out of the collision bits.
        forced_walk_tiles: Set[Tuple[int, int]] = set()
        transparent_tiles: Set[Tuple[int, int]] = set()
        gated_tiles: Dict[Tuple[int, int], int] = {}
        for r in range(h_tiles):
            for c in range(w_tiles):
                cw = cw_grid[r][c]
                if coll.is_always_walkable(cw):
                    forced_walk_tiles.add((c, r))
                if coll.is_plane_transparent(cw):
                    transparent_tiles.add((c, r))
                gate = coll.entity_gate(cw)
                if gate in coll.GATE_BLOCKS:
                    gated_tiles[(c, r)] = gate
        transition_tiles = coll.plane_transition_tiles(cw_grid)

        # 4. Object footprints.  Section 3 objects are a separate mechanism
        #    from terrain collision and are all drawn.
        object_rects: List[Tuple[int, int, int, int, int]] = []
        for obj in self.room_data.get("objects", []):
            oid = obj["object_index"]
            for s in obj.get("states", []):
                tx, ty = s["tile_x"], s["tile_y"]
                w = max(s.get("target_width", s.get("width", 1)), 1)
                h = max(s.get("target_height", 1), 1)
                object_rects.append((tx, ty, w, h, oid))

        # 5. Contour each plane.  Cuttable grass is transparent to all of them.
        def contour(mask: bytearray) -> bytearray:
            edge = bytearray(w_px * h_px)
            for y in range(h_px):
                y_off = y * w_px
                for x in range(w_px):
                    idx = y_off + x
                    if mask[idx] != 1 or grass_px[idx]:
                        continue
                    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h_px and 0 <= nx < w_px:
                            n_idx = ny * w_px + nx
                            if mask[n_idx] == 0 and grass_px[n_idx] == 0:
                                edge[idx] = 1
                                break
            thick = bytearray(edge)
            for y in range(h_px):
                y_off = y * w_px
                for x in range(w_px):
                    if edge[y_off + x] == 1:
                        for dy in (-1, 0, 1):
                            for dx in (-1, 0, 1):
                                ny, nx = y + dy, x + dx
                                if 0 <= ny < h_px and 0 <= nx < w_px:
                                    thick[ny * w_px + nx] = 1
            return thick

        plane_border: Dict[int, bytearray] = {p: contour(plane_solid[p]) for p in planes}
        thick_border = plane_border[main_plane]

        # 6. Output buffer + legend
        legend_items: List[Tuple[Tuple[int, int, int], str]] = []
        for p in planes:
            suffix = "" if p == main_plane else " (DOTTED)"
            legend_items.append((PLANE_COLORS[p], f"PLANE {p} BOUNDARY{suffix}"))
        if forced_walk_tiles:
            legend_items.append(((0, 188, 212), "DRIFT / FORCED WALKABLE (BIT 13, ARROW = DIRECTION)"))
        if transparent_tiles:
            legend_items.append(((156, 39, 176), "PLANE-TRANSPARENT (BIT 6)"))
        if transition_tiles:
            legend_items.append(((255, 152, 0), "ELEVATION CHANGE"))
        if gated_tiles:
            legend_items.append(((235, 235, 235), "ENTITY GATE (BIT 8)"))
        if cuttable_tiles:
            legend_items.append(((76, 175, 80), "CUTTABLE GRASS"))
        legend_items += [
            ((33, 150, 243), "OBJECT STAMP (N BOTTOM-LEFT = SCRIPT_ALL OBJ N)"),
            ((255, 255, 0), "B-TRIGGER (HEX TOP-LEFT = SCRIPT_ALL ID)"),
            ((255, 0, 255), "STEP-ON (HEX TOP-LEFT = SCRIPT_ALL ID)"),
        ]
        legend_rows: List[List[Tuple[Tuple[int, int, int], str]]] = []
        if add_legend:
            cur_row: List[Tuple[Tuple[int, int, int], str]] = []
            cur_w = 12
            for col, text in legend_items:
                item_w = 14 + len(text) * 4 + 14
                if cur_row and cur_w + item_w > w_px - 8:
                    legend_rows.append(cur_row)
                    cur_row = [(col, text)]
                    cur_w = 12 + item_w
                else:
                    cur_row.append((col, text))
                    cur_w += item_w
            if cur_row:
                legend_rows.append(cur_row)
            banner_h = 36 if len(legend_rows) <= 1 else (10 + len(legend_rows) * 18)
            out_h = h_px + banner_h
        else:
            banner_h = 0
            out_h = h_px
        buf = bytearray(w_px * out_h * 4)
        buf[:len(base_comp)] = base_comp

        def blend_pixel(x: int, y: int, r: int, g: int, b: int, alpha: float):
            if not (0 <= x < w_px and 0 <= y < h_px):
                return
            p_off = (y * w_px + x) * 4
            inv = 1.0 - alpha
            buf[p_off] = int(r * alpha + buf[p_off] * inv)
            buf[p_off + 1] = int(g * alpha + buf[p_off + 1] * inv)
            buf[p_off + 2] = int(b * alpha + buf[p_off + 2] * inv)
            buf[p_off + 3] = 255

        # 7. Solid tint for the dominant plane, then the plane contours.
        #    Secondary planes are dashed so crossings stay readable.
        main_r, main_g, main_b = PLANE_COLORS[main_plane]
        for idx in range(w_px * h_px):
            if solid[idx] == 1 and grass_px[idx] == 0 and thick_border[idx] == 0:
                y, x = divmod(idx, w_px)
                blend_pixel(x, y, 220, 20, 20, 0.20)

        for idx in range(w_px * h_px):
            if thick_border[idx] == 1:
                p_off = idx * 4
                buf[p_off] = main_r
                buf[p_off + 1] = main_g
                buf[p_off + 2] = main_b
                buf[p_off + 3] = 255

        # Secondary planes ride on top as dashes, so where two planes share a
        # boundary you see the dash pattern over the solid line, and where they
        # differ (a tunnel under a bridge) the two outlines cross.
        for p in planes:
            if p == main_plane:
                continue
            pr, pg, pb = PLANE_COLORS[p]
            border = plane_border[p]
            for idx in range(w_px * h_px):
                if border[idx] == 0:
                    continue
                y, x = divmod(idx, w_px)
                if ((x + y) // 3) % 2:
                    continue
                p_off = idx * 4
                buf[p_off] = pr
                buf[p_off + 1] = pg
                buf[p_off + 2] = pb
                buf[p_off + 3] = 255

        # 8. Forced-walkable tiles (bit 13): cyan wash, plus a drift arrow where
        #    the low nibble carries one.  Under bit 13 the low nibble is not
        #    geometry -- it indexes the direction jump table at $8FAF28 (see
        #    tools/collision.py).
        def draw_arrow(bx: int, by: int, dx: int, dy: int, double: bool = False):
            sx = (dx > 0) - (dx < 0)
            sy = (dy > 0) - (dy < 0)
            # Shaft from one edge of the tile to the other through the centre.
            for t in range(-5, 6):
                blend_pixel(bx + 8 + sx * t, by + 8 + sy * t, 255, 255, 255, 0.95)
            heads = (1, -1) if double else (1,)
            for hs in heads:
                tipx, tipy = bx + 8 + sx * 5 * hs, by + 8 + sy * 5 * hs
                # Two barbs, perpendicular-ish, stepped back along the shaft.
                for k in (1, 2, 3):
                    back_x, back_y = tipx - sx * k * hs, tipy - sy * k * hs
                    if sx and sy:        # diagonal: barbs along each axis
                        blend_pixel(back_x - sx * k, back_y, 255, 255, 255, 0.95)
                        blend_pixel(back_x, back_y - sy * k, 255, 255, 255, 0.95)
                    elif sx:             # horizontal: barbs vertically
                        blend_pixel(back_x, back_y - k, 255, 255, 255, 0.95)
                        blend_pixel(back_x, back_y + k, 255, 255, 255, 0.95)
                    else:                # vertical: barbs horizontally
                        blend_pixel(back_x - k, back_y, 255, 255, 255, 0.95)
                        blend_pixel(back_x + k, back_y, 255, 255, 255, 0.95)

        for (tc, tr) in forced_walk_tiles:
            bx, by = tc * 16, tr * 16
            for py in range(16):
                for px in range(16):
                    blend_pixel(bx + px, by + py, 0, 188, 212, 0.34)
            ddx, ddy, dname = coll.drift_vector(cw_grid[tr][tc])
            if dname.startswith("SHEAR"):
                # Direction depends on the entity's own motion, not the map, so
                # draw a double-headed diagonal instead of a single arrow.
                sign = 1 if dname.endswith("+") else -1
                draw_arrow(bx, by, 1, -sign, double=True)
            elif dname:
                draw_arrow(bx, by, ddx, ddy)

        # 9. Plane-transparent tiles (bit 6): purple wash.
        for (tc, tr) in transparent_tiles:
            bx, by = tc * 16, tr * 16
            for py in range(16):
                for px in range(16):
                    blend_pixel(bx + px, by + py, 156, 39, 176, 0.30)

        # 9b. Elevation-change tiles: amber wash + step rungs.
        for (tc, tr) in transition_tiles:
            bx, by = tc * 16, tr * 16
            for py in range(16):
                for px in range(16):
                    if py in (3, 7, 11, 15) and 2 <= px <= 13:
                        blend_pixel(bx + px, by + py, 255, 220, 50, 0.90)
                    else:
                        blend_pixel(bx + px, by + py, 255, 152, 0, 0.34)

        # 9c. Entity-gated tiles (bit 8): dashed light border + gate digit.
        for (tc, tr), gate in gated_tiles.items():
            bx, by = tc * 16, tr * 16
            for i in range(16):
                if i % 4 < 2:
                    blend_pixel(bx + i, by, 235, 235, 235, 0.95)
                    blend_pixel(bx + i, by + 15, 235, 235, 235, 0.95)
                    blend_pixel(bx, by + i, 235, 235, 235, 0.95)
                    blend_pixel(bx + 15, by + i, 235, 235, 235, 0.95)

        # 9d. Object stamps -> soft blue tint + 1px perimeter.
        # Index labels are collected here and drawn last, so later passes
        # cannot paint over them.  Text matches SoEScriptDumper's `script_all`:
        # objects are "UNLOAD OBJ <n>" there, triggers are "(id:<hex>)".
        index_labels: List[Tuple[int, int, int, int, str, RGBA, str]] = []
        for tx, ty, w, h, oid in object_rects:
            x1, y1 = tx * 16, ty * 16
            x2, y2 = (tx + w) * 16 - 1, (ty + h) * 16 - 1
            for y in range(y1, y2 + 1):
                for x in range(x1, x2 + 1):
                    if 0 <= y < h_px and 0 <= x < w_px:
                        if y in (y1, y2) or x in (x1, x2):
                            blend_pixel(x, y, 33, 150, 243, 0.90)
                        else:
                            blend_pixel(x, y, 33, 150, 243, 0.32)
            index_labels.append((x1, y1, x2, y2, str(oid), (150, 210, 255, 255), "bottom"))

        # 10. Cuttable Grass -> soft green fill + continuous 2px green contour,
        #     drawn in the same outlined-box style as the red wall boundary.
        #     Adjacent grass tiles merge into a single outline.
        g_edge: List[int] = []
        for (tc, tr) in cuttable_tiles:
            bx, by = tc * 16, tr * 16
            for py in range(16):
                y = by + py
                for px in range(16):
                    x = bx + px
                    for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
                        ny, nx = y + dy, x + dx
                        if not (0 <= ny < h_px and 0 <= nx < w_px) or grass_px[ny * w_px + nx] == 0:
                            g_edge.append(y * w_px + x)
                            break

        thick_g = bytearray(w_px * h_px)
        thick_g_idx: List[int] = []
        for idx in g_edge:
            y, x = divmod(idx, w_px)
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    ny, nx = y + dy, x + dx
                    if 0 <= ny < h_px and 0 <= nx < w_px:
                        n_idx = ny * w_px + nx
                        if thick_g[n_idx] == 0:
                            thick_g[n_idx] = 1
                            thick_g_idx.append(n_idx)

        for (tc, tr) in cuttable_tiles:
            bx, by = tc * 16, tr * 16
            for py in range(16):
                y = by + py
                for px in range(16):
                    x = bx + px
                    if thick_g[y * w_px + x] == 0:
                        blend_pixel(x, y, 76, 175, 80, 0.28)
        for idx in thick_g_idx:
            p_off = idx * 4
            buf[p_off] = 60
            buf[p_off + 1] = 225
            buf[p_off + 2] = 70
            buf[p_off + 3] = 255

        # 11. Triggers Overlay
        def draw_box(x1, y1, x2, y2, color, fill_color):
            if x2 < x1: x1, x2 = x2, x1
            if y2 < y1: y1, y2 = y2, y1
            x1, x2 = max(0, min(x1, w_px)), max(0, min(x2, w_px))
            y1, y2 = max(0, min(y1, h_px)), max(0, min(y2, h_px))
            for y in range(y1, y2):
                for x in range(x1, x2):
                    is_border = (y == y1 or y == y2 - 1 or x == x1 or x == x2 - 1)
                    c = color if is_border else fill_color
                    blend_pixel(x, y, c[0], c[1], c[2], c[3] / 255.0)

        for t in self.room_data["triggers"]["b_trigger"]:
            px1 = (t["x1"] - ox) * 16
            py1 = (t["y1"] - oy) * 16
            px2 = (t["x2"] - ox) * 16
            py2 = (t["y2"] - oy) * 16
            draw_box(px1, py1, px2, py2, color=(255, 255, 0, 255), fill_color=(255, 255, 0, 85))
            index_labels.append((px1, py1, px2, py2, f"{t['script_id']:X}", (255, 255, 140, 255), "top"))

        for t in self.room_data["triggers"]["step_on"]:
            px1 = (t["x1"] - ox) * 16
            py1 = (t["y1"] - oy) * 16
            px2 = (t["x2"] - ox) * 16
            py2 = (t["y2"] - oy) * 16
            draw_box(px1, py1, px2, py2, color=(255, 0, 255, 255), fill_color=(255, 0, 255, 85))
            index_labels.append((px1, py1, px2, py2, f"{t['script_id']:X}", (255, 160, 255, 255), "top"))

        # 11b. Index labels (drawn last so nothing paints over them)
        for lx1, ly1, lx2, ly2, text, lcolor, anchor in index_labels:
            draw_label_in_rect(buf, w_px, h_px, lx1, ly1, lx2, ly2, text, lcolor, anchor)

        # 12. Legend Banner
        if add_legend:
            banner_y = h_px
            for y in range(banner_y, out_h):
                for x in range(w_px):
                    off = (y * w_px + x) * 4
                    buf[off] = 20
                    buf[off + 1] = 24
                    buf[off + 2] = 30
                    buf[off + 3] = 255

            for r_idx, row in enumerate(legend_rows):
                cur_x = 12
                row_y = banner_y + 11 if len(legend_rows) <= 1 else (banner_y + 8 + r_idx * 18)
                for col, text in row:
                    box_y = row_y + 2
                    for by in range(10):
                        for bx in range(10):
                            if 0 <= cur_x + bx < w_px and 0 <= box_y + by < out_h:
                                is_b = (by == 0 or by == 9 or bx == 0 or bx == 9)
                                c = (255, 255, 255) if is_b else col
                                off = ((box_y + by) * w_px + (cur_x + bx)) * 4
                                buf[off] = c[0]
                                buf[off + 1] = c[1]
                                buf[off + 2] = c[2]
                                buf[off + 3] = 255
                    draw_string_3x5(buf, w_px, cur_x + 14, row_y + 5, text)
                    cur_x += 14 + len(text) * 4 + 14

        if not add_legend:
            return buf, w_px, out_h

        # 13. Header banner (room summary, prepended above the map)
        b_trig = self.room_data.get("triggers", {}).get("b_trigger", [])
        step_on = self.room_data.get("triggers", {}).get("step_on", [])
        segments = [
            f"ROOM 0x{rid:02X}" if rid is not None else "ROOM ?",
            f"{w_tiles}X{h_tiles} TILES",
            "PLANES " + ",".join(str(p) for p in planes),
            f"OBJECTS {len(self.room_data.get('objects', []))}",
            f"B-TRIGGERS {len(b_trig)}",
            f"STEP-ON {len(step_on)}",
            f"CUTTABLE GRASS {len(cuttable_tiles)}",
        ]
        if forced_walk_tiles:
            segments.append(f"FORCED WALKABLE {len(forced_walk_tiles)}")
        if transparent_tiles:
            segments.append(f"PLANE-TRANSPARENT {len(transparent_tiles)}")
        if transition_tiles:
            segments.append(f"ELEV CHANGE {len(transition_tiles)}")
        if gated_tiles:
            segments.append(f"ENTITY GATES {len(gated_tiles)}")
        header_lines: List[str] = []
        cur = ""
        for seg in segments:
            candidate = seg if not cur else f"{cur}  -  {seg}"
            if cur and 12 + len(candidate) * 4 > w_px - 8:
                header_lines.append(cur)
                cur = seg
            else:
                cur = candidate
        if cur:
            header_lines.append(cur)

        header_h = 8 + len(header_lines) * 10
        final_h = out_h + header_h
        out = bytearray(w_px * final_h * 4)
        for i in range(w_px * header_h):
            o = i * 4
            out[o] = 20
            out[o + 1] = 24
            out[o + 2] = 30
            out[o + 3] = 255
        out[w_px * header_h * 4:] = buf
        for i, line in enumerate(header_lines):
            draw_string_3x5(out, w_px, 12, 4 + i * 10, line)

        return out, w_px, final_h



def render_room_layers(
    room_id: int,
    rom_path: str = DEFAULT_ROM_PATH,
    out_dir: str = "out/maps",
    layers: Optional[List[str]] = None,
    with_collision: bool = False,
    with_triggers: bool = False,
    with_grid: bool = False,
    with_composition: bool = False,
    with_legend: bool = True,
    grid_spec: Union[str, int, Tuple[int, int]] = "8,16",
    grid_color: Union[str, RGBA] = "white",
    grid_opacity: Optional[Union[str, float, Tuple[float, float]]] = None,
    bg_color: Union[str, RGBA] = "black",
    collision_label: Optional[str] = None,
    collision_mode: str = "contour",
) -> Dict[str, str]:
    """
    Renders all layers for a given room ID and saves them as PNG files.

    Args:
        room_id:        Room ID (0..126).
        rom_path:       Path to Secret of Evermore (U) ROM file.
        out_dir:        Destination directory for output PNG files.
        layers:         List of layers to generate: '1', '2', 'composite', 'collision', 'triggers', 'grid', 'composition'.
                        Defaults to ['1', '2', 'composite'].
        with_collision:   If True, also renders collision layer.
        with_triggers:    If True, also renders triggers overlay.
        with_grid:        If True, also renders subtle tile grid overlay on composite.
        with_composition: If True, also renders unified composition graphic.
        with_legend:      If True (default), appends bottom legend banner on composition graphics.
        grid_spec:      Grid step size: "8,16" (default), 16, or (soft, strong).
        grid_color:     Grid line color (default: 'white').
        grid_opacity:   Grid line opacity: "soft,strong" e.g. "0.12,0.30" or single float.
        bg_color:       Backdrop color for composite: 'black' (default), 'transparent',
                        'cgram', hex string (#RRGGBB / #RRGGBBAA), or RGBA tuple.
        collision_label: Label style on collision tiles: 'ascii' (for ascii mode),
                         'index' (0, 1, 2... for verbose mode), 'hex', or 'none'.
        collision_mode:  Collision style: 'contour' / 'line' (default, continuous red boundary line with
                         light red solid tint), 'ascii' / 'passability' (semantic physical groups with ASCII art),
                         or 'verbose' / 'raw' (distinct color for each unique 16-bit word).

    Returns:
        Dictionary mapping layer name to output PNG file path.
    """
    if collision_label is None:
        if collision_mode in ("verbose", "raw"):
            collision_label = "index"
        elif collision_mode in ("ascii", "passability"):
            collision_label = "ascii"
        else:
            collision_label = "none"
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
    if with_grid:
        selected_layers.add("grid")
    if with_composition:
        selected_layers.add("composition")


    l1_buf: Optional[bytearray] = None
    l2_buf: Optional[bytearray] = None
    comp_buf: Optional[bytearray] = None

    # Render Layer 1 (Canopy)
    if "1" in selected_layers or "composite" in selected_layers or "triggers" in selected_layers or "collision" in selected_layers or "grid" in selected_layers or "composition" in selected_layers:
        l1_buf = renderer.render_vram_layer(room_data["layer1_vram_int_words"])
        if "1" in selected_layers:
            path_l1 = os.path.join(out_dir, f"{prefix}_layer1.png")
            save_png(l1_buf, renderer.w_pixels, renderer.h_pixels, path_l1)
            output_files["layer1"] = path_l1

    # Render Layer 2 (Terrain)
    if "2" in selected_layers or "composite" in selected_layers or "triggers" in selected_layers or "collision" in selected_layers or "grid" in selected_layers or "composition" in selected_layers:
        l2_buf = renderer.render_vram_layer(room_data["layer2_vram_int_words"])
        if "2" in selected_layers:
            path_l2 = os.path.join(out_dir, f"{prefix}_layer2.png")
            save_png(l2_buf, renderer.w_pixels, renderer.h_pixels, path_l2)
            output_files["layer2"] = path_l2

    # Render Composite (Layer 2 + Layer 1)
    if "composite" in selected_layers or "triggers" in selected_layers or "collision" in selected_layers or "grid" in selected_layers or "composition" in selected_layers:
        assert l1_buf is not None and l2_buf is not None
        comp_buf = renderer.composite_layers(l2_buf, l1_buf)
        if "composite" in selected_layers:
            path_comp = os.path.join(out_dir, f"{prefix}_composite.png")
            save_png(comp_buf, renderer.w_pixels, renderer.h_pixels, path_comp)
            output_files["composite"] = path_comp

    # Render Collision
    if "collision" in selected_layers:
        coll_buf = renderer.render_collision_overlay(
            room_data["collision_int_words"],
            base_comp=comp_buf,
            label_mode=collision_label,
            collision_mode=collision_mode,
        )
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

    # Render Grid Overlay
    if "grid" in selected_layers:
        assert comp_buf is not None
        grid_buf = renderer.render_grid_overlay(
            comp_buf,
            spec=grid_spec,
            color=grid_color,
            opacity=grid_opacity,
        )
        path_grid = os.path.join(out_dir, f"{prefix}_grid.png")
        save_png(grid_buf, renderer.w_pixels, renderer.h_pixels, path_grid)
        output_files["grid"] = path_grid

    # Render Unified Composition Overlay
    if "composition" in selected_layers:
        assert comp_buf is not None
        comp_overlay, w_final, h_final = renderer.render_full_composition(comp_buf, add_legend=with_legend)
        path_composition = os.path.join(out_dir, f"{prefix}_composition.png")
        save_png(comp_overlay, w_final, h_final, path_composition)
        output_files["composition"] = path_composition

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
        choices=["1", "2", "composite", "all", "collision", "triggers", "grid", "composition"],
        default="all",
        help="Layer to render: 1, 2, composite, collision, triggers, grid, composition, or all (default: all)",
    )
    parser.add_argument("--collision", action="store_true", help="Include collision visualization layer")
    parser.add_argument("--triggers", action="store_true", help="Include triggers overlay on composite")
    parser.add_argument("--composition", action="store_true", help="Include unified composition overlay with all features")
    parser.add_argument("--no-legend", action="store_true", help="Omit bottom legend banner on composition graphics")
    parser.add_argument(
        "--grid",
        nargs="?",
        const="8,16",
        default=None,
        help="Include tile grid overlay (default: 8,16 for 8px soft & 16px strong; or specify step e.g. 16 or 8,16)",
    )
    parser.add_argument(
        "--grid-color",
        default="white",
        help="Grid line color: 'white' (default), 'black', hex (#RRGGBB), etc.",
    )
    parser.add_argument(
        "--grid-opacity",
        default=None,
        help="Grid line opacity: 'soft,strong' e.g. '0.12,0.30' or single float (default: 0.12,0.30)",
    )
    parser.add_argument(
        "--bg-color",
        "--background",
        default="black",
        help="Backdrop color: 'black' (default), 'transparent', 'cgram', hex (#RRGGBB or #RRGGBBAA), or R,G,B (default: black)",
    )
    parser.add_argument(
        "--collision-label",
        choices=["ascii", "index", "hex", "none"],
        default=None,
        help="Label style on collision tiles: 'ascii' (for ascii mode), 'index' (0, 1, 2... for verbose mode), 'hex' (4-digit hex), or 'none'",
    )
    parser.add_argument(
        "--collision-mode",
        choices=["contour", "line", "ascii", "passability", "verbose", "raw"],
        default="contour",
        help="Collision style: 'contour'/'line' (default, continuous red boundary line with light red solid tint), 'ascii'/'passability' (physical groups with ASCII art), or 'verbose'/'raw' (word palette with unique colors and IDs)",
    )
    parser.add_argument(
        "--collision-verbose",
        action="store_true",
        help="Secondary command shortcut: view verbose collision words with unique colors and IDs",
    )
    parser.add_argument("--all-rooms", action="store_true", help="Render all 127 vanilla rooms")

    args = parser.parse_args()

    if args.collision_verbose:
        args.collision_mode = "verbose"
    if args.collision_label is None:
        if args.collision_mode in ("verbose", "raw"):
            args.collision_label = "index"
        elif args.collision_mode in ("ascii", "passability"):
            args.collision_label = "ascii"
        else:
            args.collision_label = "none"

    if "--layer" in sys.argv:
        if args.layer == "all":
            layers = ["1", "2", "composite", "composition"]
        else:
            layers = [args.layer]
    else:
        # The composition is the all-in-one view (Layer 1+2 + collision +
        # cuttable grass + objects + triggers), so it ships by default.
        layers = ["composite", "composition"] if args.all_rooms else ["1", "2", "composite", "composition"]

    with_collision = args.collision or (args.layer == "collision")
    with_triggers = args.triggers or (args.layer == "triggers")
    with_composition = args.composition or (args.layer == "composition")
    with_legend = not args.no_legend
    with_grid = (args.grid is not None) or (args.layer == "grid")
    grid_spec = args.grid if args.grid else "8,16"

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
                    layers=layers,
                    with_collision=with_collision,
                    with_triggers=with_triggers,
                    with_grid=with_grid,
                    with_composition=with_composition,
                    with_legend=with_legend,
                    grid_spec=grid_spec,
                    grid_color=args.grid_color,
                    grid_opacity=args.grid_opacity,
                    bg_color=args.bg_color,
                    collision_label=args.collision_label,
                    collision_mode=args.collision_mode,
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

    print(f"Rendering Room 0x{room_id:02X}...")
    files = render_room_layers(
        room_id,
        rom_path=args.rom,
        out_dir=args.out_dir,
        layers=layers,
        with_collision=with_collision,
        with_triggers=with_triggers,
        with_grid=with_grid,
        with_composition=with_composition,
        with_legend=with_legend,
        grid_spec=grid_spec,
        grid_color=args.grid_color,
        grid_opacity=args.grid_opacity,
        bg_color=args.bg_color,
        collision_label=args.collision_label,
        collision_mode=args.collision_mode,
    )


    print(f"Successfully generated {len(files)} image(s) in {args.out_dir}:")
    for name, path in files.items():
        print(f"  [{name:9s}] {path}")

    if with_collision:
        room_data = dump_room(room_id, args.rom)
        cwords = room_data["collision_int_words"]
        unique_words = sorted(list(set(w for row in cwords for w in row)))

        cnt_wall = sum(1 for row in cwords for w in row if (w & 0x0F) == 0x0F)
        cnt_slope_sw_ne = sum(1 for row in cwords for w in row if (w & 0x0F) in (0x01, 0x0A, 0x05, 0x0E))
        cnt_slope_nw_se = sum(1 for row in cwords for w in row if (w & 0x0F) in (0x02, 0x09, 0x06, 0x0D))
        cnt_vert = sum(1 for row in cwords for w in row if (w & 0x0F) in (0x07, 0x08))
        cnt_horiz = sum(1 for row in cwords for w in row if (w & 0x0F) in (0x03, 0x0C, 0x04, 0x0B))
        cnt_floor = sum(1 for row in cwords for w in row if (w & 0x0F) == 0)

        print(f"\nCollision Physical Groups (Room 0x{room_id:02X}):")
        print(f"  [#] Solid Wall:          {cnt_wall:4d} tiles")
        print(f"  [/] Diagonal Slope /:    {cnt_slope_sw_ne:4d} tiles")
        print(f"  [\\] Diagonal Slope \\:    {cnt_slope_nw_se:4d} tiles")
        print(f"  [|] Vertical Barrier |:  {cnt_vert:4d} tiles")
        print(f"  [-] Horiz. Barrier -:    {cnt_horiz:4d} tiles")
        print(f"  [.] Walkable Floor:      {cnt_floor:4d} tiles")

        print(f"\nCollision Types ({len(unique_words)} unique in Room 0x{room_id:02X}):")
        for idx, cw in enumerate(unique_words):
            cnt = sum(row.count(cw) for row in cwords)
            print(f"  [{idx:2d}] 0x{cw:04X} ({cnt:4d} tiles)")


if __name__ == "__main__":
    main()

