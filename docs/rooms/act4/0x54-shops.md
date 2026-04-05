# 0x54 — Omnitopia: Shops

| Key | Value |
|-----|-------|
| ROM | `0x9fff37` |
| Data | `0xaa8000` |
| Enter script | `0x9b9f33` |
| Step-ons | 7 entries @ `0xaa800f` (len=0x002a) |
| B-triggers | 3 entries @ `0xaa803b` (len=0x0012) |
| Music | 0x88 |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0001` (always safe — shops never have active enemies) |

---

## Overview

The Omnitopia Shops are Omnitopia's commercial hub: a tripartite room split between a boy-only shopping zone and a dog-only zone, separated by two OBJ gates (`$2834&0x01`/`$0x02`). The boy can access three shops (weapons/ammo, ingredients, items) and a healing station; the dog is refused service at all three counters. A critical shared mechanic: this room generates the two 3-digit playthrough codes (`$236d`–`$2377`) if `$22e6&0x08` has not yet been set — the same generation that normally happens in the Control Room (0x43). Three DUSTER_BOT-type shopkeeper NPCs (NPC 0x4d) occupy the counters. Two hatch exits return to the Metroplex Tunnels (0x48).

---

## Enter Logic

```
0x9b9f33:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE $2348 = 0x0009
  WRITE $23bf = 0x0001              // PACIFIED — no enemies

  PLAY MUSIC 0x88

  // Code generation (shared with 0x43 — fires only if not yet generated)
  if !$22e6&0x08:
    $236d = RANDRANGE(1, 3)         // access code digit 1
    $236f = RANDRANGE(1, 3)         // access code digit 2
    $2371 = RANDRANGE(1, 3)         // access code digit 3
    $2373 = RANDRANGE(1, 3)         // secret door code digit 1
    $2375 = RANDRANGE(1, 3)         // secret door code digit 2
    $2377 = RANDRANGE(1, 3)         // secret door code digit 3
    $22e6 |= 0x08

  LOAD NPC (0x9a>>1 = 0x4d, DUSTER_BOT) at (0x48, 0x4e) — shopkeeper A
  LOAD NPC (0x9a>>1 = 0x4d, DUSTER_BOT) at (0x12, 0x58) — shopkeeper B
  LOAD NPC (0x9a>>1 = 0x4d, DUSTER_BOT) at (0x25, 0x57) — shopkeeper C

  if $22eb&0x04: CALL showcase mode intro

  if $22f8&0x04:
    CALL "Omnitopia hatch fade-in"
    $22f8 &= 0xfb
    END

  if $22ee&0x01:                    // arrived from Professor's lab intro
    $22ee &= 0xfe
    $238f = 0x000f
    Teleport boy + dog to fixed intro position, face north
    CALL "Some cinematic script"
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
| `[05,2b:07,2c]` | 7 | 0x48 @ [0x0078, 0x0088] |
| `[37,0c:39,0d]` | 2 | 0x48 @ [0x0078, 0x0088] |

### Gate Zones (4)

These step-ons manage the OBJ gates separating the boy and dog sections of the shop.

| Zone (tile) | Action |
|-------------|--------|
| `[29,18:2d,19]` | **Boy gate**: if `!$2834&0x01` → SET OBJ 0=0x7e (open), SFX 0xb0, `$2834\|=0x01` |
| `[29,2b:2d,2c]` | **Dog gate**: if `!$2834&0x02` → SET OBJ 1=0x7e (open), SFX 0xb0, `$2834\|=0x02` |
| `[29,1f:2d,20]` | **Boy→Dog crossing**: if `$2834&0x01` → walk dog to pos, SET OBJ 0=0 (close boy gate), `$2834&=0xfe`; then if `!$2834&0x02` → SET OBJ 1=0x7e, `$2834\|=0x02` |
| `[29,24:2d,25]` | **Dog→Boy crossing**: if `$2834&0x02` → walk boy to pos, SET OBJ 1=0 (close dog gate), `$2834&=0xfd`; then if `!$2834&0x01` → SET OBJ 0=0x7e, `$2834\|=0x01` |

### Healing Station (1)

| Zone (tile) | Controller | Cost | Action |
|-------------|-----------|------|--------|
| `[17,26:1b,28]` | Boy | 100 credits | Full HP restore + clear status effects + save (`$2449 = 0x0016`). If `$240d == 0`, show credit-exchange reminder. |
| `[17,26:1b,28]` | Dog | — | "Canine unit detected. Healing program is unable to engage." |

