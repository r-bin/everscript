# 0x3d — Pipe Maze

**ROM:** `0x9ffedc` | **Data:** `0xa39eb3` | **Enter:** `0x92814a` → `0x949996`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x86` |
| Map bounds | Large outdoor pipe maze |
| NPCs | 8× `0x1e` |
| Step-on zones | 39 (18 gate toggles + 21 pipe exits to 0x3e) |
| B-triggers | 0 |

## Connections

All exits lead to **0x3e Side rooms of pipe maze**. The `$24c3` value written before warping selects which sub-room of 0x3e the player enters.

### Pipe Gate Toggles (18 step-ons)

These step-ons do NOT change maps — they toggle the open/closed state of pipe gates (objects 0–8).

| Object | Close zone (state 0) | Open zone (state 1) |
|--------|----------------------|---------------------|
| OBJ 0 | `[1a,29:1b,2a]` | `[16,2d:17,2e]` |
| OBJ 1 | `[20,29:21,2a]` | `[1d,2d:1e,2e]` |
| OBJ 2 | `[2c,26:2d,27]` | `[29,2a:2a,2b]` |
| OBJ 3 | `[1d,3c:1e,3d]` | `[20,3f:21,40]` |
| OBJ 4 | `[2d,3c:2e,3d]` | `[30,39:31,3a]` |
| OBJ 5 | `[34,3c:35,3d]` | `[37,3f:38,40]` |
| OBJ 6 | `[55,30:56,31]` | `[52,34:53,35]` |
| OBJ 7 | `[55,41:56,42]` | `[51,45:52,46]` |
| OBJ 8 | `[30,22:31,23]` | `[34,26:35,27]` |

### Pipe Exits to 0x3e (21 step-ons)

`$24c3` = sub-room selector written before warping to 0x3e. `$24b3`, `$24b5`, `$24b7` control spawn position/orientation in 0x3e.

| Zone | $24c3 | $24b3 | $24b5 | $24b7 | Spawn in 0x3e |
|------|-------|-------|-------|-------|---------------|
| `[1d,35:1e,36]` | 0x0001 | 0x0002 | 0x0022 | 0x0016 | `[0x0378\|0x00d8]` |
| `[20,32:21,33]` | 0x0001 | 0x0002 | 0x002d | 0x0000 | `[0x0378\|0x00d8]` |
| `[23,35:24,36]` | 0x0001 | 0x0002 | 0x0022 | 0xffea | `[0x0378\|0x00d8]` |
| `[20,38:21,39]` | 0x0001 | 0x002a | 0x0023 | 0x0000 | `[0x0378\|0x00d8]` |
| `[29,1b:2a,1c]` | 0x0002 | 0x0002 | 0x002d | 0x0000 | `[0x0378\|0x00d8]` |
| `[2c,1e:2d,1f]` | 0x0002 | 0x0002 | 0x0022 | 0xffea | `[0x0378\|0x00d8]` |
| `[29,21:2a,22]` | 0x0002 | 0x002a | 0x0023 | 0x0000 | `[0x0378\|0x00d8]` |
| `[37,1b:38,1c]` | 0x0003 | 0x0002 | 0x002d | 0x0000 | `[0x0378\|0x00d8]` |
| `[34,1e:35,1f]` | 0x0003 | 0x0002 | 0x001a | 0x0016 | `[0x0378\|0x00d8]` |
| `[2d,4e:2e,4f]` | 0x0004 | 0x0002 | 0x0022 | 0x0016 | `[0x0378\|0x00d8]` |
| `[30,4b:31,4c]` | 0x0004 | 0x0002 | 0x002d | 0x0000 | `[0x0378\|0x00d8]` |
| `[33,4e:34,4f]` | 0x0004 | 0x0002 | 0x0022 | 0xffea | `[0x0378\|0x00d8]` |
| `[3a,3c:3b,3d]` | — | 0x0002 | 0x0022 | 0x0010 | `[0x05f8\|0x0118]` |
| `[43,39:44,3a]` | — | 0x0002 | 0x002d | 0x0000 | `[0x0438\|0x00f8]` |
| `[43,3f:44,40]` | — | 0x002a | 0x0023 | 0x0000 | `[0x0438\|0x00f8]` |
| `[4c,26:4d,27]` | 0x0007 | 0x002a | 0x0023 | 0x0000 | `[0x0378\|0x00d8]` |
| `[58,1c:59,1d]` | 0x0008 | 0x0002 | 0x002d | 0x0000 | `[0x0378\|0x00d8]` |
| `[60,34:61,35]` | 0x0009 | 0x0002 | 0x0022 | 0x0016 | `[0x0378\|0x00d8]` |
| `[63,31:64,32]` | 0x0009 | 0x0002 | 0x002d | 0x0000 | `[0x0378\|0x00d8]` |
| `[55,4c:56,4d]` | 0x000a | 0x0002 | 0x002d | 0x0000 | `[0x0378\|0x00d8]` |
| `[58,4e:59,4f]` | 0x000a | 0x0002 | 0x0022 | 0xffea | `[0x0378\|0x00d8]` |

**Notes on `$24c3`:** Sub-room IDs 5 and 6 have no exits from 0x3d; they are entered only from within 0x3e. Three exits do not set `$24c3` at all — these use alternate spawn coords in 0x3e.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | `0x20` | ⚙️ | Animation-skip flag (standard entry guard) |

## NPCs

| NPC ID | Count | Positions | State | Notes |
|--------|-------|-----------|-------|-------|
| `0x1e` | 8 | `(1b,31)`, `(4f,2d)`, `(83,25)`, `(91,35)`, `(99,69)`, `(71,77)`, `(35,89)`, `(15,7d)` | `8400` | Enemies scattered across maze |

## Enter Script Summary

1. Standard `$22eb&0x20` animation guard; teleport both to `(0x67, 0x89)`.
2. Set engine hook `$0eac+8=0x178b`.
3. Write `$2433=0x000a`.
4. Load 8× NPC `0x1e` (enemies) at fixed positions.
5. Play music `0x86`.

## Notes

- **Pipe maze puzzle:** Objects 0–8 represent 9 pipe gates (rotating valves or sliding doors). Each has two step-on zones: one closes it (state 0), one opens it (state 1). The correct gate configuration routes the player to a specific pipe exit and thus to a specific sub-room of 0x3e.
- **`$24c3` routing:** Step-ons in 0x3d write `$24c3` = 1–10 (0x1–0xa) to identify which puzzle room the player enters in 0x3e. The 0x3e enter script is a long chain of `if ($24c3 == N)` branches that configure the object layout for that sub-room. Sub-rooms 5 and 6 are entered only from within 0x3e itself.
- **No loot here.** All gourds and sniff spots for this section of the game are inside 0x3e (side rooms).
- **`$24b3/$24b5/$24b7`** are spawn coordinate components written before each map change. `$24b3=0x002a` vs `0x0002` appears to select the pipe opening direction; `$24b5` and `$24b7` are X/Y offsets within 0x3e's map.
- **Music `0x86`** is confirmed as the pipe maze theme, also used in 0x3e.
- **`$2433=0x000a`** — purpose unknown; possibly a counter or sub-system parameter. TODO: cross-reference other rooms that write `$2433`.
- **NPC `0x1e`** has state `0x8400` (vs `0x8000` or standard values seen elsewhere). The high nibble `8` indicates the NPC is enabled; `400` may be a specific behavior flag. These 8 enemies are scattered across the full maze area.
