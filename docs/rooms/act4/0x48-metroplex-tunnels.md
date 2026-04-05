# 0x48 — Omnitopia: Metroplex Tunnels

| Key | Value |
|-----|-------|
| ROM | `0x9fff07` |
| Data | `0x9fd4e3` |
| Enter script | `0x928183 → 0x9ad3df` |
| Step-ons | 56 entries @ `0x9fd4f2` (len=0x0150) |
| B-triggers | 53 entries @ `0x9fd644` (len=0x013e) |
| Music | SPACE (`0x3e`) |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (enemies always active) |

---

## Overview

The Metroplex Tunnels are the central transit hub of Omnitopia, connecting 9 other rooms via animated hatch transitions. The dog (forced to Toaster) crawls through a network of ventilation ducts to open barriers for the boy to advance. 16 GATE_BOTs guard corridor barriers throughout the tunnels; their kill state is tracked persistently across room entries. 8 RIMSALAS also patrol and respawn on each visit. On the very first entry to Omnitopia (`$22f8&0x02`), a ship-landing cutscene plays here before routing to the Junkyard (0x49). The tunnels are physically the largest room in act 4.

Cross-room relationships: serves as the hub connecting 0x46, 0x47, 0x43, 0x44, 0x00, 0x54, 0x7e, 0x42, and 0x4a.

---

## Enter Logic

```
0x9ad3df:
  if $22eb&0x20:               // "in animation" flag set = came from another room
    $22eb &= 0xdf              // clear flag, proceed to spawn
  else:                        // fresh/undefined entry
    teleport both to (0x12, 0x12)
    $24fd = 0x0001
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE $2348 = 0x0009
  WRITE $23bf = 0x0000         // un-PACIFIED
  if CHANGE MUSIC ($238d) != 0x00:
    PLAY MUSIC 0x3e (SPACE)
    CALL "Fade-in / start music"
  if $2264&0x20 || $22f9&0x20:
    SET OBJ 0x40 STATE = 0x7e  // remove exit gate

  if $22f8&0x02:               // BRANCH A — first Omnitopia entry (ship landing)
    CALL 0x9ad434
    END
  else:                        // BRANCH B — normal entry
    CALL 0x9ad5c8              // spawn position routing by $24fd
    CALL 0x9ad899              // enemy loader (16 GATE_BOTs + 8 RIMSALAS)
    CALL 0x9ae4f6              // kill-state applier
    END
```

### Branch A: Ship Landing Intro Cutscene (`0x9ad434`)

Triggered by `$22f8&0x02` (first Omnitopia entry; set never in this script, must be set externally before first entry).

1. BOY+DOG = STOPPED
2. LOAD DUSTER_BOT (`0x4d`) at `(0x37, 0x1f)` → entity handle → `$2838`; set player/AI controlled
3. LOAD PLACEHOLDER (`0x20`) at `(0x17, 0x00)` → entity handle → `$283a`; set script controlled; apply sprite change (`0x0198`)
4. Teleport both to off-screen `(0xFF, 0xE7)`
5. Play ship landing animation (multi-stage flight path through screen: `(0x00b8,0x0000)` → `(0x0138,0x00e8)` → `(0x0180,0x0130)` → `(0x0190,0x0158)`)
6. DUSTER_BOT walks out; PLACEHOLDER (ship) descends to `(0x0190, 0x01b0)`; fades out
7. SET OBJ 0x3f STATE = 0x7e (load ship-related OBJ)
8. CALL "Fade-out / stop music"
9. CALL "Unnamed Global script 0x2e"
10. CHANGE MAP = 0x49 Junkyard @ [0x0220, 0x0000]

### Branch B: Spawn Routing (`0x9ad5c8`)

Uses `$24fd` (entry-origin code set by the room you came from) to place the player near the correct entrance hatch:

