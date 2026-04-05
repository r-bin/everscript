# 0x45 — Omnitopia: Secret Boss Room

| Key | Value |
|-----|-------|
| ROM | `0x9ffefb` |
| Data | `0xabebf5` |
| Enter script | `0x9b88db` |
| Step-ons | 2 entries @ `0xabec04` |
| B-triggers | 0 (none) |
| Music | 0x88 (ambient) → 0x24 (boss fight) |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (enemies active) |

---

## Overview

The Secret Boss Room is a hidden chamber accessible only by entering the correct 3-digit secret-door code at the Control Room terminal (0x43) or by crawling through the duct above the terminal. It houses a pair of FACE_ENTITY enemies ("Face", #124) and contains the "secret boss" fight of Omnitopia. The room is entered via a vertical slide-down from 0x43 OBJ 2. Once the boss is defeated (`$22e6&0x80`), the room becomes peaceful. The return exit goes back to 0x43 and sets `$22f9&0x04` (secret door open flag). There are no B-triggers and no looted items.

---

## Enter Logic

```
0x9b88db:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both to (0x09, 0x11)
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE $2348 = 0x0009
  WRITE $23bf = 0x0000

  PLAY MUSIC 0x88
  SET OBJ 2 STATE = 0x7e         // load room object

  if !$22e6&0x80:                 // boss alive
    PLAY MUSIC 0x24               // boss battle music
    LOAD FACE_ENTITY (0x7d) at (0x09, 0x11) → $2835
    SET kill script 0x1b1b for $2835
    LOAD FACE_ENTITY (0x7d) at (0x27, 0x11) → $2837
    SET kill script 0x1b1e for $2837

  CALL palette script 0x92d8e9 WITH 0x60
  CALL palette script 0x92d8ff WITH 0x80

  if $22f8&0x04:                  // arrived via hatch
    CALL "Omnitopia hatch fade-in"
    $22f8 &= 0xfb
    END
  else:
    CALL "Some cinematic script"
    END
```

---

## Step-On Zones

| Zone (tile) | Condition | Action |
|-------------|-----------|--------|
| `[28,32:2a,33]` | — | Walk both to pos, CALL ABS script `0x92ded8`, `$22f9\|=0x04`, fade-out → **CHANGE MAP 0x43** @ [0x00e0, 0x0050] |
| `[16,29:1a,2a]` | `!$2834&0x04 && !$22e6&0x80` | `$2834\|=0x04`, walk to (0x18, 0x31), SET OBJ 2 STATE=0, PLAY MUSIC 0x24, CALL `0x9b8995` + `0x9b89c9` (boss fight setup) |

The second step-on is the boss encounter trigger in the middle of the room. It only fires once per session (`$2834&0x04`) and only if the boss is still alive (`!$22e6&0x80`). The first step-on is the south-wall exit hatch back to 0x43; it sets `$22f9&0x04` (secret door open), which causes 0x43 to enter with dog-in-duct mode.

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x43 Control Room | Slide-down via OBJ 2 (B-trigger in 0x43) or direct CHANGE MAP from 0x43 |
| Out | 0x43 Control Room | Step-on `[28,32:2a,33]` — sets `$22f9&0x04` |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22e6` | `0x80` | 📖 | Boss defeated flag — if set, FACE_ENTITYs not loaded; music stays ambient |
| `$22f8` | `0x04` | ⚙️ | Hatch-entry flag (set by 0x43); cleared on enter after fade-in |
| `$22f9` | `0x04` | 📖 | Secret door open (set on exit); causes 0x43 to unlock duct route |
| `$2834` | `0x04` | ⚙️ | Boss encounter triggered this session (session-only guard) |
| `$2835` | — | ⚙️ | FACE_ENTITY #1 entity handle |
| `$2837` | — | ⚙️ | FACE_ENTITY #2 entity handle |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0 | Unknown (not referenced in enter script) |
| 1 | Unknown |
| 2 | Room barrier / floor hatch (state 0x7e = loaded; state 0 = closed during boss fight) |

---

## Notes

- The FACE_ENTITY ("Face", NPC 0x7d, enemy #124) is unique to this room; it is the secret boss of Omnitopia.
- Kill scripts 0x1b1b and 0x1b1e handle the two FACE_ENTITY deaths. When both are dead, one of the kill scripts presumably sets `$22e6&0x80`.
- The boss fight subroutines (`0x9b8995` and `0x9b89c9`) are not crawled here; they likely contain the full combat choreography.
- `$2834&0x04` is a session-only trigger guard (not written to SRAM); killing the boss without leaving and returning will not re-trigger the encounter.
- OBJ 2 is SET 0x7e on every enter, then SET 0 when the boss encounter step-on fires — this probably opens a gate or shows the arena floor.
- The palette scripts `0x92d8e9` (arg 0x60) and `0x92d8ff` (arg 0x80) apply a dark room effect, same as in 0x47 and 0x44 when lights are off.
