# Room 0x78 — Gothica: Ivor Tower Queen's Room

| Field | Value |
|-------|-------|
| **Room ID** | 0x78 |
| **Act** | 3 — Gothica |
| **Data** | `0x9fffc7` |
| **Enter script** | `0x928273` → `0x989c84` |
| **Dog sprite** | Poodle (`$2443=0x08` on enter) |
| **Music** | 0x18 (Gothica throne room) |
| **Step-ons** | 4 entries |
| **B-triggers** | 0 entries |
| **Connections** | 0x6e (Ivor Tower Hall, south), 0x77 (Puppet Show / Mungola, west — 2 exits) |

---

## Overview

The Queen's throne room — the central narrative hub of Act 3. Three major cutscene paths branch on entry:

1. **Post-Mungola collapse** (`$22ee&0x80`): Eronio rushes in, castle shakes, party is escorted to 0x6e.
2. **First Queen audience** (`$234b == 0x8d`, `$22de&0x04` clear): "Queen Below Chessboard" cutscene Pt. 2 — boy+dog are hidden, Queen and Eronio discuss their captives, the party is teleported to 0x21 (Dark Forest Entrance). `$22de|=0x04` guards this cutscene (one-shot).
3. **Normal Queen audience** (default): Eronio escorts the player to the Queen's throne, Queen delivers the mission briefing about Ebon Keep, drawbridge, and the ravine. Sets `$2354=0x0001`.

Also handles replay case when `$234b == 0x8e` (returning from chessboard area): loads Queen+Eronio in standing positions with ambient talk scripts.

Key items: the Queen's Key (`$2264&0x10`, `$2353`) is picked up via a step-on here.

---

## Enter Logic

