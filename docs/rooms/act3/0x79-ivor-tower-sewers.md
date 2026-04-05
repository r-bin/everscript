# Room 0x79 — Gothica: Ivor Tower Sewers

| Field | Value |
|-------|-------|
| **Room ID** | 0x79 |
| **Act** | 3 — Gothica |
| **Data** | `0x9fffcb` |
| **Enter script** | `0x928278` → `0x98b332` |
| **Dog sprite** | Poodle (`$2443=0x08` on enter) |
| **Music** | 0x56 |
| **Step-ons** | 4 entries |
| **B-triggers** | 8 entries (all gourds) |
| **Connections** | 0x6e (Ivor Tower Hall, drain exit), 0x7a (Sewers Exterior, 2 exits) |

---

## Overview

The underground sewer network beneath Ivor Tower. Entered through a drain in 0x6e (Ivor Tower Hall) or from 0x7a (the exterior landing platform). Features Corrosion Guy NPC, 16 Ratling (NPC 0x42) spawners spread across the sewer tunnels, and 8 gourd chests. One "too slippery" barrier prevents walking back up a certain pipe. Loot drop rates are configured for the Ratling enemies.

---

## Enter Logic

1. If NOT `$22eb&0x20`: teleport both to `[49,1b]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. `$23bf = 0x0000`
4. `$2443 = 0x08` (Poodle)
5. Load NPC 0x90>>1 (flags/state 0002) at `[d1,1b]` → `$2455`; set talk script 0x19cb (arg 0x40) = **Corrosion Guy**
6. Conditionally unload OBJ 1–8 based on persistence flags:

| OBJ | Guard flag |
|-----|-----------|
| 1 | `$2285&0x20` |
| 2 | `$2285&0x40` |
| 3 | `$2285&0x80` |
| 4 | `$2286&0x01` |
| 5 | `$2286&0x02` |
| 6 | `$2286&0x04` |
| 7 | `$2286&0x08` |
| 8 | `$2286&0x10` |

7. Set enemy loot rates: Prize 1 = Ratling bone (0x0801) ×10, Prize 2 = Talons (0x0001) qty 0x41 ×3, Prize 3 = Biscuit (0x0802) ×1
8. `$2433 = 0x0003` (spawn count); spawn 16 NPC 0x42 (Ratling) spawners at positions spread across the map
9. If music not locked: PLAY MUSIC 0x56; fade in
10. `CALL 0x92de75` (cinematic setup); `CALL 0x92d52d`

---

## Step-On Table

| Tile(s) | Action |
|---------|--------|
| `[34,04:35,05]` | **"Too Slippery"** — script-controls player, walks them 2 tiles south with slipping animation; shows text "Too Slippery" (0x17b5); returns control |
| `[42,08:44,09]` | **Drain exit → 0x6e** — plays SFX 0x46; sleep 29 ticks; fade out; `$22eb\|=0x20` (in animation); `$238f=0x0002`; fade-out screen; `$234b=0x008e`; walk entity upward; sleep 15; CHANGE MAP → 0x6e `[0258, 02a0]` |
| `[7f,39:80,3a]` | → 0x7a `[0028, 00a8]` (Sewers Exterior) |
| `[7e,31:80,38]` | → 0x7a `[0028, 0058]` (Sewers Exterior, east side) |

---

## B-Trigger Table (Gourds)

| Tile(s) | Guard flag | Item | Qty | MAP REF |
|---------|-----------|------|-----|---------|
| `[7a,0b:7c,0c]` | `$2286&0x10` | 🫙 Call Beads (0x0807) | 1 | 0x0008 |
| `[76,0b:78,0c]` | `$2286&0x08` | 🫙 Biscuit (0x0803) | 1 | 0x0007 |
| `[4c,35:4e,36]` | `$2285&0x20` | 🫙 Honey (0x0802) | 1 | 0x0001 |
| `[4e,35:50,36]` | `$2285&0x40` | 🫙 Mushroom (0x0206) | 2 | 0x0002 |
| `[20,4b:22,4c]` | `$2285&0x80` | 🫙 Water (0x0201) | 5 | 0x0003 |
| `[22,4b:24,4c]` | `$2286&0x01` | 🫙 Acorns (0x0215) | 2 | 0x0004 |
| `[24,4b:26,4c]` | `$2286&0x02` | 🫙 Iron (0x0209) | 3 | 0x0005 |
| `[5e,53:60,54]` | `$2286&0x04` | 🫙 Oil (0x0204) | 2 | 0x0006 |

All gourds: `flag |= bit if $22ea&0x01 else flag &= ~bit` (standard loot-gourd pattern).

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$23bf` | word | W | Unknown (cleared to 0) |
| `$2443` | word | W | Dog sprite |
| `$2455` | word | W | Corrosion Guy NPC pointer |
| `$2285` | 0x20 | R/W | 🫙 Gourd MAP REF 0x01 looted (Honey) |
| `$2285` | 0x40 | R/W | 🫙 Gourd MAP REF 0x02 looted (Mushroom) |
| `$2285` | 0x80 | R/W | 🫙 Gourd MAP REF 0x03 looted (Water) |
| `$2286` | 0x01 | R/W | 🫙 Gourd MAP REF 0x04 looted (Acorns) |
| `$2286` | 0x02 | R/W | 🫙 Gourd MAP REF 0x05 looted (Iron) |
| `$2286` | 0x04 | R/W | 🫙 Gourd MAP REF 0x06 looted (Oil) |
| `$2286` | 0x08 | R/W | 🫙 Gourd MAP REF 0x07 looted (Biscuit) |
| `$2286` | 0x10 | R/W | 🫙 Gourd MAP REF 0x08 looted (Call Beads) |
| `$22ea` | 0x01 | R | Loot-gourd success flag |
| `$238d` | word | R | Music lock |
| `$238f` | word | W | Entry source (0x0002 = rising through drain) |
| `$234b` | word | W | Entry source code for 0x6e |
| `$2391` | word | W | Gourd prize item |
| `$2395` | word | W | Gourd MAP REF |
| `$2461` | word | W | Gourd prize quantity |

## Notes

- Eight gourds tracked across `$2285` (bits 0x20–0x80) and `$2286` (bits 0x01–0x10) — the most loot-dense sewer area in the game.
- Corrosion Guy NPC is always loaded on entry with no condition check; he serves as the room's ambient guide NPC.
- The sewer connects three entry points: dungeon pipes from 0x74 (via `$2843` pipe index), exterior platform from 0x7a, and the Ivor Tower Hall drain from 0x6e (via `$238f=0x0002`).
