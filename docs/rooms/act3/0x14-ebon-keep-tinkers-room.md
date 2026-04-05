# [0x14] Gothica — Ebon Keep Tinker's Room

| Field | Value |
|-------|-------|
| Room ID | 0x14 |
| Name | Gothica - Ebon Keep Tinker's Room |
| Act | Act 3 — Gothica |
| Data offset | `0xabd086` |
| Enter script | `0x928075` → (address not fully captured) |
| Step-ons | 2 |
| B-triggers | 3 |
| Music | 0x70 |

> ⚠️ **Note**: The enter script header (first entry teleport, NPC load block) was not captured in the script read. Data here is derived from partial enter script, RCALL branches, step-ons, and B-triggers.

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 3 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | Tinker `$2455` (NPC 0x00b0>>1=0x58) |
| Forced dog form | — |
| Music | 0x70 |

---

## Overview

Tinker's workshop, east of the Stained Glass Hallway. Tinker (Professor Tinker) is found here with his rocket/space cannon project. The room tracks build progress via `$2356` (Tinker stage counter).

**Rocket components**: Boy must bring three items to Tinker — **Gauge** (`$2264&0x04`), **Wheel** (`$2264&0x08`), and **Diamond Eyes** (`$2264&0x02`). These are surrendered one by one and tracked by `$22dc` flags. Once all three are given (`$2836==3`) and `$2356==2`, Tinker completes the rocket and transitions to the Fire Pit (0x39).

**First visit RCALL**: Tinker tells boy+dog about the space station he saw through his telescope. The conversation ends with `$22ef|=0x08` and CHANGE MAP → 0x70 (Ivor Tower Exterior Bridges, to show the telescope view).

Three pickup B-triggers give alchemy formulas and a weapon specific to the castle path:
- **West castle path** (no callbeads): Knight Basher weapon; Explosion formula
- **East castle path** (`$225d&0x02`): Atom Smasher weapon; Nitro formula

---

## Enter Script Logic (Partial)

1. `$22eb&0x20` guard: teleport both (position not captured), fade-out
2. Music 0x70 if `$238d == 0x00`
3. Load Tinker `$2455` (NPC at some position)
4. **IF `$2836==3 && $2356==2`** (all parts given, final stage):
   - `$2356 = 0x0003`
   - RCALL 0x9989a4 (Tinker part 5 — Rocket done): Tinker walks to rocket, confirms all 3 parts, operates machinery ("Let's see here. I have to make sure the pieces are all in order..."), Tinker: *"I think we're ready to go!"*; brightness fade → CHANGE MAP 0x39 @ `[0x0138|0x01d8]` (Fire Pit)
5. ELSE: cinematic
6. **IF `$2356==1`** (first-visit telescope RCALL, from partial data):
   - Tinker tells boy+dog about the space station: *"I think I know of this place in space!... I've seen it through my telescope!"*
   - Walks toward telescope; boy+dog follow; brightness fade
   - `$22ef|=0x08`; CHANGE MAP 0x70 @ `[0x0378|0x0138]` (Ivor Tower Exterior, telescope view)

---

## Giving Tinker the Rocket Parts

Happens via RCALL 0x998956 during the stage-5 sequence:

| Item | Carry Flag | Transfer | Tinker Flag |
|------|-----------|----------|-------------|
| Gauge | `$2264&0x04` | Clear `$2264&0x04`; show "Gave away the Gauge" | `$22dc\|=0x10` |
| Wheel | `$2264&0x08` | Clear `$2264&0x08`; show "Gave away the Wheel" | `$22dc\|=0x20` |
| Diamond Eyes | `$2264&0x02` | Clear `$2264&0x02`; show "Gave away the Diamond Eyes" | `$22dc\|=0x40` |

`$2836` = count of parts already given (0–3), calculated as count of `$22dc` bits 0x10/0x20/0x40.

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[47,32:48,35]` | MAP 0x39 @ `[0x0078\|0x01a8]` | East → Ebon Keep Fire Pit (global 0x1d) |
| `[2b,32:2e,35]` | MAP 0x10 @ `[0x0168\|0x00c8]` | West → Stained Glass Hallway (global 0x19) |

---

## B-Trigger Scripts

| Tile | Guard Flag | Item / Formula | Notes |
|------|------------|----------------|-------|
| `[34,2b:38,2c]` | `$225b&0x40` (Slow Burn) | ⚗️ Slow Burn formula (`$225b\|=0x40`); preselects alchemy slot 0x3c | Boy only; "This should come in handy." / "The formula requires one part Iron and one part Brimstone." / "Heavy!" |
| `[33,39:35,3a]` | `$22db&0x01` (Atom Smasher) or `$22da&0x80` (Knight Basher) | ⚔️ If `$225d&0x02` (callbeads): give **Atom Smasher** (`$22db\|=0x01`, weapon ID 0x10); else give **Knight Basher** (`$22da\|=0x80`, weapon ID 0x0e) | Boy only; weapon fanfare |
| `[37,3a:38,3c]` | `$2259&0x10` (Explosion) AND/OR `$225b&0x01` (Nitro) | ⚗️ If Explosion not known: give **Explosion** (`$2259\|=0x10`); else if callbeads AND Nitro not known: give **Nitro** (`$225b\|=0x01`) | Boy only; reads formula book |

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$2356` | — | R/W | 📖 Tinker build stage counter (1=intro, 2=awaiting parts, 3=ready, 4=launched) |
| `$2836` | — | W | ⚙️ Count of rocket parts already given (0–3) |
| `$22dc` | 0x10 | R/W | 💎 Gave away Gauge — set when Gauge item is surrendered |
| `$22dc` | 0x20 | R/W | 💎 Gave away Wheel — set when Wheel is surrendered |
| `$22dc` | 0x40 | R/W | 💎 Gave away Diamond Eyes — set when Diamond Eyes surrendered |
| `$2264` | 0x04 | R/W | 💎 Gauge (carry flag) — cleared on surrender |
| `$2264` | 0x08 | R/W | 💎 Wheel (carry flag) — cleared on surrender |
| `$2264` | 0x02 | R/W | 💎 Diamond Eyes (carry flag) — cleared on surrender |
| `$225d` | 0x02 | R | 📖 Prof. Callbeads (Camellia met) — determines weapon and formula variant |
| `$22ef` | 0x08 | W | 📖 Tinker telescope shown — set before CHANGE MAP 0x70 |
| `$225b` | 0x40 | R/W | ⚗️ Slow Burn formula learned |
| `$225b` | 0x01 | R/W | ⚗️ Nitro formula learned |
| `$2259` | 0x10 | R/W | ⚗️ Explosion formula learned |
| `$22db` | 0x01 | R/W | ⚔️ Atom Smasher obtained |
| `$22da` | 0x80 | R/W | ⚔️ Knight Basher obtained |
| `$2455` | — | W | ⚙️ Tinker NPC pointer |

## Notes

- The three key treasure items (Gauge `$2264&0x04`, Wheel `$2264&0x08`, Diamond Eyes `$2264&0x02`) are surrendered here; each surrender clears the carry flag and sets the corresponding `$22dc` persistence bit.
- Tinker stage `$2356` advances 1→2→3→4; stage 4 means the rocket has launched. `$22ef&0x08` (telescope shown) is set before the CHANGE MAP to 0x70.
- The formula-book B-trigger at `[37,3a:38,3c]` gives Explosion first; if already known, gives Nitro instead (requires Prof. Callbeads met and Nitro not yet known).
