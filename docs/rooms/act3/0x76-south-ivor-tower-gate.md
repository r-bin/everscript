# 0x76 — South of Ivor Tower (Gate)

**Act:** 3 — Gothica  
**Script address:** `0x9fff97` (0x76 block)  
**Music:** `MUSIC.ACT3` (0x60) — Gothica outdoor  
**Dog sprite:** Poodle (0x08)

## Overview

Large outdoor area immediately south of the Ivor Tower castle complex, serving as the main approach zone from the wilderness. The room has two exits: north to the castle exteriors (0x7b) and east to the Well (0x6c). It contains 16 sniff spots, two story-critical item pickups (Horace's Aura spell, Amulet of Annihilation), two gourds, and three enemy spawners (DANCING_DEVIL_2, HEDGEHOG, SLIME). Drop table rewards Feather, Acorns, and Honey.

## Connections

| Direction | Tile range | Destination | Notes |
|-----------|-----------|-------------|-------|
| North | `[14,0d:18,0f]` | MAP 0x7b — Ebon Keep/Ivor Tower Exterior Bottom | main road to castle |
| East | `[32,3f:34,44]` | MAP 0x6c — SE of Ivor Tower (Well) | `[0x0008 \| 0x00e0]` |

## Enter Script

1. Set drop table: PRIZE1=0x020c (Feather) rate 10, PRIZE2=0x0215 (Acorns) rate 2, PRIZE3=0x0802 (Honey) rate 1
2. Play `MUSIC.ACT3` (0x60)
3. Unload gourd OBJs based on `$22c6`–`$22c8` flags (sniff spots) and `$227c` bits (gourds)
4. Unload Horace's Aura OBJ if `$227b&0x80`; unload Amulet OBJ if `$227c&0x01`
5. Spawn tables:
   - 4× NPC 0x75 (`DANCING_DEVIL_2`) — `$2433=0x0001` each
   - 8× NPC 0x50 (`HEDGEHOG`) — `$2433=0x0002` each
   - 8× NPC 0x71 (`SLIME`) — `$2433=0x0001` each

## Step-On Scripts

| Tile | Destination | Notes |
|------|------------|-------|
| `[14,0d:18,0f]` | MAP 0x7b @ `[0x00e0 \| 0x02f8]` | North → Ebon Keep/Ivor Tower exterior |
| `[32,3f:34,44]` | MAP 0x6c @ `[0x0008 \| 0x00e0]` | East → Well |

## B-Trigger Scripts

### Special Item Pickups

| Tile | Item | Flag | Notes |
|------|------|------|-------|
| `[07,1c:09,1e]` | **Horace's Aura** (alchemy spell) | `$227b&0x80` | `$22db\|=0x40`; OBJ 0 unloaded (`state 0x63`) |
| `[04,2c:06,2e]` | **Amulet of Annihilation** | `$227c&0x01` | OBJ 1 loaded; `$2517+=1`; sets flag |

### Gourds

| Tile | OBJ flag | Item | Qty |
|------|----------|------|-----|
| `[0a,39:0c,3b]` | `$227c&0x02` | Ash (0x0214) | 4 |
| `[15,46:17,48]` | `$227c&0x04` | Atlas Medallion (0x0213) | 1 |

### Sniff Spots (16 total)

Sniff spots #4–#19 (gourds occupy MAP REF slots 1–3). All check/set bits in `$22c6`–`$22c8`:

| # | Tile | Item | Flag |
|---|------|------|------|
| 4 | `[19,40:1a,41]` | Iron | `$22c6&0x02` |
| 5 | `[22,31:23,32]` | Iron | `$22c6&0x04` |
| 6 | `[0e,26:0f,27]` | Acorns | `$22c6&0x08` |
| 7 | `[24,43:25,44]` | Acorns | `$22c6&0x10` |
| 8 | `[0d,16:0e,17]` | Mushroom | `$22c6&0x20` |
| 9 | `[03,20:04,21]` | Mushroom | `$22c6&0x40` |
| 10 | `[0b,42:0c,43]` | Mushroom | `$22c6&0x80` |
| 11 | `[24,1b:25,1c]` | Feather | `$22c7&0x01` |
| 12 | `[32,3c:33,3d]` | Feather | `$22c7&0x02` |
| 13 | `[1d,11:1e,12]` | Brimstone | `$22c7&0x04` |
| 14 | `[0f,20:10,21]` | Water | `$22c7&0x08` |
| 15 | `[1a,2b:1b,2c]` | Roots | `$22c7&0x10` |
| 16 | `[00,2f:01,30]` | Roots | `$22c7&0x20` |
| 17 | `[11,49:12,4a]` | Ethanol | `$22c7&0x40` |
| 18 | `[15,35:16,36]` | Ash | `$22c7&0x80` |
| 19 | `[26,3c:27,3d]` | Ash | `$22c8&0x01` |

## Spawners

| Qty | NPC ID | Enum | Name | Rate |
|-----|--------|------|------|------|
| 4 | 0x75 | `DANCING_DEVIL_2` | Dancin' Fool | `$2433=0x0001` |
| 8 | 0x50 | `HEDGEHOG` | Hedgadillo | `$2433=0x0002` |
| 8 | 0x71 | `SLIME` | Blue Goo | `$2433=0x0001` |

## Drop Table

| Slot | Item | ID | Rate |
|------|------|-----|------|
| PRIZE1 | Feather | 0x020c | 10 |
| PRIZE2 | Acorns | 0x0215 | 2 |
| PRIZE3 | Honey | 0x0802 | 1 |

## Memory Access

| Address | Bit | Type | Name | Notes |
|---------|-----|------|------|-------|
| `$227b` | `0x80` | 💎 | Horace's Aura collected | Spell pickup flag |
| `$22db` | `0x40` | ⚗️ | Horace's Aura alchemy known | Set when picking up spell tile |
| `$227c` | `0x01` | 💎 | Amulet of Annihilation found | `$2517+=1` |
| `$227c` | `0x02` | 🫙 | Ash gourd looted `[0a,39]` | 4× Ash (0x0214) |
| `$227c` | `0x04` | 🫙 | Atlas Medallion gourd looted `[15,46]` | 1× Atlas Medallion (0x0213) |
| `$22c6` | `0x02` | 👃 | Sniffed Iron (#4) [0x76] (0x02) | |
| `$22c6` | `0x04` | 👃 | Sniffed Iron (#5) [0x76] (0x04) | |
| `$22c6` | `0x08` | 👃 | Sniffed Acorns (#6) [0x76] (0x08) | |
| `$22c6` | `0x10` | 👃 | Sniffed Acorns (#7) [0x76] (0x10) | |
| `$22c6` | `0x20` | 👃 | Sniffed Mushroom (#8) [0x76] (0x20) | |
| `$22c6` | `0x40` | 👃 | Sniffed Mushroom (#9) [0x76] (0x40) | |
| `$22c6` | `0x80` | 👃 | Sniffed Mushroom (#10) [0x76] (0x80) | |
| `$22c7` | `0x01` | 👃 | Sniffed Feather (#11) [0x76] (0x01) | |
| `$22c7` | `0x02` | 👃 | Sniffed Feather (#12) [0x76] (0x02) | |
| `$22c7` | `0x04` | 👃 | Sniffed Brimstone (#13) [0x76] (0x04) | |
| `$22c7` | `0x08` | 👃 | Sniffed Water (#14) [0x76] (0x08) | |
| `$22c7` | `0x10` | 👃 | Sniffed Roots (#15) [0x76] (0x10) | |
| `$22c7` | `0x20` | 👃 | Sniffed Roots (#16) [0x76] (0x20) | |
| `$22c7` | `0x40` | 👃 | Sniffed Ethanol (#17) [0x76] (0x40) | |
| `$22c7` | `0x80` | 👃 | Sniffed Ash (#18) [0x76] (0x80) | |
| `$22c8` | `0x01` | 👃 | Sniffed Ash (#19) [0x76] (0x01) | |

## Notes

- This room contains the Horace's Aura spell — one of the alchemy spells obtained in the field rather than from a trainer
- The Amulet of Annihilation pickup here is one of the Annihilation Amulets tracked by `$2517` (global amulet count)
- `$22c8` bits are not used by this room's sniff spots — they may be used by adjacent rooms sharing the Gothica outdoors sniff block
