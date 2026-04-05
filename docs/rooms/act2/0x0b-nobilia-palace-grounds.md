# 0x0b — Nobilia, Palace Grounds

| Field | Value |
|-------|-------|
| **ROM addr** | `0x9ffe13` |
| **Data addr** | `0xa6964a` |
| **Enter script** | `0x928052` → `0x96d5c8` |
| **Step-on table** | `0xa69659` len=`0x003c` (10 entries) |
| **B-trigger table** | `0xa69697` len=`0x0048` (12 entries) |
| **Music** | `0x4a` (vol `0x96`) |
| **Act** | Act 2 — Antiqua |

## Overview

The large courtyard between the fountain plaza (0x4c) and the Palace interior
(0x4d). Contains ten dog sniff spots (Water ×3, Vinegar ×2, Roots ×2, Bone ×2,
Limestone ×1), a 2500-gold chest, and a water-trap puzzle where the boy can sink
into a puddle. Three portal archways on the west wall have a special dog
slide-in animation. Arriving from 0x4c with `$234b=0x4f` triggers a Sacred-Dog
ceremony entry cinematic with the same dog portal animation.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22cf` | `0x10` | 💰 | 2500 Gold Coins chest looted [0x0b] |
| `$22cf` | `0x20` | 👃 | Sniffed Vinegar (#3) [0x0b] (0x20) |
| `$22cf` | `0x40` | 👃 | Sniffed Vinegar (#4) [0x0b] (0x40) |
| `$22cf` | `0x80` | 👃 | Sniffed Water (#1) [0x0b] (0x80) |
| `$22d0` | `0x01` | 👃 | Sniffed Water (#2) [0x0b] (0x01) |
| `$22d0` | `0x02` | 👃 | Sniffed Water (#5) [0x0b] (0x02) |
| `$22d0` | `0x04` | 👃 | Sniffed Roots (#6) [0x0b] (0x04) |
| `$22d0` | `0x08` | 👃 | Sniffed Roots (#7) [0x0b] (0x08) |
| `$22d0` | `0x10` | 👃 | Sniffed Bone (#8) [0x0b] (0x10) |
| `$22d0` | `0x20` | 👃 | Sniffed Bone (#9) [0x0b] (0x20) |
| `$22d0` | `0x40` | 👃 | Sniffed Limestone (#10) [0x0b] (0x40) |
| `$22dc` | `0x08` | 📖 | WindWalker unlocked (gates WindWalker obj 0) |
| `$2834` | `0x01` | 📖 | Boy-in-puddle flag (session-local) |
| `$2834` | `0x02` | 📖 | Boy-sinking animation played (session-local) |
| `$2843` | — | ⚙️ | Puddle state tracker: 0=none, 1=active, 2=puddle tile, 3=exit tile (session-local) |
| `$2857`–`$285f` | — | ⚙️ | Drip damage tracking registers (session-local) |
| `$2835` | — | ⚙️ | Guard NPC entity ref (talk `0x1962`; session-local) |
| `$2837` | — | ⚙️ | Guard NPC entity ref (talk `0x1965`; session-local) |
| `$283d`/`$283f`/`$2841` | — | ⚙️ | NPC `0x88` ×3 entity refs (fountain-entry animation; session-local) |

## Enter Script Summary

1. If `!IN_ANIMATION`: teleport both to `(0x06, 0x16)`, fade-out; else clear in-animation flag.
2. Load 3× NPC `0x88` (crowd/ceremony actors) at off-screen `(0xa9, 0x53)` → `$283d` / `$283f` / `$2841`.
3. Unload already-looted/sniffed objects via `$22cf`/`$22d0` bits (objs 1–10).
4. Play music `0x4a` at volume `0x96`; fade in; write `$23bf = 0x0001` (pacified).
5. If `$22dc&0x08` (WindWalker unlocked): SET OBJ 0 STATE = `0x7e`.
6. Load guard NPCs: NPC `0x1c` at `(0x2f, 0x35)` → `$2835` (talk `0x1962`); NPC `0x1d` at `(0x83, 0x27)` → `$2837` (talk `0x1965`).
7. **If `$234b == 0x4f`** (arriving from fountain Sacred-Dog ceremony): clear `$234b`; call cinematic `0x92de75`; RCALL dog-portal animation (`0x96d545`); then loop-RCALL boy-drip-damage monitor (`0x96d127` while `$2834&0x01`).
8. **Else** (normal entry): switch to dog; stop boy; teleport both to `(0x0b, 0x03)`; RCALL dog-portal animation (`0x96d545`).

**Dog portal animation sub `0x96d545`:**
- Stop dog, play anim `0x004e`, sleep 9.
- Face south; yield; play anim `0x0050 ×4`.
- Starting at `(0xa8, 0x148)`, loop 69 steps: decrement pos by `(-16, -8)` each tick, teleport dog.
- Face west; anim `0x004c`; yield; SFX `0x72`; return control to player.

## Exits

| Dest | Coords | Trigger |
|------|--------|---------|
| [0x4c] Fountain Plaza | `[0x00a8\|0x0058]` | Step-on `[29,2a:2f,2b]`; global `0x21` |
| [0x4d] Inside Palace | `[0x01b8\|0x0008]` | Step-on `[2b,13:2d,14]`; global `0x26` |

## B-Triggers

| Tile | Flag | Description |
|------|------|-------------|
| `[07,19:08,1a]` | `$22cf&0x10` | 💰 2500 Gold Coins chest |
| `[46,10:47,22]` | `$22cf&0x80` | 👃 Sniffed Water (#1) [0x0b] (0x80) |
| `[11,10:12,22]` + `[11,10:12,19]` | `$22d0&0x01` | 👃 Sniffed Water (#2) [0x0b] (0x01) |
| `[04,0d:05,0e]` | `$22cf&0x20` | 👃 Sniffed Vinegar (#3) [0x0b] (0x20) |
| `[53,0d:54,0e]` | `$22cf&0x40` | 👃 Sniffed Vinegar (#4) [0x0b] (0x40) |
| `[3e,0b:3f,0c]` | `$22d0&0x02` | 👃 Sniffed Water (#5) [0x0b] (0x02) |
| `[0c,21:0d,22]` | `$22d0&0x04` | 👃 Sniffed Roots (#6) [0x0b] (0x04) |
| `[50,21:51,22]` | `$22d0&0x08` | 👃 Sniffed Roots (#7) [0x0b] (0x08) — no NEXT ADD |
| `[19,12:1a,13]` | `$22d0&0x10` | 👃 Sniffed Bone (#8) [0x0b] (0x10) |
| `[03,17:04,18]` | `$22d0&0x20` | 👃 Sniffed Bone (#9) [0x0b] (0x20) — no NEXT ADD |
| `[54,15:55,16]` | `$22d0&0x40` | 👃 Sniffed Limestone (#10) [0x0b] (0x40) |

## Step-ons (additional)

| Tile | Action |
|------|--------|
| `[0a,1a:0b,1c]` + `[10,19:11,1b]` | Dog portal archway animation (sub `0x96d545`); dog slides west through archway |
| `[07,16:09,17]` | Dog portal animation (south-facing variant) |
| `[11,14:12,15]` ×2 | Water-trap: if `$2843==1` END; if dog controlled → walk by `(1,0)`; else → boy-sinking cutscene `0x96d226` (3× dig animation; `$2834\|=0x02` then `$2834\|=0x01`); unload objs 11+12 |
| `[10,14:11,15]` | Write `$2843 = 0x0002` (puddle state marker) |
| `[0f,14:10,15]` | Write `$2843 = 0x0003` (puddle state marker) |
| `[12,13:13,16]` | If `$2843 > 0`: clear `$2843 = 0`; if `$2834&0x01` → call `0x96d19d` with args `(1, -12)` |

## NPCs

| Ref | NPC# | Pos | Notes |
|-----|------|-----|-------|
| `$283d`/`$283f`/`$2841` | `0x88` ×3 | `(0xa9, 0x53)` off-screen | Ceremony actors loaded on entry; used in fountain Sacred-Dog animation |
| `$2835` | `0x1c` | `(0x2f, 0x35)` | Guard; talk script `0x1962` |
| `$2837` | `0x1d` | `(0x83, 0x27)` | Guard; talk script `0x1965` |

## Notes

- Sniff spots #3–#10 overlap address `$22d0` with 0x4c's Vinegar sniff `$22d0&0x80`;
  these are adjacent bits in the same byte, covering different objects.
- The water-trap puddle (`$2843` states) is an Act 2 puzzle. The boy-sinking
  animation only plays once (`$2834&0x02`). The drip-damage loop (`0x96d127`)
  deals damage scaled by elapsed time while the boy remains in the water
  (`$2834&0x01`).
- Entering with `$234b=0x4f` (from the Fountain after the Sacred Dog ceremony)
  triggers the dog slide-in animation which culminates in the dog walking through
  the palace archway, setting up the `0x4d` cutscene.
