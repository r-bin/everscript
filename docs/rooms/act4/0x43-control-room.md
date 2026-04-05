# 0x43 — Omnitopia: Control Room

| Key | Value |
|-----|-------|
| ROM | `0x9ffef3` |
| Data | `0xaba9f5` |
| Enter script | `0x9b8000` |
| Step-ons | 1 entry @ `0xabaa04` |
| B-triggers | 6 entries @ `0xabaa0c` (len=0x0024) |
| Music | 0x3c |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (enemies active) |

---

## Overview

The Control Room is the puzzle hub of Omnitopia and the most complex room in act 4. On first entry (to either this room or the Shops, 0x54), a set of six random digits is generated and stored in `$236d`–`$2377` — these form the two 3-digit codes for the entire playthrough. The room displays the current access code digits on three screen OBJs (3/4/5). Two FAN_BOTs ("Floating Fan", #127) guard the terminals. The dog uses a ventilation duct system to reach the Greenhouse (0x44), Storage Room (0x47), and Alarm Room (0x00). The boy uses the main terminal to enter one of two codes: the access code (disables the alarm, sends both to 0x00) or the secret door code (opens OBJ 2, allowing entry to the Secret Boss Room 0x45). A secondary B-trigger sends the dog directly into the alarm from above. The single exit step-on returns to the Metroplex Tunnels (0x48).

---

## Enter Logic

```
0x9b8000:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE $2348 = 0x0009
  WRITE $23bf = 0x0000

  PLAY MUSIC 0x3c

  // Code generation (also runs in 0x54 Shops — whichever is visited first)
  if !$22e6&0x08:
    CALL 0x9b814e                   // generate access + secret-door codes

  // Show code display if alarm already cleared
  if $22e6&0x10:
    set OBJ 3/4/5 states from $236d/$236f/$2371

  // Secret door state
  if $22f9&0x02: SET OBJ 2 STATE = 9   // knock hole visible

  // FAN_BOT #1
  if !$22f8&0x20:
    LOAD FAN_BOT (0x69) at (0x50, 0x17); SET OBJ 7 = 0x7e
  else:
    SET OBJ 7 = 0x7e                  // dead state
  if $22f8&0x40: SET OBJ 8 = 0x7e    // corpse/cleanup OBJ

  // FAN_BOT #2
  if !$22f8&0x80:
    LOAD FAN_BOT (0x69) at (0x50, 0x1d); SET OBJ 9 = 0x7e
  else:
    SET OBJ 9 = 0x7e
  if $22f9&0x01: SET OBJ 10 = 0x7e

  // Return from alarm room
  if $22f8&0x08:
    $2834 &= 0xfe                    // clear dog-duct mode
    CALL 0x9b8189                    // restore saved boy/dog positions
    if $22f8&0x10:
      CALL 0x9b8210                  // present code-entry dialog

  // Secret door open
  if $22f9&0x04:
    $2834 |= 0x01                    // dog in duct mode
    CALL 0x9b841c                    // secret door open sequence

  if $22f8&0x04:
    $2834 |= 0x01
    CALL "Omnitopia hatch fade-in"
    $22f8 &= 0xfb
    END
  else:
    $2834 |= 0x01
    CALL "Some cinematic script"
    END
```

### Code Generation (`0x9b814e`)

Called once per playthrough on first entry to 0x43 **or** 0x54 (whichever comes first).

```
$236d = RANDRANGE(1, 3)   // access code digit 1
$236f = RANDRANGE(1, 3)   // access code digit 2
$2371 = RANDRANGE(1, 3)   // access code digit 3
$2373 = RANDRANGE(1, 3)   // secret door code digit 1
$2375 = RANDRANGE(1, 3)   // secret door code digit 2
$2377 = RANDRANGE(1, 3)   // secret door code digit 3
$22e6 |= 0x08             // mark codes generated
```

---

## Step-On Zones

| Zone (tile) | Action |
|-------------|--------|
| `[3c,18:3e,19]` | Clear `$22f8&0x10`, walk to hatch, `$24fd = 14`, fade-out → **CHANGE MAP 0x48** |

---

## B-Trigger Zones

| Zone (tile) | Controller | Condition | Action |
|-------------|-----------|-----------|--------|
| `[1f,14:23,15]` | Either | `$22f9&0x02` (hole visible) | Slide-down animation: SET OBJ 2 state 0x7e→6, clear `$22f8&0x10`, CHANGE MAP **0x45** @ [0x01d0, 0x0270] |
| `[1f,15:23,16]` | Either | `!$22f9&0x02` | Knock on wall: SET OBJ 2 state=9, SFX 0xb0, `$22f9\|=0x02` |
| `[2b,1d:2e,20]` + `[2b,1e:2e,20]` | **Dog** | Dog-controlled + `$2834&0x01` | Save positions to `$24ff`/`$2501`/`$2503`/`$2505`, `$22f8\|=0x08`, `$22f8\|=0x10`, CHANGE MAP **0x00** @ [0x00b0, 0x07f0] |
| `[2b,1d:2e,20]` + `[2b,1e:2e,20]` | **Boy** | Boy-controlled | Code entry dialog (3 menus × 3 choices); if access code correct (`$2839==$236d`, `$283b==$236f`, `$283d==$2371`): `$22e6\|=0x10`, CHANGE MAP **0x00**; if secret code correct: camera → OBJ 2 projector sequence |
| `[23,1d:27,20]` | **Dog** | Dog-controlled + `$2834&0x01` | Save positions, `$22f8\|=0x08`, CHANGE MAP **0x44** @ [0x07e0, 0x07f8] |
| `[1a,1d:1e,20]` | **Dog** | Dog-controlled + `$2834&0x01` | Save positions, `$22f8\|=0x08`, CHANGE MAP **0x47** @ [0x0050, 0x0190] |

The terminal B-triggers (`[2b,1d]` and `[2b,1e]`) share the same script, which branches on whether boy or dog is the active controller.

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x48 Metroplex Tunnels | `$24fd = 14` (set by 0x48) |
| In | 0x00 Alarm Room | `$22f8&0x08` return path (positions restored by `0x9b8189`) |
| In | 0x45 Secret Boss Room | Step-on `[28,32:2a,33]` in 0x45 (sets `$22f9&0x04`) |
| Out | 0x48 Metroplex Tunnels | Step-on `[3c,18:3e,19]`, `$24fd=14` |
| Out (dog) | 0x00 Alarm Room | Terminal B-trigger: dog → CHANGE MAP 0x00 |
| Out (boy correct code) | 0x00 Alarm Room | Terminal B-trigger: boy + correct access code → CHANGE MAP 0x00 |
| Out (boy secret code) | 0x45 Secret Boss Room | B-trigger `[1f,14:23,15]`: slide-down after knock → CHANGE MAP 0x45 |
| Out (dog duct) | 0x44 Greenhouse | B-trigger `[23,1d:27,20]` |
| Out (dog duct) | 0x47 Storage Room | B-trigger `[1a,1d:1e,20]` |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22e6` | `0x08` | 📖 | Codes generated — set on first visit to 0x43 **or** 0x54 |
| `$22e6` | `0x10` | 📖 | Alarm disabled — set when boy enters correct access code |
| `$22f8` | `0x04` | ⚙️ | Hatch-entry flag; cleared after fade-in |
| `$22f8` | `0x08` | ⚙️ | Returned from alarm room; triggers position restore |
| `$22f8` | `0x10` | ⚙️ | Dog entered alarm room; triggers code dialog on return |
| `$22f8` | `0x20` | 📖 | FAN_BOT #1 killed |
| `$22f8` | `0x40` | ⚙️ | FAN_BOT #1 cleanup OBJ shown |
| `$22f8` | `0x80` | 📖 | FAN_BOT #2 killed |
| `$22f9` | `0x01` | ⚙️ | FAN_BOT #2 cleanup OBJ shown |
| `$22f9` | `0x02` | 📖 | Knock hole visible (OBJ 2 state=9) |
| `$22f9` | `0x04` | 📖 | Secret door open — set by 0x45 exit; enables slide-down |
| `$2834` | `0x01` | ⚙️ | Dog-in-duct mode (session-only) |
| `$236d` | — | ⚙️ | Access code digit 1 (1–3) |
| `$236f` | — | ⚙️ | Access code digit 2 (1–3) |
| `$2371` | — | ⚙️ | Access code digit 3 (1–3) |
| `$2373` | — | ⚙️ | Secret door code digit 1 (1–3) |
| `$2375` | — | ⚙️ | Secret door code digit 2 (1–3) |
| `$2377` | — | ⚙️ | Secret door code digit 3 (1–3) |
| `$24ff` | — | ⚙️ | Saved boy X position (before entering alarm) |
| `$2501` | — | ⚙️ | Saved boy Y position |
| `$2503` | — | ⚙️ | Saved dog X position |
| `$2505` | — | ⚙️ | Saved dog Y position |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0 | Unknown |
| 1 | Unknown |
| 2 | Secret door / wall panel (state 9 = knocked hole; state 6 = open for sliding; state 0x7e = closed) |
| 3 | Code display digit 1 (state = `$236d` value) |
| 4 | Code display digit 2 (state = `$236f` value) |
| 5 | Code display digit 3 (state = `$2371` value) |
| 6 | Unknown |
| 7 | FAN_BOT #1 spawn marker (SET 0x7e on enter) |
| 8 | FAN_BOT #1 cleanup OBJ (SET 0x7e if `$22f8&0x40`) |
| 9 | FAN_BOT #2 spawn marker (SET 0x7e on enter) |
| 10 | FAN_BOT #2 cleanup OBJ (SET 0x7e if `$22f9&0x01`) |

---

## Notes

- The code generation is shared between 0x43 and 0x54 (Shops). Both rooms call the same generator with the same guard flag (`$22e6&0x08`). Whichever room is visited first will generate the codes; the other room will do nothing. The same six registers (`$236d`–`$2377`) are used by both rooms.
- The terminal B-trigger occupies two adjacent tile zones (`[2b,1d]` and `[2b,1e]`) pointing at the same script — a common SoE pattern for wide interactive zones.
- Code entry dialog presents three separate menus of three choices (1/2/3) for each digit. Player answers are stored temporarily in `$2839`/`$283b`/`$283d` before comparison with the stored codes.
- When the boy enters the **secret door code** correctly, a projector/camera animation plays but the door does **not** open — only the knock B-trigger (`[1f,15:23,16]`) creates the hole and sets `$22f9&0x02`. The secret code triggers the projector then presumably sets `$22f9&0x04` to allow the slide-down.
- Positions `$24ff`–`$2505` are saved when the dog enters the alarm room and are restored by `0x9b8189` on return — this allows both boy and dog to snap back to their pre-alarm positions after the alarm segment ends.
- FAN_BOT kill flags (`$22f8&0x20`, `$22f8&0x80`) are persistent (SRAM); once killed, the FAN_BOTs never respawn.
