# [0x29] Antiqua — Halls main room

| Field | Value |
|-------|-------|
| Room ID | `0x29` |
| Name | Halls main room |
| Act | Act 2 — Antiqua |
| Data | `0xa7bb53` |
| Enter script ptr | `0x9280e8` |
| Enter script addr | `0x9794d7` |
| Step-ons | 27 entries (12 unique scripts) |
| B-triggers | 2 |
| Music | 0x1e |
| Doggo | Greyhound (0x06) |

## Overview

The central hub of the Halls of Colossa. Four wings branch off to sub-areas (SW, NW, SE, NE); the north passage leads to the boss room (0x2a). A Spear switch puzzle in the center opens the north boss door (requires WEAPON_TYPE 0x04 / Spear; does NOT check weapon level). A spike-fall trap in the central pit drops the player back to this room with rotating comic landing dialogue. Two gourds sit near the boss door. Wings (NPC 0x5e) is loaded here. Arriving via a spike-fall sets `$22f3&0x80`, which plays the spike-fall landing sequence on entry — this flag is NOT related to Wings.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | 0x20 | ⚙️ | Enter animation guard — if clear on enter, teleports both to south spawn [0x29,0x7b] + fade; else clear flag |
| `$22ee` | 0x01 | ⚙️ | North entrance routing: if set on enter, clear flag, set `$238f=0xf`, teleport both to [0x3f,0x0d] |
| `$22e7` | 0x04 | 📖 | Switch puzzle throw-animation activated (one-time; prevents repeat throw) [0x29] |
| `$22f3` | 0x80 | 📖 | Spike-fall arrival flag: if set on enter, play spike-fall landing sequence (NOT related to Wings) [0x29] |
| `$2283` | 0x08 | 🫙 | OBJ 1 Nectar×1 looted [0x29] (MAP REF 0x01) |
| `$2283` | 0x10 | 🫙 | OBJ 2 Vinegar×1 looted [0x29] (MAP REF 0x02) |
| `$228a` | 0x10 | 📖 | Gate/door opened — OBJs 3+10 revealed (one-time, step-on [10,05:12,07]) [0x29] |
| `$228a` | 0x20 | ? | OBJ 8 state persistence [0x29] |
| `$228a` | 0x40 | ? | OBJ 7 state persistence [0x29] |
| `$228a` | 0x80 | ? | OBJ 9 state persistence [0x29] |
| `$2834` | 0x01 | ⚙️ | Spike trap active — OBJ 5 raised (set after Wings-fall cutscene; cleared by spike-reset tile) [0x29] |
| `$2834` | 0x02 | ⚙️ | Cutscene/camera-pan mode flag (set during `$22f3&0x80` entry, cleared at end) [0x29] |
| `$2834` | 0x04 | 📖 | Switch puzzle succeeded (Spear / WEAPON_TYPE 0x04 equipped; opens boss door) [0x29] |
| `$2839` | word | ⚙️ | Wings-fall dialogue counter — 0: "glad we missed those big spikes"; 1: "experiments with gravity a success"; 2: "stop falling into pits"; 12: 4th-wall "on the other side of the glass"; else: silent increment [0x29] |

> **Note:** `$2834` bits 0x08–0x80 are also manipulated by step-on scripts in the adjacent Halls wing rooms (0x23, 0x2c) for their own spike/gate puzzles. See those rooms' docs for the full `$2834` picture.

## Enter Script Summary

