# 0x7d — Ebon Keep + Ivor Tower Interior (Multi-Area)

**Act:** 3 — Gothica  
**Script address:** `0x9fff97` (0x7d block)  
**Music:** `MUSIC.EBON_KEEP` (0x62) or `MUSIC.DRAGON_ROAR` (0x6a) — same formula as 0x7b/0x7c  
**Dog sprite:** Poodle (0x08)

## Overview

A single physical interior room that represents nine distinct logical sub-areas, dispatched by `$234b` (values 1–9, set by the entering exterior room). Sub-areas 1–4 are reached from 0x7b (bottom exterior); sub-areas 5–9 from 0x7c (top exterior). Sub-area 5 contains Cecil (a story NPC) and is the "professor's lab" re-entry point. Sub-area 7 contains the Lance cutscene that teaches the Lance alchemy formula. Sub-area 8 contains the Regrowth Lady NPC.

All gourds have **dual contents**: when `$22dd&0x40` is set (east castle / Ebon Keep), one set of items; when clear (west castle / Ivor Tower), a different set. Persistence is tracked by two separate flag groups (`$227a`–`$227b` for east, `$2276`–`$2278` for west).

## Music Dispatch

Identical to 0x7b/0x7c.

## Sub-Area Map

| `$234b` | Sub-area | Entry from | Notes |
|---------|----------|------------|-------|
| 1 | Room 1 — Lower west hall | 0x7b door 1 | NPCs 0x55/0x53 |
| 2 | Room 2 — Lower west stair | 0x7b door 2 | NPCs 0x55/0x56 |
| 3 | Room 3 — Lower west side | 0x7b door 3 | NPCs 0x55/0x56 |
| 4 | Room 4 — Lower east hall | 0x7b Ebon Keep door | NPCs 0x53/0x52/0x55 |
| 5 | Room 5 — Upper lobby | 0x7c west doors | Cecil NPC; prof lab re-entry |
| 6 | Room 6 — Upper west | 0x7c east door 1 | NPC conditional |
| 7 | Room 7 — Upper east | 0x7c east door 2 | Lance cutscene |
| 8 | Room 8 — Upper tier | 0x7c east door 3 / tower | Regrowth Lady |
| 9 | Room 9 — Tower top | 0x7c tower top | OBJ-only |

## Connections (Step-Ons)

| Tile | Destination | Notes |
|------|------------|-------|
| _(south exits, 12 total)_ | MAP 0x7c or MAP 0x7b | Exit back to matching exterior half |
| _(internal)_ | Self MAP 0x7d | Stairwell transitions between sub-areas |

## Enter Script Dispatch (`$234b`)

### $234b = 1 (Room 1)
- Load NPCs: 0x55 (`VILLAGER_3_5`) × 1, 0x53 (`VILLAGER_3_4`) × 1
- Unload OBJs per `$2278&0x20` (east) and `$2278&0x40` (east) / `$2275&0x20`–`$2275&0x40` (west) gourd flags

### $234b = 2 (Room 2)
- Load NPCs: 0x55 × 1, 0x56 (`VILLAGER_3_6`) × 1
- Gourd flags: `$2278&0x80` / `$2279&0x01`

### $234b = 3 (Room 3)
- Load NPCs: 0x55 × 1, 0x56 × 1
- Gourd flags: `$2279&0x02` / `$2279&0x04`

### $234b = 4 (Room 4)
- Load NPCs: 0x53 × 1, 0x52 (`VILLAGER_3_3`) × 1, 0x55 × 1
- Gourd flags: `$2279&0x08` / `$2279&0x10`

### $234b = 5 (Room 5 — Upper Lobby)

**East castle (`$22dd&0x40`):**
- Load Cecil NPC (`0x55` at `[c7,19]`) with talk `0x1a3e`; if `$22de&0x80` (Talked to Cecil): already-flagged talk path
- Load shop NPC (`0x55` at `[cc,19]`) with talk `0x1a43`
- If `$22ee&0x01` (from prof lab): teleport boy to `[69,11]`, face west; clear flag
- If `$227b&0x20` (OBJ 31 collected): unload OBJ 31

**West castle (NOT `$22dd&0x40`):**
- Load guard NPC (`VILLAGER_3_6 0x56`, `0x00ac>>1`) at door
- Load shop NPC (`0x55`, `0x00aa>>1`) at counter with talk `0x1a3f`
- If `$2276&0x20`: unload OBJ 0 (chest already looted)

### $234b = 6 (Room 6)
- If `$22ec&0x10` (east hall active): load NPC10/11 pair
- Else: load single NPC in west region
- Gourd flags: `$227a&0x01`/`$227a&0x40`/`$2279&0x40`/`$2279&0x80` (east) vs. `$2277&0x01`/`$2277&0x40`/`$2276&0x40`/`$2276&0x80` (west)

