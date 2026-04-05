# 0x7b — Ebon Keep + Ivor Tower Exterior (Bottom Half)

**Act:** 3 — Gothica  
**Script address:** `0x9fff97` (0x7b block)  
**Music:** `MUSIC.EBON_KEEP` (0x62) or `MUSIC.DRAGON_ROAR` (0x6a) — see Music Dispatch below  
**Dog sprite:** Poodle (0x08)

## Overview

Large dual-castle exterior area covering the lower half of both Ebon Keep (east) and Ivor Tower (west). This room functions as the Act 3 hub: it connects to the market square (0x4e), the southern gate area (0x76), four interior doors of both castles (→0x7d, `$234b` 1–4), and the dungeon entrance (→0x74). A permanent outdoor market operates here with seven interactive vendor stalls handling Perfume production, currency exchange, trading goods, and special items. Town NPCs load conditionally based on castle-state flags.

## Music Dispatch

```
if ($22dd & 0x40) == ($22dc & 0x08):   → no music change (inherited)
else if ($22dd & 0x40):                 → MUSIC.EBON_KEEP (0x62)
else if ($22dc & 0x08):                 → MUSIC.EBON_KEEP (0x62)
else:                                   → MUSIC.DRAGON_ROAR (0x6a)
```

`$22dd&0x40` = East castle (Ebon Keep) active  
`$22dc&0x08` = WindWalker unlocked

## Connections

| Direction | Tile range | Destination | Notes |
|-----------|-----------|-------------|-------|
| South | `[23,6b:27,6d]` | MAP 0x76 @ `[0x0160 \| 0x0048]` | South → Gate area |
| Market alley | `[17,5a:19,5e]` | MAP 0x4e — Ivor Tower West Alley | Market interior |
| North | `[26,3d:28,3f]` | MAP 0x7c @ `[0x0100 \| 0x03b8]` | North → Exterior top half |
| Dungeon | `[66,5c:67,5d]` | MAP 0x74 — Dungeon | `$234f` dispatch |
| Castle door (W) 1 | `[34,49:36,4a]` | MAP 0x7d @ `$234b=1` | Ivor Tower door 1 |
| Castle door (W) 2 | `[4d,49:4f,4a]` | MAP 0x7d @ `$234b=2` | Ivor Tower door 2 |
| Castle door (W) 3 | `[61,63:63,64]` | MAP 0x7d @ `$234b=3` | Ivor Tower door 3 |
| Castle door (E) | `[66,49:68,4a]` | MAP 0x7d @ `$234b=4` | Ebon Keep door |

### Dungeon (`$234f`) Dispatch

| `$234f` | Dungeon spawn point |
|---------|---------------------|
| 1 | Spawn A |
| 2 | Spawn B |
| 4 | Spawn C |
| 5 | Spawn D |
| 6 | Spawn E |
| 7 | Spawn F |

## Enter Script

1. Determine music via flag dispatch above; play if not already playing
2. If `$2437&0x0007` and west castle: clear to `$2437=0x0000`
3. If `$22eb&0x40` (step-out from interior): run door-open SFX + OBJ animation; clear flag
4. Load villager NPCs (0x52–0x56, ~11 total) **if** `($22dd&0x40) == ($22dc&0x08)` (castle state is "normal" — not mid-transition)
5. If `$22dd&0x40` (east castle): load east-castle OBJ set (market stalls, east-side wall dressings, 26 OBJs)
6. Else: load west-castle OBJ set

## Step-On Scripts

| Tile | Destination | `$234b` set | Notes |
|------|------------|-------------|-------|
| `[23,6b:27,6d]` | MAP 0x76 | — | South exit |
| `[17,5a:19,5e]` | MAP 0x4e | — | Market alley |
| `[26,3d:28,3f]` | MAP 0x7c | — | North |
| `[66,5c:67,5d]` | MAP 0x74 | via `$234f` | Dungeon (multiple spawns) |
| `[34,49:36,4a]` | MAP 0x7d | 1 | West castle door 1 |
| `[4d,49:4f,4a]` | MAP 0x7d | 2 | West castle door 2 |
| `[61,63:63,64]` | MAP 0x7d | 3 | West castle door 3 |
| `[66,49:68,4a]` | MAP 0x7d | 4 | East castle door |

## B-Trigger Scripts (Vendors / Trade)

### 1. Perfume Vendor — `[3d,66:40,67]`

Convert Spice → Perfume. Requires `$2529` (spice inventory).

| Option | Cost | Result |
|--------|------|--------|
| 1 jar | 2× Spice | 1× Perfume (`$2525+=1`) |
| 2 jars | 4× Spice | 2× Perfume |
| 3 jars | 6× Spice | 3× Perfume |

### 2. Currency Exchange — `[33,64:37,65]`

Calls global routine `0x55` (standard Gold ↔ currency exchange). Details determined by routine.