1. Write `$0ea2+8=0x01`, `$0eac+8=0x1794` (Halls Wings parameter).
2. Set Greyhound.
3. **`$22f3&0x80` branch (spike-fall entry):** if set → set `$2834|=0x02`; RCALL camera-adjust sub `0x979195`; skip normal entry block (SKIP 19).
4. **Normal entry guard:** if NOT `$22eb&0x20` → teleport both to [0x29,0x7b] + fade-out. Else clear `$22eb&0x20`.
5. **`$22ee&0x01` guard:** if set → clear flag; write `$238f=0xf`; teleport both to [0x3f,0x0d].
6. Spawn NPC 0x70 × 6 positions (enemies); `$2433=0x0001`.
7. Spawn NPC 0x76 × 2 (at [0x3f,0x0d] and [0x18,0x0d]).
8. Spawn NPC 0x7c × 11 positions.
9. Load NPC 0x1b at [0x3d,0x0b] → entity `$283b`; talk script `0x1986`.
10. Load NPC 0x5e (Wings) at [0x3f,0x0d] → entity `$2837`; at [0x20,0x24] and [0x34,0x24] → entity `$2835`.
11. Write `$0ea2+2=0x01`, `$0eac+2=0x1983`.
12. **OBJ unloads:** if `$228a&0x10` → unload OBJs 3+10; if `$228a&0x40` → unload OBJ 7; if `$228a&0x20` → unload OBJ 8; if `$228a&0x80` → unload OBJ 9; if `$2283&0x08` → unload OBJ 1; if `$2283&0x10` → unload OBJ 2.
13. Play music 0x1e (only if `$238d!=0`); fade-in; `$23bf=0`; CALL cinematic sub `0x92de75`.
14. **Post-enter `$22f3&0x80` branch:** sleep 15 ticks; clear `$22f3&0x80`; RCALL sub `0x979300`:
    - Teleport boy to [0x31,0x28], dog to [0x31,0x2a]; face south.
    - Sleep 29 ticks; play SFX 0x76; SET OBJ 5 state = 1 → sleep 19 → SFX → state = 2 → sleep 19 → SFX → state = 3 → sleep 19 → SFX → state = 4.
    - RCALL `0x97927b`: check `$22eb&0x40` (clear if set, skip dialogue); else check `$2839` counter for dialogue line; increment `$2839`; restore player control.
    - RCALL `0x97933c`: BOY+DOG = player controlled; `$2834|=0x01`.
15. Else (normal entry): `$2834&=0xfd` (clear camera-pan bit); write `$242b=0xffff`.

## Step-on Scripts

| Tiles | Script | Effect |
|-------|--------|--------|
| `[1c,12:1e,13]` | `0x9793ad` | Switch puzzle — boy only; guard `$2834&0x04`; sets `$22e7|=0x04` (one-time throw animation); requires WEAPON_TYPE 0x04 (Spear; CURRENT_WEAPON_TYPE `$2360`); on success: `$2834|=0x04`, CALL `0x979443` (open boss door); else shows "not heavy enough" dialogue |
| `[14,10:17,11]` + 15 more tiles | `0x979372` | Pit-fall (16 tiles) — CALL `0x979226`; fall animation (controlled char drops until y > 0x128); RCALL camera sub `0x979195`; RCALL landing sub `0x979300` (spike display + dialogue) |
| `[1b,44:1f,46]` | `0x979127` | Exit south → 0x2b (Outside of Halls) |
| `[0c,1d:0e,21]` | `0x979131` | Exit west → 0x24 (Halls NW) |
| `[0c,2c:0e,30]` | `0x979139` | Exit west → 0x23 (Halls SW); sets `$238d=0x0001` (music cue) |
| `[2c,2c:2e,30]` | `0x979147` | Exit east → 0x2c (Halls SE); sets `$238d=0x0001` |
| `[2c,1d:2e,21]` | `0x979155` | Exit east → 0x2d (Halls NE); sets `$238d=0x0001` |
| `[1b,01:1f,03]` | `0x979163` | Exit north → 0x2a (Halls Boss Room); sets `$238d=0x0001` |
| `[10,05:12,07]` | `0x979171` | Gate trigger (one-time, `$228a&0x10`): SFX 0x5a; SET OBJ 10 state=1; SET OBJ 3 state=1; dialogue "Is that a door I hear?" |
| `[17,12:19,13]` | `0x9793ab` | Empty END (spike tile placeholder) |
| `[21,12:23,13]` | `0x9793ac` | Empty END (spike tile placeholder) |
| `[1a,28:1f,29]` | `0x979342` | Spike reset — if `$2834&0x01`: clear flag; walk non-controlled char to [0x29,0x50]; reverse OBJ 5 states 4→3→2→1→0 with SFX 0x76 between each; sleep 39 ticks |

