# [0x55] Antiqua — 'mids Bottom Level (Dog Start)

## Header

| Field | Value |
|-------|-------|
| Room ID | 0x55 |
| Act | Antiqua (Act 2) |
| Data | `0x9ed770` |
| Enter script ptr | `0x9281c4` → `0x95936b` |
| Step-on table | `0x9ed77f`, len=0x011a (47 entries) |
| B-trigger table | `0x9ed89b`, len=0x0090 (24 entries) |
| Music | 0x20 |
| Dog | Greyhound |
| `$23bf` | 0 (cleared on entry) |

## Overview

The lower level of 'mids. Heavily puzzle-driven: four floor switch / pressure plate puzzles (`$22e0` bits), multiple platform mechanisms (`$22e1`/`$22e2` bits), an encounter with enemy group NPC 0x3a // TODO: verify ENEMY name, and the key Lotus Bridge switch puzzle (5 B-triggers, requires WEAPON_INDEX ≥ 0x12 / SPEAR_1 / Horn Spear) that frees the dog and sets `$22e3&0x40`. Boy and dog use separate entry points; split mechanic mirrors [0x06].

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22e0` | 0x10 | R/W | ⚙️ Gear puzzle A active [0x55] |
| `$22e0` | 0x20 | R/W | ⚙️ Gear puzzle B active [0x55] |
| `$22e0` | 0x40 | R/W | ⚙️ Gear puzzle C active [0x55] |
| `$22e0` | 0x80 | R/W | ⚙️ Gear puzzle D active [0x55] |
| `$22e1` | 0x01 | R/W | ⚙️ Mechanism A-1 activated [0x55] |
| `$22e1` | 0x02 | R/W | ⚙️ Mechanism A-2 activated [0x55] |
| `$22e1` | 0x04 | R/W | ⚙️ Mechanism B activated [0x55] |
| `$22e1` | 0x08 | R/W | ⚙️ Mechanism C-entry direction (south) [0x55] |
| `$22e1` | 0x10 | R/W | ⚙️ Mechanism D-entry direction [0x55] |
| `$22e1` | 0x20 | R/W | ⚙️ Exit N-left interaction done [0x55] |
| `$22e1` | 0x40 | R/W | ⚙️ Exit N-right interaction done [0x55] |
| `$22e1` | 0x80 | R/W | ⚙️ Lotus Bridge switch step 2 — OBJ 12 state [0x55] |
| `$22e2` | 0x01 | R/W | ⚙️ Lotus Bridge switch step 3 — OBJ 13 state [0x55] |
| `$22e2` | 0x02 | R/W | ⚙️ Lotus Bridge switch step 1 — OBJ 14 state [0x55] |
| `$22e2` | 0x04 | R/W | ⚙️ Lotus Bridge switch step 5 — OBJ 15 state (+ dog freed) [0x55] |
| `$22e2` | 0x08 | R/W | ⚙️ Lotus Bridge switch step 4 — OBJ 16 state [0x55] |
| `$22e2` | 0x40 | R | 📖 Enemy group (NPC 0x3a) defeated [0x55] // TODO: look up ENEMY 0x3a name — "Sons of Shyness" is unverified |
| `$22e3` | 0x40 | W | 📖 Dog freed from 'mids — set by B-trigger #23 (`$22e2&0x04`) [0x55] |
| `$22e4` | 0x01 | R/W | 📖 Sons encounter triggered [0x55] |
| `$22da` | 0x40 | R | ⚔️ AXE_2 (Bronze Axe) owned — skips Sons encounter |
| `$22eb` | 0x20 | R/W | ⚙️ IN_ANIMATION — entry teleport guard |
| `$22ee` | 0x01 | R/W | ⚙️ Special teleport flag — teleports both to [0xa9,0x13] if set |
| `$225c` | 0x80 | R | 💎 Horace's Call Beads owned — required to open Regenerate chest [0x55] |
| `$22db` | 0x80 | W | ⚗️ Horace's Regenerate — set when opened [0x55] |
| `$227c` | 0x20–0x80 | R/W | 🫙 Gourd persistence (OBJs 20–22) [0x55] |
| `$227d` | 0x01–0x80 | R/W | 🫙 Gourd persistence (OBJs 0x21/0x2b/0x22/0x2e/23–26) [0x55] |
| `$227e` | 0x01–0x80 | R/W | 🫙 Gourd persistence (OBJs 27–31/0x20/0x23) [0x55] |
| `$2834` | 0x01–0x80 | R/W | ⚙️ One-time switch/lever triggers [0x55] |
| `$235f` | — | R | ⚙️ CURRENT_WEAPON — value ≥ 0x12 (WEAPON_INDEX.SPEAR_1 / Horn Spear) gates Lotus Bridge switch B-triggers |
| `$2357` | — | R/W | ⚙️ Boy's 'mids destination (read on entry) |
| `$2358` | — | R/W | ⚙️ Dog's 'mids destination (read on entry) |
| `$2350` | — | W | ⚙️ Reset to 0 on entry |
| `$2261` | 0x01/0x02 | R/W | ⚙️ Dog/Boy unavailable flags |
| `$238d` | — | R | 🎵 CHANGE_MUSIC flag |
| `$23bf` | — | W | ⚙️ Cleared to 0 on entry |

## Enter Script Summary (`0x95936b`)

1. **Entry guard**: if `$22eb&0x20`: teleport both to [0x8a,0x87] + fade; else clear flag.
2. **Dog-freed state** (`$22e3&0x40`): write `$2357=1`, `$2358=1`; clear `$22e4&0x04`, `$22e5&0x04/0x02`; clear `$2261&0x02/0x01`; `$2350=0`.
3. **Special teleport** (`$22ee&0x01`): clear flag; write `$238f=0x000f`; teleport both to [0xa9,0x13].
4. **NPC**: LOAD NPC 0x38 flags/state 0x02 at [0xad,0x15] → `$283c`; talk scripts 0x187b/0x187e.
5. **Enemy drops**: PRIZE1=0x0801 (rate 10); PRIZE2=0x0001 qty 90 (rate 3); PRIZE3=0x0802 (rate 1).
6. `$23c5=0x0280`.
7. **Monster spawner** (sub `0x95910d`):
   - If `$22e2&0x40` (Sons defeated): extra NPC 0x39 at [0x82,0x2d] + NPC 0x74 at 2 positions.
   - Always: NPC 0x72 at ~13 positions; NPC 0x39 at ~12 positions; NPC 0x74 at ~12 positions.
8. **OBJ unload persistence**: `$227c&0x20–0x80` → OBJs 20–22; `$227d&0x01–0x80` → OBJs 0x21/0x2b/0x22/0x2e/23–26; `$227e&0x01–0x40` → OBJs 27–31/0x20/0x23.
9. **Music**: if `$238d != 0`: PLAY MUSIC 0x20; fade in.
10. **OBJ state restore** (sub `0x95900a`): 12 calls, restoring OBJs 12–16 and 0x24–0x2a based on `$22e1&0x80` and `$22e1/22e2&0x01–0x40`.
11. **Init**: `$23bf=0`; CHANGE DOGGO = Greyhound (0x06).
12. **Boy/dog split** (if NOT `$22e3&0x40`): same logic as [0x06] — marks unavailable char, teleports to holding position [0x0448,0x04ea].
13. **`$2350=0`**; END.

## Step-on Scripts (47 entries — condensed by function)

### Exits

| Tile | Description |
|------|-------------|
| [4a,55:4c,56] | **EXIT → 0x06** (Outside 'mids): dog `$2358=0`; boy `$2357=0`; `$22e5\|=0x02/0x04` → CHANGE MAP 0x06 [0x0260,0x0358] |
| [24,2a:26,2b] | **EXIT → 0x56** (top left): dog `$2358=2`; boy `$2357=2, $22e5\|=0x04` → CHANGE MAP 0x56 [0x0030,0x00c0] |
| [6f,41:71,42] | **EXIT → 0x56** (top right): same flags → CHANGE MAP 0x56 [0x05b0,0x0340] |

### Dog-only mechanics

| Tile | Description |
|------|-------------|
| [4a,48:4c,4a] | Dog-only: climbing up animation |
| [4a,4e:4c,50] | Dog-only: descending animation |

### Four floor switch / pressure plate puzzles (each with activation + 4 adjacent exit tiles)

| Tile | Flag | Description |
|------|------|-------------|
| [46,31:48,33] | `$22e0&0x10` | Switch A activate → OBJ 4 state 1; OBJ 0 state 3; SFX 0x38 |
| [53,31:55,33] | `$22e0&0x20` | Switch B activate → OBJ 5 state 1; OBJ 2 state 3 |
| [46,3c:48,3e] | `$22e0&0x40` | Switch C activate → OBJ 6 state 1; OBJ 1 state 3 |
| [53,3c:55,3e] | `$22e0&0x80` | Switch D activate → OBJ 7 state 1; OBJ 3 state 3 |
| [45,30:49,31] ×4 | `$22e0&0x10` | Switch A release → OBJ 4 state 0; OBJ 0 state 0 or 3 |
| [52,30:56,31] ×4 | `$22e0&0x20` | Switch B release → OBJ 5 state 0; OBJ 2 state 0 or 3 |
| [45,3b:49,3c] ×4 | `$22e0&0x40` | Switch C release → OBJ 6 state 0; OBJ 1 state 0 or 3 |
| [52,3b:56,3c] ×4 | `$22e0&0x80` | Switch D release → OBJ 7 state 0; OBJ 3 state 0 or 3 |

### Platform puzzle mechanisms

| Tile | Flag | Description |
|------|------|-------------|
| [1a,4a:1c,4b] | `$22e1&0x01` | Mechanism A-1: walk to [0x2d,0x85]; call OBJ 0x24 sub |
| [1b,4d:1d,4e] | `$22e1&0x01` | Mechanism A-1 alt: walk to [0x29,0x78]; call OBJ 0x24 sub |
| [1f,4a:21,4b] | `$22e1&0x02` | Mechanism A-2: walk to [0x35,0x85]; call OBJ 0x25 sub |
| [1f,4d:21,4e] | `$22e1&0x02` | Mechanism A-2 alt: walk to [0x33,0x78]; call OBJ 0x25 sub |
| [30,4a:35,4e] | `$22e1&0x04` | Mechanism B: walk to [0x55,0x76]; call OBJ 0x26 sub |
| [54,4d:56,4e] | `$22e1&0x08` | Mechanism C south-entry: walk both; call OBJ 0x27 sub |
| [53,4a:55,4b] | `$22e1&0x08` | Mechanism C north-entry: walk both; call OBJ 0x27 sub |
| [5a,4d:5c,4e] | `$22e1&0x10` | Mechanism D south-entry: walk both; call OBJ 0x28 sub |
| [5b,4a:5d,4b] | `$22e1&0x10` | Mechanism D north-entry: walk both; call OBJ 0x28 sub |
| [63,4e:66,4f] | `$22e1&0x20` | Exit area N-left (dog-freed only): walk both to exit; call OBJ 0x29 sub |
| [69,49:6b,4a] | `$22e1&0x40` | Exit area N-right (dog-freed only): walk both to exit; call OBJ 0x2a sub |

### Switch triggers (`$2834`)

| Tile | Flag | Sets | Description |
|------|------|------|-------------|
| [0f,1b:11,1d] | `$2834&0x02` | OBJ 8 state 1 | Switch: LOAD NPC 0x59; SFX 0x68 |
| [0d,21:0f,23] | `$2834&0x04` | OBJ 9 state 1 | Switch: LOAD NPC 0x59 |
| [0b,33:0d,35] | `$2834&0x08` | OBJ 11 state 1 | Switch: LOAD NPC 0x59 |
| [0d,3c:0f,3e] | `$2834&0x10` | OBJ 10 state 1 | Switch: LOAD NPC 0x59 |
| [77,44:79,46] | `$2834&0x20` | OBJ 17 state 1 | Lever: LOAD NPC 0x5a; no SFX |
| [75,3b:77,3d] | `$2834&0x40` | OBJ 18 state 1 | Lever: LOAD NPC 0x5a; SFX 0x68 |
| [75,32:77,34] | `$2834&0x80` | OBJ 19 state 1 | Lever: LOAD NPC 0x5a |

### Sons encounter

| Tile | Condition | Description |
|------|-----------|-------------|
| [32,29:37,2a] | NOT `$22da&0x40` AND NOT `$22e4&0x01` | FADE WHITE; spawn 2× NPC 0x3a (Sons) with scripts 0x1872/0x1875; `$22e4\|=0x01`; screen shake |

### Passive guards

| Tile | Description |
|------|-------------|
| [68,4a:6b,4e] | NOP — check only: `$235f==12 AND !$22e4&0x04` |
| [61,4a:66,4e] | NOP — check only: `$235f==12 AND !$22e4&0x04` |
| [6d,4a:6f,4e] | NOP (dummy step-on) |

## Exits

| Destination | Trigger | Player Spawn |
|-------------|---------|--------------|
| 0x06 Outside of 'mids | Step-on [4a,55:4c,56] | [0x0260, 0x0358] |
| 0x56 'mids top (left) | Step-on [24,2a:26,2b] | [0x0030, 0x00c0] |
| 0x56 'mids top (right) | Step-on [6f,41:71,42] | [0x05b0, 0x0340] |

## B-Triggers (24 entries)

| B# | Tile | Flag | Item/Effect | MAP REF |
|----|------|------|-------------|---------|
| 1 | [20,47:22,49] | `$2834&0x01` | ⚙️ One-time trigger → LOAD NPC 0x5a at [0x3a,0x76]; OBJ 0x2c state 1 | — |
| 2 | [1c,3b:1e,3d] | `$227d&0x02` | 🫙 Gourd OBJ 0x2b: Bone×2 [0x55] (0x02) | 0x002b |
| 3 | [6c,19:6e,1b] | `$227e&0x20` | 🫙 Horace's Regenerate (boy + `$225c&0x80`); else "Won't Open" [0x55] (0x20) | — |
| 4 | [62,3d:64,3f] | `$227e&0x10` | 🫙 Gourd OBJ 31: Call Beads [0x55] (0x10) | 0x001f |
| 5 | [50,50:52,52] | `$227e&0x08` | 🫙 Gourd OBJ 30: Herbal Essence [0x55] (0x08) | 0x001e |
| 6 | [57,12:59,14] | `$227e&0x01` | 🫙 Gourd OBJ 27: Honey [0x55] (0x01) | 0x001b |
| 7 | [59,12:5b,14] | `$227e&0x02` | 🫙 Gourd OBJ 28: Ash×2 [0x55] (0x02) | 0x001c |
| 8 | [55,12:57,14] | `$227d&0x80` | 🫙 Gourd OBJ 26: Limestone+1 [0x55] (0x80) | 0x001a |
| 9 | [5b,12:5d,14] | `$227e&0x04` | 🫙 Gourd OBJ 29: Roots [0x55] (0x04) | 0x001d |
| 10 | [53,12:55,14] | `$227d&0x40` | 🫙 Gourd OBJ 25: Vinegar×2 [0x55] (0x40) | 0x0019 |
| 11 | [3d,34:3f,36] | `$227d&0x20` | 🫙 Gourd OBJ 24: Biscuit [0x55] (0x20) | 0x0018 |
| 12 | [33,34:35,36] | `$227d&0x10` | 🫙 Gourd OBJ 23: Petal [0x55] (0x10) | 0x0017 |
| 13 | [20,3b:22,3d] | `$227d&0x04` | 🫙 Gourd OBJ 0x22: Wax+1 [0x55] (0x04) | 0x0022 |
| 14 | [18,3b:1a,3d] | `$227d&0x01` | 🫙 Gourd OBJ 0x21: Pixie Dust [0x55] (0x01) | 0x0021 |
| 15 | [13,21:15,23] | `$227c&0x80` | 🫙 Gourd OBJ 22: Nectar [0x55] (0x80) | 0x0016 |
| 16 | [08,2f:0a,31] | `$227c&0x40` | 🫙 Gourd OBJ 21: Call Beads [0x55] (0x40) | 0x0015 |
| 17 | [08,2c:0a,2e] | `$227c&0x20` | 🫙 Gourd OBJ 20: Wings [0x55] (0x20) | 0x0014 |
| 18 | [08,12:0a,14] | `$227e&0x40` | 🫙 Gourd OBJ 0x23: Dry Ice×2 [0x55] (0x40) | 0x0023 |
| 19 | [5b,31:5d,36] | `$22e2&0x02` | ⚙️ Lotus Bridge switch step 1 (boy, `$235f≥0x12` / SPEAR_1) → OBJ 14 state | — |
| 20 | [46,1f:48,22] | `$22e1&0x80` | ⚙️ Lotus Bridge switch step 2 → OBJ 12 state | — |
| 21 | [57,19:59,1c] | `$22e2&0x01` | ⚙️ Lotus Bridge switch step 3 → OBJ 13 state | — |
| 22 | [6c,23:6e,26] | `$22e2&0x08` | ⚙️ Lotus Bridge switch step 4 → OBJ 16 state | — |
| 23 | [52,43:54,45] | `$22e2&0x04` | ⚙️ Lotus Bridge switch step 5 → OBJ 15 state; **SET `$22e3\|=0x40` (DOG FREED)** | — |
| 24 | [17,47:19,49] | `$227d&0x08` | 🫙 Gourd OBJ 0x2e: Biscuit [0x55] (0x08) | 0x002e |

## NPCs

| NPC | Type | Load Condition | Pos | Notes |
|-----|------|----------------|-----|-------|
| NPC 0x38 flags/state 0x02 | Unknown | Always (enter script) | [0xad,0x15] | Stored at `$283c`; talk scripts 0x187b/0x187e |
| NPC 0x72 | Enemy | Always (spawner) | ~13 positions | Additional spawns pre-Sons |
| NPC 0x39 | Enemy | Always (spawner) | ~12 positions | Additional if Sons defeated |
| NPC 0x74 | Enemy | Always (spawner) | ~12+ positions | |
| NPC 0x3a | ? // TODO: look up ENEMY 0x3a name | Step-on [32,29:37,2a] | [0x4d,0x15] ×2 | Spawned in pairs with scripts 0x1872/0x1875 |
| NPC 0x5a | Lever/prop | B-trigger `$2834&0x01` | [0x3a,0x76] | + B-triggers `$2834&0x20/0x40/0x80` |
| NPC 0x59 | Switch/prop | Step-ons `$2834&0x02–0x10` | Various | 4 switch positions |

## Notes

- **Lotus Bridge switch puzzle**: B-triggers #19–23 require boy + `$235f≥0x12` (WEAPON_INDEX.SPEAR_1 / Horn Spear — a metroidvania-style weapon gate). Must be activated in sequence (each sets a `$22e1`/`$22e2` bit). B-trigger #23 final step sets `$22e3|=0x40` (DOG FREED from 'mids) and also clears `$22e4&0x04`, `$22e5&0x02/0x04`.
- **Enemy group encounter** (NPC 0x3a): step-on [32,29:37,2a] fires once (gates `$22e4&0x01`) unless `$22da&0x40` (Knight Basher owned) already set. // TODO: look up ENEMY 0x3a name — "Sons of Shyness" is unverified.
- **`$22e2&0x40`** (enemy group defeated) is used by the monster spawner but is NOT set in this room's scripts — it must be set by the NPC 0x3a defeat script. // TODO: find where this flag is set.
- **17 gourds + 1 Regenerate chest**: gourds use `$227c&0x20–0x80`, `$227d&0x01–0x80`, `$227e&0x01–0x40`; Regenerate chest uses `$227e&0x20` and requires `$225c&0x80`.
- **`$22ee&0x01`**: special teleport to [0xa9,0x13] — suggests a shortcut or warp from 0x56 that uses this flag.
- **`$23bf=0`** on entry.
