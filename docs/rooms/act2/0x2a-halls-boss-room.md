# [0x2a] Antiqua — Halls Boss Room

| Field | Value |
|-------|-------|
| Room ID | 0x2a |
| Name | Antiqua - Halls Boss Room |
| Act | Act 2 — Antiqua |
| Data offset | `0xaa98b5` |
| Enter script | `0x9280ed` → `0x97a7f3` |
| Step-ons | 1 |
| B-triggers | 0 |
| Music | 0x24 (boss theme) |

---

## Overview

Arena room for the Act 2 boss fight: the **Megatuar** (NPC 0x36). The enter script unconditionally spawns and activates the Megatuar AI. On defeat, kill script 0x1998 sets the Diamond Eye Halls flag (`$22d8|=0x80`) and auto-exits to room **0x2b** (Outside of Halls). One south exit tile returns to the Halls main room (0x29) before the fight is concluded.

---

## Memory Access

| Address | Bit | OBJ | Type | Item / Effect |
|---------|-----|-----|------|---------------|
| `$22d8` | 0x80 | — | 📖 | Diamond Eye Halls obtained (Megatuar defeated) — set in kill script 0x1998 |

---

## Enter Script Summary

1. **Greyhound** animation guard (`$22eb&0x20`); teleport to [3f,4d] + fade-out if in animation.
2. **Music** 0x24 (plays if not already playing); fade-in.
3. Write `$23bf = 0`; CALL `0x92de75`.
4. **LOAD NPC 0x36** (Megatuar) at [40, 21].
5. Write `$2834` = entity slot (Megatuar pointer).
6. Set sprite/animation; set kill script: `$2834+0x66 = 0x1998` ("Megataur kill"), `$2834+0x68 = 0x200`.
7. SET OBJ 0 STATE = 0x7e (unload guard/door OBJ).
8. RCALL `0x97a7de` — **Megatuar combat loop**:
   - Wait 239 ticks → check if will die
   - If alive: RCALL `0x97a51c` (teleport AI — moves to random positions in 3×2 grid)
   - Then RCALL `0x97a7c1` (behavior selector):
     - Random wander (AI-controlled walk) → RCALL `0x97a44b` (charge + stomp + spell attack cycle; stomp deals 10 dmg to boy/dog, spell cast at power 0x2d)
     - RCALL `0x97a699` (secondary movement sub — homing glide toward player)
   - Loop while alive

### Megatuar Kill Script (0x1998)

1. Stop boy+dog; `$22eb|=0x01` (cutscene guard).
2. **`$22d8|=0x80`** — Diamond Eye Halls (Megatuar defeated).
3. Spawn death particle at Megatuar position (CALL `0x92df1c` with args x, y, 3).
4. Fade to white; CALL `0x92df70` ("Boss kill part"); **heal boy+dog 999 HP**.
5. Fade from white; play music 0x36; CALL `0x92bf33` ("Hold up weapon" victory pose).
6. Sleep; CALL `0x92d594` **"Megataur/Rimsala/DE reward"** (awards Diamond Eye item).
7. Fade out; play music 0x78; fade in; sleep.
8. CALL room-change prep (`0x21`); **CHANGE MAP = 0x2b** @ [0x0208, 0x0018] ("Antiqua - Outside of Halls").

---

## Step-on Scripts

| # | Tile | Condition | Effect |
|---|------|-----------|--------|
| 1 | `[1d,28:23,2a]` | — | CALL room-change prep (`0x21`); CHANGE MAP **0x29** @ [0x0148, 0x0018] |

---

## Exits

| Tile / Trigger | Destination | Notes |
|----------------|-------------|-------|
| `[1d,28:23,2a]` | **0x29** Halls main room | Pre-boss exit |
| Kill script 0x1998 | **0x2b** Outside of Halls | After Megatuar defeated |

---

## B-Triggers

None.

---

## NPCs

| NPC | Count | Notes |
|-----|-------|-------|
| NPC 0x36 (Megatuar) | 1 | Loaded at [40,21]; kill script 0x1998 |

---

## Notes

- The Megatuar AI uses two movement patterns:
  1. **Teleport-charge** (`0x97a51c`): randomises between 3 positions across two rows (top row y≈0xb0, bottom row y≈0x140); glides to position over ~0x20 frames, attacks
  2. **Homing glide** (`0x97a699`): approaches player position; slides over ~0x20 frames
- Stomp attack damages both boy and dog for 10 HP (dog only if HP > 10, otherwise exact remaining HP)
- Spell cast uses power 0x2d; 3 possible spells targeting boy, dog, or both
- After victory the game auto-exits to 0x2b — there is no voluntary exit to 0x2b
- `$22d8 bit 0x80` is the primary "Act 2 boss beaten" flag and is cross-checked in multiple rooms (e.g. [0x05] Diamond Eyes theft)
