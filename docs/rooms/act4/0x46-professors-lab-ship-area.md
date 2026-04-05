# Room 0x46 — Omnitopia: Professor's Lab and Ship Area

| Field | Value |
|-------|-------|
| **Room ID** | 0x46 |
| **Act** | 4 — Omnitopia |
| **ROM** | `0x9ffeff` |
| **Data** | `0xa6eb36` |
| **Enter script** | `0x928179` → `0x9bdc6c` |
| **Music** | `0x3c` (normal) / SPACE_NOISE `0x30` (`$22ec&0x20`) / `0x8e` (outro) / FANFARE_ITEM `0x78` (weapon receipt) |
| **Step-ons** | 5 entries |
| **B-triggers** | 3 entries |
| **Connections** | 0x48 Metroplex Tunnels (step-on exit east); 0x19 Chessboard (CHANGE MAP at end of lab cutscene) |

---

## Overview

The Professor's lab is both the main hub room of Omnitopia and the site of the game's ending sequences. It contains the WindWalker ship, an armor shop terminal, and the Laser Lance pickup. The room has four distinct operational paths gated by persistent flags:

1. **Credits path** (`$22f2&0x01` set): Carltron cleaning-bot cutscene plays, then credits roll. Room is otherwise inactive.
2. **Outro path** (`$22f1&0x40` set): Two-phase ending sequence. Phase 1 loads lab objects and dog breed-cycling animation, sets `$22f9|=0x10`, then CHANGE MAP → `0x19` (Chessboard). Phase 2 (`$22f1&0x80` set) loads PROFESSOR, CARLTRON, HORACE, FIRE_EYES, QUEEN as the friends-arrive-at-lab sequence before the ship launches.
3. **First-arrival path** (`$22ec&0x20` set): Prof explains Carltron's backstory cutscene. Laser Lance B-trigger redirects to a separate "Intro Bazooka Gourd Opened" subroutine. WindWalker step-on is inactive.
4. **Normal path**: Prof NPC loaded, Laser Lance gourd available, WindWalker launch active, armor shop accessible.

---

## Enter Logic

1. If `$22eb&0x20` (IN_ANIMATION): teleport both to `(0x3e, 0x25)`, fade out.  
   Else: clear `$22eb&0x20`.
2. If music not locked (`$238d ≠ 0`): play music based on flags:
   - `$22ec&0x20` → SPACE_NOISE `0x30`
   - `$22f1&0x40` → `0x8e` (outro music `// ?`)
   - else → `0x3c` (`// ?`)
   - Fade in.
3. If `$2287&0x20` (Laser Lance already taken): SET OBJ 1 STATE = 0x7e (unload gourd).
4. Load PROFESSOR (0x57) NPC at `(0x34, 0x59)` → `$285b`; assign talk script `0x1b72`, sprite `0x0040`.
5. If `$225d&0x02 || $22f1&0x40 || $22f2&0x01`: make NPC script-controlled, face north (skip intro).
6. Branch:
   - If `$22f2&0x01` (credits): RCALL Prof. Lab part [1] → credits sequence → END.
   - If NOT credits: if `$22f1&0x40` (outro): RCALL Prof. Lab part [2] → outro sequence.
   - Else (normal entry): SKIP to 0x9bdd7e.
7. **Normal entry** (0x9bdd7e):
   - If `$22ee&0x01` set: clear it, teleport boy+dog west to `(0x1a, 0x2c–0x2e)`, face west.
   - `$23bf = 0x0001` (PACIFIED).
   - If `$22ec&0x20`: RCALL Prof. Lab part [3] (backstory cutscene, ~600 lines).
   - Else: check `$238f` (TRANSITION_ENTER_DIRECTION); if ≠ 0: RCALL Prof. Lab part [6] (WW landing cinematic, sets CHANGE MAP); else: call `0x92de75` (cinematic init), END.

---

## Cutscene: Credits (`$22f2&0x01`, Prof. Lab Part [1])

