# 0x49 — Omnitopia: Junkyard (Landing Spot)

| Key | Value |
|-----|-------|
| ROM | `0x9fff0b` |
| Data | `0xa4ee2d` |
| Enter script | `0x928188 → 0x9be2a1` |
| Step-ons | 13 entries @ `0xa4ee3c` (len=0x004e) |
| B-triggers | 0 (none) |
| Music | 0x6c |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (enemies active) |

---

## Overview

The Junkyard is the landing zone below the Omnitopia ship crash site. It is the destination of the ship-landing cutscene triggered in the Metroplex Tunnels (0x48) on the very first Omnitopia entry (`$22f8&0x02`). Eleven RAT (NPC 0x42, "Rat") spawner points fill the exterior. Three patrol-spawn step-on groups (each guarded by `$2834` bits 0x01/0x02/0x04) trigger TENTACLE_SPIKE (NPC 0x4a, "Tiny Tentacle", #73) and TENTACLE_WHIP (NPC 0x3f, "Tentacle", #72) swarms as the player explores zones. One GUARD_BOT (NPC 0x4e) with a "Junkyard Robot / Reflect" kill script patrols the north end. An energy core teleporter step-on (requiring `$2264&0x20` or `$22eb&0x08`) allows fast-travel back to the Metroplex Tunnels. A separate step-on leads back up to the Jail (0x7e). There are no B-triggers.

---

## Enter Logic

```
0x9be2a1:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both to (0x3b, 0x43)
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE $2348 = 0x0009
  WRITE $2433 = 0x0001

  // 11 × RAT spawner points
  Add NPC 0x42 (RAT) spawner at (0x33, 0x41)
  Add NPC 0x42 (RAT) spawner at (0x3f, 0x35)
  Add NPC 0x42 (RAT) spawner at (0x5b, 0x43)
  Add NPC 0x42 (RAT) spawner at (0x6f, 0x2b)
  Add NPC 0x42 (RAT) spawner at (0x73, 0x1f)
  Add NPC 0x42 (RAT) spawner at (0x55, 0x1b)
  Add NPC 0x42 (RAT) spawner at (0x2f, 0x1d)
  Add NPC 0x42 (RAT) spawner at (0x1b, 0x3f)
  Add NPC 0x42 (RAT) spawner at (0x05, 0x2b)
  Add NPC 0x42 (RAT) spawner at (0x09, 0x47)
  Add NPC 0x42 (RAT) spawner at (0x19, 0x1b)

  if CHANGE MUSIC ($238d) != 0: PLAY MUSIC 0x6c, fade-in

  LOAD NPC 0x9c>>1 = 0x4e (GUARD_BOT) at (0x6e, 0x18) → $2837
  SET kill script 0x1b75 ("Junkyard Robot / Reflect") for $2837
  CALL palette script 0x92d8e9 WITH 0x60
  CALL palette script 0x92d8ff WITH 0x80

  // Branch: special intro path from Professor's lab
  if $22ee&0x01:
    $22ee &= 0xfe; $238f = 0x000f
    Teleport boy + dog to intro position, face north
    CALL "Some cinematic script"
    END

  // Branch: ship landing cutscene (first Omnitopia entry)
  if $22f8&0x02:
    RCALL 0x9bde41                  // junkyard landing cutscene
    END

  // Branch: arrived from jail hatch (above)
  if $22f9&0x08:
    CALL "Omnitopia hatch fade-in" (0x92de7e)
    END

  // Default
  CALL "Some cinematic script"
  END
```

### Landing Cutscene (`0x9bde41`, triggered by `$22f8&0x02`)

The ship-landing cutscene animates a spacecraft descending from y=0x0000 to y=0x0290, with screen shake on impact. Positions are derived from saved coordinates. Afterward:

1. SET OBJ 4 = 0x7e (ship visible), then 0 (ship gone) after landing.
2. Boy and dog perform arrival choreography, walking forward and turning.
3. Dialog sequence:
   - Boy: *"Yesss! What a ride! Tinker's ship worked great!"*
   - Dog: *"!! What's happened?? You're so metallic! Like Toastzilla in {Attack of the Appliance People}. At least we'll be ready if attacked by Bagel Beasts or Waffle Weasels. <snicker> <snicker>"*
   - Boy: *"Sorry, [dog]. Just kidding! Now we better start looking for Professor Ruffleberg."*
4. Clears `$22f8&0x02`.

---

## Step-On Zones

### Enemy Spawn Groups (3 scripts × multiple zones)

| Script | Zones | Guard flag | Enemies spawned |
|--------|-------|-----------|-----------------|
| `0x9bdf7b` | `[28,2f:2d,30]`, `[1b,31:1c,34]`, `[2d,29:2e,2b]` | `$2834&0x01` | 3×TENTACLE_SPIKE at (3d,47),(35,35),(2d,53) + 2×TENTACLE_WHIP at (2b,43),(45,39) |
| `0x9bdfa2` | `[3f,1d:42,1e]`, `[3e,27:3f,2c]`, `[2e,29:2f,2b]` | `$2834&0x02` | 3×TENTACLE_SPIKE at (5f,53),(61,4b),(67,3b) + 2×TENTACLE_WHIP at (51,47),(6b,33) |
| `0x9bdfc9` | `[39,17:3a,1b]`, `[2a,16:2b,1b]`, `[24,1b:2b,1c]`, `[23,16:24,1c]`, `[0d,1c:0e,1e]` | `$2834&0x04` | 3×TENTACLE_SPIKE at (5f,1d),(3d,28),(1a,18) + 3×TENTACLE_WHIP at (48,1d),(29,15),(15,23) |

Each group fires at most once per session (respective `$2834` bit acts as guard). Enemies are loaded with a short staggered delay (14 ticks each).

### Jail Return Step-On

| Zone (tile) | Action |
|-------------|--------|
| `[26,15:28,16]` | BOY+DOG = STOPPED, walk to (0x01f8, 0x00b0), CALL ABS `0x92ded8`, SLEEP 47, `$22f9\|=0x40`, fade-out → **CHANGE MAP 0x7e** @ [0x0070, 0x00e0] |

### Energy Core Teleporter

| Zone (tile) | Condition | Action |
|-------------|-----------|--------|
| `[0d,32:11,33]` | `$2264&0x20` (Energy Core) OR `$22eb&0x08` | `$22f9\|=0x20`, SET OBJs 0–3=0x7e, SLEEP 119, SAVE (`$2449=0x001b`), clear `$2264&0x20`, walk to (0xa8, 0x270), `$24fd=0x11`, → **CHANGE MAP 0x48** @ [0x03c8, 0x0298] |

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x48 Metroplex Tunnels | Ship-landing cutscene (`$22f8&0x02`), OR first entry via prof lab (`$22ee&0x01`) |
| In | 0x7e Jail | Drop-hatch B-trigger in 0x7e sets `$22f9&0x08` |
| Out | 0x7e Jail | Step-on `[26,15:28,16]`, sets `$22f9&0x40` |
| Out | 0x48 Metroplex Tunnels | Energy Core teleporter step-on, `$24fd=17` |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22e6` | — | — | Not used in this room |
| `$22eb` | `0x08` | ⚙️ | Alternate energy-core unlock (source unknown) |
| `$22ee` | `0x01` | ⚙️ | Intro from Professor's lab — triggers special spawn |
| `$22f8` | `0x02` | 📖 | First Omnitopia entry — ship landing cutscene plays; cleared by cutscene |
| `$22f9` | `0x08` | ⚙️ | Arrived from jail hatch — triggers hatch fade-in |
| `$22f9` | `0x20` | ⚙️ | Energy core teleporter used |
| `$22f9` | `0x40` | ⚙️ | Returned to jail from junkyard (set on `[26,15]` step-on) |
| `$2264` | `0x20` | 💎 | Energy Core collected — enables energy core teleporter; cleared on use |
| `$2834` | `0x01` | ⚙️ | South enemy group spawned (session guard) |
| `$2834` | `0x02` | ⚙️ | East enemy group spawned (session guard) |
| `$2834` | `0x04` | ⚙️ | North enemy group spawned (session guard) |
| `$2837` | — | ⚙️ | GUARD_BOT entity handle (Junkyard Robot) |
| `$2449` | — | ⚙️ | Save spot ID — written `0x001b` at energy core teleporter |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0 | Energy core teleporter visual #1 |
| 1 | Energy core teleporter visual #2 |
| 2 | Energy core teleporter visual #3 |
| 3 | Energy core teleporter visual #4 |
| 4 | Ship crash OBJ (SET 0x7e during landing cutscene; SET 0 after impact) |

---

## Notes

- The Junkyard is the only room in act 4 where `$22f8&0x02` (first Omnitopia entry) is consumed. After the landing cutscene clears this flag, subsequent visits use the standard cinematic.
- The three enemy-spawn step-on groups cover different sectors of the junkyard. Zones from different groups can overlap in tile space — e.g. `[2e,29:2f,2b]` (group 1) and `[2d,29:2e,2b]` (group 2) are adjacent. Each group independently checks its `$2834` guard bit.
- The GUARD_BOT kill script 0x1b75 is labelled "Junkyard Robot / Reflect" in the disassembly — distinct from the prison warden GUARD_BOT in 0x7e (kill script 0x1b42).
- The energy core teleporter (`[0d,32:11,33]`) requires `$2264&0x20` (Energy Core item collected) OR `$22eb&0x08`. This is the only in-room save point in the Junkyard area (`$2449 = 0x001b = 27`).
- `$22f9&0x40` is set when leaving the junkyard back to the jail, and is checked by 0x7e's enter script to call the special re-entry routine `0x9b9692`.
- The landing cutscene dialog contains a rare dog-focused joke: Toaster compares himself to "Toastzilla in {Attack of the Appliance People}" — the `{…}` notation in the dump indicates a VWFS-formatted italic text run.
