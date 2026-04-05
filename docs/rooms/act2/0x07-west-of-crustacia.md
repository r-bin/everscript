---
room: 0x07
name: Antiqua – West of Crustacia
act: act2
data: 0xa793e9
---

# 0x07 — Antiqua – West of Crustacia

| Field | Value |
|-------|-------|
| Room ID | 0x07 |
| Full Name | Antiqua – West of Crustacia |
| Act | 2 (Antiqua) |
| Data block | 0xa793e9 |
| Enter script | 0x92803e → 0x96bcd8 |
| Step-on table | 0xa793f8 (10 entries, 0x3c bytes) |
| B-trigger table | 0xa79436 (13 entries, 0x4e bytes) |

## Overview

An outdoor transitional area west of Crustacia, connecting to Between 'Mids and Halls (0x05 — east), Crustacia exterior (0x68 — east/town), and the Alchemy Cave complex (0x35 — north). The dog is switched to Greyhound form on entry.

The room features a patrol NPC (NPC 0x20) whose position is toggled between two map zones by step-on triggers tied to `$22df&0x04`. Two step-ons are dog-only broken bridge jumps (the dog can jump the gap; the boy cannot). 12 sniff spots (`$22c0` / `$22c1`) and one conditional combat B-trigger (`$22d8&0x20`) are present.

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$22c0` | R/W | &0x10–0x80 | Sniff persistence — sniffs #1–#4 (Ethanol×2, Vinegar, Limestone); enter script unloads objs 1–4 if set |
| `$22c1` | R/W | &0x01–0x80 | Sniff persistence — sniffs #5–#12 (Limestone, Brimstone×2, Wax, Ash, Roots×2, Water×2); enter script unloads objs 5–12 if set |
| `$22d8` | R/W | &0x20 | OBJ 0 triggered flag [0x07] — set by conditional B-trigger when alchemy conditions met (`$235f≥12` AND `$2360==2`); enter script unloads OBJ 0 if set |
| `$22df` | R/W | &0x04 | NPC position flag — 0=NPC at left position [0x11,0x0f]; 1=NPC at right position [0x31,0x0f]; toggled by step-ons and on room entry |
| `$22eb` | R/W | &0x20 | In-animation entry routing — teleport to [0x3a, 0x41] if set; cleared on normal entry |
| `$2443` | write | =0x06 | CHANGE DOGGO to Greyhound on room entry |

## Enter Script Summary (`0x96bcd8`)

1. **Entry routing**: if `$22eb&0x20`: teleport both to [0x3a, 0x41] + fade music; else clear flag.
2. Configure prize drops (rates 10/3/2, items 0x0801 / 0x0001 qty 40 / 0x0806).
3. **NPC position setup**: if `$22df&0x04 == 0` (last seen at left), load NPC 0x20 at [0x11, 0x0f] → `$24d7`; then clear `$22df&0x04`; else load NPC 0x20 at [0x31, 0x0f] → `$24d7`; set `$22df |= 0x04`.
4. Unload persistence objects based on flags (`$22d8&0x20` = obj 0; `$22c0&0x10..0x80` = objs 1–4; `$22c1&0x01..0x80` = objs 5–12).
5. Play music 0x3a; fade in.
6. Spawn combat NPCs: 2× NPC 0x27 at [0x11,0x2d] / [0x2d,0x17]; 3× NPC 0x23 at [0x07,0x21] / [0x19,0x49] / [0x32,0x1b].
7. Set `CHANGE DOGGO = 0x06` (Greyhound).
8. If dog unavailable: hide dog, disable, return early; else call cinematic setup (0x92de75).

## Step-on Scripts (10 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [0a,09:0b,0a] | `0x96b9f9` | **NPC left trigger** — if `$22df&0x04==0` (NPC at left): walk NPC to [0x11,0x0f], set `$22df|=0x04`, walk controlled char south; solo/duo handling; sets `$2834&0x02` toggle |
| [1a,09:1b,0a] | `0x96b970` | **NPC right trigger** — if `$22df&0x04!=0` (NPC at right): walk NPC to [0x31,0x0f], clear `$22df&0x04`; similar to left trigger; sets `$2834&0x02/0x04` toggles |
| [02,1e:04,22] | `0x96b918` | **EXIT east** → 0x05 (Between 'mids and halls) at [0x2f8, 0x268] |
| [16,1f:17,21] | `0x96bb10` | **Dog bridge jump west** — dog-only; animate dog walking west over broken bridge at [0x29,0x3c]; toggles `$2834&0x02` |
| [12,1f:13,21] | `0x96bb42` | **Dog bridge jump east** (tile 1 of 2) — dog-only; animate dog walking east over broken bridge at [0x20,0x3c] |
| [12,1f:13,21] | `0x96bb42` | **Dog bridge jump east** (tile 2 of 2) |
| [22,08:24,09] | `0x96b922` | **EXIT north** → 0x35 (Act1 caves + Act2 West Alchemy Cave) at [0x610, 0x138]; sets `$234e=5, $234d=6` (cave entry identifiers) |
| [24,23:26,25] | `0x96b90e` | **EXIT east** → 0x68 (Crustacia exterior) at [0x028, 0x2c8] |
| [0a,09:0b,0a] | `0x96b9f9` | NPC left trigger (duplicate entry) |
| [1a,09:1b,0a] | `0x96b970` | NPC right trigger (duplicate entry) |

## Exits

| Tiles | Destination | Coordinates | Notes |
|-------|-------------|-------------|-------|
| [02,1e:04,22] | 0x05 — Between 'mids and halls | [0x2f8, 0x268] | step-on |
| [22,08:24,09] | 0x35 — Caves complex | [0x610, 0x138] | step-on; `$234e=5, $234d=6` |
| [24,23:26,25] | 0x68 — Crustacia exterior | [0x028, 0x2c8] | step-on |

## B-Triggers (13 entries)

| Tile | Script | Contents | Flag |
|------|--------|----------|------|
| [02,12:03,13] | `0x96bb74` | 👃 Sniff #1: Ethanol (ADD 1, MAP REF 1) | `$22c0&0x10` |
| [1b,1a:1c,1b] | `0x96bb92` | 👃 Sniff #2: Ethanol (ADD 2, MAP REF 2) | `$22c0&0x20` |
| [17,21:18,22] | `0x96bbb0` | 👃 Sniff #3: Vinegar (ADD 1, MAP REF 3) | `$22c0&0x40` |
| [1b,10:1c,11] | `0x96bbce` | 👃 Sniff #4: Limestone (ADD 2, MAP REF 4) | `$22c0&0x80` |
| [19,04:1a,05] | `0x96bbec` | 👃 Sniff #5: Limestone (ADD 1, MAP REF 5) | `$22c1&0x01` |
| [24,0d:25,0e] | `0x96bc0a` | 👃 Sniff #6: Brimstone (MAP REF 6) | `$22c1&0x02` |
| [11,27:12,28] | `0x96bc24` | 👃 Sniff #7: Brimstone (ADD 2, MAP REF 7) | `$22c1&0x04` |
| [06,06:07,07] | `0x96bc42` | 👃 Sniff #8: Wax (ADD 1, MAP REF 8) | `$22c1&0x08` |
| [07,23:08,24] | `0x96bc60` | 👃 Sniff #9: Ash (ADD 2, MAP REF 9) | `$22c1&0x10` |
| [07,19:08,1a] | `0x96bc7e` | 👃 Sniff #10: Roots (ADD 2, MAP REF 10) | `$22c1&0x20` |
| [13,12:14,13] | `0x96bc9c` | 👃 Sniff #11: Water (ADD 1, MAP REF 11) | `$22c1&0x40` |
| [10,21:11,22] | `0x96bcba` | 👃 Sniff #12: Water (ADD 1, MAP REF 12) | `$22c1&0x80` |
| [20,09:24,0a] | `0x96b934` | Special trigger (OBJ 0): if boy AND `$235f≥12` AND `$2360==2`: load 2× NPC 0x20 at [0x3e,0x0d]/[0x42,0x0d], set OBJ 0 state, `$22d8\|=0x20` | `$22d8&0x20` |

## NPCs

| NPC | Qty | Spawn | Notes |
|-----|-----|-------|-------|
| NPC 0x20 | 1 | [0x11,0x0f] or [0x31,0x0f] | Patrol NPC; position based on `$22df&0x04`; moves between positions via step-on triggers at [0a,09] and [1a,09]; stored in `$24d7` |
| NPC 0x27 | 2 | [0x11,0x2d] / [0x2d,0x17] | Combat enemies |
| NPC 0x23 | 3 | [0x07,0x21] / [0x19,0x49] / [0x32,0x1b] | Combat enemies |

## Notes

- **Dog broken bridge jumps** at [12,1f:13,21] and [16,1f:17,21]: only activates for dog; the dog jumps over a broken bridge at x≈[0x20–0x29], y≈0x3c — the boy cannot cross.
- **Lift / ferry** (`$22df&0x04`): the NPC (0x20) operates a lift or ferry that takes the player across the river. The sub `0x96ba82` is called with `$2835=0x0001` (cross east) or `0xffff` (cross west) — exact ferry mechanics not fully resolved. // TODO: identify sub 0x96ba82 purpose and confirm ferry behavior.
- **Special B-trigger** at [20,09:24,0a]: Shares the same `$235f≥12` AND `$2360==2` condition as the analogous triggers in [0x05]. This is the second occurrence of this pattern — likely related to a minigame, alchemy skill gate, or persistent story event. Sets `$22d8&0x20` (distinct from the Diamond Eyes bits 0x40/0x80). // TODO: identify `$235f` and `$2360` semantics.
- Music track 0x3a is loaded; this is distinct from the market track (0x40).
- `$22df&0x04` is also tested in the enter script to determine which side the NPC spawns, creating a persistent position between room re-entries.
