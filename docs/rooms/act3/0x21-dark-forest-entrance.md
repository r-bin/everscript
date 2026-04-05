# [0x21] Gothica — Dark Forest Entrance

| Field | Value |
|-------|-------|
| Room ID | 0x21 |
| Name | Gothica - Dark Forest Entrance |
| Act | Act 3 — Gothica |
| Data offset | `0xacf37c` |
| Enter script | `0x9280c0` → `0x99a7fa` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | 0x46 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | NPC 0x55 (VILLAGER?) at `[09,15]` → talk `0x1a55` (always loaded) |
| Forced dog form | Poodle (0x08) |
| Music | 0x46 |

---

## Overview

A small outdoor area serving as the transition between the underground chessboard region (0x1a) to the north and the Dark Forest (0x22) to the south. Contains a single NPC (0x55) at `[09,15]`. A save point is accessible here. The room is also the exit destination from the Below Chessboard (0x1a) once the Queen cutscene has been watched.

If `$22ee&0x01` is set on entry (intro/outro flag), the boy is repositioned and the flag is cleared — used for scripted arrival sequences.

---

## Enter Script Logic

1. Set dog = Poodle (`$2443 = 0x08`)
2. If `$22eb&0x20` (in-animation guard): teleport both to `[09,15]`, fade-out
3. Load NPC 0x55 at `[09,15]` → talk `0x1a55` (unconditional)
4. If `$22ee&0x01` (intro/outro positioning flag):
   - `$238f = 0x000f` (scroll lock)
   - Clear `$22ee&0x01`
   - Teleport boy to `[0x30,0x98]`, then `[0x40,0x98]`, facing south
5. Music 0x46 if `$238d == 0x00`
6. `$23bf = 0x0001`
7. Cinematic script `0x92de75`

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[03,14:11,16]` | MAP 0x22 @ `[0x0080\|0x0138]` | South → Dark Forest; `$24f7 = 0xfffa` |
| `[07,09:0a,0a]` | MAP 0x1a @ `[0x02f8\|0x0508]` | North → Below Chessboard (global script 0x26) |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22ee` | 0x01 | R/W | 📖 Intro/outro arrival positioning flag — clears on entry, repositions boy |
| `$238f` | — | W | 🎥 Scroll/camera lock — set to 0x000f when `$22ee&0x01` is active |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |
| `$24f7` | — | W | ⚙️ Set to 0xfffa on south step-on (map transition parameter) |
| `$2443` | — | W | ⚙️ Dog form forced to Poodle (0x08) |

## Notes

- A pure transit room with no gourds, sniff spots, or enemies — the only scripted content is the step-on transitions and one always-loaded NPC.
- Dog form is permanently forced to Poodle (`$2443=0x08`) here, consistent with all Act 3 overworld-adjacent rooms.
- `$22ee&0x01` (arrival repositioning flag) is set by outro paths (e.g., the 0x78 teleport after the Queen's below-chessboard cutscene) and clears on entry, adjusting the boy's spawn position via `$238f=0x000f`.
