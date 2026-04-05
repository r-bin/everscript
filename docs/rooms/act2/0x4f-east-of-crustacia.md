---
room: 0x4f
name: Antiqua – East of Crustacia
act: act2
data: 0xa99f92
---

# 0x4f — Antiqua – East of Crustacia

| Field | Value |
|-------|-------|
| Room ID | 0x4f |
| Full Name | Antiqua – East of Crustacia |
| Act | 2 (Antiqua) |
| Data block | 0xa99f92 |
| Enter script | 0x9281a6 → 0x95babf |
| Step-on table | 0xa99fa1 (25 entries, 0x96 bytes) |
| B-trigger table | 0xa9a039 (16 entries, 0x60 bytes) |

## Overview

A large outdoor area east of Crustacia town, with a tiered upper plateau (reached via in-room teleport warp passages) and lower ground. Connects west to Crustacia exterior (0x68), south to Crustacia fire pit (0x04), north to Desert of Doom (0x1b), and via a north passage to Blimp's Cave (0x2e).

The room has three distinct entry modes:

1. **Normal entry**: 5 enemy NPCs spawned; player controls returned.
2. **Rock landing cutscene** (`$22df&0x10` set, `$22df&0x20` clear): NPC 0x1e falls from the sky (rock), camera scroll, screen shake, music 0x52; sets `$22df&0x20`. Boy remarks "Wow! It sure took a long time for that rock to fall!"
3. **Crush formula cutscene** (`$22f3&0x01` set): NPC 0x2e (Crush) appears at [0x21, 0x17], delivers tutorial speech about the dog being in the north desert, awards the **Crush formula** (alchemy selection screen), and opens **ingredient shop 0x000b**. Clears `$22f3&0x01`.

