# 0x4a — Omnitopia: Final Boss Room (Rimsala)

| Key | Value |
|-----|-------|
| ROM | `0x9fff0f` |
| Data | `0xa3da2c` |
| Enter script | `0x92818d → 0x9bb945` |
| Step-ons | 2 entries @ `0xa3da3b` (len=0x000c) |
| B-triggers | 8 entries @ `0xa3da49` (len=0x0030) |
| Music | 0x24 (boss fight) / 0x3c (outro) |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (normal entry) / `0x0001` (outro) |

---

## Overview

The Final Boss Room is the endgame arena for Omnitopia and the site of the climactic confrontation with Rimsala. The room has two completely distinct modes controlled by `$22f1&0x40` ("Inside outro?"):

- **Normal mode** (`!$22f1&0x40`): Boss music 0x24, enemies active. Eight interactive B-trigger zones represent Rimsala's switch-panels (`$2845`–`$2853`); the player must hit panels in the correct order. Two step-on zones trigger Rimsala's floor-sweeping attacks, tracked in `$2865`.
- **Outro mode** (`$22f1&0x40`): PACIFIED, music 0x3c. OBJs 0–7 loaded, Professor Ruffleberg (NPC 0x57, `0xae>>1`) appears at (0x09, 0x11) for the game's ending cutscene, which ends with CHANGE MAP to 0x36 (Prehistoria — Both Fire Pits), triggering the final credit sequence.

This room is entered from the Metroplex Tunnels (0x48) and has no exits in normal mode — defeating Rimsala presumably sets `$22f1&0x40` and re-enters the room for the outro.

---

## Enter Logic

```
0x9bb945:
  if $22f1&0x40:                    // BRANCH A — OUTRO
    PLAY MUSIC 0x3c, fade-in
    WRITE $23bf = 0x0001            // PACIFIED
    WRITE CHANGE DOGGO = Toaster
    WRITE $238f = 0x0000
    SET OBJ 0–7 STATE = 0x7e       // load all room objects
    WRITE $2857 = last entity
    RCALL 0x9bb4f0                  // ending cutscene
    END

  else:                             // BRANCH B — BOSS FIGHT
    WRITE $23bf = 0x0000
    WRITE CHANGE DOGGO = Toaster
    WRITE $2413 = 0x00a8
    $2262 |= 0x02                   // Jaguar Ring ?
    // 4 × untraced instr (ids 0x00–0x03)
    if $22eb&0x20:
      $22eb &= 0xdf
    else:
      teleport both to (0x14, 0x25)
      CALL "Fade-out / stop music"
    PLAY MUSIC 0x24, fade-in
    WRITE entity hook [$0ea2+0] = 0x40; [$0eac+0] = 0x1b5a  // "Boss rush loot script?"
    Face both NORTH
    Teleport boy to (0x1f, 0x12), dog to (0x1f, 0x16)
    Set boy sprite/animation
    CALL 0x9bb928                   // Rimsala arena setup
    SLEEP 59 ticks
    Boy animation effects
    Screen shake (y = 0x0004), SLEEP 7, stop shake
    BOY = Player controlled
    CALL 0x9baf4b                   // main Rimsala battle loop
    END
```

### Outro Cutscene (`0x9bb4f0`)

1. BOY+DOG = STOPPED; hide status bar layer.
2. Teleport boy to (0x11, 0x12), dog to (0x11, 0x16).
3. LOAD NPC `0xae>>1 = 0x57` (PROFESSOR Ruffleberg) at (0x09, 0x11) → `$2857`.
4. Brightness fade-in loop (0 → 15).
5. Extended cinematic: Professor walks toward characters, multiple dialog exchanges (text strings 0x2307, 0x230a, 0x230d, 0x230d etc.), camera cuts.
6. Fade out brightness, `WINDWALK`, CHANGE MAP = **0x36** (Prehistoria — Both Fire Pits) @ [0x00e8, 0x0148].

---

## Step-On Zones

These represent Rimsala's floor-laser sweep attacks. Both zones cover the same wide row (y=25–29).

| Zone (tile) | Condition | Action |
|-------------|-----------|--------|
| `[33,26:43,28]` | `($2865 & 0xa5) != 0xa5` | `$2835=4`, `$2837=0x5a`, write sweep params, `$243b=0x0028`, SFX 0x8a, CALL `0x9bac5f` (sweep A) |
| `[33,28:43,29]` | `!($2835 > 2)` and `!($2865 & 0x5a) == 0x5a` | `$2835=2`, `$2837=0xf0`, write sweep params, SFX 0xb2, CALL `0x9bac5f` (sweep B) |

