# 0x67 — Prehistoria: Bugmuck Exterior

**ROM address:** `0x9fff83`  
**Data address:** `0x9eabdf`  
**Enter script:** `0x92821e` → `0x93b7ca`  
**Act:** 1 — Prehistoria

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on zones | 13 (4 map exits + 3 to BBM/Bug rooms + 2 north to desert + 2 bug-leg reset + 2 cave) |
| B-trigger zones | 42 (34 sniff spots + 8 gourds) |
| Gourds | 8 |
| Sniff spots | 34 unique |
| Enemy spawners | 16 (+5 post-Thraxx) NPC `0x0e`, 7× NPC `0x0a`, 8× NPC `0x0f` (static spawned) |
| Music | `0x14` (Bugmuck / swamp theme) |

---

## Connections

| Direction | Zone | Destination | Notes |
|-----------|------|-------------|-------|
| North (step-on) | `[14,0b:18,0e]` | `0x59` Quick sand desert @ `0x04f0` | Global script `0x26` (indoor→outdoor) |
| North (step-on) | `[19,0b:22,0e]` | `0x59` Quick sand desert @ `0x04f0` | Sets `$22eb\|=0x10`; script `0x27` |
| North/cave (step-on) | `[21,30:23,32]` | `0x35` Quicksand/Bugmuck caves @ `0x0148` | Writes `$234d=2`, `$234e=3`; script `0x26` |
| North/entrance (step-on) | `[4a,45:52,47]` | `0x16` BBM @ `0x0548` | Global script `0x26` |
| East (step-on) | `[48,24:4a,26]` | `0x17` Bug room 2 @ `0x0100` | Script `0x1d` |
| East (step-on) | `[48,29:4a,2b]` | `0x17` Bug room 2 @ `0x0190` | Script `0x1d` |
| East (step-on) | `[49,2f:4b,31]` | `0x17` Bug room 2 @ `0x0220` | Script `0x1d` |
| West (step-on) | `[52,24:54,26]` | `0x17` Bug room 2 @ `0x0100` | Script `0x19` (return from east entrance) |
| West (step-on) | `[52,29:54,2b]` | `0x17` Bug room 2 @ `0x0190` | Script `0x19` |
| West (step-on) | `[52,2f:54,31]` | `0x17` Bug room 2 @ `0x0220` | Script `0x19` |

---

## Memory Access

