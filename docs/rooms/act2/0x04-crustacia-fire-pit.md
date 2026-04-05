---
room: 0x04
name: Antiqua – Crustacia Fire Pit (WindWalker Landing)
act: act2
data: 0xacd00a
---

# 0x04 — Antiqua – Crustacia Fire Pit (WindWalker Landing)

| Field | Value |
|-------|-------|
| Room ID | 0x04 |
| Full Name | Antiqua – Crustacia Fire Pit (WindWalker Landing) |
| Act | 2 (Antiqua) |
| Data block | 0xacd00a |
| Enter script | 0x92802f → 0x97c10c |
| Step-on table | 0xacd019 (2 entries, 0x0c bytes) |
| B-trigger table | 0xacd027 (0 entries) |

## Overview

A small outdoor fire-pit area east of Crustacia, accessible only from 0x4f (East of Crustacia). This is the WindWalker (WW) landing zone. No combat, no gourds, no B-triggers. The primary gameplay function is the WW landing sequence: when the WindWalker is ready (`$22dc&0x08`, `$237d==2`, `$2355==1 or 2`) the NPC 0x20 (WindWalker) is loaded and the landing step-on triggers the take-off cinematic or the Omnitopia destination dialog.

The room is also one of only two places where `$23bf` is written to 0 (most rooms write 1).

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$22eb` | R/W | &0x20 | IN_ANIMATION — if set on entry: teleport to [0x09,0x19] + fade; cleared otherwise |
| `$23bf` | write | =0x0000 | PACIFIED — written 0 on enter (most rooms write 1) |
| `$22dc` | R | &0x08 | WINDWALKER_UNLOCKED — gates all WW NPC activity |
| `$22e5` | R/W | &0x08 | WW Landing flag — set before loading this room from OW; triggers WW landing teleport on enter |
| `$237b` | R/W | word | WW previous destination — set to 0x0002 when WW landing begins; read to determine if WW enter should repeat |
| `$237d` | R/W | word | WW destination state — 2 = second landing pending / confirmed; 4 = Omnitopia selected |
| `$2355` | R | low byte | WINDWALKER_TYPE / WW landing phase — 1 = first landing (OBJ 0/1 state 1), 2 = second landing (OBJ 0 state 1 / OBJ 1 state 2) |
| `$2834` | write | ptr | NPC pointer — set to last loaded WW NPC (0x20 at [0x19,0x1f]) |
| `$2261` | R | &0x01 | DOG_UNAVAILABLE — if set, dog is hidden at [0x34,0x01] and stopped |
| `$2545` | R | — | Dialog response register — reads Yes/No for Omnitopia prompt in step-on |

## Enter Script Summary (`0x97c10c`)

1. If `$22eb&0x20`: teleport both to [0x09,0x19] + fade music; else clear flag.
2. PLAY MUSIC 0x3a; `$23bf = 0`.
3. Camera bounds: [0x0000–0x0170, 0x0000–0x0190].
4. SET OBJ 0 STATE = 0; SET OBJ 1 STATE = 0.
5. If (`$22e5&0x08` OR `$237b==2`) AND `$22dc&0x08` AND `$237d==2`:
   - If `$2355==1`: SET OBJ 0/1 STATE = 1; LOAD NPC 0x20 at [0x19,0x1f]→`$2834`; animate sprite 0x014e; SKIP to step 6.
   - If `$2355==2`: SET OBJ 0 STATE = 1, OBJ 1 STATE = 2; LOAD NPC 0x20 at [0x19,0x1f]→`$2834`; write `*($2834+30)=16`; animate sprite 0x0144; fall through.
6. If `$22e5&0x08` set:
   - `$237b = 2`; stop boy + dog; teleport NPC/boy/dog to signed arg positions; END.
7. Else: if dog unavailable (`$2261&0x01`): hide dog at [0x34,0x01], call 0x36, stop dog; else: cinematic setup (sub 0x92de75).
8. If WW unlocked AND NOT (`$22e5&0x08` AND `$237d==2`): call 0x92dd6e (WW setup sub) + 0x97c0f3 (WW position sub).

## Step-on Scripts (2 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [14,1c:16,21] | `0x97bfde` | **EXIT west** → 0x4f (East of Crustacia) at [0x01f8, 0x0258]; fade music + prep exit |
| [1c,1b:24,22] | `0x97bfe8` | **WindWalker platform** — fade music; if `$2355==1`: WW first landing cinematic (call 0x97c08d for animation, then 0x92dc83 for NPC move, set `$237d=2`, call 0x92dc02); if `$2355==2`: same animation setup + show dialog: "Is your destination Omnitopia?[LF]Yes.[LF]No." → Yes: `$237d=4`, call 0x92dc51; No: `$237d=2`, call 0x92dc1b |

## Exits

| Tiles | Destination | Coordinates | Notes |
|-------|-------------|-------------|-------|
| [14,1c:16,21] | 0x4f — East of Crustacia | [0x01f8, 0x0258] | step-on |

## B-Triggers

None.

## NPCs

| NPC | Qty | Spawn | Notes |
|-----|-----|-------|-------|
| NPC 0x20 (WindWalker) | 0 or 1 | [0x19, 0x1f] | Conditionally loaded: only if WW unlocked AND `$237d==2`; stored in `$2834`; OBJ 0/1 state gates load; sprite differs by phase (0x014e for phase 1, 0x0144 for phase 2) |

## Notes

- **WW phase 1** (`$2355==1`): Both OBJ 0 and 1 state = 1; WW NPC loaded; step-on triggers first WW landing animation; sets `$237d=2` (second landing ready), then ends via sub 0x92dc02.
- **WW phase 2** (`$2355==2`): OBJ 0 state = 1, OBJ 1 state = 2; WW NPC loaded with extra parameter; step-on shows Omnitopia Yes/No dialog; Yes → `$237d=4` (Omnitopia selected, sub 0x92dc51); No → `$237d=2` (retry, sub 0x92dc1b).
- **`$23bf=0`**: Unlike most rooms (which set PACIFIED=1), this room sets it to 0. Likely disables pacification of enemies/triggers in this area.
- **`$22e5&0x08` on entry**: If the WW landing flag is already set when entering, the enter script teleports boy/dog/NPC to pre-set landing positions and writes `$237b=2`, then returns immediately without running cinematic setup. This handles the case where the player is being transported by the WW.
- // TODO: Identify subs 0x92dc02, 0x92dc1b, 0x92dc51, 0x92dc83, 0x92dd6e, 0x97c08d (WW landing/launch cinematic chain).
