# Room 0x5d — Gothica: Ebon Keep Courtyard (South of Verm)

| Field | Value |
|-------|-------|
| **Room ID** | 0x5d |
| **Act** | 3 — Gothica |
| **Data** | `0x9fff5b` |
| **Enter script** | `0x9281ec` → `0x99ee1e` |
| **Dog sprite** | Default (no override) |
| **Music** | 0x6a (if windwalker unlocked) / 0x62 (otherwise) |
| **Step-ons** | 7 entries |
| **B-triggers** | 0 entries |
| **Connections** | 0x5e (Ebon Keep Front Room, north), 0x5f (Verm Side Rooms, 2 exits north), 0x7c (Exterior Top Half, south) |

---

## Overview

The exterior courtyard area immediately south of Verminator's domain inside Ebon Keep. A mid-sized outdoor area with Ratling enemies and three guarded doorway triggers. Contains portcullis-style barriers (OBJ 0/1/2) that animate briefly when the player tries to pass through, blocking entry unless the barrier OBJ is not loaded.

Music switches based on `$22dc&0x08` (windwalker unlocked).

On entry, `$238f==3` is used to route the player through a specific entrance tunnel:
- `$23b9==1` → unload OBJ 1 (left entrance)
- `$23b9==2` → unload OBJ 2 (right entrance)
- otherwise → unload OBJ 0 (center entrance)

After the cinematic call, the corresponding OBJ is re-loaded at state 0.

---

## Enter Logic

1. If NOT `$22eb&0x20`: teleport both to `[13,45]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. Set enemy loot: Prize 1 = Oil (0x0204) ×10, Prize 2 = Talons (0x0001) qty 0x4b ×5, Prize 3 = Biscuit (0x0803) ×1
4. `$23bf = 0x0000`; `$2433 = 0x0002`
5. Spawn 11 NPC 0x42 (Ratling) spawners across the courtyard
6. If music not locked:
   - If `$22dc&0x08` (windwalker unlocked): PLAY MUSIC 0x6a
   - Else: PLAY MUSIC 0x62
   - Fade in
7. If `$238f == 3` (entry from side room door): hide the entry-point OBJ based on `$23b9`:
   - `$23b9 == 1` → unload OBJ 1
   - `$23b9 == 2` → unload OBJ 2
   - else → unload OBJ 0
8. `$23b9 = 0x0000`
9. `CALL 0x92de75` (cinematic setup)
10. Re-load the same OBJ at state 0 (show barrier again after spawn)
11. `$23b9 = 0x0000`; END

---

## Step-On Table

| Tile(s) | Action |
|---------|--------|
| `[1e,1a:20,1c]` | → 0x5f `[02e0, 0368]` (Verm Side Rooms, right entrance) |
| `[10,1a:12,1c]` | → 0x5f `[0080, 0368]` (Verm Side Rooms, left entrance) |
| `[14,2f:1c,32]` | `$22dd \|= 0x40` (Load east castle); → 0x7c `[0200, 0058]` (Ebon Keep Exterior Top Half, south exit) |
| `[16,13:1a,15]` | **Barrier OBJ 0** — if `$2834&0x01` already set: skip. Else: set, unload OBJ 0, sleep 119 ticks, reload OBJ 0, clear bit. (Transient — does not persist.) |
| `[10,1c:12,1d]` | **Barrier OBJ 1** — same pattern as above with `$2834&0x02` and OBJ 1 |
| `[1e,1c:20,1d]` | **Barrier OBJ 2** — same pattern with `$2834&0x04` and OBJ 2 |
| `[16,11:1a,13]` | Fade out; → 0x5e `[00b0, 0328]` (Ebon Keep Front Room) |

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$22dc` | 0x08 | R | 📖 Windwalker unlocked (music switch) |
| `$22dd` | 0x40 | W | Load east castle (set when exiting south to 0x7c) |
| `$238d` | word | R | Music lock |
| `$238f` | word | R | Entry routing: 3 = entering from side room |
| `$23b9` | word | R/W | Entrance selector (1/2/other) for OBJ routing; cleared after use |
| `$23bf` | word | W | Unknown (cleared) |
| `$2433` | word | W | Enemy spawn count |
| `$2834` | 0x01 | R/W | Barrier OBJ 0 animation in-progress (transient) |
| `$2834` | 0x02 | R/W | Barrier OBJ 1 animation in-progress (transient) |
| `$2834` | 0x04 | R/W | Barrier OBJ 2 animation in-progress (transient) |

## Notes

- The three portcullis barriers (OBJ 0/1/2) animate briefly when crossed but do not block permanently — `$2834` bits 0x01/0x02/0x04 are transient flags cleared after each animation.
- Entry routing via `$238f` and `$23b9` selects which barrier OBJ to unload/reload on arrival; `$23b9` is cleared after use.
- Music switches between 0x62 (pre-WindWalker) and 0x6a (WindWalker unlocked) based on `$22dc&0x08` on every entry.