| Address | Bits | Category | R/W | Meaning |
|---------|------|----------|-----|---------|
| `$22eb` | `0x20` | ⚙️ | R/W | In animation — cleared on enter if set |
| `$22eb` | `0x10` | ⚙️ | W | Set on north exit step-on |
| `$22ec` | `0x04` | 📖 | R | On bug legs — if set, show objs 0–5 on enter |
| `$2260` | `0x10` | 📖 | R | Thraxx dead — adds 5 extra NPC `0x0e` spawners in north section |
| `$226f` | `0x80` | 🫙 | R/W | Gourd obj6 (Petal) looted |
| `$2270` | `0x01` | 🫙 | R/W | Gourd obj7 (Biscuit) looted |
| `$2270` | `0x02` | 🫙 | R/W | Gourd obj8 (Clay) looted |
| `$2270` | `0x04` | 🫙 | R/W | Gourd obj9 (Water) looted |
| `$2270` | `0x08` | 🫙 | R/W | Gourd obj10 (Crystal) looted |
| `$2270` | `0x10` | 🫙 | R/W | Gourd obj11 (Petal) looted |
| `$2270` | `0x20` | 🫙 | R/W | Gourd obj12 (Mammoth Guard) looted |
| `$2270` | `0x40` | 🫙 | R/W | Gourd obj13 (Crystal) looted |
| `$2299` | `0x01` | 👃 | R/W | Sniff Oil #14 |
| `$2299` | `0x02` | 👃 | R/W | Sniff Oil #15 |
| `$2299` | `0x04` | 👃 | R/W | Sniff Oil #16 |
| `$2299` | `0x08` | 👃 | R/W | Sniff Oil #17 |
| `$2299` | `0x10` | 👃 | R/W | Sniff Oil #18 |
| `$2299` | `0x20` | 👃 | R/W | Sniff Oil #19 |
| `$2299` | `0x40` | 👃 | R/W | Sniff Oil #20 |
| `$2299` | `0x80` | 👃 | R/W | Sniff Oil #21 |
| `$229a` | `0x01` | 👃 | R/W | Sniff Roots #22 |
| `$229a` | `0x02` | 👃 | R/W | Sniff Roots #23 |
| `$229a` | `0x04` | 👃 | R/W | Sniff Roots #24 |
| `$229a` | `0x08` | 👃 | R/W | Sniff Roots #25 |
| `$229a` | `0x10` | 👃 | R/W | Sniff Roots #26 |
| `$229a` | `0x20` | 👃 | R/W | Sniff Roots #27 |
| `$229a` | `0x40` | 👃 | R/W | Sniff Roots #28 |
| `$229a` | `0x80` | 👃 | R/W | Sniff Ash #29 |
| `$229b` | `0x01` | 👃 | R/W | Sniff Ash #30 |
| `$229b` | `0x02` | 👃 | R/W | Sniff Ash #31 |
| `$229b` | `0x04` | 👃 | R/W | Sniff Ash #32 |
| `$229b` | `0x08` | 👃 | R/W | Sniff Ash #33 |
| `$229b` | `0x10` | 👃 | R/W | Sniff Crystal #34 |
| `$229b` | `0x20` | 👃 | R/W | Sniff Crystal #36 |
| `$229b` | `0x40` | 👃 | R/W | Sniff Crystal #37 |
| `$229b` | `0x80` | 👃 | R/W | Sniff Clay #38 |
| `$229c` | `0x01` | 👃 | R/W | Sniff Clay #39 |
| `$229c` | `0x02` | 👃 | R/W | Sniff Clay #40 |
| `$229c` | `0x04` | 👃 | R/W | Sniff Clay #41 |
| `$229c` | `0x08` | 👃 | R/W | Sniff Wax #35 |
| `$229c` | `0x10` | 👃 | R/W | Sniff Wax #42 |
| `$229c` | `0x20` | 👃 | R/W | Sniff Wax #43 |
| `$229c` | `0x40` | 👃 | R/W | Sniff Wax #44 |
| `$229c` | `0x80` | 👃 | R/W | Sniff Wax #45 |
| `$229d` | `0x01` | 👃 | R/W | Sniff Wax #46 |
| `$229d` | `0x02` | 👃 | R/W | Sniff Wax #47 |
| `$2391` | — | ⚙️ | W | PRIZE (sniff/gourd content) |
| `$2395` | — | ⚙️ | W | MAP REF? |
| `$2461` | — | ⚙️ | W | NEXT ADD (gourd respawn delta) |
| `$238d` | — | 🎵 | R | CHANGE MUSIC flag |
| `$2433` | — | ⚙️ | W | Spawner group ID |
| `$22ea` | `0x01` | ⚙️ | R | Collected flag (engine result) |
| `$234d` | — | ⚙️ | W | Written `0x0002` before cave entrance |
| `$234e` | — | ⚙️ | W | Written `0x0003` before cave entrance |
| `$23a1`–`$23a9` | — | ⚙️ | W | Enemy drops: rate 10/2/1; Petal/(`0x0001`×10)/Nectar |
| `$23bf` | — | ⚙️ | W | Written `0x0000` on enter |
| `$23c1` | — | ⚙️ | W | Written `0x0001` on enter |
| `$0ea2` | — | ⚙️ | W | Unknown engine register |
| `$0eac` | — | ⚙️ | W | Unknown = `0x172b` |

---

## Objects

### Bug-Leg Platform Objects

| Obj | Behavior |
|-----|----------|
| 0–5 | Shown (state=1) if `$22ec&0x04` on enter; reset to state=0 by step-on exit zones |

**`// TODO: determine what sets $22ec bit 0x04 (entering giant bug ride?)`**

### Gourds

| Obj | Persistence | Zone | Content | Notes |
|-----|-------------|------|---------|-------|
| 6 | `$226f` bit `0x80` | `[60,25:62,27]` | Petal | MapRef `0x0006` |
| 7 | `$2270` bit `0x01` | `[35,39:37,3b]` | Biscuit | MapRef `0x0007` |
| 8 | `$2270` bit `0x02` | `[2b,4a:2d,4c]` | Clay | MapRef `0x0008` |
| 9 | `$2270` bit `0x04` | `[1b,42:1d,44]` | Water | MapRef `0x0009`; NEXT_ADD=3 |
| 10 | `$2270` bit `0x08` | `[28,2e:2a,30]` | Crystal | MapRef `0x000a`; NEXT_ADD=1 |
| 11 | `$2270` bit `0x10` | `[35,2d:37,2f]` | Petal | MapRef `0x000b` |
| 12 | `$2270` bit `0x20` | `[22,2b:24,2d]` | Mammoth Guard | MapRef `0x000c`; item `0x041a` |
| 13 | `$2270` bit `0x40` | `[23,1e:25,20]` | Crystal | MapRef `0x000d`; NEXT_ADD=1 |

