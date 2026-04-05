# [0x12] Gothica — Ebon Keep Sewers

| Field | Value |
|-------|-------|
| Room ID | 0x12 |
| Name | Gothica - Ebon Keep sewers |
| Act | Act 3 — Gothica |
| Data offset | `0xa58000` |
| Enter script | `0x928075` → `0x999032` |
| Step-ons | 2 |
| B-triggers | 13 |
| Music | 0x2a // ? (not in core.evs MUSIC enum; TODO: identify) |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 13 |
| Gourds | 5 |
| Sniff spots | 0 |
| Enemies | SLIME (0x71) × 16 + RAT (0x42) × 17 |
| NPCs | 0 |
| Forced dog form | — |
| Music | 0x2a // ? |

**Drop table**:

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| 1 | 🧪 Honey (0x0802) | 100/50 | 1 |
| 2 | 💰 Currency (0x0001) | 30/50 | 0x4b (75) |
| 3 | 🧪 Call Beads (0x0807) | 2/50 | 1 |

---

## Overview

Large sewer map connecting Ebon Keep dungeon (0x74) and the crossroads room (0x13). Contains 16 SLIME (NPC 0x71) spawners and 17 RAT (NPC 0x42) spawners. The B-triggers consist of 5 gourds (OBJs 9–13) and 8 weapon-gated barriers (OBJs 0–7) that require the boy with Knight Basher equipped (`$235f==14` = WEAPON_INDEX.AXE_3; `$2360==2` = WEAPON_TYPE.AXE). Barriers are not persistent — OBJs 0–7 are not unloaded by the enter script and reset on re-entry.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$2286` | 0x20 | R/W | � Gourd OBJ 9 looted — Acorns×1 [0x12] (MAP REF 0x0009) |
| `$2286` | 0x40 | R/W | 🫙 Gourd OBJ 10 looted — Water×3 [0x12] (MAP REF 0x000a) |
| `$2286` | 0x80 | R/W | 🫙 Gourd OBJ 11 looted — Ethanol×3 [0x12] (MAP REF 0x000b) |
| `$2287` | 0x01 | R/W | 🫙 Gourd OBJ 12 looted — Ash×4 [0x12] |
| `$2287` | 0x02 | R/W | 🫙 Gourd OBJ 13 looted — Pixie Dust×1 [0x12] (MAP REF 0x000d) |
| `$235f` | — | R | ⚙️ CURRENT_WEAPON — value 14 (WEAPON_INDEX.AXE_3 / Knight Basher) gates weapon-gated barrier B-triggers |
| `$2360` | — | R | ⚙️ CURRENT_WEAPON_TYPE — value 2 (WEAPON_TYPE.AXE) gates weapon-gated barrier B-triggers alongside `$235f` |
| `$2433` | — | W | ⚙️ Set to 1 for all enemy spawners |
| `$23bf` | — | W | ⚙️ Cleared to 0 on entry |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard (standard `IN_ANIMATION` pattern) |

---

## Enter Script Summary

1. **Animation guard** (`$22eb&0x20`): if NOT set, teleport both to default spawn + fade-out; else clear flag.
2. **OBJ unloads** (persistence restore):
   - OBJ 9 if `$2286&0x20`; OBJ 10 if `$2286&0x40`; OBJ 11 if `$2286&0x80`
   - OBJ 12 if `$2287&0x01`; OBJ 13 if `$2287&0x02`
3. WRITE `$0ea2 = 0x40`, `$0eac = 0x172b` (hook slot setup).
4. **Drop table**: PRIZE1 = 0x0802 (Honey) rate 100/50; PRIZE2 = 0x0001 (currency×75) rate 30/50; PRIZE3 = 0x0807 (Call Beads) rate 2/50.
5. **Enemy spawners**: SLIME (0x71) ×16; RAT (0x42) ×17; `$2433=1` for all.
6. **Music**: PLAY MUSIC 0x2a; fade-in.
7. `SET OBJ 8 STATE = 1` (unconditional).
8. WRITE `$23bf = 0`.
9. CALL `0x92de75` (cinematic helper).

---

## Step-on Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[3c,05:3e,08]` | **0x74** Ebon Keep and Ivory Tower dungeon + pipe room | @ [0x0290, 0x00d8] |
| `[4b,05:4c,08]` | **0x13** Between Ebon Keep sewers, Dark Forest and Swamp | @ [0x0158, 0x0088] |

