# Room 0x72 — Gothica: Ivor Tower East Upper Floor

| Field | Value |
|-------|-------|
| **Room ID** | 0x72 |
| **Act** | 3 — Gothica |
| **Data** | `0xa88000` |
| **Enter script** | `0x928255` → `0x98903f` |
| **Dog sprite** | Poodle (0x08) |
| **Music** | 0x82 |
| **Step-ons** | 19 entries |
| **B-triggers** | 18 entries |
| **Connections** | 0x70 (Exterior Bridges, 3 levels × 2 sides), 0x71 (East Room, east/west), 0x73 (Dog Maze Underground, 5 vents) |

---

## Overview

The upper floor of Ivor Tower's east wing — a long balconied corridor above the main hall. Features:
- **6 key rooms** (3 east, 3 west) — dog retrieves keys here while boy is unavailable; each key sets a `$2834`/`$2835`/`$2836` bit that unlocks a Queen's Key Door in 0x71
- **5 vent grates** dropping dog to 0x73 (underground maze), same mechanic as 0x71
- **3-level east/west exits** to the exterior balconies (0x70) at y = 0x0078, 0x00c8, 0x0118
- **14 sniff spots** and **2 gourds**
- OBJ persistence for sniff spots (flags `$22d3`–`$22d5`) and west-castle collapse (OBJs 9–18)

---

## Enter Logic

1. If `$22f4&0x02` OR `$2261&0x02`: set `$2261|=0x02` (boy unavailable), disable SELECT, teleport boy to `[0,0]`
2. If NOT `$22eb&0x20`: teleport both to `[0f,5f]`; fade music
3. If `$22eb&0x20`: clear in-animation flag; play music 0x82
4. Dog = Poodle (0x08)
5. OBJ unload for sniff/gourd persistence: `$22d3`–`$22d5` bits → OBJs 19–31, 0x20; `$22d7&0x40` → OBJ 7; `$22d7&0x80` → OBJ 8
6. If `$22e5&0x40` (West castle collapsed): toggle OBJs 9–18; `$2437=0x0007`
7. Extract `$234b` high nibble (0xa0 or 0xb0) → set camera scroll limits:
   - 0xa0: left-half view `[0,0]→[0x01c0,0x03a0]`
   - 0xb0: right-half view `[0x0210,0]→[0x03c0,0x03a0]`
8. Extract `$234b` low nibble:
   - Bit 3 (`0x08`): teleport non-controlled to `[0,0]`; RCALL enter-right (−16) → **END**
   - Bit 2 (`0x04`): teleport non-controlled to `[0,0]`; RCALL enter-left (+16) → **END**
   - Default: cinematic (fade-up from floor) → **END**
9. `$238f=0x0000`; `$234b=0x0000` → **END**

---

## Step-On Table

### Key Rooms (6 entries — only active when `$2261&0x02` OR `$22f4&0x02`)