### Sniff Spots

| # | Persistence | Zone | Content | MapRef |
|---|-------------|------|---------|--------|
| 14 | `$2299` bit `0x01` | `[15,31:16,32]` | Oil | `0x000e` |
| 15 | `$2299` bit `0x02` | `[24,3f:25,40]` | Oil | `0x000f` |
| 16 | `$2299` bit `0x04` | `[2b,51:2c,52]` | Oil | `0x0010` |
| 17 | `$2299` bit `0x08` | `[2a,26:2b,27]` | Oil | `0x0011` |
| 18 | `$2299` bit `0x10` | `[39,1c:3a,1d]` | Oil | `0x0012` |
| 19 | `$2299` bit `0x20` | `[3d,19:3e,1a]` | Oil | `0x0013` |
| 20 | `$2299` bit `0x40` | `[59,20:5a,21]` | Oil | `0x0014` |
| 21 | `$2299` bit `0x80` | `[57,4e:58,4f]` | Oil | `0x0015` |
| 22 | `$229a` bit `0x01` | `[15,1e:16,1f]` | Roots | `0x0016` |
| 23 | `$229a` bit `0x02` | `[1d,3c:1e,3d]` | Roots | `0x0017` |
| 24 | `$229a` bit `0x04` | `[30,39:31,3a]` | Roots | `0x0018` |
| 25 | `$229a` bit `0x08` | `[2a,1d:2b,1e]` | Roots | `0x0019` |
| 26 | `$229a` bit `0x10` | `[52,10:53,11]` | Roots | `0x001a` |
| 27 | `$229a` bit `0x20` | `[4f,4d:50,4e]` | Roots | `0x001b` |
| 28 | `$229a` bit `0x40` | `[63,30:64,31]` | Roots | `0x001c` |
| 29 | `$229a` bit `0x80` | `[1c,11:1d,12]` | Ash | `0x001d` |
| 30 | `$229b` bit `0x01` | `[1b,18:1c,19]` | Ash | `0x001e` |
| 31 | `$229b` bit `0x02` | `[2a,2b:2b,2c]` | Ash | `0x001f` |
| 32 | `$229b` bit `0x04` | `[5b,37:5c,38]` | Ash | `0x0020` |
| 33 | `$229b` bit `0x08` | `[60,3a:61,3b]` | Ash | `0x0021` |
| 34 | `$229b` bit `0x10` | `[13,2c:14,2d]` | Crystal | `0x0022`; NEXT_ADD=2 |
| 35 | `$229c` bit `0x08` | `[1c,20:1d,21]` | Wax | `0x0023` |
| 36 | `$229b` bit `0x20` | `[31,41:32,42]` | Crystal | `0x0024`; NEXT_ADD=1 |
| 37 | `$229b` bit `0x40` | `[3b,0e:3c,0f]` | Crystal | `0x0025` |
| 38 | `$229b` bit `0x80` | `[1d,2f:1e,30]` | Clay | `0x0026` |
| 39 | `$229c` bit `0x01` | `[33,33:34,34]` | Clay | `0x0027` |
| 40 | `$229c` bit `0x02` | `[3a,15:3b,16]` | Clay | `0x0028` |
| 41 | `$229c` bit `0x04` | `[60,23:61,24]` | Clay | `0x0029` |
| 42 | `$229c` bit `0x10` | `[17,3a:18,3b]` | Wax | `0x002a` |
| 43 | `$229c` bit `0x20` | `[20,43:21,44]` | Wax | `0x002b` |
| 44 | `$229c` bit `0x40` | `[2d,48:2e,49]` | Wax | `0x002c` |
| 45 | `$229c` bit `0x80` | `[32,1a:33,1b]` | Wax | `0x002d` |
| 46 | `$229d` bit `0x01` | `[40,3b:41,3c]` | Wax | `0x002e` |
| 47 | `$229d` bit `0x02` | `[5d,3c:5e,3d]` | Wax | `0x002f` |

---

## NPCs / Enemies

