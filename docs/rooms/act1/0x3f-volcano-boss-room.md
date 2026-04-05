# 0x3f — Volcano Boss Room

**ROM:** `0x9ffee3` | **Data:** `0xaabd2c` | **Enter:** `0x928156` → `0x94bd7c`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x16` (boss theme); none if `$2260&0x40` |
| Map bounds | Small sealed chamber |
| NPCs | `0x2c` (Alma, cutscene), `0x2a` (evil twin, cutscene), `0x35` (boss), `0x20` (lava ball) |
| Step-on zones | 1 (exit only; locked until boss defeated) |
| B-triggers | 0 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| South | `0x3e` Side rooms of pipe maze @ `[0x04c0\|0x0080]` | step-on `[0d,27:0f,2a]` | **Only if `$2260&0x40` (Magmar dead)** |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$2260` | `0x20` | 📖 | Magmar fight started (set when NPC `0x2c` is loaded; gates intro cutscene) |
| `$2260` | `0x40` | 📖 | **Magmar dead** (boss killed flag; unlocks exit step-on) |
| `$22eb` | `0x04` | ⚙️ | Running showcase / attract mode (special enter path) |
| `$22eb` | `0x20` | ⚙️ | Animation-skip flag (standard entry guard) |

## NPCs

| NPC ID | Position | Phase | Notes |
|--------|----------|-------|-------|
| `0x2c` | `(0x18, 0x17)` | Cutscene | Alma / "Fire Eyes" (volcano master); loaded if `$2260&0x20` not set; ref `$2840` |
| `0x2a` | `(0x18, 0x21)` | Cutscene | Evil twin "Magmar"; loaded during intro; destroyed at end of cutscene; ref `$2842` |
| `0x20` | `(0x18, 0x1f)` | Cutscene | "Pet rock" visual effect; briefly loaded then destroyed during intro |
| `0x35` | `(0x05, 0x19)` | Fight | Boss damage entity; script `0x181e` ("Magmar damage"); loaded after intro; ref `$2846` |
| `0x20` | `(0x05, 0x19)` | Fight | Lava ball (healing phase visual); ref `$2848` |

Note: NPC `0x20` appears twice — once briefly during the intro cutscene (rock materializes), and again in the fight phase (healing lava ball).

## Enter Script Summary

1. `$22eb&0x20` animation guard; default teleport to `(0x18, 0x36)`; stop music.
2. `$23bf=0`.
3. If `$22eb&0x04` (showcase mode): cinematic walk sequence → call `0x94b4ce` (intro cutscene).
4. Else: call `0x92de75` (common cinematic setup).
5. If NOT `$2260&0x40` (boss alive): play music `0x16` (boss theme).
6. If NOT `$2260&0x20` (fight not started): set `$2260|=0x20`, load NPC `0x2c` at `(0x18, 0x17)` (Alma), run intro cutscene (`0x94b4ce`).
7. After intro: screen shake ramp (`$2854` 1→4, 60-tick intervals each step), load NPC `0x35` at `(0x05, 0x19)` (boss entity, script `0x181e`), load NPC `0x20` (lava ball).
8. **Enter fight loop** (runs until `$2260&0x40`):
   - YIELD each iteration; read counters `$284a`/`$284c`.
   - Every 4 `$284a` increments: call **attack routine** (Magmar intro part [1]) — pick a random landing spot (6 options) from `$249d/$249f` lookup table, animate NPC `0x35` in a parabolic arc, screen shake on impact.
   - Every 20 `$284a` increments: call **healing routine** (Magmar intro part [2]) — NPC `0x35` arcs back to its previous position; NPC `0x20` follows; **`HEAL $2846 FOR 0x32 + ((RAND&5)+1)*11`** (heals 50–105 HP); reset `$284a=0`.
   - Counter `$284c` resets to 0 when `>0x50`.
9. When `$2260&0x40` set (boss killed): END.

## Boss Fight: Landing Spot Table

The `$2835 = RAND & 5` determines which of 6 positions the boss arc targets. The Y coordinate (`$249f`) is decremented by 16 before the arc begins (approaches from slightly above landing zone).

| $2835 | $249d (X) | $249f (Y) |
|-------|-----------|-----------|
| 0 | 0x0098 | 0x00f8 |
| 1 | 0x0058 | 0x00d8 |
| 2 | 0x0028 | 0x00c8 |
| 3 | 0x00e8 | 0x00f8 |
| 4 | 0x0128 | 0x00d8 |
| 5 | 0x0158 | 0x00d8 |

## Intro Cutscene (`0x94b4ce`)

Triggered on first entry (`$2260&0x20` not set). Sequence:

1. Stops boy and dog; walks them to `(0x18, 0x2e)` and `(0x19, 0x32)`.
2. Alma (`$2840`) says: **"Hello, Kiddo!"**
3. Player responds: **"Fire Eyes?!"**
4. Loads evil twin NPC `0x2a` (`$2842`) at `(0x18, 0x21)`, plays sound `0x34`.
5. Evil twin says: **"You called?"**
6. Alma says: **"Hi Sis! Hot enough for ya'?"**
7. Evil twin says: **"Who do you think? I'm your evil twin! And I'm here to take over! As hot as it may be inside the volcano, the temperature is dropping outside — 'cause I'm cutting it off at the source!"**
8. Player: **"If the world freezes, my village will die out!"**
9. Evil twin: **"That's the idea! Then my Vipers and I can take control over your world."**
10. Evil twin: **"As much as I'd like to chat, Sister, I've got work to do. So, if you'll forgive me, I'm going to make you go away now!"**
11. Music stops; briefly loads NPC `0x20` (rock) at `(0x18, 0x1f)` with sprite animation (sound `0x64`), then immediately destroys both NPC `0x2a` and NPC `0x20`.
12. Waits 60 ticks; Alma: **"Say Hello to my pet rock!"**
13. Destroys Alma (`$2840`). Restores player control. Plays music `0x24` (post-intro theme).

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x181e` | NPC `0x35` boss combat script ("Magmar damage") |
| `0x94b4ce` | Intro cutscene subroutine (evil twin dialog, shared with 0x3e attract mode) |
| `0x94bb17` | "Magmar intro part [1]" — attack arc subroutine |
| `0x94bc20` | "Magmar intro part [2]" — healing arc subroutine |
| `0x94ba3b` | "Magmar intro part [3]" — landing spot selector |
| `0x94baa9` | "Magmar intro part [4]" — target landing spot selector |

## Notes

- **The boss fight is entirely scripted via the enter script loop** — there are no step-ons or B-triggers. The boss's movement, attacks, and healing all happen in `YIELD`-driven coroutine loops.
- **Healing mechanic:** On every 20th attack cycle, NPC `0x35` (the boss entity) is healed for 50–105 HP via the lava ball routine. This means killing the boss quickly avoids the heal.
- **Music `0x24`** plays during the intro cutscene's end phase (after the evil twin is dispatched but before the boss fight starts with `0x16`).
- **Alma (`0x2c`) role:** She is the volcano's guardian; the evil twin is her sibling. This is the Act 1 story climax.
- **`$22eb&0x04` = showcase / attract mode:** The room includes a special alternate intro path used in the game's attract mode (demo reel). It skips the boss fight loop and plays just the cutscene.
- **No gourds or sniff spots.** This room is purely story + combat.
- **The exit `[0d,27:0f,2a]` is locked until `$2260&0x40` is set.** Entering the zone before killing the boss does nothing.
- **`$2260&0x40`** is the Act 1 completion flag referenced in subsequent rooms. Cross-reference: 0x36 (Both fire pits) and other post-Act-1 rooms likely check this flag.
