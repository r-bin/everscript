---
room: 0x2e
name: Antiqua – Blimp's Cave
act: act2
data: 0xadc8ba
---

# 0x2e — Antiqua – Blimp's Cave

| Field | Value |
|-------|-------|
| Room ID | 0x2e |
| Full Name | Antiqua – Blimp's Cave |
| Act | 2 (Antiqua) |
| Data block | 0xadc8ba |
| Enter script | 0x928101 → 0x95b329 |
| Step-on table | 0xadc8c9 (1 entry, 0x06 bytes) |
| B-trigger table | 0xadc8d1 (2 entries, 0x0c bytes) |

## Overview

A small cave room containing Blimp (NPC 0x17), reached either by falling through the pit-fall zone on [0x4f] East of Crustacia's upper plateau, or by walking in from the north passage. The room has a single exit north back to 0x4f, 2 gourds, and Blimp's extended first-meeting dialog.

Entry mode is determined by `$22ed&0x80` (pit-fall flag) and `$225f&0x01` (BLIMP_BRIDGE / "Blimp intro already seen").

Dog is set to Greyhound on entry. Music 0x26.

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$225f` | R/W | &0x01 | BLIMP_BRIDGE — if set, Blimp intro already shown; set during first-meeting pit-fall dialog; gates alternate dialog path |
| `$2273` | R/W | &0x08 | Gourd OBJ 0 (Wax) looted [0x2e]; enter unloads OBJ 0 if set |
| `$2273` | R/W | &0x10 | Gourd OBJ 1 (Ash) looted [0x2e]; enter unloads OBJ 1 if set |
| `$22eb` | R/W | &0x20 | IN_ANIMATION routing — teleport to [0x13, 0x17] + fade music if set; cleared otherwise |
| `$22ed` | R/W | &0x80 | Falling into a pit — set by pit-fall step-ons in [0x4f]; cleared in enter; triggers Blimp pit-fall dialog branch |
| `$2443` | write | =0x06 | CHANGE DOGGO to Greyhound on room entry |

## Enter Script Summary (`0x95b329`)

1. `CHANGE DOGGO = Greyhound (0x06)`.
2. If `$22eb&0x20`: teleport to [0x13, 0x17] + fade music; else clear flag.
3. Unload persistence: `$2273&0x08` → unload OBJ 0 (Wax gourd); `$2273&0x10` → unload OBJ 1 (Ash gourd).
4. Load NPC 0x17 (Blimp) at [0x11, 0x0f] → `$2455`; if `$225f&0x01` not set: make script-controlled, face west; set talk script 0x18bd.
5. Set camera scroll bounds: X 0x0010–0x0130, Y 0x0000–0x00e0.
6. Play music 0x26; `$23bf = 1`.

### Branch A — Pit-fall entry (`$22ed&0x80` set)
7. Clear `$22ed&0x80`; teleport boy to [0x13, 0x17] face west; teleport dog to [0x15, 0x19] face east (or hide if unavailable); teleport Blimp to [0x13, 0x0d] face east.
8. Fade in from black.
9. **Pit-fall dialog** (0x95b17e): Blimp: *"That was quite a fall! I hope that you're OK now, kid."* Boy: *"Thanks for pulling me/us out of that ditch, Blimp! I think I'll/we'll be all right."*
10. If `$225f&0x01` already set: restore control and return.
11. Else: set `$225f|=0x01`; Blimp: *"I'm glad to see you survived the big wash out."* → **Blimp dialog pt. 2** (0x95b2ca; body not captured — continues conversation; ends with control return).

### Branch B — Normal entry (no pit-fall)
7. If dog unavailable: teleport dog to [0x21, 0x2b], stop.
8. If `$225f&0x01` not set: **Blimp intro dialog** (0x95b26f): Blimp says *"Hello friend! Glad to see you survived the big wash out."* Boy: *"Likewise! My dog and I used your boat to float downstream and over the falls_"* → Blimp: *"Ahh! Well done! I escaped by floating down with swamp flowers full of the essence of Mud Pepper!"* → face exchanges → set `$225f|=0x01` → **Blimp dialog pt. 2** (0x95b2ca).
9. Call cinematic setup (0x92de75).

## Step-on Scripts (1 entry)

| Tile | Script | Description |
|------|--------|-------------|
| [09,0f:0c,10] | `0x95b174` | **EXIT north** → 0x4f East of Crustacia at [0x00a8, 0x00d0] |

## Exits

| Tiles | Destination | Coordinates | Notes |
|-------|-------------|-------------|-------|
| [09,0f:0c,10] | 0x4f — East of Crustacia | [0x00a8, 0x00d0] | step-on |
| (pit-fall) | 0x2e — self (entered from 0x4f) | — | player arrives via `$22ed&0x80` |

## B-Triggers (2 entries)

| Tile | Script | Contents | Flag |
|------|--------|----------|------|
| [0c,08:0e,0a] | `0x95b140` | 🫙 Gourd MAP REF 0x00 looted (Wax) | `$2273&0x08` |
| [0e,09:10,0b] | `0x95b15a` | 🫙 Gourd MAP REF 0x01 looted (Ash) | `$2273&0x10` |

## NPCs

| NPC | Qty | Spawn | Notes |
|-----|-----|-------|-------|
| NPC 0x17 (Blimp) | 1 | [0x11, 0x0f] | Talk script 0x18bd; script-controlled unless `$225f&0x01` set; repositioned during pit-fall entry; key story NPC for Blimp bridge mechanic |

## Notes

- **`$225f&0x01` = BLIMP_BRIDGE**: named constant in `core.evs`. Blimp's Cave is the room where this flag is first set. It gates subsequent re-introductions throughout the game.
- **Blimp dialog pt. 2** (`0x95b2ca`): not captured in this session — call sequence continues from both dialog branches. // TODO: read sub body for full dialog content.
- **Dog unavailable branching**: If `$2261&0x01` is set (dog missing), dialog uses "me" / "I'll" variants; otherwise "us" / "we'll". The dog is teleported to [0x21, 0x2b] and disabled when unavailable.
- **`$22e9&0x10`** (Killed robots with no ammo left) is tested during the **Crustacia intro** cutscene in 0x68 (not this room), but the branching begins in 0x68's script. No reference to `$22e9&0x10` in 0x2e.
- Music 0x26 (the cave/underground Antiqua theme, distinct from town 0x2c).
- Camera bounds tightly constrain the view: X 0x0010–0x0130, Y 0x0000–0x00e0 — this is a small room.
