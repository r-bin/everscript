# 0x00 — Omnitopia: Alarm Room

| Key | Value |
|-----|-------|
| ROM | `0x9ffde7` |
| Data | `0xabf4f1` |
| Enter script | `0x9b8fb5` |
| Step-ons | 8 entries @ `0xabf500` (len=0x0030) |
| B-triggers | 1 entry @ `0xabf532` (len=0x0006) |
| Music | 0x5c (alarm ambience) / 0x8c (alarm triggered) |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (enemies active) |

---

## Overview

The Alarm Room is Omnitopia's security corridor, entered when the dog crawls through the Control Room (0x43) ventilation duct and activates the alarm response. Four patrol zones tile the corridor; as the dog advances through each row, two additional GUARD_BOTs ("Guardbot", #69) spawn. The alarm can only be disabled by entering the correct 3-digit code at the Control Room terminal — doing so sets `$22e6&0x10` and suppresses further guard spawning. The room contains one boy-only chest (Titanium Vest) and two hatch exits back to the Metroplex Tunnels (0x48).

---

## Enter Logic

```
0x9b8fb5:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE $2348 = 0x0009
  WRITE $23bf = 0x0000

  if $22f8&0x08:
    CALL 0x9b9005                   // first-visit initialization

  if CHANGE MUSIC ($238d) != 0x00:
    PLAY MUSIC 0x5c
    CALL "Fade-in / start music"

  SET OBJ 0 STATE = 0x7e            // load ceiling alarm #1
  SET OBJ 1 STATE = 0x7e            // load ceiling alarm #2

  if $22f8&0x04:
    CALL "Omnitopia hatch fade-in"
    $22f8 &= 0xfb
    END
  else:
    CALL "Some cinematic script"
    END
```

---

## Step-On Zones

### Exit Hatches (2)

| Zone (tile) | `$24fd` | Destination |
|-------------|---------|-------------|
| `[1b,1a:1d,1b]` | 5 | 0x48 @ [0x0078, 0x0088] |
| `[06,4f:08,50]` | 12 | 0x48 @ [0x0078, 0x0088] |

### Alarm Activation Zones (2)

Triggered when the dog steps into a zone that connects to an alarm node. Only fires if `!$22e6&0x10` (alarm not yet disabled via code entry).

| Zone (tile) | Walk destination | Action |
|-------------|-----------------|--------|
| `[15,48:19,49]` | (0x2e, 0x67) | PLAY MUSIC 0x8c (alarm SFX), SET OBJ 0=0 / OBJ 1=0 (alarms active), SFX 0xaa, YIELD, `$2834\|=0x01` |
| `[15,2d:19,2e]` | (0x2e, 0x39) | Same as above |

### Patrol Spawn Zones (4)

GUARD_BOTs ("Guardbot", NPC 0x4e) spawn in pairs as the dog advances through the alarm corridor rows. Each zone fires once per session and requires the prior row's guards to have been acknowledged (via `$2834` bits).

| Zone (tile) | Prerequisite | Guard spawn positions | Session flag set |
|-------------|--------------|----------------------|-----------------|
| `[0b,3c:23,3e]` | `!$2835&0x02` (first time) | GUARD_BOT at (0x22,0x54)→`$2836`; (0x3a,0x54)→`$2838` | `$2835\|=0x02`, SET OBJ 5=0x7e |
| `[0b,38:23,3a]` | `$2834&0x02 && $2834&0x04` | GUARD_BOT at (0x22,0x4c)→`$283a`; (0x3a,0x4c)→`$283c` | `$2835\|=0x04`, SET OBJ 4=0x7e |
| `[0b,34:23,36]` | `$2834&0x08 && $2834&0x10` | GUARD_BOT at (0x22,0x44)→`$283e`; (0x3a,0x44)→`$2840` | `$2835\|=0x08`, SET OBJ 3=0x7e |
| `[0b,30:23,32]` | `$2834&0x20 && $2834&0x40` | GUARD_BOT at (0x22,0x3c)→`$2842`; (0x3a,0x3c)→`$2844` | `$2835\|=0x10`, SET OBJ 2=0x7e |

