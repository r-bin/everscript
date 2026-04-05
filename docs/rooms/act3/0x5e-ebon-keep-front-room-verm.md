# Room 0x5e — Gothica: Ebon Keep Front Room (Verm)

| Field | Value |
|-------|-------|
| **Room ID** | 0x5e |
| **Act** | 3 — Gothica |
| **Data** | `0x9fff5f` |
| **Enter script** | `0x9281f1` → `0x9a81a0` |
| **Dog sprite** | Default (no override) |
| **Music** | 0x66 (Verminator battle) / 0x6e (after Verm dead) |
| **Step-ons** | 10 entries (5 share one address) |
| **B-triggers** | 0 entries |
| **Connections** | 0x0d (Ebon Keep Hall behind Verm, north), 0x5d (Courtyard south), 0x5f (Verm Side Rooms, 2 exits), 0x60 (Storage Room) |

---

## Overview

The large front room of Ebon Keep, where **Verminator** (NPC 0x41) is encountered. Contains Ratling (NPC 0x42) enemies and a multi-trigger doorway grid leading to the upper hall (0x0d). On first approach to the boss tile, Verminator appears and delivers his opening monologue. Music is 0x66 (Verm boss track) before defeat, 0x6e after.

If Verminator is dead (`$22dd&0x01`): OBJ 1 is force-unloaded (body/blocking object removed).
If windwalker is unlocked (`$22dc&0x08`): `$2437=0x0004` (enable windwalker-mode feature).
If debug mode (`$22eb&0x08`): forces `$22dc|=0x08` (windwalker unlocked) on entry.

---

## Enter Logic

1. If NOT `$22eb&0x20`: if debug `$22eb&0x08`: `$22dc|=0x08`. Teleport both to `[15,5b]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. Set enemy loot: Prize 1 = Oil (0x0204) ×10, Prize 2 = Talons (0x0001) qty 0x50 ×3, Prize 3 = Biscuit (0x0802) ×1
4. `$2433 = 0x0002`; spawn 16 NPC 0x42 (Ratling) spawners
5. If music not locked:
   - If `$22dd&0x01` (Verm dead): PLAY MUSIC 0x6e
   - Else: PLAY MUSIC 0x66
   - Fade in
6. If `$22dc&0x08` (windwalker unlocked): `$2437 = 0x0004`
7. If `$22dd&0x01` (Verm dead): unload OBJ 1
8. `$23bf = 0x0000`; `CALL 0x92de75`; END

---

## Step-On Table

### Upper Hall Entrance (5 entries — all go to 0x0d)

All five tiles share the same script at 0x99ef32.

| Tile(s) | Notes |
|---------|-------|
| `[17,13:18,14]`, `[18,13:19,14]`, `[17,14:18,15]`, `[18,14:19,15]`, `[17,13:19,15]` | → 0x0d `[0128, 03a8]` (Ebon Keep Hall behind Verm) |

### Other Step-Ons

| Tile(s) | Action |
|---------|--------|
| `[17,1c:19,1d]` | **Verminator boss trigger**: If `$2834&0x01` or `$22dd&0x01` (fight in progress or Verm already dead): skip. Else: `$2834\|=0x01`, stop movement, fade out + play Verm music (0x24), load Verm NPC at `[16,09]` → `$2835`, set script 0x1a7c ("Verm kill"), walk Verm toward player, restrict camera, move both chars to watch position, yield, show Verm as OBJ states 1/2, display Verm opening dialog ("I am King of the Rats…"), release Verm (`$242f=0x0080`), call 0x99efce (Verm spell cast). |
| `[19,34:1b,36]` | → 0x60 `[0148, 0068]` (Ebon Keep Storage Room) |
| `[17,40:19,42]` | Fade out; `$23b9 = 0x0003`; → 0x5d `[00a0, 0088]` (Courtyard south) |
| `[0e,2a:10,2c]` | → 0x5f `[0108, 0180]` (Verm Side Rooms, left) |
| `[20,2a:22,2c]` | → 0x5f `[0238, 0180]` (Verm Side Rooms, right) |

---

## Verminator Cutscene Dialog (step-on 0x99ef32→ launch at 0x99efb6)

> *"I am King of the Rats! I tell ya! King of the Rats! And I'm claiming this castle in the name of disease-carrying vermin everywhere. Prepare to be plagued!"*

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$22eb` | 0x08 | R | Debug mode |
| `$22dc` | 0x08 | R/W | 📖 Windwalker unlocked |
| `$22dd` | 0x01 | R | 📖 Verminator dead |
| `$2437` | word | W | Windwalker mode enable (0x0004) |
| `$23bf` | word | W | Unknown (cleared) |
| `$2433` | word | W | Enemy spawn count |
| `$238d` | word | R | Music lock |
| `$23b9` | word | W | Entrance selector for 0x5d (set to 3 on south exit) |
| `$2834` | 0x01 | R/W | Verm fight in-progress flag (transient; `$22dd&0x01` is the permanent "dead" flag) |
| `$2835` | word | W | Verminator NPC pointer |

## Notes

- Verminator's permanent death is tracked by `$22dd&0x01`; a separate transient `$2834&0x01` guards the fight-in-progress state and is not saved across room transitions.
- This room shares music logic with 0x5f (Verm Side Rooms) — both switch between 0x66 (boss track) and 0x6e (post-boss) based on `$22dd&0x01`.
- Verminator's opening monologue ("I am King of the Rats!") is a one-shot approach cutscene; the full dialog is documented in this file.
