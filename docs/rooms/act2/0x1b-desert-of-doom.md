---
room: 0x1b
name: Antiqua – Desert of Doom
act: act2
data: 0xa68000
---

# 0x1b — Antiqua – Desert of Doom

| Field | Value |
|-------|-------|
| Room ID | 0x1b |
| Full Name | Antiqua – Desert of Doom |
| Act | 2 (Antiqua) |
| Data block | 0xa68000 |
| Step-on table | 0xa6800f (19 entries, 0x72 bytes) |
| B-triggers | none |

## Overview

The Desert of Doom is an infinite-scrolling torus map connecting Nobilia (north, room 0x0a) and Crustacia (south, room 0x4f). The room simulates a continuous desert by teleporting the player two screens in the opposite direction whenever they walk off any edge, and tracking position with two SRAM counters:

- **`$22fc`** (Desert Wrap Y, 0–17=0x11): tracks north–south position. Incremented when the player walks off the **top** (north wrap edge, y≈0x22–0x23) and teleported back south. Decremented when the player walks off the **bottom** (south wrap edge, y≈0x68–0x69) and teleported back north. When decremented below 0 (from $22fc=0), exits to 0x4f (East of Crustacia). When incremented to or above 17, the counter clamps and no teleport occurs — the player is at the maximum-north position.
- **`$22fd`** (Desert Wrap X, 0–7): tracks east–west position. Decremented on east-edge wrap, incremented on west-edge wrap; both clamp within 0–7.