### $234b = 7 (Room 7 — Upper East / Lance Cutscene)
- If `$22ec&0x10` (east hall): load Lance NPC (`0x55` at `[c7,19]`) **if `$225a&0x08` NOT set** (Lance alchemy not yet learned); else load post-cutscene NPC
- Else (west): load NPC13/14 pair

### $234b = 8 (Room 8)
- If `$22ec&0x10` (east hall): load NPC15 (`0x51`, `VILLAGER_3_2`)
- Manage OBJs 26–30 per `$227b` bits
- Load Regrowth Lady (`0x53` at `[87,17]` via talk `0x1a46`)

### $234b = 9 (Room 9)
- OBJ management only: unload per `$227b&0x04`/`0x08`/`0x10`

## B-Trigger Scripts (All Gourds)

All gourds have dual contents. Flag group `A` = east castle (`$22dd&0x40`); flag group `B` = west castle.

### Room 1 Gourds

| Tile | East flag | East item | West flag | West item |
|------|-----------|-----------|-----------|-----------|
| `[15,12:17,13]` | `$2279&0x20` | Call Beads (0x0807) ×1 | `$2276&0x20` | Brimstone ×? |
| `[31,10:33,11]` | `$227b&0x04` | Gold ×50 | `$2278&0x04` | Amulet of Annihilation (OBJ 1 loaded; `$2517+=1`) |
| `[33,10:35,11]` | `$227b&0x08` | Feather ×1 | `$2278&0x08` | Gold ×100 |
| `[38,10:3a,11]` | `$227b&0x10` | Limestone ×2 | `$2278&0x10` | Acorns ×? |
| `[61,2b:63,2c]` | `$2278&0x40` | Honey ×1 | `$2275&0x40` | Acorns ×1 |

### Room 2 Gourds

| Tile | East flag | East item | West flag | West item |
|------|-----------|-----------|-----------|-----------|
| `[61,2b:63,2c]`* | `$2279&0x01` | Wax ×3 | `$2276&0x01` | _(west room 2 content)_ |

_*This tile's dispatch covers rooms 1+2+others — see dispatch logic in enter script._

### Room 4 Gourds

| Tile | East flag | East item | West flag | West item |
|------|-----------|-----------|-----------|-----------|
| `[45,12:47,13]` | `$227a&0x10` | Ethanol ×2 | `$2277&0x10` | Ash ×5 |
| `[51,12:53,13]` | `$227a&0x20` | Vinegar ×2 | `$2277&0x20` | Biscuit (0x0803) ×1 |

### Room 6–8 Gourds (Dispatch by `$234b`)

| Tile | `$234b` | East flag | East item | West flag | West item |
|------|---------|-----------|-----------|-----------|-----------|
| `[57,12:59,13]` | 6 | `$227a&0x40` | Limestone ×1 | `$2277&0x40` | Amulet of Annihilation (OBJ 6 loaded) |
| `[53,1b:55,1c]` | 7 | `$227b&0x02` | Crystal (0x020f) ×1 | `$2278&0x02` | Limestone ×1 |
| `[54,34:56,35]` | 6 | `$227a&0x01` | Iron ×4 | `$2277&0x01` | Petal (0x0800) ×1 |
| `[54,34:56,35]` | 7 | `$227a&0x08` | Ethanol ×2 | `$2277&0x08` | Nectar ×3 |
| `[70,12:72,13]` | 6 | `$2279&0x40` | Wax (0x0200) ×2 | `$2276&0x40` | Water ×5 |
| `[70,12:72,13]` | 7 | `$227a&0x02` | Brimstone ×1 | `$2277&0x02` | Gold-Plated Vest (0x0408) ×1 |
| `[70,12:72,13]` | 8 | `$227a&0x80` | Vinegar ×5 | `$2277&0x80` | Ethanol ×2 |
| `[73,12:75,13]` | 6 | `$2279&0x80` | Ash ×7 | `$2276&0x80` | Vinegar ×3 |
| `[73,12:75,13]` | 7 | `$227a&0x04` | Nectar ×? | `$2277&0x04` | Amulet of Annihilation (OBJ 8 loaded) |
| `[73,12:75,13]` | 8 | `$227b&0x01` | Water ×5 | `$2278&0x01` | Ash ×5 |

### Amulet of Annihilation Gourds (West Castle)

Three west-castle gourds yield an Amulet of Annihilation. Each:
- Loads the OBJ marker (OBJ 1, 6, or 8)
- Increments `$2517` (global Amulet count)
- Sets its respective persistence bit

