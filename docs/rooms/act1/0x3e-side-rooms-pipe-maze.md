# 0x3e — Side Rooms of Pipe Maze

**ROM:** `0x9ffedf` | **Data:** `0xa98000` | **Enter:** `0x928151` → `0x94b1a8`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x86` |
| Map bounds | Shared multi-chamber pipe room (sub-room layouts selected by `$24c3`) |
| NPCs | `0x52` (main NPC), `0x1a` (Raptor, one-time), 5× `0x0f`, optional `0x2b` |
| Step-on zones | 12 |
| B-triggers | 14 (5 gourds + 9 sniff spots) |
| Sniff spots | 9 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| West (low) | `0x3d` Pipe maze @ `[0x02d8\|0x04a0]` | step-on `[17,10:18,12]` | Global 0x2e |
| West (high) | `0x3d` Pipe maze @ `[0x0338\|0x04a0]` | step-on `[1e,10:1f,12]` | Global 0x2e |
| South | `0x3b` Volcano Room 2 @ `[0x03b0\|0x0030]` | step-on `[1b,22:1d,24]` | fade+stop music; `$22ee&=0xfb` |
| North | `0x3f` Volcano Boss Room @ `[0x00c0\|0x0238]` | step-on `[5a,13:5c,15]` | fade+stop music |

### Internal Teleports / Pipe Rides

| Zone | Action | Notes |
|------|--------|-------|
| `[63,1e:65,1f]` | Switch press (OBJ state changes, SFX) | Sets `$225f\|=0x08`; gated by `$225f&0x08` |
| `[66,13:67,15]` | `$24c3=0`; teleport to `(0x17, 0x2d)` | Internal reposition |
| `[58,13:59,15]` | `$24c3=0`; teleport to `(0x17, 0x07)` | Internal reposition |
| `[3c,0f:3d,11]` | `$24c3=0`; if `$24c3<=4` → `(0x17,0x2d)` else `(0x17,0x07)` | Conditional return |
| `[6b,1d:6c,1e]` | Pipe ride: `$24b3=2, $24b5=0x22, $24b7=0xec, $24b9=0xec`; non-ctrl → `(0x23,0xbf)` | Calls `0x94af59` |
| `[54,1b:55,1c]` | Pipe ride: `$24b3=2, $24b5=0x22, $24b7=0x14, $24b9=0x14`; non-ctrl → `(0x1f,0x87)` | Calls `0x94af59` |
| `[41,19:42,1a]` | Pipe ride: `$24b3=2, $24b5=0x22, $24b7=0xec, $24b9=0xec`; non-ctrl → `(0x1b,0x6f)` | Calls `0x94af59` |
| `[5a,18:5e,19]` | Dialog: "there's a switch in the next room!" | Sets `$22ee\|=0x04`; gated by `$225f&0x08` OR `$22ee&0x04` |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22ee` | `0x01` | ⚙️ | Intro/outro flag (from Prof. Lab); if set on entry, teleports to `(0x25, 0xaf)` |
| `$22ee` | `0x04` | 📖 | Side rooms corridor dialog shown (Blimp "switch in next room") |
| `$225f` | `0x08` | 📖 | **Pipe Maze switch pressed** |
| `$225f` | `0x10` | 📖 | **Pipe Maze Raptor shown** (one-time Raptor cutscene gate) |
| `$22b0` | `0x40` | 👃 | Sniffed Water (#8) |
| `$22b0` | `0x80` | 👃 | Sniffed Water (#9) |
| `$22b1` | `0x01` | 👃 | Sniffed Water (#10) |
| `$22b1` | `0x02` | 👃 | Sniffed Clay (#11) |
| `$22b1` | `0x04` | 👃 | Sniffed Roots (#12) |
| `$22b1` | `0x08` | 👃 | Sniffed Oil (#13) |
| `$22b1` | `0x10` | 👃 | Sniffed Ash (#15) |
| `$22b1` | `0x20` | 👃 | Sniffed Ash (#14) |
| `$22b1` | `0x40` | 👃 | Sniffed Wax (#16) |
| `$226a` | `0x02` | 🫙 | Gourd MAP REF 0x07 looted (Wax) |
| `$226a` | `0x04` | 📖 | Gourd MAP REF 0x00 looted (Wax alt; also gates OBJ 0 state in sub-room 1) |
| `$226a` | `0x08` | 🫙 | Gourd MAP REF 0x01 looted (Oil); also gates OBJ 1 state in sub-room 7 |
| `$226a` | `0x10` | 📖 | Gourd MAP REF 0x02 looted (Clay alt); also gates OBJ 2 state in sub-room 4 |
| `$226a` | `0x20` | 🫙 | Gourd MAP REF 0x03 looted (Ash); also gates OBJ 3 state in sub-room 8 |
| `$226a` | `0x40` | 📖 | Gourd MAP REF 0x02 looted (Clay; `$24c3==10`); also gates OBJ 2 state in sub-room 10 |
| `$226a` | `0x80` | 📖 | Gourd MAP REF 0x00 looted (Oil; `$24c3==7`); also gates OBJ 0 state in sub-room 7 |

## NPCs

| NPC ID | Position | State | Notes |
|--------|----------|-------|-------|
| `0x1a` | `(0x0e, 0x23)` | `0020` | Raptor — one-time entry cutscene (slides in from top); only if NOT `$225f&0x10`; stored `$2834`; makes obj 7 state 1 after walking in |
| `0x52` | `(0xa9, 0x17)` | `0002` | Unknown NPC type; talk script `0x181b`; always loaded |
| `0x0f` | 5 positions | — | Loaded at `(25,0f)`, `(07,1b)`, `(63,0f)`, `(8b,15)`, `(97,27)` |
| `0x2b` | varies | — | Sub-room NPC; loaded in sub-rooms 3, 8, 9 only (positions `(55,1d)`, `(4f,19)`, `(4b,21)`) |

## Sub-room Layouts (by `$24c3`)

`$24c3` is set by the step-ons in 0x3d. Each value selects a different object configuration.

| Sub-room | OBJ 0 | OBJ 1 | OBJ 2 | OBJ 3 | OBJ 4 | OBJ 5 | NPC `0x2b`? |
|----------|-------|-------|-------|-------|-------|-------|------------|
| 1 | 1 or 2 (`$226a&0x04`) | 0 | 0 | 0 | 1 | 0 | No |
| 2 | 0 | 0 | 0 | 0 | 1 | 1 | No |
| 3 | 0 | 0 | 0 | 0 | 1 | 1 | Yes ×2 |
| 4 | 0 | 0 | 1 or 2 (`$226a&0x10`) | 0 | 1 | 0 | No |
| 7 | 1/2 (`$226a&0x80`) | 1/2 (`$226a&0x08`) | 0 | 0 | 1 | 1 | No |
| 8 | 0 | 0 | 0 | 0/1 (`$226a&0x20`) | 0 | 0 | Yes ×1 |
| 9 | 0 | 0 | 0 | 0 | 0 | 1 | Yes ×1 |
| 10 | 0 | 0 | 0/1 (`$226a&0x40`) | 0 | 1 | 2 | No |
| — (no $24c3) | — | — | — | — | — | — | No |

Sub-rooms 5 and 6 have no matching branch in the enter script and are likely reached only via the `$24c3=5/6` internal teleports triggered from within 0x3e itself. OBJ 17 and OBJ 6 states 1/3 are set by the switch step-on (`$225f&0x08`).

## Gourds

| MAP REF | Zone | Contents | Flag | Notes |
|---------|------|----------|------|-------|
| 0x0000 | `[31,19:33,1b]` | 🛢️ Oil | `$226a&0x80` | Only if `$24c3==7`; else Wax (`$226a&0x04`) |
| 0x0001 | `[36,14:38,16]` | 🛢️ Oil | `$226a&0x08` | |
| 0x0002 | `[39,17:3b,19]` | 🏺 Clay | `$226a&0x40` | Only if `$24c3==10`; else Clay (`$226a&0x10`) |
| 0x0003 | `[45,1b:47,1d]` | 💨 Ash | `$226a&0x20` | |
| 0x0007 | `[15,1b:17,1d]` | 🕯️ Wax | `$226a&0x02` | |

## Sniff Spots

| # | Zone | Ingredient | Flag |
|---|------|------------|------|
| 8 | `[42,1a:43,1b]` | 💧 Water | `$22b0&0x40` |
| 9 | `[53,1c:54,1d]` | 💧 Water | `$22b0&0x80` |
| 10 | `[6c,1e:6d,1f]` | 💧 Water | `$22b1&0x01` |
| 11 | `[19,1d:1a,1e]` | 🏺 Clay | `$22b1&0x02` |
| 12 | `[30,15:31,16]` | 🌿 Roots | `$22b1&0x04` |
| 13 | `[63,14:64,15]` | 🛢️ Oil | `$22b1&0x08` |
| 14 | `[5c,1e:5d,1f]` | 💨 Ash | `$22b1&0x20` |
| 15 | `[1d,1d:1e,1e]` | 💨 Ash | `$22b1&0x10` |
| 16 | `[36,22:37,23]` | 🕯️ Wax | `$22b1&0x40` |

**Summary:** Water×3, Clay×1, Roots×1, Oil×1, Ash×2, Wax×1 = 9 sniff spots.

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x181b` | NPC `0x52` talk script |
| `0x94af59` | Pipe ride subroutine (moves non-controlled character, plays animation) |
| `0x94afd4` | Unknown subroutine called after pipe ride |
| `0x94ac56` | Shared CHANGE MAP setup (called from 0x3d step-ons before warping here) |

## Notes

- **Sub-room system:** The same physical map area of 0x3e is reused for all 10 sub-rooms. The enter script reads `$24c3` and configures objects 0–5 to present different puzzle layouts. This is an unusual pattern — most rooms are distinct maps. 0x3e is essentially a single-tile environment that presents different configurations on entry.
- **Switch step-on `[63,1e:65,1f]`:** Pressing the switch moves the camera (`$242b/$242d` viewport scroll), plays sound `0x44` and `0x3c` three times, and sets objs 6/17 to states 1/2/3. The `$225f|=0x08` flag persists this for future entries.
- **Pipe rides:** Three step-ons (zones `[6b,1d:6c,1e]`, `[54,1b:55,1c]`, `[41,19:42,1a]`) call `0x94af59` with `$24b3/$24b5/$24b7/$24b9` parameters, then teleport the non-controlled character to a specific position. These simulate riding through a pipe.
- **Gourd MAP REF 0x0000 and 0x0002 are dual-content:** The same zone gives different items depending on `$24c3`. The flag bits used also overlap with the sub-room layout flags — looting the gourd changes the object state. This appears intentional (loot = puzzle element resolved).
- **Raptor cutscene (`$225f&0x10`):** On first entry ever, the Raptor NPC `0x1a` slides down from the top of the screen in a scripted animation, then walks to its final position. The `$225f|=0x10` flag prevents this from replaying. After the cutscene, OBJ 7 is set to state 1 or 2 based on whether `$226a&0x02` is set.
- **`$22ee&0x01`** = from Prof. Lab — if set on 0x3e entry, teleports player to `(0x25, 0xaf)` (presumably near the Prof. Lab gate area), then clears the flag.
- **Music:** Shares music `0x86` with 0x3d (pipe maze theme).
