---
room: 0x68
name: Antiqua – Crustacia Exterior
act: act2
data: 0xa6abe2
---

# 0x68 — Antiqua – Crustacia Exterior

| Field | Value |
|-------|-------|
| Room ID | 0x68 |
| Full Name | Antiqua – Crustacia Exterior |
| Act | 2 (Antiqua) |
| Data block | 0xa6abe2 |
| Enter script | 0x928223 → 0x958443 |
| Step-on table | 0xa6abf1 (13 entries, 0x4e bytes) |
| B-trigger table | 0xa6ac41 (0 entries) |

## Overview

The outdoor area of Crustacia town. Contains multiple staircases (4 sets), an elevator (NPC pair, 2 positions), 5 entrances to the pirate ship (0x30) and exits to West of Crustacia (0x07) and East of Crustacia (0x4f). A Monk NPC inside (pirate ship section tile [29,0c:2a,10]) sells an Amulet of Annihilation for 10,000 Jewels.

The dog cannot climb the steep staircases — the boy must leave the dog at the bottom and ascend alone. This is tracked via `$2350` (dog staircase state 0–4) and `$22f2&0x08` (first "stay here" instruction given).

If `$22ed&0x08` is set on entry, the **Crustacia arrival cutscene** plays: the boy falls into Crustacia's basin (camera scroll, fade-out/in with "Hours later_" caption), arrives at the pirate ship dock, and delivers a monologue about the dog being missing. If `$22e9&0x10` (killed robots with no ammo), a robot NPC also appears.