### 3. Thug's Cloak Trade — `[3b,5d:3e,5e]`

One-time trade. Requires: 8× Perfume (`$2525`) + 6× Beads (`$2519`).

- If `$2263&0x02` (already purchased): "You already have the cloak."
- Else: deduct items; set `$2263|=0x02` (Thug's Cloak flag); `$243d=0x0018`

### 4. Oracle Bone Trade — `[34,5d:37,5e]`

One-time trade. Requires: 1× Golden Jackal Statuette (`$251f`) + 1× Jeweled Scarab (`$2521`).

- If `$2262&0x10` (already purchased): "The oracle says you need nothing more."
- Else: deduct items; set `$2262|=0x10` (Oracle Bone received)

### 5. Ammo / Ticket Vendor — `[2d,5d:30,5e]`

**If `$22dc&0x08`** (WindWalker unlocked): sell Thunderball Shells (bazooka ammo).

| Option | Cost | Result |
|--------|------|--------|
| 5 shells | 50 gold | `$2437_ammo += 5` |
| 10 shells | 100 gold | `$2437_ammo += 10` |
| 15 shells | 150 gold | `$2437_ammo += 15` |

**Else** (WindWalker not yet unlocked): sell Exhibition Ticket (`TICKET_FOR_EXHIBITION`).

| Option | Cost | Result |
|--------|------|--------|
| 1 ticket | 1× Amulet of Annihilation (`$2517-=1`) | `$252f+=1` (`TICKET_FOR_EXHIBITION`) |

### 6. Spice Vendor — `[22,5d:25,5e]`

| Option | Cost | Result |
|--------|------|--------|
| 1 jar | 12 gold | `$2529+=1` (Spice) |
| 2 jars | 24 gold | `$2529+=2` |
| 3 jars | 36 gold | `$2529+=3` |

### 7. Beads Vendor — `[1f,5d:22,5e]`

| Option | Cost | Result |
|--------|------|--------|
| 1 | 15 gold | `$2519+=1` (Beads) |
| 2 | 30 gold | `$2519+=2` |
| 3 | 45 gold | `$2519+=3` |

## NPCs

Loaded when `($22dd&0x40) == ($22dc&0x08)` (non-transition castle state):

| NPC ID | Enum | Approx qty | Notes |
|--------|------|-----------|-------|
| 0x52 | `VILLAGER_3_3` | ~2 | — |
| 0x53 | `VILLAGER_3_4` | ~3 | — |
| 0x54 | `VILLAGER_3_5` | ~2 | — |
| 0x55 | `VILLAGER_3_5` | ~2 | — |
| 0x56 | `VILLAGER_3_6` | ~2 | — |

## Memory Access

| Address | Bit | Type | Name | Notes |
|---------|-----|------|------|-------|
| `$22dd` | `0x40` | 📖 | East castle (Ebon Keep) active | Major castle-state toggle |
| `$22dc` | `0x08` | 📖 | WindWalker unlocked | Ammo vendor vs. ticket vendor |
| `$22eb` | `0x40` | ⚙️ | Step-out from interior (door open SFX) | Transient |
| `$2263` | `0x02` | 💎 | Thug's Cloak purchased | One-time trade flag |
| `$2262` | `0x10` | 💎 | Oracle Bone received | One-time trade flag |
| `$2437` | word | ⚙️ | Bazooka ammo / dispatch sub-ID | Dual use |
| `$2519` | word | 🏺 | Beads (inventory count) | Increased by vendor |
| `$2525` | word | 🏺 | Perfume (inventory count) | Increased by perfume vendor |
| `$2529` | word | 🏺 | Spice (inventory count) | Used by perfume vendor |
| `$252f` | word | 🏺 | Exhibition Ticket (`TICKET_FOR_EXHIBITION`) | Increased by ticket vendor; cost = 1× Amulet of Annihilation |
| `$251f` | word | 💎 | Golden Jackal Statuette | Deducted by Oracle Bone trade |
| `$2521` | word | 💎 | Jeweled Scarab | Deducted by Oracle Bone trade |
| `$2517` | word | 💎 | Amulet of Annihilation count | Deducted by ticket vendor |
| `$234b` | word | ⚙️ | Interior sub-room dispatch ID | Set on castle door step-ons |
| `$234f` | word | ⚙️ | Dungeon exit sub-ID | Set before entering 0x74 |

## Drop Table

_No drop table configured for this room._

## Notes

- `$22dd&0x40` (east castle) and `$22dc&0x08` (WindWalker) together form the castle state machine shared across 0x7b, 0x7c, and 0x7d
- The Thug's Cloak flag `$2263&0x02` may gate a story path elsewhere (disguise mechanic)
- The Oracle Bone trade is a key item for story progression
- `$234b` values 1–4 route to the bottom-half castle doors in 0x7d; values 5–9 are assigned in 0x7c
