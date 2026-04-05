# 0x42 — Omnitopia: Reactor Room

| Key | Value |
|-----|-------|
| ROM | `0x9ffeef` |
| Data | `0xa9f1d1` |
| Enter script | `0x9bba21` |
| Step-ons | 28 entries @ `0xa9f1e0` (len=0x00a8) |
| B-triggers | 2 entries @ `0xa9f28a` (len=0x000c) |
| Music | 0x1c (reactor ambience) |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | not written (enemies always active) |

---

## Overview

The Reactor Room is the power core of Omnitopia's facility. Its defining mechanic is a reactor toggle switch: when the reactor is OFF (`!$22e6&0x04`), a grid of damage zones is active across the reactor floor, blocking safe traversal. Flipping the switch (`$22e6|=0x04`) deactivates those zones and changes the room's visual state. A boy-only chest contains the Old Reliable armor. The room connects back to the Metroplex Tunnels (0x48) via three hatch exits. There are no `$23bf = 0x0001` PACIFIED writes — enemies are permanently active.

---

## Enter Logic

```
0x9bba21:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE [$0ea2+8] = 0x17a9          // unknown engine hook
  WRITE [$0eac+8] = 0x17a9

  if $22e6&0x04:
    CALL 0x9bbad6                   // reactor-ON state (safe floor, lit visuals)
  else:
    CALL 0x9bbb53                   // reactor-OFF state (dangerous floor, dim visuals)

  if $22e9&0x02:
    UNLOAD OBJ 31                   // chest already opened

  PLAY MUSIC 0x1c

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

### Exit Hatches (3)

| Zone (tile) | `$24fd` | Destination |
|-------------|---------|-------------|
| `[1a,09:1c,0a]` | 9 | 0x48 @ [0x0078, 0x0088] |
| `[2d,09:2f,0a]` | 10 | 0x48 @ [0x0078, 0x0088] |
| `[23,20:25,21]` | 16 | 0x48 @ [0x0078, 0x0088] |

### Damage Zones (25)

All damage zones deal **0x32 damage** with an animation effect.

**Conditional (only active when reactor is OFF, `!$22e6&0x04`):**

These are the central reactor core corridor tiles. When `$22e6&0x04` is set (reactor ON), these zones do nothing.

| Zone (tile) | Group |
|-------------|-------|
| `[07,14:0a,16]` | Core A |
| `[09,13:0a,14]` | Core A |
| `[0b,14:0f,16]` | Core B |
| `[0b,13:0f,14]` | Core B |
| `[10,13:11,14]` | Core C |
| `[17,13:18,14]` | Core C |
| `[17,14:18,16]` | Core C |
| `[10,14:11,16]` | Core C |

**Unconditional (always active):**

Remaining damage zones in the lower section of the room — approximately 17 zones covering the lower reactor floor (`[0e,13:17,16]` range and floor drain tiles below hatch level).

---

## B-Trigger Zones

| Zone (tile) | Condition | Action |
|-------------|-----------|--------|
| `[28,10:29,11]` | — | Reactor toggle: if `!$22e6&0x04` → `$22e6\|=0x04`, SFX 0x44, CALL `0x9bbad6` (ON). Else → `$22e6&=0xfb`, SFX 0x44, CALL `0x9bbb53` (OFF). |
| `[26,1f:28,21]` | Boy-controlled; `!$22e9&0x02` | Chest → Old Reliable (armor), loot music, `$22e9\|=0x02`, UNLOAD OBJ 31 |

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x48 Metroplex Tunnels | `$24fd` = 9, 10, or 16 (set by 0x48 step-ons/triggers) |
| Out (×3) | 0x48 Metroplex Tunnels | Step-ons at row 09 (×2) and row 20 |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22e6` | `0x04` | 📖 | Reactor switched ON — disables core damage zones; persists across visits |
| `$22e9` | `0x02` | 💎 | Old Reliable chest looted — OBJ 31 unloaded on enter |
| `$22f8` | `0x04` | ⚙️ | Hatch-entry flag; cleared on enter after fade-in |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0–30 | Reactor room visual tiles (state changes driven by `0x9bbad6`/`0x9bbb53` — not individually documented here) |
| 31 | Chest (Old Reliable armor) — unloaded if `$22e9&0x02` |

---

## Notes

- `$23bf` is **not written** in this room's enter script — this is unusual compared to other act4 rooms. Enemies remain active on every entry.
- The engine hook writes (`[$0ea2+8]` and `[$0eac+8] = 0x17a9`) are seen in a few other rooms; their purpose is unclear but may relate to collision or enemy behavior.
- `0x9bbad6` (reactor ON) and `0x9bbb53` (reactor OFF) likely swap OBJ states, tile animations, and lighting to reflect the reactor's power state.
- The three hatch exits all map to 0x48 with `$24fd` values 9, 10, and 16 — matching the Metroplex Tunnels' spawn routing table for the three reactor-side hatches.
- The damage value 0x32 (50 decimal) is consistent with hazard zones found elsewhere in Omnitopia.