## Lance Cutscene (`$234b == 7`, east hall)

Triggered when entering Room 7 via east hall (`$22ec&0x10`) and `$225a&0x08` is NOT set:

1. Lance NPC (`VILLAGER_3_5` 0x55) stands at `[c7,19]`
2. On player approach: NPC delivers alchemy lesson dialog
3. Sets `$225a|=0x08` (Lance formula learned)
4. Sets `$22eb|=0x40` (door-open SFX flag for return to exterior)
5. Opens ingredient shop: `$2459 = 0x000c`
6. Teaches alchemy formula 0x26: **Lance = Iron + Acorn**

After `$225a&0x08` is set, Lance NPC displays a post-cutscene talk on subsequent visits.

## NPCs

| NPC ID | Enum | Sub-areas | Role |
|--------|------|-----------|------|
| 0x51 | `VILLAGER_3_2` | 8 | Pedestrian (east hall) |
| 0x52 | `VILLAGER_3_3` | 4 | Pedestrian |
| 0x53 | `VILLAGER_3_4` | 1, 4, 8 | Pedestrian / Regrowth Lady |
| 0x54 | `VILLAGER_3_5` | — | Pedestrian |
| 0x55 | `VILLAGER_3_5` | 1–7 | Pedestrian / Cecil / Lance / shop |
| 0x56 | `VILLAGER_3_6` | 2, 3, 5 | Pedestrian / guard |

## Memory Access