| `$24fd` | Spawn (x, y) | Inner hatch OBJ | Source |
|---------|-------------|-----------------|--------|
| 1 | (0x0090, 0x0090) | OBJ 0x0b | 0x46 Prof's Lab (hatch) |
| 2 | (0x0290, 0x0090) | OBJ 0x00 | 0x00 Alarm room |
| 3 | (0x0490, 0x0090) | OBJ 0x0c | 0x44 Greenhouse |
| 4 | (0x0690, 0x0090) | OBJ 0x0d | 0x46 Prof's Lab (step-on east) |
| 5 | (0x0690, 0x01f0) | OBJ 0x0e | — |
| 6 | (0x0490, 0x01f0) | OBJ 0x0f | — |
| 7 | (0x0290, 0x01f0) | OBJ 0x10 | — |
| 8 | (0x0090, 0x0090) | OBJ 0x0b | — |
| 9 | (0x0090, 0x0350) | OBJ 0x11 | — |
| 10 | (0x0290, 0x0350) | OBJ 0x12 | 0x42 Reactor |
| 11 | (0x0090, 0x0090) | OBJ 0x0b | — |
| 12 | (0x0690, 0x0350) | OBJ 0x13 | — |
| 13 | (0x0690, 0x04b0) | OBJ 0x14 | — |
| 14 | (0x0490, 0x04b0) | OBJ 0x15 | 0x42 Reactor |
| 15 | (0x0090, 0x0090) | OBJ 0x0b | — (default/fallback) |
| 16 | (0x0090, 0x04b0) | OBJ 0x16 | 0x7e Jail |
| 17 | special cutscene | — | re-entry from Junkyard? |
| else | (0x0090, 0x0090) | OBJ 0x0b | default |

`$24fd = 17` triggers a mini-cutscene: loads PLACEHOLDER (`0x20`) at `(0x79, 0x53)`, dims sprites, then clears the entity; used for a character exit animation.

### Branch B: Enemy Loader (`0x9ad899`)

Loads 16 GATE_BOTs (`GATE_BOT = 0x66`) — one per corridor barrier — plus 8 RIMSALAS (`RIMSALA = 0x7b`). For each GATE_BOT:

- If `($22f6&bit || $22f7&bit)` OR `!$22f8&0x01` → show as already killed (set kill script, unload OBJ barrier)
- Else → enemy is alive; SET OBJ barrier STATE = 0x7e (barrier active)

After all 16 GATE_BOTs and 8 RIMSALAS are loaded: **`$22f8 |= 0x01`** (mark enemies as initialized).

### Branch B: Kill-State Applier (`0x9ae4f6`)

For each kill flag in `$22f6` and `$22f7`: if killed, applies a special entity modification (bits 20) to the corresponding entity handle — likely makes the corpse/dead state visible.

---

## Step-on Logic

All 56 step-on entries implement one mechanic: **dog duct gate triggers**.

**Condition:** dog controlled + `$2834&0x01` (dog in duct) + `!$2834&0x02` (not mid-transition) + gate not yet opened

**Effect:** SET OBJ (barrier) STATE = 0x7e (remove barrier), SFX 0xb0, set gate-open flag

Each gate is triggered from two zones (one on each side of the corridor). The gate flags are **session-only** (not persistent — reset on re-entry).

| Gate OBJ | Flag bit set | Zone A | Zone B |
|----------|-------------|--------|--------|
| OBJ 3 | `$2836 \|= 0x10` | [36,29:38,2a] | [36,25:38,26] |
| OBJ 4 | `$2836 \|= 0x20` | [16,29:18,2a] | [16,25:18,26] |
| OBJ 5 | `$2836 \|= 0x40` | [16,3f:18,40] | [16,3b:18,3c] |
| OBJ 6 | `$2836 \|= 0x80` | [36,3f:38,40] | [36,3b:38,3c] |
| OBJ 7 | `$2837 \|= 0x02` | [76,3f:78,40] | [76,3b:78,3c] |
| OBJ 8 | `$2837 \|= 0x04` | [76,55:78,56] | [76,51:78,52] |
| OBJ 9 | `$2837 \|= 0x08` | [56,55:58,56] | [56,51:58,52] |
| OBJ 10 | `$2837 \|= 0x10` | [36,55:38,56] | [36,51:38,52] |
| OBJ 23 | `$2834 \|= 0x04` | [16,1a:18,1b] | [16,17:18,18] |
| OBJ 24 | `$2834 \|= 0x10` | [56,1a:58,1b] | [56,17:58,18] |
| OBJ 25 | `$2834 \|= 0x20` | [76,1a:78,1b] | [76,17:78,18] |
| OBJ 26 | `$2834 \|= 0x80` | [56,30:58,31] | [56,2d:58,2e] |
| OBJ 27 | `$2835 \|= 0x01` | [36,30:38,31] | [36,2d:38,2e] |
| OBJ 28 | `$2835 \|= 0x02` | [16,30:18,31] | [16,2d:18,2e] |
| OBJ 29 | `$2835 \|= 0x04` | [16,46:18,47] | [16,43:18,44] |
| OBJ 30 | `$2835 \|= 0x10` | [56,46:58,47] | [56,43:58,44] |
| OBJ 31 | `$2835 \|= 0x20` | [76,46:78,47] | [76,43:78,44] |
| OBJ 2 | `$2834 \|= 0x08` | [36,1a:38,1b] | [36,17:38,18] |

