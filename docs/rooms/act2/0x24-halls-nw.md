# [0x24] Antiqua — Halls NW

| Field | Value |
|-------|-------|
| Room ID | `0x24` |
| Name | Halls NW |
| Act | Act 2 — Antiqua |
| Data | `0xa3bc84` |
| Enter script ptr | `0x9280cf` |
| Enter script addr | `0x979a8b` |
| Step-ons | 29 entries (9 unique scripts) |
| B-triggers | 7 |
| Music | 0x1e (conditional) |
| Doggo | Greyhound (0x06) |

## Overview

Northwest wing of the Halls of Colossa. Features a multi-level pit-fall puzzle: stepping on any of 16 upper pit tiles drops the player within 0x24 to a lower section (OBJs 11/12/13 animate, first-time dialogue fires). From the lower section, 4 additional tiles set `$22f3&0x80` and load room 0x29 (the main hub) — this is the origin of the Wings drop cutscene. Two interactive bridge mechanisms: OBJ 2 bridge (B-trigger, states 1→10 = collapse animation, also retracted by step-on [38,25:3c,26]); OBJ 3 bridge (B-trigger [25,22:26,24], states 1→11 + camera pan via `$22e7&0x08`). One Spear weapon B-trigger (no persistence). Four gourds on OBJs 14–17. Wings (NPC 0x5e) is loaded here.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | 0x20 | ⚙️ | Enter animation guard — if clear, teleports both to [0x75,0xa7] + fade |
| `$228a` | 0x20 | 📖 | OBJ 0 one-time reveal (step-on [20,07:22,09]) [0x24]; also read in [0x29] enter to unload OBJ 8 |
| `$2285` | 0x02 | 🫙 | OBJ 14 Pixie Dust×1 looted [0x24] (MAP REF 0x0e) |
| `$2285` | 0x04 | 🫙 | OBJ 15 Call Beads×1 looted [0x24] (MAP REF 0x0f) |
| `$2285` | 0x08 | 🫙 | OBJ 16 Brimstone×2 looted [0x24] (MAP REF 0x10) |
| `$2285` | 0x10 | 🫙 | OBJ 17 Ash×1 looted [0x24] (MAP REF 0x11) |
| `$22e7` | 0x08 | ⚙️ | OBJ 3 bridge-reveal camera pan done (set after first pan, not repeated) [0x24] |
| `$22f3` | 0x80 | 📖 | Wings drop cutscene trigger — set in fall-to-0x29 tiles before CHANGE MAP [0x24] |
| `$2834` | 0x01 | ⚙️ | OBJ 1/3 bridge reveal B-trigger guard (once/session) [0x24] |
| `$2834` | 0x02 | ⚙️ | Pit direction flag (set = boy controlled; determines dog animation variant) [0x24] |
| `$2834` | 0x08 | ⚙️ | Pre-set on enter (part of inter-room session state) |
| `$2834` | 0x10 | ⚙️ | "Secret passage" first-time dialogue shown [0x24] |
| `$2834` | 0x20 | ⚙️ | Fell to lower section this session [0x24] |
| `$2834` | 0x40 | ⚙️ | Bridge retracted (step-on sets; B-trigger clears) [0x24] |

> **Note:** All `$2834` flags are session-only (re-initialized on next enter). See also 0x23 which uses different `$2834` bits for its own spike toggles.

## Enter Script Summary

1. Write `$0ea2+8=0x01`, `$0eac+8=0x1794` (Halls Wings parameter).
2. Set `$2834|=0x08` (session flag pre-set).
3. Set Greyhound.
4. **Entry guard:** if NOT `$22eb&0x20` → teleport both to [0x75,0xa7] + fade-out. Else clear `$22eb&0x20`.
5. Load NPC 0x5e (Wings) at [0x66,0x49].
6. Write `$0ea2+2=0x01`, `$0eac+2=0x1989` (Wings param).
7. **OBJ unloads:** if `$228a&0x20` → unload OBJ 0; if `$2285&0x02` → unload OBJ 14; if `$2285&0x04` → unload OBJ 15; if `$2285&0x08` → unload OBJ 16; if `$2285&0x10` → unload OBJ 17.
8. Write `$0ea2+0=0x40`, `$0eac+0=0x172b`.
9. Set prize rates: 100/30/2; prizes: 0x0801 (Nectar), 0x0001 qty 50, 0x0807.
10. `$2433=0x0002`.
11. Spawn NPC 0x70 × 12 positions; NPC 0x7c × 9 positions; NPC 0x76 × 8 positions.
12. Play music 0x1e (if `$238d!=0`); `$23bf=0`; CALL cinematic sub `0x92de75`.

## Step-on Scripts

