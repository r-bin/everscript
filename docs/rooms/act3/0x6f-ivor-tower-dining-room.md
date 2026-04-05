# [0x6f] Gothica — Ivor Tower Dining Room

| Field | Value |
|-------|-------|
| Room ID | 0x6f |
| Name | Gothica - Ivor Tower Dining Room |
| Act | Act 3 — Gothica |
| Data offset | `0xaadfdf` |
| Enter script | `0x928246` → `0x9ac384` |
| Step-ons | 2 |
| B-triggers | 2 |
| Music | 0x74 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 2 |
| Gourds | 2 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | Queen Bluegarden `$0090>>1=0x48` at `[3b,21]`; Verminator `$0096>>1=0x4b` at `[3b,21]` or `[27,21]`; NPC `0xa6>>1=0x53` at `[14,2a]` |
| Forced dog form | Poodle (0x08) |
| Music | 0x74 |

---

## Overview

The royal dining hall of Ivor Tower. Features two major cutscenes triggered by arrival from different directions — the "banquet incident" where boy+dog cause a scene with the queen, leading to their arrest and imprisonment in the dungeon.

- **Cutscene 1** (`$234b==0x89`, entering from the Ivor Tower Hall): Full banquet intro, dog lands on the table, queen orders boy+dog to the kitchen/guards. → CHANGE MAP 0x71 (East Room + Kitchen)
- **Cutscene 2** (`$234b==0x50`, entering from the Kitchen): Second meeting — queen questions boy about her castle; dog ruins the meal again. → CHANGE MAP 0x74 (Dungeon)

Both cutscenes include a save prompt (*"I'd rather call a lawyer"*) before going to the dungeon.

---

## Enter Script Logic

1. **IF `$22ee&0x01`** (unknown flag): clear it; guard `$22eb&0x20`; hide status bar; `$238d=1`; CHANGE MAP 0x74 @ `[0x0178|0x0068]` (Dungeon) — forced dungeon warp
2. Guard `$22eb&0x20`; teleport both to `[1e,39]`; fade-out
3. Dog = Poodle
4. If `$22e5&0x40` (West castle collapsed): unload OBJs 14–17, 19–23; `$2437=0x0007`
5. Play music 0x74 (if not already playing)
6. `$23bf = 0x0001`
7. **IF `$234b==0x89`** AND NOT `$22de&0x10`: set `$22de|=0x10`; RCALL 0x9abed9 (Banquet cutscene 1 — see below)
8. **IF `$234b==0x50`** AND NOT `$22de&0x20`: set `$22de|=0x20`; RCALL 0x9ac0f7 (Banquet cutscene 2 — see below)
9. Else: cinematic; **END**

---

## Banquet Cutscene 1 (RCALL 0x9abed9 — `$234b==0x89`)

Triggered first time entering from the Ivor Tower Hall (`$234b==0x89`).

- Dog hidden (`$2261|=0x01`); dog teleported to x=0, y=0
- NPCs loaded: Verminator `$0096>>1=0x4b` at `[3b,21]`, Queen `$0090>>1=0x48` at `[3b,21]`, NPC `0xa6>>1=0x53` at `[14,2a]`
- Banquet OBJs 1–7 loaded
- Dialog:
  - Verminator: *"Hey, [boy]! Where did you run off to? I hope he doesn't get into too much trouble."*
  - Announcer: *"Honored guests and assorted rabble! May I have your attention, please!"* / *"Dinner will begin once her majesty arrives."*
  - Boy: *"Wow! This is some fancy castle!"*
  - NPC: *"I've heard that Phlegm the Fancy did the decorating... gold paint on their backsides... Phlegm has such taste!"*
  - *"EVERYONE! Please be seated! The queen is about to arrive!"*
  - Camera scroll; Queen's NPC enters: *"People of Ivor Tower, distinguished guests, I present to you, her majesty, the Queen!"*
  - Queen: *"Thank you all so much for attending!"* / *"And who do we have here?"*
  - Verminator: *"This young man is [boy], the owner of the winning pig, your highness."*
  - Queen: *"It is a great pleasure to meet you, Mr. [boy]. You may call me Queen Bluegarden."*
  - Boy: *"Uh, hi. You haven't seen my dog, er, pig, er, pigdog, have you? He followed me into the castle, and then he just disappeared!"*
  - Dog slides onto banquet table (frame-by-frame animation)
  - Queen: *"This is an outrage! Who is responsible for this filthy beast? Names!! I want names!!"*
  - Boy: *"Uh, th_ that would be me."*
  - Verminator: *"Make a mockery of my banquet, will you? Let's see how you feel after a night in the dungeon. Guards! Take these mockers away!"*
  - Naris(?): *"Ok, buddy. Had your fun? ... And your furry friend... He looks like a real trouble maker. Come along now!"*
