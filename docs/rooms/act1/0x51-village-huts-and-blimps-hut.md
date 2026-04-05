# Room 0x51 — Prehistoria - Village Huts and Blimp's Hut

**ROM address:** 0x9fff2b
**Data address:** 0xa9aed7
**Enter script:** 0x9281b0 → 0x94e1ee
**Act:** 1 (Prehistoria)
**Analyzed:** 2026-04-03

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on triggers | 9 |
| B-triggers | 25 |
| Gourds | 25 |
| Sniff spots | 0 |
| Enemies | 0 |
| NPCs | 1–3 (depending on active hut) |

---

## Structure

This room contains **9 sub-rooms** arranged in a 3×3 grid, each representing a different hut. The active sub-room is selected by `FAKE_HOUSE_ID ($234b)` written before entering from room 0x25. Each sub-room has its own NPC, map scroll bounds, and object subset.

| FAKE_HOUSE_ID | Hut | Tile Bounds (X, Y) | NPC | Music |
|---|---|---|---|---|
| 1 | Hut 1 | (0,0)–(0x100,0x120) | Man (0x07) | 0x12 |
| 2 | Hut 2 | (0x110,0)–(0x210,0x120) | Old Woman (0x08) | 0x12 |
| 3 | Hut 3 | (0x220,0)–(0x320,0x120) | Old Man (0x09) | 0x12 |
| 4 | Hut 4 | (0,0x130)–(0x100,0x250) | Man (0x07) | 0x12 |
| 5 | Hut 5 | (0x110,0x130)–(0x210,0x250) | Woman (0x06) | 0x12 |
| 6 | Hut 6 | (0x220,0x130)–(0x320,0x250) | Man (0x07) | 0x12 |
| 7 | Fire Eyes' Hut | (0,0x260)–(0x100,0x380) | Fire Eyes (0x15) (conditional) | 0x28 |
| 8 | Hut 8 | (0x110,0x260)–(0x210,0x380) | Woman (0x06) | 0x12 |
| 9 | Blimp's Hut | (0x220,0x260)–(0x320,0x380) | Blimp/Harry (0x17) | 0x0c |

---

## Memory Access

