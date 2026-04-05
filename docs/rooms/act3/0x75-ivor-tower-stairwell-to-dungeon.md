# Room 0x75 — Gothica: Ivor Tower Stairwell to Dungeon

| Field | Value |
|-------|-------|
| **Room ID** | 0x75 |
| **Act** | 3 — Gothica |
| **Data** | `0x9fffbb` |
| **Enter script** | `0x928264` → `0x98b172` |
| **Dog sprite** | Poodle (`$2443=0x08` on enter) |
| **Music** | 0x5c (dungeon) |
| **Step-ons** | 2 entries |
| **B-triggers** | 0 entries |
| **Connections** | 0x71 (East Room + Kitchen), 0x74 (Ebon Keep Dungeon + pipe room) |

---

## Overview

A small transitional stairwell connecting Ivor Tower's east wing to the dungeon below (0x74). Entered from 0x71 via the dog-only dungeon entrance grate. Two exits: back to 0x71, or down into 0x74. If the west castle has collapsed (`$22e5&0x40`), OBJ 0–4 are all force-unloaded on entry (the castle is in ruins).

---

## Enter Logic

1. If NOT `$22eb&0x20` (in animation): teleport both to `[21,3d]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. `$2443 = 0x08` (Poodle)
4. If `$22e5&0x40` (west castle collapsed): unload OBJ 0–4
5. If music not locked: PLAY MUSIC 0x5c; fade in

---

## Step-On Table

| Tile(s) | Destination | Notes |
|---------|-------------|-------|
| `[1a,17:1e,19]` | → 0x71 `[06c0, 0118]` (Ivor Tower East Room + Kitchen) | `$234b = 0x0064` |
| `[26,28:2a,2a]` | → 0x74 `[0170, 0088]` (Ebon Keep and Ivory Tower dungeon + pipe room) | — |

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$22e5` | 0x40 | R | West castle collapsed |
| `$2443` | word | W | Dog sprite (`0x08` = Poodle) |
| `$238d` | word | R | Music lock |
| `$234b` | word | W | Entry source code (0x0064 = from south/dungeon entrance) |

## Notes

- A minimal transit stairwell with no gourds, enemies, or sniff spots; its only role is connecting 0x71 (East Room) to 0x74 (Dungeon).
- West castle collapse (`$22e5&0x40`) force-unloads all 5 OBJs on entry — the stairwell's visual state changes permanently after the Act 3 collapse event.
- `$234b=0x0064` is set when exiting north to 0x71, positioning the player at the dungeon-entrance grate in 0x71's layout.