---

## B-Trigger Zones

| Zone (tile) | Condition | Item | Action |
|-------------|-----------|------|--------|
| `[16,19:18,1b]` | Boy-controlled; `!$22e9&0x01` | Titanium Vest (armor) | Loot routine, play fanfare, `$22e9\|=0x01`, UNLOAD OBJ 10 |

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x43 Control Room | Dog enters alarm duct (dog-B-trigger in 0x43) or correct code entry in 0x43 |
| Out (×2) | 0x48 Metroplex Tunnels | Step-ons at `[1b,1a]` (`$24fd=5`) and `[06,4f]` (`$24fd=12`) |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22e6` | `0x10` | 📖 | Alarm disabled (set by correct code entry in 0x43) — suppresses alarm activation zones |
| `$22e9` | `0x01` | 🛡️ | Titanium Vest looted — OBJ 10 unloaded on enter |
| `$22f8` | `0x04` | ⚙️ | Hatch-entry flag; cleared after fade-in |
| `$22f8` | `0x08` | ⚙️ | First-visit init flag (calls `0x9b9005`) |
| `$2834` | `0x01` | ⚙️ | Alarm triggered (set by alarm activation step-ons) |
| `$2834` | `0x02–0x40` | ⚙️ | Patrol acknowledge bits (set by guard kill scripts or other logic) |
| `$2835` | `0x02` | ⚙️ | Row 1 patrol spawned (session guard) |
| `$2835` | `0x04` | ⚙️ | Row 2 patrol spawned (session guard) |
| `$2835` | `0x08` | ⚙️ | Row 3 patrol spawned (session guard) |
| `$2835` | `0x10` | ⚙️ | Row 4 patrol spawned (session guard) |
| `$2836` | — | ⚙️ | GUARD_BOT handle — row 1 left |
| `$2838` | — | ⚙️ | GUARD_BOT handle — row 1 right |
| `$283a` | — | ⚙️ | GUARD_BOT handle — row 2 left |
| `$283c` | — | ⚙️ | GUARD_BOT handle — row 2 right |
| `$283e` | — | ⚙️ | GUARD_BOT handle — row 3 left |
| `$2840` | — | ⚙️ | GUARD_BOT handle — row 3 right |
| `$2842` | — | ⚙️ | GUARD_BOT handle — row 4 left |
| `$2844` | — | ⚙️ | GUARD_BOT handle — row 4 right |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0 | Ceiling alarm lamp #1 (SET 0x7e on enter) |
| 1 | Ceiling alarm lamp #2 (SET 0x7e on enter) |
| 2 | Row 4 patrol spawn marker (SET 0x7e when row 4 spawns) |
| 3 | Row 3 patrol spawn marker |
| 4 | Row 2 patrol spawn marker |
| 5 | Row 1 patrol spawn marker |
| 10 | Chest — Titanium Vest (unloaded if `$22e9&0x01`) |

---

## Notes

- The Alarm Room has the most complex step-on logic in act 4 after the Metroplex Tunnels: two exits, two alarm trigger zones, and four guard patrol rows.
- The four patrol rows advance north (decreasing Y) through the corridor. The first row spawns unconditionally on first visit; subsequent rows require prior-row `$2834` bits, which are presumably set by the GUARD_BOT kill scripts in 0x43.
- `$2834` bits 0x02/0x04/0x08/0x10/0x20/0x40 are the patrol chaining flags. Since they share the `$2834` register with other rooms' session state (0x43 dog-duct, 0x54 shop doors), they are session-only values — not SRAM-persistent.
- `$2835` bits 0x02–0x10 serve as duplicate session guards so the patrol spawn step-ons do not fire multiple times on a single visit if the player walks back and forth.
- Music 0x8c is the alarm-triggered state; it overrides the base 0x5c when the dog steps into an alarm zone and `$22e6&0x10` is clear.
