# 0x1e — Nobilia, Arena Holding Room

| Field | Value |
|-------|-------|
| Room ID | `0x1e` |
| ROM header | `0x9ffe5f` |
| Data ptr | `0xacde7c` |
| Enter script | `0x9280b1` → `0x95cfaa` |
| Step-on table | `0xacde8b`, len=`0x0006` (1 entry) |
| B-trigger table | `0xacde93`, len=`0x0036` (9 entries) |
| Music | `0x02` (Nobilia theme) |
| Act | act2 |

---

## Overview

The staging room outside the Nobilia Arena. The first time you enter, Pompolonius walks in and delivers a welcome speech, offers a save spot, and gives a brief countdown before the gate opens. If re-entering after the arena fight (`$22ee&0x01` set by the Sacred Dog ceremony in [0x08]), the room takes a shortcut path: teleport both characters to their exit positions and skip the cutscene.

The room contains three tiered chest sequences (Chestplate, Gauntlet, Helmet) and five gourds, all gated by `$2271` bits. All chest interactions are boy-only.

---

## Memory Access

| Address | Bits | Name | R/W | Meaning |
|---------|------|------|-----|---------|
| `$22eb` | `0x20` | IN_ANIMATION | R | Standard enter guard; suppresses re-entry |
| `$238d` | all | CHANGE_MUSIC | W | Standard music register |
| `$23bf` | all | PACIFIED | W | Set to `0x0001` on enter |
| `$22ee` | `0x01` | Arena return flag | R/W | Set by Sacred Dog ceremony in [0x08]; if set, skip intro and teleport to exit positions; cleared on enter via `&=0xfe` |
| `$2271` | `0x01` | Chest 1 (chestplate) opened | R/W | If set: unload objs 1+5 on enter; set by chest B-trigger on first loot |
| `$2271` | `0x02` | 🫙 Gourd MAP REF 0x02 looted (Petal) | R/W | `[0x1e]` |
| `$2271` | `0x04` | 🫙 Gourd MAP REF 0x03 looted (Wax) | R/W | `[0x1e]` |
| `$2271` | `0x08` | 🫙 Gourd MAP REF 0x04 looted (Call Beads) | R/W | `[0x1e]` |
| `$2271` | `0x10` | Chest 2 (gauntlet) opened | R/W | If set: unload objs 2+6 on enter; set by chest B-trigger on first loot |
| `$2271` | `0x20` | 🫙 Gourd MAP REF 0x06 looted (Wax) | R/W | `[0x1e]` |
| `$2271` | `0x40` | 🫙 Gourd MAP REF 0x07 looted (Call Beads) | R/W | `[0x1e]` |
| `$2271` | `0x80` | Chest 3 (helmet) opened | R/W | If set: unload objs 3+7 on enter; set by chest B-trigger on first loot |
| `$2263` | `0x02` | Thug's Cloak acquired | W | Set when the chestplate chest cycles past Centurian Cape (4th loot) |
| `$2320` | all | CHEST_2_1 | R/W | Chestplate progression counter (Bronze Chestplate) |
| `$2321` | all | CHEST_2_2 | R/W | Chestplate progression counter (Stone Vest) |
| `$2322` | all | CHEST_2_3 | R/W | Chestplate progression counter (Centurian Cape) |
| `$2338` | all | GLOVE_2_1 | R/W | Gauntlet progression counter (Serpent Bracelet) |
| `$2339` | all | GLOVE_2_2 | R/W | Gauntlet progression counter (Bronze Gauntlet) |
| `$233a` | all | GLOVE_2_3 | R/W | Gauntlet progression counter (Gloves of Ra) |
| `$232c` | all | HELM_2_1 | R/W | Helmet progression counter (Bronze Helmet) |
| `$232d` | all | HELM_2_2 | R/W | Helmet progression counter (Obsidian Helmet) |
| `$232e` | all | HELM_2_3 | R/W | Helmet progression counter (Centurian Helmet) |
| `$2449` | all | Save spot | W | Set to `0x0012` during Pompolonius intro sequence |
| `$2836` | all | Tiny entity ref | W | Entity pointer for Tiny (session-local) |
| `$244d` | all | Pompolonius entity ref | W | Entity pointer for Pompolonius (session-local) |
| `$2834` | all | Fade counter | W | Session-local brightness loop counter |

---

## Enter Script Summary

### Path A — Arena return (`$22ee&0x01` set)

