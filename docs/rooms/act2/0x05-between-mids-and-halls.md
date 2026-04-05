---
room: 0x05
name: Antiqua – Between 'Mids and Halls
act: act2
data: 0xa4d3b4
---

# 0x05 — Antiqua – Between 'Mids and Halls

| Field | Value |
|-------|-------|
| Room ID | 0x05 |
| Full Name | Antiqua – Between 'Mids and Halls |
| Act | 2 (Antiqua) |
| Data block | 0xa4d3b4 |
| Enter script | 0x928034 → 0x96c3fb |
| Step-on table | 0xa4d3c3 (20 entries, 0x78 bytes) |
| B-trigger table | 0xa4d43d (20 entries, 0x78 bytes) |

## Overview

A large outdoor area bridging the Pyramids and the Halls of Knowledge. It connects to Horace's camp (0x2f), Outside of 'mids (0x06), Outside of halls (0x2b), and West of Crustacia (0x07). Multiple pit-fall zones send the player to Horace's camp via a pit-fall animation.

This room holds the Act 2 diamond-theft cutscene: when both Diamond Eyes are in the player's inventory and Aegis is not yet dead (`$22d8&0xC0` set, `$22d9&0x08` clear), a story trigger fires at tile [46,40:47,44] — a villain NPC appears, steals the Diamond Eyes, and two guards spawn to start combat.

