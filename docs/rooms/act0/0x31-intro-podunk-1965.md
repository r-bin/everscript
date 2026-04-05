# [0x31] Misc — Intro: Podunk 1965

| Field | Value |
|-------|-------|
| Room ID | 0x31 |
| Name | Intro - Podunk 1965 |
| Act | Misc (intro sequence) |
| Data offset | `0xacd757` |
| Enter script | `0x928110` → `0x92e432` |
| Step-ons | 0 |
| B-triggers | 0 |
| Music | 0x38 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 0 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | 5 anonymous NPC 20 entities (`$2836`, `$2838`, `$283a`, + 2 unnamed) |
| Forced dog form | Regular (0x0A) — set on entry |
| Music | 0x38 |

---

## Overview

The second intro room — a cinematic establishing shot of Podunk in 1965. Displays title cards "Podunk, U.S.A." and "Fall, 1965" over a slowly scrolling street scene with characters. Ends with the text "An experiment is about to conclude_" and transitions to 0x02 (Mansion Exterior 1965).

Three major branching paths on entry:
1. **Outro path** (`$22f1&0x40`): skips the intro entirely — fades out, sets `$22f1|=0x80`, and jumps to 0x46 (Omnitopia / Prof's lab). This is the Act 4 outro return.
2. **Showcase path** (`$22eb&0x04`): calls the Showcase Thraxx routine (`0x92cfe7`).
3. **Start pressed** (`$22eb&0x02`): immediately CHANGE MAP → 0x38 (South Jungle / Start), beginning the actual game.

---

## Enter Logic

1. If `$22f1&0x40` (outro): CALL `0x92de75`; RCALL outro stub → `$22f1|=0x80`; CHANGE MAP `0x46` @ `[0x01f0|0x0128]`
2. If `$22eb&0x04` (showcase): CALL `0x92cfe7` (Showcase Thraxx)
3. If `$22eb&0x02` (start pressed): CHANGE MAP `0x38` @ `[0x0230|0x0448]` (South Jungle / Start)
4. Load 5 NPCs (NPC 20 at various positions) → `$2836`, `$2838`, `$283a` + 2 unnamed
5. `$24ab = 0x0108`, `$24af = 0x00a0`; teleport `$283a` to `[$24ab - 16, $24af]`
6. If `$22ea&0x04` (no previous save found): adjust `$22ea` flags (`&= 0xdf`, `|= 0x08`, `|= 0x10`)
7. WRITE CHANGE DOGGO → Regular (0x0A)
8. `$22fa = 0x0016`; `$22fb = 0x0014` (scroll limits)
9. Teleport both to `[1c, 0f]`; CALL `0x92a3e7` (Hide status bar); PLAY MUSIC 0x38; FADE IN
10. Camera `$242b = 0x0078`, `$242d = 0x0008`; BOY+DOG = STOPPED; SET BRIGHTNESS 0
11. SLEEP 63; CALL `0x92a3d3`; Open message box; SHOW TEXT → **"Podunk, U.S.A."**
12. Brightness ramp-up loop (`$2834` 1→15); SLEEP 183; Fade-out; SLEEP 63
13. SHOW TEXT → **"Fall, 1965"**; brightness ramp again; SLEEP 183; fade; SLEEP 63
14. SHOW TEXT → `[0x87]` (blank); CALL `0x92a3e5` (Intro part); brightness ramp
15. CALL `0x92e401` (Intro part running in BG); SLEEP 103
16. Camera scroll: `$242f = 0x0008`, `$242b = 0x03f0`, `$242d = 0x0008`; SLEEP 279
17. CALL `0x92e3ad`; CALL `0x92e414`; SLEEP 1147
18. Fade; CALL `0x92a3d3`; open box; SHOW TEXT → **"An experiment is about to conclude_"**; VRAM write; SLEEP 119
19. Fade; SLEEP 15; CLEAR TEXT; CHANGE MAP `0x02` @ `[0x0058|0x0358]` (Mansion Exterior 1965)

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
| `$22f1` | 0x40 | R | 📖 Inside outro — triggers immediate warp to 0x46 |
| `$22f1` | 0x80 | W | 📖 Outro phase 2 — set before CHANGE MAP 0x46 |
| `$22eb` | 0x04 | R | ⚙️ Showcase mode — triggers Showcase Thraxx CALL |
| `$22eb` | 0x02 | R | ⚙️ Start pressed in intro — CHANGE MAP 0x38 immediately |
| `$22ea` | 0x04 | R | ⚙️ No previous save found — adjusts `$22ea` flags |
| `$22ea` | 0x08 | R/W | ⚙️ Set/adjusted on entry based on save state |
| `$22ea` | 0x10 | R/W | ⚙️ Set on entry if no save found |
| `$22ea` | 0x20 | W | ⚙️ Cleared on entry (`&= 0xdf`) if no save found |
| `$2443` | — | W | ⚙️ Dog form set to Regular (0x0A) |
| `$22fa` | — | W | ⚙️ Set to 0x0016 (scroll limit) |
| `$22fb` | — | W | ⚙️ Set to 0x0014 (scroll limit) |
| `$2834` | — | W | ⚙️ Brightness ramp counter (0→15, reused three times) |
| `$24ab` | — | W | ⚙️ NPC `$283a` X position |
| `$24af` | — | W | ⚙️ NPC `$283a` Y position |
| `$2836` | — | W | ⚙️ NPC pointer (NPC 20 at `[40,11]`) |
| `$2838` | — | W | ⚙️ NPC pointer (NPC 20 at `[21,14]`) |
| `$283a` | — | W | ⚙️ NPC pointer (NPC 20 at `[21,14]` — animated walk) |

---

## Notes

- The `$22eb&0x02` (start pressed) check immediately jumps to the start of the game (0x38 South Jungle) without playing any cinematic — this is the standard "hold Start on title screen" shortcut.
- The outro path (`$22f1&0x40`) is a cross-act bridge: this room appears in the Act 4 outro chain even though it is an intro room. Setting `$22f1|=0x80` before jumping to 0x46 is the mechanism that tells the lab room which outro phase to play.
- `$2834` is repurposed three times as a brightness ramp counter (each loop 1→15) — not persistent.
- The 5 NPCs are fully session-local (script-arg pointers); none of their positions persist.
