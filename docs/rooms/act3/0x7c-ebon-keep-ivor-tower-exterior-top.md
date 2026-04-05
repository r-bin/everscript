# 0x7c — Ebon Keep + Ivor Tower Exterior (Top Half)

**Act:** 3 — Gothica  
**Script address:** `0x9fff97` (0x7c block)  
**Music:** `MUSIC.EBON_KEEP` (0x62) or `MUSIC.DRAGON_ROAR` (0x6a) — same formula as 0x7b  
**Dog sprite:** Poodle (0x08)

## Overview

Upper half of the dual-castle exterior, directly above 0x7b. Contains seven doors leading into the castles' upper-floor interiors (→0x7d, `$234b` 5–9), two lower exits (→0x7b), and the top gate leading to either Ebon Keep Courtyard (0x5d) or Ivor Tower Hall (0x6e) depending on castle state. No B-triggers — all interaction is via step-ons.

A special pig-race winner entry (`$234b == 0x89`, set externally by the pig-race sub-system) triggers a cutscene in which a guard NPC challenges the player and, upon recognizing them as the pig-race winner, opens the main gate (`OBJ 0 state 0x7e`) and sets `$22e8|=0x10`.

## Music Dispatch

Identical formula to 0x7b:

```
if ($22dd & 0x40) != ($22dc & 0x08):
  if ($22dd & 0x40) or ($22dc & 0x08): → MUSIC.EBON_KEEP (0x62)
  else:                                 → MUSIC.DRAGON_ROAR (0x6a)
```

## Connections

| Direction | Tile range | Destination | Notes |
|-----------|-----------|-------------|-------|
| South | `[26,3b:28,3d]` | MAP 0x7b @ `[0x0100 \| 0x0008]` | Down to bottom exterior |
| Castle approach gate | `[35,06:39,08]` | MAP 0x5d — Ebon Keep Courtyard | if `$22dd&0x40` (east castle) |
| Castle approach gate | `[35,06:39,08]` | MAP 0x6e — Ivor Tower Hall | if NOT `$22dd&0x40` (west castle) |
| Interior door (W) 1 | `[2c,34:2e,35]` | MAP 0x7d @ `$234b=5` west | `[0x0080 \| 0x0238]` |
| Interior door (W) 2 | `[38,34:3a,35]` | MAP 0x7d @ `$234b=5` east | `[0x0458 \| 0x0238]` |
| Interior door (E) 1 | `[50,34:52,35]` | MAP 0x7d @ `$234b=6` | `[0x0390 \| 0x03c8]` |
| Interior door (E) 2 | `[67,34:69,35]` | MAP 0x7d @ `$234b=7` | `[0x0390 \| 0x03c8]` |
| Interior door (E) 3 | `[5d,17:5f,18]` | MAP 0x7d @ `$234b=8` | `[0x0380 \| 0x0238]` |
| Interior tower (E) | `[6b,10:6d,12]` | MAP 0x7d @ `$234b=8` | `[0x0460 \| 0x0080]` |
| Interior tower (E) top | `[69,26:6a,27]` | MAP 0x7d @ `$234b=9` | `[0x0280 \| 0x0060]` |
| North gate trigger | `[34,0b:3a,0c]` | _(in-room)_ | opens OBJ 0 gate if `$22dd&0x40 \| $22de&0x02` |

## Enter Script

1. Apply music dispatch (same as 0x7b)
2. Load villager NPCs (0x51–0x56, ~7 total) if `($22dd&0x40) == ($22dc&0x08)`
3. If `$22dd&0x40` (east castle): load east OBJ set (22 guard/wall objects OBJs 4–30)
4. Else: load west OBJ set (OBJs 0x20/0x21 at state 2 = closed gates)
5. If `$234b == 0x41` or `$22e8&0x10` (pig-race gate already passed): set OBJ 0 to state 0x7e (open gate), skip pig-race cutscene
6. If `$234b == 0x89` (pig-race winner entry): run Pig-Race Cutscene (see below)
7. Else: restore normal patrol

