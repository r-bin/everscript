# Room 0x5f — Gothica: Ebon Keep Verm Side Rooms

| Field | Value |
|-------|-------|
| **Room ID** | 0x5f |
| **Act** | 3 — Gothica |
| **Data** | `0x9fff63` |
| **Enter script** | `0x9281f6` → `0x9a8286` |
| **Dog sprite** | Default (no override) |
| **Music** | 0x66 (Verminator battle) / 0x6e (after Verm dead) |
| **Step-ons** | 4 entries |
| **B-triggers** | 0 entries |
| **Connections** | 0x5d (Ebon Keep Courtyard, 2 exits south), 0x5e (Ebon Keep Front Room, 2 exits east/west) |

---

## Overview

Two large side chambers flanking the main Ebon Keep area — a combined room containing both halves of the Verm side-wing. Heavily populated with Ratling variants (NPC 0x7c, a tougher variant). No gourds or sniff spots. Music matches 0x5e (Verm battle / post-Verm). Uses two ABS display-setup scripts on entry.

---

## Enter Logic

1. If NOT `$22eb&0x20`: teleport both to `[4d,69]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. CALL 0x92d8ff WITH arg 0x40 (camera/area setup)
4. CALL 0x92d8e9 WITH arg 0x60 (camera/area setup)
5. Set enemy loot: Prize 1 = Bead (0x0801) ×100, Prize 2 = Talons (0x0001) qty 0x50 ×30, Prize 3 = Call Beads (0x0807) ×2
6. `$2433 = 0x0001`; spawn 34 NPC 0x7c (Verm Grunt) spawners spread across both chambers
7. If music not locked:
   - If `$22dd&0x01` (Verm dead): PLAY MUSIC 0x6e
   - Else: PLAY MUSIC 0x66
   - Fade in
8. `$23bf = 0x0000`; `CALL 0x92de75`; END

---

## Step-On Table

| Tile(s) | Action |
|---------|--------|
| `[15,43:17,46]` | Fade out; `$23b9 = 0x0001`; → 0x5d `[0030, 0118]` (Ebon Keep Courtyard, left exit) |
| `[3b,43:3d,46]` | Fade out; `$23b9 = 0x0002`; → 0x5d `[0110, 0118]` (Ebon Keep Courtyard, right exit) |
| `[1d,25:20,27]` | → 0x5e `[0018, 01c0]` (Ebon Keep Front Room, left/west) |
| `[30,25:33,27]` | → 0x5e `[0148, 01c0]` (Ebon Keep Front Room, right/east) |

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$22dd` | 0x01 | R | 📖 Verminator dead (music switch) |
| `$23bf` | word | W | Unknown (cleared) |
| `$2433` | word | W | Enemy spawn count |
| `$238d` | word | R | Music lock |
| `$23b9` | word | W | Entrance selector for 0x5d (1 = left, 2 = right) |

## Notes

- The two side chambers share a single room script and load 34 Ratling Grunts (NPC 0x7c, a tougher variant than the standard 0x42 Ratling) across both chambers.
- Exit direction to the courtyard (0x5d) is encoded in `$23b9` (1=left, 2=right); the courtyard reads this value to select which entrance barrier animation to play.
- No persistent content (no gourds, sniff spots) — purely a combat gauntlet. Drop table includes Call Beads as a rare prize.
