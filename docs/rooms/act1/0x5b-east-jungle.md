# 0x5b — Prehistoria: East Jungle

**ROM address:** `0x9fff53`  
**Data address:** `0xa78000`  
**Enter script:** `0x9281e2` → `0x93b1ac`  
**Act:** 1 — Prehistoria

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on zones | 5 |
| B-trigger zones | 17 (14 unique spots; 3 have dual coverage) |
| Gourds | 0 |
| Sniff spots | 14 |
| NPCs / Enemies | FLOWER_PURPLE ×12 (2 static + 10 spawned), SKELESNAIL ×4–5 (conditional static) |
| Music | `0x0a` (Prehistoria jungle) |

---

## Connections

| Direction | Zone | Destination | Notes |
|-----------|------|-------------|-------|
| West (step-on) | `[10,23:12,25]` | `0x25` Fire Eyes' Village | |
| East (step-on) | `[45,11:47,14]` | `0x59` Quick sand desert @ `0x00a8` | Sets `$22eb\|=0x10` |
| East (step-on) | `[45,18:47,1d]` | `0x59` Quick sand desert @ `0x0110` | Middle east exit |
| East (step-on) | `[45,20:47,27]` | `0x59` Quick sand desert @ `0x0150` | Calls global script `0x1e` |
| North (step-on) | `[17,0c:1b,0d]` | `0x36` Both fire pits @ `0x0160` | Clears `$237d = 0x0000` |

---

## Memory Access

| Address | Bits | Category | R/W | Meaning |
|---------|------|----------|-----|---------|
| `$2260` | `0x10` | 📖 | R | Thraxx dead (enables static SKELESNAIL at 45,21) |
| `$22eb` | `0x10` | ⚙️ | W | Set on first east exit step-on |
| `$22eb` | `0x20` | ⚙️ | R/W | In animation — cleared on enter if set |
| `$22eb` | `0x04` | ⚙️ | R | Showcase/attraction mode flag |
| `$22f2` | `0x01` | 📖 | R | In credits — triggers credits-scroll cutscene on enter |
| `$2294` | `0x20` | 👃 | R/W | Sniff spot #1 (Roots) looted |
| `$2294` | `0x40` | 👃 | R/W | Sniff spot #2 (Roots) looted |
| `$2294` | `0x80` | 👃 | R/W | Sniff spot #5 (Roots) looted |
| `$2295` | `0x01` | 👃 | R/W | Sniff spot #6 (Roots) looted |
| `$2295` | `0x02` | 👃 | R/W | Sniff spot #7 (Roots) looted |
| `$2295` | `0x04` | 👃 | R/W | Sniff spot #0 (Water) looted |
| `$2295` | `0x08` | 👃 | R/W | Sniff spot #11 (Water) looted |
| `$2295` | `0x10` | 👃 | R/W | Sniff spot #12 (Water) looted |
| `$2295` | `0x20` | 👃 | R/W | Sniff spot #3 (Water) looted |
| `$2295` | `0x40` | 👃 | R/W | Sniff spot #4 (Water) looted |
| `$2295` | `0x80` | 👃 | R/W | Sniff spot #13 (Clay) looted |
| `$2296` | `0x01` | 👃 | R/W | Sniff spot #8 (Clay) looted |
| `$2296` | `0x02` | 👃 | R/W | Sniff spot #9 (Clay) looted |
| `$2296` | `0x04` | 👃 | R/W | Sniff spot #10 (Clay) looted |
| `$237d` | — | 🎥 | W | Cleared to `0x0000` before exit to `0x36` |
| `$238d` | — | 🎵 | R | CHANGE MUSIC flag (skip play if set) |
| `$2391` | — | ⚙️ | W | PRIZE (sniff content) |
| `$2395` | — | ⚙️ | W | MAP REF? (sniff object index) |
| `$2433` | — | ⚙️ | W | Spawner group ID (`0x0001` = FLOWER_PURPLE group, `0x0002` = SKELESNAIL group) |
| `$23a1` | — | ⚙️ | W | PRIZE_DROP_1 = `0x0800` (PETAL) |
| `$23a3` | — | ⚙️ | W | PRIZE_DROP_2 = `0x0001` qty=7 (`// TODO: identify item 0x0001 in enemy prize context`) |
| `$23a5` | — | ⚙️ | W | PRIZE_DROP_3 = `0x0200` (`// TODO: identify item 0x0200 in enemy prize context`) |
| `$239b` | — | ⚙️ | W | PRIZE_RATE_1 = `0x0a` |
| `$239d` | — | ⚙️ | W | PRIZE_RATE_2 = `0x02` |
| `$239f` | — | ⚙️ | W | PRIZE_RATE_3 = `0x01` |
| `$22ea` | `0x01` | ⚙️ | R | Sniff collected (engine result; written to persistence bit) |
| `$23e9` | — | 🎥 | W | Camera X start = `0x0000` |
| `$23eb` | — | 🎥 | W | Camera Y start = `0x0030` |
| `$23ed` | — | 🎥 | W | Camera X end = `0x0370` |
| `$23ef` | — | 🎥 | W | Camera Y end = `0x0290` |
| `$23bf` | — | ⚙️ | W | Written `0x0000` on enter |
| `$0ea2` | — | ⚙️ | W | Unknown engine register (set on enter) |
| `$0eac` | — | ⚙️ | W | Unknown engine register set to `0x172b` on enter |

