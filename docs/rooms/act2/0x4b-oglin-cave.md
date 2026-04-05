# [0x4b] Antiqua — Oglin Cave

| Field | Value |
|-------|-------|
| Room ID | 0x4b |
| Name | Antiqua - Oglin cave |
| Act | Act 2 — Antiqua |
| Data offset | `0xa0a80a` |
| Enter script | `0x928192` → `0x97d828` |
| Step-ons | 50 |
| B-triggers | 32 |
| Music | 0x44 |

---

## Overview

A massive cave complex spanning multiple sub-areas connected by 49 internal warp/scroll tiles plus one exit to the Aquagoth Room (0x6d). The cave contains **32 sniff spots** (plus 1 Call Beads gourd at the entrance) spread across the entire map. OBJs 0–31 correspond to sniff-spot locations and are unloaded on entry if the player's dog has already sniffed them. Three enemy types spawn throughout: Oglin (0x6e), Rollers (0x42), and Grubs (0x74). A first-entry cutscene plays when `$22f4&0x01` is set (boy looks around the cave).

---

## Memory Access

| Address | Bit | OBJ | Type | Item / Effect |
|---------|-----|-----|------|---------------|
| `$2287` | 0x40 | 0 | 🧪 | Call Beads×2 gourd looted [0x4b] |
| `$22bc` | 0x20 | 1 | 👃 | Sniffed Oil in Oglin cave (#1) [0x4b] |
| `$22bc` | 0x40 | 2 | 👃 | Sniffed Oil in Oglin cave (#2) [0x4b] |
| `$22bc` | 0x80 | 3 | 👃 | Sniffed Oil in Oglin cave (#3) [0x4b] |
| `$22bd` | 0x01 | 4 | 👃 | Sniffed Clay in Oglin cave (#4) [0x4b] |
| `$22bd` | 0x02 | 5 | 👃 | Sniffed Clay in Oglin cave (#5) [0x4b] |
| `$22bd` | 0x04 | 6 | 👃 | Sniffed Clay in Oglin cave (#6) [0x4b] |
| `$22bd` | 0x08 | 7 | 👃 | Sniffed Clay in Oglin cave (#7) [0x4b] |
| `$22bd` | 0x10 | 8 | 👃 | Sniffed Crystal in Oglin cave (#8) [0x4b] |
| `$22bd` | 0x20 | 9 | 👃 | Sniffed Crystal in Oglin cave (#9) [0x4b] |
| `$22bd` | 0x40 | 10 | 👃 | Sniffed Ethanol in Oglin cave (#10) [0x4b] |
| `$22bd` | 0x80 | 11 | 👃 | Sniffed Ethanol in Oglin cave (#11) [0x4b] |
| `$22be` | 0x01 | 12 | 👃 | Sniffed Ethanol in Oglin cave (#12) [0x4b] |
| `$22be` | 0x02 | 13 | 👃 | Sniffed Roots in Oglin cave (#13) [0x4b] |
| `$22be` | 0x04 | 14 | 👃 | Sniffed Limestone in Oglin cave (#14) [0x4b] |
| `$22be` | 0x08 | 15 | 👃 | Sniffed Limestone in Oglin cave (#15) [0x4b] |
| `$22be` | 0x10 | 16 | 👃 | Sniffed Limestone in Oglin cave (#16) [0x4b] |
| `$22be` | 0x20 | 17 | 👃 | Sniffed Limestone in Oglin cave (#17) [0x4b] |
| `$22be` | 0x40 | 18 | 👃 | Sniffed Wax in Oglin cave (#18) [0x4b] |
| `$22be` | 0x80 | 19 | 👃 | Sniffed Wax in Oglin cave (#19) [0x4b] |
| `$22bf` | 0x01 | 20 | 👃 | Sniffed Water in Oglin cave (#20) [0x4b] |
| `$22bf` | 0x02 | 21 | 👃 | Sniffed Water in Oglin cave (#21) [0x4b] |
| `$22bf` | 0x04 | 22 | 👃 | Sniffed Water in Oglin cave (#22) [0x4b] |
| `$22bf` | 0x08 | 23 | 👃 | Sniffed Water in Oglin cave (#23) [0x4b] |
| `$22bf` | 0x10 | 24 | 👃 | Sniffed Vinegar in Oglin cave (#24) [0x4b] |
| `$22bf` | 0x20 | 25 | 👃 | Sniffed Vinegar in Oglin cave (#25) [0x4b] |
| `$22bf` | 0x40 | 26 | 👃 | Sniffed Ash in Oglin cave (#26) [0x4b] |
| `$22bf` | 0x80 | 27 | 👃 | Sniffed Bone in Oglin cave (#27) [0x4b] |
| `$22c0` | 0x01 | 28 | 👃 | Sniffed Bone in Oglin cave (#28) [0x4b] |
| `$22c0` | 0x02 | 29 | 👃 | Sniffed Bone in Oglin cave (#29) [0x4b] |
| `$22c0` | 0x04 | 30 | 👃 | Sniffed Brimstone in Oglin cave (#30) [0x4b] |
| `$22c0` | 0x08 | 31 | 👃 | Sniffed Brimstone in Oglin cave (#31) [0x4b] |
| `$22f4` | 0x01 | — | 📖 | First-entry intro cutscene flag [0x4b] |

---

## Enter Script Summary

1. Set map bounds: x=0x0000–0x0230, y=0x0490–0x0660.
2. **Greyhound**.
3. **OBJ unloads** (if already sniffed / looted):
   - OBJ 0 if `$2287&0x40` (Call Beads gourd)
   - OBJ 1 if `$22bc&0x20`, OBJ 2 if `$22bc&0x40`, OBJ 3 if `$22bc&0x80`
   - OBJs 4–11 via `$22bd` bits 0x01–0x80
   - OBJs 12–19 via `$22be` bits 0x01–0x80
   - OBJs 20–27 via `$22bf` bits 0x01–0x80
   - OBJs 28–31 via `$22c0` bits 0x01–0x08
4. `$22eb&0x20` animation guard; teleport to [2b, b7] + fade-out if in animation.
5. CALL `0x0ea2` setup; write `$0eac = 0x172b`.
6. **Drop table**: Nectar 10/50 · Coins 4/50 · Honey 2/50.
7. **NPC spawners**:
   - NPC 0x6e (Oglin) ×31 spawners (scattered throughout)
   - NPC 0x42 (Roller) ×12 spawners
   - NPC 0x74 (Grub) ×8 spawners
8. **Music** 0x44 (if not already playing); write `$23bf = 0`.
9. If `$22f4&0x01`: cutscene — boy STOPPED, looks WEST, NORTH, SOUTH; then CALL `0x92de75`.
   Else: CALL `0x92de75` directly.

---

## Step-on Scripts

The cave uses two step-on patterns:

### Pattern A — Standard warp tiles (32 tiles)
Each sets a specific map-window viewport, teleports both characters to the target position within the same room, and calls a global transition script (0x21/0x19/0x1d/0x26). No room change.

| Tile | Target pos | Viewport (x0,y0:x1,y1) | Transition |
|------|-----------|------------------------|------------|
| `[68,3c:6a,3d]` | [a4,01] | [2b0,000:550,328] | 0x21 |
| `[3a,62:3c,63]` | [72,d5] | [330,6a0:550,7c0] | 0x21 |
| `[4f,62:51,63]` | [a4,d5] | [330,6a0:550,7c0] | 0x21 |
| `[5f,3d:61,3e]` | [a4,01] | [2b0,000:550,328] | 0x21 (reuse) |
| `[56,03:58,04]` | [c8,77] | [5a0,230:6a0,3c0] | 0x26 |
| `[4f,33:51,34]` | [98,6f] | [2a0,370:520,610] | 0x21 |
| `[3b,33:3d,34]` | [7c,6f] | [2a0,370:520,610] | 0x21 |
| `[32,33:34,34]` | [5e,6f] | [2a0,370:520,610] | 0x21 |
| `[31,1f:32,21]` | [4b,3c] | [060,010:260,230] | 0x19 |
| `[31,13:32,15]` | [4b,24] | [060,010:260,230] | 0x19 |
| `[31,07:32,09]` | [4b,0c] | [060,010:260,230] | 0x19 |
| `[29,07:2a,09]` | [57,0c] | [2b0,000:550,328] | 0x1d |
| `[29,13:2a,15]` | [57,24] | [2b0,000:550,328] | 0x1d |
| `[29,1f:2a,21]` | [57,3c] | [2b0,000:550,328] | 0x1d |
| `[24,23:26,24]` | [44,4f] | [060,270:280,420] | 0x21 |
| `[0f,23:11,24]` | [16,4f] | [060,270:280,420] | 0x21 |
| `[2b,3c:2c,3e]` | [55,80] | [2a0,370:520,610] | 0x1d |
| `[26,2a:28,2b]` | [40,45] | [060,010:260,230] | 0x26 |
| `[0f,2a:11,2b]` | [16,45] | [060,010:260,230] | 0x26 |
| `[25,42:27,43]` | [38,93] | [000,490:230,660] | 0x21 |
| `[50,3a:52,3b]` | [96,65] | [2b0,000:550,328] | 0x26 |
| `[42,3a:44,3b]` | [6e,65] | [2b0,000:550,328] | 0x26 |
| `[33,3a:35,3b]` | [5c,65] | [2b0,000:550,328] | 0x26 |
| `[30,41:31,43]` | [4f,76] | [060,270:280,420] | 0x19 |
| `[32,62:34,63]` | [4c,d5] | [100,6a0:320,7d0] | 0x21 |
| `[56,6d:58,6e]` | [96,c3] | [2a0,370:520,610] | 0x26 |
| `[3d,6d:3f,6e]` | [6c,c3] | [2a0,370:520,610] | 0x26 |
| `[2a,6d:2c,6e]` | [5c,c3] | [2a0,370:520,610] | 0x26 |
| `[20,4c:22,4d]` | [42,83] | [060,270:280,420] | 0x26 |
| `[23,6d:26,6e]` | [40,cb] | [000,490:230,660] | 0x26 |
| `[24,66:26,67]` | [3f,d5] | [100,6a0:320,7d0] | 0x21 |
| `[1a,6d:1c,6e]` | [2c,cb] | [000,490:230,660] | 0x26 |
| `[1a,66:1c,67]` | [2c,d5] | [100,6a0:320,7d0] | 0x21 |

### Pattern B — Scroll-zone tiles (16 tiles)
Each writes two viewport rectangles to `$23f1–$23ff` (current) and `$23f9–$23ff` (target), writes `$2834/$2836/$2838/$283a`, and calls scroll-sub `0x97d39d` (camera interpolation). These tiles are positioned at sub-area boundaries and smoothly scroll the camera between adjacent sections.

| Tile | Current viewport | Target viewport |
|------|-----------------|-----------------|
| `[16,7b:19,7d]` | [000,490:230,660] | [128,7a0:048,550] |
| `[48,71:4b,73]` | [060,010:260,230] | [448,700:0b8,070] |
| `[32,55:35,57]` | [060,270:280,420] | [2e8,540:1a8,360] |
| `[20,5b:23,5d]` | [000,490:230,660] | [1c8,5a0:168,4f0] |
| `[08,56:0b,58]` | [100,6a0:320,7d0] | [048,550:128,7a0] (reverse) |
| `[1a,50:1d,52]` | [000,490:230,660] | [168,4f0:1c8,5a0] (reverse) |
| `[44,40:47,42]` | [2b0,000:550,328] | [408,3f0:358,050] |
| `[64,33:67,35]` | [2b0,000:550,328] | [608,320:4c8,0f0] |
| `[65,29:68,2b]` | [060,270:280,420] | [618,280:178,2d0] |
| `[44,2f:47,31]` | [060,270:280,420] | [408,2e0:0c8,360] |
| `[1e,37:21,39]` | [2a0,370:520,610] | [1a8,360:2e8,540] |
| `[10,37:13,39]` | [2b0,000:550,328] | [0c8,360:408,2e0] (reverse) |
| `[1b,2e:1e,30]` | [5a0,230:6a0,3c0] | [178,2d0:618,280] (reverse) |
| `[50,10:53,12]` | [5a0,230:6a0,3c0] | [4c8,0f0:608,320] (reverse) |
| `[39,06:3c,08]` | [2a0,370:520,610] | [358,050:408,3f0] (reverse) |
| `[0f,08:12,0a]` | [330,6a0:550,7c0] | [0b8,070:448,700] (reverse) |

### Special exit
| Tile | Destination | Notes |
|------|-------------|-------|
| `[26,03:28,04]` | **0x6d** Aquagoth Room | CALL 0x26 prep, fade-out, CHANGE MAP |

---

## Exits

| Tile | Destination | Notes |
|------|-------------|-------|
| `[26,03:28,04]` | **0x6d** Aquagoth Room | @ [0x00d8, 0x0288] |

---

## B-Triggers

| # | Tile | Flag | Item | Qty |
|---|------|------|------|-----|
| 1 | `[3e,06:40,08]` | `$2287&0x40` | 🧪 Call Beads | ×2 |
| 2 | `[2b,34:2c,35]` | `$22c0&0x08` | 👃 Brimstone (#31) | ×2 |
| 3 | `[6b,32:6c,33]` | `$22c0&0x04` | 👃 Brimstone (#30) | ×2 |
| 4 | `[46,7d:47,7e]` | `$22c0&0x02` | 👃 Bone (#29) | ×1 |
| 5 | `[27,72:29,73]` | `$22c0&0x01` | 👃 Bone (#28) | ×1 |
| 6 | `[30,5a:31,5b]` | `$22bf&0x80` | 👃 Bone (#27) | ×1 |
| 7 | `[32,1c:33,1d]` | `$22bf&0x40` | 👃 Ash (#26) | ×2 |
| 8 | `[50,1d:51,1e]` | `$22bf&0x20` | 👃 Vinegar (#25) | ×3 |
| 9 | `[56,4a:57,4b]` | `$22bf&0x10` | 👃 Vinegar (#24) | ×2 |
| 10 | `[32,73:33,74]` | `$22bf&0x08` | 👃 Water (#23) | ×1 |
| 11 | `[34,0b:35,0c]` | `$22bf&0x04` | 👃 Water (#22) | ×1 |
| 12 | `[3d,5e:3e,5f]` | `$22bf&0x02` | 👃 Water (#21) | ×2 |
| 13 | `[10,50:11,51]` | `$22bf&0x01` | 👃 Water (#20) | ×1 |
| 14 | `[49,3d:4a,3e]` | `$22be&0x80` | 👃 Wax (#19) | ×2 |
| 15 | `[0f,5b:10,5c]` | `$22be&0x40` | 👃 Wax (#18) | ×1 |
| 16 | `[24,60:25,61]` | `$22be&0x20` | 👃 Limestone (#17) | ×1 |
| 17 | `[1c,7a:1d,7b]` | `$22be&0x10` | 👃 Limestone (#16) | ×1 |
| 18 | `[4d,70:4e,71]` | `$22be&0x08` | 👃 Limestone (#15) | ×2 |
| 19 | `[43,63:44,64]` | `$22be&0x04` | 👃 Limestone (#14) | ×1 |
| 20 | `[3f,2a:40,2b]` | `$22be&0x02` | 👃 Roots (#13) | ×1 |
| 21 | `[62,37:63,38]` | `$22be&0x01` | 👃 Ethanol (#12) | ×2 |
| 22 | `[50,05:51,06]` | `$22bd&0x80` | 👃 Ethanol (#11) | ×1 |
| 23 | `[0c,36:0d,37]` | `$22bd&0x40` | 👃 Ethanol (#10) | ×1 |
| 24 | `[35,05:36,06]` | `$22bd&0x20` | 👃 Crystal (#9) | ×2 |
| 25 | `[20,23:21,24]` | `$22bd&0x10` | 👃 Crystal (#8) | ×1 |
| 26 | `[20,05:21,06]` | `$22bd&0x08` | 👃 Clay (#7) | ×1 |
| 27 | `[16,42:17,43]` | `$22bd&0x04` | 👃 Clay (#6) | ×1 |
| 28 | `[17,51:18,52]` | `$22bd&0x02` | 👃 Clay (#5) | ×2 |
| 29 | `[30,50:31,51]` | `$22bd&0x01` | 👃 Clay (#4) | ×1 |
| 30 | `[56,5c:57,5d]` | `$22bc&0x80` | 👃 Oil (#3) | ×2 |
| 31 | `[42,34:43,35]` | `$22bc&0x40` | 👃 Oil (#2) | ×1 |
| 32 | `[0e,16:0f,17]` | `$22bc&0x20` | 👃 Oil (#1) | ×1 |

---

## NPCs

| Spawner | Count | Notes |
|---------|-------|-------|
| NPC 0x6e (Oglin) | 31 | Scattered throughout all sub-areas |
| NPC 0x42 (Roller) | 12 | Mid/upper cave areas |
| NPC 0x74 (Grub) | 8 | Various sections |

---

## Notes

- The 16 scroll-zone tiles (Pattern B) call sub `0x97d39d` which interpolates the camera viewport between two rectangles over several frames. They are always placed in pairs — one for each direction of travel.
- The "reverse" scroll tiles (`$2836=0xfffe`, `$283a=0xfffe`) move the camera in the opposite direction.
- Sniff spots #1–#3 (Oil) share the same `$22bc` byte as Horace's Camp sniff spots #10–#14 (bits 0x01–0x10). These addresses are unambiguously separated by bit position.
- `$22f4&0x01` must be set externally (before first entry). When set, the boy shows an exploration animation before the cave intro. Not set/cleared within this room.
- The Call Beads gourd uses `$2287&0x40` — a shared flag byte (`$2287`) also used by other Act 2/Act 3 rooms.