It also contains the **Act 2 → Act 3 outro path**: when `$22f1&0x40` (OUTRO) is set on room entry, a cinematic loads three NPCs and destroys them one by one before map-changing to 0x40 (Gothica — Swamp south of Gomi's Tower).

The dog is transformed to Greyhound form on normal entry (`CHANGE DOGGO = 0x06`).

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$22d1` | R/W | &0x10–0x80 | Sniff spot persistence — sniffs #9–#12 (Ethanol×2, Roots×2); enter script unloads objs 9–12 if set |
| `$22d2` | R/W | &0x01–0x80 | Sniff spot persistence — sniffs #13–#20 (Roots×2, Limestone×2, Wax×2, Water, Vinegar); enter script unloads objs 13–20 |
| `$22d3` | R/W | &0x01–0x02 | Sniff spot persistence — sniffs #21–#22 (Vinegar, Bone); enter script unloads objs 21–22 |
| `$22d8` | read | &0x40, &0x80 | Both Diamond Eyes obtained — gate for the Diamond Eyes theft cutscene |
| `$22d9` | read | &0x08 | Aegis dead — if set, Diamond Eyes theft cutscene is suppressed |
| `$22d9` | write | \|=0x20 | Diamond Eyes stolen — set at start of theft cutscene to prevent replay |
| `$22d9` | read | &0x20 | Already stolen check — if set, skip cutscene |
| `$22d9` | read | &0x01 | Horace met flag — selects dialogue variant in theft cutscene |
| `$22eb` | R/W | &0x20 | In-animation entry routing — teleport to [0x29, 0x5f] if set; cleared on normal entry |
| `$22ed` | write | \|=0x80 | Set when player falls into a pit; tells Horace's camp the player arrived via pit-fall |
| `$22f1` | read | &0x40 | OUTRO flag — if set on entry, run Act 2→Act 3 outro cinematic instead of normal entry |
| `$2264` | write | &=0xfd | Diamond Eyes removed from inventory (`&0x02` = Diamond Eyes bit) |
| `$2272` | R/W | &0x01–0x20 | Object/gourd persistence — bits 0x04–0x20 are gourds (Water, Water, Limestone, Wax); bits 0x01–0x02 are set by conditional B-triggers |
| `$2443` | write | =0x06 | CHANGE DOGGO to Greyhound (0x06) on normal room entry |

## Enter Script Summary (`0x96c3fb`)

### Path A — Outro (`$22f1&0x40` set)

1. CALL cinematic setup (0x92de75).
2. Load three NPCs: NPC 0x63 at [0x25,0x57] → `arg0`; NPC 0x75 at [0x23,0x45] → `arg2`; NPC 0x75 at [0x39,0x45] → `arg4`.
3. Walk boy and dog to staging positions.
4. For each of the three NPCs: call explosion/death animation (0x92d5bd), sleep, destroy entity, call cinematic sub (0x92d607).
5. Walk boy and dog east to [0x39, 0x41].
6. Fade screen, set `$238f = 0`, CHANGE MAP → **0x40** (Gothica — Swamp south of Gomi's Tower) at [0x0d8, 0x278].

### Path B — Normal entry

1. **Entry routing**: if `$22eb&0x20`: teleport both to [0x29, 0x5f] + fade music; else clear flag.
2. Configure prize drops (rates 10/2/1, items 0x0801 / 0x0001 qty 40 / 0x0802).
3. Unload sniff-spot objects (objs 9–22) and gourd objects (objs 0,1,5–8) based on persistence flags.
4. **NPC load**: if `$22d9&0x20` (Diamond Eyes stolen): `$2433=10`, load NPC 0x0f at [0x1f, 0x37].
5. Spawn NPC 0x23 enemy spawners at [0x35,0x23] and [0x33,0x4f].
6. Spawn NPC 0x75 spawners at 4 locations.
7. Load NPC 0x5e (Greyhound) at [0x24, 0x1d] → store in `$283b`; set `CHANGE DOGGO = 0x06` (Greyhound).
8. Play music 0x40; fade in.
9. Call cinematic setup (0x92de75).

## Step-on Scripts (20 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [30,26:31,2b] | `0x96bf7c` | **Pit fall** (band 1) — animate player falling into pit; set `$22ed|=0x80`; CHANGE MAP → 0x2f (Horace's camp) at [0x198, 0x140] |
| [31,24:32,25] | `0x96bf7c` | Pit fall (band 2) |
| [31,25:33,26] | `0x96bf7c` | Pit fall (band 3) |
| [31,26:38,27] | `0x96bf7c` | Pit fall (band 4) |
| [31,26:39,27] | `0x96bf7c` | Pit fall (band 5) |
| [33,29:3b,2a] | `0x96bf7c` | Pit fall (band 6) |
| [33,29:34,2b] | `0x96bf7c` | Pit fall (band 7) |
| [33,2a:34,2b] | `0x96bf7c` | Pit fall (band 8) |
| [34,29:3c,2a] | `0x96bf7c` | Pit fall (band 9) |
| [38,25:39,26] | `0x96bf7c` | Pit fall (band 10) |
| [38,25:39,27] | `0x96bf7c` | Pit fall (band 11) |
| [3b,23:3c,29] | `0x96bf7c` | Pit fall (band 12) |
| [3b,23:3c,2a] | `0x96bf7c` | Pit fall (band 13) — total 13 pit-fall tile bands sharing same script |
| [46,40:47,44] | `0x96c113` | **Diamond Eyes theft cutscene** — fires if `$22d8&0xC0` set AND `$22d9&0x08` clear AND `$22d9&0x20` clear; sets `$22d9|=0x20`; plays cutscene, gives Diamond Eyes to villain, spawns 2 guard NPCs for combat; skips silently if already stolen or Aegis dead |
| [4e,41:50,45] | `0x96bf58` | **EXIT west** → 0x07 (West of Crustacia) at [0x008, 0x1e8] |
| [33,1c:3b,1e] | `0x96bf74` | **EXIT north** → 0x2b (Outside of halls) at [0x228, 0x208] |
| [20,31:22,35] | `0x96bf6a` | **EXIT west** → 0x2f (Horace's camp) at [0x408, 0x188] |
| [20,53:22,56] | `0x96bf62` | **EXIT west** → 0x06 (Outside of 'mids) at [0x518, 0x388] |

## Exits

| Tiles | Destination | Coordinates | Notes |
|-------|-------------|-------------|-------|
| [20,31:22,35] | 0x2f — Horace's camp | [0x408, 0x188] | step-on |
| [20,53:22,56] | 0x06 — Outside of 'mids | [0x518, 0x388] | step-on |
| [33,1c:3b,1e] | 0x2b — Outside of halls | [0x228, 0x208] | step-on |
| [4e,41:50,45] | 0x07 — West of Crustacia | [0x008, 0x1e8] | step-on |
| Pit falls (×13) | 0x2f — Horace's camp | [0x198, 0x140] | step-on; pit-fall animation; `$22ed|=0x80` |
| Enter script (outro) | 0x40 — Gothica: Swamp S of Gomi's Tower | [0x0d8, 0x278] | `$22f1&0x40` outro flag |

## B-Triggers (20 entries)

| Tile | Script | Contents | Flag |
|------|--------|----------|------|
| [3e,4c:44,4d] | `0x96c09b` | Special trigger: if boy controlled AND `$235f≥12` AND `$2360==2`: load 2× NPC 0x20, set OBJ 0 state 1; `$2272\|=0x01` | `$2272&0x01` |
| [3d,3a:44,3b] | `0x96c0d7` | Special trigger (same conditions): load 2× NPC 0x20, set OBJ 1 state 1; `$2272\|=0x02` | `$2272&0x02` |
| [40,47:42,49] | `0x96c2c8` | 🫙 Gourd MAP REF 0x06 (Water, ADD 2) | `$2272&0x04` |
| [43,31:45,33] | `0x96c2e6` | 🫙 Gourd MAP REF 0x05 (Water, ADD 1) | `$2272&0x08` |
| [45,33:47,35] | `0x96c304` | 🫙 Gourd MAP REF 0x07 (Limestone, ADD 2) | `$2272&0x10` |
| [48,36:4a,38] | `0x96c322` | 🫙 Gourd MAP REF 0x08 (Wax, ADD 3) | `$2272&0x20` |
| [49,56:4a,57] | `0x96bdb8` | 👃 Sniff #9: Ethanol (ADD 3, MAP REF 9) | `$22d1&0x10` |
| [28,3a:29,3b] | `0x96bdd6` | 👃 Sniff #10: Ethanol (ADD 2, MAP REF 10) | `$22d1&0x20` |
| [47,40:48,41] | `0x96bdf4` | 👃 Sniff #11: Roots (ADD 1, MAP REF 11) | `$22d1&0x40` |
| [24,32:25,33] | `0x96be12` | 👃 Sniff #12: Roots (ADD 3, MAP REF 12) | `$22d1&0x80` |
| [34,21:35,22] | `0x96be30` | 👃 Sniff #13: Roots (MAP REF 13) | `$22d2&0x01` |
| [27,52:28,53] | `0x96be4a` | 👃 Sniff #14: Roots (ADD 2, MAP REF 14) | `$22d2&0x02` |
| [2e,2c:2f,2d] | `0x96be68` | 👃 Sniff #15: Limestone (ADD 2, MAP REF 15) | `$22d2&0x04` |
| [27,45:28,46] | `0x96be86` | 👃 Sniff #16: Limestone (ADD 1, MAP REF 16) | `$22d2&0x08` |
| [40,43:41,44] | `0x96bea4` | 👃 Sniff #17: Wax (ADD 2, MAP REF 17) | `$22d2&0x10` |
| [3c,38:3d,39] | `0x96bec2` | 👃 Sniff #18: Wax (ADD 2, MAP REF 18) | `$22d2&0x20` |
| [44,58:46,59] | `0x96bee0` | 👃 Sniff #19: Water (ADD 1, MAP REF 19) | `$22d2&0x40` |
| [44,47:45,48] | `0x96befe` | 👃 Sniff #20: Vinegar (ADD 1, MAP REF 20) | `$22d2&0x80` |
| [46,2f:47,30] | `0x96bf1c` | 👃 Sniff #21: Vinegar (ADD 1, MAP REF 21) | `$22d3&0x01` |
| [4b,38:4c,39] | `0x96bf3a` | 👃 Sniff #22: Bone (ADD 1, MAP REF 22) | `$22d3&0x02` |

## NPCs

| NPC | Qty | Position | Notes |
|-----|-----|----------|-------|
| NPC 0x5e | 1 | [0x24, 0x1d] | Greyhound dog form, loaded on normal entry; stored in `$283b`; triggers `CHANGE DOGGO = 0x06` |
| NPC 0x0f | 1 | [0x1f, 0x37] | Loaded only if `$22d9&0x20` (Diamond Eyes stolen); likely Madronius's representative or guard captain |
| NPC 0x23 | 2 | [0x35,0x23] / [0x33,0x4f] | Enemy spawners (spawned with `$2433=5`) |
| NPC 0x75 | 4 | [0x25,0x29] / [0x4b,0x2d] / [0x11,0x4b] / [0x49,0x73] | Enemy spawners (spawned with `$2433=1`) |
| NPC 0x20 | 2 | [0x3f,0x5f] / [0x45,0x5f] or [0x3d,0x3b] / [0x43,0x3b] | Conditionally spawned by B-triggers (id:3f / id:42) when `$235f≥12` AND `$2360==2` |
| NPC 0x62 (0xc4>>1) | 1 | Enters from east at [0x62, 0x4e] | Cutscene villain (likely **Madronius**) — steals Diamond Eyes at `[46,40:47,44]` trigger |
| NPC 0x27 | 2 | [0x61,0x4c] / [0x62,0x4e] | Guards spawned after Diamond Eyes theft; transition to combat |

## Notes

- **Diamond Eyes theft cutscene** (step-on [46,40:47,44], id:30): the full condition is `($22d8&0x40) AND ($22d8&0x80) AND NOT($22d9&0x08) AND NOT($22d9&0x20)`. The first two bits are likely "has Diamond Eye #1" and "has Diamond Eye #2." The cutscene fires only once (protected by `$22d9&0x20`) and only if Aegis is still alive.
- The villain's name is not shown in the script; dialog: "I must have them! Give them to me!" / "They're mine! Guaaaahaha!" matches known Act 2 antagonist **Madronius**. // TODO: confirm NPC 0x62 = Madronius
- **Act 2 → Act 3 outro** (`$22f1&0x40`): the outro path destroys NPCs with explosion-style animations before loading Gothica. The three NPCs loaded are NPC 0x63 and 2× NPC 0x75 — identities unresolved. `$238f` is cleared to 0 before the map change (likely disabling story scripts in the destination).
- **Sniff numbering**: Sniffs #9–#22 continue from sniffs #1–#8 presumably in other rooms that use `$22d1&0x01..0x08` (first 4 bits in the same byte are used by Fountain Plaza [0x4c]).
- **Special B-triggers at [3e,4c] and [3d,3a]**: Conditions `$235f≥12` (alchemy level) and `$2360==2` (game state) are unresolved. These may spawn combat-area enemies under specific conditions. // TODO: identify $235f and $2360 semantics.
- `$22d2&0x01..0x04` entries listed here use the upper half of `$22d2` — the first few bits of `$22d2` may be shared with another room (see memory-map for the full picture).