---

## Objects (Sniff Spots)

| Obj | Persistence | Zone | Content |
|-----|-------------|------|---------|
| 0 | `$2295` bit `0x04` | `[24,30:25,31]` | Water — MapRef `0x0000` |
| 1 | `$2294` bit `0x20` | `[1f,21:20,22]` | Roots — MapRef `0x0001` |
| 2 | `$2294` bit `0x40` | `[1a,1f:1b,20]` | Roots — MapRef `0x0002` |
| 3 | `$2295` bit `0x20` | `[31,0f:32,10]` | Water — MapRef `0x0003` |
| 4 | `$2295` bit `0x40` | `[36,31:37,32]` | Water — MapRef `0x0004` |
| 5 | `$2294` bit `0x80` | `[3c,15:3d,16]` | Roots — MapRef `0x0005` |
| 6 | `$2295` bit `0x01` | `[2a,21:2b,22]` | Roots — MapRef `0x0006` |
| 7 | `$2295` bit `0x02` | `[1f,18:20,19]` | Roots — MapRef `0x0007` |
| 8 | `$2296` bit `0x01` | `[17,2b:18,2c]` | Clay — MapRef `0x0008` |
| 9 | `$2296` bit `0x02` | `[41,1c:42,1d]` | Clay — MapRef `0x0009` |
| 10 | `$2296` bit `0x04` | `[36,2e:37,2f]` | Clay — MapRef `0x000a` |
| 11 | `$2295` bit `0x08` | `[15,12:16,13]` + `[15,14:16,15]` | Water — MapRef `0x000b` (dual-zone) |
| 12 | `$2295` bit `0x10` | `[14,13:15,14]` + `[13,19:14,1a]` | Water — MapRef `0x000c` (dual-zone) |
| 13 | `$2295` bit `0x80` | `[27,29:28,2a]` + `[27,2a:28,2b]` | Clay — MapRef `0x000d` (dual-zone) |

---

## NPCs / Enemies

| Sprite ID | Name | Type | Count | Notes |
|-----------|------|------|-------|-------|
| `0x0b` (FLOWER_PURPLE) | Wimpy Flower | Enemy spawner | 10 spawners + 2 static | Static at `(0f,3f)` and `(23,3b)`; spawner group `$2433=0x0001` |
| `0x26` (SKELESNAIL) | Skelesnail | Enemy spawner | 4 spawners | Group `$2433=0x0002` at `(4b,15)`, `(41,31)`, `(57,25)`, `(53,3d)` |
| `0x26` (SKELESNAIL) | Skelesnail | Static (conditional) | 0–1 | Loaded at `(45,21)` only if Thraxx dead (`$2260&0x10`) |

