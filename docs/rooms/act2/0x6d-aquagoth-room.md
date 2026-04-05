# [0x6d] Antiqua — Aquagoth Room

| Field | Value |
|-------|-------|
| Room ID | 0x6d |
| Name | Antique - Aquagoth Room |
| Act | Act 2 — Antiqua |
| Data offset | `0xabb3bc` |
| Enter script | `0x92823c` → `0x97e836` |
| Step-ons | 0 |
| B-triggers | 0 |
| Music | 0x24 (boss) |

---

## Overview

Pure boss room — Aquagoth, the giant water creature. No step-on tiles and no B-triggers: the entire room is the boss fight. The enter script loads all entities (Aquagoth body + 4 tentacles), then the Aquagoth NPC's own tick script runs the fight loop: periodic jellyfish spawns, timed spell attacks, and a kill sequence that transitions the player to Act 3 (Gothica).

Entering from 0x4b (Oglin Cave) at [0x00d8, 0x0288].

---

## Memory Access

| Address | Bit | Type | Effect |
|---------|-----|------|--------|
| `$2834` | 0x01 | ⚙️ | Aquagoth combat-active flag — cleared (to 0) on enter; behavior loop attacks while 0; set to 1 by kill script to stop AI [0x6d] |
| `$22ed` | 0x08 | 📖 | Crustacia intro to be shown — set by Aquagoth kill script before CHANGE MAP 0x6c [0x6d]; consumed in [0x68] |
| `$2317` | full byte | 🧪 | Honey count — incremented +1 by Aquagoth kill script (static reward) [0x6d] |

### Entity slots (local / transient — not persistent)

| Address | Contents |
|---------|----------|
| `$283b` | Aquagoth body entity (NPC 0x3e) |
| `$283d` | Tentacle entity #1 (NPC 0x3f) |
| `$283f` | Tentacle entity #2 (NPC 0x3f) |
| `$2841` | Tentacle entity #3 (NPC 0x3f) |
| `$2843` | Tentacle entity #4 (NPC 0x3f) |
| `$2845` | Hit animation in-progress counter |
| `$2847` | Jellyfish entity slot #1 (NPC 0x40) |
| `$2849` | Jellyfish entity slot #2 (NPC 0x40) |
| `$284b` | Jellyfish entity slot #3 (NPC 0x40) |
| `$284d` | Jellyfish entity slot #4 (NPC 0x40) |
| `$284f` | Jellyfish entity slot #5 (NPC 0x40) |
| `$2853` | Jellyfish wave counter (max 5 per wave per `0x97e150`) |
| `$2855` | Boss combat radius low bound (`$2857 − 16`) |
| `$2857` | Boss combat radius param (0x0b00) |
| `$2859` | Boss combat radius param (0x003d) |
| `$2863` | Escape-Oglin spawned flag (0 or 1) |
| `$2867` | Escape-Oglin entity slot |

---

## Enter Script Summary

1. `$22eb&0x20` animation guard: if set → teleport both to [1a, 43], fade-out, skip to main; else clear bit.
2. If CHANGE MUSIC (`$238d`) != 0: **PLAY MUSIC 0x24** (boss music) + fade-in.
3. **Greyhound**.
4. WRITE `$23bf = 0`.
5. Load 4 tentacles (NPC 0x3f):
   - [12, 32] → `$283d`, teleport relative (−4, +98)
   - [22, 30] → `$283f`, teleport relative (−6, +102)
   - [1a, 33] → `$2841`, teleport relative (+128, +35)
   - [1a, 33] → `$2843`, teleport relative (−69, −48)
6. **`$2834 &= 0xfe`** — clear combat-active bit (start fresh).
7. Load Aquagoth body (NPC 0x3e) at [1a, 33]; teleport relative (+0, +8); `$283b` = entity; assign behavior script id:19b0 ("Aquagoth") with tick rate 0x300.
8. WRITE `$0ea2 = 0x40`, `$0eac = 0x172b`.
9. **Drop table** (jellyfish enemy drops): PRIZE 1 = `0x0801` at 20/50 rate; PRIZE 2/3 = none.
10. Init entity slots: `$2847–$284f = 0`; `$2855 = $2857 − 16`; `$2857 = 0x0b00`; `$2859 = 0x003d`.
11. CALL `0x97e0da`, `0x97e6a0`, `0x97e6c9`, `0x97e7dd` ×4 (combat sub-scripts / tentacle AI init).
12. CALL `0x92de75` (cinematic setup).