1. Teleport boy to `(13,14)`, dog to `(0f,14)`; both face south
2. BOY + DOG = player-controlled
3. Sleep 179 ticks
4. SET OBJ 0 STATE=4 + SFX `0x76`
5. Clear `$22ee&=0xfe`
6. END

### Path B — Normal (first arrival)

1. Fade in from black
2. Load Tiny (`$2836`, NPC `0x8c`) at `(14,05)`; boy walks in
3. Load Pompolonius (`$244d`, NPC `0x31`) at `(1e,02)`; walks south
4. Pompolonius dialogue:
   - *"Greetings, challenger."*
   - *"You were chosen by the Nobilia Arena Committee…"*
   - *"When the gate opens, come out fighting!"*
5. Save spot offered: `$2449 = 0x0012`
6. Pompolonius walks out + despawned
7. BOY + DOG = player-controlled; 899-tick timer countdown
8. Timer ends → SET OBJ 0 STATE=4 + SFX `0x76`, END

---

## Exits

| Tile rect | Dest | Condition | Notes |
|-----------|------|-----------|-------|
| `[0d,0a:0f,0c]` | 0x1d "Arena (Vigor Fight)" @ `[0x0100\|0x0038]` | always | Align both characters, fade out → CHANGE MAP |

---

## B-Triggers

| # | Tile rect | Flag | Type | Contents |
|---|-----------|------|------|----------|
| 1 | `[06,11:08,13]` | `$2271&0x01` | Chest (boy only) | Cycles `$2320`→`$2321`→`$2322`: Bronze Chestplate → Stone Vest → Centurian Cape → Thug's Cloak (`$2263\|=0x02`) |
| 2 | `[17,14:18,15]` | — | Empty | END immediately |
| 3 | `[13,15:15,17]` | `$2271&0x02` | 🫙 Gourd | Petal (`0x0800`), map ref `0x0002` |
| 4 | `[24,0d:26,0f]` | `$2271&0x04` | 🫙 Gourd | Wax (`0x0200`), map ref `0x0003` |
| 5 | `[27,0d:29,0f]` | `$2271&0x08` | 🫙 Gourd | Call Beads (`0x0807`), map ref `0x0004` |
| 6 | `[2a,0d:2c,0f]` | `$2271&0x10` | Chest (boy only) | Cycles `$2338`→`$2339`→`$233a`: Serpent Bracelet → Bronze Gauntlet → Gloves of Ra → 100 Jewels |
| 7 | `[24,11:26,13]` | `$2271&0x20` | 🫙 Gourd | Wax (`0x0200`), map ref `0x0006` |
| 8 | `[27,11:29,13]` | `$2271&0x40` | 🫙 Gourd | Call Beads (`0x0807`), map ref `0x0007` |
| 9 | `[2a,11:2c,13]` | `$2271&0x80` | Chest (boy only) | Cycles `$232c`→`$232d`→`$232e`: Bronze Helmet → Obsidian Helmet → Centurian Helmet → 100 Jewels |

---

## NPCs

| Entity ref | Type | Pos | Notes |
|------------|------|-----|-------|
| `$2836` | `0x8c` Tiny | `(14,05)` | Loaded on normal enter; no interaction |
| `$244d` | `0x31` Pompolonius | `(1e,02)` | Cutscene-only; despawned after intro |

---

## Notes

- **Two enter paths:** The `$22ee&0x01` check at the top of the enter script lets re-entry after the arena fight skip the full Pompolonius intro. This flag is set in [0x08] during the Sacred Dog ceremony when escorting the dog to the arena, and cleared here on re-entry.
- **Chest tier progression:** Each of the three boy-only chests cycles through equipment tiers (`CHEST_2_x`, `GLOVE_2_x`, `HELM_2_x`), then awards a bonus item (Thug's Cloak / 100 Jewels) on the fourth loot. The chest-open flag gates both the chest object and a second object (likely an overlay sprite), since each `$2271` bit unloads two object indices on enter.
- **`$2271` double-gating:** Bits 0x01/0x10/0x80 each trigger unloading of two objects: e.g. bit 0x01 unloads both obj 1 and obj 5. The exact pairing is `0x01→{1,5}`, `0x10→{2,6}`, `0x80→{3,7}`.
- **Trigger 2 is empty:** The `[17,14:18,15]` B-trigger immediately ENDs — likely a placeholder for a removed interaction or an access-blocker for an internal wall area.
- **Save point at `0x0012`:** `$2449` is set during the intro cutscene; this is the save-register used by the in-world save pedestal mechanic.
- **Music:** `0x02` is the standard Nobilia/Antiqua town theme, same as the square and inn.