---

## Exits

| Tile | Destination |
|------|-------------|
| `[3c,05:3e,08]` | **0x74** Ebon Keep dungeon |
| `[4b,05:4c,08]` | **0x13** Crossroads |

---

## B-Triggers

### Gourds (OBJs 9–13)

| Tile | Flag | Item | Qty | `$2461` (NEXT_ADD) | MAP REF |
|------|------|------|-----|--------------------|---------|
| `[30,35:32,36]` | `$2287&0x01` | 🫏 Ash | ×4 | 0x0004 | — |
| `[32,35:34,36]` | `$2287&0x02` | 🦵 Pixie Dust | ×1 | — | 0x000d |
| `[5a,4b:5c,4c]` | `$2286&0x20` | 🫏 Acorns | ×1 | 0x0001 | 0x0009 |
| `[5c,4b:5e,4c]` | `$2286&0x40` | 🫏 Water | ×3 | 0x0003 | 0x000a |
| `[5e,4b:60,4c]` | `$2286&0x80` | ⚗️ Ethanol | ×3 | 0x0003 | 0x000b |

### 🚪 Weapon-gated barriers (OBJs 0–7)

Boy-only. Requires `$235f==14` (WEAPON_INDEX.AXE_3 / Knight Basher) AND `$2360==2` (WEAPON_TYPE.AXE). No persistence — barriers reset on room re-entry.

Script per trigger: CALL `0x92d5bd` (with target coords + arg=1) → sleep 59 ticks → SET OBJ state=0x7e → CALL `0x92d607`.

| OBJ | Tile | Target coords `($249d,$249f)` |
|-----|------|------------------------------|
| 0 | `[38,2a:3b,2e]` | (0x0398, 0x02c0) |
| 1 | `[38,14:3b,18]` | (0x0398, 0x0160) |
| 2 | `[64,1f:67,23]` | (0x0658, 0x0210) |
| 3 | `[49,30:4c,34]` | (0x04a8, 0x0320) |
| 4 | `[64,3b:67,3f]` | (0x0658, 0x03d0) |
| 5 | `[38,45:3b,49]` | (0x0398, 0x0470) |
| 6 | `[1e,28:21,2c]` | (0x01f8, 0x02a0) |
| 7 | `[0d,32:10,36]` | (0x00e8, 0x0340) |

---

## Enemies

| Sprite ID | ENEMY name | Position (x,y) | Count | Notes |
|-----------|-----------|----------------|-------|-------|
| 0x71 | SLIME ("Blue Goo") | various | 16 | `$2433=1`; sewer enemy |
| 0x42 | RAT | various | 17 | `$2433=1`; sewer enemy |

---

## Notes

- **Weapon-gated barriers**: 8 B-triggers break barriers (OBJs 0–7). Boy-only; requires Knight Basher equipped (`$235f==14` = WEAPON_INDEX.AXE_3; `$2360==2` = WEAPON_TYPE.AXE). No persistence — barriers reset on re-entry. See `docs/patterns.md` — Weapon-Gated Passages.
- **Gourd NEXT_ADD**: `$2461` is written with the item quantity for Ash (0x0004), Acorns (0x0001), Water (0x0003), and Ethanol (0x0003). Pixie Dust has no `$2461` write (qty 1 default).
- **Drop table confirmed**: HONEY = 0x0802; CALL_BEADS = 0x0807; currency = 0x0001.
- **OBJ 8**: state=1 loaded unconditionally on every entry. Type and purpose unclear. // TODO: identify OBJ 8.
- **Music 0x2a**: not found in core.evs MUSIC enum. // TODO: identify.
- **No dog form change**: dog breed carries over from previous room.
- **`$22eb&0x20`** animation-skip guard present; standard pattern (see `docs/patterns.md`).
