# 0x01 — Exterior of Blimp's Hut

**ROM:** `0x9ffdeb` | **Data:** `0xa9e517` | **Enter:** `0x928020` → `0x978e34`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x0c` |
| Map bounds | Default (outdoor area) |
| Dog form | Wolf (`$2443=0x02`) |
| Objects | ~12 (0–11; some gated by `$225e&0x80`) |
| NPCs | 0 on load (Salabog/NPC summoned by fight trigger) |
| Step-on zones | 4 |
| B-triggers | 0 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| Into hut | `0x51` Village Huts and Blimp's Hut @ `[0x02a0\|0x0378]` | step-on `[14,0c:15,0d]` | hut 0x09 (Blimp's hut); Global 0x27 |
| South | `0x65` Swamp (main area) @ `[0x0490\|0x0008]` | step-on `[13,32:17,34]` | outdoor → outdoor (Global 0x21) |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$225e` | `0x80` | 📖 | Salabog defeated (gates unload of objs 1–11; clears post-fight rubble/obstacles) |
| `$22e8` | `0x02` | 📖 | Salabog fight started (gates fight trigger step-ons) |

## Objects

All objects 1–11 are unloaded if `$225e&0x80` (Salabog defeated). Object 0 is summoned during the fight cinematic (loaded with state 0x7e).

## Enter Script Summary

1. Set dog form to Wolf (`$2443=0x02`).
2. If not re-entry: teleport both to `(0x1b, 0x5d)`.
3. Set `$23bf=0x0000`; play music `0x0c`.
4. If `$225e&0x80`: unload objs 7, 8, 1, 2, 3, 4, 5, 6, 11, 10, 9 (clear post-fight rubble/blocks).
5. Call cinematic entry (`0x92de75`). Sleep 14 ticks. End.

## Step-on Zones

| Zone | Action | Notes |
|------|--------|-------|
| `[14,0c:15,0d]` | CHANGE MAP = `0x51` @ `[0x02a0\|0x0378]`, hut `0x09` | Enter Blimp's hut |
| `[13,32:17,34]` | CHANGE MAP = `0x65` @ `[0x0490\|0x0008]` | South to Swamp |
| `[13,16:1a,17]` | **Salabog fight trigger** (first encounter) | If `$22e8&0x02`: skip (fight over). Otherwise: spawn NPC `0x2e`, cinematic, spawn NPC `0x2c` Salabog, fight! |
| `[13,13:15,14]` | Set `$22e8\|=0x02` if not set | Alternate entry guard zone |

## Salabog Fight Trigger (`[13,16:1a,17]`)

1. Guard: if `$22e8&0x02` already set → END (fight complete or started).
2. Set `$22e8|=0x02` (Salabog fight started).
3. Load NPC `0x2e` with state 0x0020 at `(0x1b, 0x15)` — store ref in `$245b`, face south.
4. Stop both characters; setup movement params (`$242b=0x0050`, `$242d=0x0010`).
5. Wait for entity, play SFX, call Global script 0x09.
6. **TEXT 15db:** *"Hey, kid! Give me a hand with this snake! It's getting out of control!"* (Blimp NPC `0x2e`)
7. Clear text; load Salabog (NPC `0x2c`) at `(0x1e, 0x22)`, ref → `$24e5`.
8. Assign Salabog kill script `0x1980` (address `0x978df7`).
9. Set `$23db=0x0020`; teleport Salabog to `(0x22, 0x1e)`.
10. Return player control; screen shake, SFX `0x6a`, shake 59 ticks.
11. Destroy NPC `0x2e` (Blimp flees); set `$24e3=0x0002`. End.

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x1980` (`0x978df7`) | Salabog damage / kill handler |

## Notes

- **Salabog** (NPC `0x2c`) is the Act 1 mini-boss encountered here. It's a large snake in the swamp. `$22e8&0x02` = "Salabog fight started" is set on first entry to the trigger zone. `$225e&0x80` is set upon defeat (presumably by the kill script `0x1980`).
- **Post-fight:** with `$225e&0x80` set, enter script unloads objs 1–11 on re-entry, clearing whatever visual obstacles surrounded the fight area.
- NPC `0x2e` is Blimp (helper NPC who summons the fight). He's despawned at the end of the trigger sequence.
- Step-on `[13,13:15,14]` is a smaller guard zone that sets the fight flag without triggering the full cinematic — used for players entering the area from a slightly different position.
- `$23bf=0x0000` is explicitly cleared on entry (no sky/parallax effect, unlike the swamp rooms where it was set).
- Music `0x0c` is shared with the swamp area rooms (0x65, 0x66).
