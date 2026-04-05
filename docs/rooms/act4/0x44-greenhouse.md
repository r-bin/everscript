# 0x44 — Omnitopia: Greenhouse

| Key | Value |
|-----|-------|
| ROM | `0x9ffef7` |
| Data | `0xaaf592` |
| Enter script | `0x9b85c1` |
| Step-ons | 2 entries @ `0xaaf5a1` |
| B-triggers | 1 entry @ `0xaaf5af` |
| Music | 0x0a (lights on) / 0x7c (dark) |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (enemies active) |

---

## Overview

The Greenhouse is an Omnitopia side room accessible via dog duct from the Control Room (0x43). In its default dark state (`!$22e6&0x40`), four CIVILIAN NPCs wander amid a dim palette effect and barriers block off the back. When the lights are activated (`$22e6&0x40`), the room transitions to a lit variant: barriers are removed and four FLOWER_BLACK enemies ("Flowering Death", #107) spawn. One of the three non-designated flowers is randomly chosen as "deadly" (`$2835 = 1–3`) and becomes script-controlled, making it more dangerous than the AI-controlled ones. A Cryo-Blast crate (B-trigger) sits in the back section. Two hatch exits return to the Metroplex Tunnels (0x48).

---

## Enter Logic

```
0x9b85c1:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE $2348 = 0x0009
  WRITE $23bf = 0x0000

  if $2284&0x02: UNLOAD OBJ 5       // Cryo-Blast crate already opened

  if !$22e6&0x40:                    // dark state
    WRITE $2437 = 0x0006
    // (barrier OBJs 1–4 remain visible)
  
  if $22f8&0x08:
    CALL 0x9b871e                    // first-visit enemy initialization

  if $22e6&0x40:                     // LIGHT STATE — flowers active
    UNLOAD OBJ 1; UNLOAD OBJ 2; UNLOAD OBJ 3; UNLOAD OBJ 4   // barriers gone
    LOAD FLOWER_BLACK (0x6a) at (0x1b, 0x36) → $2837, kill script 0x1b0f
    LOAD FLOWER_BLACK (0x6a) at (0x42, 0x53) → $2839, kill script 0x1b12
    LOAD FLOWER_BLACK (0x6a) at (0x30, 0x31) → $283b, kill script 0x1b15
    LOAD FLOWER_BLACK (0x6a) at (0x43, 0x27) → $283d, kill script 0x1b18
    // $283d entity is ALWAYS script-controlled
    $2835 = RANDRANGE(1, 3)          // session-only: pick second deadly flower
      == 1: $2839 + $283b become script-controlled
      == 2: $2837 + $283b become script-controlled
      == 3: $2837 + $2839 become script-controlled
    CALL 0x9b87dc                    // activate enemies
  else:                              // DARK STATE
    CALL palette script 0x92d8e9 WITH 0x60
    CALL palette script 0x92d8ff WITH 0x80

  // Civilian NPCs (always loaded)
  WRITE $23c1 = 0x0001
  WRITE $2433 = 0x000a
  LOAD NPC (type 0x7a) at (0x59, 0x3d) flags 0x8400
  LOAD NPC (type 0x7a) at (0x59, 0x5d) flags 0x8400
  LOAD NPC (type 0x7a) at (0x07, 0x3b) flags 0x8400
  LOAD NPC (type 0x7a) at (0x0f, 0x1f) flags 0x8400

  PLAY MUSIC 0x0a if $22e6&0x40 else 0x7c

  if $22f8&0x04:
    CALL "Omnitopia hatch fade-in"
    $22f8 &= 0xfb
    END
  else:
    CALL "Some cinematic script"
    END

  // Debug output:
  SHOW "DB: Deadly flower is [$2835]."
```

---

## Step-On Zones

| Zone (tile) | `$24fd` | Action |
|-------------|---------|--------|
| `[2a,10:2c,11]` | 3 | `$2834\|=0x01`, walk to hatch, fade-out → **CHANGE MAP 0x48** @ [0x0078, 0x0088] |
| `[0b,3a:0d,3b]` | 6 | Walk to hatch, fade-out → **CHANGE MAP 0x48** @ [0x0078, 0x0088] |

---

## B-Trigger Zones

| Zone (tile) | Condition | Item | Action |
|-------------|-----------|------|--------|
| `[24,0f:26,11]` | `!$2284&0x02` | 30 Cryo-Blast Projectiles | Play loot fanfare, give ammo, `$2284\|=0x02`, UNLOAD OBJ 5 |

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x43 Control Room | Dog duct from 0x43 B-trigger → CHANGE MAP 0x44 |
| In | 0x48 Metroplex Tunnels | `$24fd = 3` or `$24fd = 6` (set by 0x48) |
| Out (×2) | 0x48 Metroplex Tunnels | Step-ons `[2a,10]` (`$24fd=3`) and `[0b,3a]` (`$24fd=6`) |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22e6` | `0x40` | 📖 | Greenhouse lights on / cleared — loads flowers, removes barriers, changes music |
| `$22f8` | `0x04` | ⚙️ | Hatch-entry flag; cleared after fade-in |
| `$22f8` | `0x08` | ⚙️ | First-visit init flag (calls `0x9b871e`) |
| `$2284` | `0x02` | ⚔️ | Cryo-Blast crate looted — OBJ 5 unloaded on enter |
| `$2835` | — | ⚙️ | Session-only: random deadly flower index (1–3); shown in debug text |
| `$2837` | — | ⚙️ | FLOWER_BLACK entity handle (position 0x1b,0x36) |
| `$2839` | — | ⚙️ | FLOWER_BLACK entity handle (position 0x42,0x53) |
| `$283b` | — | ⚙️ | FLOWER_BLACK entity handle (position 0x30,0x31) |
| `$283d` | — | ⚙️ | FLOWER_BLACK entity handle (always script-controlled; position 0x43,0x27) |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0 | Unknown (not referenced in enter script) |
| 1 | Barrier / wall segment (light state: UNLOADED) |
| 2 | Barrier / wall segment (light state: UNLOADED) |
| 3 | Barrier / wall segment (light state: UNLOADED) |
| 4 | Barrier / wall segment (light state: UNLOADED) |
| 5 | Crate — Cryo-Blast Projectiles (unloaded if `$2284&0x02`) |

---

## Notes

- The FLOWER_BLACK ("Flowering Death", NPC 0x6a, enemy #107) behavior: in the dark state these enemies are absent. In the light state (`$22e6&0x40`), `$283d` is always script-controlled (the "queen" flower), and a random pair of the remaining three is also script-controlled. The third flower uses AI mode. `$2835` (session variable, not saved to SRAM) holds the random index 1–3 identifying which of the first three flowers is the "safe" AI one.
- The debug line `"DB: Deadly flower is [$2835]."` appears unconditionally after the enter script — it is a developer remnant showing the random flower designation.
- `$2834&0x01` is set on the north step-on exit (`$24fd=3`); this likely marks "entered from Greenhouse side" for the 0x48 routing logic.
- The four civilian NPCs (type 0x7a) are loaded in both dark and light states. They carry `flags 0x8400` which may give them their wandering behaviour pattern.
- `$2437 = 0x0006` is written in the dark state (compare `0x0007` in 0x47) — the slight difference may reflect a different layer depth for the palette blend.