`$2865` accumulates the hit-panel bitmask across B-triggers. `0xa5 = 10100101b` (panels 1,3,6,8) and `0x5a = 01011010b` (panels 2,4,5,7) — the two groups of four panels that Rimsala cycles through.

---

## B-Trigger Zones

All 8 triggers invoke the shared subroutine `0x9babe4` with an entity handle and bitmask:

| Zone (tile) | Entity handle | Bitmask | Bit in `$2865` |
|-------------|---------------|---------|----------------|
| `[33,25:35,26]` | `$2845` | 1 | bit 0 |
| `[35,25:37,26]` | `$2847` | 2 | bit 1 |
| `[37,25:39,26]` | `$2849` | 4 | bit 2 |
| `[39,25:3b,26]` | `$284b` | 8 | bit 3 |
| `[3b,25:3d,26]` | `$284d` | 16 | bit 4 |
| `[3d,25:3f,26]` | `$284f` | 32 | bit 5 |
| `[3f,25:41,26]` | `$2851` | 64 | bit 6 |
| `[41,25:43,26]` | `$2853` | 128 | bit 7 |

Each call to `0x9babe4` checks whether the panel entity at the given handle is in the correct state and, if so, sets the corresponding bit in `$2865` (or a related accumulator). All 8 triggers are on a single-tile-wide row at y=25, reading left to right.

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x48 Metroplex Tunnels | `$24fd` set by 0x48 step-on/trigger |
| Out | 0x36 Prehistoria — Both Fire Pits | Outro cutscene (`$22f1&0x40`), via WINDWALK |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22f1` | `0x40` | 📖 | Inside outro — switches room to PACIFIED mode with Professor cutscene |
| `$2262` | `0x02` | ⚙️ | Jaguar Ring flag — written on boss fight entry |
| `$2835` | — | ⚙️ | Rimsala sweep parameter (4 = sweep A; 2 = sweep B) |
| `$2837` | — | ⚙️ | Rimsala sweep speed parameter (0x5a / 0xf0) |
| `$2843` | — | ⚙️ | Sweep damage zone width (`$243b = 0x28`) |
| `$2845` | — | ⚙️ | Rimsala panel #1 entity handle |
| `$2847` | — | ⚙️ | Rimsala panel #2 entity handle |
| `$2849` | — | ⚙️ | Rimsala panel #3 entity handle |
| `$284b` | — | ⚙️ | Rimsala panel #4 entity handle |
| `$284d` | — | ⚙️ | Rimsala panel #5 entity handle |
| `$284f` | — | ⚙️ | Rimsala panel #6 entity handle |
| `$2851` | — | ⚙️ | Rimsala panel #7 entity handle |
| `$2853` | — | ⚙️ | Rimsala panel #8 entity handle |
| `$2857` | — | ⚙️ | Professor Ruffleberg entity handle (outro only) |
| `$2865` | — | ⚙️ | Rimsala hit-panel accumulator (bitmask of struck panels) |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0–7 | Room OBJs (SET 0x7e=load during outro; unknown purpose in normal mode) |

---

## Notes

- The Final Boss Room is the only room in the game with two fully distinct gameplay modes controlled by a single flag (`$22f1&0x40`). Normal mode is a combat arena; outro mode is a pure narrative cutscene.
- The 8 B-trigger panels at y=25 form a single interactive row spanning 10 tiles (x=33 to x=43). Each 2-tile-wide panel corresponds to one Rimsala form/phase. The bitmasks form a standard 8-bit byte.
- `$2865` bitmask values: `0xa5 = 10100101b` (panels 1,3,6,8) and `0x5a = 01011010b` (panels 2,4,5,7) — the step-on attack triggers cycle between two sweep groups. When all panels in group A are hit (bits `0xa5`), sweep A no longer triggers. Group B (`0x5a`) tracks the alternate set.
- The outro CHANGE MAP destination is 0x36 ("Prehistoria — Both Fire Pits") — this is the final credits room, revisiting the earliest area of the game.
- `$2262&0x02` (Jaguar Ring) is set at the start of the boss fight entry. This may enable or modify Rimsala's vulnerability window.
- The entity hook writes (`[$0ea2+0]` and `[$0eac+0]`) with label "Boss rush loot script?" are analogous to the hook writes seen in 0x42 (Reactor Room) at `[$0ea2+8]`. Their function is unconfirmed.
- Professor Ruffleberg uses NPC type 0x57 (`PROFESSOR`, enemy/NPC #41), loaded from `0xae>>1` in the outro branch. He appears at position (0x09, 0x11) and is the only character NPC in act 4.
