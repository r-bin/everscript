# 0x20 — Gothica: Timberdrake Room in Forest

| Field | Value |
|-------|-------|
| Room ID | 0x20 |
| Act | Gothica (Act 3) |
| Data | `0xace592` |
| Enter script ptr | `0x9280bb` |
| Enter script addr | `0x99cddc` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | MUSIC.BOSS (0x24) alive / MUSIC.WIND_AMBIENT_BIRDS (0x68) dead |
| Dog sprite | Poodle (0x08) |

---

## Overview

Small forest room containing ENEMY::FORESTDRAKE (NPC 0x43 / Timberdrake).
If the Timberdrake is alive (`$22dd&0x04` not set), it is loaded with its AI
script and boss music plays. After defeat `$22dd&0x04` is set; on re-entry the
boss is replaced by OBJ 1 (a persistent marker) and ambient music plays.

One exit leads south to the crossroads (0x13), the other leads east into the
Dark Forest (0x22) with a fade-out transition.

No gourds, no sniff spots, no B-triggers.

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$22dd` | 0x04 | 📖 Timberdrake dead [multi-room] — gates enemy spawn and music |
| `$22eb` | 0x20 | ⚙️ Animation-skip guard (standard pattern) |
| `$238d` | — | 🎵 CHANGE MUSIC register |
| `$23bf` | — | ⚙️ Cleared to 0 on enter |
| `$24f7` | — | ⚙️ Dark-forest entry token — set to 0x0092 when exiting to 0x22 |
| `$2835` | — | ⚙️ Timberdrake entity pointer (session-local) |

---

## Enter Script Summary (`0x99cddc`)

1. Set Poodle dog (`$2443=0x08`).
2. **Animation guard**: if NOT `$22eb&0x20` → teleport both to [0x1b,0x29]; fade-out music.
3. If NOT `$22dd&0x04` (**Timberdrake alive**): load FORESTDRAKE (0x43) at [0x07,0x21],
   set `$2835=entity`, set script "Timberdrake Kill" (0x1a6d); CALL `0x99cec1`
   (Timberdrake AI init).
4. Else (**Timberdrake dead**): OBJ 1 → state 0x7e.
5. Music: if alive → MUSIC.BOSS (0x24); else → MUSIC.WIND_AMBIENT_BIRDS (0x68).
6. `$23bf=0`; CALL `0x92de75`; CALL `0x99d39c` (unknown — Timberdrake room init).

---

## Step-on Scripts (2 entries)

| # | Tile | Description |
|---|------|-------------|
| 1 | [18,08:1a,0d] | **Exit south → 0x13** Crossroads |
| 2 | [0c,16:13,18] | **Exit east → 0x22** Dark Forest; writes `$24f7=0x0092`; fade-out |

---

## NPCs

| NPC ID | Spawn condition | Notes |
|--------|-----------------|-------|
| ENEMY::FORESTDRAKE (0x43) | NOT `$22dd&0x04` | Timberdrake; script "Timberdrake Kill" sets `$22dd\|=0x04` on defeat |

---

## Notes

- `$22dd&0x04` ("Timberdrake dead") is a shared SRAM flag checked across all Act 3 forest rooms.
- The exit to 0x22 sets `$24f7=0x0092` (cell ID 146 in the Dark Forest maze), placing
  the player at a specific position in the forest on arrival.
- `0x99cec1` is the Timberdrake AI routine; its full logic is not read in this session.
- `0x99d39c` is called after the main setup; purpose unknown. `// TODO: read 0x99d39c`.
