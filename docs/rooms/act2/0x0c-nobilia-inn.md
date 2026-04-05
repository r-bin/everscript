# 0x0c — Nobilia, Inn

| Field | Value |
|-------|-------|
| **ROM addr** | `0x9ffe17` |
| **Data addr** | `0xad9f83` |
| **Enter script** | `0x928057` → `0x95e919` |
| **Step-on table** | `0xad9f92` len=`0x0018` (4 entries) |
| **B-trigger table** | `0xad9fac` len=`0x000c` (2 entries) |
| **Music** | `0x42` |
| **Act** | Act 2 — Antiqua |

## Overview

A two-area building in Nobilia: an inn on the lower floor (innkeeper offers
rest + save for 30 Jewels) and a warehouse/shop on the upper floor (hidden Atlas
merchant). The camera bounds switch based on `$22ec&0x40` to focus on whichever
area the player entered from. Also contains the Atlas spell teaching sequence,
where the merchant is surprised in bed and offers Atlas + an Atlas Medallion upsell.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$2258` | `0x02` | ⚗️ | Atlas spell taught [0x0c] R/W (set here on first Atlas meeting) |
| `$22ec` | `0x40` | ⚙️ | Camera area flag (upper floor vs. lower floor) |
| `$22ee` | `0x01` | ⚙️ | Cleared on enter (unknown intro/outro flag) |
| `$22ed` | `0x20` | 📖 | Warehouse merchant greeting seen [0x0c] |
| `$2455` | — | ⚙️ | NPC `0x20` entity ref (session-local) |
| `$2836` | — | ⚙️ | Atlas merchant NPC entity ref (session-local) |
| `$2457` | — | ⚙️ | Shop type flag = `0x0005` (set before calling shop global) |
| `$2445` | — | ⚙️ | PRESELECT_ALCHEMY = Atlas `0x02` |
| `$2449` | — | ⚙️ | SAVE SPOT = `0x0004` (Nobilia inn) |
| `$2312` | — | ⚙️ | Some counter gating Atlas step-on (must be `< 3`) |

## Enter Script Summary

1. If `!IN_ANIMATION`: teleport both to `(0x0d, 0x3b)`, fade-out; else clear in-animation.
2. Set camera bounds: if `$22ec&0x40` → upper room `(X:0x0010–0x02d0, Y:0x0000–0x00e0)`; else → lower room `(X:0x0000–0x0120, Y:0x0120–0x0210)`.
3. Play music `0x42`; load NPC `0x20` at `(0x0a, 0x10)` → `$2455`; write `$23bf = 0x0001`.
4. Clear `$22ee&0x01`.
5. Dog unavailable → hide at `(1,5)`, global `0x36`, disable; else → cinematic `0x92de75`.
6. If `!$2258&0x02` (Atlas not yet taught): SET OBJ 0 STATE = 1 (load atlas merchant bed object); yield; load NPC `0x46` at `(0x44, 0x0a)` → `$2838`; walk NPC to `(0x57, 0x0b)`; sleep 59; unload OBJ 0; wait for NPC.

## Step-ons (Exits)

| Tile | Dest | Notes |
|------|------|-------|
| `[07,0f:0a,10]` | [0x0a] Market @ `[0x02d0\|0x0390]` | Walk by `(0,3)`; `$22eb\|=0x40`; global `0x2e` |
| `[06,22:09,23]` | [0x0a] Market @ `[0x02e0\|0x01b0]` | Walk by `(0,3)`; `$22eb\|=0x40`; global `0x2e` |
| `[29,0f:2c,10]` | [0x08] Square @ `[0x0040\|0x02c0]` | Walk by `(0,3)`; `$22eb\|=0x40`; global `0x2e` |
| `[2c,07:2d,08]` | **Atlas merchant** | See B-trigger section below (step-on that acts as B-trigger) |

## B-Triggers

| Tile | Flag | Description |
|------|------|-------------|
| `[05,0b:08,0c]` | — | Warehouse merchant (NPC in area): dog→*"You're the Sacred Dog! Pleasure to have you in my warehouse emporium."*; boy→`$2457=5`, if `!$22ed&0x20` → set flag + *"Hello, Buddy. Welcome to my warehouse emporium..."* full greeting + global `0x53` (shop); else → global `0x53` |
| `[03,1d:07,1e]` | — | Innkeeper: dog→*"You should take a nap. You look tired."*; boy → inn menu (see below) |

**Innkeeper menu (boy only):**
- *"Hello, Matey. Welcome to my inn. Please stay and rest. It's only 30 jewels."*
- YES + enough jewels: take 30 Jewels, walk boy+dog to beds, sleep 329 ticks, full heal boy+dog (`0x03e7`), fade music to `0x50` (sleep music) and back to `0x42`, *"I hope you had a good night's rest."* → SAVE SPOT `0x0004`; actual save dialog.
- YES + not enough jewels: global `0x50` (not-enough-money); if `$240d != 0` → *"You can exchange other currencies for jewels at any shop."*
- NO: SAVE SPOT `0x0004`; actual save dialog.
- Dog: *"You should take a nap."* → save dialog.

**Atlas merchant step-on `[2c,07:2d,08]`:**

Only fires if: entity is boy AND (`$2312 < 3` OR `!$2258&0x02`).

- Stop boy; if dog available, stop dog and walk to `(0x51, 0x13)`; face boy east; yield.
- Walk boy back toward wall (45 steps if Atlas taught, 49 steps otherwise).
- Load NPC `0x4e` at `(0x57, 0x0b)` → `$2836` with talk script `0x0222`; walk NPC west by `(-3, 0)`.
- **First time** (`!$2258&0x02`): `$2258|=0x02`; dialogue:
  - Merchant: *"What's the meaning of this? Why do you disturb my rest?"*
  - Boy: *"I, I'm sorry, I didn't know."*
  - Merchant: *"You're a skinny little guy, aren't you? You need meat on your bones. You need brute strength! I've got just the thing for you! The power of Atlas!"*
  - Show Atlas alchemy screen (`$2445=0x02`); *"Of course, in order to use this Atlas Formula, you'll need an Atlas Medallion."*; call hidden medallion sale sub `0x95e8a1`.
- **Repeat**: *"Oh, it's you! Have you come back for an Atlas Medallion?"*; call hidden medallion sale.

## NPCs

| Ref | NPC# | Pos | Notes |
|-----|------|-----|-------|
| `$2455` | `0x20` | `(0x0a, 0x10)` | Generic background NPC; loaded every enter |
| `$2836` | `0x4e` | `(0x57, 0x0b)` | Atlas merchant; only spawned by Atlas step-on |

## Notes

- `$22ec&0x40` (camera area flag) is set by the exits when leaving to Market or
  Square, so re-entering the inn routes the camera to the correct area.
- The Atlas merchant (sub `0x95e8a1` "hidden medallion sale") is the only place in
  act 2 to buy Atlas Medallions; the alchemy spell itself is taught here for free.
- `$2312 < 3` acts as an early-game gate; once this counter reaches 3 the Atlas
  step-on no longer auto-triggers the merchant encounter.
- Inn save spot index `0x0004` = Nobilia inn (one of the four act 2 save points).