1. Teleport both off-screen; camera scroll to `(0x50, 0x240)`.
2. Load CARLTRON (0x5f) at `(0x1a, 0x56)`; animate dusting routine.
3. Slow brightness fade-up (0→15 over 48 ticks).
4. Play `0x5c` (`// ?` music).
5. CARLTRON walks patrol; Prof speaks:
   - **TEXT 22fe:** *"That's a good robot, Carltron. Dust, dust. Clean, clean."*
   - **TEXT 2301:** *"And no more plans for world domination, OK?"*
   - **TEXT 2304:** *"Good."*
6. CARLTRON walks to exit; brightness fades down; CALL `0x92db35/56/5c/66/6b` (world map functions `// ?`); fade out music; CALL Credits (`0x5a`); END.

---

## Cutscene: Outro Phase 1 (`$22f1&0x40`, NOT `$22f1&0x80`, Prof. Lab Part [2])

Complex multi-step lab destruction and escape sequence:
1. SET OBJ 12–25 STATE = 1 (load outro room objects); OBJ 5–7, 23–24 = 1; OBJ 4, 0 = 0x7e.
2. Change dog to Toaster (`$2443 = 0x0C`).
3. Teleport boy to `(0x14, 0x3e)` → `(0x3b, 0x01)` (off-screen staging area); camera scroll to `(0x170, 0x30)`.
4. Load CARLTRON ship entity at `(0x1a, 0x59)` → `$2859`; animate spinning.
5. Bright fade-up; **TEXT 220e** (dog): *"We should get out of here before something goes terribly wrong!"*
6. Dog undergoes breed cycle: Wolf → Greyhound → Poodle → Regular (with TESLA sfx 0x34 between each).
7. `$2834|=0x01`, `$22eb|=0x20`.
8. `$22f9|=0x10` ("Second half of Lab cutscene to be played").
9. CHANGE MAP → `0x19` (Chessboard) @ `(0x0258, 0x0228)`.

---

## Cutscene: Outro Phase 2 (`$22f1&0x80`, Prof. Lab Part [2])

Friends-arrive ending:
1. Change dog to Regular. Camera positioned.
2. PROFESSOR, HORACE (0x45), FIRE_EYES (0x15), QUEEN (0x4c) drop into lab from ship.
3. Extended dialog sequence (TEXTs 21ff–229e); Prof explains Carltron origin story, Carltron's plan, asks for help.
4. Prof leads party to control panel; activates lab machinery (reveals entity sequences with TESLA sfx 0x34).
5. Ends at door / ready for final area.

---

## Cutscene: Backstory (`$22ec&0x20`, Prof. Lab Part [3])

First-arrival dialogue:
1. Dog → Regular; clear `$22da&0x02` (remove Bone Crusher flag); remove all weapons (`GET_WEAPON = 0xFFFF`).
2. Boy set to kill script `0x1b6c`; hide status bar.
3. Dog slides into lab from `(0x61, 0x2d)` → boy walks to control panel area.
4. **TEXT 21ff** (boy): *"Wow!"*; **TEXT 2202**: *"This looks like the PZS Plasma Drive in When Consonants Collide."*
5. Multiple lab object activations (OBJs 8–18, 25, 14, 19–22, 5–7, 23–24).
6. Dog chews wires; Prof scolds: **TEXT 2214/2217**: *"Hey! Don't chew on those wires!"*
7. Prof explains Carltron, robot clones, plan to stop him: TEXTs 2295–229e.
8. **TEXT 22a7** (Prof): *"There's a special item on Evermore that is the key to entering Carltron's chamber. The item is an Energy Core at the base of the chessboard…"*
9. Armor shop terminal activates (OBJ 27); `$22eb|=0x20`; `$22f9|=0x10`; CHANGE MAP → `0x19`.

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | `0x20` | ⚙️ | IN_ANIMATION — entry animation guard |
| `$22ec` | `0x20` | 📖 | First-arrival intro mode active (`// MISMATCH: memory-map says "walk-in monologue spy cutscene [0x1c]"; in 0x46 = first-arrival path guard`) |
| `$22f1` | `0x40` | 📖 | OUTRO active |
| `$22f1` | `0x80` | 📖 | Outro phase 2 (friends-arrive) active |
| `$22f2` | `0x01` | 📖 | Credits mode active |
| `$22f9` | `0x10` | 📖 | Second half of lab cutscene queued (W; set before CHANGE MAP → 0x19) |
| `$22ee` | `0x01` | ⚙️ | Entry teleport guard — cleared on normal entry; if set, teleports boy+dog west |
| `$22eb` | `0x20` | ⚙️ | W — set before CHANGE MAP → 0x19 at end of outro phase 1 |
| `$22da` | `0x02` | ⚔️ | Bone Crusher (SWORD_1) — cleared in backstory cutscene (removes weapon) |
| `$2287` | `0x20` | 💎 | Laser Lance gourd looted [0x46] |
| `$22e5` | `0x08` | ⚙️ | WW Landing flag — set in B-trig 2 before calling WW landing script |
| `$2355` | full | ⚙️ | WINDWALKER_TYPE — written = 0x0002 (OUTRO) in B-trig 2 |
| `$23bf` | full | ⚙️ | PACIFIED — written = 0x0001 on enter |
| `$238f` | full | ⚙️ | TRANSITION_ENTER_DIRECTION — read on enter to select which Prof scene plays |