---

## Enemy Drop Table

| Slot | Rate | Item | Qty | Notes |
|------|------|------|-----|-------|
| 1 | `0x0a` | `0x0800` (PETAL) | 1 | Most common drop |
| 2 | `0x02` | `0x0001` qty=7 | 7 | `// TODO: identify item 0x0001 in enemy prize context` |
| 3 | `0x01` | `0x0200` | 1 | `// TODO: identify item 0x0200 in enemy prize context` |

---

## External Scripts

| Opcode | Callee | Purpose |
|--------|--------|---------|
| `0x00` | `"Fade-out / stop music"` | Standard enter fade-out |
| `0x01` | `"Fade-in / start music"` | Standard enter fade-in |
| `0x19` | `"Prepare room change? West exit/east entrance outdoor-outdoor?"` | West exit |
| `0x1d` | `"Prepare room change? East exit/west entrance outdoor-outdoor?"` | East exits |
| `0x1e` | `"Unnamed Global script 0x1e"` | Called by southern east exit |
| `0x27` | `"Prepare room change? North exit/south entrance indoor-outdoor?"` | North exit to 0x36 |
| `0x39` | `"Loot nature?"` | Called by all B-triggers |
| `0x59` | `"Attraction mode, after Thraxx"` | Showcase mode sequence |
| `0x5a` | `"Credits"` | Called if `$22f2&0x01` (in credits) |
| `0x92de75` | `"Some cinematic script (used multiple times)"` | End of normal enter sequence |

---

## Enter Script Summary

1. **In-animation branch:** if `$22eb&0x20` — clear flag; else teleport both to `(09, 37)` and fade out.
2. **Credits check:** if `$22f2&0x01`, run credits-scroll cutscene (`0x93b10a`): hides status bar, stops players, slowly scrolls camera east to west while animating NPC sprites (VILLAGER_1_4 and VILLAGER_1_2), then calls `"Credits"` (0x5a).
3. Set unknown engine registers (`$0ea2`, `$0eac`).
4. Set enemy drop table (Petal, ?, ?; rates 10/2/1).
5. Set camera bounds `[0x0000,0x0370] × [0x0030,0x0290]`.
6. Unload already-collected sniff spots (objs 0–13 via `$2294`–`$2296` bits).
7. Load 2 static FLOWER_PURPLE at `(0f,3f)` and `(23,3b)`.
8. Spawn 10 FLOWER_PURPLE spawners (group 1) across the map.
9. Spawn 4 SKELESNAIL spawners (group 2) in east section.
10. If Thraxx dead: load 1 static SKELESNAIL at `(45,21)`.
11. If music not set: play music `0x0a`, fade in.
12. Reset camera bounds (second write), clear `$23bf`.
13. **Showcase check:** if `$22eb&0x04`, run attraction mode demo animation, then call `"Attraction mode, after Thraxx"`. Otherwise call `"Some cinematic script"`.

---

## Notes

- **Three east exits** to `0x59` with different Y entry coordinates, forming a wide transition band at `x=45–47`.
- **North exit to `0x36`** (Both fire pits) — only outdoor→indoor transition in this room; clears `$237d` before entering.
- **Credits cutscene** uses this room as the backdrop for the Act 1 credits scroll. The windwalker NPC (`0x000e>>1`=NPC 7 = VILLAGER_1_4) rides east while the villager (`0x000a>>1`=NPC 5 = VILLAGER_1_2) follows.
- **Sniff spots #11, #12, #13** each have two overlapping B-trigger zones (different tile coordinates, same script). Likely for wider hit detection on irregular terrain.
- **`$22eb bit 0x04`** (showcase mode) triggers an attraction-mode fly-by animation when the game is idle on the title screen.
- **SKELESNAIL at `(45,21)`** is a post-Thraxx addition — its purpose (quest NPC? barrier?) is not clear from the enter script alone.
  - `// TODO: identify role of static SKELESNAIL spawned post-Thraxx at (45,21)`
