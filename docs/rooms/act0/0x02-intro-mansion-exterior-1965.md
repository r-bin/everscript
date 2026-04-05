# [0x02] Misc — Intro: Mansion Exterior 1965

| Field | Value |
|-------|-------|
| Room ID | 0x02 |
| Name | Intro - Mansion Exterior 1965 |
| Act | Misc (intro sequence) |
| Data offset | `0xacc12d` |
| Enter script | `0x928025` → `0x92e59f` |
| Step-ons | 0 |
| B-triggers | 0 |
| Music | 0x38 (inherited) → 0x52 (explosion) |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 0 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | 1 anonymous NPC 20 (Horace/Prof. character outside mansion) |
| Forced dog form | — |
| Music | Inherited from 0x31 (0x38), switches to 0x52 at explosion |

---

## Overview

The exterior of the Highwater mansion in 1965 — the scene of Horace Highwater's botched experiment. Horace's character (NPC 20) stands outside delivering his opening monologue about the experiment before something goes wrong. Music shifts to 0x52 as the "explosion" sound effects play.

The room then displays the title card "Thirty years later..." and transitions to 0x32 (Podunk 1995). There is no branching in this room — it is a linear cinematic from start to finish.

---

## Enter Logic

1. Teleport both to `[0b, 6b]`
2. Load NPC 20 at `[1e, 5f]` with sprite `0x018c` (Horace/Prof character)
3. Camera scroll: `$242b = 0x0040`, `$242d = 0x02a0`; `$242f = 0x0008`; VRAM write
4. Wait for camera scroll to settle; camera: `$242b = 0x00a0`, `$242d = 0x02a0`; SLEEP 129
5. Wait; camera: `$242b = 0x00a0`, `$242d = 0x0040`; SLEEP 1019
6. PLAY SFX `0x60`; wait; SLEEP 179; PLAY SFX `0x60`
7. Open message box; SHOW TEXT → **"[Horace:] My friends, prepare to be a part of history!"**
8. PLAY SFX `0x60`; SHOW TEXT pause; SHOW TEXT → **"With a twist of a knob here... and a flip of a switch there..."**
9. PLAY SFX `0x60`; SHOW TEXT → **"Wait a minute... that's not right."**
10. PLAY SFX `0x34`; SLEEP 44; PLAY SFX `0xaa`; CLEAR TEXT; SLEEP 59
11. FADE OUT / stop music; SLEEP 15; PLAY MUSIC `0x52`; PLAY SFX `0x64`
12. `$22eb |= 0x01`
13. CALL `0x92d7e1` (explosion/flash effect); SLEEP 104
14. Brightness ramp-down loop (`arg0` 15→0); `$22eb &= 0xfe`
15. CALL `0x92d81c`; FADE OUT / stop music; SLEEP 15
16. CALL `0x92a3d3`; open box; SHOW TEXT → **"Thirty years later..."**
17. VRAM write; SLEEP 119; Fade-out; SLEEP 31; CLEAR TEXT; Fade-out; SLEEP 14
18. CHANGE MAP `0x32` @ `[0x0010|0x0000]` (Podunk 1995)

---

## Step-On Scripts

None.

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x01 | R/W | ⚙️ Set just before explosion effect; cleared after ramp-down |
| `$242b` | — | W | ⚙️ Camera scroll X target |
| `$242d` | — | W | ⚙️ Camera scroll Y target |
| `$242f` | — | W | ⚙️ Camera scroll speed |

---

## Notes

- The simplest intro room — fully linear, no branching, no persistent state changes.
- Music transition: inherited 0x38 (Podunk theme) plays through the monologue, then FADE OUT → 0x52 (intro/explosion music) starts as the experiment fails.
- `$22eb&0x01` is a transient flag set during the explosion flash effect (`0x92d7e1`) and cleared immediately after the brightness ramp. Not persistent.
- The "Thirty years later..." title card is the only text that persists on-screen beyond a clear; it is explicitly CLEAR TEXT'd and then faded before the CHANGE MAP.
- The NPC 20 character here uses sprite `0x018c`, the same sprite ID used for a character in 0x31 — consistent with it being Horace's appearance across both intro rooms.