### Pit-fall tile list
`[14,10:17,11]`, `[19,0e:1a,11]`, `[17,0d:1a,0e]`, `[17,0a:18,0d]`, `[15,09:18,0a]`, `[14,0c:15,10]`, `[12,0c:14,0d]`, `[12,09:13,0c]`, `[20,0d:21,11]`, `[21,0d:23,0e]`, `[22,0a:23,0d]`, `[22,09:27,0a]`, `[23,10:26,11]`, `[25,0c:26,10]`, `[29,09:2a,0d]`, `[26,0c:29,0d]`

## Exits

| Destination | Tiles | Condition |
|-------------|-------|-----------|
| 0x2b — Outside of Halls | `[1b,44:1f,46]` | always |
| 0x24 — Halls NW | `[0c,1d:0e,21]` | always |
| 0x23 — Halls SW | `[0c,2c:0e,30]` | always |
| 0x2c — Halls SE | `[2c,2c:2e,30]` | always |
| 0x2d — Halls NE | `[2c,1d:2e,21]` | always |
| 0x2a — Halls Boss Room | `[1b,01:1f,03]` | always |

## B-Triggers

| OBJ | Tiles | Flag | Item | Notes |
|-----|-------|------|------|-------|
| OBJ 1 | `[24,04:26,06]` | `$2283&0x08` | Nectar×1 | MAP REF `0x0001` |
| OBJ 2 | `[15,04:17,06]` | `$2283&0x10` | Vinegar×1 | MAP REF `0x0002` |

## NPCs

| NPC | Count | Positions | Entity | Notes |
|-----|-------|-----------|--------|-------|
| 0x70 | 6 | Various | — | Enemies; `$2433=0x0001` |
| 0x76 | 2 | [0x3f,0x0d], [0x18,0x0d] | — | Doors/pillars |
| 0x7c | 11 | Scattered | — | Enemies/wanderers |
| 0x1b | 1 | [0x3d,0x0b] | `$283b` | Talk NPC; script `0x1986` |
| 0x5e | 3 | [0x3f,0x0d], [0x20,0x24], [0x34,0x24] | `$2837` / `$2835` | Wings (fairy companion) |

## Notes

- **Switch puzzle** at `[1c,12:1e,13]` requires boy to have a Spear equipped (WEAPON_TYPE `$2360` == 0x04). No weapon level check. `$22e7&0x04` is the one-time animation flag (prevents re-throw); `$2834&0x04` is the success flag (gates door open).
- **Pit-fall landing dialogue** cycles through 4 lines as `$2839` increments: 0→1→2→…→12 (4th-wall break at 12). Counter persists across saves. Check `$22eb&0x40` first — if set, skip dialogue entirely (used when Wings joins or re-enters).
- **Spike-fall landing sequence** (`$22f3&0x80`): set by the room above when the player falls into a pit and lands here. NOT related to Wings. OBJ 5 is the spike ceiling object; states 1–4 = dropping position. After landing, `$2834|=0x01` marks the spikes as active — stepping on tile `[1a,28:1f,29]` pulls them back up.
- `$228a` bits 0x10/0x20/0x40/0x80 map to OBJs 3+10 / 8 / 7 / 9 respectively. OBJs 3 and 10 share the same `$228a&0x10` flag (set together on the gate-trigger step-on).
- The four wing exits (SW/NW/SE/NE) all set `$238d=0x0001` to signal that the Halls music 0x1e should keep playing on return; the south exit to 0x2b does not.