| Address | core.evs Name | Size | Op | Section | Notes |
|---------|--------------|------|----|---------|-------|
| 0x2443 | DOG_WRITE | 16b | W | enter | Writes 0x02 (Wolf) |
| 0x22eb | IN_ANIMATION | 1b | R/W | enter | Bit 0x20: skip teleport; cleared after |
| 0x23bf | PACIFIED | 16b | W | enter | Writes 0x0001 |
| 0x238d | CHANGE_MUSIC | 16b | R | enter | Skips PLAY MUSIC if 0x00 |
| 0x234b | FAKE_HOUSE_ID | 16b | R | enter (all huts) | Selects active sub-room (1–9) |
| 0x22ee | — | 1b | R/W | enter (huts 3, 9) | Bit 0x01 "unknown intro/outro? flag in prof. lab"; teleports boy/dog on entry if set; cleared |
| 0x22ed | — | 1b | R | enter | Bit 0x04: triggers FE Cutscene 1 in hut 3 (raptor healing scene) |
| 0x22dc | — | 1b | R | enter (hut 7) | Bit 0x08 "windwalker unlocked"; routes between FE Cutscene 2 and 3 |
| 0x22ec | — | 1b | W | FE Cutscene 3 | Bit 0x20 set at start (windwalker flag) |
| 0x2260 | — | 1b | R | enter (hut 7), gourd obj17 | Bit 0x10 "Thraxx dead"; routes FE dialogue and gourd content |
| 0x225f | RAPTORS | 1b | R/W | enter (hut 7) | Bit 0x80 "Village post-thraxx message shown?"; gates FE Cutscene 2 |
| 0x228b | — | 1b | R/W | enter (hut 7) | Bit 0x01 "FE visited pre-thraxx"; guards FE First Encounter |
| 0x2264 | — | 1b | R/W | enter (hut 7), gourds obj0–obj1 | Bits 0x40/0x80: gourds 0/1 persistence; bits 0x04/0x08 (Gauge/Wheel): gate Fire Eyes dialogue |
| 0x2265 | — | 1b | R/W | gourds obj2–obj9 | Bits 0x01–0x80: gourds 2–9 persistence |
| 0x2266 | — | 1b | R/W | gourds obj10–obj17 | Bits 0x01–0x80: gourds 10–17 persistence; bit 0x80 uses Thraxx flag for content |
| 0x2267 | — | 1b | R/W | gourds obj18–obj23; enter (hut 7) | Bits 0x01–0x40: gourds 18–23 persistence; bit 0x10 UNLOAD OBJ 16; bit 0x01 UNLOAD OBJ 16 |
| 0x2268 | — | 1b | R/W | gourd obj24; enter (hut 8) | Bit 0x01: gourd 24 persistence; bit 0x04/0x08/0x10/0x20 UNLOAD OBJs 20–23 |
| 0x2266 | — | 1b | R | enter (hut 7) | Bit 0x80 → UNLOAD OBJ 17 |
| 0x2267 | — | 1b | R | enter (hut 7) | Bit 0x01 → UNLOAD OBJ 16 |
| 0x22e5 | — | 1b | R/W | FE Cutscene 1 | Bit 0x20 "Defeated raptors?"; read for opening line variation; set in FE Cutscene 1 |
| 0x2834 | — | 1b | W | FE Cutscene 1, Blimp | Bit 0x01 set in FE Cutscene 1; bit 0x02 set/cleared in Blimp cutscene |
| 0x2259 | — | 1b | W | FE First Encounter | Bit 0x80 "Flash"; set when Flash alchemy is granted |
| 0x225c | — | 1b | W | FE Cutscene 3 | Bit 0x40 "FE call beads?" |
| 0x234a | — | 16b | W | FE Cutscene 3 | Written 0x0063 |
| 0x225e | — | 1b | R/W | Blimp cutscene | Bit 0x80 "Talked to Blimp in hut?"; guards cutscene; set at start |
| 0x225f | — | 1b | R | Blimp cutscene | Bit 0x02 "???"; gates Levitate vs generic Mud Pepper text |
| 0x231c | — | 8b | W | FE Cutscene 3 | += 6 (grants 6 Call Beads) |
| 0x2305 | — | 8b | W | Blimp cutscene | += 1 (grants 1 Mud Pepper) |
| 0x2445 | PRESELECT_ALCHEMY | 16b | W | FE First Encounter | Written 0x001e (Flash formula) before alchemy screen |
| 0x2391 | LOOT_ITEM | 16b | W | all gourds | Item type |
| 0x2393 | LOOT_AMOUNT | 16b | W | money gourds (obj4, obj9) | Written 0x001e (30 talons) / 0x0012 (18 talons) |
| 0x2395 | LOOT_OBJECT | 16b | W | all gourds | MAP REF (0x0000–0x0018) |
| 0x2461 | LOOT_AMOUNT | 16b | W | selected gourds | Extra items; objs 2/7/9/12/13/15/19/20/21/22 get AMOUNT written |
| 0x22ea | LOOT_SUCCESSFUL | 1b | R | all gourds | Bit 0x01 |
| 0x2413 | — | 16b | W | FE Cutscene 2/3, Blimp | Camera X target |
| 0x2415 | — | 16b | W | FE Cutscene 2/3, Blimp | Camera Y target |
| 0x242f | CAMERA_PAN_SPEED | 16b | W | FE Cutscene 2/3, Blimp | Written 0x0018 or 0x0020 or 0x0080 |
| 0x2455 | VENDOR_ENTITY | 16b | W | enter (huts 1, 4, 5) | Written with last entity ref (NPC entity) |
| 0x245b | — | 16b | W | enter (hut 9) | Written with Blimp entity ref |
| 0x2533 | — | 16b | W | enter (huts 2, 3) | Written with last entity ref before NPC or companion load |
| `$2264` | `0x40` | 🫙 | R/W | Gourd obj0 (Roots) looted |
| `$2264` | `0x80` | 🫙 | R/W | Gourd obj1 (Water) looted |
| `$2265` | `0x01` | 🫙 | R/W | Gourd obj2 (Water) looted |
| `$2265` | `0x02` | 🫙 | R/W | Gourd obj3 (Water) looted |
| `$2265` | `0x04` | 🫙 | R/W | Gourd obj4 (Money 30 talons) looted |
| `$2265` | `0x08` | 🫙 | R/W | Gourd obj5 (Nectar) looted |
| `$2265` | `0x10` | 🫙 | R/W | Gourd obj6 (Water) looted |
| `$2265` | `0x20` | 🫙 | R/W | Gourd obj7 (Roots) looted |
| `$2265` | `0x40` | 🫙 | R/W | Gourd obj8 (Clay) looted |
| `$2265` | `0x80` | 🫙 | R/W | Gourd obj9 (Money 18 talons) looted |
| `$2266` | `0x01` | 🫙 | R/W | Gourd obj10 (Clay) looted |
| `$2266` | `0x02` | 🫙 | R/W | Gourd obj11 (Water) looted |
| `$2266` | `0x04` | 🫙 | R/W | Gourd obj13 (Water) looted |
| `$2266` | `0x08` | 🫙 | R/W | Gourd obj12 (Roots) looted |
| `$2266` | `0x20` | 🫙 | R/W | Gourd obj14 (Roots) looted |
| `$2266` | `0x40` | 🫙 | R/W | Gourd obj15 (Water) looted |
| `$2266` | `0x80` | 🫙 | R/W | Gourd obj17 (Biscuit/Call Beads) looted |
| `$2267` | `0x01` | 🫙 | R/W | Gourd obj16 (Water) looted |
| `$2267` | `0x02` | 🫙 | R/W | Gourd obj18 (Petal) looted |
| `$2267` | `0x04` | 🫙 | R/W | Gourd obj19 (Clay) looted |
| `$2267` | `0x08` | 🫙 | R/W | Gourd obj20 (Water) looted |
| `$2267` | `0x10` | 🫙 | R/W | Gourd obj21 (Water) looted |
| `$2267` | `0x20` | 🫙 | R/W | Gourd obj22 (Water) looted |
| `$2267` | `0x40` | 🫙 | R/W | Gourd obj23 (Water) looted |
| `$2268` | `0x01` | 🫙 | R/W | Gourd obj24 (Water) looted |

