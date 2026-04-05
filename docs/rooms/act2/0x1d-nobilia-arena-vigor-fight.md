# 0x1d — Nobilia, Arena (Vigor Fight)

| Field | Value |
|-------|-------|
| Room ID | `0x1d` |
| ROM header | `0x9ffe5b` |
| Data ptr | `0xa7f396` |
| Enter script | `0x9280ac` → `0x99ed10` |
| Step-on table | `0xa7f3a5`, len=`0x0000` (no entries) |
| B-trigger table | `0xa7f3a7`, len=`0x0000` (no entries) |
| Music | `0x54` (fanfare/intro), then `0x7e` (boss theme) |
| Act | act2 |

---

## Overview

The Nobilia Arena, where the boy fights Vigor the Indestructible in a scripted boss encounter. There are no step-ons or B-triggers — the entire room is a single enter script that runs the fight cutscene, AI loop, and post-fight outcome.

Pompolonius (`$244d`) announces the fight from the stands. Vigor (`$2835`, NPC `0x3d`) enters from the north and fights the boy using a randomised AI pattern loop. When Vigor is defeated (`$2834&0x02` set by the engine), a post-fight cutscene script at `0x99e417` handles the outcome (not read here).

---

## Memory Access

| Address | Bits | Name | R/W | Meaning |
|---------|------|------|-----|---------|
| `$22eb` | `0x20` | IN_ANIMATION | R | Standard enter guard |
| `$238d` | all | CHANGE_MUSIC | W | Standard music register; set to `0x54` then `0x7e` |
| `$23bf` | all | PACIFIED | W | Set to `0x0000` on enter (enemies active) |
| `$2261` | `0x01` | DOG_UNAVAILABLE | W | Set on enter; dog is locked out for the fight |
| `$2360` | all | CURRENT_WEAPON_TYPE | R | Used by announcer intro: `0x02`=claw, `0x00`=femur, `0x04`=stick |
| `$23e9` | all | CAMERA_BOUNDARY_X_START | W | `0x0000` — fight area camera constraint |
| `$23eb` | all | CAMERA_BOUNDARY_Y_START | W | `0x0180` — fight area camera constraint |
| `$23ed` | all | CAMERA_BOUNDARY_X_END | W | `0x0200` — fight area camera constraint |
| `$23ef` | all | CAMERA_BOUNDARY_Y_END | W | `0x0380` — fight area camera constraint |
| `$2443` | all | CHANGE_DOGGO | W | Set to `0x06` (Greyhound) on enter |
| `$2834` | `0x01` | Vigor facing flag | W | Session-local; set during walk-attack phase |
| `$2834` | `0x02` | Vigor dead | R | Set by engine when Vigor's HP reaches 0; triggers end of fight loop |
| `$2834` | `0x04` | Vigor applause pending | W | Session-local; set/cleared during crowd-animation sub |
| `$2835` | all | ENTITY_1 / Vigor ref | W | Entity pointer for Vigor (session-local) |
| `$244d` | all | Pompolonius entity ref | W | Entity pointer for Pompolonius announcer (session-local) |
| `$2845` | all | Vigor attack pattern | W | Session-local; `RANDRANGE(0,<4)` — selects attack variant |
| `$2847` | all | Vigor animation timer | W | Session-local; animation step counter |
| `$2849` | all | RNG2849 | W | Session-local; random throwable selector for Vigor projectile |
| `$284b` | all | Vigor state | W | Session-local; `0=idle`, `1=attacking`, `2=walking`, `3=flinch` |
| `$284d` | all | Fight loop counter | W | Session-local; incremented each attack cycle |

---

## Enter Script Summary

1. Set up dog: `CHANGE_DOGGO = 0x06` (Greyhound), init movement speeds (`$241f=3`, `$22fa=0x10`, `$22fb=0x08`)
2. Teleport both to `(20,07)` (arena entrance)
3. Fade out → play music `0x54` (fanfare) → fade in
4. `$2261|=0x01` (Dog unavailable), hide status bar, `$23bf=0x0000`
5. Load Pompolonius (`$244d`, NPC `0x31`) at `(20,42)`; script-controlled
6. Spawn Vigor (`$2835`, NPC `0x3d`) at arena south
7. Brightness fade-in loop (`$2837` 0→16)
8. **Announcer intro** (RCALL `0x99dc6c`):
   - *"Ladies and Gentlemen."*
   - *"You paid for an entire seat, but you're only going to need the edge."*
   - *"This is the main event!"*
   - *"Entering the Colosseum…"*
   - *"The King of Chaos…"*
   - *"The Babylonian Bruiser…"*
   - *"The Pulverizing Prince of Pandemonium…"*
   - *"Vigor the Indestructible!"*
