# Secret of Evermore ROM Memory Map

This document serves as the authoritative single source of truth for the **ROM layout, bank organization, and map blob locations** in *Secret of Evermore* (US 1.0), matching the standard established in [.github/memory-map.md](memory-map.md) for WRAM.

---

## 1. SNES ROM Address Mapping Overview

Secret of Evermore is a **3 MB (24 Mbit) HiROM** cartridge, mapped into the SNES 24-bit address bus across fast and slow banks:

| Address Range | Bank Type | Purpose | ROM File Offset |
|---|---|---|---|
| `$00:8000..$3F:FFFF` | LoROM Mirror (Slow) | System vectors, hardware registers ($21xx), WRAM mirror | Mirrors HiROM |
| `$40:0000..$7D:FFFF` | HiROM (Slow) | Expanded data / patch freespace | `$000000..$3FFFFF` |
| `$80:8000..$BF:FFFF` | HiROM (Fast) | Engine core, ASM hooks, script VM, map blobs | `$000000..$3FFFFF` |
| `$C0:0000..$FF:FFFF` | HiROM (Fast) | Compressed graphics (CHR), audio samples, string tables | `$000000..$3FFFFF` |

### Key Subsystem Memory Banks

| Banks | Primary Subsystem Content |
|---|---|
| `$80..$91` | SNES Engine Core, interrupt handlers, V-Blank DMA routines, PPU drivers |
| `$92..$9C` | Script Virtual Machine bytecode streams, dialog handlers, event dispatchers |
| `$8C..$A8` | Room Map Blobs (Block 1 palette, Block 2 grid, Block 3 planar slices, Section 3 objects) |
| `$9F:FDE7` | Master Map Pointer Table (127 room entries, 4-byte stride -- see §2) |
| `$C0..$C4` | Text string tables (Huffman / dictionary compressed game dialogue) |
| `$D0..$DF` | CHR Character Tile graphics banks (decompressed via LZSS/copy to VRAM) |
| `$18:0000` | SPC700 Audio Engine, Sound Effects, and Music sequence tracks |

---

## 2. Master Map Directory: All 127 Room Blobs

The engine resolves room pointers via `$9FFDE7 + room_id * 4` (`0x1FFDE7` in ROM): a 24-bit
pointer plus one padding byte per entry.

> [!IMPORTANT]
> **There are 127 rooms, `0x00`..`0x7E` -- not 128.**
> The entry at index `0x7F` is not a room. Its padding byte is `0xCC` (every real room's is
> `0x00`), and the bytes it points at (`$C9CF89`) do not parse as a room blob: Block 2 reports
> `sub_flag 0x09` where the loader requires `0x07`, and a decompressed size of 4102 against the
> 16576 its header dimensions imply. It is unallocated table space that happens to follow the
> last real entry. `MAX_ROOMS = 127` in `tools/dump_room.py` is correct; any document claiming
> `0x00..0x7F` is not.

All 127 blobs are listed below, generated from the ROM via `tools/dump_room.py` and
`tools/encode_room.py` -- see §4 for how to regenerate this table.

