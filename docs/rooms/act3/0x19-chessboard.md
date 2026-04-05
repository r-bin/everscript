# [0x19] Gothica — Chessboard

| Field | Value |
|-------|-------|
| Room ID | 0x19 |
| Name | Gothica - Chessboard |
| Act | Act 3 — Gothica |
| Data offset | `0xa48000` |
| Enter script | `0x928098` → `0x99d8ae` |
| Step-ons | 5 |
| B-triggers | 19 |
| Music | 0x60 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 5 |
| B-triggers | 19 |
| Gourds | 0 |
| Sniff spots | 19 |
| Enemies | NPC 0x82 (chess piece enemy) × 23 spawners |
| NPCs | OBJ 0 = Footknight (0x92), OBJ 1 = Prof. Callbeads NPC, OBJ 4/5 = castle blocks |
| Forced dog form | — (unchanged; Knight Basher set in showcase mode only) |
| Music | 0x60 |

**Drop table**:

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| 1 | 🧪 Honey (0x0802) | 10/50 | 1 |
| 2 | 💰 Currency (0x0001) | 3/50 | 0x96 (150) |
| 3 | 🧪 Medicine (0x0806) | 1/50 | 1 |

---

## Overview

The large outdoor chessboard between Ebon Keep (west, 0x0f) and Ivor Tower (east, 0x70). Two holes in the floor drop the player to 0x1a (Below Chessboard). The Footknight boss spawns on a step-on at `[1e,23:1f,25]` if `$22e6&0x01` is not set. OBJ 4 vs OBJ 5 loads as the castle block depending on `$22dd&0x40` (west vs east castle orientation). Sniff spots #6–#24 populate the board with mushrooms, acorns, feathers, iron, brimstone, roots, ash, and water.

If `$22f9&0x10` (Second half of lab cutscene to be played): fades out and transitions to Omnitopia professor's lab (0x46). This path is triggered by a prior story event.

---

## Enter Script Logic

1. If `$22eb&0x20` (in animation): teleport both to `[0f,45]`, fade-out, clear flag
2. Unload chess piece objects based on kill flags:
   - OBJ 6–13 from `$22ca` bits 0x01–0x80 (8 entries)
   - OBJ 14–21 from `$22cb` bits 0x01–0x80 (8 entries)
   - OBJ 22–24 from `$22cc` bits 0x01–0x04 (3 entries)
3. Set up OBJ for physics/tile data (`$0ea2+0 = 0x40`, `$0eac+0 = 0x172b`)
4. Drop table: Prize1=Honey(0x0802)/10, Prize2=Currency(0x0001)/3/0x96, Prize3=Medicine(0x0806)/1
5. `$2433 = 0x0001`; 23× NPC 0x82 spawners placed across the board
6. Music 0x60 if `$238d == 0x00`
7. If `$22dc&0x08` (WindWalker unlocked): skip castle OBJ load
   - Else if `$22dd&0x40` (east castle): load OBJ 5
   - Else: load OBJ 4
