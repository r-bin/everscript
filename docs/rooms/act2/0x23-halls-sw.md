# [0x23] Antiqua — Halls SW

| Field | Value |
|-------|-------|
| Room ID | `0x23` |
| Name | Halls SW |
| Act | Act 2 — Antiqua |
| Data | `0xacb96b` |
| Enter script ptr | `0x9280ca` |
| Enter script addr | `0x979064` |
| Step-ons | 6 entries (5 unique scripts) |
| B-triggers | 3 |
| Music | 0x5e (conditional) |
| Doggo | Greyhound (0x06) |

## Overview

Southwest wing of the Halls of Colossa. Contains three spike-panel puzzle toggles: stepping on any of three tiles activates OBJ state changes on spike panels (OBJs 3/4/5) and triggers SFX. Each toggle fires once per session (session-only `$2834` flags). Three gourds in the south area. One exit to the Collapsing Bridge (0x28); one exit back to the main hub (0x29).

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | 0x20 | ⚙️ | Enter animation guard — if clear, teleports both to south spawn [0x35,0x41] + fade |
| `$2283` | 0x20 | 🫙 | OBJ 6 Wings×1 looted [0x23] (MAP REF 0x06) |
| `$2283` | 0x40 | 🫙 | OBJ 7 Nectar×1 looted [0x23] (MAP REF 0x07) |
| `$2283` | 0x80 | 🫙 | OBJ 8 Brimstone×2 looted [0x23] (MAP REF 0x08) |
| `$2834` | 0x02 | ⚙️ | Spike-toggle session flag (set during toggle C; used by toggle B's OBJ routing) [0x23] |
| `$2834` | 0x04 | ⚙️ | Spike toggle B fired this session (one-time guard) [0x23] |
| `$2834` | 0x08 | ⚙️ | Spike toggle A fired this session (one-time guard) [0x23] |
| `$2834` | 0x10 | ⚙️ | Spike toggle C fired this session (one-time guard) [0x23] |
| `$2834` | 0x20 | ⚙️ | OBJ 3 spike panel raised state [0x23] (session) |
| `$2834` | 0x40 | ⚙️ | OBJ 4 spike panel raised state [0x23] (session) |
| `$2834` | 0x80 | ⚙️ | OBJ 5 spike panel raised state [0x23] (session) |
| `$22f3` | 0x40 | ⚙️ | Spike panel state changed (set within toggle script; gates SFX 0x76 ×3) [0x23] |

> **Note:** All `$2834` flags here are session-only (re-initialized on next room enter). The spike puzzle state does NOT persist across saves.

## Enter Script Summary

1. Write `$0ea2+8=0x01`, `$0eac+8=0x1794` (Halls Wings parameter).
2. Set Greyhound.
3. **Entry guard:** if NOT `$22eb&0x20` → teleport both to [0x35,0x41] + fade-out. Else clear `$22eb&0x20`.
4. Write `$0ea2+0=0x40`, `$0eac+0=0x172b`.
5. Set prize rates: 10/3/1; prizes: 0x0801 (Nectar), 0x0001 qty 50, 0x0803 (Wings).
6. `$2433=0x0001`.
7. Spawn NPC 0x76 × 3 (at [0x0d,0x35], [0x19,0x31], [0x31,0x1b]).
8. Spawn NPC 0x7c × 6 (at [0x2f,0x31], [0x33,0x39], [0x21,0x49], [0x0b,0x47], [0x27,0x37], [0x23,0x37]).
9. **OBJ unloads:** if `$2283&0x20` → unload OBJ 6; if `$2283&0x40` → unload OBJ 7; if `$2283&0x80` → unload OBJ 8.
10. Play music 0x5e (if `$238d!=0`); `$23bf=0`; CALL cinematic sub `0x92de75`.

## Step-on Scripts

| Tiles | Script | Effect |
|-------|--------|--------|
| `[69,50:6b,53]` ×2 | `0x978ede` | Exit east → 0x29 (Halls main room); sets `$238d=0x0001` |
| `[58,54:5a,56]` | `0x978f64` | Spike toggle A — once/session (guard `$2834&0x08`); shows OBJ 1; sets `$2834|=0x08|0x02`; lowers OBJ 3 if `$2834&0x20`; raises OBJ 4 if not `$2834&0x40`; raises OBJ 5 if not `$2834&0x80`; SFX 0x76 ×3 if any state changed |
| `[53,54:55,56]` | `0x978efa` | Spike toggle B — once/session (guard `$2834&0x04`); shows OBJ 0; sets `$2834|=0x04`; toggles bit 0x01 via 0x02; raises OBJ 3 if not `$2834&0x20`; lowers OBJ 4 if `$2834&0x40`; raises OBJ 5 if not `$2834&0x80`; SFX 0x76 ×3 if changed |
| `[5e,54:60,56]` | `0x978fc1` | Spike toggle C — once/session (guard `$2834&0x10`); shows OBJ 2; sets `$2834|=0x10|0x02`; SFX 0x2c; branches on `($2834&0x01)&&($2834&0x04)`: both-set path raises OBJs 3+4 and lowers OBJ 5; neither-set path raises OBJs 3+4+5; SFX 0x76 ×3 if changed |
| `[5e,48:61,4a]` | `0x978eec` | Exit north → 0x28 (Halls Collapsing Bridge); sets `$238d=0x0001` |

## Exits

| Destination | Tiles | Condition |
|-------------|-------|-----------|
| 0x29 — Halls main room | `[69,50:6b,53]` | always |
| 0x28 — Halls Collapsing Bridge | `[5e,48:61,4a]` | always |

## B-Triggers

| OBJ | Tiles | Flag | Item | Notes |
|-----|-------|------|------|-------|
| OBJ 6 | `[53,46:55,48]` | `$2283&0x20` | Wings×1 | MAP REF `0x0006` |
| OBJ 7 | `[58,46:5a,48]` | `$2283&0x40` | Nectar×1 | MAP REF `0x0007` |
| OBJ 8 | `[65,3c:67,3e]` | `$2283&0x80` | Brimstone×2 | MAP REF `0x0008` |

## NPCs

| NPC | Count | Positions | Notes |
|-----|-------|-----------|-------|
| 0x76 | 3 | [0x0d,0x35], [0x19,0x31], [0x31,0x1b] | Doors/pillars |
| 0x7c | 6 | Scattered | Enemies/wanderers |

## Notes

- The three spike toggles manipulate the same OBJs (3/4/5) with different logic, effectively cycling through spike-panel configurations. Each fires only once per session.
- `$22f3&0x40` is set during any toggle that changes an OBJ state, and is checked immediately to play SFX 0x76 ×3 (with 19-tick gaps). This flag persists in SRAM but is only read within the same script execution.
- Music 0x5e plays here (instead of the usual 0x1e hub music) only when arriving from 0x29 with `$238d` reset. Exits to all other rooms set `$238d=0x0001` to preserve the music.
- The 0x28 exit `[5e,48:61,4a]` leads north to the Collapsing Bridge area.
