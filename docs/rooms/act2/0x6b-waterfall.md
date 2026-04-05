---
room: 0x6b
name: Antiqua – Waterfall
act: act2
data: 0xa99047
---

# 0x6b — Antiqua – Waterfall

| Field | Value |
|-------|-------|
| Room ID | 0x6b |
| Full Name | Antiqua – Waterfall |
| Act | 2 (Antiqua) |
| Data block | 0xa99047 |
| Enter script | 0x928232 → 0x97dd60 |
| Step-on table | 0xa99056 (7 entries, 0x2a bytes) |
| B-triggers | none |

## Overview

The Waterfall room is an outdoor area where the WindWalker barrel ride terminates. Players who have not yet unlocked the WindWalker can step onto the waterfall barrel launch tiles to ride down through a cinematic sequence into the Oglin Cave (0x4b). Once the WindWalker is unlocked (`$22dc&0x08`), the barrel tiles are blocked with "Been there, done that." The room also connects south to Horace's camp (0x2f).

The enter script spawns two combat enemies (NPC 0x28) and one interactive NPC (0x1e), configures prize drop rates, and plays music track 0x46.

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$22dc` | read | &0x08 | WindWalker unlocked — if set, barrel ride is blocked ("Been there, done that") |
| `$22eb` | R/W | &0x20 | In-animation flag — if set on entry, teleport both chars to [0x0f, 0x3d] and fade music; cleared on normal entry |
| `$22f4` | write | \|=0x01 | Set immediately before CHANGE MAP to 0x4b; tells Oglin cave which entry point to use |

## Enter Script Summary (`0x97dd60`)

1. **Entry routing**: if `$22eb&0x20` is set (came from a cinematic), teleport both characters to [0x0f, 0x3d] and fade music out; otherwise clear the flag.
2. Set `$23c1 = 1`, `$2437 = 7` (room state and barrel status).
3. Configure prize drop table:
   - PRIZE 1: item `0x0804`, rate 10
   - PRIZE 2: item `0x0001`, rate 3, qty 70
   - PRIZE 3: item `0x0802`, rate 1
4. Spawn NPC 0x28 at [0x0f, 0x25] and [0x11, 0x37] (combat enemies).
5. Set `$2433 = 10` (enemy counter or spawn cap).
6. Load NPC 0x0f (0x001e>>1) with flags 0x8400 at pos [0x23, 0x11].
7. Play music track 0x46 (if not already playing); fade in.
8. Set `$23bf = 0`; call cinematic setup script 0x92de75.

## Step-on Scripts (7 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [0d,0f:0e,10] | `0x97da0d` | **Barrel launch** — if `$22dc&0x08` (WW unlocked): "Uh, I don't think so. Been there, done that." / dog says "Urf-urf.", push player back west; else: animate full barrel-ride cinematic down the waterfall, then CHANGE MAP to 0x4b (Oglin cave) at [0x120, 0x640]; sets `$22f4|=0x01` before map change |
| [0d,10:0e,11] | `0x97da0d` | Barrel launch (tile 2 of 6) |
| [0d,11:0e,12] | `0x97da0d` | Barrel launch (tile 3 of 6) |
| [0e,11:0f,12] | `0x97da0d` | Barrel launch (tile 4 of 6) |
| [0e,12:0f,13] | `0x97da0d` | Barrel launch (tile 5 of 6) |
| [0f,12:10,13] | `0x97da0d` | Barrel launch (tile 6 of 6) |
| [06,21:0a,22] | `0x97da05` | **EXIT south** → 0x2f (Horace's camp) at [0x298, 0x020] |

## Exits

| Tiles | Destination | Coordinates | Condition |
|-------|-------------|-------------|-----------|
| [0d,0f:10,13] (6 tiles) | 0x4b — Oglin cave | [0x120, 0x640] | step-on; only if `$22dc&0x08` = 0 |
| [06,21:0a,22] | 0x2f — Horace's camp | [0x298, 0x020] | step-on |

## B-Triggers

None.

## NPCs

| NPC id | Qty | Position | Notes |
|--------|-----|----------|-------|
| 0x28 | 2 | [0x0f,0x25], [0x11,0x37] | Combat enemies spawned at room entry |
| 0x0f (0x001e>>1) | 1 | [0x23,0x11] | Flags 0x8400; interactive NPC — identity unresolved |

## Notes

- The barrel-ride cinematic (script `0x97da0d`) is a multi-phase animation: the barrel slides along the waterfall path across several screen-coordinate waypoints before fading to black and loading 0x4b. The sub at `0x97dc0a` handles path-following animation with speed and direction arguments.
- The WindWalker barrel can only be ridden **once**: `$22f4&0x01` is set before the map change to 0x4b, permanently blocking re-entry via the "Been there, done that." guard (`$22dc&0x08` check).
- `$22eb&0x20` entry teleport is used when transitioning from an animation state (e.g. landing from a different room cinematic). Normal walk-in entry just clears the flag.