9. Music changes: `0x54` → `0x7e` (boss theme)
10. Vigor entrance walk animation (slides in from north)
11. Boy teleported to arena at `(6a,22)`, walks south to fight position `(22,5e)`
12. **Announcer mocks challenger** (based on `$2360`):
    - `0x02`: *"Some loser with a claw!"*
    - `0x00`: *"Some loser with a femur!"*
    - `0x04`: *"Some loser with a stick!"*
13. **Boy monologue:**
    - *"Well, it's good to know that the crowd is on my side. This is like the big fight scene in 'Dirt, Swords, Sweat and Togas.'"*
    - *"I think the hero got pummeled in that picture."*
    - *"Oh, well. Here goes nothing!"*
14. Both walk to fight positions; camera boundaries set to `(0,0x180)–(0x200,0x380)`
15. Announcer: *"Let the battle begin!"*
16. BOY = Player-controlled; sleep 59 ticks
17. END → RCALL `0x99ebe2` (Vigor enter part 2 / fight AI loop)

### Fight AI Loop

The fight AI runs as a repeating routine keyed off `$2834` bits:

- **Phase 1:** Vigor does a slow walk-approach; 30 sub-steps with `$2834&0x01` set
- **Phase 2:** Random attack (`$2845 = RANDRANGE(0,<4)`), selects one of 3 patterns via `0x99ea06` (Vigor script pt 4) + `0x99e9dc` (pt 5):
  - `$2845==0`: Vigor strafes / repositions; 8 sub-steps
  - `$2845==1`: 3-projectile throw arc (REVEAL ENTITY × 3 with staggered offsets)
  - `$2845==2`: Single animation-lunge
  - `$2845==3`: Face-boy + conditional throw
- Loop repeats; if `$2834&0x02` becomes set (Vigor dead), skip to post-fight
- Post-fight: CALL `0x1a76` → `0x99e417` (post-fight cutscene; not read here)

---

## Exits

None. The room has no step-on exits — the player is returned to [0x1e] by the post-fight script at `0x99e417`.

---

## B-Triggers

None.

---

## NPCs

| Entity ref | Type | Pos | Notes |
|------------|------|-----|-------|
| `$244d` | `0x31` Pompolonius | `(20,42)` | Announcer; script-controlled; despawned after fight |
| `$2835` | `0x3d` Vigor | south arena | Spawned at `($24ab,$24af)` (calculated); fight AI entity |

---

## Notes

- **Boss-only room:** No gourds, no chests, no step-ons, no B-triggers. All interaction is scripted.
- **$2834 recycled:** In [0x0a] (Market), `$2834` carries market music + appraiser state. Here it carries Vigor's fight-state flags (`0x01`=facing, `0x02`=dead, `0x04`=applause). These are session-local script temporaries — not SRAM flags — so they can be safely reused across rooms.
- **Weapon-based mockery:** The announcer's intro line for the boy is selected by reading `$2360` (CURRENT_WEAPON_TYPE). Three lines cover the bone (femur), claw, and stick/spear classes.
- **Dog excluded for fight:** `$2261|=0x01` (DOG_UNAVAILABLE) is set on enter; the dog entity is not present during the fight. The Greyhound change (`$2443=0x06`) before entering the arena appears to be a cosmetic setup for the dog's wait-outside appearance.
- **Post-fight at `0x99e417`:** This subroutine is not read in this session. It handles reward, flag sets, and the map transition back to [0x1e]. The `$22ee&0x01` flag (used by [0x1e] to skip the Pompolonius intro on re-entry) is presumably set here or in the lead-up to the arena from [0x08].
- **$2845/2847/2849/284b/284d:** All session-local fight temporaries. `$2845` and `$2847` coincidentally share addresses with `RIMSALA_STATUE_RESET_5/6` (from act4 boss scripting) — they are unrelated.
- **Camera constraints:** The fight sets `$23e9–$23ef` (CAMERA_BOUNDARY) to lock the view on the arena floor during Vigor's entrance walk.