| Tiles | Script | Effect |
|-------|--------|--------|
| `[1c,28:1d,31]` + 15 more (16 total) | `0x979759` | Pit-fall A (upper level) — shows OBJs 11/12/13; sets `$2834|=0x02/0x20`; fall animation (loop until y>0x31c); walk to [0x5b,0x25]; reset OBJs 11/12/13; if NOT `$2834&0x10`: set `$2834|=0x10`, dialogue "I'm glad we found that secret passage in the pit!" |
| `[1a,30:1c,31]` + 2 more (3 total) | `0x979739` | Fall to 0x29 (lower level) — shows OBJs 11/12/13; clears `$2834&0x02`; fall animation; sets `$22f3|=0x80`; CHANGE MAP to 0x29 |
| `[40,51:42,53]` | `0x979647` | Exit east → 0x29 (Halls main room) |
| `[1a,31:1c,32]` | `0x979a6e` | Non-controlled char follow — if `$2834&0x08` set → use saved coords; else store controlled char position; walk non-controlled to position |
| `[32,25:34,26]` | `0x979a27` | Empty END |
| `[15,4f:16,52]`, `[0a,4f:0b,52]` | `0x979a4e` | Camera scroll reset — if `$2834&0x04` set: clear it; write `$240f/$2411=0x48`, `$2413=0x68`, `$2415=0x38` |
| `[14,50:15,51]`, `[0b,50:0c,51]` | `0x979a28` | Camera scroll set — if NOT `$2834&0x04`: set it; write `$240f/$2411=0x80`, `$2413=0x68`, `$2415=0x78` |
| `[38,25:3c,26]` | `0x9797fa` | Bridge retract step-on (once/session, guard `$2834&0x40`): sets `$2834|=0x40`; walks non-controlled to [0x74,0x4a]; OBJ 2 states 9→8→…→0 + OBJ 4 state 0 with SFX 0x3c |

### Pit-fall A tile list
`[1c,28:1d,31]`, `[19,28:1a,31]`, `[30,28:31,2a]`, `[31,28:32,2a]`, `[34,28:35,2c]`, `[2e,2c:35,2d]`, `[2d,2b:2e,2d]`, `[2a,2a:2e,2b]`, `[29,28:2a,2b]`, `[22,27:2a,28]`, `[2c,27:32,28]`, `[34,27:3c,28]`, `[14,27:1a,28]`, `[1c,27:21,28]`, `[1a,27:1c,2f]`, `[1a,2f:1c,30]`

### Fall-to-0x29 tile list
`[1a,30:1c,31]`, `[25,30:27,31]`, `[28,30:2d,31]`, `[2e,30:3c,31]`

## Exits

| Destination | Tiles | Condition |
|-------------|-------|-----------|
| 0x29 — Halls main room (east) | `[40,51:42,53]` | always |
| 0x29 — Halls main room (via fall) | fall-to-0x29 tiles | always (drops through floor, sets `$22f3&0x80`) |

## B-Triggers

| OBJ | Tiles | Flag | Item | Notes |
|-----|-------|------|------|-------|
| OBJ 14 | `[05,4e:07,50]` | `$2285&0x02` | Pixie Dust×1 | MAP REF `0x000e` |
| OBJ 15 | `[17,56:19,58]` | `$2285&0x04` | Call Beads×1 | MAP REF `0x000f` |
| OBJ 16 | `[1c,3d:1e,3f]` | `$2285&0x08` | Brimstone×2 | MAP REF `0x0010` |
| OBJ 17 | `[2e,22:30,24]` | `$2285&0x10` | Ash×1 | MAP REF `0x0011` |
| OBJ 5 | `[1b,53:1e,56]` | none | — | Boy only; weapon type 2 (Spear), level ≥ 12; SFX 0x58 + SET OBJ 5 state 0x7e; no persistence — fires every B-press |
| OBJ 2/4 | `[3d,30:3e,32]` | none | — | Bridge collapse reverse: clears `$2834&0x40`; OBJ 4 state 0x7e; OBJ 2 states 1→10 with SFX 0x3c; no persistence |
| OBJ 1/3 | `[25,22:26,24]` | `$2834&0x01` (session) | — | Bridge reveal: shows OBJ 1; OBJ 3 states 1→11 with SFX 0x3c; camera pan on first trigger (`$22e7&0x08` gates repeat); one-time per session |

## NPCs

| NPC | Count | Positions | Notes |
|-----|-------|-----------|-------|
| 0x70 | 12 | Scattered | Enemies |
| 0x7c | 9 | Scattered | Enemies/wanderers |
| 0x76 | 8 | Scattered | Doors/pillars |
| 0x5e | 1 | [0x66,0x49] | Wings |

## Notes

- **Pit-fall loop**: stepping on any of the 16 upper-level pit tiles triggers OBJs 11/12/13 (trapdoor animation) and drops the controlled character to the lower section of 0x24. The first time shows a one-time dialogue (`$2834&0x10`).
- **Fall-to-0x29**: stepping on the 4 lower-level fall tiles sets `$22f3&0x80` and loads 0x29 — triggering the Wings-fall cutscene in the main hub. This is the authoritative source of that event.
- **`$2834|=0x08`** is set immediately on enter (before anything else). In 0x2d's step-ons, `$2834&0x08` is read as a guard — entering 0x24 effectively pre-fires some state for the NE room. // TODO: verify exact cross-room implication.
- **`$228a&0x20`** is set in this room's one-time step-on [20,07:22,09], AND read in 0x29's enter to unload OBJ 8. These are linked — the event in 0x24 removes a corresponding object in 0x29.