---

## Objects

| Obj | Type | Persistence Flag | Item / Behavior |
|-----|------|-----------------|----------------|
| 0 | platform | session-local `$2834&0x02` | Lab equipment platform; SET STATE 0x7e on step-on zone `[31,2b/2f]`; no SRAM |
| 1 | 💎 hidden item | `$2287&0x20` | Laser Lance (SPEAR_4 `0x18`) |
| 4 | platform | session-local `$2834&0x04` | Lab equipment station; SET STATE 0x7e on step-on zone `[31,1e/22]`; no SRAM |
| 5–24 | outro props | — | Activated at state 1 during outro / backstory cutscenes only |
| 26 | ship animation | — | Ship hatch / engine effect; state 0x7e = active burst |
| 27 | shop terminal | — | Armor shop robot terminal; activated in B-trig 3 and backstory |

---

## NPCs

| Sprite ID | ENEMY name | Position (x,y) | Talk script | Behavior |
|-----------|-----------|----------------|-------------|---------|
| `0x57` | PROFESSOR | `(0x34, 0x59)` | `0x1b72` | Main NPC; script-controlled if skipping intro |
| `0x5f` | CARLTRON | `(0x1a, 0x56)` (credits only) | none | Credits dusting cutscene |
| `0x45` | HORACE | loaded in outro | none | Drops into lab in Phase 2 outro |
| `0x15` | FIRE_EYES | loaded in outro | none | Drops into lab in Phase 2 outro |
| `0x4c` | QUEEN | loaded in outro | none | Drops into lab in Phase 2 outro |
| `0x20` | PLACEHOLDER | `(0x34, 0x54)` (B-trig 3) | none | Armor shop terminal entity; text "Armor Sales Mode engaged" |

---

## Connections

| Direction | Destination | Condition | Notes |
|-----------|-------------|-----------|-------|
| East (step-on) | [0x48] Metroplex Tunnels @ `[0x0078\|0x0088]` | always | Writes `$24fd = 0x0004` before CHANGE MAP |
| Exit (cutscene) | [0x19] Chessboard @ `(0x0258, 0x0228)` | end of lab intro cutscene | Sets `$22eb\|=0x20`, `$22f9\|=0x10` before CHANGE MAP |

---

## Step-on Zones

| Zone | Script | Condition | Effect |
|------|--------|-----------|--------|
| `[31,1e:33,1f]` | `0x9bc77e` | `!$2834&0x04 && !$22ec&0x20` | SET OBJ 4 STATE = 0x7e; sfx `0xb0`; `$2834\|=0x04` (session) |
| `[31,22:33,23]` | `0x9bc77e` | same | (same script — duplicate zone) |
| `[31,2b:33,2c]` | `0x9bc766` | `!$2834&0x02 && !$22ec&0x20` | SET OBJ 0 STATE = 0x7e; sfx `0xb0`; `$2834\|=0x02` (session) |
| `[31,2f:33,30]` | `0x9bc766` | same | (same script — duplicate zone) |
| `[3e,2e:40,2f]` | `0x9bd066` | always | CHANGE MAP → 0x48 |