---

## Step-on Scripts

None.

---

## Exits

None via step-on tiles. Exit is scripted via the kill sequence:

| Trigger | Destination | Notes |
|---------|-------------|-------|
| Aquagoth kill script (`0x97e25e`) | **0x6c** Gothica — SE of Ivor Tower (Well) | @ [0x00e8, 0x00f8] |

---

## B-Triggers

None.

---

## NPCs

| NPC | Count | Role |
|-----|-------|------|
| 0x3e | 1 | Aquagoth body; behavior script id:19b0 |
| 0x3f | 4 | Aquagoth tentacles |
| 0x40 | 0–5 | Jellyfish (dynamically spawned during fight) |
| 0x20 | 1 | Bucket (spawned post-kill for Act 3 elevator cutscene) |
| 0x6e | 1 | Oglin (spawned briefly during kill animation at [1a, 43]) |

---

## Boss AI Summary (id:19b0 "Aquagoth" at `0x97e25e`)

The Aquagoth entity runs a tick loop:

**Tentacle hit phase** (script bit 0x0100 set — takes damage):
- Increments `$2845` (hit-in-progress guard), plays a visual effect, decrements `$2845`.
- If boss HP < 0x3e8 AND `$2863 == 0` AND RAND chance: spawn escape Oglin NPC 0x6e, start kill sequence.

**Kill sequence** (bit 0x0100 NOT set):
1. Stop players; `$2834 |= 0x01` (stop the behavior tick loop).
2. Destroy Aquagoth body + tentacles + all jellyfish.
3. Explosion/bubble animation loop (120 frames × 2 phases with water spout sub-calls and Aquagoth-part subs `0x97e060`/`0x97e039`).
4. Fade to white (`0x92d752`); `$22eb &= 0xfe`; PLAY MUSIC 0x36.
5. Fully heal boy and dog.
6. Award 5000 Jewels; show reward text.
7. Increment honey count: `$2317 += 1`.
8. Show "Received some Honey" text.
9. Fade-out → PLAY MUSIC 0x60; fade-in.
10. Camera pan; player faces north; "Hey! Kid! Get in the bucket!" dialogue.
11. Spawn NPC 0x20 (bucket) at [1a, 33]; run bucket-rise animation (boy rides up 0x100 pixels).
12. Fade to black; `$22ed |= 0x08` (Crustacia intro flag).
13. **CHANGE MAP = 0x6c** (Gothica — SE of Ivor Tower / Well).

**Idle behavior loop** (at `0x97e951`, while `$2834&0x01 == 0`):
- Every 0x3f–0xbe ticks:
  - Call jellyfish-spawn sub `0x97e150`: spawns 1 NPC 0x40 at random position (8 possible), registers in `$2847–$284f`, increments `$2853`.
  - If timer elapsed (0x012c ticks): pick RAND 0–127:
    - < 2: spell 16 power 0x1a on boy+dog (fountain blast)
    - < 11: spell 12 power 0x34 on boy+dog (whirlpool)
    - else: spell 24 power 0x43 on boy+dog (water jet)
  - Reset timer.

---

## Notes

- **No SRAM "Aquagoth defeated" flag is written** — the kill transition is one-way (Act 3). The game never returns to this room after Aquagoth's death, so no persistence is needed.
- `$22ed&0x08` is set here (labeled "Crustacia intro to be shown") and consumed in room 0x68 (Crustacia) to trigger the intro cutscene.
- `$2317` stores the Honey item count; the kill script gives +1 Honey.
- `$2834&0x01` is a transient combat flag, re-initialized on every room entry.
- The drop `0x0801` is the jellyfish enemy drop — item identity not yet confirmed; // TODO: verify 0x0801 item ID from core.evs.
- This is the final room of Act 2. The bucket ride ends at `0x6c` (Gothica), beginning Act 3.
