# [0x70] Gothica — Ivor Tower Exterior Bridges and Balconies

| Field | Value |
|-------|-------|
| Room ID | 0x70 |
| Name | Gothica - Ivor Tower Exterior Bridges and Balconies |
| Act | Act 3 — Gothica |
| Data offset | `0xa9cb12` |
| Enter script | `0x92824b` → `0x9ad361` |
| Step-ons | 10 |
| B-triggers | 0 |
| Music | 0x82 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 10 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | Camellia `$2838` = NPC `0x62>>1=0x31` at `[75,27]`; unnamed `$2836` = NPC `0x96>>1=0x4b` at `[61,27]` (both in telescope RCALL) |
| Forced dog form | Poodle (0x08) |
| Music | 0x82 |

---

## Overview

The exterior bridges and balconies of Ivor Tower, overlooking the castle grounds. Contains the telescope used by the enemy faction to surveil the kingdom.

The room's primary story event is the **telescope cutscene** (`$22ef&0x08`): Boy + dog watch through the telescope as the enemy commanders (Camellia and her superior) discuss their plan to find the "special device" (Tinker's machine). This ends with a CHANGE MAP to 0x14 (Tinker's Room), initiating the Tinker questline.

The exterior is split into two camera zones controlled by `$234b & 0xf0`:
- Zone 0xa0: scroll limits `[0x0000,0x0000]`→`[0x0200,0x01c0]`
- Zone 0xb0: scroll limits `[0x0270,0x0000]`→`[0x0470,0x01c0]`

---

## Enter Script Logic

1. If `$22f4&0x02`: `$2261|=0x02` (Boy unavailable)
2. Guard `$22eb&0x20`; teleport both to `[07,27]`; fade-out
3. Dog = Poodle
4. Set camera bounds based on `$234b & 0xf0` (zone 0xa0 or 0xb0)
5. Play music 0x82 (if not already playing)
6. **IF `$22ef&0x08`** (telescope scene pending): RCALL 0x9ad29c (telescope cutscene — see below)
7. Else: cinematic; **END**

---

## Telescope Cutscene (RCALL 0x9ad29c — `$22ef&0x08`)

Triggered when `$22ef&0x08` is set (written in Tinker's Room 0x14 when Tinker shows telescope).

- Set camera to `[0x0300|0x00b0]`
- Load Camellia `$2838` = NPC `0x62>>1=0x31` at `[75,27]`; load other commander `$2836` = NPC `0x4b` at `[61,27]`
- Boy + dog hidden (teleported to `[1,1]`); fade animation
- World map animation calls (`0x92dade`, `0x92db66`, `0x92db56`, `0x92db6b`, `0x92db61`) — telescope visual sequence
- Commander `$2836` walks to `[6f,27]`; Camellia `$2838` faces west
- Dialog:
  - Commander: *"I have orders from above, Eronio. We are to find a device that produces a special kind of energy. It is somewhere in the kingdom, but there is no specific information as to its whereabouts."*
  - Commander: *"My superior has ordered me to do whatever it takes to find it_"*
  - Camellia: *"_even if we must tear the kingdom apart,"*
  - Commander (east-facing): *"piece by piece."*
  - Camellia: *"But, your highness, won't the citizens be suspicious?"*
  - Commander: *"I'll deal with those cretins when the time comes."*
  - *"Now, let's find that device!"*
- Fade; show status bar; CHANGE MAP 0x14 @ `[0x00e8|0x0070]` (Ebon Keep Tinker's Room)

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[3f,21:41,24]` | MAP 0x71 @ `[0x0728\|0x0488]` | East end → Ivor Tower East Room + Kitchen (west entrance) |
| `[25,21:27,24]` | MAP 0x71 @ `[0x0038\|0x0488]` | West end → Ivor Tower East Room + Kitchen (east entrance) |
| `[54,20:56,24]` | MAP 0x19 @ `[0x0008\|0x0210]` | Far east → Chessboard (east exit) |
| `[37,1e:39,21]` | MAP 0x72 @ `[0x03a8\|0x02f0]` | Bridge → Ivor Tower East Upper Floor (code 0xb0) |
| `[37,19:39,1c]` | MAP 0x72 @ `[0x03a8\|0x01e0]` | Bridge → Ivor Tower East Upper Floor (code 0xb0) |
| `[37,14:39,17]` | MAP 0x72 @ `[0x03a8\|0x00d0]` | Bridge → Ivor Tower East Upper Floor (code 0xb0) |
| `[10,20:12,24]` | MAP 0x6f @ `[0x01d8\|0x0108]` | West end → Ivor Tower Dining Room |
| `[2e,1e:30,21]` | MAP 0x72 @ `[0x0028\|0x02f0]` | Bridge → Ivor Tower East Upper Floor (code 0xa0) |
| `[2e,19:30,1c]` | MAP 0x72 @ `[0x0028\|0x01e0]` | Bridge → Ivor Tower East Upper Floor (code 0xa0) |
| `[2e,14:30,17]` | MAP 0x72 @ `[0x0028\|0x00d0]` | Bridge → Ivor Tower East Upper Floor (code 0xa0) |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22f4` | 0x02 | R | ⚙️ Boy unavailable flag |
| `$22ef` | 0x08 | R | 📖 Telescope scene pending — triggers RCALL; set in 0x14 enter |
| `$234b` | — | R | ⚙️ Entry source — high nibble `& 0xf0` selects camera zone (0xa0 or 0xb0) |
| `$2836` | — | W | ⚙️ Commander NPC pointer (NPC 0x4b at `[61,27]`) |
| `$2838` | — | W | ⚙️ Camellia NPC pointer (NPC 0x31 at `[75,27]`) |
| `$2261` | 0x02 | W | ⚙️ Boy unavailable — set if `$22f4&0x02` |

## Notes

- The telescope cutscene RCALL fires once when `$22ef&0x08` is set (flag written by 0x14 Tinker's Room enter script after the rocket is ready); Camellia and a Commander NPC are loaded for it.
- Camera zone on entry is selected by the high nibble of `$234b` (`0xa0` = lower bridge level, `0xb0` = upper); this shared encoding also appears in 0x71 and 0x72 vent-exit routing.
- Boy unavailability (`$22f4&0x02`) is propagated here from the 0x71 dog-rescue sequence and suppresses `$2261|=0x02` on entry.
