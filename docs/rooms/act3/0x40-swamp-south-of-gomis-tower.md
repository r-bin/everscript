# 0x40 — Gothica: Swamp South of Gomi's Tower

| Field | Value |
|-------|-------|
| Room ID | 0x40 |
| Act | Gothica (Act 3) |
| Data | `0xab8000` |
| Enter script ptr | `0x92815b` |
| Enter script addr | `0x999374` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | MUSIC.WIND_AMBIENT_BIRDS (0x68) |
| Dog sprite | — (not forced) |

---

## Overview

Open swamp area connecting Gomi's Tower (0x37) to the north and the crossroads
room (0x13) to the south. Enemies: SLIME (NPC 0x71) × 5 spawners and
ENEMY::MOSQUITO (0x0f) × 2 loaded at fixed positions.

Contains an outro sequence (if `$22f1&0x40` / "Inside outro"): a cutscene
loads four MOSQUITO NPCs, plays an animated flight sequence, triggers screen
shake, and transitions to 0x4a (Omnitopia Final Boss Room) via CHANGE MAP.

No gourds, no sniff spots, no B-triggers.

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$22eb` | 0x20 | ⚙️ Animation-skip guard (standard pattern) |
| `$22eb` | 0x08 | ⚙️ Debug flag — if set on enter: forces `$22f1\|=0x40` |
| `$22f1` | 0x40 | 📖 Inside outro flag [0x40] — if set: triggers outro cutscene → map 0x4a |
| `$238d` | — | 🎵 CHANGE MUSIC register |
| `$23bf` | — | ⚙️ Cleared to 0 on enter |
| `$23c1` | — | ⚙️ Written 0x0001 on enter |

---

## Enter Script Summary (`0x999374`)

1. **Animation guard**: if NOT `$22eb&0x20` → teleport both to [0x1b,0x4f]; fade-out music;
   if debug (`$22eb&0x08`) → set `$22f1|=0x40`.
2. Else: clear `$22eb&0x20`.
3. If `$22f1&0x40` (**outro path**): teleport to [0x47,0x19]; CALL `0x92de75`; RCALL
   `0x99924a` (outro cutscene — loads MOSQUITO × 4 at scripted positions, screen
   walks + shaking, play MUSIC.WIND_AMBIENT_PLANE (0x84) + SFX 0x64, fade-out →
   CHANGE MAP 0x4a "Omnitopia - Final Boss Room"); END.
4. **Normal path**: `$23c1=1`, set drops; SLIME (0x71) × 5 spawners;
   MOSQUITO (0x0f) × 2 at [0x05,0x27] and [0x25,0x33]; music WIND_AMBIENT_BIRDS;
   `$23bf=0`; CALL `0x92de75`; END.

---

## Enemy Drop Table

| Slot | Item | Rate |
|------|------|------|
| 1 | 🧪 Honey (0x0802) | 10 |
| 2 | 💰 Currency (0x0001) qty 90 | 3 |
| 3 | 🧪 Pixie Dust (0x0806) | 1 |

---

## Step-on Scripts (2 entries)

| # | Tile | Description |
|---|------|-------------|
| 1 | [06,03:0b,05] | **Exit north → 0x37** Gomi's Tower |
| 2 | [0e,2b:13,2d] | **Exit south → 0x13** Crossroads |

---

## NPCs

| NPC ID | Count | Notes |
|--------|-------|-------|
| ENEMY::SLIME (0x71) | 5 spawners | Standard |
| ENEMY::MOSQUITO (0x0f) | 2 fixed | Loaded at [0x05,0x27] and [0x25,0x33]; also used as cutscene props in outro (×4) |

---

## Notes

- **Outro sequence**: triggered by `$22f1&0x40`. Four MOSQUITO instances are
  loaded via `0x99924a`, animated via `0x92d5bd`, then destroyed; screen
  shakes; CHANGE MAP 0x4a. The debug path (`$22eb&0x08`) force-sets this flag.
- `$22f2&0x01` ("In credits") is checked in 0x37 (Gomi's Tower); it is NOT
  checked in 0x40 itself.
