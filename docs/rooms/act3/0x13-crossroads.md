# [0x13] Gothica — Between Ebon Keep Sewers, Dark Forest and Swamp

| Field | Value |
|-------|-------|
| Room ID | 0x13 |
| Name | Gothica - Between Ebon Keep sewers, Dark Forest and Swamp |
| Act | Act 3 — Gothica |
| Data offset | `0xacb18d` |
| Enter script | `0x92807a` → `0x999210` |
| Step-ons | 4 |
| B-triggers | 1 |
| Music | 0x68 |

---

## Overview

Small crossroads room connecting the Ebon Keep sewers (0x12), the Swamp (0x40), and the Timberdrake forest room (0x20). Contains a single B-trigger "interaction spot" at the Swamp entrance (OBJ 0), which requires the boy to interact with a specific game-state condition (`$235f=14`, `$2360=2`). Setting `$22dd&0x40` ("Load east castle") before leaving east toward 0x12.

---

## Memory Access

| Address | Bit | OBJ | Type | Effect |
|---------|-----|-----|------|--------|
| `$2272` | 0x40 | 0 | 📖 | OBJ 0 interaction trigger fired [0x13] |
| `$22dd` | 0x40 | — | ⚙️ | Routing flag: "Load east castle" — set before CHANGE MAP 0x12 [0x13] |

---

## Enter Script Summary

1. Animation guard (`$22eb&0x20`): teleport to [21, 0f], fade-out.
2. **Music** 0x68 (if not already playing) + fade-in.
3. OBJ unload: OBJ 0 if `$2272&0x40`.
4. WRITE `$23bf = 0`.
5. CALL `0x92de75`.

---

## Step-on Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[02,14:04,18]` | **0x20** Timberdrake room in forest | CALL 0x19 (west exit) |
| `[09,0b:0f,0c]` | **0x40** Swamp south of Gomi's Tower | CALL 0x26 (north exit) |
| `[09,0a:0f,0b]` | **0x40** Swamp south of Gomi's Tower | same script (adjacent row of swamp entrance) |
| `[15,12:17,13]` | **0x12** Ebon Keep Sewers | Sets `$22dd\|=0x40` ("Load east castle") before CALL 0x20 + CHANGE MAP |

---

## Exits

| Tile | Destination |
|------|-------------|
| `[02,14:04,18]` | **0x20** Timberdrake room |
| `[09,0a:0f,0c]` | **0x40** Swamp (two-tile entrance) |
| `[15,12:17,13]` | **0x12** Ebon Keep Sewers |

---

## B-Triggers

| Tile | Flag | Action |
|------|------|--------|
| `[09,0e:0f,0f]` | `$2272&0x40` | Boy-only; requires `$235f=14` AND `$2360=2`; calls `0x92d5bd` @ (0x0098, 0x0038, arg 2); sleeps 89 ticks; unloads OBJ 0; calls `0x92d607`; then sets `$2272\|=0x40` |

---

## Notes

- The B-trigger at the swamp entrance has the same conditional pattern as 0x12's OBJ 0–7 triggers, but here it correctly sets `$2272&0x40` (unlike 0x12 which leaves OBJs 0–7 without a persistence flag).
- `$22dd&0x40` = "Load east castle" — the disassembler name suggests this flag signals to 0x12 that the player entered from the crossroads direction. Not consumed by 0x12's enter script directly; may be used by sub-scripts or other rooms.