---

## B-triggers

| Zone | Object | Persistence Flag | Contents / Effect |
|------|--------|-----------------|-------------------|
| `[34,10:36,12]` | OBJ 1 | `$2287&0x20` | If intro mode (`$22ec&0x20`): CALL 0x9bc497 (Intro Bazooka Gourd Opened `// ?`); else if boy and flag unset: give Laser Lance (SPEAR_4 `0x18`), FANFARE_ITEM `0x78`, set flag |
| `[31,0d:33,0f]` | OBJ 26 | none | If NOT intro mode: WW ship launch animation (`$2355=2`, `$22e5\|=0x08`), CALL 0x92dc34 (WW launch `// ?`); if intro mode: no-op |
| `[2c,2f:2e,30]` | OBJ 27 | none | If boy: load PLACEHOLDER NPC, "Armor Sales Mode engaged" → buy/sell armor (global scripts 0x47/0x49); if dog: "Sales program is unable to engage" |

---

## External Scripts

| Address | Call type | Section | Purpose |
|---------|-----------|---------|---------|
| Global `0x00` | CALL | enter | Fade-out / stop music |
| Global `0x01` | CALL | enter | Fade-in / start music |
| Global `0x5a` | CALL | credits | Credits roll |
| `0x92de75` | CALL | normal enter | Cinematic init — see `docs/patterns.md` |
| `0x92dc34` | CALL | B-trig 2 | WindWalker launch `// ?` |
| `0x9bc497` | CALL | B-trig 1 | Intro Bazooka Gourd Opened `// ?` |
| `0x92db35/56/5c/66/6b` | CALL | credits | Unknown world map functions `// ?` |
| Global `0x2e` | CALL | step-on exit | Unknown pre-CHANGE MAP function `// ?` |
| Global `0x47` | CALL | B-trig 3 | Buy armor |
| Global `0x49` | CALL | B-trig 3 | Sell armor |
| Global `0x52` | CALL | B-trig 3 | Shop menu? `// ?` |
| Global `0x55` | CALL | B-trig 3 | Money exchange |
| Global `0x02` | CALL | B-trig 3 | Open message box |

---

## Notes

- This room is simultaneously the game's most narrative-dense room and its ending hub. Four completely different code paths run depending on story state — credits, outro phase 1, outro phase 2, first arrival, and normal gameplay.
- The Laser Lance (OBJ 1) is the only persistent pickup. `$2287&0x20` is a new bit not yet in the memory map — needs to be added.
- `$22ec&0x20` is flagged as "walk-in monologue spy cutscene [0x1c]" in the memory map (Act 2 origin), but in 0x46 it gates the first-arrival intro path. These may be the same flag repurposed across acts. // MISMATCH: investigate.
- `$22f9&0x10` ("Second half of Lab cutscene to be played") falls inside the gap `$22f6…$22fb` in the memory map. Needs a new row.
- The outro phase 1 dog breed-cycling animation (Wolf → Greyhound → Poodle → Regular) uses `$2834&0x01` as a session-local animation toggle — not SRAM.
- The step-on cargo platform activations (`$2834&0x02/0x04`) are session-local entity working RAM — they reset on every room entry. These are NOT SRAM persistence flags.
- `$24fd` (written = 4 before CHANGE MAP 0x48) is undocumented in core.evs and the memory map. Likely an entry-origin code for the Metroplex destination.
- `0x9bc497` ("Intro Bazooka Gourd Opened") appears to give a Bazooka when the Laser Lance trigger is accessed during the intro. Contents unverified — // TODO: read 0x9bc497 to confirm item given.
- PLACEHOLDER (0x20) is used as the armor shop robot NPC. This is the same sprite used for explosions and WindWalker effects — the specific visual in this context is unconfirmed. // TODO: verify sprite appearance.
- Music ID `0x3c` (normal lab theme) and `0x8e` (outro theme) are not in the core.evs MUSIC enum. // TODO: add to MUSIC enum.
- `0x92dc34` (WindWalker launch) is referenced but unnamed in the dump. This may correspond to the WindWalker world-map transition sequence.