---

## B-Trigger Zones

All three shop counters refuse service to the dog with: *"Canine unit detected. Sales program is unable to engage."*

| Zone (tile) | Shop | Shopkeeper pos | Inventory |
|-------------|------|---------------|-----------|
| `[13,0a:17,0b]` | **Armament Shop** | NPC 0x20 at (0x28, 0x0e) | 10 Thunderballs (300cr, cap 90); 10 Particle Bombs (600cr, cap 90); 10 Cryo-Blasts (1000cr, cap 90); Buy/Sell general; Money Exchange (if `$240d != 0`) |
| `[1d,0a:21,0b]` | **Ingredient Shop** | NPC 0x20 at (0x3c, 0x0e) | Ingredient shop menu (`$2459 = 0x000f`); sets `$22ee\|=0x02` while open, clears on close |
| `[27,0a:2b,0b]` | **Item Shop** | NPC 0x20 at (0x50, 0x0e) | Item shop menu (`$2457 = 0x000e`); Buy/Sell; Money Exchange (if `$240d != 0`) |

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x48 Metroplex Tunnels | `$24fd = 2` or `$24fd = 7` (set by 0x48) |
| In | 0x46 Professor's Lab | `$22ee&0x01` intro path (special spawn) |
| Out (×2) | 0x48 Metroplex Tunnels | Step-ons `[05,2b]` (`$24fd=7`) and `[37,0c]` (`$24fd=2`) |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22e6` | `0x08` | 📖 | Codes generated — set on first visit to 0x54 **or** 0x43 |
| `$22eb` | `0x04` | ⚙️ | Showcase/attraction mode active |
| `$22ee` | `0x01` | ⚙️ | Intro flag from Professor's lab — triggers special spawn on first entry |
| `$22ee` | `0x02` | ⚙️ | Ingredient shop currently open |
| `$22f8` | `0x04` | ⚙️ | Hatch-entry flag; cleared after fade-in |
| `$2834` | `0x01` | ⚙️ | Boy-side gate open (OBJ 0) — session state |
| `$2834` | `0x02` | ⚙️ | Dog-side gate open (OBJ 1) — session state |
| `$236d` | — | ⚙️ | Access code digit 1 (generated here if `!$22e6&0x08`) |
| `$236f` | — | ⚙️ | Access code digit 2 |
| `$2371` | — | ⚙️ | Access code digit 3 |
| `$2373` | — | ⚙️ | Secret door code digit 1 |
| `$2375` | — | ⚙️ | Secret door code digit 2 |
| `$2377` | — | ⚙️ | Secret door code digit 3 |
| `$240d` | — | ⚙️ | Credit exchange / talons availability flag |
| `$2449` | — | ⚙️ | Save spot ID — written `0x0016` at healing station |
| `$2457` | — | ⚙️ | Item shop index (`0x000e`) |
| `$2459` | — | ⚙️ | Ingredient shop index (`0x000f`) |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0 | Boy-side gate (SET 0x7e = open; SET 0 = closed) |
| 1 | Dog-side gate (SET 0x7e = open; SET 0 = closed) |
| 2 | Armament shop door/counter visual |
| 3 | Ingredient shop door/counter visual |
| 4 | Item shop door/counter visual |
| 5 | Armament shop secondary OBJ |
| 6 | Ingredient shop secondary OBJ |
| 7 | Item shop secondary OBJ |

---

## Notes

- The boy/dog gate mechanic (`$2834&0x01`/`0x02`) is unusual: gates open when the correct character enters their section, and the crossing step-ons enforce that only one side is open at a time — the dog cannot be in the boy zone and vice versa simultaneously.
- The shopkeeper NPCs use sprite type 0x9a>>1 = 0x4d (DUSTER_BOT / "Mechaduster"), giving them the same sprite as the enemies in the tunnels, but with talk scripts.
- Shop counter NPCs are `NPC 0x20` (FRIPPO / palette NPC), loaded dynamically on B-trigger interaction — not present on room entry.
- The code generation in 0x54 is a **separate inline block** (not a CALL to `0x9b814e`) from the one in 0x43, but generates identical values into the same six registers with the same guard flag.
- `$22ee&0x02` is set while the ingredient shop is open and cleared on close — probably to suppress other events or track shop-open state for save-safety.
- The healing station save ID `0x0016 = 22` decimal is an Omnitopia-specific save spot marker.
