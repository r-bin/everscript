---
name: rom-map-data
description: Experimental guide on reverse-engineering Secret of Evermore map data, tilemap layouts, collision layers, and tileset compression from the ROM.
---

# ROM Map Data & Tilemap Architecture (Experimental)

Understanding how Secret of Evermore stores, decompresses, and renders map data is an ongoing reverse-engineering effort. This guide outlines the current state of knowledge regarding ROM map pointers, tilemaps, collision layers, and external tooling.

---

## 1. Room Header Structure

Each of the 116 maps in the game is referenced via a master **Map Pointer Table** in ROM:
- The pointer table contains 24-bit pointers to each map's header block.
- A standard map header contains:
  1. **Tileset Pointer (ROM Address):** Points to the compressed 8x8 and 16x16 tile graphic patterns.
  2. **Tilemap Layout Pointer:** Points to the compressed tile placement grid (Layer 1 and Layer 2).
  3. **Palette Index:** References the 16-color sub-palettes loaded into CGRAM for background layers.
  4. **Collision Data Pointer:** Defines solid walls, water, pit barriers, and height transitions.
  5. **Map Dimensions:** Width and height measured in 16x16 pixel metatiles.

---

## 2. Coordinate Spaces

Evermore operates across two distinct coordinate planes:

| Coordinate Plane | Scale | Typical Usage |
|---|---|---|
| **Pixel Coordinates** | 1:1 ($256 \times 224$ screen space) | Sprite rendering, projectile hits, camera tracking |
| **Tile Coordinates** | 1:8 or 1:16 ($X_{pix} / 8$, $Y_{pix} / 8$) | Step-on trigger rects `[x0, y0 : x1, y1]`, spawn points |

When analyzing room dumps from `script_all`:
```
(22) CHANGE MAP = 0x38 @ [ 0x0180 | 0x02C0 ]: "South Jungle / Start"
```
The spawn coordinates `0x0180` and `0x02C0` are raw pixel values. Divided by 8, these correspond to tile coordinates `(48, 88)`.

---

## 3. Map Compression & Tilesets

Evermore utilizes a proprietary LZ/dictionary-based decompression scheme:
- Background graphics and tilemap arrays are stored in compressed blocks to conserve ROM space.
- Decompression is performed by 65c816 routines during map load transitions, unpacking raw tile definitions into high WRAM (`$7E2900..$7EFFFF`) before DMA transfers to VRAM.

---

## 4. Reverse-Engineering Tools & Avenues

1. **`SoETilesViewer` Project:**
   - Located in the sibling repository `../SoETilesViewer/`.
   - Contains C++ tools (`list-rooms.cpp`) that parse ROM headers, extract tile blocks, and generate the disassemblies stored in `script_all`.
2. **Mesen2 PPU Viewer:**
   - Using Mesen2's **Tilemap Viewer** and **PPU Memory Viewer**, you can inspect VRAM to see how Layer 1 and Layer 2 are constructed in real time.
3. **Open Research Questions:**
   - Full decoding of the collision tile bitmask (determining how elevation and stairs interact with player collision).
   - Rebuilding custom tilemaps from scratch in `.evs` without relying on existing vanilla map IDs.
