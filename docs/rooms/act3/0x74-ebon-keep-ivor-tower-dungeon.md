# [0x74] Gothica — Ebon Keep / Ivor Tower Dungeon and Pipe Room

| Field | Value |
|-------|-------|
| Room ID | 0x74 |
| Name | Gothica - Dungeon and Pipe Room |
| Act | Act 3 — Gothica |
| Data offset | `0xa49d43` |
| Enter script | `0x92825f` → `0x98afe0` |
| Step-ons | ~32 |
| B-triggers | 1 |
| Music | 0x72 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | ~32 (7 prison doors + 6 pipe exits + staircase + damage zones + misc) |
| B-triggers | 1 |
| Gourds | 0 |
| Sniff spots | 0 |
| Rare/key items | 1 (Iron Bracer `GLOVE_3_1` — west castle B-trigger, `$22d8&0x04`) |
| Enemies | NPC spawners (enemy config set on entry) |
| NPCs | Guard NPC `$2849` (NPC 0xaa>>1=0x55) at `[2f,0d]` — cutscene only |
| Forced dog form | Poodle (0x08) |
| Music | 0x72 |

**Drop table**:

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| 1 | 🧪 Honey (0x0801) | 6/12 | 1 |
| 2 | 💰 Currency (0x0001) | 4/12 | 0x55 (85) |
| 3 | 🌿 Feather (0x020c) | 2/12 | 1 |

---

## Overview

A shared dungeon map used for **both** the Ebon Keep (west castle, NOT `$22dd&0x40`) and Ivor Tower (east castle, `$22dd&0x40`) story paths. The room logic branches heavily on `$22dd&0x40` (Load east castle flag) to determine which prison story is active.

**West castle path**: Boy and dog are thrown into a cell by a guard (`$2849`) in a cutscene on first entry (`$2351 == 0`). Dog crawls through a pipe hole and gains player control. Exploring the dungeon opens 7 prison doors tracked by `$22f4` and `$22f5`. Exit via the NE staircase (`[37,12:39,14]`) to room 0x75 once `$2351 != 0`. There is also a hidden B-trigger item (Iron Bracer `GLOVE_3_1`) at `[2a,1b:2b,1c]` that uses the `"Loot nature?"` (0x39) function and persists via `$22d8&0x04`.

**East castle path**: No getting-thrown-in cutscene; castle layout variant with Verminator. Exit via the NE staircase to Ebon Keep (0x0d) once Verminator is dead (`$22dd&0x01`).

**Pipe room**: Six step-ons drop the player through pipes to the Ivor Tower sewers (0x79), with `$2843` set to values 2–7 to identify which pipe was used.

---

## Enter Script Logic

**Branch A — Prison already escaped** (if `$2351 != 0` [west] OR `$234f != 0` [east]):
1. Set all 7 prison door flags open: `$22f4 |= 0xf8`, `$22f5 |= 0x03`
2. Unload door and lock OBJs: 0,1,2,3,4,5,7,8,9,10,11,12,13,14
3. If east castle AND Verminator dead (`$22dd&0x01`): unload OBJ 6 also
4. `$23bf = 0x0001`

**Branch B — Fresh entry** (prison not escaped):
1. Clear all 7 prison door flags: `$22f4 &= ~0xf8`, `$22f5 &= ~0x03`
2. `$283d = 0x0005`; `$23bf = 0x0000`
3. If west castle: set dog script `0x19c5` (dog dies in prison?)
4. If east castle: unload OBJs 9+10; `$2437 = 0x0007`

**Shared continue**:
5. If `$22eb&0x20` (in-animation guard): teleport both to `[52,1b]`, fade-out
6. Set dog = Poodle (`$2443 = 0x08`); enemy config; drop table
7. Music 0x72 if `$238d == 0x00`
8. If east castle AND `$234f == 0` (not yet escaped east): run east-castle arrival (OBJ 9+10 animation)
9. If west castle AND `$2351 == 0` (not yet escaped west): run **getting-thrown-in cutscene** (see below)

---

## Getting-Thrown-In Cutscene (West Castle, First Entry)

1. Load guard NPC `$2849` = NPC 0xaa>>1=0x55 at `[2f,0d]`
2. Animate boy+dog+guard falling/walking into cell
3. Guard: *"OK, boys. Welcome to your new home. Now, get in there!"*
4. Boy and dog placed in cell; prison door closes
5. Guard: *"Make yourselves comfy. You're going to be here a long time."*
6. Guard walks away; dog is directed to the pipe hole:
   *"[boy], see if you can fit through this hole in the wall!"*
7. Dog crawls through pipe hole → dog gains player control (`$2261 &= ~0x01`), boy becomes unavailable (`$2261 |= 0x02`)

---

## Prison Door Step-Ons (West Castle)

Each door tile pair triggers an open/locked sequence. Once opened, the door number is written to `$2351` (west) or `$234f` (east).

| Door # | Flag | Tile |
|--------|------|------|
| 1 | `$22f4&0x08` | `[2f,1d:30,1e]` |
| 2 | `$22f4&0x10` | `[42,16:43,17]` |
| 3 | `$22f4&0x20` | `[48,1c:49,1d]` |
| 4 | `$22f4&0x40` | `[4f,2b:50,2c]` |
| 5 | `$22f4&0x80` | `[46,2d:47,2e]` |
| 6 | `$22f5&0x01` | `[33,2b:34,2c]` |
| 7 | `$22f5&0x02` | `[28,26:29,27]` |

