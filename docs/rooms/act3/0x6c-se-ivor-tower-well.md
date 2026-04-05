# 0x6c — SE of Ivor Tower (Well)

**Act:** 3 — Gothica  
**Script address:** `0x9fff97`  
**Music:** `MUSIC.ACT3` (0x60) — Gothica outdoor  
**Dog sprite:** Poodle (0x08)

## Overview

Small outdoor room at the southeast edge of Ivor Tower, centered on the well that connects the Oglin Cave (0x4b) below to the surface. This is the Act 2 → Act 3 transition room where the dog emerges from the well as a Poodle. On first entry after clearing the well, the Crustacia intro cutscene fires (Oglin cave aftermath). The Well Guy (VILLAGER_3_1) explains the local geography and offers a save point.

The well B-trigger is a crank mechanism: pressing B at the well rotates the crank, lowering the bucket. After 24 presses with the bucket state active, an OGLIN surfaces from the well in a scripted animation.

## Connections

| Direction | Tile range | Destination | Notes |
|-----------|-----------|-------------|-------|
| West | `[06,17:08,1c]` | MAP 0x76 — South of Ivor Tower (Gate) | outdoor→outdoor |

## Enter Script

1. If `$22eb&0x20` (in-animation flag): clear flag, skip teleport
2. Else: teleport both to `[1d,1f]`, fade-out
3. Play `MUSIC.ACT3` (0x60) if no music pending
4. Write dog = Poodle (`$2443 = 0x08`)
5. If `$22ee&0x01` (entry from professor's lab): teleport boy to `[37,27]` face west, clear flag
6. If `$22ed&0x08` (Crustacia intro pending): run well intro cutscene (see Cutscene section), then clear `$22ed&0x08`
7. Else: load VILLAGER_3_1 (0x48) at `[24,37]` with talk script `0x1ad0` ("Ivor Tower Well Guy"), fade in

## Step-On Scripts

| Tile | Destination | Notes |
|------|------------|-------|
| `[06,17:08,1c]` | MAP 0x76 @ `[0x0338 \| 0x0388]` | West exit |

## B-Trigger Scripts

| Tile | Condition | Effect |
|------|-----------|--------|
| `[16,25:18,26]` | Controlled char = boy only | Well crank mechanism (see below) |

### Well Crank Mechanic

- Each B press: play SFX 0x6c, increment `$2469` by 1, toggle OBJ 0 state (bucket up/down visual)
- At `$2469 == 24`:
  - If `$22e0&0x01` (bucket was lowered): reset `$2469 = 0x0001`, hide OBJs 0/1/2, skip to end
  - Else: set `$22e0|=0x01`; disable dog (`be`); load OBJ 3 (cover); load OGLIN (0x6e, NPC `0x00dc>>1`) at `[1b,39]` into `$2841`; run bucket-rise animation (`$2839 = dog`); OGLIN walks east off-screen

## Well Intro Cutscene (`$22ed&0x08`)

Long cutscene triggered on first surface entry (flag set by 0x4b — Oglin Cave):

1. Fade to black; load VILLAGER_3_1 (0x48) into `$2837` at `[24,32]`
2. Bucket-descend animation (boy riding bucket down): `$2839 = boy`, SFX 0x5a, scroll boy from above
3. Well Guy dialog: "Why, you're just south of Ivor Tower, the queen's new castle!"
4. Bucket-ascend animation (dog riding bucket up): `$2839 = dog`, sprite transform to Poodle, SFX 0x5a
5. Well Guy says "You're a poodle!" / "And a fine poodle he is, too."
6. Write save spot `$2449 = 0x000c`; run actual save dialog (`0x4e`)
7. Restore player control

## NPCs

| ID | Enum | Name | Tile | Talk script | Condition |
|----|------|------|------|-------------|-----------|
| 0x48 | `VILLAGER_3_1` | Ivor Tower Well Guy | `[24,37]` | `0x1ad0` | Always (normal enter) |
| 0x48 | `VILLAGER_3_1` | Ivor Tower Well Guy | `[24,32]` | `0x1ad0` | Crustacia intro cutscene only |
| 0x6e | `OGLIN` | Well Oglin | `[1b,39]` | — | B-trigger crank (24 presses) |

## OBJ Map

| OBJ | Purpose |
|-----|---------|
| 0 | Well bucket (toggles up/down) |
| 1 | Bucket/rope visual A |
| 2 | Bucket/rope visual B |
| 3 | Well cover (OBJ state 1 = open) |
| 5 | Well visual (extra) |

## Memory Access

| Address | Bit | Type | Name | Notes |
|---------|-----|------|------|-------|
| `$22ed` | `0x08` | 📖 | Crustacia intro pending | Set by 0x4b; cleared here after cutscene |
| `$22e0` | `0x01` | 📖 | Well bucket lowered | Set on 24th crank press |
| `$22ee` | `0x01` | ⚙️ | Entry from professor's lab | Cleared on use; repositions boy |
| `$22eb` | `0x20` | ⚙️ | In-animation (transient) | Standard room-entry re-use guard |
| `$2443` | word | 🐶 | Dog sprite (`= 0x08` Poodle) | Set on every enter |
| `$2449` | word | ⚙️ | Save spot ID (`= 0x000c`) | Set during Well cutscene |
| `$2469` | word | ⚙️ | Well crank press counter | Transient; resets to 0 |
| `$2841` | ptr | ⚙️ | OGLIN entity pointer | Set during B-trigger animation |
| `$2837` | ptr | ⚙️ | Well Guy entity pointer | Set during cutscene |

## Drop Table

_No drop table configured for this room._

## Notes

- `MUSIC.ACT3` (0x60) plays here — same as the general Gothica outdoor theme
- `$22ee&0x01` is also used in rooms 0x6c, 0x7d (`$234b==5`): it positions the player at specific coords for a "back from professor's lab" re-entry
- The dog transformation from earlier form to Poodle (0x08) is locked in by `$2443` on every entry to this room
