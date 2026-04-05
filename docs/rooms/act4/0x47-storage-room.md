# 0x47 — Omnitopia: Storage Room

| Key | Value |
|-----|-------|
| ROM | `0x9fff03` |
| Data | `0xaa8c6d` |
| Enter script | `0x9b8ce6` |
| Step-ons | 1 entry @ `0xaa8c7c` |
| B-triggers | 7 entries @ `0xaa8c84` (len=0x002a) |
| Music | 0x88 (lights on) / 0x7c (dark) |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (enemies active) |

---

## Overview

The Storage Room is accessible via a dog duct from the Control Room (0x43). It holds seven looted crates in a back alcove, all behind the `$22e6&0x20` "lights on" flag. Until the lights are activated, the room is dark (palette effect applied, music 0x7c), and all B-trigger loot interactions are suppressed. Two FAN_BOTs guard the corridor and five DUSTER_BOT spawners patrol the outer ring. Items include consumables, alchemy ingredients, a Protector Ring, and a Meteorite. The only exit is a single hatch back to the Metroplex Tunnels (0x48).

---

## Enter Logic

```
0x9b8ce6:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)

  // Loot state: unload already-opened crate OBJs
  if $2284&0x04: UNLOAD OBJ 0    // Dry Ice
  if $2284&0x08: UNLOAD OBJ 1    // Acorns
  if $2284&0x10: UNLOAD OBJ 2    // Honey gourd
  if $2284&0x20: UNLOAD OBJ 3    // Thunderballs
  if $2284&0x40: UNLOAD OBJ 4    // Protector Ring
  if $2284&0x80: UNLOAD OBJ 5    // Particle Bombs / Nectar gourd
  if $2285&0x01: UNLOAD OBJ 6    // Meteorite

  if !$22e6&0x20:                 // dark state
    WRITE $2437 = 0x0007
    CALL palette script 0x92d8e9 WITH 0x60
    CALL palette script 0x92d8ff WITH 0x80

  if $22f8&0x08:
    CALL 0x9b8d99                 // first-visit initialization

  SET OBJ 7 STATE = 0x7e
  LOAD FAN_BOT (0x69) at (0x30, 0x25) → entity, SET kill script 0x1b24
  SET OBJ 8 STATE = 0x7e
  LOAD FAN_BOT (0x69) at (0x40, 0x25) → entity, SET kill script 0x1b27

  WRITE $2433 = 0x0001
  Add DUSTER_BOT spawner at (0x1b, 0x23)
  Add DUSTER_BOT spawner at (0x31, 0x3d)
  Add DUSTER_BOT spawner at (0x51, 0x45)
  Add DUSTER_BOT spawner at (0x67, 0x3b)
  Add DUSTER_BOT spawner at (0x67, 0x19)

  PLAY MUSIC 0x88 if $22e6&0x20 else 0x7c

  // Note: no $22f8&0x04 hatch check in this room — always standard cinematic
  CALL "Some cinematic script"
  END
```

---

## Step-On Zones

| Zone (tile) | Action |
|-------------|--------|
| `[13,15:15,16]` | Walk both to (0x0078, 0x0088), `$24fd = 13`, fade-out → **CHANGE MAP 0x48** |

---

## B-Trigger Zones

All 7 triggers are gated: if `!$22e6&0x20` (dark), the interaction does nothing.

| Zone (tile) | Item | Qty | Sell Price | Flag | OBJ |
|-------------|------|-----|-----------|------|-----|
| `[26,25:28,27]` | Dry Ice | — | — | `$2284&0x04` | 0 |
| `[2c,25:2e,27]` | Acorns | — | — | `$2284&0x08` | 1 |
| `[32,25:34,27]` | Honey 🫙 | gourd | — | `$2284&0x10` | 2 |
| `[38,25:3a,27]` | Thunderball Ammo | 30 | — | `$2284&0x20` | 3 |
| `[38,1d:3a,1f]` | Protector Ring 💎 | — | — | `$2284&0x40` | 4 |
| `[3c,1d:3e,1f]` | Particle Bomb Ammo (first time: 600cr) + Nectar Gourd 🫙 | 30 | 600cr | `$2284&0x80` / `$22e6&0x80` | 5 |
| `[40,1d:42,1f]` | Meteorite 🌿 | — | — | `$2285&0x01` | 6 |

The Particle Bombs crate (OBJ 5) has two states:
- `!$2284&0x80 && !$22e6&0x80`: first visit → gives 30 Particle Bombs; shows sell-price dialog for 600cr; sets `$22e6|=0x80`
- `$22e6&0x80` (sold once): replaces with Nectar gourd pickup, sets `$2284|=0x80`

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x43 Control Room | Dog enters duct from 0x43 B-trigger → CHANGE MAP 0x47 |
| In | 0x48 Metroplex Tunnels | `$24fd = 13` (set by 0x48) |
| Out | 0x48 Metroplex Tunnels | Step-on `[13,15:15,16]`, `$24fd = 13` |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22e6` | `0x20` | 📖 | Storage room lights on — prerequisite for all B-trigger loot |
| `$22e6` | `0x80` | 📖 | Particle Bombs already sold (first-time 600cr interaction used) |
| `$22f8` | `0x08` | ⚙️ | First-visit initialization flag (calls `0x9b8d99`) |
| `$2284` | `0x04` | 🌿 | Dry Ice looted |
| `$2284` | `0x08` | 🌿 | Acorns looted |
| `$2284` | `0x10` | 🫙 | Honey gourd looted |
| `$2284` | `0x20` | ⚔️ | Thunderball Ammo looted |
| `$2284` | `0x40` | 💎 | Protector Ring looted |
| `$2284` | `0x80` | 🫙 | Particle Bombs / Nectar gourd looted |
| `$2285` | `0x01` | 🌿 | Meteorite looted |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0 | Crate — Dry Ice |
| 1 | Crate — Acorns |
| 2 | Crate — Honey gourd |
| 3 | Crate — Thunderball Ammo |
| 4 | Crate — Protector Ring |
| 5 | Crate — Particle Bombs / Nectar gourd |
| 6 | Crate — Meteorite |
| 7 | FAN_BOT #1 spawn marker |
| 8 | FAN_BOT #2 spawn marker |

---

## Notes

- The "lights off" path (`!$22e6&0x20`) applies the same dark palette effect used in 0x44 (Greenhouse) and 0x45 (Secret Boss Room): `0x92d8e9`/`0x92d8ff` with args 0x60/0x80.
- `$2437 = 0x0007` is written before the palette scripts in the dark state; this may set a layer or blend register for the darkening effect.
- The first-visit subroutine `0x9b8d99` (called when `$22f8&0x08` is set) likely turns the lights on, clears `$22f8&0x08`, and sets `$22e6|=0x20`.
- Kill scripts 0x1b24 and 0x1b27 handle the two FAN_BOT deaths. The FAN_BOTs are always respawned on entry (no kill-state persistence).
- The hatch fade-in branch (`$22f8&0x04`) is **absent** from this enter script — always enters via standard cinematic, even when arriving from 0x43 via duct.
- `$2285` is a separate persistence byte from `$2284`; only bit 0x01 (Meteorite) is used in this room.