Door behavior:
- If `$2834&0x01` (dog has key): auto-open animation, sets flag, updates `$2351`/`$234f`
- **West castle, no key**: doors auto-open when stepped on (most doors call `0x98ab37` after opening); door 1 triggers boy-release cutscene (`$2834&0x04` one-time flag)
- **East castle, no key**: shows "Won't Budge" (`c2115a`) — player must acquire key before opening

---

## Pipe Step-Ons

**West castle** (when `$2351 == $2843`): All lead to MAP 0x79 (Ivor Tower Sewers) @ `[0x0248|0x0068]` via falling animation.

**East castle** (when `$234f == $2843` OR `$2843 == 3`):
- `$2843 == 3` always exits to MAP 0x12 (Ebon Keep sewers) @ `[0x03d0|0x0058]`
- Other pipes: exit to MAP 0x7b (Ebon Keep / Ivor Tower Exterior Bottom) @ `[0x0538|0x01f8]`

| Tile | `$2843` Value |
|------|--------------|
| `[43,14:46,15]` | 0x0002 |
| `[48,19:4c,1a]` | 0x0003 |
| `[49,28:4e,29]` | 0x0004 |
| `[42,2a:47,2b]` | 0x0005 |
| `[2f,28:34,29]` | 0x0006 |
| `[25,23:29,24]` | 0x0007 |

---

## Other Step-Ons

| Tile | Destination | Notes |
|------|-------------|-------|
| `[37,12:39,14]` | MAP 0x0d @ `[0x0038\|0x0298]` | If east castle AND Verminator dead → Ebon Keep (0x0d) |
|  | MAP 0x75 @ `[0x0110\|0x0228]` | If west castle AND `$2351 != 0` → escape stairwell |
|  | (locked) | Otherwise → "Locked" (SOUND 0x3c) |
| `[22,28:23,29]` | (damage) | Periodic damage (ticks after 0x78 frames); west castle only |
| `[3e,1e:3f,20]` | (damage) | As above |
| `[4e,1d:4f,1f]` | (damage) | As above |

---

## B-Trigger Scripts

| Tile | Condition | Action |
|------|-----------|--------|
| `[2a,1b:2b,1c]` | If east castle | Mazquito bite — proportional damage based on speed stat |
|  | If west castle + boy | 💎 Hidden item: Iron Bracer `GLOVE_3_1` (0x041f) via `"Loot nature?"` (0x39) — `$22d8|=0x04` (#0) |

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22dd` | 0x40 | R | ⚙️ Load east castle — primary branch condition for all dungeon logic |
| `$22dd` | 0x01 | R | 📖 Verminator dead — gates east-castle staircase exit to 0x0d |
| `$22f4` | 0x08 | R/W | 📖 Prison door 1 open |
| `$22f4` | 0x10 | R/W | 📖 Prison door 2 open |
| `$22f4` | 0x20 | R/W | 📖 Prison door 3 open |
| `$22f4` | 0x40 | R/W | 📖 Prison door 4 open |
| `$22f4` | 0x80 | R/W | 📖 Prison door 5 open |
| `$22f5` | 0x01 | R/W | 📖 Prison door 6 open |
| `$22f5` | 0x02 | R/W | 📖 Prison door 7 open |
| `$234f` | — | R/W | 📖 East castle prison exit door number (nonzero = escaped) |
| `$2351` | — | R/W | 📖 West castle prison exit door number (nonzero = escaped) |
| `$22d8` | 0x04 | W | 💎 Hidden item: Iron Bracer `GLOVE_3_1` (0x041f) in Dungeon (#0) [0x74] (0x04) — west castle B-trigger; uses `"Loot nature?"` (0x39); flag set via `$22ea&0x01` |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$2261` | 0x01 | W | ⚙️ Dog available flag (cleared after cutscene until dog crawls) |
| `$2261` | 0x02 | W | ⚙️ Boy unavailable flag (set after cutscene) |
| `$2834` | 0x01 | R | ⚙️ Dog has key — auto-opens prison doors |
| `$2437` | — | W | ⚙️ Set to 0x0007 on east castle entry |
| `$283d` | — | W | ⚙️ Set to 0x0005 on fresh entry |
| `$2843` | — | W | ⚙️ Pipe exit index (0x0002–0x0007) for sewers routing |
| `$2849` | — | W | ⚙️ Guard NPC pointer (NPC 0x55 at `[2f,0d]`) |
| `$23bf` | — | W | ⚙️ 0x0001 if escaped, 0x0000 otherwise |
| `$2443` | — | W | ⚙️ Dog form forced to Poodle (0x08) |

## Notes

- A dual-context room: `$22dd&0x40` (Load east castle) determines whether the Ebon Keep dungeon (west) or the Ivor Tower dungeon (east) is active — the same map data serves both narrative segments.
- Seven prison doors have individual persistence flags (`$22f4` bits 0x08–0x80 and `$22f5` bits 0x01–0x02); when the dog has the key (`$2834&0x01`) all doors open automatically.
- The pipe exit index (`$2843`, values 0x0002–0x0007) determines which sewer entry point in 0x79 the player arrives at after escaping through a pipe.
