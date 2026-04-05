# 0x53 — Act 2 Start Cutscene

**ROM:** `0x9fff33` | **Data:** `0xabe2f9` | **Enter:** `0x9281ba` → `0x94eb15`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x64` (WindWalker flight theme) |
| Map bounds | `(0,0)` to `(0x0310, 0x00e0)` (wide horizontal scroll) |
| NPCs | 1× `0x20` (WindWalker visual) |
| Step-on zones | 0 |
| B-triggers | 0 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| End of cutscene | `0x6a` Act2 Start Cutscene - waterfall @ `[0x0088\|0x0000]` | scripted | Sets `$22eb\|=0x20` before warping |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | `0x20` | ⚙️ | Animation-skip flag (standard entry guard) |

## Enter Script Summary

1. `$22eb&0x20` guard; default teleport to `(0x61, 0x0f)`.
2. Set map bounds `(0,0)–(0x0310,0x00e0)`.
3. Set WW start coordinates: `$24ab/$24af = (0x02e8, 0x0008)`; `$24cf/$24d1 = (0x02e8, 0x0068)`.
4. Stop boy+dog; teleport both to `($24ab+6, $24af-16)`.
5. Load NPC `0x20` at `(0x63, 0x0d)` → `$2838`, sprite 0x006e (WindWalker sled visual).
6. Teleport `$2838` to `($24cf, $24d1)`.
7. Hide status bar (`0x92a3e7`); cinematic setup (`0x92de75`).
8. Play music `0x64`; `$23bf=1`.
9. **Landing animation** (RCALL `0x94e8df`): teleport boy and dog onto the WW from behind, each making a 5-frame slide (left by 1 each tick). Update `$24ab/$24af` after landing.
10. Sleep 19 ticks.
11. **Flight animation** (RCALL `0x94e9d8`): WW moves left; plays sound `0x3c`; boy and dog bounce sprite changes; WW scrolls across screen.
12. **First sliding loop**: while boy X > WW X, teleport both left 1 tile per YIELD, WW follows.
13. **Second sliding loop** `$2835` 1→40: teleport both left 2 tiles per tick.
14. **Drop loop** `$2835` 1→20: teleport both down 4 tiles per tick (WW dropping off screen).
15. BOY+DOG STOPPED; `DESTROY/DEALLOC ENTITY $2838`; set `$22eb|=0x20`; CHANGE MAP 0x6a.

## Notes

- **Pure cutscene — no player interaction.** The boy, dog, and WindWalker NPC fly in from the right side of the map and exit left/downward.
- **`$22eb|=0x20`** is set immediately before warping to 0x6a so that 0x6a skips its own teleport (continues the seamless cutscene).
- **Music `0x64`** = WindWalker flight theme. First use of this track in Act 2.
- NPC `0x20` is reused here as the WindWalker sled visual — same NPC type as the "lava ball" in 0x3f and the "rock" in the Magmar cutscene.
- **Act 1 → Act 2 transition sequence:** 0x36 (fire pit) → WINDWALK → 0x3a (Antiqua fire pit) → ??? → 0x53 (this room) → 0x6a (waterfall) → 0x68 (Crustacia exterior).
