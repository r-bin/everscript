# 0x22 — Gothica: Dark Forest

| Field | Value |
|-------|-------|
| Room ID | 0x22 |
| Act | Gothica (Act 3) |
| Data | `0xa1c650` |
| Enter script ptr | `0x9280c5` |
| Enter script addr | `0x99c2ca` |
| Step-ons | 17 |
| B-triggers | 9 |
| Music | MUSIC.WIND_AMBIENT_BIRDS (0x68) |
| Dog sprite | Poodle (0x08) |

---

## Overview

The Dark Forest is a **single map room that simulates a grid maze** by reloading
itself with different `$2835` cell-ID values. Each step-on trigger at a room
edge increments or decrements `$2835` by 1 (east/west) or 10 (north/south), then
calls `0x99bc6d` ("Dark forest room change") which re-enters room 0x22 with the
new cell ID encoded in `$24f7`.

A single ENEMY::OWL_BLACK (Greeble, NPC 0x4f) acts as a guide escort NPC,
spawned at a position determined by the entry token (`$24f7`).

Nine physical B-trigger tiles are distributed around the visual map; each
shares the same script (`0x99bb9d`) which checks `$2835` against 12 possible
cell values and fires the corresponding sniff-spot if the player is in a
matching cell.

Enemy drops come from enemies spawned via CHANGE MAP mechanics (enemies
are dynamically related to the cell layout, not persistent spawners in the
enter script).

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$22c8` | 0x02 | 👃 Sniffed Mushroom in Dark Forest — zone #22 [0x22] (MAP REF 0x0016) |
| `$22c8` | 0x04 | 👃 Sniffed Mushroom in Dark Forest — zone #22 [0x22] (MAP REF 0x0016) |
| `$22c8` | 0x10 | 👃 Sniffed Iron in Dark Forest — zone #20 [0x22] (MAP REF 0x0014) |
| `$22c8` | 0x20 | 👃 Sniffed Iron in Dark Forest — zone #20 [0x22] (MAP REF 0x0014) |
| `$22c8` | 0x40 | 👃 Sniffed Feather in Dark Forest — zone #22 [0x22] (MAP REF 0x0016) |
| `$22c8` | 0x80 | 👃 Sniffed Feather in Dark Forest — zone #23 [0x22] (MAP REF 0x0017) |
| `$22c9` | 0x02 | 👃 Sniffed Roots in Dark Forest — zone #22 [0x22] (MAP REF 0x0016) |
| `$22c9` | 0x04 | 👃 Sniffed Roots in Dark Forest — zone #23 [0x22] (MAP REF 0x0017) |
| `$22c9` | 0x10 | 👃 Sniffed Acorns in Dark Forest — zone #23 [0x22] (MAP REF 0x0017) |
| `$22c9` | 0x20 | 👃 Sniffed Ash in Dark Forest — zone #22 [0x22] (MAP REF 0x0016) |
| `$22c9` | 0x40 | 👃 Sniffed Brimstone in Dark Forest — zone #21 [0x22] (MAP REF 0x0015) |
| `$22c9` | 0x80 | 👃 Sniffed Brimstone in Dark Forest — zone #23 [0x22] (MAP REF 0x0017) |
| `$22eb` | 0x20 | ⚙️ Animation-skip guard (standard pattern) |
| `$238d` | — | 🎵 CHANGE MUSIC register |
| `$23bf` | — | ⚙️ Cleared to 0 on enter |
| `$24f7` | — | ⚙️ Entry token / starting cell ID — written by entering rooms and by `0x99bc6d` |
| `$2835` | — | ⚙️ Current cell ID (session-local); also written to `$24f7` when re-entering |
| `$2837` | — | ⚙️ Previous cell ID (session-local) |
| `$2841` | — | ⚙️ Guide Greeble entity pointer (session-local) |

---

## Enter Script Summary (`0x99c2ca`)

1. Set Poodle dog (`$2443=0x08`); set drops.
2. **Animation guard**: if NOT `$22eb&0x20` → teleport both to [0x10,0x27];
   `$2835=0xfffa (-6)`; fade-out music; `arg0=-6`; SKIP to step 5.
3. Else: clear `$22eb&0x20`.
4. **Cell dispatch** based on `$24f7`:
   - `== -6` → `$2835=0xfffa`, `arg0=-6`, load OWL_BLACK (0x4f) flags 0x22 at [0x8f,0x4a]
   - `== 0x77` → `$2835=0x77`, `arg0=0x77`, load OWL_BLACK at [0x09,0x89]
   - `== 0xa9` → `$2835=0xa9`, `arg0=0xa9`, load OWL_BLACK at [0x5f,0x8a]
   - `== 0x92` → `$2835=0x92`, `arg0=-6`, load OWL_BLACK at [0x8f,0x4a]
   - Other: no OWL_BLACK spawn
5. `$2841=last entity`; music WIND_AMBIENT_BIRDS (0x68).
6. If `$2835 < 0x8c`: set short script 0x179a; else: set short script 0x179d.
7. `$23bf=0`; dispatch to sniff-spot sub based on `arg0` (`0x99aa89`, `0x99aa70`,
   or `0x99aaa2`); CALL `0x99c1a9`; END.

---

## Enemy Drop Table

| Slot | Item | Rate |
|------|------|------|
| 1 | 🧪 Nectar (0x0801) | 7 |
| 2 | 💰 Currency (0x0001) qty 100 | 3 |
| 3 | 🌿 Feather (0x020c) | 1 |

---

## Step-on Scripts (17 entries — 4 shared scripts)

All step-ons call `0x99bc6d` ("Dark forest room change") after updating `$2835`.

| Direction | Script | `$2835` change | Example tiles |
|-----------|--------|----------------|---------------|
| South (+10) | `0x99aa89` | `$2837=$2835`, `$2835+=10` | [2c,2b], [0b,10], [21,10], [05,2b], [32,10] |
| North (−10) | `0x99aa57` | `$2837=$2835`, `$2835-=10` | [06,14], [1b,14], [2d,14] |
| East (+1) | `0x99aaa2` | `$2837=$2835`, `$2835+=1` | [1b,09], [38,09], [12,1b], [25,22] |
| West (−1) | `0x99aa70` | `$2837=$2835`, `$2835-=1` | [15,26], [02,08], [1e,0a], [02,1b], [28,22] |

---

## B-trigger Scripts (9 physical tiles, 1 shared script `0x99bb9d`)

All 9 B-trigger tiles share the same script, which checks `$2835` against the
following cell IDs and fires the matching sniff sub:

| Cell (`$2835`) | Sniff flag | Item | MAP REF | NEXT_ADD |
|----------------|------------|------|---------|----------|
| 12 (0x0c) | `$22c8&0x02` | 🌿 Mushroom | 0x0016 | 4 |
| 18 (0x12) | `$22c8&0x10` | 🌿 Iron | 0x0014 | 2 |
| 47 (0x2f) | `$22c9&0x40` | 🌿 Brimstone | 0x0015 | 2 |
| 52 (0x34) | `$22c9&0x02` | 🌿 Roots | 0x0016 | 2 |
| 61 (0x3d) | `$22c8&0x40` | 🌿 Feather | 0x0016 | 2 |
| 75 (0x4b) | `$22c9&0x04` | 🌿 Roots | 0x0017 | 3 |
| 78 (0x4e) | `$22c9&0x80` | 🌿 Brimstone | 0x0017 | 4 |
| 92 (0x5c) | `$22c8&0x04` | 🌿 Mushroom | 0x0016 | 3 |
| 101 (0x65) | `$22c8&0x20` | 🌿 Iron | 0x0014 | 4 |
| 107 (0x6b) | `$22c9&0x20` | 🌿 Ash | 0x0016 | 4 |
| 131 (0x83) | `$22c8&0x80` | 🌿 Feather | 0x0017 | 2 |
| 136 (0x88) | `$22c9&0x10` | 🌿 Acorns | 0x0017 | 5 |

---

## Exits

| Destination | Mechanism |
|-------------|-----------|
| 0x13 Crossroads | Via `0x99bc6d` when `$2835` reaches south boundary |
| 0x20 Timberdrake | Via `0x99bc6d` when `$2835` reaches north boundary |
| 0x1f Doubles | Via `0x99bc6d` when `$2835` reaches west/north-west boundary |

// TODO: read `0x99bc6d` to confirm exact boundary cell values for each exit.

---

## NPCs

| NPC ID | Spawn condition | Notes |
|--------|-----------------|-------|
| ENEMY::OWL_BLACK (0x4f) | On enter (based on `$24f7`) | Guide Greeble; position depends on entry cell |

---

## Notes

- **Cell ID encoding**: The grid is conceptually a 2D space where rows are spaced
  by 10 and columns by 1. Moving south adds 10, moving north subtracts 10. E/W
  moves add/subtract 1.
- **Sniff spots are not persistent OBJs**: the dark forest has no per-sniff OBJ
  unloading on enter. Sniff flags in `$22c8`/`$22c9` prevent duplicate collection
  but the visual spot is always present.
- MAP REF zones: 0x0014 = zone 20, 0x0015 = zone 21, 0x0016 = zone 22,
  0x0017 = zone 23. These zone numbers appear to correspond to the global sniff-spot
  indexing scheme seen in Gomi's Tower ($22d5–$22d7 range).
- Short scripts 0x179a / 0x179d are set conditionally based on cell depth
  (`$2835 < 0x8c`); purpose unknown. `// TODO: read 0x179a and 0x179d`.