---

## Objects (Gourds)

| Obj ID | Item | Persistence | Tile | Notes |
|--------|------|-------------|------|-------|
| 0x0000 | Roots | $2264 bit 0x40 | [04,06:06,08] | AMOUNT=1 |
| 0x0001 | Water | $2264 bit 0x80 | [0b,07:0d,09] | |
| 0x0002 | Water | $2265 bit 0x01 | [14,07:16,09] | AMOUNT=2 |
| 0x0003 | Water | $2265 bit 0x02 | [17,06:19,08] | |
| 0x0004 | Money | $2265 bit 0x04 | [1a,06:1c,08] | AMOUNT=30 talons ($2393=0x1e) |
| 0x0005 | Nectar | $2265 bit 0x08 | [25,07:27,09] | |
| 0x0006 | Water | $2265 bit 0x10 | [27,06:29,08] | |
| 0x0007 | Roots | $2265 bit 0x20 | [2c,06:2e,08] | AMOUNT=1 |
| 0x0008 | Clay | $2265 bit 0x40 | [02,1b:04,1d] | |
| 0x0009 | Money | $2265 bit 0x80 | [0b,1a:0d,1c] | AMOUNT=18 talons ($2393=0x12) |
| 0x000a | Clay | $2266 bit 0x01 | [0d,1d:0f,1f] | AMOUNT=2 |
| 0x000b | Water | $2266 bit 0x02 | [14,1a:16,1c] | |
| 0x000c | Roots | $2266 bit 0x08 | [16,19:18,1b] | AMOUNT=1 |
| 0x000d | Water | $2266 bit 0x04 | [1b,19:1d,1b] | AMOUNT=3 |
| 0x000e | Roots | $2266 bit 0x20 | [24,1b:26,1d] | |
| 0x000f | Water | $2266 bit 0x40 | [26,19:28,1b] | AMOUNT=1 |
| 0x0010 | Water | $2267 bit 0x01 | [03,2d:05,2f] | |
| 0x0011 | Biscuit/Call Beads | $2266 bit 0x80 | [05,2c:07,2e] | Content changes: Biscuit if $2260&0x10=0 (Thraxx alive); Call Beads if Thraxx dead |
| 0x0012 | Petal | $2267 bit 0x02 | [13,2f:15,31] | |
| 0x0013 | Clay | $2267 bit 0x04 | [17,2c:19,2e] | AMOUNT=1 |
| 0x0014 | Water | $2267 bit 0x08 | [1a,2c:1c,2e] | AMOUNT=3 |
| 0x0015 | Water | $2267 bit 0x10 | [1c,2d:1e,2f] | |
| 0x0016 | Water | $2267 bit 0x20 | [24,2e:26,30] | |
| 0x0017 | Water | $2267 bit 0x40 | [27,2c:29,2e] | |
| 0x0018 | Water | $2268 bit 0x01 | [2f,2f:31,31] | |

