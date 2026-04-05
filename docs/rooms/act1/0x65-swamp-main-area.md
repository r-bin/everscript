# 0x65 — Swamp (main area)

**ROM:** `0x9fff7b` | **Data:** `0x9d8000` | **Enter:** `0x928214` → `0x948fea`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x0c` |
| Map bounds | Very large (~0xb0 tiles tall × ~0xa0 wide, based on NPC spawn coords) |
| Objects | 0x00–0x3b (60 objects: sniff spots, gourds, swamp platforms) |
| NPCs | ~30+ (`0x21` spawners + `0x22` spawners + 7× `0x1e`) |
| Step-on zones | 29 |
| B-triggers | 34 (25 sniff spots with 2 duplicates + 7 gourds) |
| Sniff spots | 25 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| North | `0x01` Exterior of Blimp's Hut @ `[0x00e0\|0x0308]` | step-on `[52,00:56,02]` | outdoor → indoor (Global 0x26) |
| West | `0x66` West of swamp @ `[0x02f8\|0x01d0]` | step-on `[0b,57:0e,59]` | outdoor → outdoor; also sets `$22f2\|=0x02` |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22f2` | `0x02` | 📖 | Swamp leafpad activated (SET unconditionally when exiting west) |
| `$22b2` | `0x02` | 📖 | Swamp platform group A persistent (SE corner row) |
| `$22b2` | `0x04` | 📖 | Swamp platform group B persistent |
| `$22b2` | `0x08` | 📖 | Swamp platform group C persistent |
| `$22b2` | `0x10` | 📖 | Swamp platform group D persistent |
| `$22b2` | `0x20` | 📖 | Swamp platform group E persistent |
| `$22b2` | `0x40` | 📖 | Swamp platform group F persistent |
| `$228c` | `0x01` | 👃 | Sniffed Water (#2) |
| `$228c` | `0x02` | 👃 | Sniffed Water (#3) |
| `$228c` | `0x04` | 👃 | Sniffed Water (#5) |
| `$228c` | `0x08` | 👃 | Sniffed Water (#6) |
| `$228c` | `0x10` | 👃 | Sniffed Water (#7) |
| `$228c` | `0x20` | 👃 | Sniffed Water (#9) |
| `$228c` | `0x40` | 👃 | Sniffed Water (#10) |
| `$228c` | `0x80` | 👃 | Sniffed Water (#15) |
| `$228d` | `0x01` | 👃 | Sniffed Water (#16) |
| `$228d` | `0x02` | 👃 | Sniffed Water (#19) |
| `$228d` | `0x04` | 👃 | Sniffed Water (#20) |
| `$228d` | `0x08` | 👃 | Sniffed Water (#21) |
| `$228d` | `0x10` | 👃 | Sniffed Roots (#0) — also gated by `$2425==0x02` |
| `$228d` | `0x20` | 👃 | Sniffed Roots (#1) |
| `$228d` | `0x40` | 👃 | Sniffed Roots (#4) |
| `$228d` | `0x80` | 👃 | Sniffed Roots (#8) |
| `$228e` | `0x01` | 👃 | Sniffed Roots (#12) |
| `$228e` | `0x02` | 👃 | Sniffed Roots (#13) |
| `$228e` | `0x04` | 👃 | Sniffed Roots (#14) |
| `$228e` | `0x08` | 👃 | Sniffed Roots (#17) |
| `$228e` | `0x10` | 👃 | Sniffed Roots (#18) |
| `$228e` | `0x20` | 👃 | Sniffed Oil (#61) |
| `$228e` | `0x40` | 👃 | Sniffed Oil (#11) |
| `$228e` | `0x80` | 👃 | Sniffed Oil (#60) |
| `$228f` | `0x02` | 👃 | Sniffed Oil (#22) |
| `$2274` | `0x40` | 🫙 | Gourd obj 0x37 looted (Nectar) |
| `$2274` | `0x80` | 🫙 | Gourd obj 0x35 looted (Wax) |
| `$2275` | `0x01` | 🫙 | Gourd obj 0x36 looted (Biscuit) |
| `$2275` | `0x02` | 🫙 | Gourd obj 0x3b looted (Oil) |
| `$2275` | `0x04` | 🫙 | Gourd obj 0x3a looted (Call Beads) |
| `$2275` | `0x08` | 🫙 | Gourd obj 0x39 looted (Roots) — also sets `$2461=0x0001` |
| `$2275` | `0x10` | 🫙 | Gourd obj 0x38 looted (Clay) — also sets `$2461=0x0002` |

## NPCs / Enemies

| NPC ID | Count | Positions (examples) | State | Notes |
|--------|-------|----------------------|-------|-------|
| `0x21` | ~22 | Many spawners + 5 fixed w/ kill scripts | `0x0001` | Fixed NPC kill scripts: `0x17e5`, `0x17e8`, `0x17eb`, `0x17ee`, `0x17f1` |
| `0x22` | ~8 | Spawners throughout map | `0x0005` | Boss-tier enemy (same as 0x27, 0x69) |
| `0x1e` | 7 | `(2f,91)`,`(95,af)`,`(5d,47)`,`(21,31)`,`(41,4f)`,`(81,79)`,`(4d,77)` | `8400` | Quest NPC; alternates `$2433=0x000a`/`0x0008` |

## Drop Table

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| Prize 1 | Petal (`0x0800`) | 2 | 1 |
| Prize 2 | `0x0001` | 2 | 20 |
| Prize 3 | Oil (`0x0204`) | 1 | 1 |

## Enter Script Summary

1. Set engine hooks `$0eac+8=0x1791`, `$0eac+0=0x172b`; prize table.
2. If not re-entry: teleport both to `(0x0b, 0xb0)`.
3. Set `$23c1=0x0001`, `$23c5=0x0280`.
4. Unload per-sniff-spot objects (`$228c`, `$228d`, `$228e`, `$228f&0x02`, `$2274`, `$2275`).
5. If `$22b2&0x02`: load objs 0x20–0x35 at state 0x7e (reload whole platform group A).
6. Each `$22b2` bit `0x04`–`0x40` similarly restores its own group of platform objects.
7. Load NPC `0x21` spawners (`$2433=0x0001`), NPC `0x22` spawners (`$2433=0x0005`), and 7× NPC `0x1e` (alternating `$2433=0x000a`/`0x0008`).
8. Play music `0x0c`. Call cinematic entry. End.

## Swamp Platform Step-ons

There are 27 swamp platform step-on zones (plus 2 exits). Each tile activates a visual object (state 0x7e = risen/visible) with SFX `0x72`. Some tiles **also set a `$22b2` persistence flag** (the leading tile of each group); tiles within the same group that don't set a flag will reset on re-entry unless the group flag was already set by the leading tile.

| `$22b2` bit | Trigger zone | Objects activated | Notes |
|-------------|-------------|-------------------|-------|
| — | `[43,2e:44,2f]` | — | Dead zone (END only) |
| `0x40` | `[44,2e:45,2f]` | obj 0x30 | **Sets flag** |
| — | `[46,2e:47,2f]` | obj 0x2f | Non-flagged tile |
| — | `[4f,20:50,21]` | — | Dead zone |
| `0x20` | `[4d,20:4e,21]` | obj 0x2d | **Sets flag** |
| — | `[23,1d:25,1e]` | — | SFX only (no object) |
| `0x10` | `[23,1e:25,1f]` | obj 0x2b | **Sets flag** |
| `0x08` | `[15,4a:17,4b]` | obj 0x34 | **Sets flag** |
| — | `[15,49:17,4a]` | obj 0x29 | Non-flagged tile |
| — | `[15,48:17,49]` | obj 0x28 | Non-flagged tile |
| `0x04` | `[1e,53:20,54]` | obj 0x31 | **Sets flag** |
| — | `[1e,52:20,53]` | obj 0x26 | Non-flagged |
| — | `[1e,51:20,52]` | obj 0x25 | Non-flagged |
| — | `[3d,5b:3e,5c]` | — | Dead zone |
| `0x02` | `[3b,5b:3c,5c]` | obj 0x23 | **Sets flag** |
| — | `[39,5b:3a,5c]` | obj 0x22 | Non-flagged |
| — | `[37,5b:38,5c]` | obj 0x21 | Non-flagged |
| — | `[30,5b:31,5c]` | obj 0x20 | Non-flagged |
| — | `[2e,5b:2f,5c]` | obj 31 | Non-flagged |
| — | `[2c,5b:2d,5c]` | obj 30 | Non-flagged |
| — | `[2a,5b:2b,5c]` | obj 29 | Non-flagged |
| — | `[28,5b:29,5c]` | obj 28 | Non-flagged |
| — | `[26,5b:27,5c]` | obj 27 | Non-flagged |
| — | `[20,5b:21,5c]` | obj 26 | Non-flagged |
| — | `[1e,5b:1f,5c]` | obj 25 | Non-flagged |
| — | `[1c,5b:1d,5c]` | obj 24 | Non-flagged |
| — | `[1a,5b:1b,5c]` | obj 23 | Non-flagged |

## Gourds

| MAP REF | Zone | Contents | Flag |
|---------|------|----------|------|
| 0x0035 | `[50,58:52,5a]` | 🕯️ Wax | `$2274&0x80` |
| 0x0036 | `[2a,4d:2c,4f]` | 🍪 Biscuit | `$2275&0x01` |
| 0x0037 | `[12,4c:14,4e]` | 🧪 Nectar | `$2274&0x40` |
| 0x0038 | `[17,0b:19,0d]` | 🏺 Clay | `$2275&0x10` (also sets `$2461=0x0002`) |
| 0x0039 | `[1d,11:1f,13]` | 🌿 Roots | `$2275&0x08` (also sets `$2461=0x0001`) |
| 0x003a | `[46,18:48,1a]` | 📿 Call Beads | `$2275&0x04` |
| 0x003b | `[4f,37:51,39]` | 🛢️ Oil | `$2275&0x02` |

## Sniff Spots

25 unique spots (#0–#22, #60, #61); spots #5 and #60 each have 2 physical zones sharing the same flag.

| # | Zone | Ingredient | Flag | Notes |
|---|------|------------|------|-------|
| 0 | `[18,59:19,5b]` | 🌿 Roots | `$228d&0x10` | Also requires `$2425==0x02` — TODO: identify |
| 1 | `[39,56:3a,58]` | 🌿 Roots | `$228d&0x20` | |
| 2 | `[0f,4b:10,4d]` | 💧 Water | `$228c&0x01` | |
| 3 | `[12,4f:15,51]` | 💧 Water | `$228c&0x02` | |
| 4 | `[1c,4c:1d,4f]` | 🌿 Roots | `$228d&0x40` | |
| 5 | `[04,41:05,43]`, `[2c,4d:2e,50]` | 💧 Water | `$228c&0x04` | Dual-zone |
| 6 | `[2c,54:2e,55]` | 💧 Water | `$228c&0x08` | |
| 7 | `[53,5a:54,5c]` | 💧 Water | `$228c&0x10` | |
| 8 | `[4f,50:54,51]` | 🌿 Roots | `$228d&0x80` | |
| 9 | `[49,29:4a,2b]` | 💧 Water | `$228c&0x20` | |
| 10 | `[46,1e:4b,1f]` | 💧 Water | `$228c&0x40` | |
| 11 | `[55,20:56,22]` | 🛢️ Oil | `$228e&0x40` | |
| 12 | `[58,14:59,17]` | 🌿 Roots | `$228e&0x01` | |
| 13 | `[37,0c:39,0d]` | 🌿 Roots | `$228e&0x02` | |
| 14 | `[31,0e:34,0f]` | 🌿 Roots | `$228e&0x04` | |
| 15 | `[20,17:21,19]` | 💧 Water | `$228c&0x80` | |
| 16 | `[20,1a:21,1c]` | 💧 Water | `$228d&0x01` | |
| 17 | `[1a,0e:1b,10]` | 🌿 Roots | `$228e&0x08` | |
| 18 | `[10,19:11,1d]` | 🌿 Roots | `$228e&0x10` | |
| 19 | `[0d,34:0e,36]` | 💧 Water | `$228d&0x02` | |
| 20 | `[1c,39:1d,3c]` | 💧 Water | `$228d&0x04` | |
| 21 | `[15,46:1a,47]` | 💧 Water | `$228d&0x08` | |
| 22 | `[0d,3e:0e,40]` | 🛢️ Oil | `$228f&0x02` | |
| 60 | `[1d,11:1f,12]`, `[12,0f:13,11]` | 🛢️ Oil | `$228e&0x80` | Dual-zone; high MAP REF (non-sequential) |
| 61 | `[4f,40:50,41]` | 🛢️ Oil | `$228e&0x20` | High MAP REF (non-sequential) |

**Summary:** Water×12, Roots×9, Oil×4 = 25 sniff spots.

## Notes

- `$22b2` bits `0x02–0x40` persist swamp platform states across visits. Only the leading tile (with `$22b2 |= bit`) needs to be stepped on — the full group is restored on re-entry. Tiles without a corresponding flag are transient (activated only during the current visit).
- Two "dead zones" (`[43,2e:44,2f]`, `[4f,20:50,21]`) and one SFX-only zone (`[23,1d:25,1e]`) have no object or flag effect — likely boundary guards.
- **`$2425==0x02` guard on sniff #0** is unusual — only occurs in this room. `$2425` appears to be a character state or form register. TODO: identify.
- **Gourds 0x0038 and 0x0039 write `$2461`** after pickup: `0x0002` and `0x0001` respectively. This may be a quest tracker or inventory slot pointer. TODO: identify `$2461`.
- `$228f&0x04` is used in 0x66 (West of Swamp sniff #0 Water). The same `$228f` byte spans both 0x65 and 0x66: bit `0x02` is used here (#22 Oil), bit `0x04` is used in 0x66 (#0 Water). These share a persistence byte across room boundaries.
- The west exit step-on `[0b,57:0e,59]` unconditionally sets `$22f2|=0x02` (leafpad activated) before changing to 0x66. This ensures the leafpad entity is shown in 0x66 even if the player entered 0x65 from the north (skipping the leafpad trigger in 0x66).
- Spots #60 and #61 have non-sequential MAP REFs (0x003c, 0x003d) suggesting they may have been added late or are from a different region group.
- Music `0x0c` is shared with 0x66 (West of swamp) and 0x01 (Exterior of Blimp's Hut).