- `$2261|=0x02` (Boy unavailable); `$22eb|=0x20`; `$234b=0x0060`
- CHANGE MAP 0x71 @ `[0x0280|0x0568]` (Ivor Tower East Room + Kitchen)

---

## Banquet Cutscene 2 (RCALL 0x9ac0f7 — `$234b==0x50`)

Triggered the second time entering from the Kitchen (`$234b==0x50`).

- Dog re-enabled with walk-in animation (slides across floor)
- NPCs loaded: Verminator at `[27,21]`, Queen at `[3b,21]`; OBJs 1–12 loaded
- Dialog:
  - Queen: *"So, tell me, Mr. [boy], what do you think of my new castle?"*
  - Boy: *"I like it! It's really_"* / Queen: *"Clean? Immaculate? Spotless? Without flaw?"* / Boy: *"Yeah, sure. I guess."*
  - Queen: *"It is well past time for the main dish... Where is my meal?"*
  - Dog slides onto table; bell sounds
  - Queen: *"This is an outrage! Who is responsible for this filthy beast? Names!!"*
  - Boy: *"Uh, th_ that would be me."*
  - Verminator: *"Ok, buddy... Come along now!"*
- Save spot = 0x001d; save dialog: *"Would you like to record your progress? / OK / I'd rather call a lawyer."*
- `$22eb|=0x20`; `$234b=0x0000`; CHANGE MAP 0x74 @ `[0x0178|0x0068]` (Dungeon)

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[54,2e:56,31]` | MAP 0x70 @ `[0x0008\|0x0148]` | East → Ivor Tower Exterior Bridges and Balconies |
| `[45,3a:49,3c]` | MAP 0x6e @ `[0x01f0\|0x0228]` | South → Ivor Tower Hall |

---

## B-Trigger Scripts

| Tile | Contents | Guard | Notes |
|------|----------|-------|-------|
| `[3b,25:3d,26]` | 🫙 Water (0x0201) qty 2 — MAP REF 0x0018 | `$22d8&0x01` | West gourd |
| `[51,25:53,26]` | 🫙 Wax (0x0200) qty 1 — MAP REF 0x0019 | `$22d8&0x02` | East gourd |

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22ee` | 0x01 | R/W | 📖 Force dungeon warp on entry (unknown trigger) |
| `$22e5` | 0x40 | R | 📖 West castle collapsed — unload castle OBJs |
| `$22de` | 0x10 | R/W | 📖 Banquet cutscene 1 done (flag guard) |
| `$22de` | 0x20 | R/W | 📖 Banquet cutscene 2 done (flag guard) |
| `$234b` | — | R/W | ⚙️ Entry source — 0x89 = from Hall; 0x50 = from Kitchen; 0x60 = written for Kitchen exit |
| `$2437` | — | W | ⚙️ Set to 0x0007 if West castle collapsed |
| `$22d8` | 0x01 | R/W | 🫙 Gourd MAP REF 0x0018 looted (Water) |
| `$22d8` | 0x02 | R/W | 🫙 Gourd MAP REF 0x0019 looted (Wax) |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |
| `$2261` | 0x01 | W | ⚙️ Dog unavailable — set in banquet cutscene 1 |
| `$2261` | 0x02 | W | ⚙️ Boy unavailable — set in banquet cutscene 1 |

## Notes

- Two sequential banquet cutscenes (`$22de&0x10` and `$22de&0x20`) each play exactly once, involving Queen Bluegarden and Verminator; both characters/OBJs are disabled during the scenes.
- If `$22e5&0x40` (west castle collapsed), castle OBJs are force-unloaded on entry and `$2437=0x0007` is set — the collapsed-castle branch mirrors behavior in 0x71 and 0x72.
- `$22ee&0x01` triggers a forced dungeon warp on entry; the origin of this flag is undocumented and may come from a dungeon-escape path in 0x74.
