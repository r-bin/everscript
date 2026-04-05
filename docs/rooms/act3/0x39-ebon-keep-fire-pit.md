# [0x39] Gothica — Ebon Keep Fire Pit (Rocket / WindWalker Pad)

| Field | Value |
|-------|-------|
| Room ID | 0x39 |
| Name | Gothica - Ebon Keep Fire pit |
| Act | Act 3 — Gothica |
| Data offset | `0xaca984` |
| Enter script | `0x928138` → `0x9acf9e` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | 0x70 (normal) / 0x84 (outro) / 0x52 (rocket launch) |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | `$2835` = NPC 0x14 (20 decimal) at `[19,3f]` (WindWalker spirit / rocket OBJ); Tinker `$2455`; Naris `$2841` |
| Forced dog form | Poodle (0x08) — set inside RCALL |
| Music | 0x70 |

---

## Overview

The outdoor pit area behind Ebon Keep, containing the rocket launch platform and WindWalker pad. This room has the most complex enter logic in Act 3 — it handles four distinct scenarios based on game state:

1. **Act 3 finale / earthquake** (`$22f1&0x40`): Camellia's earthquake escape sequence → transitions to 0x11 or 0x46
2. **WindWalker landing** (`$22e5&0x08` + `$22dc&0x08`): WindWalker lands on the pad from the overworld
3. **Rocket launch** (`$2356==3`): Turret launch sequence → CHANGE MAP 0x48 (Metroplex tunnels) — the "shot out of a turret" scene
4. **Normal visits**: Simple cinematic entry with OBJ/NPC load based on `$2355`/`$2356` stage

`$2355` tracks the fire pit's construction stage (0=nothing, 1=building, 2=complete). `$2356` tracks Tinker's overall mission stage.

---

## Enter Script Logic

1. `$22eb&0x20` guard: teleport both to `[27,3b]`, fade-out
2. `$23bf = 0x0001`; unload OBJ 1 and OBJ 2
3. If `$22eb&0x08` (debug flag): set `$22f1|=0x40` and `$22dc|=0x08`
4. **Branch IF `$22f1&0x40`** (outro / earthquake):
   - Fade-out; PLAY MUSIC 0x84; fade-in
   - RCALL 0x9accbe (WindWalker/outro sequence):
     - Load fire-pit NPCs; set `$22e5|=0x08` (WW Landing flag) at `$22fe==2`; or load Naris at `[0f,35]` → `$2841`; position boy/dog
     - Set Poodle: `$2443=0x08`
     - If `$22e5&0x08` (WW landing): call WW landing sub → CHANGE MAP 0x46 @ `[0x01f0|0x00a0]` (Omnitopia, Professor's lab); sets `$2443=0x0C` (Toaster), `$2348=0x0009`, `WINDWALK` call
     - Else (earthquake exit): call outro rain/sky; `$22e5|=0x08`; CHANGE MAP 0x11 @ `[0x00d8|0x00f8]` (Ebon Keep Queen's Room) — actually this completes the earthquake by going back to 0x11 with Camellia
   - (after RCALL): check `$22dc&0x08` + `$22e5&0x08` + `$237d==4` for WW fly sequence
5. **Branch: normal `$22f1` not set**: PLAY MUSIC 0x70; cinematic
6. **If `$22dc&0x08` (WindWalker unlocked) AND `$22e5&0x08` AND `$237d==4`**: WW animation (loading pad sequence)
7. **If `$2356==3`**: RCALL 0x9ac56d (rocket/turret launch — see below)

---

## Turret Launch Cutscene (RCALL 0x9ac56d, `$2356==3`)

Triggered when `$2356==3` (Tinker has completed the rocket and boy+dog have arrived at the fire pit for launch). First sets `$2356=0x0004`.

1. Load Tinker `$2455` at `[2d,39]`; load NPC 0x14 rocket at `[44,3a]` → `$2839`
2. Brightness fade-in
3. Tinker: *"This is it, [boy]! You're going to go where no one has gone before!"*
4. Boy: *"We've actually been there before."* / Tinker: *"Oh."* / Tinker: *"Well, you've never been shot out of a turret, with only a minimal chance of survival!"*
5. Boy: *"That's true."* / Tinker: *"OK! Let's go!"*
6. Characters walk to rocket platform; countdown (11 → 0) displayed in message box
7. Rocket flies: multiple trajectory arc calls; `$22f8|=0x02`
8. Fade-out; CHANGE MAP 0x48 @ `[0x00b8|0x0000]` (Omnitopia — Metroplex tunnels)

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[17,1f:1e,26]` | Fly to Omnitopia (MAP 0x46 via WindWalker) | If `$2355==1`: direct fly (`$237d=0x0004`); if `$2355==2`: ask *"Is your destination Omnitopia? Yes/No"* — Yes=Omnitopia fly, No=other destination |
| `[15,1c:16,1e]` | MAP 0x14 @ `[0x01d0\|0x0198]` | West → Tinker's Room |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x08 | R | ⚙️ Debug flag — forces `$22f1&0x40` and `$22dc&0x08` |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22f1` | 0x40 | R | 📖 Inside outro / earthquake — triggers earthquake escape RCALL |
| `$22dc` | 0x08 | R/W | 📖 WindWalker unlocked |
| `$22e5` | 0x08 | R/W | 📖 WW Landing (set before loading fire pit from overworld) — set/cleared by landing logic |
| `$237d` | — | R/W | ⚙️ WindWalker travel state — set to 0x0004 when flying |
| `$237b` | — | W | ⚙️ WindWalker state — set to 0x0004 on landing |
| `$2355` | — | R/W | 📖 Fire pit stage (1=building, 2=complete/ready) |
| `$2356` | — | R/W | 📖 Tinker stage (3=launch ready → set to 4 after launch cutscene) |
| `$22fe` | — | R/W | ⚙️ WW visit counter — checked for `==2` to set `$22e5&0x08` |
| `$22f8` | 0x02 | W | 📖 Turret launch done — set just before CHANGE MAP 0x48 |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |
| `$2443` | — | W | ⚙️ Dog form: Poodle (0x08) set in outro RCALL; Toaster (0x0c) set for Omnitopia flight |
| `$2348` | — | W | ⚙️ Set to 0x0009 before Omnitopia WINDWALK |
| `$246b` | — | W | ⚙️ Set to 0x0001 before WINDWALK |
| `$2835` | — | W | ⚙️ NPC 0x14 (rocket/WindWalker) pointer |
| `$2455` | — | W | ⚙️ Tinker NPC pointer |
| `$2841` | — | W | ⚙️ Naris NPC pointer (earthquake path) |

## Notes

- Acts as the narrative culmination of Act 3: first the rocket construction and launch sequence, later the WindWalker landing pad for overworld travel.
- Three distinct music tracks switch based on story state: `0x70` (normal), `0x84` (outro earthquake), and `0x52` (rocket launch).
- Dog form changes dynamically: Poodle (`0x08`) in the outro earthquake RCALL; Toaster (`0x0c`) for the Omnitopia WindWalk flight sequence (`$2348=0x0009` before WINDWALK).
- `$22fe` tracks the WindWalker visit count; on the second visit `$22e5&0x08` (WW Landing) is set, activating the landing-pad behavior.