The dog is switched to Greyhound on entry. 19 pit-fall step-ons cover the upper plateau area and fall the player to Blimp's Cave (0x2e). 14 sniff spots and 2 gourds cover the lower and mid areas.

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$225f` | R | &0x01 | OBJ 0 persistence [0x4f] — enter script unloads OBJ 0 if set; flag set elsewhere // TODO: identify which room/trigger sets `$225f&0x01` |
| `$226b` | R/W | &0x01 | Gourd #15 (Call Beads) looted [0x4f] — enter script unloads OBJ 15 if set |
| `$226b` | R/W | &0x02 | Gourd #16 (200 Gold Coins) looted [0x4f] — enter script unloads OBJ 16 if set |
| `$22b4` | R/W | &0x20–0x80 | Sniff persistence — sniffs #1–#3 Ethanol [0x4f]; enter unloads objs 1–3 |
| `$22b5` | R/W | &0x01–0x80 | Sniff persistence — sniffs #4–#11 [0x4f] (Ethanol, Roots, Limestone×2, Wax×3, Vinegar); enter unloads objs 4–11 |
| `$22b6` | R/W | &0x01–0x04 | Sniff persistence — sniffs #12–#14 [0x4f] (Bone, Brimstone×2); enter unloads objs 12–14 |
| `$22df` | R/W | &0x10 | Rock scene pending [0x4f] — if set and 0x20 clear: triggers rock landing cutscene on entry |
| `$22df` | R/W | &0x20 | Rock landed [0x4f] — set during rock cutscene (`$22df\|=0x20`); gates OBJ 17 state; prevents re-triggering cutscene |
| `$22eb` | R/W | &0x20 | In-animation entry routing — teleport both to [0x1b, 0x4b] if set; cleared otherwise |
| `$22ee` | write | &0x40 | Set at start of Crush dialog sequence; cleared at end |
| `$22f3` | R/W | &0x01 | Crush dialog to be shown [0x4f] — if set: triggers Crush formula cutscene; cleared after completion |
| `$2443` | write | =0x06 | CHANGE DOGGO to Greyhound on room entry |

## Enter Script Summary (`0x95babf`)

1. `CHANGE DOGGO = Greyhound (0x06)`.
2. If `$22eb&0x20`: teleport to [0x1b, 0x4b] + fade music; else clear flag.
3. Unload persistence objects: `$225f&0x01`=OBJ 0; `$226b&0x01`=OBJ 15; `$226b&0x02`=OBJ 16; `$22b4&0x20..0x80`=objs 1–3; `$22b5&0x01..0x80`=objs 4–11; `$22b6&0x01..0x04`=objs 12–14.
4. Configure `$0ea2+0=0x40` (unknown).
5. Configure prize drops: rates 10/3/1, items 0x0801 / 0x0001 qty 75 / 0x0804.
6. Play music 0x3a if not already playing; `$23bf = 0`.
7. If `($22df&0x10) && ($22df&0x20)`: set OBJ 17 state = 1 (rock NPC already resolved).
8. If dog unavailable: `DOGGO CLOSE = 1`.

### Branch A — Crush dialog (`$22f3&0x01` set)
9. Set `$23bf=1`, `$22ee|=0x40`; clear `$22f3&0x01`.
10. Teleport both to [0x27, 0x17]; load NPC 0x2e (Crush) flags 0x0020 at [0x21, 0x17] → `$2455`.
11. Fade in from black (brightness 0→15 over 3 ticks/step).
12. **Crush dialog** (0x95ba3f): boy and Crush face each other; Crush delivers speech → "You can cross over to the desert on my new bridge!" → awards **Crush formula** (0x0a, alchemy selection screen) → opens **ingredient shop 0x000b** → Crush exits.
13. After dialog: call "East of Crustacia Enter Part 2" (spawn 5 enemies).

### Branch B — Rock landing cutscene (`$22df&0x10` set, `$22df&0x20` clear)
9. `$22df |= 0x20`; teleport both to [0x1c, 0x28] facing south.
10. Load NPC 0x1e at [0x32, 0x1a] (rock) → `$2839`. Camera scroll to [0x0190, 0x0170].
11. Fade out music; play music 0x52; SFX 0xa4 (impact); screen shake.
12. Rock (NPC 0x1e) animate falling (y: 0x00d0 → 0x0170, +3/tick); load NPC 0x20 at [0x32, 0x2e]; destroy NPC 0x1e; stop shake; restore music 0x3a.
13. Boy: "Wow! It sure took a long time for that rock to fall!"
14. After cutscene: call "East of Crustacia Enter Part 2" (spawn 5 enemies).

### Branch C — Normal entry
9. Call "East of Crustacia Enter Part 2": load NPC 0x27 at [0x17,0x35], NPC 0x28 at [0x1d,0x33], NPC 0x27 at [0x23,0x4d], NPC 0x28 at [0x11,0x49], NPC 0x27 at [0x17,0x2d].
10. Call cinematic setup (0x92de75).

## Step-on Scripts (25 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [26,19:27,1a] | `0x95b729` | **Pit-fall** → 0x2e Blimp's Cave at [0x00b8, 0x0098]; sets `$22ed\|=0x80` |
| [23,19:24,1a] | `0x95b729` | Pit-fall (same) |
| [24,19:25,1a] | `0x95b729` | Pit-fall |
| [21,19:22,1a] | `0x95b729` | Pit-fall |
| [1c,19:1d,1a] | `0x95b729` | Pit-fall |
| [22,16:23,19] | `0x95b729` | Pit-fall |
| [1f,16:20,18] | `0x95b729` | Pit-fall |
| [1c,18:22,19] | `0x95b729` | Pit-fall |
| [22,19:23,1a] | `0x95b729` | Pit-fall |
| [23,18:25,19] | `0x95b729` | Pit-fall |
| [26,18:27,19] | `0x95b729` | Pit-fall |
| [25,19:26,1a] | `0x95b729` | Pit-fall |
| [27,18:2b,19] | `0x95b729` | Pit-fall |
| [28,14:2b,15] | `0x95b729` | Pit-fall |
| [25,15:29,16] | `0x95b729` | Pit-fall |
| [23,14:25,15] | `0x95b729` | Pit-fall |
| [1f,15:24,16] | `0x95b729` | Pit-fall |
| [1d,13:1e,14] | `0x95b729` | Pit-fall |
| [1a,14:1f,15] | `0x95b729` | Pit-fall (total: 19 pit-fall tiles) |
| [2e,32:30,38] | `0x95b6c3` | **EXIT south** → 0x04 Crustacia fire pit at [0x0018, 0x00f8] |
| [18,1d:1b,1e] | `0x95b5ce` | **EXIT north** → 0x2e Blimp's Cave at [0x0098, 0x00d8] (bridge/passage entrance) |
| [0f,32:10,39] | `0x95b6b5` | **EXIT west** → 0x68 Crustacia exterior at [0x02f8, 0x02d8] |
| [1b,34:1e,35] | `0x95b5dc` | **In-room warp** (south → north): walk to [0x1b, 0x45], teleport to [0x2a, 0x0d], emerge walking south. Traverses underground passage to upper-north section. |
| [14,26:17,27] | `0x95b649` | **In-room warp** (mid-west → far-east): walk to [0x0d, 0x2a], teleport to [0x46, 0x1b], emerge walking south. Traverses underground passage to far-east section. |
| [19,10:2d,11] | `0x95b6d1` | **EXIT north** → 0x1b Desert of Doom at [0x0248, 0x0638]; clears `$22f3&0x08`; sets `$22fd=4, $22fc=0` |

## Exits

| Tiles | Destination | Coordinates | Notes |
|-------|-------------|-------------|-------|
| [1a,14:2b,1a] (×19) | 0x2e — Blimp's Cave | [0x00b8, 0x0098] | pit-fall; sets `$22ed\|=0x80` |
| [2e,32:30,38] | 0x04 — Crustacia fire pit | [0x0018, 0x00f8] | step-on |
| [18,1d:1b,1e] | 0x2e — Blimp's Cave | [0x0098, 0x00d8] | step-on (north bridge passage) |
| [0f,32:10,39] | 0x68 — Crustacia exterior | [0x02f8, 0x02d8] | step-on |
| [19,10:2d,11] | 0x1b — Desert of Doom | [0x0248, 0x0638] | step-on; clears `$22f3&0x08`; `$22fd=4, $22fc=0` |

## B-Triggers (16 entries)

| Tile | Script | Contents | Flag |
|------|--------|----------|------|
| [2b,22:2c,23] | `0x95b432` | 👃 Sniff #1: Ethanol (ADD 3, MAP REF 1) | `$22b4&0x20` |
| [17,22:18,23] | `0x95b450` | 👃 Sniff #2: Ethanol (ADD 1, MAP REF 2) | `$22b4&0x40` |
| [11,29:12,2a] | `0x95b46e` | 👃 Sniff #3: Ethanol (ADD 2, MAP REF 3) | `$22b4&0x80` |
| [21,32:22,33] | `0x95b48c` | 👃 Sniff #4: Ethanol (MAP REF 4) | `$22b5&0x01` |
| [29,1d:2a,1e] | `0x95b4a6` | 👃 Sniff #5: Roots (ADD 1, MAP REF 5) | `$22b5&0x02` |
| [2b,1f:2c,20] | `0x95b4c4` | 👃 Sniff #6: Limestone (ADD 1, MAP REF 6) | `$22b5&0x04` |
| [27,2b:28,2c] | `0x95b4e2` | 👃 Sniff #7: Limestone (ADD 2, MAP REF 7) | `$22b5&0x08` |
| [1c,26:1d,27] | `0x95b500` | 👃 Sniff #8: Wax (ADD 1, MAP REF 8) | `$22b5&0x10` |
| [15,32:16,33] | `0x95b51e` | 👃 Sniff #9: Wax (MAP REF 9) | `$22b5&0x20` |
| [17,39:18,3a] | `0x95b538` | 👃 Sniff #10: Wax (ADD 2, MAP REF 10) | `$22b5&0x40` |
| [17,2c:18,2d] | `0x95b556` | 👃 Sniff #11: Vinegar (ADD 2, MAP REF 11) | `$22b5&0x80` |
| [2a,30:2b,31] | `0x95b574` | 👃 Sniff #12: Bone (ADD 3, MAP REF 12) | `$22b6&0x01` |
| [1e,2d:1f,2e] | `0x95b592` | 👃 Sniff #13: Brimstone (ADD 1, MAP REF 13) | `$22b6&0x02` |
| [2a,29:2b,2a] | `0x95b5b0` | 👃 Sniff #14: Brimstone (ADD 2, MAP REF 14) | `$22b6&0x04` |
| [2a,24:2c,26] | `0x95b3fb` | 🫙 Gourd MAP REF 0x0f looted (Call Beads) | `$226b&0x01` |
| [2c,27:2e,29] | `0x95b415` | 🫙 Gourd MAP REF 0x10 looted (200 Gold Coins, AMOUNT=0xC8) | `$226b&0x02` |

## NPCs

| NPC | Qty | Spawn | Notes |
|-----|-----|-------|-------|
| NPC 0x2e (Crush) | 1 | [0x21, 0x17] | Cutscene only (`$22f3&0x01`); awards Crush formula + ingredient shop 0x000b; exits after dialog |
| NPC 0x1e (Rock) | 1 | [0x32, 0x1a] | Rock-landing cutscene only (`$22df&0x10`); animated falling; destroyed after impact |
| NPC 0x20 | 1 | [0x32, 0x2e] | Spawned at end of rock cutscene; identity unresolved |
| NPC 0x27 | 3 | [0x17,0x35] / [0x23,0x4d] / [0x17,0x2d] | Combat enemies (normal + post-cutscene entry) |
| NPC 0x28 | 2 | [0x1d,0x33] / [0x11,0x49] | Combat enemies (normal + post-cutscene entry) |

## Notes

- **Crush formula cutscene**: Triggered by `$22f3&0x01`. This is set by another room/event — the flag gate ensures the tutorial is shown on first relevant entry. // TODO: identify where `$22f3&0x01` is set.
- **Rock landing**: `$22df&0x10` (pending) + `$22df&0x20` (done) pair. The rock is NPC 0x1e. // TODO: identify where `$22df&0x10` is set.
- **Pit-fall plateau**: 19 step-on tiles in roughly [0x1a–0x2b, 0x13–0x1a] area all fall to 0x2e Blimp's Cave. Players who reach the upper plateau via the northern in-room warp can be sent to Blimp's Cave.
- **In-room warps**: Two underground passage transitions (south→north, mid→east) within the same map. No CHANGE MAP — purely position teleports within 0x4f.
- **Desert exit** sets `$22fd=4, $22fc=0`: positions the player at the south side of the desert (row 0, column 4) when entering 0x1b from the south.
- **`$226b`**: Gourd persistence byte shared with [0x4f]; `$226b&0x01..0x02` = East of Crustacia gourds; other bits may be used by adjacent rooms. // TODO: full `$226b` mapping.
- Prize 2 quantity = 0x4b = 75 (Gold Coins).