| Sprite ID | Name | Count | Spawn type | Notes |
|-----------|------|-------|-----------|-------|
| `0x0f` (unknown) | Unknown (NPC 0x0f) | 8 | `3c` static spawned | Groups 6/8/10/8/6/8/10/8; flags `0x8400`; `// TODO: identify` |
| `0x0e` (unknown) | Unknown (NPC 0x0e) | 16+5 | `c2` roaming spawner | Group 1; 5 extra spawned if Thraxx dead (`$2260&0x10`); `// TODO: identify` |
| `0x0a` (unknown) | Unknown (NPC 0x0a) | 7 | `c2` roaming spawner | Group 1; `// TODO: identify` |

---

## Enemy Drop Table

| Slot | Rate | Item | Qty |
|------|------|------|-----|
| 1 | `0x0a` | `0x0800` (PETAL) | 1 |
| 2 | `0x02` | `0x0001` qty=10 | 10 |
| 3 | `0x01` | `0x0801` (NECTAR) | 1 |

---

## Bug-Leg Platform Mechanics

Two step-on zones reset the bug-leg platform objects (objs 0–5) back to state=0 when the player walks off them:

| Zone | Objs reset |
|------|-----------|
| `[59,34:5e,35]` | 3, 4, 5 |
| `[3e,34:41,35]` + `[40,20:44,21]` | 2, 1, 0 |

On enter, if `$22ec&0x04` (player was on bug legs), the objects are force-shown (state=1).

---

## External Scripts

| Opcode | Callee | Purpose |
|--------|--------|---------|
| `0x00` | `"Fade-out / stop music"` | Standard enter fade-out |
| `0x01` | `"Fade-in / start music"` | Standard enter fade-in |
| `0x19` | `"Prepare room change? West exit/east entrance outdoor-outdoor?"` | Return exits from Bug room 2 |
| `0x1d` | `"Prepare room change? East exit/west entrance outdoor-outdoor?"` | East exits to Bug room 2 |
| `0x26` | `"Prepare room change? North exit/south entrance outdoor-indoor?"` | North/cave entries |
| `0x27` | `"Prepare room change? North exit/south entrance indoor-outdoor?"` | Second north exit |
| `0x39` | `"Loot nature?"` | Sniff spot B-triggers |
| `0x3a` | `"Loot gourd?"` | Gourd B-triggers |
| `0x92de75` | `"Some cinematic script (used multiple times)"` | End of enter sequence |

---

## Enter Script Summary

1. In-animation branch (standard).
2. Set enemy drop table: Petal/`0x0001`×10/Nectar; rates 10/2/1.
3. Unload 34 already-collected sniff spots (objs 14–31, 0x20–0x2f via `$2299`–`$229d`).
4. Write `$23c1=0x0001`.
5. Load 8 static NPC `0x0f` spawners at various coords with flags `0x8400`.
6. Unload already-collected gourds (objs 6–13 via `$226f&0x80` and `$2270` bits).
7. Add 16 NPC `0x0e` + 7 NPC `0x0a` roaming spawners.
8. If Thraxx dead: add 5 more NPC `0x0e` spawners in the north section (`y≤0x23`).
9. If `$22ec&0x04` (on bug legs): show objs 0–5 (bug leg platforms).
10. If music not set: play music `0x14`, fade in.
11. Clear `$23bf`, call cinematic script.

---

## Notes

- **Mammoth Guard (`0x041a`)** in gourd obj12 is a rare alchemy item found here. Its precise ITEM enum mapping is unclear — `0x041a` falls outside the documented alchemy/consumable sections of `core.evs`.  
  - `// TODO: resolve ITEM 0x041a (Mammoth Guard) in enum`
- **Sniff spot renumbering:** spots in this room use numbers #14–#47, continuing the global namespace from desert (#14–#46 in 0x59) and jungle (#0–#13 in 0x5b). Wax #44–#47 in this room overlap with Wax #44–#46 in 0x59 — this is the same physical sniff spot (shared persistence bits in `$229c`/`$229d`).
  - `// TODO: verify whether $229c&0x40/$229c&0x80/$229d&0x01/$229d&0x02 are truly shared between 0x59 and 0x67`
- **Bug-leg mechanic:** Objects 0–5 are the elevated platforms accessible by riding the giant bug enemy. `$22ec bit 0x04` persists between room transitions so the platforms stay in the correct state when re-entering.
- **Three enemy types** (0x0a, 0x0e, 0x0f) are loaded but not identified in `core.evs`. All three appear in Act 1 exterior bugmuck/desert rooms.
  - `// TODO: identify NPC sprite IDs 0x0a, 0x0e, 0x0f`
- **Music `0x14`** = Bugmuck/swamp theme; differs from Prehistoria overworld (`0x12`) and jungle (`0x0a`).
