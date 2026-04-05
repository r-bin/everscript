# [0x6e] Gothica — Ivor Tower Hall

| Field | Value |
|-------|-------|
| Room ID | 0x6e |
| Name | Gothica - Ivor Tower Hall |
| Act | Act 3 — Gothica |
| Data offset | `0xa8a2f4` |
| Enter script | `0x928241` → `0x98a337` |
| Step-ons | 9 |
| B-triggers | 0 |
| Music | 0x74 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 9 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | Guard `$2835` = NPC 0x54 at `[12,11]` (collapse); Guard `$0090>>1=0x48` at `[1d,53]` or `[3e,45]` |
| Forced dog form | Poodle (0x08) |
| Music | 0x74 |

---

## Overview

The main corridor of Ivor Tower, connecting the dining room, exterior, Queen's Room, and a locked east wing. This room hosts two major story events:

1. **Escape cutscene** (`$234b==0x8e`, `$2354==0`): Boy + dog have escaped the sewer/dungeon; a guard catches them in the hall and escorts them back to the Queen's Room.
2. **West castle collapse** (`$22ee&0x80`): The Ebon Keep (west castle) dramatically collapses during an earthquake. Screen shakes, OBJs 8–22 unload (collapse), flag `$22e5|=0x40` is set permanently.

---

## Enter Script Logic

1. Guard `$22eb&0x20`; teleport both to `[12,11]`; fade-out music
2. Dog = Poodle
3. Play music 0x74 (if not already playing)
4. **IF `$234b==0x64`** (returning from Queen's Room via north door, post-collapse): sound 0x46; unload OBJ 2, 5, 6; **END**
5. **IF `$234b==0x8e`** (returning from Queen's Room after meeting, `$2354==0`): sound 0x46; unload OBJ 23; RCALL 0x989e9d (escape cutscene):
   - Load Guard NPC at `[3e,45]`; boy repositioned; text shown
   - Boy: *"Whew! I'm glad we're out of that sewer."* / Dog: *"Sniff... We'll probably stink for a while."*
   - *"Oh no! A Guard!"* → Guard walks in: *"Stay right where you are, little mister!"*
   - Guard: *"Thought you could escape? Didn't you? Well, I have orders that the queen is waiting to see you."*
   - *"You're coming with me! Sniff... Do you smell something?"*
   - Frame-by-frame escort walk (boy, dog, guard walk south together); fade-out
   - `$234b = 0x008e`; `$22eb|=0x20`; CHANGE MAP 0x78 @ `[0x00f8|0x02b8]` (Ivor Tower Queen's Room)
6. **IF `$22ee&0x80`** (West castle collapse trigger): `$2437=0x0007`; RCALL 0x98a10d (collapse cutscene):
   - Clear `$22ee&0x80`; start screen shaking (magnitude 3/3)
   - Load NPC 0x54 at `[12,11]` → `$2835`; NPC walks through OBJ gates
   - OBJs 2, 5, 6 unload one by one; OBJs 8–22 all unloaded (castle collapse)
   - Screen shake at max; sound 0x62 (collapse SFX)
   - **`$22e5|=0x40`** (West castle collapsed — permanent flag)
   - Dialog: *"Whew! That was close!"*
   - `$22de|=0x08`; screen shake gradually fades; play music 0x74; **END**
7. **IF `$22e5&0x40`** (West castle already collapsed): unload OBJs 8–22 (suppress debris permanently)
8. Remaining enter paths: cinematic; load guard NPC at `[1d,53]` if `$22de&0x08`; **END**

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[2e,28:2f,2a]` | OBJ 5 close | Distance-based: if NPC is ahead of player, stop player, walk NPC to y=0x1e, then close OBJ 5 |
| `[2e,30:2f,32]` | OBJ 6 close | Same logic, NPC walks to y=0x2e, close OBJ 6 |
| `[2e,33:2f,35]` | OBJ 6 open | Distance-based: open OBJ 6 after NPC walk to y=0x34 |
| `[2e,2b:2f,2d]` | OBJ 5 open | Distance-based: open OBJ 5 after NPC walk to y=0x24 |
| `[30,24:32,25]` | MAP 0x78 @ `[0x00f8\|0x02b8]` | OBJ 2 = 0x7e; sound 0x46 → Queen's Room (north staircase, top) |
| `[30,20:32,22]` | MAP 0x78 @ `[0x00f8\|0x02b8]` | Same as above (alternate tile range) |
| `[3c,54:41,56]` | MAP 0x7c @ `[0x0200\|0x0058]` | South → Ebon Keep and Ivor Tower Exterior Top Half (code 0x41) |
| `[46,3c:48,3e]` | MAP 0x6f @ `[0x00f0\|0x01c8]` | North → Ivor Tower Dining Room |
| `[4c,43:4d,45]` | **Locked** (push west) | Shows "Locked" unwindowed text; pushes controlled char west |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22ee` | 0x80 | R/W | 📖 West castle collapse trigger — cleared inside RCALL |
| `$22e5` | 0x40 | R/W | 📖 West castle collapsed (permanent) — set during collapse RCALL |
| `$22de` | 0x08 | R/W | 📖 Guard NPC persistent — set after collapse; also enables NPC load at `[1d,53]` |
| `$22dc` | 0x08 | R | 📖 WindWalker unlocked (checked via `$2437=0x0007`) |
| `$2354` | 0xff | R | ⚙️ Escape cutscene gate — `0` = play cutscene; nonzero = skip |
| `$234b` | — | R/W | ⚙️ Room-entry source code — 0x64 = from Queen's Room post-collapse; 0x8e = from Queen's Room after meeting; cleared to 0x0000 before escape RCALL |
| `$2437` | — | W | ⚙️ Set to 0x0007 during collapse / when WindWalker unlocked |
| `$2835` | — | W | ⚙️ Collapse/escort NPC pointer |

## Notes

- The west castle collapse is the Act 3 pivot event: `$22ee&0x80` (Mungola defeated, set in 0x77/0x78) triggers the collapse RCALL here, permanently setting `$22e5&0x40`.
- `$2354` gates the escape cutscene — once nonzero (set to 0x0001 by 0x78 mission briefing), the cutscene is permanently skipped on re-entry.
- `$234b` encodes two distinct post-event entry states: `0x64` (post-collapse, from 0x78) and `0x8e` (returning from Queen's Room after the first meeting); both routes clear `$234b` to 0x0000 before the escape RCALL.