| Address | Bit | Type | Name | Notes |
|---------|-----|------|------|-------|
| `$22dd` | `0x40` | 📖 | East castle (Ebon Keep) active | Dual-gourd / NPC / music toggle |
| `$22dc` | `0x08` | 📖 | WindWalker unlocked | Music formula |
| `$22ec` | `0x10` | 📖 | East hall sub-state | Routes room 6/7/8 NPC loading |
| `$22de` | `0x80` | 📖 | Talked to Cecil | Set by Cecil NPC interact |
| `$225a` | `0x08` | 📖 | Lance alchemy learned | Set by Lance cutscene |
| `$22eb` | `0x40` | ⚙️ | Step-out door SFX pending | Set after Lance cutscene |
| `$22ee` | `0x01` | ⚙️ | Entry from professor's lab | Cleared on use (room 5) |
| `$234b` | word | ⚙️ | Sub-room dispatch ID | 1–9 |
| `$2459` | word | ⚙️ | Ingredient shop ID | Set to `0x000c` after Lance |
| `$2517` | word | 💎 | Amulet of Annihilation count | Incremented by 3 west-castle gourds |
| `$2276` | `0x20` | 🫙 | Room 5 west gourd OBJ 0 | `$2276&0x20` |
| `$2276` | `0x40` | 🫙 | Gourd Room 6 west [70,12] looted | Water ×5 |
| `$2276` | `0x80` | 🫙 | Gourd Room 6 west [73,12] looted | Vinegar ×3 |
| `$2277` | `0x01` | 🫙 | Gourd Room 6 west [54,34] looted | Petal ×1 [0x7d] (0x01) |
| `$2277` | `0x02` | 🫙 | Gourd Room 7 west [70,12] looted | Gold-Plated Vest [0x7d] (0x02) |
| `$2277` | `0x04` | 🫙 | Gourd Room 7 west [73,12] looted | Amulet of Annihilation [0x7d] (0x04) |
| `$2277` | `0x08` | 🫙 | Gourd Room 7 west [54,34] looted | Nectar ×3 [0x7d] (0x08) |
| `$2277` | `0x10` | 🫙 | Gourd Room 4 west [45,12] looted | Ash ×5 [0x7d] (0x10) |
| `$2277` | `0x20` | 🫙 | Gourd Room 4 west [51,12] looted | Biscuit [0x7d] (0x20) |
| `$2277` | `0x40` | 🫙 | Gourd Room 6 west [57,12] looted | Amulet of Annihilation [0x7d] (0x40) |
| `$2277` | `0x80` | 🫙 | Gourd Room 8 west [70,12] looted | Ethanol ×2 [0x7d] (0x80) |
| `$2278` | `0x01` | 🫙 | Gourd Room 8 west [73,12] looted | Ash ×5 [0x7d] (0x01) |
| `$2278` | `0x02` | 🫙 | Gourd Room 7 west [53,1b] looted | Limestone [0x7d] (0x02) |
| `$2278` | `0x04` | 🫙 | Gourd Room 1 west [31,10] looted | Amulet of Annihilation [0x7d] (0x04) |
| `$2278` | `0x08` | 🫙 | Gourd Room 1 west [33,10] looted | Gold ×100 [0x7d] (0x08) |
| `$2278` | `0x10` | 🫙 | Gourd Room 1 west [38,10] looted | Acorns [0x7d] (0x10) |
| `$2278` | `0x20` | 🫙 | Room 1 west gourd (enter) | — |
| `$2278` | `0x40` | 🫙 | Gourd Room 1 west [61,2b] looted | Honey? [0x7d] (0x40) |
| `$2278` | `0x80` | 🫙 | Room 2 west gourd (enter) | — |
| `$2279` | `0x01` | 🫙 | Gourd Room 2 west [61,2b] looted | — [0x7d] (0x01) |
| `$2279` | `0x02` | 🫙 | Room 3 west gourd A (enter) | — |
| `$2279` | `0x04` | 🫙 | Room 3 west gourd B (enter) | — |
| `$2279` | `0x08` | 🫙 | Room 4 west gourd A (enter) | — |
| `$2279` | `0x10` | 🫙 | Room 4 west gourd B (enter) | — |
| `$2279` | `0x20` | 🫙 | Gourd Room 1 east [15,12] looted | Call Beads [0x7d] (0x20) |
| `$2279` | `0x40` | 🫙 | Gourd Room 6 east [70,12] looted | Wax ×2 [0x7d] (0x40) |
| `$2279` | `0x80` | 🫙 | Gourd Room 6 east [73,12] looted | Ash ×7 [0x7d] (0x80) |
| `$227a` | `0x01` | 🫙 | Gourd Room 6 east [54,34] looted | Iron ×4 [0x7d] (0x01) |
| `$227a` | `0x02` | 🫙 | Gourd Room 7 east [70,12] looted | Brimstone ×1 [0x7d] (0x02) |
| `$227a` | `0x04` | 🫙 | Gourd Room 7 east [73,12] looted | Nectar [0x7d] (0x04) |
| `$227a` | `0x08` | 🫙 | Gourd Room 7 east [54,34] looted | Ethanol ×2 [0x7d] (0x08) |
| `$227a` | `0x10` | 🫙 | Gourd Room 4 east [45,12] looted | Ethanol ×2 [0x7d] (0x10) |
| `$227a` | `0x20` | 🫙 | Gourd Room 4 east [51,12] looted | Vinegar ×2 [0x7d] (0x20) |
| `$227a` | `0x40` | 🫙 | Gourd Room 6 east [57,12] looted | Limestone ×1 [0x7d] (0x40) |
| `$227a` | `0x80` | 🫙 | Gourd Room 8 east [70,12] looted | Vinegar ×5 [0x7d] (0x80) |
| `$227b` | `0x01` | 🫙 | Gourd Room 8 east [73,12] looted | Water ×5 [0x7d] (0x01) |
| `$227b` | `0x02` | 🫙 | Gourd Room 7 east [53,1b] looted | Crystal ×1 [0x7d] (0x02) |
| `$227b` | `0x04` | 🫙 | Gourd Room 1 east [31,10] looted | Gold ×50 [0x7d] (0x04) |
| `$227b` | `0x08` | 🫙 | Gourd Room 1 east [33,10] looted | Feather ×1 [0x7d] (0x08) |
| `$227b` | `0x10` | 🫙 | Gourd Room 1 east [38,10] looted | Limestone ×2 [0x7d] (0x10) |
| `$227b` | `0x20` | 📖 | OBJ 31 collected (Room 5 east) | — |
| `$275a` | — | — | Room 1 east gourd A (enter) | — |
| `$2275` | `0x20` | 🫙 | Room 1 west gourd A (enter) | — |
| `$2275` | `0x40` | 🫙 | Gourd Room 1 west [61,2b] looted? | Acorns ×1 [0x7d] |

## Drop Table

_No drop table configured for this room._

## Notes

- The dual-gourd system (`$227a`–`$227b` east vs. `$2276`–`$2278` west) maps directly to the castle you are in when you enter 0x7d — Ebon Keep (east) and Ivor Tower (west) interiors are the same physical room with different contents
- `$225a&0x08` (Lance alchemy learned) is a key progression flag — once set, Lance's shop opens and the formula becomes available
- Cecil (`$22de&0x80`) is a named story NPC with a unique talk flag; only in east castle Room 5
- `$22ec&0x10` (east hall) controls which of two NPC sets loads in rooms 6–8; the exact trigger setting is not yet documented — likely set by a story event
- The Regrowth Lady (0x53 via `0x1a46`) appears in east Room 8 and presumably teaches or sells the Regrowth alchemy formula
- `$2276`–`$2279` bits for rooms 1–4 enter script OBJ management: exact per-bit mapping partially reconstructed here; some bits marked uncertain (enter-script only vs. B-trigger looted)