The Sting Man NPC offers a one-time shuttle service for 1× Amulet of Annihilation (or 3× if the potty-mouth curse `$22e9&0x20` is active). Two oases heal the party to full HP every time they are visited. A sandstorm zone near the center of the desert deals periodic damage and can knock the player far off course.

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$22d9` | write | \|=0x40 | First Sting Man meeting shown — prevents re-introduction dialog on future contacts |
| `$22e8` | R/W | &0x08 | Tornado/dust devil: first full-heal of boy has occurred; gate prevents repeat healing |
| `$22e9` | read | &0x20 | Potty-mouth curse flag — shuttle costs 3× Amulet of Annihilation instead of 1× |
| `$22eb` | read | &0x08 | Debug flag — if set, desert wrap counters are shown as HUD text |
| `$22f3` | write | \|=0x08 | Set on north tile exit to 0x0a — tells Nobilia Market the player arrived from the desert north end |
| `$22f3` | R/W | &0x10 | Shuttle accepted (payment made); set by Sting Man payment dialog; read by shuttle step-on to trigger ride animation; cleared on ride completion |
| `$22fc` | R/W | 0–17 | Desert Wrap Y counter — see Overview |
| `$22fd` | R/W | 0–7 | Desert Wrap X counter — see Overview |
| `$2517` | R/W | −=1 or −=3 | Amulet of Annihilation inventory consumed on shuttle; 1× normally, 3× if potty-mouth cursed |
| `$2527` | write | =0x63 | Rice count — refilled to 99 by oasis and tornado |
| `$2529` | write | =0x63 | Spice count — refilled to 99 by oasis and tornado |

## Enter Script Summary

*(Enter script entry address precedes line 23158 of script_all; only subroutine bodies are captured.)*

On room entry the script sets up the torus-desert environment. Based on subroutine bodies visible in the dump:

- Checks `$22fc` to determine the player's vertical position in the desert and spawns Sting Man at the matching shuttle location (north end if $22fc is near 0, south end if near 17).
- Calls "Desert of Doom part [2]" (`0x96e3fe`) after every wrap to refresh Sting Man's position and state.
- The subroutine at `0x96e2f3` loads Sting Man as NPC `0064` at tile position `[51,9f]` (south spawn) and stores the entity in `$2849`. The subroutine at `0x96e30f` destroys `$2849` when needed.
- Primary Sting Man entity is stored in `$2847`; all shuttle step-ons and exit scripts reference `$2847`.

## Step-on Scripts (19 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [22,10:28,15] | `0x9782d6` | **Sandstorm damage zone** — persistent damage loop; deals 5 HP per tick every ~3 ticks to any character standing in the zone; three progressive dizzy messages to boy at >33/66/99 cumulative HP lost; at >120 cumulative damage (boy as controlled char): disables control, teleports boy to [0,0], shows "Hey! Where am I?"; uses `$2834&0x10` as re-entry lock |
| [23,22:38,23] | `0x96e366` | **NS north-edge wrap** (tile band 1 of 4) — `$22fc` +=1; if <17: teleport +2 screens south; if ==17: teleport +2 screens south; if >17: clamp to 17, no teleport |
| [38,22:4f,23] | `0x96e366` | NS north-edge wrap (tile band 2 of 4) |
| [4f,22:66,23] | `0x96e366` | NS north-edge wrap (tile band 3 of 4) |
| [66,22:6b,23] | `0x96e366` | NS north-edge wrap (tile band 4 of 4) |
| [3d,1a:42,20] | `0x96ed74` | **Sting Man shuttle (north end)** — if `$2834&0x08`=0 and `$2847` exists: trigger Sting Man dialog (`0x96e163`); if `$22f3&0x10` (paid): animate south→north shuttle ride, sets `$2834|=0x08` after ride (permanent, prevents repeat) |
| [3d,46:42,4c] | `0x96ec38` | **Sting Man shuttle (south end)** — same logic as north-end shuttle but animates north→south; uses same dialog subroutine `0x96e163` |
| [3e,46:44,48] | `0x96eebe` | **Oasis (south)** — heal boy and dog to full HP (0x3E7 each); top up Rice and Spice to 99 (0x63); fades music out during heal, fades back in on exit |
| [40,4f:49,56] | `0x96eebe` | **Oasis (north)** — identical to south oasis |
| [43,6b:70,6c] | `0x96e0a7` | **EXIT south** → 0x4f East of Crustacia at [0x138, 0x008]; destroys `$2847` before map change |
| [1e,6b:43,6c] | `0x96e0a7` | **EXIT south** (secondary tile band) → same as above |
| [22,3e:23,6b] | `0x96e342` | **EW left-edge wrap** — `$22fd` −=1; if <0: clamp to 7; teleport player +2 screens east |
| [22,1c:23,3e] | `0x96e342` | EW left-edge wrap (secondary band) |
| [6b,40:6c,6b] | `0x96e31e` | **EW right-edge wrap** — `$22fd` +=1; if >7: clamp to 0; teleport player −2 screens west |
| [6b,1b:6c,40] | `0x96e31e` | EW right-edge wrap (secondary band) |
| [23,68:49,69] | `0x96e3b4` | **NS south-edge wrap** — `$22fc` −=1; if <0 (was 0): set to 0, despawn Sting Man, EXIT to 0x4f; else teleport −2 screens north |
| [49,68:6b,69] | `0x96e3b4` | NS south-edge wrap (secondary band) |
| [3b,0c:3c,10] | `0x96e0bf` | **EXIT north** → 0x0a Nobilia Market at [0x028, 0x258]; sets `$22f3|=0x08` (coming from north); destroys `$2847` |
| [2c,18:2d,19] | `0x97823b` | **Tornado / dust devil** — tops up Rice and Spice to 99 if either is below 99; heals boy only on first encounter (`$22e8|=0x08` gate); runs brief animation teleporting boy to [0,0] and back; sets `$2834|=0x01` on completion |

## Exits

| Tiles | Destination | Coordinates | Condition |
|-------|-------------|-------------|-----------|
| [43,6b:70,6c] / [1e,6b:43,6c] | 0x4f — East of Crustacia | [0x138, 0x008] | step-on |
| [23,68:49,69] / [49,68:6b,69] | 0x4f — East of Crustacia | (via wrap; triggers when `$22fc` decrements below 0) | step-on (wrap) |
| [3b,0c:3c,10] | 0x0a — Nobilia Market | [0x028, 0x258] | step-on |

## B-Triggers

None.

## NPCs

| Entity var | NPC | Description |
|-----------|-----|-------------|
| `$2847` | Sting Man (primary) | Shuttle service NPC. Spawns at north shuttle zone (~[0x3f,0x1b]) or south shuttle zone (~[0x3f,0x47]) depending on $22fc. Offers transport for 1× Amulet of Annihilation; 3× if potty-mouth cursed (`$22e9&0x20`). One-time service: after first completed ride `$2834&0x08` is set permanently, disabling further shuttle dialogs. If dog is the controlled character, Sting Man calls the dog by a random name (Sparky, Spartacus, Spot, or Rex). |
| `$2849` | Sting Man (secondary spawn) | Secondary entity handle used when Sting Man is spawned at the alternate shuttle end. Subroutine `0x96e2f3` loads him at position `[51,9f]` and stores in `$2849`; subroutine `0x96e30f` destroys him. |

## Notes

- **North exit is NOT via the wrap counter**: Reaching $22fc=17 (max north) only clamps the counter and stops teleporting — it does not exit to Nobilia. The actual Nobilia exit is tile [3b,0c:3c,10], a specific step-on near the top-left area of the desert.
- **South exit via wrap**: Reaching $22fc=0 and then walking off the south edge triggers `$22fc` to underflow to 0xFF (signed: −1 < 0), which is detected as below zero, triggering exit to 0x4f.
- **`$2834` WRAM bits** (not persisted to SRAM): 0x01=oasis/event complete lock; 0x04=shuttle animation in motion; 0x08=shuttle has been used (set permanently after first ride); 0x10=sandstorm step-on active (re-entry lock). The oasis sets 0x01 at entry but does not gate on it — the oasis heals every visit.
- **Potty-mouth curse** (`$22e9&0x20`): This flag is set elsewhere in the game (likely via Crustacia NPC dialog). When active, Sting Man shows a unique "Hey! Potty mouth…" message and demands 3 Amulets instead of 1.
- **Rice/Spice refill sources**: Both oases and the tornado refill these to 99. The oasis heals both boy and dog every time. The tornado heals boy only, and only on first visit. The tornado also tops up Rice and Spice regardless of visit count.
- **`$22f3&0x08`** set by this room is read by 0x0a (Nobilia Market) to determine which side of the market to place the player's entry point.
- **Debug mode** (`$22eb&0x08`): When enabled, all wrap scripts display the current $22fc and $22fd values as HUD overlay text.
