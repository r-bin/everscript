# Room 0x73 — Gothica: Ivor Tower Dog Maze Underground

| Field | Value |
|-------|-------|
| **Room ID** | 0x73 |
| **Act** | 3 — Gothica |
| **Data** | `0x9cf0c2` |
| **Enter script** | `0x92825a` → `0x9894ed` |
| **Dog sprite** | Poodle (default — boy unavailable) |
| **Music** | 0x5c (underground/dungeon) |
| **Step-ons** | 28 entries |
| **B-triggers** | 0 entries |
| **Connections** | 0x71 (East Room + Kitchen, 15 exits), 0x72 (East Upper Floor, 5 exits) |

---

## Overview

The underground ventilation/crawlspace network beneath Ivor Tower's east wing — a dog-only maze. This room is entered exclusively by falling through vent grates in 0x71 or 0x72. Features:
- **Boy is always hidden** (`$2261|=0x02`); dog is sole player character
- **"Dog Maze Lady"** NPC (NPC 53, talk script 0x19b6) at `[f7,0d]` — guides the dog; activates only when `$2834&0x01` not yet set
- **Guard patrol tiles** — 4 patrol positions use game-timer gates; OBJ 0/1/2 toggle in/out to simulate guards walking past. If `$2834&0x01` is set, all guards are silent
- **20 exit grates** — dog climbs back up through holes in the ceiling to 0x71 or 0x72
- **No sniff spots or gourds** in this room

---

## Enter Logic