8. `$23bf = 0x0000`
9. If NOT showcase: check Prof. Callbeads (`$225d&0x02`) and Footknight (`$22e6&0x01`) OBJ load/unload
10. If `$22f9&0x10` (second lab cutscene pending): RCALL → fade, CHANGE MAP 0x46 @ `[0x01a0|0x02c8]`
11. Otherwise: cinematic script

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[30,26:31,28]` | MAP 0x1a @ `[0x0218|0x0018]` | Chessboard hole (NW) — `$22eb|=0x20`, `$238f=0x0003` |
| `[1e,23:1f,25]` | Footknight spawn | If NOT `$22e6&0x01`: load NPC 0x92 (FOOTKNIGHT) at `[4b,45]` → `$2834` and begin boss encounter |
| `[06,20:08,24]` | MAP 0x70 @ `[0x0458|0x0140]` | West exit → Ivor Tower Exterior Bridges; clears `$22dd&0x40` |
| `[4e,20:50,24]` | MAP 0x0f @ `[0x0038|0x0140]` | East exit → Ebon Keep West Room (Naris); sets `$22dd|=0x40` |
| `[26,20:27,22]` | MAP 0x1a @ `[0x00a8|0x0028]` | Chessboard hole (SW) — `$22eb|=0x20`, `$238f=0x0003` |

---

## B-Trigger Scripts (Sniff Spots)

| Tile | Flag | Item | MAP REF | NEXT ADD |
|------|------|------|---------|----------|
| `[11,12:12,13]` | `$22ca&0x01` | 🌿 Mushroom (0x0206) (#6) | 0x0006 | +2 |
| `[45,27:46,28]` | `$22ca&0x02` | 🌿 Mushroom (0x0206) (#7) | 0x0007 | +3 |
| `[39,0c:3a,0d]` | `$22ca&0x04` | 🌿 Acorns (0x0215) (#8) | 0x0008 | +1 |
| `[35,34:36,35]` | `$22ca&0x08` | 🌿 Acorns (0x0215) (#9) | 0x0009 | +2 |
| `[13,2b:14,2c]` | `$22ca&0x10` | 🌿 Acorns (0x0215) (#10) | 0x000a | +3 |
| `[25,16:26,18]` | `$22ca&0x80` | 🌿 Feather (0x020c) (#11) | 0x000b | +2 |
| `[20,12:21,13]` | `$22ca&0x20` | 🌿 Iron (0x0209) (#12) | 0x000c | — |
| `[3b,29:3c,2a]` | `$22ca&0x40` | 🌿 Iron (0x0209) (#13) | 0x000d | +3 |
| `[18,38:19,39]` | `$22cb&0x01` | 🌿 Brimstone (0x0211) (#14) | 0x000e | +1 |
| `[37,18:38,19]` | `$22cb&0x02` | 🌿 Brimstone (0x0211) (#15) | 0x000f | +1 |
| `[2a,0c:2b,0d]` | `$22cb&0x04` | 🌿 Brimstone (0x0211) (#16) | 0x0010 | +3 |
| `[39,0f:3a,10]` | `$22cb&0x08` | 🌿 Roots (0x0203) (#17) | 0x0011 | +4 |
| `[37,37:38,38]` | `$22cb&0x10` | 🌿 Roots (0x0203) (#18) | 0x0012 | +3 |
| `[13,2e:14,2f]` | `$22cb&0x20` | 🌿 Roots (0x0203) (#19) | 0x0013 | +4 |
| `[49,18:4a,19]` | `$22cb&0x40` | 🌿 Roots (0x0203) (#20) | 0x0014 | +2 |
| `[2a,04:2b,05]` | `$22cb&0x80` | 🌿 Ash (0x0214) (#21) | 0x0015 | +3 |
| `[2a,2c:2b,2d]` | `$22cc&0x01` | 🌿 Ash (0x0214) (#22) | 0x0016 | +2 |
| `[21,1f:22,20]` | `$22cc&0x02` | 🌿 Water (0x0201) (#23) | 0x0017 | +1 |
| `[37,25:38,26]` | `$22cc&0x04` | 🌿 Water (0x0201) (#24) | 0x0018 | +3 |

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22ca` | 0x01 | R/W | 👃 Sniffed Mushroom in Chessboard (#6) [0x19] (0x01) |
| `$22ca` | 0x02 | R/W | 👃 Sniffed Mushroom in Chessboard (#7) [0x19] (0x02) |
| `$22ca` | 0x04 | R/W | 👃 Sniffed Acorns in Chessboard (#8) [0x19] (0x04) |
| `$22ca` | 0x08 | R/W | 👃 Sniffed Acorns in Chessboard (#9) [0x19] (0x08) |
| `$22ca` | 0x10 | R/W | 👃 Sniffed Acorns in Chessboard (#10) [0x19] (0x10) |
| `$22ca` | 0x20 | R/W | 👃 Sniffed Iron in Chessboard (#12) [0x19] (0x20) |
| `$22ca` | 0x40 | R/W | 👃 Sniffed Iron in Chessboard (#13) [0x19] (0x40) |
| `$22ca` | 0x80 | R/W | 👃 Sniffed Feather in Chessboard (#11) [0x19] (0x80) |
| `$22cb` | 0x01 | R/W | 👃 Sniffed Brimstone in Chessboard (#14) [0x19] (0x01) |
| `$22cb` | 0x02 | R/W | 👃 Sniffed Brimstone in Chessboard (#15) [0x19] (0x02) |
| `$22cb` | 0x04 | R/W | 👃 Sniffed Brimstone in Chessboard (#16) [0x19] (0x04) |
| `$22cb` | 0x08 | R/W | 👃 Sniffed Roots in Chessboard (#17) [0x19] (0x08) |
| `$22cb` | 0x10 | R/W | 👃 Sniffed Roots in Chessboard (#18) [0x19] (0x10) |
| `$22cb` | 0x20 | R/W | 👃 Sniffed Roots in Chessboard (#19) [0x19] (0x20) |
| `$22cb` | 0x40 | R/W | 👃 Sniffed Roots in Chessboard (#20) [0x19] (0x40) |
| `$22cb` | 0x80 | R/W | 👃 Sniffed Ash in Chessboard (#21) [0x19] (0x80) |
| `$22cc` | 0x01 | R/W | 👃 Sniffed Ash in Chessboard (#22) [0x19] (0x01) |
| `$22cc` | 0x02 | R/W | 👃 Sniffed Water in Chessboard (#23) [0x19] (0x02) |
| `$22cc` | 0x04 | R/W | 👃 Sniffed Water in Chessboard (#24) [0x19] (0x04) |
| `$22dc` | 0x08 | R | 📖 WindWalker unlocked — skips OBJ 4/5 load if set |
| `$22dd` | 0x40 | R/W | ⚙️ Load east castle — controls OBJ 4 vs OBJ 5 and exit destinations; SET on east exit step-on, CLEARED on west exit step-on |
| `$22e6` | 0x01 | R | 📖 Footknight defeated — if set, Footknight spawn step-on is skipped |
| `$225d` | 0x02 | R | 📖 Prof. Callbeads — OBJ 1 unloaded if this flag is set |
| `$22f9` | 0x10 | R | 📖 Second half of lab cutscene to be played — redirects to 0x46 |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$2433` | — | W | ⚙️ Set to 0x0001 for enemy spawners |
| `$23bf` | — | W | ⚙️ Set to 0x0000 on entry |
| `$2834` | — | W | ⚙️ Footknight NPC pointer (NPC 0x92 at `[4b,45]`) |

## Notes

- Contains 24 sniff spots across `$22c8`–`$22cc` — the densest ingredient collection in Act 3.
- `$22dd&0x40` (Load east castle) controls exit destinations and OBJ loading; it is set on the east exit step-on and cleared on the west exit step-on, bridging the Ebon Keep / Ivor Tower duality.
- If `$22f9&0x10` is set (act4 lab cutscene pending), entry routes immediately to room 0x46 (Omnitopia lab) — the flag that bridges the Act 3 → Act 4 transition passes through this room.
- Prof. Callbeads NPC (OBJ 1) is unloaded if `$225d&0x02` is already set (Camellia met).
