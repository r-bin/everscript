# [0x2c] Antiqua — Halls SE

| Field | Value |
|-------|-------|
| Room ID | `0x2c` |
| Name | Halls SE |
| Act | Act 2 — Antiqua |
| Data | `0xac911f` |
| Enter script ptr | `0x9280f7` |
| Enter script addr | `0x979cec` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | 0x5a (Minitaur alive) / 0x1e (Minitaur defeated) |
| Doggo | Greyhound (0x06) |

## Overview

Southeast wing of the Halls of Colossa. Contains a roaming Minitaur boss (NPC 0x70, entity `$2835`, stomp patrol AI). Once the Minitaur is defeated (`$22e9&0x40`), the room switches to normal Halls music and OBJ 0 is unloaded on enter. A one-time step-on switch at `[12,19:14,1b]` activates the SE passage (`$228a|=0x40`), opening the exit tile back to the main hub. Before the switch is activated, the east exit tile does nothing. No gourds.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | 0x20 | ⚙️ | Enter animation guard — if clear, teleports both to [0x09,0x23] + fade |
| `$22e9` | 0x40 | 📖 | Minitaur defeated [0x2c] — skips NPC load, switches music to 0x1e, unloads OBJ 0 |
| `$228a` | 0x40 | 📖 | Ruins SE switch activated [0x2c] — set by step-on [12,19:14,1b]; gates east exit tile |

## Enter Script Summary

1. Write `$0ea2+8=0x01`, `$0eac+8=0x1794` (Halls Wings parameter).
2. Set Greyhound.
3. **Entry guard:** if NOT `$22eb&0x20` → teleport both to [0x09,0x23] + fade-out. Else clear `$22eb&0x20`.
4. If `$22e9&0x40` (Minitaur defeated) → unload OBJ 0.
5. Music logic: if `$238d!=0`: if NOT `$22e9&0x40` → play music 0x5a (boss theme); else → play music 0x1e (Halls theme); fade-in.
6. `$23bf=0`; CALL cinematic sub `0x92de75`.
7. If NOT `$22e9&0x40`: load NPC 0x70 at [0x16,0x20] → entity `$2835`; set talk script `0x198c`; RCALL boss patrol sub `0x979bb7` (Minitaur stomp loop — wanders toward player with random delay; debug text "StopStomp cleared" visible in debug mode).

## Step-on Scripts

| Tiles | Script | Effect |
|-------|--------|--------|
| `[08,16:0a,1a]` | `0x979b89` | Exit west → 0x29 — only if `$228a&0x40` set; else END |
| `[12,19:14,1b]` | `0x979b9d` | SE switch (one-time, `$228a&0x40`): SFX 0x5a + SET OBJ 0 state 11 + YIELD |

## Exits

| Destination | Tiles | Condition |
|-------------|-------|-----------|
| 0x29 — Halls main room | `[08,16:0a,1a]` | requires `$228a&0x40` (switch activated) |

## B-Triggers

None.

## NPCs

| NPC | Count | Position | Entity | Notes |
|-----|-------|----------|--------|-------|
| 0x70 | 1 | [0x16,0x20] | `$2835` | Minitaur boss; stomp patrol AI; talk script `0x198c`; only spawned if NOT `$22e9&0x40` |

## Notes

- The Minitaur patrol sub (`0x979bb7`) uses a randomized timer (`arg0` incremented + `RAND&1`); at threshold 0x3ff it triggers a stomp walk toward the player. The sub loops until the entity is despawned (likely on defeat).
- The SE switch step-on (`[12,19:14,1b]`) uses a conditional YIELD — it only fires once (`$228a&0x40` guard), then on re-step the exit tile at `[08,16:0a,1a]` becomes active.
- `$22e9&0x40` (Minitaur defeated) is presumably set by the Minitaur's defeat script; that flag persists across saves and gates the boss encounter on re-entry.