1. If NOT `$22eb&0x20`: teleport both to `[1f,3b]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. `$2443 = 0x08` (Poodle); `$23bf = 0x0001`
4. If music not locked: PLAY MUSIC 0x18; fade in
5. **If `$22ee&0x80`** (Mungola defeated — collapse cutscene):
   - RCALL 0x989637 — **"Castle Collapse" cutscene**:
     - Load NPC 0x36>>1 (Eronio, NPC 54) at `[03,35]` → `$2834`
     - Start screen shake; set audio 0xe6
     - Eronio walks east 3 tiles, then NE by (11,2), then south 14 tiles; waits
     - Boy and dog follow
     - CHANGE MAP → 0x6e `[0090, 0088]` (Ivor Tower Hall)
   - END
6. **If `($234b & 0xff) == 0x8d`** (from Queen below chessboard):
   - `$234b = 0x0000`
   - If NOT `$22de&0x04` (cutscene not yet watched):
     - `$22de |= 0x04` (mark watched)
     - RCALL 0x989bb5 — **"Queen Below Chessboard Pt. 2"**:
       - `$2261|=0x02` (Boy unavailable), `$2261|=0x01` (Dog unavailable)
       - Teleport boy+dog to `[0,0]`; hide status bar
       - Set up camera to center of room
       - Load Queen NPC (0x96>>1) at `[1f,17]` → `$2836`; face south
       - Load Eronio NPC (0x31>>1) at `[1f,57]` → `$283a`; face east
       - Load guard NPC (0x48>>1) at `[1f,57]` → `$2838`; face south
       - PLAY MUSIC 0x18; fade in
       - Brightness fade in; display extended dialog (Queen ↔ Eronio dialogue about sending the boy "on a little journey")
       - Brightness fade out; fade music
       - `$2261&=0xfd`, `$2261&=0xfe` (restore availability)
       - Show status bar; `$238f = 0x0003`
       - CHANGE MAP → 0x21 `[0058, 0058]` (Dark Forest Entrance)
     - END
   - Else if `$22de&0x04` already set: skip to cinematic call
7. **If `($234b & 0xff) == 0x8e` or `$2354 & 0xff`** (returning from chessboard area or mission given):
   - If NOT `$22de&0x04` (audience not yet watched): load Queen+Eronio NPCs at their positions with ambient talk scripts (0x19b9, 0x19bc)
   - `CALL 0x92de75`; END
8. **Default** (first visit, `$234b != 0x8d/0x8e` and `$2354 == 0`):
   - `$234b = 0x0000`
   - RCALL 0x989838 — **"Queen Audience" cutscene**:
     - Load Queen (0x96>>1) at `[1f,17]` → `$2836`; load Eronio (0x48>>1) at `[1f,57]` → `$2838`; both script-controlled
     - Stop party; face north; open text box
     - Eronio and boy+dog perform an elaborate choreographed walk to approach the throne (four-phase movement: west, north, west, north, with YIELD pauses)
     - Open message box; Eronio: *"Your majesty. I've brought the prisoners as requested."*
     - Queen delivers mission briefing (7 dialog segments):
       - *"Ah! Mr. [name]! So nice to see that you made it through the night."*
       - *"I didn't mean to react so harshly at the banquet."*
       - *"But I just hate it when things don't go as planned!"*
       - *(Boy:) "Uh, that's OK. We're really sorry for the mess we made. And we're hoping, maybe, you could help us find our way home?"*
       - *"There will be time for that later! This meeting is really about me-- my needs!"*
       - *"…Ebon Keep is our former home and it is filthy. … I want to remove them! And you can help me do that!"*
       - *"What we need you to do is go down into the ravine … and open the drawbridge from within."*
       - *"You'll find it when you get there."*
     - `$2354 = 0x0001` (mission given); return party to player control

---

## Step-On Table

| Tile(s) | Action |
|---------|--------|
| `[1c,47:23,48]` | **Queen's Key pickup**: if `$2352&0xff` AND `$2354&0xff` AND `$2353==0` AND NOT `$2259&0x40`: stop party, face characters, show dialog: *"Well, [dog name]. Looks like we're off to Ebon Keep. Hey, what's that around your neck? A key! … I'll hang on to it."* → `$2264\|=0x10` (Queen's Key in inventory), `$2353=0x0001` (key given flag). Returns player control. |
| `[1e,4a:21,4c]` | Fade out; `$234b = 0x0064`; → 0x6e `[0090, 0088]` (Ivor Tower Hall) |
| `[11,39:13,3c]` | Fade out; `$234b = 0x0030`; → 0x77 `[01c8, 0120]` (Puppet Show / Mungola, upper) |
| `[10,2b:12,2f]` | Fade out; `$234b = 0x0031`; → 0x77 `[01c8, 00a8]` (Puppet Show / Mungola, lower) |

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$22ee` | 0x80 | R/W | 📖 Mungola defeated (triggers collapse cutscene; set in 0x77) |
| `$22de` | 0x04 | R/W | 📖 Queen Below Chessboard cutscene watched (one-shot guard) |
| `$2261` | 0x01 | R/W | 📖 Dog unavailable |
| `$2261` | 0x02 | R/W | 📖 Boy unavailable |
| `$2259` | 0x40 | R | Unknown availability/state flag |
| `$2264` | 0x10 | W | 💎 Queen's Key obtained |
| `$2352` | word (low byte) | R | ⚙️ Companion warning dialog active |
| `$2353` | word (low byte) | R/W | 📖 Queen's Key on boy (0=no, 1=yes) |
| `$2354` | word (low byte) | R/W | 📖 Queen's mission given (`0x0001` = yes) |
| `$2443` | word | W | Dog sprite (Poodle) |
| `$23bf` | word | W | Unknown (set to 0x0001) |
| `$234b` | byte (low) | R/W | Entry source code (0x8d = from Queen below chessboard; 0x8e = returning) |
| `$238d` | word | R | Music lock |
| `$238f` | word | W | Entry routing to 0x21 (0x0003 = "dark forest entrance") |
| `$2409/$240b` | word | W | Screen shake magnitude |
| `$2834` | word | W | Eronio NPC pointer (collapse cutscene) |
| `$2836` | word | W | Queen NPC pointer |
| `$2838` | word | W | Guard/Eronio NPC pointer |
| `$283a` | word | W | Eronio NPC pointer (side dialog) |

## Notes

- Three completely distinct cutscene paths branch on entry: post-Mungola collapse (`$22ee&0x80`), first Queen audience (`$234b==0x8d` with `$22de&0x04` clear), or normal mission briefing (default).
- The Queen's Key (`$2264&0x10`, tracked in `$2353`) is obtained via a step-on here; it persists across map changes and is consumed by the 19 Queen's Key Doors in 0x71.
- `$2354=0x0001` (Queen's mission given) gates the escape cutscene in 0x6e — without this flag set, 0x6e plays the escape cinematic again on re-entry.