**Columns.** *Bytes* is the blob's true extent, measured from its start to the furthest byte any
object record or stamping block reaches (`encode_room._object_area_end`), not a guess from the
gap to the next blob -- blobs are not stored in room order. *B1*/*B3* are the compression
`sub_flag`s of Block 1 and Block 3 (`raw` = `0x00` uncompressed, `lzss` = `0x03`); Block 2 is
`markov` (`0x07`) in all 127 rooms. *Planes* is the set of elevation planes the room's collision
words use (bold where more than one -- see [docs/map_collision_mechanics.md](../docs/map_collision_mechanics.md)).
*Grass* is the cuttable-tile count where non-zero ([docs/cuttable_grass_mechanics.md](../docs/cuttable_grass_mechanics.md)).

| ID | Hex | Room | SNES ptr | ROM offset | Bytes | Tiles | Metatiles | B1 | B3 | Objs | Step | B-Trig | Planes | Grass |
|---:|---|---|---|---|---:|---|---:|---|---|---:|---:|---:|---|---:|
| 0 | `0x00` | Omnitopia - Alarm room | `$ABF4F1` | `0x2BF4F1` | 2272 | 37x68 | 201 | lzss | lzss | 11 | 8 | 1 | 1 |  |
| 1 | `0x01` | Prehistoria - Exterior of Blimp's Hut | `$A9E517` | `0x29E517` | 3260 | 33x49 | 510 | lzss | lzss | 12 | 4 | 0 | 1 |  |
| 2 | `0x02` | Intro - Mansion Exterior 1965 | `$ACC12D` | `0x2CC12D` | 1931 | 28x56 | 353 | lzss | lzss | 0 | 0 | 0 | 1 |  |
| 3 | `0x03` | Intro - Mansion Exterior 1995 | `$AAEABA` | `0x2AEABA` | 2775 | 20x56 | 539 | lzss | lzss | 3 | 0 | 0 | 1 |  |
| 4 | `0x04` | Antiqua - Crustacia fire pit | `$ACD00A` | `0x2CD00A` | 1903 | 23x25 | 269 | lzss | lzss | 2 | 2 | 0 | 1 |  |
| 5 | `0x05` | Antiqua - Between 'mids and halls | `$A4D3B4` | `0x24D3B4` | 6776 | 48x63 | 959 | lzss | lzss | 23 | 20 | 20 | 1 | 31 |
| 6 | `0x06` | Antiqua - Outside of 'mids | `$9C8000` | `0x1C8000` | 17185 | 80x82 | 2027 | lzss | lzss | 36 | 27 | 20 | **0,1,2,3** |  |
| 7 | `0x07` | Antiqua - West of Crustacia | `$A793E9` | `0x2793E9` | 5048 | 37x42 | 772 | lzss | lzss | 13 | 10 | 13 | 1 | 5 |
| 8 | `0x08` | Antiqua - Nobilia, Square | `$A5B42E` | `0x25B42E` | 6570 | 48x59 | 1085 | lzss | lzss | 15 | 5 | 5 | 1 |  |
| 9 | `0x09` | Antiqua - Nobilia, Square during Aegis fight | `$A9BDE6` | `0x29BDE6` | 3379 | 32x44 | 423 | lzss | lzss | 4 | 3 | 0 | 1 |  |
| 10 | `0x0A` | Antiqua - Nobilia, Market | `$9FAAEB` | `0x1FAAEB` | 10743 | 48x76 | 1807 | lzss | lzss | 41 | 11 | 58 | 1 |  |
| 11 | `0x0B` | Antiqua - Nobilia, Palace grounds | `$A6964A` | `0x26964A` | 5527 | 86x42 | 963 | lzss | lzss | 13 | 10 | 12 | 1 |  |
| 12 | `0x0C` | Antiqua - Nobilia, Inn | `$AD9F83` | `0x2D9F83` | 1537 | 45x33 | 253 | lzss | lzss | 1 | 4 | 2 | 1 |  |
| 13 | `0x0D` | Gothica - Ebon Keep Hall (Stairs, behind Verm) | `$A9D82A` | `0x29D82A` | 3314 | 41x61 | 506 | lzss | lzss | 6 | 8 | 0 | 1 |  |
| 14 | `0x0E` | Gothica - Ebon Keep Dining Room | `$ACC8B8` | `0x2CC8B8` | 1873 | 32x32 | 303 | lzss | lzss | 1 | 2 | 1 | 1 |  |
| 15 | `0x0F` | Gothica - Ebon Keep West Room (Naris) | `$AAC915` | `0x2AC915` | 2965 | 63x43 | 387 | lzss | lzss | 8 | 2 | 2 | 1 |  |
| 16 | `0x10` | Gothica - Ebon Keep Stained Glass Hallway | `$ADC553` | `0x2DC553` | 870 | 24x15 | 128 | lzss | lzss | 5 | 2 | 0 | 1 |  |
| 17 | `0x11` | Gothica - Ebon Keep Queen's Room | `$ABBD82` | `0x2BBD82` | 2437 | 31x45 | 372 | raw | lzss | 0 | 2 | 0 | 1 |  |
| 18 | `0x12` | Gothica - Ebon Keep sewers | `$A58000` | `0x258000` | 6688 | 112x90 | 823 | lzss | lzss | 14 | 2 | 13 | 1 |  |
| 19 | `0x13` | Gothica - Between Ebon Keep sewers, Dark Forest and Swamp | `$ACB18D` | `0x2CB18D` | 2024 | 23x24 | 386 | lzss | lzss | 1 | 4 | 1 | 1 |  |
| 20 | `0x14` | Gothica - Ebon Keep Tinker's Room | `$ABD077` | `0x2BD077` | 2390 | 32x46 | 363 | lzss | lzss | 4 | 2 | 3 | 1 |  |
| 21 | `0x15` | Brians Test Ground | `$A0FF33` | `0x20FF33` | 157 | 24x24 | 2 | raw | raw | 0 | 0 | 0 | 1 |  |
| 22 | `0x16` | Prehistoria - BBM | `$A38000` | `0x238000` | 7881 | 52x85 | 1180 | lzss | lzss | 40 | 42 | 24 | 1 |  |
| 23 | `0x17` | Prehistoria - Bug room 2 | `$AC9955` | `0x2C9955` | 2082 | 29x46 | 364 | lzss | lzss | 12 | 8 | 12 | **1,2** |  |
| 24 | `0x18` | Prehistoria - Thraxx' room | `$AB8AD2` | `0x2B8AD2` | 2749 | 24x32 | 344 | lzss | lzss | 5 | 3 | 2 | 1 |  |
| 25 | `0x19` | Gothica - Chessboard | `$A48000` | `0x248000` | 7490 | 74x66 | 957 | lzss | lzss | 25 | 5 | 19 | **1,2** |  |
| 26 | `0x1A` | Gothica - Below chessboard | `$A8E53C` | `0x28E53C` | 4179 | 67x82 | 552 | lzss | lzss | 1 | 4 | 1 | 1 |  |
| 27 | `0x1B` | Antiqua - Desert of Doom | `$A68000` | `0x268000` | 5714 | 97x113 | 544 | lzss | lzss | 4 | 19 | 0 | **0,1** |  |
| 28 | `0x1C` | Antiqua - Nobilia, North of Market | `$A7E153` | `0x27E153` | 4674 | 64x28 | 782 | lzss | lzss | 15 | 6 | 20 | 1 |  |
| 29 | `0x1D` | Antiqua - Nobilia, Arena (Vigor Fight) | `$A7F396` | `0x27F396` | 3153 | 69x56 | 518 | lzss | lzss | 2 | 0 | 0 | 1 |  |
| 30 | `0x1E` | Antiqua - Nobilia, Arena Holding Room | `$ACDE7C` | `0x2CDE7C` | 1813 | 45x24 | 239 | lzss | lzss | 9 | 1 | 9 | 1 |  |
| 31 | `0x1F` | Gothica - Doubles room in forest | `$A8D4CA` | `0x28D4CA` | 4207 | 50x25 | 771 | lzss | lzss | 8 | 2 | 0 | 1 |  |
| 32 | `0x20` | Gothica - Timberdrake room in forest | `$ACE592` | `0x2CE592` | 1795 | 24x22 | 300 | lzss | lzss | 2 | 2 | 0 | 1 |  |
| 33 | `0x21` | Gothica - Dark forest entrance (save point) | `$ACF37C` | `0x2CF37C` | 1713 | 17x19 | 246 | lzss | lzss | 0 | 2 | 0 | 1 |  |
| 34 | `0x22` | Gothica - Dark Forest | `$A1C650` | `0x21C650` | 8597 | 75x79 | 741 | lzss | lzss | 24 | 17 | 9 | **0,1,3** |  |
| 35 | `0x23` | Antiqua - Halls SW | `$ACB96B` | `0x2CB96B` | 1985 | 31x42 | 213 | lzss | lzss | 9 | 6 | 3 | 1 |  |
| 36 | `0x24` | Antiqua - Halls NW | `$A3BC84` | `0x23BC84` | 7591 | 71x100 | 829 | lzss | lzss | 18 | 29 | 7 | 1 |  |
| 37 | `0x25` | Prehistoria - Fire Eyes' Village | `$A4B92D` | `0x24B92D` | 6790 | 63x58 | 1036 | lzss | lzss | 21 | 13 | 20 | 1 |  |
| 38 | `0x26` | Prehistoria - West area with Defend | `$ADCEE5` | `0x2DCEE5` | 728 | 19x18 | 98 | raw | lzss | 3 | 1 | 3 | 1 |  |
| 39 | `0x27` | Prehistoria - Mammoth Graveyard | `$A6D67A` | `0x26D67A` | 5307 | 50x48 | 771 | lzss | lzss | 32 | 3 | 30 | 1 |  |
| 40 | `0x28` | Antiqua - Halls Collapsing Bridge | `$A1A38F` | `0x21A38F` | 8896 | 83x82 | 880 | lzss | lzss | 33 | 32 | 2 | **0,1** |  |
| 41 | `0x29` | Antiqua - Halls main room | `$A7BB53` | `0x27BB53` | 4925 | 42x70 | 571 | lzss | lzss | 18 | 32 | 2 | 1 |  |
| 42 | `0x2A` | Antiqua - Halls Boss Room | `$AA98B5` | `0x2A98B5` | 3134 | 64x42 | 364 | raw | lzss | 1 | 1 | 0 | 1 |  |
| 43 | `0x2B` | Antiqua - Outside of halls | `$A7CE91` | `0x27CE91` | 4801 | 69x33 | 786 | lzss | lzss | 16 | 2 | 17 | 1 |  |
| 44 | `0x2C` | Antiqua - Halls SE | `$AC911F` | `0x2C911F` | 2101 | 21x28 | 264 | lzss | lzss | 1 | 2 | 0 | 1 |  |
| 45 | `0x2D` | Antiqua - Halls NE | `$A28000` | `0x228000` | 8572 | 105x96 | 965 | lzss | lzss | 15 | 18 | 5 | **0,1** |  |
| 46 | `0x2E` | Antiqua - Blimp's Cave | `$ADC8BA` | `0x2DC8BA` | 848 | 20x15 | 132 | lzss | lzss | 2 | 1 | 2 | 1 |  |
| 47 | `0x2F` | Antiqua - Horace's camp | `$A0CD23` | `0x20CD23` | 9449 | 65x57 | 1247 | lzss | lzss | 22 | 6 | 20 | **1,2** |  |
| 48 | `0x30` | Antiqua - Crustacia inside pirate ship | `$AAA4F5` | `0x2AA4F5` | 3117 | 67x46 | 462 | lzss | lzss | 7 | 8 | 7 | 1 |  |
| 49 | `0x31` | Intro Podunk 1965 | `$ACD757` | `0x2CD757` | 1829 | 98x20 | 317 | lzss | lzss | 0 | 0 | 0 | **0,1** |  |
| 50 | `0x32` | Intro - Podunk 1995 | `$ADA585` | `0x2DA585` | 1506 | 43x16 | 278 | lzss | lzss | 2 | 0 | 0 | 1 |  |
| 51 | `0x33` | Prehistoria - Strong Heart's Exterior | `$ADB50C` | `0x2DB50C` | 1109 | 20x16 | 197 | lzss | lzss | 0 | 2 | 0 | 1 |  |
| 52 | `0x34` | Prehistoria - Strong Heart's Hut | `$ADBD79` | `0x2DBD79` | 1027 | 18x18 | 175 | lzss | lzss | 3 | 1 | 3 | 1 |  |
| 53 | `0x35` | Act1 Quicksand, Bugmuck and Volcano caves + Act2 West Alchemy Cave | `$AAD4AB` | `0x2AD4AB` | 2867 | 109x23 | 429 | lzss | lzss | 13 | 5 | 10 | 1 |  |
| 54 | `0x36` | Prehistoria - Both fire pits (one room) | `$A3F774` | `0x23F774` | 2151 | 25x25 | 305 | lzss | lzss | 7 | 2 | 4 | 1 | 17 |
| 55 | `0x37` | Gothica - Gomi's Tower | `$9DBCF3` | `0x1DBCF3` | 11609 | 56x125 | 2131 | lzss | lzss | 30 | 12 | 22 | 1 |  |
| 56 | `0x38` | Prehistoria - South jungle / Start | `$9E8000` | `0x1E8000` | 11230 | 83x91 | 1352 | lzss | lzss | 31 | 2 | 31 | 1 | 152 |
| 57 | `0x39` | Gothica - Ebon Keep Fire pit | `$ACA984` | `0x2CA984` | 2091 | 44x38 | 344 | lzss | lzss | 3 | 2 | 0 | 1 |  |
| 58 | `0x3A` | Antiqua - Nobilia, Fire pit | `$ADAB68` | `0x2DAB68` | 1380 | 28x22 | 190 | lzss | lzss | 2 | 2 | 0 | 1 |  |
| 59 | `0x3B` | Prehistoria - Volcano Room 2 | `$A2C0A8` | `0x22C0A8` | 7985 | 80x89 | 828 | lzss | lzss | 38 | 4 | 34 | **1,2** |  |
| 60 | `0x3C` | Prehistoria - Volcano Room 1 | `$A2A161` | `0x22A161` | 8006 | 127x96 | 898 | lzss | lzss | 24 | 21 | 25 | **1,2** |  |
| 61 | `0x3D` | Prehistoria - Pipe maze | `$A39ECA` | `0x239ECA` | 7624 | 88x75 | 1029 | lzss | lzss | 9 | 39 | 0 | **0,1** |  |
| 62 | `0x3E` | Prehistoria - Side rooms of pipe maze | `$A98000` | `0x298000` | 4166 | 100x24 | 659 | lzss | lzss | 18 | 12 | 14 | 1 |  |
| 63 | `0x3F` | Prehistoria - Volcano Boss Room | `$AABD2C` | `0x2ABD2C` | 3050 | 24x37 | 514 | lzss | lzss | 7 | 1 | 0 | 1 |  |
| 64 | `0x40` | Gothica - Swamp south of Gomi's Tower | `$AB8000` | `0x2B8000` | 2770 | 24x42 | 503 | lzss | lzss | 0 | 2 | 0 | 1 |  |
| 65 | `0x41` | Prehistoria - North jungle | `$A5E6BE` | `0x25E6BE` | 5793 | 61x47 | 858 | lzss | lzss | 23 | 4 | 23 | 1 | 54 |
| 66 | `0x42` | Omnitopia - Reactor room and Reactor control | `$A9F1D1` | `0x29F1D1` | 3235 | 45x36 | 326 | lzss | lzss | 32 | 28 | 2 | 1 |  |
| 67 | `0x43` | Omnitopia - Control room | `$ABA9F5` | `0x2BA9F5` | 2502 | 48x18 | 296 | lzss | lzss | 11 | 1 | 6 | 1 |  |
| 68 | `0x44` | Omnitopia - Greenhouse (dark or both?) | `$AAF592` | `0x2AF592` | 2549 | 45x59 | 360 | lzss | lzss | 6 | 2 | 1 | 1 |  |
| 69 | `0x45` | Omnitopia - Secret boss room | `$ABEBF5` | `0x2BEBF5` | 2299 | 34x48 | 264 | lzss | lzss | 3 | 2 | 0 | 1 |  |
| 70 | `0x46` | Omnitopia - Professor's lab and ship area, (also?) Intro | `$A6EB36` | `0x26EB36` | 5107 | 49x51 | 622 | lzss | lzss | 32 | 5 | 3 | **0,1** |  |
| 71 | `0x47` | Omnitopia - Storage room | `$AA8C6D` | `0x2A8C6D` | 3143 | 56x38 | 458 | lzss | lzss | 12 | 1 | 7 | 1 |  |
| 72 | `0x48` | Omnitopia - Metroplex tunnels (rimsalas, spheres) | `$9FD4E3` | `0x1FD4E3` | 10530 | 114x82 | 849 | lzss | lzss | 65 | 56 | 53 | 1 |  |
| 73 | `0x49` | Omnitopia - Junkyard (Landing spot) | `$A4EE2D` | `0x24EE2D` | 4430 | 60x46 | 611 | lzss | lzss | 5 | 13 | 0 | 1 |  |
| 74 | `0x4A` | Omnitopia - Final Boss Room | `$A3DA2C` | `0x23DA2C` | 7495 | 20x28 | 612 | lzss | lzss | 8 | 2 | 8 | 1 |  |
| 75 | `0x4B` | Antiqua - Oglin cave | `$A0A80A` | `0x20A80A` | 9496 | 106x125 | 575 | lzss | lzss | 32 | 50 | 32 | 1 |  |
| 76 | `0x4C` | Antiqua - Nobilia, Fountain and snake statues | `$AB958D` | `0x2B958D` | 2683 | 22x36 | 477 | lzss | lzss | 8 | 2 | 10 | 1 |  |
| 77 | `0x4D` | Antiqua - Nobilia, Inside palace (Horace cutscene) | `$AD8669` | `0x2D8669` | 1617 | 38x17 | 246 | lzss | lzss | 1 | 0 | 0 | 1 |  |
| 78 | `0x4E` | Gothica - Ivor Tower, west alley (market) | `$AAB123` | `0x2AB123` | 3081 | 31x102 | 486 | lzss | lzss | 0 | 2 | 0 | **1,3** |  |
| 79 | `0x4F` | Antiqua - East of Crustacia | `$A99F92` | `0x299F92` | 3908 | 33x45 | 558 | lzss | lzss | 18 | 25 | 16 | **1,2** |  |
| 80 | `0x50` | Prehistoria - Sky above Volcano | `$A5FD60` | `0x25FD60` | 371 | 17x15 | 95 | lzss | lzss | 0 | 0 | 0 | 1 |  |
| 81 | `0x51` | Prehistoria - Village Huts and Blimp's Hut | `$A9AED7` | `0x29AED7` | 3854 | 50x56 | 575 | lzss | lzss | 25 | 9 | 25 | 1 |  |
| 82 | `0x52` | Prehistoria - Top of Volcano | `$ACFA2D` | `0x2CFA2D` | 1436 | 32x15 | 249 | lzss | lzss | 1 | 1 | 0 | 1 |  |
| 83 | `0x53` | Antiqua - Act2 Start Cutscene | `$ABE2F9` | `0x2BE2F9` | 2300 | 49x15 | 438 | lzss | lzss | 0 | 0 | 0 | 1 |  |
| 84 | `0x54` | Omnitopia - Shops | `$AA8000` | `0x2A8000` | 3180 | 60x47 | 452 | lzss | lzss | 8 | 7 | 3 | **0,1** |  |
| 85 | `0x55` | Antiqua - 'mids bottom level (Dog start) | `$9ED770` | `0x1ED770` | 10310 | 120x73 | 1058 | lzss | lzss | 47 | 47 | 24 | 1 |  |
| 86 | `0x56` | Antiqua - 'mids top level (Boy start) | `$A6C154` | `0x26C154` | 5413 | 94x58 | 646 | lzss | lzss | 25 | 6 | 24 | 1 |  |
| 87 | `0x57` | Antiqua - 'mids basement level (Tiny) | `$A7A7A2` | `0x27A7A2` | 5039 | 104x60 | 573 | lzss | lzss | 15 | 21 | 11 | 1 |  |
| 88 | `0x58` | Antiqua - 'mids boss room (Rimsala) | `$AD8CBB` | `0x2D8CBB` | 1630 | 34x34 | 212 | lzss | lzss | 7 | 5 | 0 | 1 |  |
| 89 | `0x59` | Prehistoria - Quick sand desert | `$A08000` | `0x208000` | 10249 | 58x79 | 1252 | lzss | lzss | 47 | 65 | 28 | **1,2** |  |
| 90 | `0x5A` | Prehistoria - Acid rain guy | `$AD9309` | `0x2D9309` | 1597 | 27x24 | 211 | lzss | lzss | 2 | 1 | 2 | 1 |  |
| 91 | `0x5B` | Prehistoria - East jungle | `$A78000` | `0x278000` | 5096 | 72x48 | 742 | lzss | lzss | 14 | 5 | 17 | 1 | 41 |
| 92 | `0x5C` | Prehistoria - Raptors | `$A8F590` | `0x28F590` | 2656 | 31x26 | 452 | lzss | lzss | 10 | 3 | 4 | 1 |  |
| 93 | `0x5D` | Gothica - Ebon Keep Courtyard (South of Verm) | `$ABD9CE` | `0x2BD9CE` | 2346 | 20x40 | 375 | lzss | lzss | 3 | 7 | 0 | 1 |  |
| 94 | `0x5E` | Gothica - Ebon Keep Front Room (Verm) | `$ACEC95` | `0x2CEC95` | 1799 | 22x52 | 255 | raw | lzss | 2 | 10 | 0 | 1 |  |
| 95 | `0x5F` | Gothica - Ebon Keep Verm side rooms | `$ADB961` | `0x2DB961` | 1048 | 53x56 | 79 | raw | lzss | 0 | 4 | 0 | 1 |  |
| 96 | `0x60` | Gothica - Ebon Keep Storage Room | `$ADCC0B` | `0x2DCC0B` | 729 | 22x17 | 95 | raw | lzss | 3 | 1 | 3 | 1 |  |
| 97 | `0x61` | Scrolling Over Machine | `$A8B3A9` | `0x28B3A9` | 4264 | 48x47 | 762 | lzss | lzss | 2 | 0 | 0 | 1 |  |
| 98 | `0x62` | Gothica - Ivor Tower, west square (trailers) | `$A0F130` | `0x20F130` | 3586 | 50x38 | 636 | lzss | lzss | 3 | 9 | 0 | 1 |  |
| 99 | `0x63` | Gothica - Ivor Tower, inside trailers | `$AD8000` | `0x2D8000` | 1640 | 47x20 | 211 | lzss | lzss | 4 | 2 | 0 | 1 |  |
| 100 | `0x64` | Antiqua - Cave entrance under 'mids | `$ADB0AA` | `0x2DB0AA` | 1122 | 21x18 | 188 | lzss | lzss | 0 | 2 | 0 | 1 |  |
| 101 | `0x65` | Prehistoria - Swamp (main area) | `$9D8000` | `0x1D8000` | 15602 | 80x99 | 2105 | lzss | lzss | 62 | 29 | 34 | **1,2** |  |
| 102 | `0x66` | Prehistoria - West of swamp | `$A8C44E` | `0x28C44E` | 4219 | 48x38 | 663 | lzss | lzss | 14 | 7 | 19 | 1 |  |
| 103 | `0x67` | Prehistoria - Bugmuck exterior | `$9EABDF` | `0x1EABDF` | 11152 | 86x73 | 1672 | lzss | lzss | 48 | 13 | 42 | **1,2** |  |
| 104 | `0x68` | Antiqua - Crustacia exterior | `$A6ABE2` | `0x26ABE2` | 5489 | 48x50 | 870 | lzss | lzss | 2 | 13 | 0 | 1 |  |
| 105 | `0x69` | Prehistoria - Volcano path | `$A18000` | `0x218000` | 9101 | 54x79 | 1009 | lzss | lzss | 41 | 31 | 33 | **1,2,3** | 86 |
| 106 | `0x6A` | Antiqua - Act2 Start Cutscene - waterfall | `$AC88E1` | `0x2C88E1` | 2110 | 17x82 | 364 | lzss | lzss | 0 | 0 | 0 | 1 |  |
| 107 | `0x6B` | Antiqua - Waterfall | `$A99047` | `0x299047` | 3915 | 48x34 | 657 | lzss | lzss | 0 | 7 | 0 | **1,2** |  |
| 108 | `0x6C` | Gothica - SE of Ivor Tower (Well) | `$ABC707` | `0x2BC707` | 2415 | 32x34 | 391 | lzss | lzss | 6 | 1 | 1 | 1 |  |
| 109 | `0x6D` | Antique - Aquagoth Room | `$ABB3BC` | `0x2BB3BC` | 2496 | 26x41 | 393 | lzss | lzss | 2 | 0 | 0 | 1 |  |
| 110 | `0x6E` | Gothica - Ivor Tower Hall | `$A8A2F4` | `0x28A2F4` | 4283 | 38x61 | 610 | lzss | lzss | 24 | 9 | 0 | 1 |  |
| 111 | `0x6F` | Gothica - Ivor Tower Dining Room | `$AADFDF` | `0x2ADFDF` | 2795 | 31x29 | 364 | lzss | lzss | 26 | 2 | 2 | 1 |  |
| 112 | `0x70` | Gothica - Ivor Tower Exterior Bridges and Balconies | `$A9CB12` | `0x29CB12` | 3352 | 71x28 | 630 | raw | lzss | 0 | 10 | 0 | 1 |  |
| 113 | `0x71` | Gothica - Ivor Tower East Room + Kitchen | `$9F8000` | `0x1F8000` | 10986 | 118x98 | 1110 | lzss | lzss | 72 | 57 | 32 | 1 |  |
| 114 | `0x72` | Gothica - Ivor Tower East Upper Floor | `$A88000` | `0x288000` | 4661 | 61x58 | 484 | raw | lzss | 33 | 19 | 18 | 1 |  |
| 115 | `0x73` | Gothica - Ivor Tower Dog Maze Underground | `$9CF0C2` | `0x1CF0C2` | 3899 | 128x70 | 336 | raw | lzss | 3 | 28 | 0 | 1 |  |
| 116 | `0x74` | Gothica - Ebon Keep and Ivory Tower dungeon + pipe room | `$A49D43` | `0x249D43` | 7200 | 52x70 | 1095 | lzss | lzss | 21 | 32 | 1 | 1 |  |
| 117 | `0x75` | Gothica - Ivor Tower Stariwell to dungeon | `$AD9947` | `0x2D9947` | 1594 | 29x37 | 186 | lzss | lzss | 5 | 2 | 0 | 1 |  |
| 118 | `0x76` | Gothica - South of Ivor Tower (Gate) | `$9DEA4E` | `0x1DEA4E` | 5538 | 52x70 | 702 | lzss | lzss | 20 | 2 | 20 | 1 |  |
| 119 | `0x77` | Gothica - Ivor Tower Puppet Show / Mungola | `$ABA009` | `0x2BA009` | 2539 | 30x25 | 321 | raw | lzss | 15 | 3 | 0 | **0,1** |  |
| 120 | `0x78` | Gothica - Ivor Tower Queen's Room | `$ACA178` | `0x2CA178` | 2060 | 31x45 | 322 | raw | lzss | 0 | 4 | 0 | 1 |  |
| 121 | `0x79` | Gothica - Ivor Tower Sewers | `$A5CDD9` | `0x25CDD9` | 6372 | 112x90 | 735 | lzss | lzss | 9 | 4 | 8 | 1 |  |
| 122 | `0x7A` | Gothica - Ivor Tower Sewers Exterior (landing spot) | `$ADC17D` | `0x2DC17D` | 982 | 17x22 | 146 | lzss | lzss | 0 | 2 | 0 | 1 |  |
| 123 | `0x7B` | Gothica - Ebon Keep and Ivor Tower Exterior Bottom Half | `$A59A21` | `0x259A21` | 6668 | 101x48 | 952 | lzss | lzss | 34 | 8 | 7 | 1 |  |
| 124 | `0x7C` | Gothica - Ebon Keep and Ivor Tower Exterior Top Half | `$A2DFCB` | `0x22DFCB` | 7887 | 101x60 | 1067 | lzss | lzss | 35 | 11 | 0 | 1 |  |
| 125 | `0x7D` | Gothica - Ebon Keep and Ivor Tower Interior | `$A1E7E2` | `0x21E7E2` | 5811 | 109x70 | 640 | lzss | lzss | 35 | 12 | 21 | 1 |  |
| 126 | `0x7E` | Omnitopia - Jail | `$A89236` | `0x289236` | 4285 | 103x31 | 489 | lzss | lzss | 22 | 1 | 17 | 1 |  |

**Total blob bytes: 561,259** (548.1 KiB across 127 rooms, ~17.8% of the 3 MB ROM).

---

## 3. Map Blob Binary Anatomy

Every room blob in the table above follows this exact sequential layout in ROM:

```text
Room Blob Start (Offset $00)
  ├── [0x00..0x0C]: 13-Byte Room Header (Origin X/Y, Width, Height, PPU Mode 1 Regs)
  ├── [0x0D..0x0E]: 16-bit Step-on Trigger Table Length (step_len)
  ├── [0x0F..0x0F+step_len]: Array of 6-byte Step-on Trigger Records
  ├── [+0..+1]: 16-bit B-Trigger Table Length (b_len)
  ├── [+2..+2+b_len]: Array of 6-byte B-Trigger Records
  ├── [+0]: Tile Family Count (1 byte)
  ├── [+1..+1+2*count]: Array of 16-bit Tile Family IDs (VRAM CHR layout)
  └── Compressed Payload Sub-Blocks (Dispatched via $8C988D):
        ├── Block 1: Tile Palette Deltas (WRAM $7FC300 → CGRAM)
        ├── Section 2: Animated Tile Descriptors ($90A0D0)
        ├── Block 2: 2D Markov Metatile Grid ($8C9B65 → WRAM $7F0000)
        ├── Block 3: Planar LZSS Metatiles Table ($8C98C9 → WRAM $7F0280)
        │     ├── Slice 0: Layer 1 Canopy (VRAM words)
        │     ├── Slice 1: Layer 2 Terrain (VRAM words)
        │     └── Slice 2: 16-bit Collision Attributes
        └── Section 3: Dynamic Map Objects ($90A5D0 Stamping Descriptors)
```

---

## 4. Regenerating the Table in §2

The table is derived data, not hand-maintained. Every column except the room *name* comes
straight from the ROM; names are curated and should be carried across when regenerating.

```python
from tools.dump_room import (dump_room, read24, snes2rom, MAP_LIST_ADDR,
                             DEFAULT_ROM_PATH, parse_blob_layout, MAX_ROOMS)
from tools.encode_room import _object_area_end

rom = open(DEFAULT_ROM_PATH, 'rb').read()
for rid in range(MAX_ROOMS):
    off = snes2rom(read24(rom, MAP_LIST_ADDR + rid * 4))
    layout = parse_blob_layout(rom, off)
    size = _object_area_end(rom, layout) - off
    room = dump_room(rid)
    # room['elevation_planes'], room['metatile_count'],
    # room['cuttable_grass_tile_count'], layout['block1_sub'], layout['block3_sub'] ...
```

Regenerate whenever the ROM's map data changes (a relocated blob via
`encode_room.write_room_into_rom`, or a new room added past `0x7E`). The *Bytes* column is the
one to watch: it is what `write_room_into_rom` checks against before allowing an in-place write.