1. If NOT `$22eb&0x20`: teleport both to `[b7,51]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. CALL 0x92d8ff WITH arg 0x40 (camera/display setup)
4. Play music 0x5c (if not already playing)
5. Unhide text; stop both characters
6. Boy unavailable (`$2261|=0x02`); teleport boy to `[0,0]`
7. Switch to dog control
8. Load NPC 53 at `[f7,0d]` → `$2841`; set talk script 0x19b6 (arg 0x40) — "Dog Maze Lady"
9. Teleport NPC 53 to `[0,0]`
10. Read dog position; adjust y by −0x37 (55 px upward — dog spawn point is above vent landing zone)
11. RCALL 0x989434 — "dog rises from vent" animation:
    - If `$238f==1`: dog faces east; else faces west
    - Brightness ramps 10→14 over 10 ticks (dog materializes from dark)
    - Dog teleports northward incrementally (falls "into" room from above, reversed visually)
    - Final standing pose
12. Walk dog based on `$238f`:
    - 0x0001: east by 3 tiles
    - 0x0002: west by 3 tiles
    - 0x0003: south by 3 tiles
    - 0x0004: north by 3 tiles
13. Dog = player controlled; `$238f=0x0000`

---

## Step-On Table

### Guard Patrol Timers (6 entries)

All guard triggers check a time-since-last-event register. If enough frames have elapsed (threshold varies), they play sound 0x5c and toggle guard OBJs briefly. All are gated by `$2834&0x01`: **if bit set → no guard activity**.

| Tile(s) | Timer reg | Threshold | OBJ(s) toggled | Sleep |
|---------|-----------|-----------|----------------|-------|
| `[68,09:69,0a]` + `[6b,18:6c,19]` *(shared)* | `$283f` | >500 frames | OBJ 1 | 89 ticks |
| `[68,0f:69,10]` | `$2835` | >500 frames | OBJ 0 + OBJ 2 | 39 ticks |
| `[6d,09:6e,0a]` | `$2837` | >800 frames | OBJ 0 + OBJ 2 | 39 ticks |
| `[71,16:72,17]` | `$283b` | >300 frames | OBJ 0 + OBJ 2 | 39 ticks |
| `[72,09:73,0a]` | `$2839` | >300 frames | OBJ 0 + OBJ 2 | 39 ticks |
| `[79,0e:7a,0f]` | `$283d` | >200 frames | OBJ 0 + OBJ 2 | 39 ticks |

### Dog Maze Lady Trigger (1 entry)

`[76,06:77,07]` — Only fires if `$2834&0x01` is NOT set:
- Untraced instruction (likely set up NPC position to dog coords)
- `$2834|=0x01` (mark NPC as activated)
- Toggle OBJ 0; teleport `$2841` (Dog Maze Lady) to dog position; make her AI-controlled

### Exit Grates → 0x71 / 0x72 (all use shared "dog rises" animation at 0x9892fa/0x989301)

All exits: sound 0x5a; dog rises animation (brightness 13→0 over 14 ticks, teleporting upward); `$238f=0x0005`; CHANGE MAP.

`$24b3=1` → dog faces east when rising; `$24b3=0` → dog faces west.

| Tile | `$24b3` | `$234b` | Destination | Dest coords |
|------|---------|---------|-------------|-------------|
| `[11,05:13,07]` | 0 | 0x0004 | 0x71 | `[0x0128\|0x0098]` |
| `[31,05:33,07]` | 1 | 0x0004 | 0x71 | `[0x02e8\|0x0098]` |
| `[56,08:58,0a]` | 1 | 0x0004 | 0x71 | `[0x04f8\|0x0098]` |
| `[4d,08:4f,0a]` | 0 | 0x0008 | 0x71 | `[0x0478\|0x0098]` |
| `[67,03:69,05]` | 1 | 0x0004 | 0x71 | `[0x05d8\|0x0088]` |
| `[03,1a:05,1c]` | 0 | 0x0004 | 0x72 | `[0x0098\|0x0118]` + `$234b\|=0xa0` |
| `[31,17:33,19]` | 0 | 0x0008 | 0x71 | `[0x02e8\|0x0218]` |
| `[3b,17:3d,19]` | 0 | 0x0008 + `$238f=0x0002` | 0x71 | `[0x0348\|0x0228]` |
| `[49,13:4b,15]` | 1 | 0x0004 | 0x71 | `[0x03f8\|0x0228]` |
| `[5d,14:5f,16]` | 1 | 0x0008 | 0x71 | `[0x0538\|0x0218]` |
| `[6d,17:6f,19]` | 1 | 0x0008 | 0x71 | `[0x0668\|0x0228]` |
| `[7c,19:7e,1b]` | 0 | 0x0008 | 0x72 | `[0x0338\|0x0118]` + `$234b\|=0xb0` |
| `[7c,35:7e,37]` | 1 | 0x0008 | 0x72 | `[0x0338\|0x0338]` + `$234b\|=0xb0` |
| `[02,29:05,2a]` | 0 | 0x0008 | 0x72 | `[0x0098\|0x0228]` + `$234b\|=0xa0` |
| `[02,37:05,38]` | 1 | 0x0004 | 0x72 | `[0x0098\|0x0338]` + `$234b\|=0xa0` |
| `[2b,28:2d,2a]` | 0 | 0x0008 | 0x71 | `[0x0288\|0x03b8]` |
| `[3b,28:3d,2a]` | 0 | 0x0008 | 0x71 | `[0x0368\|0x03b8]` |
| `[4a,26:4c,28]` | 1 | 0x0004 | 0x71 | `[0x03f8\|0x03b8]` |
| `[5a,2a:5c,2c]` | 1 | 0x0004 | 0x71 | `[0x04d8\|0x03b8]` *(+`$234b=$234b+1`)* |
| `[3d,41:3f,43]` | 1 | 0x0008 | 0x71 | `[0x03a8\|0x05e8]` |

---

## Memory Access

| Address | Bits | Type | Description |
|---------|------|------|-------------|
| `$2261` | 0x02 | ⚙️ | Boy unavailable (always set on enter) |
| `$2834` | 0x01 | 📖 | Dog Maze Lady activated / guard alert cleared |
| `$238f` | word | ⚙️ | Vent entry direction (0x0001–0x0004); 0x0005 = exit animation active |
| `$234b` | word | 📖 | Exit context code; high nibble 0xa0/0xb0 = which half of 0x72 to show |
| `$2841` | word | ⚙️ | Dog Maze Lady NPC pointer |
| `$283f` | word | ⚙️ | Guard 1 patrol timestamp (game timer at last OBJ toggle) |
| `$2835` | word | ⚙️ | Guard 2 patrol timestamp *(MISMATCH: `$2835` also used for Queen's Key Door bits in 0x71)* |
| `$2837` | word | ⚙️ | Guard 3 patrol timestamp |
| `$2839` | word | ⚙️ | Guard 4 patrol timestamp |
| `$283b` | word | ⚙️ | Guard 5 patrol timestamp *(MISMATCH: `$283b`–`$2843` used for Pierre NPC in 0x71)* |
| `$283d` | word | ⚙️ | Guard 6 patrol timestamp |

## Notes

- A dog-only navigation room: the boy is always hidden (`$2261|=0x02`) on entry; no gourds, sniff spots, or enemies — only timed guard patrol obstacles.
- Guard patrol timestamps (`$283f`, `$2835`, `$2837`, `$2839`, `$283b`, `$283d`) overlap with NPC pointer slots used by 0x71 (Queen's Key Doors and Chef Pierre). These are session-only values, not persistent saves.
- `$2834&0x01` flags the Dog Maze Lady as activated; once set, guard-alert mechanics change behavior.