---

## NPCs

| Sprite | Name | Hut | Pos (x,y) | Ref | Talk Script | Condition |
|--------|------|-----|-----------|-----|-------------|-----------|
| 0x07 VILLAGER_1_4 | Man | 1 | (0x0f, 0x0f) | $2455 | 0x1845 "Hut NPC 1" | always |
| 0x08 VILLAGER_1_5 | Old Woman | 2 | (0x33, 0x11) | — | 0x1848 "Hut NPC 2" | always |
| 0x09 VILLAGER_1_6 | Old Man | 3 | (0x4f, 0x13) | $2837 | 0x184b "Hut NPC 3" | always |
| 0x07 VILLAGER_1_4 | Man | 4 | (0x11, 0x3d) | $2455 | 0x184e "Hut NPC 4" | always |
| 0x06 VILLAGER_1_3 | Woman | 5 | (0x31, 0x38) | $2455 | 0x1851 "Hut NPC 5" | always |
| 0x07 VILLAGER_1_4 | Man | 6 | (0x4b, 0x3d) | — | 0x1854 "Hut NPC 6" | always |
| 0x15 FIRE_EYES | Fire Eyes | 7 | (0x0d, 0x5d) / (0x13, 0x65) | $2835 | 0x1857 "Fire Eyes" | if ($2260&0x10 Thraxx dead) AND (!$225f&0x80), or ($22ec&0x20) |
| 0x15 FIRE_EYES | Fire Eyes (post-Thraxx) | 7 | (0x0d, 0x5d) — face EAST or NORTH | $2835 | 0x1857 | if $228b&0x01 (already met); position depends on $22dc&0x08 |
| 0x06 VILLAGER_1_3 | Woman | 8 | (0x2f, 0x61) | — | 0x185a "Hut NPC 7" | always |
| 0x17 BLIMP | Blimp (Harry) | 9 | (0x54, 0x69) | $245b | 0x185d "Blimp (in hut)" | always |

---

## Cutscenes (Enter-Triggered)

### FE Cutscene 1 — "Raptor Aftermath" (hut 3, sub 0x94d363)
**Trigger:** `$22ed & 0x04` AND entering hut 3
**Effects:** NPC $2837 (old man) approaches; heals dog; fade-in from black; old man says *"You took quite a beating out there!"*; prompts to save; heals boy; NPC says *"The raptors got you! Thanks to this wild animal here, you were saved!"*; save menu offered; NPC says *"Feel free to take items from the gourds in this village."*
**Sets:** `$2834 |= 0x01`, `$22e5 |= 0x20` ("Defeated raptors?"), clears `$22ed & 0x04`

### FE First Encounter (hut 7, sub 0x94d849)
**Trigger:** entering hut 7, `$228b & 0x01` is NOT yet set → first visit
**Effects:** Fire Eyes approaches; if `$22e5&0x20` (raptors fought): *"I heard you had quite a fight in the jungle"*; else: *"Who let this wild beast in here?"*; asks for dog's name (**name input for the dog**); gives **Flash alchemy formula** (`$2259 |= 0x80 Flash`; shows alchemy selection screen)
**Sets:** `$228b |= 0x01` (first encounter complete)

### FE Cutscene 2 — "Post-Thraxx / Volcano Cooling" (hut 7, sub 0x94d606)
**Trigger:** entering hut 7, `$2260&0x10` (Thraxx dead) AND `!$225f&0x80` AND `$22dc&0x08` (windwalker unlocked)
**Effects:** Fire Eyes walks over; discusses Wheel ($2264&0x08) and Gauge ($2264&0x04) progress; talks about the cooling volcano and the origin of this world being Fire Eyes' grandfather's dream machine
**Sets:** `$225f |= 0x80` (prevents re-triggering)

