# Room 0x71 — Gothica: Ivor Tower East Room + Kitchen

| Field | Value |
|-------|-------|
| **Room ID** | 0x71 |
| **Act** | 3 — Gothica |
| **Data** | `0x9f8000` |
| **Enter script** | `0x928250` → `0x9888fa` |
| **Dog sprite** | Poodle (0x08) |
| **Music** | 0x82 (normal) / 0x80 (Pierre kitchen cutscene) |
| **Step-ons** | 57 entries |
| **B-triggers** | 32 entries (at `0x9f8167`) |
| **Connections** | 0x6f (Dining Room), 0x70 (Exterior Bridges), 0x72 (East Upper Floor), 0x73 (Dog Maze Underground), 0x75 (Stairwell to Dungeon) |

---

## Overview

The east half of Ivor Tower's interior. A massive multi-corridor hall containing:
- A **kitchen** in the far north-east (Chef Pierre's domain)
- 19 **locked rooms** along corridors (Queen's Key Doors — two-sided step-on per door)
- 10 **ventilation shaft grates** that drop the dog to the underground maze (0x73)
- A **dungeon stairwell** door in the west wing (0x75, dog only)
- Staircase exits to the upper floor (0x72) and balcony exits to the exterior (0x70)
- 25 **sniff spots** and 6 **gourds**
- The **Fire Power Dude** NPC at `[2f,43]` (NPC 0x48, talk script 0x19b3)

---

## Enter Logic

```
$23bf = 0x0001
Scroll limits: [0x0010, 0x0010]
Dog = Poodle (0x08)
```

### Pre-Branch Setup

1. Stop both characters; unhide text
2. If `$22f4&0x02` (Boy in special position): teleport boy using args `0x009d77`+`[0x20,0x10]`, face west — boy appears sliding in from east
3. Guard `$22eb&0x20`; teleport both to `[47,91]`; fade music

### OBJ Unload (Sniff/Gourd Persistence)

Mass unload based on looted flag bytes:
- `$22cc`/`$22cd`/`$22ce`/`$22cf` bits → unload OBJs 0x2f–0x47 (sniff spot OBJs)
- `$2282`/`$2283` bits → unload OBJs 19–23 and 0x2e (gourd OBJs)
- If `$22e5&0x40` (West castle collapsed): also unload OBJs 24–0x2e; `$2437=0x0007`

### NPC Load

- Load Fire Power Dude: `$2455` = NPC 0x48 at `[2f,43]`, talk script 0x19b3

### Branch Table (evaluated after setup)

| Condition | Action |
|-----------|--------|
| `$234b == 0x64` (returning from Queen's Room escape) | Play music 0x82; toggle OBJ 6; sound 0x46; cinematic; reload OBJ 6; sound 0x42 → **END** |
| Mask `$234b` to low nibble, then: | |
| `$234b & 0x08` | Play music 0x82; RCALL enter-right (−16); dog = player controlled → **END** |
| `$234b & 0x04` + `$234b & 0x01` + `$22dc&0x02` | Play music 0x82; clear `$2261&~0x02`; RCALL enter-left (+16); show *"[dog]!! You're back!! I was very worried."*; both player controlled → **END** |
| `$234b & 0x04` + `$234b & 0x01` + NOT `$22dc&0x02` | Play music 0x80; hide status bar; RCALL dog-escape-from-kitchen (0x97ecf0) → CHANGE MAP 0x6f `[0x01d8\|0x0108]` with `$234b=0x0050` |
| `$234b & 0x04` only | Play music 0x82; RCALL enter-left (+16); dog = player controlled; clear `$22f4&~0x02` → **END** |
| `$234b & 0x02` | Sound 0x5a; cinematic → **END** |
| `$234b == 0x60` | RCALL 0x97eb8a → **Chef Pierre Cutscene** (see below) |
| Default | `$238f=0x0000`; `$234b=0x0000` → **END** |

---

## Chef Pierre Cutscene (RCALL 0x97eb8a — triggered when `$234b==0x60`)

Fires when the player enters after being "captured" in the Dining Room.

### Setup
- `$2847=0x0002`; boy unavailable (`$2261|=0x02`); dog available (`$2261&=~0x01`)
- Switch to dog control; boy teleported off-screen to `[0,0]`
- Play music 0x80
- Camera scroll locked to kitchen corner: `[0x0260,0x04c0]` → `[0x03c0,0x0620]`

### NPC Load (Chef Pierre)
- NPC 0x40 ("Pierre") loaded at `[55,ab]` → pointer `$283b`
- Second NPC 0x40 at `$283d=0x1540` / `$283f=0x00ab`, `$2841=0x1400` / `$2843=0x00ad`

### Dialog & Chase

> **Pierre:** *"Say Goodnight, my leetell piggy. You shall be my masterpiece at the queen's deenair! You are not a very pretty piggy. Are you?"*

> **Pierre (dog reveals):** *"Sacre Bleu!! You are not a pig! Well, whatever you are, Pierre shall make you tasty!"*

- Dog runs west, south, west in segments via RCALL 0x97ea57 (chase animation)

> **Pierre (chasing):** *"Come to Pierre, you son of a motherless rodent!!"*

### Chase Outcome
- `$2834|=0x01` (chase active flag set)
- Message timer fires; CALL 0x988729 → triggers step-on `[39,69]`
- Dog falls through vent `[39,69]` → `$238f=0x0002`; CHANGE MAP 0x73 `[0x03e8|0x0428]`

---

## Step-On Table

### Vent Grates → 0x73 (Dog Maze Underground)

All vents use the same shared subroutine at `0x98819b`:
- **Boy controlled**: shows *"Hmmm... I can't see the bottom. I'd better avoid these vents."* → boy walks away; no fall
- **Dog controlled, boy present, `$2352`≠0**: shows *"Hey, [dog]! Get away from there!"* → dog walks away; no fall
- **Dog controlled, boy unavailable OR chase active OR `$2352`=0**: dog walks to vent, brightness fades (brightness 14→7 over 7 ticks, sound 0x5e), music stops → `$234b=0x0096` → CHANGE MAP 0x73

| Tile | Walk dir | `$238f` | MAP 0x73 coords |
|------|----------|---------|----------------|
| `[39,69]` | (chase script) | 0x0002 | `[0x03e8\|0x0428]` |
| `[40,46]` | east (+1) | 0x0004 | `[0x04b0\|0x0278]` |
| `[35,46]` | east (+1) | 0x0001 | `[0x03c0\|0x0298]` |
| `[27,46]` | east (+1) | 0x0003 | `[0x02c0\|0x0288]` |
| `[2d,2c]` | west (−1) | 0x0003 | `[0x0328\|0x0178]` |
| `[40,2d]` | east (+1) | 0x0004 | `[0x04a0\|0x0148]` |
| `[46,14:47,15]` | east (+1) | 0x0004 | `[0x04e0\|0x0098]` |
| `[2f,14:30,15]` | west (−1) | 0x0002 | `[0x0328\|0x0068]` |
| `[13,14:14,15]` | east (+1) | 0x0001 | `[0x0118\|0x0068]` |
| `[4e,46:4f,47]` | west (−1) | 0x0004 | `[0x05b0\|0x02b8]` |
| `[34,2c:35,2e]` | west (−1) | 0x0003 | `[0x03c8\|0x0178]` *(fade-out style: no brightness anim; uses screen fade + sound 0x5e)* |

**Creaking board** (no fall): `[30,2d:33,2e]` → sound 0xb8; SLEEP 149 ticks; no map change

### Dog Chase Trigger

`[5b,46:5c,48]` — only fires when `$2352 != 0` OR `$22f4&0x04`:
- Dog faces west; plays boy dialog *"Hey, [dog]!! Where are you going? Come back here!!"*
- Sets `$2834|=0x01` (chase active), `$2261|=0x02` (boy unavailable), `$22f4|=0x02`
- Calls step-on handler for `[4e,46:4f,47]` → dog drops to 0x73 `[0x05b0|0x02b8]`

### Room Exits

| Tile | Destination | Coords | `$238f` | `$234b` |
|------|-------------|--------|---------|---------|
| `[74,34:75,3a]` | 0x72 East Upper Floor | `[0x0228\|0x01c8]` | 0x0001 | 0x00b0 |
| `[01,35:02,3a]` | 0x72 East Upper Floor | `[0x01a8\|0x01c8]` | 0x0002 | 0x00a0 |
| `[03,52:05,55]` | 0x70 Exterior Bridges | `[0x0168\|0x0148]` | 0x0002 | 0x00a0 |
| `[71,52:73,55]` | 0x70 Exterior Bridges | `[0x02f8\|0x0140]` | 0x0001 | 0x00b0 |

### Dungeon Entrance

`[6b,1e:6d,1f]`:
- If boy is player-controlled: *"Won't Open"* (step-on deflection, walk south)
- If dog is player-controlled: sound 0x46; OBJ 6 toggle; → 0x75 `[0x0050|0x0118]`

### Queen's Key Doors (19 locked rooms × 2 sides each)

All call `0x97edd8` ("Queen's Key Door") with a numeric argument. Positive arg = approach from south; negative arg = approach from north.

| South-side tile | Bit flag | Arg | North-side tile | Arg |
|----------------|----------|-----|----------------|-----|
| `[17,1e:19,1f]` | `$2834&0x02` | +1 | `[17,19:19,1a]` | −1 |
| `[25,1e:27,1f]` | `$2834&0x04` | +2 | `[25,19:27,1a]` | −2 |
| `[33,1e:35,1f]` | `$2834&0x08` | +3 | `[33,19:35,1a]` | −3 |
| `[41,1e:43,1f]` | `$2834&0x10` | +4 | `[41,19:43,1a]` | −4 |
| `[4f,1e:51,1f]` | `$2834&0x20` | +5 | `[4f,19:51,1a]` | −5 |
| `[5d,1e:5f,1f]` | `$2834&0x40` | +6 | `[5d,19:5f,1a]` | −6 |
| `[60,37:62,38]` | `$2835&0x01` | +8 | `[60,32:62,33]` | −8 |
| `[52,37:54,38]` | `$2835&0x02` | +9 | `[52,32:54,33]` | −9 |
| `[44,37:46,38]` | `$2835&0x04` | +10 | `[44,32:46,33]` | −10 |
| `[30,37:32,38]` | `$2835&0x08` | +11 | `[30,32:32,33]` | −11 |
| `[22,37:24,38]` | `$2835&0x10` | +12 | `[22,32:24,33]` | −12 |
| `[14,37:16,38]` | `$2835&0x20` | +13 | `[14,32:16,33]` | −13 |
| `[14,50:16,51]` | `$2835&0x40` | +14 | `[14,4b:16,4c]` | −14 |
| `[22,50:24,51]` | `$2835&0x80` | +15 | `[22,4b:24,4c]` | −15 |
| `[30,50:32,51]` | `$2836&0x01` | +16 | `[30,4b:32,4c]` | −16 |
| `[44,50:46,51]` | `$2836&0x02` | +17 | `[44,4b:46,4c]` | −17 |
| `[52,50:54,51]` | `$2836&0x04` | +18 | `[52,4b:54,4c]` | −18 |
| `[30,58:32,59]` | `$2836&0x08` | +19 | *(no north-side)* | — |

> ⚠️ No step-on for `$2834&0x80` (door 7). This bit is unassigned or used elsewhere.

---

## B-Triggers (32 entries)

### Sniff Spots (25 spots)

| Tile | Flag | Item | MAP REF | NEXT ADD |
|------|------|------|---------|----------|
| `[12,44:13,45]` | `$22cc&0x08` | 🌿 Iron | 0x002f | 0x0001 |
| `[22,12:23,13]` | `$22cc&0x10` | 🌿 Iron | 0x0030 | 0x0003 |
| `[20,2b:21,2c]` | `$22cc&0x20` | 🌿 Acorns | 0x0031 | — |
| `[47,2b:48,2c]` | `$22cc&0x40` | 🌿 Acorns | 0x0032 | 0x0002 |
| `[63,45:64,46]` | `$22cc&0x80` | 🌿 Acorns | 0x0033 | 0x0003 |
| `[39,5e:3a,5f]` | `$22cd&0x01` | 🌿 Mushroom | 0x0034 | 0x0002 |
| `[28,64:29,65]` | `$22cd&0x02` | 🌿 Mushroom | 0x0035 | 0x0001 |
| `[21,46:22,47]` | `$22cd&0x04` | 🌿 Brimstone | 0x0036 | 0x0002 |
| `[14,2b:15,2c]` | `$22cd&0x08` | 🌿 Brimstone | 0x0037 | 0x0002 |
| `[41,12:43,13]` | `$22cd&0x10` | 🌿 Brimstone | 0x0038 | 0x0003 |
| `[31,2c:32,2d]` | `$22cd&0x20` | 🌿 Feather | 0x0039 | 0x0002 |
| `[33,44:34,45]` | `$22cd&0x40` | 🌿 Feather | 0x003a | 0x0001 |
| `[50,2b:51,2c]` | `$22cd&0x80` | 🌿 Feather | 0x003b | 0x0003 |
| `[43,2b:44,2c]` | `$22ce&0x01` | 🌿 Roots | 0x003c | 0x0001 |
| `[37,12:38,13]` | `$22ce&0x02` | 🌿 Roots | 0x003d | — |
| `[26,2a:27,2b]` | `$22ce&0x04` | 🌿 Roots | 0x003e | 0x0002 |
| `[64,2b:65,2c]` | `$22ce&0x08` | 🌿 Roots | 0x003f | 0x0001 |
| `[74,3e:75,3f]` | `$22ce&0x10` | 🌿 Ash | 0x0040 | 0x0002 |
| `[01,3e:02,3f]` | `$22ce&0x20` | 🌿 Ash | 0x0041 | 0x0003 |
| `[30,6b:32,6c]` | `$22ce&0x40` | 🌿 Water | 0x0042 | 0x0001 |
| `[18,45:19,46]` | `$22ce&0x80` | 🌿 Water | 0x0043 | 0x0001 |
| `[27,38:28,39]` | `$22cf&0x01` | 🌿 Ethanol | 0x0044 | 0x0002 |
| `[49,47:4a,48]` | `$22cf&0x02` | 🌿 Ethanol | 0x0045 | 0x0003 |
| `[59,48:5b,49]` | `$22cf&0x04` | 🌿 Ethanol | 0x0046 | 0x0003 |
| `[10,56:11,57]` | `$22cf&0x08` | 🌿 Ethanol | 0x0047 | 0x0002 |
| `[27,6b:28,6c]` | — | *(empty — END only)* | — | — |

### Gourds (6 gourds)

| Tile | Flag | Item | MAP REF | NEXT ADD |
|------|------|------|---------|----------|
| `[44,42:46,44]` | `$2282&0x40` | 🫙 Wings | 0x0013 | — |
| `[14,44:16,46]` | `$2282&0x20` | 🫙 Biscuit | 0x0014 | — |
| `[25,12:27,14]` | `$2283&0x01` | 🫙 Acorns | 0x0015 | 0x0001 |
| `[4a,12:4c,14]` | `$2283&0x02` | 🫙 Iron | 0x0016 | 0x0001 |
| `[58,12:5a,14]` | `$2283&0x04` | 🫙 Honey | 0x0017 | — |
| `[5d,2b:5f,2d]` | `$2282&0x80` | 🫙 Mushroom | 0x002e | 0x0002 |

---

## Memory Access

| Address | Bits | Type | Description |
|---------|------|------|-------------|
| `$234b` | word | 📖 | Entry source code: 0x60=dog captured (Pierre scene), 0x64=escaping Queen's Room, low nibble bits=walk-in direction; 0x0096=exiting via vent |
| `$22dc` | 0x02 | 📖 | Dog escaped kitchen (set after 0x97ecf0 RCALL) |
| `$22e5` | 0x40 | 📖 | West castle collapsed |
| `$22f4` | 0x02 | 📖 | Boy in special east-entry position |
| `$22f4` | 0x04 | 📖 | Dog chase-escape seen flag |
| `$2834` | 0x01 | 📖 | Kitchen chase scene active (blocks dog from vent deflection) |
| `$2834` | 0x02–0x40 | 📖 | Queen's Key Door state — doors 1–6 unlocked |
| `$2835` | 0x01–0x80 | 📖 | Queen's Key Door state — doors 8–15 unlocked |
| `$2836` | 0x01–0x08 | 📖 | Queen's Key Door state — doors 16–19 unlocked |
| `$2261` | 0x02 | ⚙️ | Boy unavailable flag |
| `$2352` | word | 📖 | Non-zero = boy companion warning dialog active (suppresses dog vent fall) |
| `$22cc` | 0x08–0x80 | 👃 | Sniff spots: Iron×2, Acorns×3 |
| `$22cd` | 0x01–0x80 | 👃 | Sniff spots: Mushroom×2, Brimstone×3, Feather×3 |
| `$22ce` | 0x01–0x80 | 👃 | Sniff spots: Roots×4, Ash×2, Water×2 |
| `$22cf` | 0x01–0x08 | 👃 | Sniff spots: Ethanol×4 |
| `$2282` | 0x20–0x80 | 🫙 | Gourds: Biscuit, Wings, Mushroom |
| `$2283` | 0x01–0x04 | 🫙 | Gourds: Acorns, Iron, Honey |
| `$2437` | word | 🎥 | Camera scroll limits (0x0007 if west castle collapsed) |
| `$23bf` | word | ⚙️ | Set to 0x0001 on enter |
| `$238f` | word | ⚙️ | Vent entrance selector (0x0001–0x0004 → which area of 0x73) |
| `$2847` | word | ⚙️ | Set to 0x0002 in Pierre scene |
| `$2455` | word | ⚙️ | Fire Power Dude NPC pointer |
| `$283b`–`$2843` | word×5 | ⚙️ | Chef Pierre NPC pointers + positions |

## Notes

- The most complex room in Act 3: 57 step-ons, 32 B-triggers, 20 sniff spots, 6 gourds, and 19 Queen's Key Doors.
- The Chef Pierre kitchen capture sequence sets `$234b=0x60` (dog captured); the dog escapes via ceiling vents to 0x73 underground while the boy is hidden throughout (`$2261&0x02`).
- The 19 Queen's Key Doors (`$2834` bits 0x02–0x40, `$2835` bits 0x01–0x80, `$2836` bits 0x01–0x08) unlock one at a time as the dog retrieves the corresponding keys in 0x72 (East Upper Floor).
