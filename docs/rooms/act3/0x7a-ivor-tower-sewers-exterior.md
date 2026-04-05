# Room 0x7a — Gothica: Ivor Tower Sewers Exterior (Landing Spot)

| Field | Value |
|-------|-------|
| **Room ID** | 0x7a |
| **Act** | 3 — Gothica |
| **Data** | `0x9fffcf` |
| **Enter script** | `0x92827d` → `0x98b817` |
| **Dog sprite** | Poodle (`$2443=0x08` on enter) |
| **Music** | 0x56 |
| **Step-ons** | 2 entries |
| **B-triggers** | 0 entries |
| **Connections** | 0x79 (Ivor Tower Sewers) |

---

## Overview

A small exterior ledge/platform outside the sewer entrance — the landing spot where the player arrives when exiting 0x79 through the upper drain passage. Primarily a transition area. Has two distinct cinematic paths on entry:

1. **Sterling escort cutscene** (`$22f5&0x08` set): "helped out of sewer" cinematic. Corrosion Guy loads and walks the player out of the sewer via an interpolated-position animation sequence.
2. **Normal re-entry**: if Sterling is dead (`$22dd&0x02`) and windwalker NOT yet unlocked (`$22dc&0x08` clear), Corrosion Guy NPC is loaded as a stationary NPC. Otherwise, no NPC.

Also: if `$22ee&0x01` is set on entry, it triggers a special positioning sequence — teleport boy to `[0f,0b]`, set positions via `$24ab/$24af`, face south. This flag is cleared on entry.

---

## Enter Logic

1. If NOT `$22eb&0x20`: teleport both to `[19,09]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. `$2443 = 0x08` (Poodle)
4. If music not locked: PLAY MUSIC 0x56; fade in
5. If `$22ee&0x01` (entry landing flag):
   - `$22ee &= 0xfe` (clear flag)
   - `$238f = 0x000f` (special entry type)
   - Teleport boy to `[0f,0b]`; set `$24ab=0x0058`, `$24af=0x0078`; teleport dog relative
   - Face both south
6. `$23bf = 0x0001`
7. If `$22f5&0x08` (Sterling escort cutscene active):
   - Stop both characters
   - Save camera registers `$23e9/$23eb/$23ed/$23ef` to `$2834/$2836/$2838/$283a` (preserve camera state)
   - Tighten camera to player position + small window
   - Load Sterling NPC (0x88>>1, flags/state 0002) at `[2d,07]` → `$2846`
   - **RCALL 0x98b545** — "climb out of sewer" animation:
     - Teleport boy+dog to `[07,2d]`
     - Load Corrosion Guy (NPC 0x102>>1) at `[2d,07]` → `$2848`; face west; talk script 0x19ce
     - Brightness ramp 0→15 (fade in over ~45 frames)
     - Record player position into `$249d/$249f`; set destination `$24a1=0x0058/$24a3=0x0078`
     - Face boy, dog, Corrosion Guy west; face Sterling west
     - **Interpolation loop** (`$2844=0x0064` steps): smoothly lerp boy+dog+Corrosion Guy from current pos to destination (`$24a1/$24a3`)
     - After lerp: dog walks north by 1; dog faces west; Corrosion Guy walks west by 2; Corrosion Guy faces south/east/east; walk Corrosion Guy to final position `[68,38]`
     - Second lerp for Corrosion Guy only
     - Boy walks south by 1; faces west
     - Trigger Corrosion Guy talk script (0x19ce)
     - Return player+Corrosion Guy to AI control; clear `$22f5&0x08`
   - Restore camera from saved `$2834/$2836/$2838/$283a`
   - END
8. Else if `($22dd&0x02) && !($22dc&0x08)` (Sterling dead, windwalker not yet unlocked):
   - Load Corrosion Guy (NPC 0x102>>1) at `[0b,0f]` → `$2848`; set talk script 0x19ce
9. `CALL 0x92de75` (cinematic setup); END

---

## Step-On Table

| Tile(s) | Action |
|---------|--------|
| `[0d,0d:0e,0e]` | **Wall-slide down into sewers** — animates player hanging and swinging down the sewer wall. Uses sprite `0x0026`/`0x0066` (hanging). Loop decrements `$24a7` from `0xfffe` (−2) incrementally while `< 0x22`: offset y by `$24a7`, offset x by +16 each tick, teleport each frame. Plays the same for the non-controlled character via RCALL. Returns control when animation ends. |
| `[09,07:0b,09]` | `$22dd &= 0xbf` (clear "Load east castle"); → 0x79 `[06f8, 0330]` (Ivor Tower Sewers) |

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$22ee` | 0x01 | R/W | 📖 Entry landing flag (cleared on entry; set from 0x7a's own step-on or from 0x6e) |
| `$22ee` | 0x80 | W | Set at end of 0x77 Mungola fight (triggers Queen cutscene in 0x78) |
| `$22f5` | 0x08 | R/W | 📖 Sterling escort cutscene flag (cleared after cinematic runs) |
| `$22dd` | 0x02 | R | 📖 Sterling dead |
| `$22dc` | 0x08 | R | 📖 Windwalker unlocked |
| `$22dd` | 0x40 | W | Load east castle (cleared when entering 0x79) |
| `$2443` | word | W | Dog sprite |
| `$23bf` | word | W | Unknown (set to 0x0001) |
| `$238d` | word | R | Music lock |
| `$238f` | word | W | Entry source (0x000f = special landing) |
| `$2834/$2836/$2838/$283a` | word | W | Saved camera registers (during cinematic only) |
| `$23e9/$23eb/$23ed/$23ef` | word | W | Camera scroll registers |
| `$2846/$2848` | word | W | Sterling / Corrosion Guy NPC pointers |

## Notes

- Features the only custom per-frame animation step-on in Act 3: the wall-slide into the sewer uses a `$24a7` decrement loop with hanging sprites (`0x0026`/`0x0066`), executed each frame until the animation completes.
- `$22f5&0x08` (Sterling escort cutscene) triggers a cinematic on the first post-sewer entry; the flag clears after running, and subsequent entries use the normal stationary-NPC path.
- `$22dd&0x40` (Load east castle) is explicitly cleared when stepping into 0x79, ensuring the sewer correctly uses the west-castle dungeon path rather than the Ivor Tower side.