### FE Cutscene 3 — "Call Beads" (hut 7, sub 0x94da6d)
**Trigger:** entering hut 7, `$2260&0x10` (Thraxx dead) AND `!$225f&0x80` AND NOT `$22dc&0x08` (windwalker NOT unlocked)
**Effects:** Fire Eyes walks over; discusses Thraxx victory in the Bugmuck; *"I can give you the ability to call on me in difficult situations"*; grants **6 Call Beads** (`$231c += 6`); shows Call Bead usage tutorial; ends by teleporting player to room 0x25 (Fire Eyes' Village) to trigger windwalker arrival cutscene
**Sets:** `$225c |= 0x40` ("FE call beads?"), `$22ec |= 0x20` (windwalker flag), `$234a = 0x0063`

### Blimp in Hut — "Mud Pepper Gift" (hut 9, sub 0x94dceb)
**Trigger:** entering hut 9, `$225e & 0x80` NOT yet set
**Effects:** Blimp shuffles around his hut looking for a gift; comedic searching animation; awards **1 Mud Pepper** (`$2305 += 1`); if `$225f&0x02` set: *"Mud Peppers are the active ingredient in the Levitate Formula"*; else: *"Mud Peppers have special qualities, if you know the right formula"*
**Sets:** `$225e |= 0x80`, `$2834 |= 0x02` during call (then cleared)

---

## External Scripts Called

| Target | Call Type | Section | Purpose |
|--------|-----------|---------|---------|
| Global 0x00 | CALL | enter, Blimp, step-on [29,37:2b,38] | Fade-out / stop music |
| Global 0x01 | CALL | enter, Blimp | Fade-in / start music |
| Global 0x22 | CALL | all step-ons | Prepare room change south indoor-outdoor |
| 0x92de75 | CALL | enter (non-cutscene path) | Cinematic helper |
| 0x94c1c5 | CALL | — | "FE Gathering Pt1?" (referenced from room 0x25; see that doc) |
| 0x01 | CHANGE MAP | step-on [29,37:2b,38] | Exterior of Blimp's Hut (spawn 0xd8, 0x88) |
| 0x25 | CHANGE MAP | step-ons [07,37:09,38]–[07,11:09,12] | Fire Eyes' Village (8 exits, various spawns) |

---

## Notes

- **Multi-room design:** All 9 huts are packed into one room. Scroll bounds ($23e9–$23ef) are written per-hut to restrict camera to the correct quadrant.
- **Gourd layout:** All 25 gourds are placed in the tile area shared across all 9 huts (3×3 grid area of gourd tiles, rows y=06-09, y=19-1f, y=2c-31). Each hut pair in a column shares a set of gourds by proximity.
- **Obj17 (changing gourd):** Contains Biscuit normally; switches to Call Beads after Thraxx is defeated. This is in Fire Eyes' Hut area (hut 7).
- **Dog naming:** Hut 7 FE First Encounter includes a dog name input (`7f SHOW TEXT/NAME INPUT 0x0003`). This is the canonical dog naming scene.
- **$2834 reuse:** Bit 0x01 set in FE Cutscene 1 (raptor aftermath). Bit 0x02 set/cleared during Blimp cutscene. // MISMATCH: same byte used in room 0x5c (bit 0x01 = raptor battle started) — multipurpose story flag.
- **$22e5 bit 0x20 "Defeated raptors?":** Set in FE Cutscene 1 and read in FE First Encounter to select opening line. Also set in room 0x5c via RCALL sub (raptor victory).
- **FE Cutscene 3 auto-exit:** After cutscene ends, player is teleported to Fire Eyes' Village (room 0x25) via `CALL 0x0d17 → 0x94d09d` (step-on exit of hut 3) to trigger the windwalker arrival in that room.
- **Music:** Hut 7 uses music 0x28 (Fire Eyes theme); Blimp's hut (9) uses 0x0c; all others use 0x12 (village). Blimp cutscene temporarily plays music 0x78 (jingle) then returns to 0x0c.