---

## B-trigger Logic

### Within-room duct entry/exit (39 entries)

Bidirectional dog-crawl mechanic. Each duct has two B-trigger zones:

**"Enter duct going south" (boy-controlled):**
- Condition: `(controlled char == dog && $2834&0x01) → END` (abort if dog in duct)
- Condition: `(controlled char == boy) → END` (boy can't enter from outside)
- Effect: `$2834 |= 0x02` (mark transitioning), SET hatch OBJ to 0x7e (open), dog walks to hatch, teleport dog into duct, `$2834 |= 0x01` (dog in duct), `$2834 &= 0xfd` (clear transition), player control

**"Exit duct going north" (dog-in-duct-controlled):**
- Condition: `(controlled char == boy || !$2834&0x01) → END` (must be dog in duct)
- Effect: stops both, dog walks to hatch, SET hatch OBJ to 0x7e (open), `$2834 &= 0xfe` (dog exits duct), `$2834 &= 0xfd` (clear transition), player control

Hatch objects used (from `$24f9`): OBJ 0x37–0x3e for within-room duct entrances in the lower half; OBJ 0x30–0x36 in the upper half.

### Cross-room hatch transitions (14 entries)

Dog + boy transported to another room. Before every CHANGE MAP: `$22f8 |= 0x04`.

| Zone | To room | Spawn @ |
|------|---------|---------|
| [46,35:48,37] | 0x4a Final Boss Room | [0x00a0, 0x0128] |
| [76,56:78,58] | 0x47 Storage Room | [0x0080, 0x00d0] |
| [56,56:58,58] | 0x43 Control Room | [0x02a0, 0x0090] |
| [56,2a:58,2c] | 0x44 Greenhouse | [0x0070, 0x0340] |
| [76,40:78,42] | 0x00 Alarm Room | [0x0070, 0x03d8] |
| // TODO: zone | 0x00 Alarm Room | [0x01c0, 0x0088] |
| // TODO: zone | 0x46 Prof's Lab | [0x02c0, 0x02b8] |
| [56,14:58,16] | 0x44 Greenhouse | [0x0260, 0x00a8] |
| [36,2a:38,2c] | 0x54 Shops | [0x0050, 0x0280] |
| [36,14:38,16] | 0x54 Shops | [0x0370, 0x0098] |
| [16,14:18,16] | 0x7e Jail | [0x0630, 0x00a0] |
| [16,56:18,58] | 0x42 Reactor | [0x01f0, 0x01d8] |
| [16,40:18,42] | 0x42 Reactor | [0x0160, 0x0068] |
| [36,40:38,42] | 0x42 Reactor | [0x0290, 0x0068] |

The `[46,35:48,37]` → 0x4a transition uses a slightly different subroutine (`0x9ae24f` "Omnitopia hatch fade-out") that requires the dog to already be in duct mode (`$2834&0x01` check at `0x9ae258`).

---

## Object List

Objects are grouped by function. The room has at minimum 0x41 objects (OBJ 0x00–0x40).

### Spawn/entrance hatches (inner, tunnel side) — OBJ 0x0b–0x16

| OBJ | Pos (approx) | Spawn when `$24fd` |
|-----|-------------|-------------------|
| 0x0b | (0x90, 0x90) | 1, 8, 11, 15, default |
| 0x0c | (0x490, 0x90) | 3 |
| 0x0d | (0x690, 0x90) | 4 |
| 0x0e | (0x690, 0x1f0) | 5 |
| 0x0f | (0x490, 0x1f0) | 6 |
| 0x10 | (0x290, 0x1f0) | 7 |
| 0x11 | (0x90, 0x350) | 9 |
| 0x12 | (0x290, 0x350) | 10 |
| 0x13 | (0x690, 0x350) | 12 |
| 0x14 | (0x690, 0x4b0) | 13 |
| 0x15 | (0x490, 0x4b0) | 14 |
| 0x16 | (0x90, 0x4b0) | 16 |

OBJ 0x00 used as spawn hatch when `$24fd == 2` (from 0x00 Alarm Room) — position `(0x290, 0x90)`.

### Dog duct gates (session-only barriers) — OBJ 2–10, 23–31

These barriers are opened by the dog crawling through zones. Reset on room re-entry.

| OBJ | Opened when flag is set |
|-----|-------------------------|
| 2 | `$2834&0x08` |
| 3 | `$2836&0x10` |
| 4 | `$2836&0x20` |
| 5 | `$2836&0x40` |
| 6 | `$2836&0x80` |
| 7 | `$2837&0x02` |
| 8 | `$2837&0x04` |
| 9 | `$2837&0x08` |
| 10 | `$2837&0x10` |
| 23 | `$2834&0x04` |
| 24 | `$2834&0x10` |
| 25 | `$2834&0x20` |
| 26 | `$2834&0x80` |
| 27 | `$2835&0x01` |
| 28 | `$2835&0x02` |
| 29 | `$2835&0x04` |
| 30 | `$2835&0x10` |
| 31 | `$2835&0x20` |

### GATE_BOT enemy barriers (persistent) — various OBJs

Each GATE_BOT blocks a corridor barrier. Kill state tracked by `$22f6`/`$22f7`.

| OBJ barrier | Kill flag | GATE_BOT spawn pos | Entity handle |
|-------------|----------|--------------------|---------------|
| OBJ 0x2e | `$22f6&0x02` | (0x32, 0x0d) | `$283c` |
| OBJ 0x26 | `$22f6&0x04` | (0xb2, 0x0d) | `$283e` |
| OBJ 0x20 | `$22f6&0x08` | (0x12, 0x22) | `$2840` |
| OBJ 0x01 | `$22f6&0x10` | (0x52, 0x22) | `$2842` |
| OBJ 0x2d | `$22f6&0x20` | (0x32, 0x39) | `$2844` |
| OBJ 0x27 | `$22f6&0x40` | (0xb2, 0x39) | `$2846` |
| OBJ 0x21 | `$22f6&0x80` | (0x12, 0x4e) | `$2848` |
| OBJ 0x22 | `$22f7&0x01` | (0x52, 0x4e) | `$284a` |
| OBJ 0x2c | `$22f7&0x02` | (0x32, 0x65) | `$284c` |
| OBJ 0x28 | `$22f7&0x04` | (0xb2, 0x65) | `$284e` |
| OBJ 0x23 | `$22f7&0x08` | (0x92, 0x7a) | `$2850` |
| OBJ 0x24 | `$22f7&0x10` | (0xd2, 0x7a) | `$2852` |
| OBJ 0x2b | `$22f7&0x20` | (0x32, 0x91) | `$2854` |
| OBJ 0x2a | `$22f7&0x40` | (0x72, 0x91) | `$2856` |
| OBJ 0x29 | `$22f7&0x80` | (0xb2, 0x91) | `$2858` |

*Note: 15 GATE_BOT barriers listed; a 16th is implied by the 16th entity loaded but not shown in the above read.*

RIMSALA (`0x7b`) positions (8, respawn each visit): `(0xbb,0x15)`, `(0xa7,0x41)`, `(0xbb,0x6d)`, `(0xa1,0x99)`, `(0x3d,0x15)`, `(0x2b,0x41)`, `(0x3d,0x6d)`, `(0x25,0x99)`.

### Cross-room hatch objects (tunnel side) — OBJ 0x2f–0x3e

| OBJ | Position | Room connection |
|-----|----------|-----------------|
| 0x2f | (0xd0, 0x40) | 0x7e Jail (B-trigger [16,14:18,16]) |
| 0x30 | (0x2d0, 0x40) | 0x54 Shops (B-trigger [36,14:38,16]) |
| 0x31 | (0x4d0, 0x40) | 0x44 Greenhouse (B-trigger [56,14:58,16]) |
| 0x32 | (0x6d0, 0x40) | // TODO: room |
| 0x33 | ? | // TODO |
| 0x34 | (0x4d0, 0x1a0) | // TODO |
| 0x35 | (0x2d0, 0x1a0) | 0x54 Shops (B-trigger [36,2a:38,2c]) |
| 0x36 | (0xd0, 0x1a0) | // TODO |
| 0x37 | (0xd0, 0x300) | 0x42 Reactor (B-trigger [16,40:18,42]) |
| 0x38 | (0x2d0, 0x300) | 0x42 Reactor (B-trigger [36,40:38,42]) |
| 0x39 | (0x4d0, 0x300) | // TODO |
| 0x3a | (0x6d0, 0x300) | // TODO |
| 0x3b | (0x6d0, 0x460) | // TODO |
| 0x3c | (0x4d0, 0x460) | // TODO |
| 0x3d | (0x2d0, 0x460) | // TODO |
| 0x3e | (0xd0, 0x460) | 0x4a Final Boss (B-trigger [46,35:48,37]) + 0x42 Reactor ([16,56:18,58]) |

### Special OBJs

| OBJ | Purpose |
|-----|---------|
| 0x3f | Ship prop — SET STATE=0x7e during landing cutscene |
| 0x40 | Final exit gate — removed on enter if `$2264&0x20 \|\| $22f9&0x20` |

---

## Memory Access

| Address | Bit | R/W | Description |
|---------|-----|-----|-------------|
| `$22eb` | `0x20` | R→W | "In animation" entry flag; cleared on enter |
| `$22f6` | `0x02` | R/W | GATE_BOT #1 killed (at 0x32,0x0d); OBJ 0x2e |
| `$22f6` | `0x04` | R/W | GATE_BOT #2 killed (at 0xb2,0x0d); OBJ 0x26 |
| `$22f6` | `0x08` | R/W | GATE_BOT #3 killed (at 0x12,0x22); OBJ 0x20 |
| `$22f6` | `0x10` | R/W | GATE_BOT #4 killed (at 0x52,0x22); OBJ 0x01 |
| `$22f6` | `0x20` | R/W | GATE_BOT #5 killed (at 0x32,0x39); OBJ 0x2d |
| `$22f6` | `0x40` | R/W | GATE_BOT #6 killed (at 0xb2,0x39); OBJ 0x27 |
| `$22f6` | `0x80` | R/W | GATE_BOT #7 killed (at 0x12,0x4e); OBJ 0x21 |
| `$22f7` | `0x01` | R/W | GATE_BOT #8 killed (at 0x52,0x4e); OBJ 0x22 |
| `$22f7` | `0x02` | R/W | GATE_BOT #9 killed (at 0x32,0x65); OBJ 0x2c |
| `$22f7` | `0x04` | R/W | GATE_BOT #10 killed (at 0xb2,0x65); OBJ 0x28 |
| `$22f7` | `0x08` | R/W | GATE_BOT #11 killed (at 0x92,0x7a); OBJ 0x23 |
| `$22f7` | `0x10` | R/W | GATE_BOT #12 killed (at 0xd2,0x7a); OBJ 0x24 |
| `$22f7` | `0x20` | R/W | GATE_BOT #13 killed (at 0x32,0x91); OBJ 0x2b |
| `$22f7` | `0x40` | R/W | GATE_BOT #14 killed (at 0x72,0x91); OBJ 0x2a |
| `$22f7` | `0x80` | R/W | GATE_BOT #15 killed (at 0xb2,0x91); OBJ 0x29 |
| `$22f8` | `0x01` | W | Set after first enemy load (marks enemies initialized) |
| `$22f8` | `0x02` | R | Omnitopia first entry flag → branch A (ship landing) |
| `$22f8` | `0x04` | W | Set before every cross-room CHANGE MAP from 0x48 |
| `$22f9` | `0x20` | R | OBJ 0x40 unload condition on enter // ? |
| `$2264` | `0x20` | R | OBJ 0x40 unload condition on enter // ? |
| `$2348` | full | W | Written = 0x0009 on enter // ? (hook slot count?) |
| `$238d` | full | R | Current music (read to skip re-play) |
| `$2443` | full | W | Dog breed → Toaster (`0x0C`) |
| `$23bf` | full | W | PACIFIED → `0x0000` (unpacified) |
| `$24fd` | full | R/W | Entry-origin code; routed via `0x9ad5c8` |
| `$2834` | `0x01` | R/W | Dog in duct mode |
| `$2834` | `0x02` | R/W | Dog mid-transition (hatch animation in progress) |
| `$2834` | `0x04` | W | Dog gate OBJ 23 opened |
| `$2834` | `0x08` | W | Dog gate OBJ 2 opened |
| `$2834` | `0x10` | W | Dog gate OBJ 24 opened |
| `$2834` | `0x20` | W | Dog gate OBJ 25 opened |
| `$2834` | `0x80` | W | Dog gate OBJ 26 opened |
| `$2835` | `0x01` | W | Dog gate OBJ 27 opened |
| `$2835` | `0x02` | W | Dog gate OBJ 28 opened |
| `$2835` | `0x04` | W | Dog gate OBJ 29 opened |
| `$2835` | `0x10` | W | Dog gate OBJ 30 opened |
| `$2835` | `0x20` | W | Dog gate OBJ 31 opened |
| `$2836` | `0x10` | W | Dog gate OBJ 3 opened |
| `$2836` | `0x20` | W | Dog gate OBJ 4 opened |
| `$2836` | `0x40` | W | Dog gate OBJ 5 opened |
| `$2836` | `0x80` | W | Dog gate OBJ 6 opened |
| `$2837` | `0x02` | W | Dog gate OBJ 7 opened |
| `$2837` | `0x04` | W | Dog gate OBJ 8 opened |
| `$2837` | `0x08` | W | Dog gate OBJ 9 opened |
| `$2837` | `0x10` | W | Dog gate OBJ 10 opened |

*All `$2834`–`$2837` gate flags are session-only (not saved). See Notes.*

---

## Notes

- `$2834`–`$2837` gate flags are NOT persistent — the dog must re-open all session gates on every visit. Only the GATE_BOT kill flags in `$22f6`/`$22f7` are persistent.
- `$22f8&0x02` (ship landing branch) is a one-shot event. After Branch A triggers it is NOT cleared here, but the branch A subroutine ends with CHANGE MAP to 0x49; 0x48 will never be re-entered via Branch A once 0x49 loads its own flags. // TODO: confirm where `$22f8&0x02` is first set.
- `$22f8&0x04` is written before every B-trigger CHANGE MAP exit. Its use in destination rooms is not confirmed here; likely a "came from 0x48" flag. // TODO: verify in destination rooms.
- `$2348 = 0x0009` on enter — meaning unknown. May control hook slot count or entity timing. // TODO.
- OBJ 0x3e is shared between two B-triggers: `[46,35:48,37]` (→ 0x4a) and `[16,56:18,58]` (→ 0x42). These two hatches are at the same position `(0xd0, 0x460)` but different coordinates, which is surprising — likely different hatches with different destination coords stored in `$24fb`. // TODO: confirm visual distinction.
- The B-trigger `[46,35:48,37]` → 0x4a uses `0x9ae24f` (hatch fade-out) which additionally checks `$2834&0x01` — requiring the dog to already be in duct mode to open the final boss door.
- 8 RIMSALAS loaded at hardcoded positions (no kill flags) — they respawn every room visit. The room name mentions "rimsalas, spheres" matching these two enemy types.
- Two B-trigger zones for cross-room connections are unresolved: the second 0x00 Alarm Room hatch and the return-to-0x46 hatch. Their zones likely appear in the mid-section of the B-trigger list (ids ~b5e–b70 area). // TODO: confirm zones by matching `CHANGE MAP` addresses: 0x9aedb9 − 0x2b = 0x9aed8e; 0x9aeeae − 0x2b = 0x9aee83.
- `$22f6&0x02` through `$22f7&0x80` uses 15 kill flags for GATE_BOTs, but 16 GATE_BOTs are loaded (the 16th in the enemy loader was not fully read before the section ended). // TODO: confirm 16th GATE_BOT OBJ and kill flag.
- Entity handles for GATE_BOTs: `$283c`, `$283e`, `$2840`, `$2842`, `$2844`, `$2846`, `$2848`, `$284a`, `$284c`, `$284e`, `$2850`, `$2852`, `$2854`, `$2856`, `$2858`, (+`$285a`?). Handle `$2838` is DUSTER_BOT (Branch A only).
- `$24fd` routing: values 1, 8, 11, 15 all map to the same spawn point (0x0090, 0x0090) — likely representing different rooms whose hatches all exit at the NW corner of the tunnels.