Dog is set to Greyhound. Music: 0x2c (town), or 0x3a during intro.

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$2260` | R/W | &0x80 | Monk shop proximity flag [0x68] — toggled by proximity to Monk; gates which greeting text fires |
| `$2261` | R/W | &0x01 | Dog unavailable — set when dog left behind on stairs; cleared when boy descends and retrieves dog |
| `$22df` | R/W | &0x02 | Crustacia elevator position — 0=bottom; 1=top; toggled by elevator ride step-ons and forced to top on Crustacia intro entry |
| `$22e9` | R | &0x10 | Killed robots with no ammo left — if set during Crustacia intro, robot NPC appears in cutscene |
| `$22eb` | R/W | &0x20 | IN_ANIMATION routing — teleport to [0x31, 0x5a] if set; cleared otherwise |
| `$22ed` | R/W | &0x08 | Crustacia intro to be shown — cleared in cutscene; if set: forces elevator top, plays intro cutscene, sets `$2261\|=0x01`, disables dog |
| `$22f2` | R/W | &0x04 | Elevator initialized — set during elevator NPC spawn |
| `$22f2` | R/W | &0x08 | Dog staircase "stay" instruction given — set first time boy tells dog to stay; gates short vs. long stair dialog |
| `$2350` | R/W | &0x00–0x04 | Dog staircase state — 0=normal; 1=dog left at left stairs; 2=dog left at right stairs; 3=dog at south-left stairs; 4=dog at south-right stairs |
| `$234c` | write | =0x01–0x05 | Pirate ship entry identifier — set before each entrance to 0x30; determines which section of the ship spawns and camera bounds |
| `$2443` | write | =0x06 | CHANGE DOGGO to Greyhound on room entry |

## Enter Script Summary (`0x958443`)

1. `CHANGE DOGGO = Greyhound (0x06)`.
2. If `$22eb&0x20`: teleport to [0x31, 0x5a] + fade music; else clear flag.
3. Load NPC 0x27 (guard) flags 0x0020 at [0x2b, 0x06] → `$283b`, face west.
4. Load NPC 0x27 flags 0x0002 at [0x4f, 0x11], talk script 0x1866.
5. If `$22ed&0x08` NOT set (intro already done): load NPC 0x1a at [0x2d, 0x2d], talk script 0x1869.
6. Load NPC 0x1a at [0x0f, 0x2d], talk script 0x186f.
7. Load NPC 0x27 flags 0x0002 at [0x0d, 0x11], talk script 0x186c.
8. If `$22ed&0x08` set: `$22df|=0x02` (force elevator top).
9. **Elevator setup**: if `$22df&0x02 == 0` (bottom): load elevator cars at [0x1f,0x54]/[0x1f,0x3f], set `$22f2|=0x04`, OBJ 0 state=0 / OBJ 1 state=1; if `$22df&0x02 == 1` (top): load at [0x1f,0x17]/[0x1f,0x02], OBJ 0 state=1 / OBJ 1 state=0.
10. Music: 0x3a if intro, else 0x2c.
11. **Crustacia intro** (`$22ed&0x08`): clear flag; teleport boy to [0x64, 0x2e]; fade in; show "Hours later_"; fade out/in; boy wanders pirate-ship dock area; if `$22e9&0x10`: robot NPC appears; boy monologue: *"Whoa! Now I know how 'Dandy' Don Carlisle felt in 'Sink, Boat, Sink!'"* and *"No sign of [dog]... I better look around."*; boy = player controlled.
12. If no intro: if `$2350` 1–4 → teleport dog to staircase holding position; else call cinematic setup.

## Step-on Scripts (13 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [22,30:24,32] | `0x94ec40` | **Dog staircase L1** — dog-only: walk dog to [0x0b,0x15]; boy-only (complex): first use shows "Stay here, [dog]" (`$22f2|=0x08`); sets `$2350=0x01`, `$2261|=0x01`; subsequent uses skip dialog |
| [48,31:4a,33] | `0x94ecdb` | **Dog staircase R1** — mirror of L1; sets `$2350=0x02`; dog to [0x53,0x15] |
| [49,4c:4b,4e] | `0x94ed77` | **Monk shop tile** — if boy + `$23b9==8` + proximity conditions: proximity whisper ("Pssst_ over here") / full Amulet of Annihilation shop (10,000 Jewels) based on `$2848`/`$2260&0x80` state |
| [38,4a:3a,4c] | `0x94eda4` | **Dog staircase L2** — same pattern as L1; sets `$2350=0x03`; dog to [0x57,0x53] |
| [38,45:3a,46] (wait, check) | `0x94ee31` | **Dog staircase R2** — same; sets `$2350=0x04`; dog to [0x35,0x4f] |
| [2f,30:30,31] | `0x94efe8` | **Elevator up** — if `$22df&0x02==1` (at top): call sub 0x958000 with `$2835=1` (ride down); clear `$22df&0x02`; swap OBJ 0/1 states |
| [20,50:22,54] | `0x94ec05` | **EXIT west** → 0x07 West of Crustacia at [0x0220, 0x0220]; clears `$2350` if set |
| [28,2b:2b,2c] | `0x94eba6` | **EXIT north** → 0x30 pirate ship section 1 at [0x0078, 0x0148]; `$234c=0x0001` |
| [4b,3b:4e,3c] | `0x94ebb4` | **EXIT north** → 0x30 pirate ship section 2 at [0x0078, 0x02d8]; `$234c=0x0002` |
| [37,37:39,38] | `0x94ebc2` | **EXIT north** → 0x30 pirate ship section 3 at [0x0238, 0x0288]; `$234c=0x0003` |
| [38,45:3a,46] | `0x94ebd0` | **EXIT north** → 0x30 pirate ship section 4 at [0x0378, 0x0288]; `$234c=0x0004`; no fade-out (uses SET AUDIO 0x64 instead) |
| [44,2b:47,2c] | `0x94ebdf` | **EXIT north** → 0x30 pirate ship section 5 at [0x0278, 0x0118]; `$234c=0x0005` |
| [4f,4e:50,56] | `0x94ebed` | **EXIT east** → 0x4f East of Crustacia at [0x0008, 0x0258]; clears `$2350` if set |
| [2f,4f:30,50] | `0x94ef46` | **Elevator down** — if `$22df&0x02==0` (at bottom): call sub 0x958000 with `$2835=0xffff` (ride up); set `$22df|=0x02`; swap OBJ 0/1 states |

## Exits

| Tiles | Destination | Coordinates | Notes |
|-------|-------------|-------------|-------|
| [20,50:22,54] | 0x07 — West of Crustacia | [0x0220, 0x0220] | step-on |
| [28,2b:2b,2c] | 0x30 — Crustacia pirate ship | [0x0078, 0x0148] | step-on; `$234c=1` |
| [4b,3b:4e,3c] | 0x30 — Crustacia pirate ship | [0x0078, 0x02d8] | step-on; `$234c=2` |
| [37,37:39,38] | 0x30 — Crustacia pirate ship | [0x0238, 0x0288] | step-on; `$234c=3` |
| [38,45:3a,46] | 0x30 — Crustacia pirate ship | [0x0378, 0x0288] | step-on; `$234c=4` |
| [44,2b:47,2c] | 0x30 — Crustacia pirate ship | [0x0278, 0x0118] | step-on; `$234c=5` |
| [4f,4e:50,56] | 0x4f — East of Crustacia | [0x0008, 0x0258] | step-on |

## B-Triggers

None.

## NPCs

| NPC | Qty | Spawn | Notes |
|-----|-----|-------|-------|
| NPC 0x27 (guard) | 1 | [0x2b, 0x06] | Stored in `$283b`; face west; talk script unresolved |
| NPC 0x27 | 1 | [0x4f, 0x11] | Talk script 0x1866 |
| NPC 0x27 | 1 | [0x0d, 0x11] | Talk script 0x186c |
| NPC 0x1a | 1 | [0x2d, 0x2d] | Spawns only if Crustacia intro NOT to be shown; talk script 0x1869 |
| NPC 0x1a | 1 | [0x0f, 0x2d] | Talk script 0x186f |
| NPC 0x20 (elevator car) | 2 | [0x1f, 0x17/0x02] or [0x1f, 0x54/0x3f] | Position depends on `$22df&0x02`; stored in `$24d3`, `$24d5` |
| NPC 0xbe>>1 (robot) | 1 | [0x35, 0x4f] | Crustacia intro only if `$22e9&0x10`; animated; destroyed at intro end |

## Notes

- **Dog staircase system**: `$2350` holds which staircase the dog was left at (1–4). `$22f2&0x08` prevents re-showing the "Stay here" dialog on subsequent uses. On descend, $2350 is cleared and dog teleports back to the boy.
- **Elevator (sub 0x958000)**: `$2835=0x0001` = ride down; `$2835=0xffff` = ride up. Call sub not captured — handles the animation. `$22df&0x02` tracks the persistent elevator position between room entries.
- **Monk shop**: `$2848` is the proximity counter/flag for the Monk; `$2260&0x80` gates which greeting text fires. The Amulet of Annihilation costs 10,000 Jewels. Sub 0x95c0c4 handles the purchase; sub 0x95c0b3 handles NPC unload on sale.
- **`$22ed&0x08` = Crustacia intro to be shown**: set externally (likely in 0x4f/0x2e/0x6b context); consumed here; triggers the full "Hours later" arrival cinematic.
- **`$22e9&0x10`**: Only relevant during the intro cutscene — causes a robot (NPC 0xbe>>1) to appear briefly.
- `$234c` values 1–5 tell 0x30 which section of the pirate ship the player entered from, determining camera bounds and NPC loads.
