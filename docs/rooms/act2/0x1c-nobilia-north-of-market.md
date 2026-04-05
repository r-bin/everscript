# 0x1c — Nobilia, North of Market

| Field | Value |
|-------|-------|
| **ROM addr** | `0x9ffe57` |
| **Data addr** | `0xa7e153` |
| **Enter script** | `0x9280a7` → `0x95ca73` |
| **Step-on table** | `0xa7e162` len=`0x0024` (6 entries) |
| **B-trigger table** | `0xa7e188` len=`0x0078` (20 entries) |
| **Music** | `0x2e` (normal) / `0x40` (market timer expired) |
| **Act** | Act 2 — Antiqua |

## Overview

The upper district of Nobilia, north of the main market. Contains 14 dog sniff
spots (Water ×3, Oil ×2, Crystal ×2, Clay ×3, Vinegar ×3, Atlas Medallion ×1),
a locked gate to the desert beyond, gate guards, and a chicken-feed NPC. After
the spy cutscene in 0x4d, the player enters here with a walk-in monologue about
Diamond Eyes and the town across the desert.

The Atlas Medallion sniff (`$22b8&0x01`) is the only sniff in act 2 that yields
a key item rather than an ingredient.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22b6` | `0x08` | 👃 | Sniffed Water in Nobilia, North of Market (#1) [0x1c] (0x08) |
| `$22b6` | `0x10` | 👃 | Sniffed Water in Nobilia, North of Market (#2) [0x1c] (0x10) |
| `$22b6` | `0x20` | 👃 | Sniffed Water in Nobilia, North of Market (#3) [0x1c] (0x20) |
| `$22b6` | `0x40` | 👃 | Sniffed Oil in Nobilia, North of Market (#4) [0x1c] (0x40) |
| `$22b6` | `0x80` | 👃 | Sniffed Oil in Nobilia, North of Market (#5) [0x1c] (0x80) |
| `$22b7` | `0x01` | 👃 | Sniffed Crystal in Nobilia, North of Market (#6) [0x1c] (0x01) |
| `$22b7` | `0x02` | 👃 | Sniffed Crystal in Nobilia, North of Market (#7) [0x1c] (0x02) |
| `$22b7` | `0x04` | 👃 | Sniffed Clay in Nobilia, North of Market (#8) [0x1c] (0x04) |
| `$22b7` | `0x08` | 👃 | Sniffed Clay in Nobilia, North of Market (#9) [0x1c] (0x08) |
| `$22b7` | `0x10` | 👃 | Sniffed Clay in Nobilia, North of Market (#10) [0x1c] (0x10) |
| `$22b7` | `0x20` | 👃 | Sniffed Vinegar in Nobilia, North of Market (#11) [0x1c] (0x20) |
| `$22b7` | `0x40` | 👃 | Sniffed Vinegar in Nobilia, North of Market (#12) [0x1c] (0x40) |
| `$22b7` | `0x80` | 👃 | Sniffed Vinegar in Nobilia, North of Market (#13) [0x1c] (0x80) |
| `$22b8` | `0x01` | 💎 | Sniffed Atlas Medallion in Nobilia, North of Market (#14) [0x1c] (0x01) |
| `$225f` | `0x20` | 📖 | Vigor defeated (unloads obj 0) |
| `$225d` | `0x08` | 📖 | Market timer expired (gates NPCs + changes music to `0x40`) |
| `$22d9` | `0x08` | 📖 | Gate guard condition flag (see NPCs section) |
| `$22df` | `0x08` | 📖 | Tiny NPC condition: load Tiny escort NPC if set [0x1c] |
| `$22df` | `0x10` | 📖 | Guard block flag: if set, suppresses guard-area NPCs [0x1c] |
| `$22ec` | `0x20` | 📖 | Entering from 0x4d spy cutscene (clears after walk-in monologue) |
| `$2843`/`$2845`/`$2847` | — | ⚙️ | Background NPC entity refs (session-local) |
| `$2835` | — | ⚙️ | Merchant NPC entity ref (session-local) |
| `$2839` | — | ⚙️ | Guard NPC entity ref (session-local) |
| `$2837` | — | ⚙️ | Tiny escort NPC entity ref (session-local) |

## Enter Script Summary

1. `CHANGE_DOGGO = Greyhound (0x06)`.
2. If `!IN_ANIMATION`: teleport both to `(0x4c, 0x33)`, fade-out; else clear in-animation.
3. Unload sniffed-spot objects: `$225f&0x20`→obj0; `$22b6&0x08`→obj1; `&0x10`→obj2; `&0x20`→obj3; `&0x40`→obj4; `&0x80`→obj5; `$22b7&0x01`→obj6; `&0x02`→obj7; `&0x04`→obj8; `&0x08`→obj9; `&0x10`→obj10; `&0x20`→obj11; `&0x40`→obj12; `&0x80`→obj13; `$22b8&0x01`→obj14.
4. If `!$225d&0x08` (market NOT expired): load ambient NPCs — NPC `0x18` at `(51,25)` → `$2843` (talk `0x18e4`); NPC `0x1b` at `(69,23)` → `$2845` (talk `0x18e7`); NPC `0x19` at `(29,19)` → `$2847` (talk `0x18ea`); NPC `0x1a` at `(4b,21)` → `$2835` face west (talk `0x18ed`).
   - If `!($22d9&0x08) && !($22df&0x10)`: load guard NPC `0x1e` at `(56,15)` → `$2839`.
   - If `$22df&0x08`: load NPC `0x46` at `(5a,15)` → `$2837`, script-controlled, face south (talk script "North of Market Tiny dialog `0x18f3`").
5. Set background NPC behavior (`0xea2`, `0xeac`).
6. Music: `0x40` if timer expired; else `0x2e`; fade-in.
7. Write `$23bf = 0x0001`; dog unavailable → hide + disable; else → cinematic.
8. If `$22ec&0x20` (from 0x4d spy cutscene): stop both, clear flag, walk both forward `(0,5)`/`(0,4)`, face each other, boy: *"It looks like we've got our work cut out for us, [name]. There's a town on the other side of the desert. We can cross the river there. Then, we can start searching for those diamonds."*; BOY+DOG = Player controlled.

## Exits

| Dest | Coords | Trigger |
|------|--------|---------|
| [0x0a] Nobilia Market | `[0x0078\|0x0040]` | Step-on `[02,1a:06,1c]` |
| [0x0a] Nobilia Market | `[0x0180\|0x0040]` | Step-on `[22,1a:29,1c]` |
| [0x0a] Nobilia Market | `[0x02a0\|0x0040]` | Step-on `[35,1a:3d,1c]` |
| — | — | Step-on `[1e,03:22,04]`: Locked gate (*"Locked!"*; walk forward 2) |

## B-Triggers

| Tile | Flag | Description |
|------|------|-------------|
| `[18,0f:1a,11]` | — | SFX `0x48` (chickens?) |
| `[19,11:1a,12]` | — | SFX `0x48` |
| `[1a,10:1b,11]` | — | SFX `0x48` |
| `[17,10:18,11]` | — | SFX `0x48` |
| `[18,0f:1a,11]` (0x42c) | — | *"Here you go! Have some chicken feed. It's delicious."* |
| `[1f,06:21,07]` + `[21,06:22,07]` + `[1e,06:1f,07]` | — | Gate guard (sub `0x95c53c`): face boy accordingly; call guard check |
| `[1f,15:21,16]` | `$22b6&0x08` | 👃 Sniffed Water (#1) [0x1c] (0x08); NEXT ADD `0x0001` |
| `[06,0e:08,0f]` | `$22b6&0x10` | 👃 Sniffed Water (#2) [0x1c] (0x10); NEXT ADD `0x0002` |
| `[37,11:38,13]` | `$22b6&0x20` | 👃 Sniffed Water (#3) [0x1c] (0x20) |
| `[29,08:2a,09]` | `$22b6&0x40` | 👃 Sniffed Oil (#4) [0x1c] (0x40); NEXT ADD `0x0002` |
| `[06,05:07,06]` | `$22b6&0x80` | 👃 Sniffed Oil (#5) [0x1c] (0x80); NEXT ADD `0x0001` |
| `[0f,10:10,11]` | `$22b7&0x01` | 👃 Sniffed Crystal (#6) [0x1c] (0x01); NEXT ADD `0x0002` |
| `[2f,13:30,14]` | `$22b7&0x02` | 👃 Sniffed Crystal (#7) [0x1c] (0x02); NEXT ADD `0x0003` |
| `[3e,05:3f,06]` | `$22b7&0x04` | 👃 Sniffed Clay (#8) [0x1c] (0x04); NEXT ADD `0x0001` |
| `[00,05:01,06]` | `$22b7&0x08` | 👃 Sniffed Clay (#9) [0x1c] (0x08); NEXT ADD `0x0002` |
| `[0c,1a:0d,1b]` | `$22b7&0x10` | 👃 Sniffed Clay (#10) [0x1c] (0x10) |
| `[3e,06:3f,07]` | `$22b7&0x20` | 👃 Sniffed Vinegar (#11) [0x1c] (0x20); NEXT ADD `0x0001` |
| `[0d,06:0e,07]` | `$22b7&0x40` | 👃 Sniffed Vinegar (#12) [0x1c] (0x40) |
| `[07,1b:08,1c]` + `[16,08:17,09]` | `$22b7&0x80` | 👃 Sniffed Vinegar (#13) [0x1c] (0x80); NEXT ADD `0x0003` |
| `[07,1b:08,1c]` (0x459) | `$22b8&0x01` | 💎 Sniffed Atlas Medallion (#14) [0x1c] (0x01) |

## NPCs

| Ref | NPC# | Pos | Notes |
|-----|------|-----|-------|
| `$2843` | `0x18` | `(0x51, 0x25)` | Ambient NPC; talk `0x18e4` |
| `$2845` | `0x1b` | `(0x69, 0x23)` | Ambient NPC; talk `0x18e7` |
| `$2847` | `0x19` | `(0x29, 0x19)` | Ambient NPC; talk `0x18ea` |
| `$2835` | `0x1a` | `(0x4b, 0x21)` | Merchant NPC; face west; talk `0x18ed` |
| `$2839` | `0x1e` | `(0x56, 0x15)` | Guard NPC (conditional: `!$22d9&0x08 && !$22df&0x10`) |
| `$2837` | `0x46` | `(0x5a, 0x15)` | Tiny escort NPC (conditional: `$22df&0x08`); talk "Tiny dialog `0x18f3`"; face south |

## Notes

- Tile `[07,1b:08,1c]` at the same location has two overlapping B-trigger entries
  (0x456 for `$22b7&0x80` Vinegar #13 and 0x459 for `$22b8&0x01` Atlas Medallion).
  Both can fire; each checks its own flag independently.
- All 14 sniff objects are persisted via dedicated bits across `$22b6–$22b8`;
  sniffed objects are unloaded on enter via the `IF flag THEN UNLOAD OBJ N` chain.
- `$22ec&0x20` is the walk-in monologue trigger set by 0x4d's spy cutscene exit
  to this room; cleared immediately after the dialogue plays.
- When the market timer expires (`$225d&0x08`), all ambient NPCs are removed and
  music changes to `0x40` (the tense/timer variant used in 0x08 Square).
- The locked gate at `[1e,03:22,04]` leads toward the Desert of Doom (0x1b); it
  requires an untracked condition to open (likely story progression to a certain point).