Each room sets a `$2834` bit (which unlocks a Queen's Key Door in 0x71) and plays sound 0x46. Once set the bit is persistent; re-entering the tile is a no-op.

| Tile | Bit | Effect |
|------|-----|--------|
| `[30,13:34,15]` | `$2834&0x01` → set | Toggle OBJ 0 (key pickup) |
| `[4f,13:53,15]` | `$2834&0x20` → set | Toggle OBJ 5 |
| `[4f,21:53,23]` | `$2834&0x10` → set | Toggle OBJ 4 |
| `[30,21:34,23]` | `$2834&0x02` → set | Toggle OBJ 1 |
| `[30,32:34,34]` | `$2834&0x04` → set | Toggle OBJ 2 |
| `[4f,32:53,34]` | `$2834&0x08` → set | Toggle OBJ 3 |

> Note: These bits in `$2834` correspond to Queen's Key Door positive args 1–6 in room 0x71. The upper-floor key rooms feed the lower-floor locked doors.

### Vent Grates → 0x73 (Dog Maze Underground)

Same shared subroutine as 0x71. Boy dialog: *"Hmmm... This looks dangerous. I'd better avoid these vents."* Dog companion dialog: *"Hey, [dog]! Don't go near the edge!"*

| Tile | Walk dir | `$238f` | MAP 0x73 coords |
|------|----------|---------|----------------|
| `[2d,16:2e,17]` | east (+1) | 0x0001 | `[0x0038\|0x01b8]` |
| `[2b,27:2c,28]` | west (−1) | 0x0003 | `[0x0038\|0x0288]` |
| `[2d,38:2e,39]` | east (+1) | 0x0003 | `[0x0038\|0x0368]` |
| `[55,16:56,17]` | west (−1) | 0x0003 | `[0x07d0\|0x0198]` |
| `[55,38:56,39]` | west (−1) | 0x0002 | `[0x07d0\|0x0368]` |

### Room Exits (8 entries)

| Tile | Destination | Coords | `$234b` high nibble |
|------|-------------|--------|---------------------|
| `[3c,21:3e,23]` | 0x71 East Room | `[0x0018\|0x02c0]` | 0x10 (left entry) |
| `[44,21:46,23]` | 0x71 East Room | `[0x0748\|0x02c0]` | 0x11 (right entry) |
| `[24,11:26,13]` | 0x70 Ext. Bridges | `[0x01f8\|0x0078]` | 0xa0 |
| `[24,22:26,24]` | 0x70 Ext. Bridges | `[0x01f8\|0x00c8]` | 0xa0 |
| `[24,33:26,35]` | 0x70 Ext. Bridges | `[0x01f8\|0x0118]` | 0xa0 |
| `[5d,11:5f,13]` | 0x70 Ext. Bridges | `[0x0278\|0x0078]` | 0xb0 |
| `[5d,22:5f,24]` | 0x70 Ext. Bridges | `[0x0278\|0x00c8]` | 0xb0 |
| `[5d,33:5f,35]` | 0x70 Ext. Bridges | `[0x0278\|0x0118]` | 0xb0 |

---

## B-Triggers (18 entries)

### Sniff Spots (14 spots)

| Tile | Flag | Item | MAP REF | NEXT ADD |
|------|------|------|---------|----------|
| `[29,39:2a,3a]` | `$22d3&0x40` | 🌿 Iron | 0x0013 | 0x0001 |
| `[58,16:59,17]` | `$22d3&0x80` | 🌿 Iron | 0x0014 | 0x0001 |
| `[34,17:35,18]` | `$22d4&0x01` | 🌿 Ash | 0x0015 | 0x0001 |
| `[4a,3d:4b,3e]` | `$22d4&0x02` | 🌿 Ash | 0x0016 | 0x0001 |
| `[29,2e:2a,2f]` | `$22d4&0x04` | 🌿 Ethanol | 0x0017 | 0x0001 |
| `[55,0b:56,0c]` | `$22d4&0x08` | 🌿 Ethanol | 0x0018 | 0x0001 |
| `[37,0e:38,0f]` | `$22d4&0x10` | 🌿 Feather | 0x0019 | 0x0001 |
| `[55,1d:56,1e]` | `$22d4&0x20` | 🌿 Feather | 0x001a | 0x0001 |
| `[38,3d:39,3e]` | `$22d4&0x40` | 🌿 Feather | 0x001b | 0x0001 |
| `[2d,2e:2e,2f]` | `$22d4&0x80` | 🌿 Acorns | 0x001c | 0x0001 |
| `[2b,1d:2c,1e]` | `$22d5&0x01` | 🌿 Acorns | 0x001d | 0x0001 |
| `[59,28:5a,29]` | `$22d5&0x02` | 🌿 Acorns | 0x001e | 0x0001 |
| `[54,2e:55,2f]` | `$22d5&0x08` | 🌿 Water | 0x001f | 0x0001 |
| `[2e,0c:2f,0d]` | `$22d5&0x04` | 🌿 Water | 0x0020 | 0x0001 |

> ⚠️ `[2e,0c:2f,0d]` (id:146d) appears twice in the B-trigger table — possible duplicate entry in ROM.

### Gourds (2 gourds)

| Tile | Flag | Item | MAP REF |
|------|------|------|---------|
| `[2b,0c:2d,0d]` | `$22d7&0x40` | 🫙 Wax | 0x0007 |
| `[58,2e:5a,2f]` | `$22d7&0x80` | 🫙 Roots | 0x0008 |

---

## Memory Access

| Address | Bits | Type | Description |
|---------|------|------|-------------|
| `$234b` | word | 📖 | Entry code: high nibble 0xa0/0xb0=camera zone; low nibble 0x04/0x08=walk-in direction |
| `$22e5` | 0x40 | 📖 | West castle collapsed |
| `$22f4` | 0x02 | 📖 | Boy in special entry state |
| `$2261` | 0x02 | ⚙️ | Boy unavailable flag |
| `$2834` | 0x01–0x20 | 📖 | Key rooms found (bits 0x01–0x20 = keys 1–6, unlock doors in 0x71) |
| `$22d3` | 0x40–0x80 | 👃 | Sniff spots: Iron×2 |
| `$22d4` | 0x01–0x80 | 👃 | Sniff spots: Ash×2, Ethanol×2, Feather×3, Acorns×1 |
| `$22d5` | 0x01–0x08 | 👃 | Sniff spots: Acorns×2, Water×2 |
| `$22d7` | 0x40–0x80 | 🫙 | Gourds: Wax, Roots |
| `$2437` | word | 🎥 | Camera scroll limits (0x0007 if west castle collapsed) |
| `$238f` | word | ⚙️ | Vent entrance selector (0x0001–0x0003 → which area of 0x73) |

## Notes

- Six key rooms (3 east, 3 west) each contain a key that sets a `$2834` bit (bits 0x01–0x20 = keys 1–6) to permanently unlock the corresponding Queen's Key Door in 0x71.
- Camera zone on entry is selected by `$234b` high nibble (`0xa0` or `0xb0`), shared with 0x70 (Exterior Bridges) and 0x71 vent-exit routing.
- Boy-unavailable state (`$2261&0x02`) is set here — this is a dog-only area during the key-hunt sequence.
