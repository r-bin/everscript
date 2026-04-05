# 0x52 — Top of Volcano

**ROM:** `0x9fff2f` | **Data:** `0xacfa2d` | **Enter:** `0x9281b5` → `0x948455`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x26` |
| Map bounds | X: 0x0000–0x0100, Y: 0x0000–0x00e0 (tiny room, ~8×7 tiles) |
| Objects | 1 (obj 0 — volcano crater / WindWalker state) |
| NPCs | 1 (WindWalker NPC, gated by `$22dc&0x08`) |
| Step-on zones | 1 |
| B-triggers | 0 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| Geyser up | `0x50` Sky above Volcano | enter with `$22ec&0x08` | geyser launch; `$22eb\|=0x20` |
| Walk exit | `0x69` Volcano Path @ `[0x0250\|0x01c0]` | step-on `[0f,0c:11,0d]` | sets `$22ec\|=0x10` |
| WindWalker descent | `0x69` Volcano Path @ `[0x02f8\|0x00d8]` | `$22dc&0x08` on entry | immediate warp if windwalker known |
| Sky return | — | enter with `$22ee&0x01` | arrives from 0x50; stays in 0x52 |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22dc` | `0x08` | 📖 | WindWalker unlocked (gates NPC load; triggers immediate descent on entry) |
| `$22ec` | `0x08` | 📖 | Stepped on geyser (gates geyser-launch branch; cleared here) |
| `$22ec` | `0x10` | 📖 | Descending from Top of Volcano (SET by step-on; consumed by 0x69 enter) |
| `$22ee` | `0x01` | 📖 | Arrived from Sky above Volcano (cleared in Branch B entry) |
| `$2273` | `0x20` | 📖 | Top of volcano visited (gates first-time NPC dialog) |
| `$225a` | `0x20` | ⚗️ | Levitate learned — **SET here** by NPC dialog |

## NPCs

| NPC ID | Position | Talk Script | Condition | Notes |
|--------|----------|-------------|-----------|-------|
| `0x34` | `(0x12, 0x0d)` | `0x17e2` | NOT `$22dc&0x08` | WindWalker NPC; teaches Levitate on first visit |

## Enter Script Summary

### Branch A — Geyser Launch (`$22ec&0x08`)
1. Teleport both to `(0x1d, 0x01)` (top of screen).
2. If `$22dc&0x08`: set obj 0 state=2. Call `0x92de75`.
3. Sleep 29; clear `$22ec&0x08`.
4. Stop characters; face south; setup geyser params (`$24b3=0x64`, `$2835/$2837/$2839/$283b = 0x0700/$0e00/$0700/$0e00`).
5. Call `0x94827e` (geyser eruption visual); sleep 19; call `0x9482d5`; sleep 14.
6. Fade out screen; set `$22eb|=0x20`.
7. **CHANGE MAP = `0x50` Sky above Volcano** @ `[0x0008|0x00d8]`.

### Branch B — Sky Return (`$22ee&0x01`)
1. Teleport boy to `(0x10, 0x19)`, dog to `(0x0f, 0x17)`, both face west.
2. Set obj 0 state=1; clear `$22ee&0x01`; set `$238f=0x000f`.
3. Call `0x92de75`. End.

### Branch C — Normal Entry (no special flags)
1. Teleport both to `(0x1d, 0x01)`.
2. Obj 0 state = 2 if `$22dc&0x08`, else state=1.
3. Clear VRAM; sleep; stop characters.
4. Call `0x94832c` ("Top of volcano [1]"); sleep 43.
5. Call `0x9483cb` ("Top of volcano [2]"): non-controlled char flies in from top of screen (Y: 0x01 → 0x3d or 0x78 depending on `$22dc&0x08`); screen shake + SFX `0x3c` on landing.
6. If NOT `$22dc&0x08`: sleep, walk controlled char down 2 tiles, clear `$2834&0x01`.
   - If NOT `$2273&0x20`: call "Top of Volcano dialog" (`0x948000`).
   - Else: BOY+DOG = player controlled.
7. If `$22dc&0x08` (WindWalker already unlocked): sleep 59; fade out slowly; **CHANGE MAP = `0x69`** @ `[0x02f8|0x00d8]`.

### Top of Volcano Dialog (`0x948000`)

1. Set `$2273|=0x20`.
2. Dog walks to `(0x17, 0x0f)`; boy walks to `(0x0d, 0x11)`.
3. **TEXT 05f4 (NPC):** *"Hmmm...mmmm...another fine blend...nice nose...good color"* (connoisseur, tasting something)
4. **TEXT 05f7 (Boy):** *"Uh, hi. You wouldn't know how to get into the volcano from here, would you?"*
5. **TEXT 05fa (NPC):** *"The volcano? No. None but the way that would turn an adventurer into ash and molten bones."*
6. **TEXT 05fd (Dog):** *"Pardon me?"*
7. **TEXT 0600 (NPC):** *"The only way that I know to enter the volcano is straight into the crater. Of course, come to think of it, you could try the catacombs at the base of the volcano."*
8. Boy: *"I've seen a passage, but it's blocked by a big rock!"*
9. **TEXT 0609 (NPC):** *"Levitation! That's a good solution! You can lift rocks and other heavy objects by using the Levitate Formula. I'll give it to you right now."*
10. **Set `$225a|=0x20`** (Levitate learned). Show Alchemy screen (pre-selected: Levitate `0x2a`).
11. **TEXT 060c:** *"The formula requires a Mud Pepper and Water."*
    - If no Mud Pepper (`$2305 == 0`): direct to swamp; ingredient shop `$2459=0x0005`; save `$2449=0x000b`.
    - Else (has Mud Pepper): *"I have a Mud Pepper! I found it in the swamp."* → ingredient shop + save.
12. Characters face south, BOY+DOG = player controlled. Call "Market NPC end" (`0x33`).

## Step-on Zones

| Zone | Sets | Destination | Notes |
|------|------|-------------|-------|
| `[0f,0c:11,0d]` | `$22ec\|=0x10` | `0x69` Volcano Path @ `[0x0250\|0x01c0]` | walk back down; fade-out loop; stop + animate both characters |

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x94827e` | Geyser eruption animation (visual effect) |
| `0x9482d5` | Geyser eruption phase 2 |
| `0x94832c` | Top of volcano entry [1] (initial landing sequence) |
| `0x9483cb` | Top of volcano entry [2] (non-controlled char fly-in + landing) |
| `0x9481fe` | Step-on animation helper |
| `0x94823b` | Step-on animation helper 2 |

## Notes

- **Levitate** (`$225a bit 0x20`) is set exclusively in this room.
- `$22dc bit 0x08` (labeled "windwalker unlocked" in the dump) gates the NPC and auto-descents on entry. Its setter has not been found yet — TODO: identify where this bit is set.
- Room 0x50 (Sky above Volcano) is a pure cutscene transition; the geyser path goes 0x69 → 0x52 → 0x50 → 0x52 → 0x69.
- NPC `0x34` is the only named WindWalker-class NPC in Act 1. Talk script `0x17e2` likely handles re-interaction.
- `$22ec bit 0x10` (set by step-on) is consumed by 0x69's enter script to play the "descent from Volcano Top" cinematic.