## Step-On Scripts

| Tile | Destination / Action | Notes |
|------|---------------------|-------|
| `[26,3b:28,3d]` | MAP 0x7b | South exit |
| `[35,06:39,08]` | MAP 0x5d (east) or MAP 0x6e (west) | Top gate; castle-state dispatch |
| `[2c,34:2e,35]` | MAP 0x7d `$234b=5` west | West door A |
| `[38,34:3a,35]` | MAP 0x7d `$234b=5` east | West door B |
| `[50,34:52,35]` | MAP 0x7d `$234b=6` | East door 1 |
| `[67,34:69,35]` | MAP 0x7d `$234b=7` | East door 2 |
| `[5d,17:5f,18]` | MAP 0x7d `$234b=8` | East door 3 |
| `[6b,10:6d,12]` | MAP 0x7d `$234b=8` | East tower (low) |
| `[69,26:6a,27]` | MAP 0x7d `$234b=9` | East tower top |
| `[34,0b:3a,0c]` | _(in-room gate trigger)_ | If `$22dd&0x40`: set `$22de\|=0x02`, OBJ 0 state 0x7e |

## B-Trigger Scripts

_None._

## Pig-Race Cutscene (`$234b == 0x89`)

Triggered when player arrives with `$234b = 0x89` (pig-race winner flag set by pig-race sub-system):

1. Load VILLAGER_3_6 guard (`NPC 0x56`, `0x00ac>>1`) at gate position
2. Guard NPC dialog: "Halt! Only the pig-race winner may enter!"
3. Check pig-race winner flag; if set: Guard steps aside ("The queen wishes to see you!")
4. Set `$22e8|=0x10` (pig-race gate passed)
5. Play door SFX; set OBJ 0 state 0x7e (gate open)
6. Restore player control

Once `$22e8&0x10` is set, the gate stays open on all future entries.

## NPCs

Loaded when `($22dd&0x40) == ($22dc&0x08)`:

| NPC ID | Enum | Role |
|--------|------|------|
| 0x51 | `VILLAGER_3_2` | Castle grounds pedestrian |
| 0x52 | `VILLAGER_3_3` | Castle grounds pedestrian |
| 0x53 | `VILLAGER_3_4` | Castle grounds pedestrian |
| 0x54 | `VILLAGER_3_5` | Castle grounds pedestrian |
| 0x55 | `VILLAGER_3_5` | Castle grounds pedestrian |
| 0x56 | `VILLAGER_3_6` | Guard (also pig-race cutscene) |

## OBJ Map

| OBJ | Purpose |
|-----|---------|
| 0 | Main gate (state 0x7e = open) |
| 4–30 | East-castle wall/guard objects (only when `$22dd&0x40`) |
| 0x20–0x21 | West-castle gate sections (state 2 = closed) |

## Memory Access

| Address | Bit | Type | Name | Notes |
|---------|-----|------|------|-------|
| `$22dd` | `0x40` | 📖 | East castle (Ebon Keep) active | Controls NPC set, OBJ set, top-gate dest |
| `$22dc` | `0x08` | 📖 | WindWalker unlocked | Part of music/NPC dispatch |
| `$22e8` | `0x10` | 📖 | Pig-race gate passed | Set after cutscene; keeps gate open |
| `$22de` | `0x02` | 📖 | North gate trigger stepped | Set by in-room gate step-on |
| `$234b` | word | ⚙️ | Interior sub-room dispatch / pig-race entry | `0x89` = pig-race winner entry |

## Drop Table

_No drop table configured for this room._

## Notes

- `$234b == 0x89` is a special non-room value used only for the pig-race winner entry sequence
- The top-gate destination (`$22dd&0x40` → 0x5d vs. → 0x6e) is the castle-side fork: east castle leads to Ebon Keep Courtyard, west castle leads into Ivor Tower
- This room shares the `$234b` dispatch register with 0x7b (values 1–4) and 0x7d (internal use); values 5–9 are assigned here for the five upper interior doors
