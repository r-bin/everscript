# 0x37 — Gothica: Gomi's Tower

| Field | Value |
|-------|-------|
| Room ID | 0x37 |
| Act | Gothica (Act 3) |
| Data | `0x9dbcf3` |
| Enter script ptr | `0x92812e` |
| Enter script addr | `0x99a6c5` |
| Step-ons | 12 |
| B-triggers | 22 |
| Music | MUSIC.WIND_AMBIENT_BIRDS (0x68) normal / MUSIC.BOSS (0x24) Sterling fight |
| Dog sprite | Poodle (0x08) |

---

## Overview

Tall tower dungeon with multiple vertical floors navigated by two elevator
step-on triggers. Contains ENEMY::STERLING (NPC 0x44) as a mini-boss — if not
defeated, he ambushes the player near the top; after defeat, the Gomi
introduction cutscene plays (`0x9997a7`).

The room has 22 B-triggers: **18 sniff spots** (OBJs 11–28, spanning SRAM bytes
`$22d5–$22d7`) and **4 gourds** (OBJs 0, 2, 8, 9, spanning `$2273–$2274`).

Four **session-local puzzle counters** (`$2835–$283b`) control water-level /
platform sub-puzzles in the tower. These reset each visit (all zeroed on enter).

Contains a **credits sequence** path (if `$22f2&0x01`): plays an animated
credit scroll and calls CALL "Credits" (0x5a).

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-ons | 12 |
| B-triggers | 22 |
| Gourds | 4 |
| Sniff spots | 18 |
| Enemies | ENEMY::DRAKE_GREEN (0x89) × 12 + ENEMY::MAGGOT_RED (0x77) × 17 |
| NPCs | ENEMY::STERLING (0x44) × 1 (conditional) |

**Enemy Drop Table**:

| Slot | Item | Rate |
|------|------|------|
| 1 | 🧪 Honey (0x0802) | 100 |
| 2 | 🧪 Call Beads (0x0807) | 1 |
| 3 | 💰 Currency (0x0001) qty 125 | 30 |

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$2273` | 0x40 | 🫙 Gourd OBJ 0 looted — Ethanol [0x37] (MAP REF 0x0000) |
| `$2273` | 0x80 | 🫙 Gourd OBJ 2 looted — Ash [0x37] (MAP REF 0x0002) |
| `$2274` | 0x01 | 🫙 Gourd OBJ 8 looted — Acorns [0x37] (MAP REF 0x0008) |
| `$2274` | 0x02 | 🫙 Gourd OBJ 9 looted — Feather [0x37] (MAP REF 0x0009) |
| `$22d5` | 0x10 | 👃 Sniffed Ethanol in Gomi's Tower (#11) [0x37] (MAP REF 0x000b) |
| `$22d5` | 0x20 | 👃 Sniffed Ethanol in Gomi's Tower (#12) [0x37] (MAP REF 0x000c) |
| `$22d5` | 0x40 | 👃 Sniffed Ethanol in Gomi's Tower (#13) [0x37] (MAP REF 0x000d) |
| `$22d5` | 0x80 | 👃 Sniffed Ash in Gomi's Tower (#14) [0x37] (MAP REF 0x000e) |
| `$22d6` | 0x01 | 👃 Sniffed Ash in Gomi's Tower (#15) [0x37] (MAP REF 0x000f) |
| `$22d6` | 0x02 | 👃 Sniffed Iron in Gomi's Tower (#16) [0x37] (MAP REF 0x0010) |
| `$22d6` | 0x04 | 👃 Sniffed Iron in Gomi's Tower (#17) [0x37] (MAP REF 0x0011) |
| `$22d6` | 0x08 | 👃 Sniffed Feather in Gomi's Tower (#18) [0x37] (MAP REF 0x0012) |
| `$22d6` | 0x10 | 👃 Sniffed Feather in Gomi's Tower (#19) [0x37] (MAP REF 0x0013) |
| `$22d6` | 0x20 | 👃 Sniffed Feather in Gomi's Tower (#20) [0x37] (MAP REF 0x0014) |
| `$22d6` | 0x40 | 👃 Sniffed Roots in Gomi's Tower (#21) [0x37] (MAP REF 0x0015) |
| `$22d6` | 0x80 | 👃 Sniffed Roots in Gomi's Tower (#22) [0x37] (MAP REF 0x0016) |
| `$22d7` | 0x01 | 👃 Sniffed Mushroom in Gomi's Tower (#23) [0x37] (MAP REF 0x0017) |
| `$22d7` | 0x02 | 👃 Sniffed Mushroom in Gomi's Tower (#24) [0x37] (MAP REF 0x0018) |
| `$22d7` | 0x04 | 👃 Sniffed Acorns in Gomi's Tower (#25) [0x37] (MAP REF 0x0019) |
| `$22d7` | 0x08 | 👃 Sniffed Acorns in Gomi's Tower (#26) [0x37] (MAP REF 0x001a) |
| `$22d7` | 0x10 | 👃 Sniffed Water in Gomi's Tower (#27) [0x37] (MAP REF 0x001b) |
| `$22d7` | 0x20 | 👃 Sniffed Water in Gomi's Tower (#28) [0x37] (MAP REF 0x001c) |
| `$22dd` | 0x02 | 📖 Sterling dead [multi-room] — gates Sterling NPC spawn |
| `$22f2` | 0x01 | 📖 In credits [multi-room] — gates credits sequence on enter |
| `$22eb` | 0x20 | ⚙️ Animation-skip guard (standard pattern) |
| `$2443` | — | 🐶 Dog sprite = Poodle (0x08) |
| `$238d` | — | 🎵 CHANGE MUSIC register |
| `$23bf` | — | ⚙️ Cleared to 0 on enter |
| `$2834` | — | ⚙️ Puzzle counter guard (set 0x01 when Sterling encounter fires; session-local) |
| `$2835` | — | ⚙️ Puzzle counter A (session-local) |
| `$2837` | — | ⚙️ Puzzle counter B (session-local) |
| `$2839` | — | ⚙️ Puzzle counter C (session-local) |
| `$283b` | — | ⚙️ Puzzle counter D (session-local) |
| `$283d` | — | ⚙️ Sterling entity pointer (session-local) |

---

## Enter Script Summary (`0x99a6c5`)

1. **Animation guard**: if NOT `$22eb&0x20` → teleport both to [0x13,0xf1]; fade-out music.
2. If `$22f2&0x01` (**credits path**): RCALL `0x99a604` — animated credit scroll
   (loads NPC 0x20 prop + NPC 0x81 + NPC 0x58, scrolls from x=0xc4 to x=0x3e8,
   calls "Credits" global script 0x5a); END.
3. Set Poodle (`$2443=0x08`); `$0ea2+8=0x01, $0eac+8=0x17a0`.
4. Clear puzzle counters: `$2835=$2837=$2839=$283b=0`.
5. Reset OBJs 5,6,7,3,4,1 → state 0 (all visible/active each visit).
6. **Gourd unloads**: OBJ 0 if `$2273&0x40`; OBJ 2 if `$2273&0x80`;
   OBJ 8 if `$2274&0x01`; OBJ 9 if `$2274&0x02`.
7. **Sniff OBJ unloads**: OBJ 11 if `$22d5&0x10` … OBJ 28 if `$22d7&0x20`
   (18 conditional unloads; OBJs 11–28 correspond to sniff spots #11–#28).
8. Drop table: PRIZE1=0x0802 rate 100; PRIZE2=0x0807 rate 1; PRIZE3=0x0001
   qty 125 rate 30.
9. If NOT `$22dd&0x02`: load STERLING (0x44) at [0x2b,0x1d], `$283d=entity`,
   set script "Sterling" (0x1a52).
10. RCALL `0x99a377` ("Gomi's tower part [2]"): DRAKE_GREEN (0x89) × 12 spawners;
    MAGGOT_RED (0x77) × 17 spawners.
11. Music WIND_AMBIENT_BIRDS (0x68); `$23bf=0`; CALL `0x92de75`; END.

---

## Step-on Scripts (12 entries)

### Elevator Rides

| # | Tile | Description |
|---|------|-------------|
| 1 | [21,67:23,68] | **Elevator descend** (bottom → top): scroll teleport from pixel y=0x0648 down to y=0x01f8; OBJ 1 (door marker) shown/hidden during transit |
| 2 | [21,27:23,28] | **Elevator ascend** (top → bottom): scroll teleport from pixel y=0x0248 up to y=0x0648; OBJ 4 (door marker) shown/hidden during transit |

### Sterling Encounter

| # | Tile | Description |
|---|------|-------------|
| 3 | [2b,10:2d,11] | **Sterling ambush**: if NOT (`$2834&0x01` OR `$22dd&0x02`): walk toward [0x50,0x1e], face west, reveal OBJ 10, fade music, play MUSIC.BOSS (0x24), CALL `0x9997a7` ("Sterling battle over, Gomi introduction"), screen shake; set `$2834\|=0x01` |

### Tower Puzzles (water-level counters)

| # | Tile | Counter | Session OBJ revealed | Description |
|---|------|---------|----------------------|-------------|
| 4 & 5 | [18,2f] [17,2f] | `$283b` +1 | OBJ 3 when `$283b==1` | Puzzle D trigger; calls `0x999d96` + `0x999d1f` when `$283b>1` |
| 6 & 7 | [0f,55] [0e,55] | `$2839` +1 | OBJ 7 when `$2839==2` | Puzzle C trigger |
| 8 & 9 | [20,4f] | `$2837` +1 | OBJ 6 when `$2837==1` | Puzzle B trigger |
| 10 & 11 | [30,5e] [2f,5e] | `$2835` +1 | OBJ 5 when `$2835==1` | Puzzle A trigger |

### Exit

| # | Tile | Description |
|---|------|-------------|
| 12 | [2a,7b:32,7d] | **Exit south → 0x40** Swamp |

---

## B-triggers (22 entries)

### Sniff Spots (B#1–18)

| B# | Tile | Flag | Item | MAP REF | NEXT_ADD |
|----|------|------|------|---------|----------|
| 1 | [0d,65:0e,66] | `$22d7&0x20` | 👃 Water (#28) | 0x001c | 2 |
| 2 | [32,5e:33,5f] | `$22d7&0x10` | 👃 Water (#27) | 0x001b | 4 |
| 3 | [32,65:33,66] | `$22d7&0x08` | 👃 Acorns (#26) | 0x001a | 2 |
| 4 | [0e,33:0f,34] | `$22d7&0x04` | 👃 Acorns (#25) | 0x0019 | 1 |
| 5 | [1d,55:1e,56] | `$22d7&0x02` | 👃 Mushroom (#24) | 0x0018 | 3 |
| 6 | [2b,76:2c,77] | `$22d7&0x01` | 👃 Mushroom (#23) | 0x0017 | 1 |
| 7 | [25,7c:26,7d] | `$22d6&0x80` | 👃 Roots (#22) | 0x0016 | — |
| 8 | [08,78:09,79] | `$22d6&0x40` | 👃 Roots (#21) | 0x0015 | 2 |
| 9 | [19,75:1a,76] | `$22d6&0x20` | 👃 Feather (#20) | 0x0014 | 2 |
| 10 | [20,3e:21,3f] | `$22d6&0x10` | 👃 Feather (#19) | 0x0013 | 3 |
| 11 | [23,13:24,14] | `$22d6&0x08` | 👃 Feather (#18) | 0x0012 | 1 |
| 12 | [12,29:13,2a] | `$22d6&0x04` | 👃 Iron (#17) | 0x0011 | — |
| 13 | [33,25:34,26] | `$22d6&0x02` | 👃 Iron (#16) | 0x0010 | 2 |
| 14 | [37,44:38,45] | `$22d6&0x01` | 👃 Ash (#15) | 0x000f | 2 |
| 15 | [0e,4b:0f,4c] | `$22d5&0x80` | 👃 Ash (#14) | 0x000e | 1 |
| 16 | [0c,6b:0d,6c] | `$22d5&0x40` | 👃 Ethanol (#13) | 0x000d | 2 |
| 17 | [35,54:36,55] | `$22d5&0x20` | 👃 Ethanol (#12) | 0x000c | 2 |
| 18 | [25,1b:26,1c] | `$22d5&0x10` | 👃 Ethanol (#11) | 0x000b | 1 |

### Gourds (B#19–22)

| B# | Tile | Flag | Item | MAP REF |
|----|------|------|------|---------|
| 19 | [10,26:12,27] | `$2274&0x02` | 🫙 Feather | 0x0009 |
| 20 | [35,4e:37,4f] | `$2274&0x01` | 🫙 Acorns | 0x0008 |
| 21 | [1f,46:21,47] | `$2273&0x80` | 🫙 Ash | 0x0002 |
| 22 | [33,46:35,47] | `$2273&0x40` | 🫙 Ethanol | 0x0000 |

---

## Objects

| OBJ | Persistence | Notes |
|-----|-------------|-------|
| OBJ 0 | `$2273&0x40` | 🫙 Ethanol gourd |
| OBJ 1 | — (reset each visit) | Elevator door marker (lower floor) |
| OBJ 2 | `$2273&0x80` | 🫙 Ash gourd |
| OBJ 3 | — (reset each visit) | Puzzle D prop (revealed by puzzle counter `$283b`) |
| OBJ 4 | — (reset each visit) | Elevator door marker (upper floor) |
| OBJ 5 | — (reset each visit) | Puzzle A prop (revealed by `$2835`) |
| OBJ 6 | — (reset each visit) | Puzzle B prop (revealed by `$2837`) |
| OBJ 7 | — (reset each visit) | Puzzle C prop (revealed by `$2839`) |
| OBJ 8 | `$2274&0x01` | 🫙 Acorns gourd |
| OBJ 9 | `$2274&0x02` | 🫙 Feather gourd |
| OBJ 10 | — (session-local) | Revealed during Sterling encounter |
| OBJs 11–28 | `$22d5&0x10` … `$22d7&0x20` | 👃 Sniff spot OBJs #11–#28 |

---

## Enemies

| NPC ID | ENEMY name | Count | Notes |
|--------|-----------|-------|-------|
| 0x89 | DRAKE_GREEN ("Dragoil") | 12 spawners | `$2433=0x0002` |
| 0x77 | MAGGOT_RED ("Gore Grub") | 17 spawners | `$2433=0x0002` |
| 0x44 | STERLING | 1 fixed | Conditional on NOT `$22dd&0x02`; at [0x2b,0x1d] |

---

## Notes

- **Sterling encounter** fires once per playthrough (guarded by `$2834&0x01`
  session-local + `$22dd&0x02` SRAM). After battle, `0x9997a7` ("Sterling battle
  over, Gomi introduction") plays a cutscene introducing Gomi. `// TODO: read 0x9997a7`.
- **Puzzle counters** (`$2835/$2837/$2839/$283b`) are WRAM-only and reset to 0
  on every room entry. The water-level puzzle subs `0x999d96` and `0x999d1f`
  handle the actual platform animation. `// TODO: read those subs`.
- **Credits path** (`$22f2&0x01`) triggers on the very last visit before credits;
  the screen scroll uses NPC 0x81 (NPC 0x102>>1) and NPC 0x58 (NPC 0x0b0>>1)
  as prop elements. `// TODO: look up ENEMY 0x81 and 0x58`.
- **Gourd MAP REFs** 0x0000 and 0x0002 are at the very bottom of the global MAP REF
  space. These may conflict with MAP REF 0 or 2 in other rooms using overlapping
  persistence bytes — check memory map for `$2273&0x40` and `$2273&0x80`.
