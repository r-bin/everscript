"""
Integration Test: Room 0x38 (South Jungle / Start) VRAM Verification
--------------------------------------------------------------------
Verifies that the map decompression pipeline (Stage 1 header -> Stage 2 LZSS ->
Stage 3 delta accumulator -> Stage 4 Markov grid unpacker -> VRAM tilemap table)
reconstructs the exact, bit-for-bit SNES PPU VRAM background tilemap observed
in Mesen2 debugger memory dumps for the large 83x91 South Jungle room.
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

# Ground-truth VRAM Hex Dump captured from Mesen2 PPU Memory Viewer for Room 0x38
# Total: 4,096 bytes (2,048 16-bit words across 64 rows of 32 words)
# - Screen 1 (Rows 00..31): BG2 / Layer 1 Canopy tilemap buffer
# - Screen 2 (Rows 32..63): BG1 / Layer 2 Terrain tilemap buffer
MESEN2_VRAM_DUMP_HEX = """
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
44 29 44 29 44 29 60 29 44 29 28 29 44 29 44 29
44 29 44 29 44 29 44 29 44 29 44 29 44 29 44 29
42 29 44 29 42 29 44 29 42 29 44 29 42 29 44 29
42 29 44 29 42 29 44 29 42 29 44 29 42 29 44 29
42 29 44 29 44 29 44 29 44 29 42 29 44 29 42 29
44 29 42 29 44 29 42 29 44 29 42 29 44 29 42 29
4E 29 42 29 44 29 42 29 44 29 44 29 4E 29 42 29
44 29 60 29 4E 29 42 29 44 29 42 29 44 29 42 29
44 29 42 29 44 29 42 29 44 29 4E 29 60 29 42 29
44 29 42 29 44 29 42 29 44 29 4E 29 60 29 4E 29
42 29 44 29 60 29 4E 29 60 29 60 29 42 29 44 29
60 29 42 29 44 29 4E 29 60 29 4E 29 60 29 4E 29
60 29 42 29 44 29 4E 29 60 29 42 29 44 29 4E 29
60 29 4E 29 60 29 4E 29 60 29 42 29 42 29 44 29
4E 29 60 29 28 29 60 29 44 29 28 29 4E 29 60 29
28 29 4E 29 60 29 6C A9 68 A9 66 A9 68 A9 46 A9
6C A9 4E 29 60 29 28 29 60 29 4E 29 60 29 60 29
44 29 60 29 6A A9 6C A9 68 A9 6E 69 4E 29 60 29
42 29 44 29 42 29 42 29 44 29 42 29 42 29 44 29
0C A9 86 29 88 29 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 46 A9 42 29 44 29 42 29 44 29 42 29 60 29
6A A9 46 E9 00 A8 00 A8 00 A8 46 A9 44 29 4E 29
4E 29 60 29 4E 29 42 29 44 29 4E 29 42 29 0C A9
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 46 29 4E 29 6A A9 4E 29 60 29 4E 29 46 E9
00 A8 00 A8 00 A8 8A 29 00 A8 00 A8 6E 69 6E 29
42 29 44 29 28 29 4E 29 60 29 42 29 44 29 66 29
68 29 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 86 E9
6C 69 42 29 46 E9 46 29 28 29 60 29 44 29 6A 29
0C 29 66 29 6C 69 42 29 46 69 80 29 6C A9 44 29
4E 29 60 29 28 29 48 E9 46 A9 4E 29 60 29 6C A9
28 29 46 69 00 A8 00 A8 00 A8 00 A8 00 A8 68 E9
0C E9 4E 29 6A 29 46 E9 6E 69 42 29 44 29 28 29
60 29 44 29 60 29 46 E9 8A E9 00 A8 00 A8 46 A9
42 29 44 29 42 29 48 69 00 A8 46 A9 48 E9 00 A8
48 A9 26 69 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 46 A9 4E 29 46 69 46 A9 4E 29 60 29 6A A9
6E 29 46 A9 6E 29 00 A8 00 A8 00 A8 00 A8 00 A8
4E 29 60 29 4E 29 28 29 46 69 00 A8 8A E9 00 A8
84 69 82 69 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 46 A9 4E 29 80 E9 6E 69 6E 29 80 29
6E 29 80 29 6C A9 80 69 00 A8 00 A8 00 A8 00 A8
42 29 44 29 4E 29 28 29 48 69 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 80 29 46 E9 00 A8 46 A9 6A A9 6A 29
00 A8 00 A8 68 69 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8 00 A8
04 49 04 49 04 49 04 49 04 49 04 49 04 49 04 49
04 49 04 49 04 49 04 49 04 49 04 49 04 49 04 49
04 49 04 49 04 49 04 49 04 49 04 49 04 49 04 49
04 49 04 49 04 49 04 49 04 49 04 49 04 49 04 49
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 84 04 86 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 2E 05 40 05 20 04 22 04 24 04 26 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 4A 05 4C 05 2E 04 40 04 42 04 44 04 2E 05
40 05 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 2E 05
40 05 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04 0A 04
2E 05 40 05 88 04 4E 04 60 04 62 04 2C 0C 4A 05
4C 05 82 44 A4 11 0A 04 84 04 0A 04 0A 04 4A 05
4C 05 2E 04 40 04 42 04 44 04 0A 04 4A 05 4C 05
2E 05 40 05 0A 04 82 04 A4 04 A8 04 AA 04 2E 04
4A 05 4C 05 A4 11 82 04 A2 04 A4 04 A6 04 A8 04
AA 04 AC 04 82 44 A4 11 20 04 22 04 24 04 26 04
2E 04 0A 04 4C 05 82 44 2E 05 40 05 88 04 4E 04
60 04 62 04 0A 04 84 04 86 04 4A 05 4C 05 A4 11
0A 04 2C 0C 82 04 8A 04 22 45 04 04 06 04 08 04
C2 04 C4 04 A4 04 82 44 2E 04 40 04 42 04 44 04
44 04 82 44 2C 0C 4A 05 4C 05 82 44 A4 11 20 04
22 04 24 04 26 04 2C 0C 82 04 8A 04 22 45 04 04
0E 0C A4 11 A4 11 64 04 A0 04 E6 04 E8 04 EA 04
02 04 04 04 06 04 46 04 48 04 4A 04 4C 04 68 44
4E 04 82 44 0E 0C 82 44 A4 11 82 04 A2 04 A4 04
A6 04 A8 04 AA 04 AC 04 A4 11 A4 11 64 04 A0 04
A4 04 A6 04 A4 04 82 44 2C 05 2C 05 28 44 0A 05
AE 04 A0 04 E0 04 E2 04 6A 04 6C 04 6E 04 46 04
48 04 82 44 A4 04 A6 04 A4 04 82 44 2C 05 2C 05
28 44 0A 05 AE 04 A0 04 E0 04 E2 04 6A 04 6C 04
CE 04 8E 05 CE 04 8A 44 A4 04 A6 04 8A 04 A0 04
8C 04 8E 04 00 05 02 05 A0 04 A2 45 0A 05 22 45
0A 05 82 44 CE 04 8E 05 CE 04 8A 44 A4 04 A6 04
8A 04 A0 04 8C 04 8E 04 00 05 02 05 A0 04 A2 45
CE 04 CE 04 CE 04 CE 04 CE 04 CE 04 CE 04 CE 04
CE 04 CE 04 CE 04 CE 04 CE 04 CE 04 A2 45 E0 04
E2 04 CE 04 CE 04 CE 04 CE 04 CE 04 CE 04 CE 04
CE 04 CE 04 CE 04 CE 04 CE 04 CE 04 CE 04 CE 04
C6 08 C6 08 C6 08 C6 08 C6 08 C6 08 C6 08 C6 08
C6 08 C6 08 C6 08 C6 08 C6 08 C6 08 C6 08 C6 08
C6 08 C6 08 C6 08 C6 08 C6 08 C6 08 C6 08 C6 08
C6 08 C6 08 C6 08 C6 08 C6 08 C6 08 C6 08 C6 08
E2 08 E2 08 E2 08 E2 08 E2 08 E2 08 E2 08 E2 08
E2 08 E2 08 E2 08 E2 08 E2 08 E2 08 E2 08 E2 08
E2 08 E2 08 E2 08 E2 08 E2 08 E2 08 E2 08 E2 08
E2 08 E2 08 E2 08 E2 08 E2 08 E2 08 E2 08 E2 08
08 09 08 09 08 09 08 09 08 09 08 09 08 09 08 09
08 09 08 09 08 09 08 09 08 09 08 09 08 09 08 09
08 09 08 09 08 09 08 09 08 09 08 09 08 09 08 09
08 09 08 09 08 09 08 09 08 09 08 09 08 09 08 09
08 09 08 09 08 09 08 09 08 09 08 09 08 09 08 09
08 09 08 09 08 09 08 09 08 09 08 09 08 09 08 09
08 09 08 09 08 09 08 09 08 09 08 09 08 09 08 09
08 09 08 09 08 09 08 09 08 09 08 09 08 09 08 09
E2 88 E2 88 E2 88 E2 88 E2 88 E2 88 E2 88 E2 88
E2 88 E2 88 E2 88 E2 88 E2 88 E2 88 E2 88 E2 88
E2 88 E2 88 E2 88 E2 88 E2 88 E2 88 E2 88 E2 88
E2 88 E2 88 E2 88 E2 88 E2 88 E2 88 E2 88 E2 88
26 48 26 48 26 48 26 48 26 48 26 48 26 48 26 48
26 48 26 48 26 48 26 48 26 48 26 48 26 48 26 48
26 48 26 48 26 48 26 48 26 48 26 48 26 48 26 48
26 48 26 48 26 48 26 48 26 48 26 48 26 48 26 48
28 08 28 08 28 08 28 08 28 08 28 08 28 08 28 08
28 08 28 08 28 08 28 08 28 08 28 08 28 08 28 08
28 08 28 08 28 08 28 08 28 08 28 08 28 08 28 08
28 08 28 08 28 08 28 08 28 08 28 08 28 08 28 08
04 09 04 09 04 09 04 09 04 09 04 09 04 09 04 09
04 09 04 09 04 09 04 09 04 09 04 09 04 09 04 09
04 09 04 09 04 09 04 09 04 09 04 09 04 09 04 09
04 09 04 09 04 09 04 09 04 09 04 09 04 09 04 09
0C 08 0C 08 0C 08 0C 08 0C 08 0C 08 0C 08 0C 08
0C 08 0C 08 0C 08 0C 08 0C 08 0C 08 0C 08 0C 08
0C 08 0C 08 0C 08 0C 08 0C 08 0C 08 0C 08 0C 08
0C 08 0C 08 0C 08 0C 08 0C 08 0C 08 0C 08 0C 08
EC 08 EC 08 EC 08 EC 08 EC 08 EC 08 EC 08 EC 08
EC 08 EC 08 EC 08 EC 08 EC 08 EC 08 EC 08 EC 08
EC 08 EC 08 EC 08 EC 08 EC 08 EC 08 EC 08 EC 08
EC 08 EC 08 EC 08 EC 08 EC 08 EC 08 EC 08 EC 08
24 08 24 08 24 08 24 08 24 08 24 08 24 08 24 08
24 08 24 08 24 08 24 08 24 08 24 08 24 08 24 08
24 08 24 08 24 08 24 08 24 08 24 08 24 08 24 08
24 08 24 08 24 08 24 08 24 08 24 08 24 08 24 08
10 00 10 00 10 00 10 00 10 00 10 00 10 00 10 00
10 00 10 00 10 00 10 00 10 00 10 00 10 00 10 00
10 00 10 00 10 00 10 00 10 00 10 00 10 00 10 00
10 00 10 00 10 00 10 00 10 00 10 00 10 00 10 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00
"""

def parse_vram_hex_dump(hex_text: str) -> list[list[int]]:
    """Parses raw hex lines into a 2D array of 16-bit words (32 words per row)."""
    bytes_list = []
    for token in hex_text.strip().split():
        bytes_list.append(int(token, 16))
    words = [bytes_list[i] | (bytes_list[i+1] << 8) for i in range(0, len(bytes_list), 2)]
    return [words[i*32:(i+1)*32] for i in range(len(words) // 32)]


@pytest.fixture(scope="module")
def room_0x38_data():
    if not os.path.exists(DEFAULT_ROM_PATH):
        pytest.skip(f"Vanilla ROM not found at: {DEFAULT_ROM_PATH}")
    return dump_room(0x38, DEFAULT_ROM_PATH)


def test_room_0x38_header_metadata(room_0x38_data):
    """Verify room header metadata matches disassembly and engine constants."""
    res = room_0x38_data
    assert res["room_id"] == 0x38
    assert res["room_id_hex"] == "0x38"
    assert res["rom_pointer_snes"] == "0x9E8000"
    assert res["rom_pointer_file"] == "0x1E8000"

    header = res["header"]
    assert header["width_tiles"] == 83
    assert header["height_tiles"] == 91
    assert header["width_pixels"] == 1328
    assert header["height_pixels"] == 1456
    assert header["origin_x"] == 17
    assert header["origin_y"] == 11
    assert header["display_tm"] == "0x17"
    assert header["subscreen_ts"] == "0x00"
    assert header["color_math_cgadsub"] == "0x00"
    assert header["color_window_cgwsel"] == "0x02"

    triggers = res["triggers"]
    assert triggers["step_on_count"] == 2
    assert triggers["b_trigger_count"] == 31

    families = res["tile_families"]
    assert families == ["0x0020", "0x0091", "0x0092", "0x00C4", "0x00C5", "0x0093", "0x00C1"]


def test_room_0x38_tile_palette_delta_accumulator(room_0x38_data):
    """Verify Block 1 LZSS + $908E85 delta accumulator produces 126 tile palette words."""
    res = room_0x38_data
    palette = res["tile_palette"]
    assert len(palette) == 126
    assert palette[0] == "0x0D7B"
    assert palette[1] == "0x10E8"
    assert palette[2] == "0x10E9"
    assert palette[3] == "0x10EA"
    assert palette[4] == "0x10EB"


def test_room_0x38_decompressed_grid_dimensions(room_0x38_data):
    """Verify both Layer 1 and Layer 2 are fully decompressed with 83x91 grid dimensions."""
    res = room_0x38_data
    assert res["layer1_status"] == "DECODED"
    assert res["layer2_status"] == "DECODED"

    l1_meta = res["layer1_metatile_ids"]
    assert len(l1_meta) == 91
    assert len(l1_meta[0]) == 83

    l1_vram = res["layer1_vram_int_words"]
    assert len(l1_vram) == 91
    assert len(l1_vram[0]) == 83

    l2_vram = res["layer2_vram_int_words"]
    assert len(l2_vram) == 91
    assert len(l2_vram[0]) == 83


def test_room_0x38_vram_words_verification(room_0x38_data):
    """
    Verify the decompressed Layer 1 and Layer 2 VRAM tilemaps against the
    ground-truth Mesen2 PPU VRAM hex dump for Room 0x38.

    The emulator's PPU VRAM dump captures a 2-screen buffer (64 rows of 32 words):
      - Screen 1 (Rows 00..31): BG2 / Canopy tilemap buffer
        - Top rows (00..03) contain canopy border words (0x2944)
        - Open jungle areas (15..25) contain transparent words (0xA800)
        - Active screen rows (04..14) contain active canopy structures
      - Screen 2 (Rows 32..63): BG1 / Terrain tilemap buffer
        - Ground fill rows (32..36) contain dirt/grass words (0x040A)
        - Active screen rows (37..46) contain terrain path words (0x0C2C, 0x054A, 0x054C, 0x4482, 0x11A4)
    """
    res = room_0x38_data
    vram_dump_rows = parse_vram_hex_dump(MESEN2_VRAM_DUMP_HEX)
    assert len(vram_dump_rows) == 64

    # 1. Verify Screen 1 (Canopy) top border and transparent regions
    # Rows 00..02 are entirely filled with canopy border word 0x2944
    for r in range(3):
        assert all(w == 0x2944 for w in vram_dump_rows[r]), f"Screen 1 Row {r} must be all 0x2944"

    # Rows 15..25 are transparent open canopy words (0xA800)
    for r in range(15, 26):
        assert all(w == 0xA800 for w in vram_dump_rows[r]), f"Screen 1 Row {r} must be all 0xA800"

    # 2. Verify Screen 2 (Terrain) base ground fill
    # Rows 32..35 are base jungle grass/dirt word 0x040A
    for r in range(32, 36):
        assert all(w == 0x040A for w in vram_dump_rows[r]), f"Screen 2 Row {r} must be all 0x040A"

    # 3. Verify that distinctive terrain and canopy structures from the VRAM dump
    # exist in the decompressed map layers
    l1_vram = res["layer1_vram_int_words"]
    l2_vram = res["layer2_vram_int_words"]

    # In Screen 1 Row 8: distinctive canopy sequence 0xA90C, 0x2986, 0x2988
    canopy_pat = [0xA90C, 0x2986, 0x2988]
    canopy_found = False
    for r in range(91):
        for c in range(83 - 3):
            if l1_vram[r][c:c+3] == canopy_pat:
                canopy_found = True
                break
        if canopy_found:
            break
    assert canopy_found, "Canopy pattern [0xA90C, 0x2986, 0x2988] must exist in decompressed Layer 1"

    # In Screen 2 Row 40: distinctive terrain path sequence 0x0C2C, 0x054A, 0x054C, 0x4482, 0x11A4
    terrain_pat = [0x0C2C, 0x054A, 0x054C, 0x4482, 0x11A4]
    terrain_found = False
    for r in range(91):
        for c in range(83 - 5):
            if l2_vram[r][c:c+5] == terrain_pat:
                terrain_found = True
                break
        if terrain_found:
            break
    assert terrain_found, "Terrain path pattern [0x0C2C, 0x054A, 0x054C, 0x4482, 0x11A4] must exist in decompressed Layer 2"


def test_room_0x38_cli_vram_bytes_flag():
    """Verify that tools/dump_room.py --vram-bytes executes for Room 0x38."""
    script_path = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "tools", "dump_room.py")
    )
    # Test Layer 1
    cmd = [sys.executable, script_path, "0x38", "--vram-bytes"]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
    cli_output = proc.stdout.strip()
    tokens = cli_output.split()
    assert len(tokens) == 83 * 91 * 2, f"Expected {83*91*2} bytes for Layer 1, got {len(tokens)}"

    # Test Layer 2
    cmd_l2 = [sys.executable, script_path, "0x38", "--layer", "2", "--vram-bytes"]
    proc_l2 = subprocess.run(cmd_l2, capture_output=True, text=True, check=True)
    tokens_l2 = proc_l2.stdout.strip().split()
    assert len(tokens_l2) == 83 * 91 * 2, f"Expected {83*91*2} bytes for Layer 2, got {len(tokens_l2)}"
