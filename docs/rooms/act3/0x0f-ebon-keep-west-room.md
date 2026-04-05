# [0x0f] Gothica — Ebon Keep West Room (Naris)

| Field | Value |
|-------|-------|
| Room ID | 0x0f |
| Name | Gothica - Ebon Keep West Room (Naris) |
| Act | Act 3 — Gothica |
| Data offset | `0xaac915` |
| Enter script | `0x928066` → `0x9abc62` |
| Step-ons | 2 |
| B-triggers | 2 |
| Music | 0x6e |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 2 |
| Gourds | 2 |
| Sniff spots | 0 |
| Enemies | NPC 0x42 spawner × 13; NPC 0x1e × 2 |
| NPCs | Naris at `[65,4f]` (NPC type depends on `$22f5&0x40`) — talk `0x1ad3`; sprite 0x0040 |
| Forced dog form | — |
| Music | 0x6e |

**Drop table**:

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| 1 | 🧪 Honey (0x0802) | 10/14 | 1 |
| 2 | 💰 Currency (0x0001) | 3/14 | 0x4b (75) |
| 3 | ⚗️ Item 0x020d | 1/14 | 1 |

> // TODO: identify item 0x020d in drop table

---

## Overview

A large interior room in Ebon Keep, west of the chessboard, containing Naris and enemy spawners. Naris has two sprite variants based on the `$22f5&0x40` age flag — the flag is toggled on each entry (NPC 0x55 = older Naris, NPC 0x51 = younger Naris). Two gourds are accessible via B-triggers: one contains Oil and the other contains Money. West exit leads to the Chessboard (0x19); east exit leads to the Dining Room (0x0e).

---

## Enter Script Logic

1. `$22eb&0x20` guard: teleport both to `[3f,29]`, fade-out
2. Drop table: Prize1=Honey(0x0802)/10, Prize2=Currency(0x0001)/3/0x4b, Prize3=0x020d/1
3. Naris NPC load:
   - If `$22f5&0x40` (age flag set): load NPC 0xaa>>1=0x55 at `[65,4f]`; set `$22f5|=0x80`
   - Else: load NPC 0xa2>>1=0x51 at `[65,4f]`; clear `$22f5&0x80`
   - Toggle `$22f5&0x40`; set talk script: 0x1ad3, sprite 0x0040
4. If `$22dc&0x08` (WindWalker unlocked): `$2437 = 0x0007`
5. `$2433 = 0x0001`; 13× NPC 0x42 spawners; `$2433 = 0x000a`; 2× NPC 0x1e at `[11,21]` and `[73,35]`
6. If `$2287&0x80`: unload OBJ 7 (gourd 1 looted)
   If `$2288&0x01`: unload OBJ 3 (gourd 2 looted)
7. Music 0x6e if `$238d == 0x00`
8. `$23bf = 0x0000`; cinematic script

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[21,30:24,34]` | MAP 0x19 @ `[0x0498\|0x0210]` | West → Chessboard (global 0x19) |
| `[59,31:5c,34]` | MAP 0x0e @ `[0x0028\|0x0108]` | East → Ebon Keep Dining Room (global 0x1d) |

---

## B-Trigger Scripts (Gourds)

| Tile | Guard Flag | Contents | MAP REF | Notes |
|------|------------|----------|---------|-------|
| `[2c,23:2e,24]` | `$2287&0x80` | 🫙 Oil (0x0204) qty +4 | 0x0007 | Calls global gourd routine 0x3a; OBJ 7 unloaded on loot |
| `[29,41:2b,42]` | `$2288&0x01` | 🫙 Money (0x0001) qty 0x01f4 (500) | 0x0003 | Calls global gourd routine 0x3a; OBJ 3 unloaded on loot |

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22f5` | 0x40 | R/W | ⚙️ Naris age flag toggle — toggled on every entry; selects NPC type 0x55 (set) vs 0x51 (clear) |
| `$22f5` | 0x80 | W | ⚙️ Naris older-sprite loaded — set/cleared alongside 0x40 |
| `$22dc` | 0x08 | R | 📖 WindWalker unlocked |
| `$2287` | 0x80 | R/W | 🫙 Gourd Oil looted [0x0f] (0x80) — OBJ 7 unloaded if set |
| `$2288` | 0x01 | R/W | 🫙 Gourd Money looted [0x0f] (0x01) — OBJ 3 unloaded if set |
| `$23bf` | — | W | ⚙️ Set to 0x0000 on entry |
| `$2433` | — | W | ⚙️ Enemy spawn config (0x0001 then 0x000a) |
| `$2437` | — | W | ⚙️ Set to 0x0007 if WindWalker unlocked |

## Notes

- Naris alternates between an older and a younger sprite on every entry — a persistent age-toggle driven by `$22f5` bits `0x40` and `0x80`.
- One of the only two Ebon Keep interior rooms where enemies actively spawn (the other being 0x10); `$2433` is set twice on entry (0x0001, then 0x000a).
- Two gourds (Oil `$2287&0x80` and 500 Talons `$2288&0x01`) provide the main loot here.
