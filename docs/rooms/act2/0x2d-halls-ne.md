# [0x2d] Antiqua — Halls NE

| Field | Value |
|-------|-------|
| Room ID | `0x2d` |
| Name | Halls NE |
| Act | Act 2 — Antiqua |
| Data | `0xa28000` |
| Enter script ptr | `0x9280fc` |
| Enter script addr | `0x97a2b3` |
| Step-ons | 18 entries (13 unique scripts) |
| B-triggers | 5 |
| Music | 0x66 |
| Doggo | Greyhound (0x06) |

## Overview

Northeast wing of the Halls of Colossa. Contains the Fireball formula cutscene (Madronius' Brother NPC `0x32`) — requires Revealer learned (`$225b&0x10`) and Fireball not yet owned (`!$2259&0x20`). A pit-fall trap (OBJ 14, 5 tiles) drops the player within the room. Two bridge toggle mechanisms (OBJ 0/1 and OBJ 4/7). OBJ 5/6 and OBJ 4/7 animate on respective trigger tiles. A Mad Monk NPC spawns if Bronze Spear is NOT owned (`!$22db&0x04`). Four gourds on `$2274` bits 0x04–0x20. Wings loaded here.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | 0x20 | ⚙️ | Enter animation guard — if clear, teleports both to [0x11,0xa1] + fade |
| `$2259` | 0x20 | ⚗️ | FIREBALL owned — gates Fireball cutscene step-on; set by cutscene at `[5b,4f:5e,50]` [0x2d] |
| `$225b` | 0x10 | ⚗️ | REVEALER owned — required to trigger Fireball cutscene [0x2d] |
| `$22db` | 0x04 | ⚔️ | SPEAR_2 (Bronze Spear) owned — if set, Mad Monk NPC skips chase script [0x2d] |
| `$22ee` | 0x01 | ⚙️ | Arrival routing — if set on enter: clear, teleport both to [0xa1,0xb9/0xb5], SET OBJs 2+3 state 1, face south [0x2d] |
| `$2274` | 0x04 | 🫙 | OBJ 13 Wax×3 looted [0x2d] (MAP REF 0x0d) |
| `$2274` | 0x08 | 🫙 | OBJ 12 Ash×5 looted [0x2d] (MAP REF 0x0c) |
| `$2274` | 0x10 | 🫙 | OBJ 10 Brimstone×3 looted [0x2d] (MAP REF 0x0a) |
| `$2274` | 0x20 | 🫙 | OBJ 11 Wax×4 looted [0x2d] (MAP REF 0x0b) |
| `$2834` | 0x01 | ⚙️ | Camera scroll enabled (session) [0x2d] |
| `$2834` | 0x02 | ⚙️ | Bridge B-trigger extended this session; gates retract step-on [0x2d] |
| `$2834` | 0x04 | ⚙️ | Fell to lower section this session [0x2d] |
| `$2834` | 0x08 | ⚙️ | Slingshot switch guard — set on first activation (once/session) [0x2d] |
| `$2834` | 0x10 | ⚙️ | Switch camera pan done this session [0x2d] |

> **Note:** `$2834` flags are session-only. `$22ee&0x01` is also set by 0x29 and cleared in other rooms — multi-room routing flag.

## Enter Script Summary

1. Write `$0ea2+8=0x01`, `$0eac+8=0x1794` (Halls Wings parameter).
2. Set Greyhound.
3. **Entry guard:** if NOT `$22eb&0x20` → teleport both to [0x11,0xa1] + fade-out. Else clear `$22eb&0x20`.
4. **`$22ee&0x01` routing:** if set → clear; teleport boy to [0xa1,0xb9], dog to [0xa1,0xb5]; SET OBJ 2 state 1; SET OBJ 3 state 1; make both face south.
5. **OBJ unloads:** if `$2274&0x04` → unload OBJ 13; if `$2274&0x08` → unload OBJ 12; if `$2274&0x10` → unload OBJ 10; if `$2274&0x20` → unload OBJ 11.
6. Write `$0ea2+0=0x40`, `$0eac+0=0x172b`; set prize rates 10/3/1; prizes 0x0801/0x0001 qty 50/0x0806.
7. `$2433=0x0002`.
8. Spawn NPC 0x76 × 12; NPC 0x71 × 12 positions.
9. Play music 0x66 (if `$238d!=0`); `$23bf=0`.
10. Load NPC 0x5e (Wings) at [0x7a,0x4a]; write `$0ea2+2=0x01`, `$0eac+2=0x198f`.
11. Load NPC 0x28 (Mad Monk) at [0x48,0x80]; if NOT `$22db&0x04` (Bronze Spear) → set kill-script `0x1995` on Mad Monk.
12. CALL cinematic sub `0x92de75`.

## Step-on Scripts

| Tiles | Script | Effect |
|-------|--------|--------|
| `[0e,24:0f,25]` | `0x979dff` | Slingshot switch (boy only, guard `$2834&0x08`): requires weapon type 4 (`$2360==4`), level ≥ 20 (`$235f>=20`); pan camera; if level < 20: dialogue "need heavier spear"; else sets `$2834|=0x08`, shows OBJ 0 state 0x7e, OBJ 1 states 1→9 with SFX 0x2c |
| `[10,24:12,25]` + 4 more (5 total) | `0x97a23f` | Pit-fall — shows OBJ 14; fall loop (until y>0x2d8); sets `$2834|=0x04`; camera scroll; walk to [0x17,0x31]; reset OBJ 14 |
| `[06,4e:07,50]` | `0x979dbf` | Exit west → 0x29 (Halls main room) |
| `[10,23:12,24]` | `0x979ee8` | Bridge retract (guard `$2834&0x02`; clears it): walk non-controlled to position; OBJ 1 state 0; OBJ 0 states 8→0 with SFX 0x2c |
| `[18,09:1a,0b]` | `0x979dc7` | OBJ toggle A: SFX 0x5a; OBJ 5 state 0x7e; OBJ 6 states 1→3 with SFX 0x76 |
| `[2f,14:31,16]` | `0x979de3` | OBJ toggle B: SFX 0x5a; OBJ 4 state 0x7e; OBJ 7 states 1→3 with SFX 0x76 |
| `[3c,24:3e,26]` | `0x979fb8` | Empty END |
| `[15,48:16,49]` | `0x979fc0` | Camera scroll on (guard `!$2834&0x01`): sets `$2834|=0x01`; writes `$240f/$2411=0x80`, `$2413=0x68`, `$2415=0x78` |
| `[16,48:17,49]` | `0x979fdf` | Camera scroll off (guard `$2834&0x01`): clears it; writes `$240f/$2411=0x48`, `$2413=0x68`, `$2415=0x38` |
| `[5c,49:5e,4a]` | `0x97a023` | SET OBJ 3 state 1 |
| `[5f,49:62,4a]` | `0x97a01f` | SET OBJ 3 state 0 |
| `[5b,4f:5e,50]` | `0x97a027` | **Fireball cutscene** (once; requires `$225b&0x10` AND `!$2259&0x20` AND boy): sets `$2259|=0x20`; loads NPC 0x32 (Madronius' Brother) at [0xad,0xa7] → `$2835`; walks characters into position; multi-line dialogue; awards Fireball formula (preselect 0x1a + alchemy screen); saves |
| `[66,41:67,42]` | `0x97a00f` | OBJ 2 state 1; teleport `$2835` to [0xa7,0xb9] if Fireball owned |
| `[51,51:52,52]` | `0x979fff` | OBJ 2 state 0; teleport `$2835` to [0xa7,0xb9] if Fireball owned |

### Pit-fall tile list
`[10,24:12,25]`, `[3e,26:3f,2c]`, `[3b,26:3c,2c]`, `[12,25:13,2d]`, `[0f,26:10,2d]`

## Exits

| Destination | Tiles | Condition |
|-------------|-------|-----------|
| 0x29 — Halls main room | `[06,4e:07,50]` | always |

## B-Triggers

| OBJ | Tiles | Flag | Item | Notes |
|-----|-------|------|------|-------|
| OBJ 10 | `[5d,46:5f,48]` | `$2274&0x10` | Brimstone×3 | MAP REF `0x000a` |
| OBJ 11 | `[5f,46:61,48]` | `$2274&0x20` | Wax×4 | MAP REF `0x000b` |
| OBJ 12 | `[17,1f:19,21]` | `$2274&0x08` | Ash×5 | MAP REF `0x000c` |
| OBJ 13 | `[0d,07:0f,09]` | `$2274&0x04` | Wax×3 | MAP REF `0x000d` |
| OBJ 0/1 | `[0e,2d:0f,2f]` | `$2834&0x02` (session) | — | Bridge extend: OBJ 0 state 0x7e; OBJ 1 states 1→9 with SFX 0x2c; sets `$2834|=0x02` — no persistence |

## NPCs

| NPC | Count | Positions | Entity | Notes |
|-----|-------|-----------|--------|-------|
| 0x76 | 12 | Scattered | — | Doors/pillars |
| 0x71 | 12 | Scattered | — | Enemies |
| 0x5e | 1 | [0x7a,0x4a] | — | Wings |
| 0x28 | 1 | [0x48,0x80] | — | Mad Monk; gets kill-script `0x1995` if Bronze Spear not owned |
| 0x32 | 1 | [0xad,0xa7] | `$2835` | Madronius' Brother — loaded only during Fireball cutscene |

## Notes

- **Fireball cutscene** requires Revealer (`$225b&0x10`) to unlock but NOT Fireball (`$2259&0x20`) already owned. After cutscene, `$2259|=0x20` is set permanently.
- The Mad Monk (`0x28`) at [0x48,0x80] spawns with a kill-script (`0x1995`) only if Bronze Spear is not owned. Once Bronze Spear is acquired, it spawns passively.
- `$22db&0x04` (Bronze Spear) gates the Mad Monk behavior, not his spawn. The disasm note reads "Bronze Spear" directly.
- `$22ee&0x01` on enter here replicates the same routing mechanic used in 0x29 — arrival from a specific origin forces position to [0xa1,0xb9/0xb5] with OBJs 2+3 raised.
- Music here is 0x66 (unique to NE wing) rather than the standard Halls 0x1e.
