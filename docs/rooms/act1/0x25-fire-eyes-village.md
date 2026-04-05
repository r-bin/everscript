# Room 0x25 — Prehistoria - Fire Eyes' Village

**ROM address:** 0x9ffe7b
**Data address:** 0xa4b92d
**Enter script:** 0x9280d4 → 0x94cdfb
**Act:** 1 (Prehistoria)
**Analyzed:** 2026-04-03

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on triggers | 13 |
| B-triggers | 20 |
| Gourds | 1 |
| Sniff spots | 19 (16 permanent + 3 respawnable Ash) |
| Enemies | 0 |
| NPCs | 12–17 (varies by flags) |

---

## Memory Access

| Address | core.evs Name | Size | Op | Section | Notes |
|---------|--------------|------|----|---------|-------|
| 0x2443 | DOG_WRITE | 16b | W | enter | Writes 0x02 (Wolf) |
| 0x22eb | IN_ANIMATION | 1b | R/W | enter | Bit 0x20: skip teleport if in animation; cleared after |
| 0x22f1 | — | 1b | R/W | enter | Bit 0x40 "Inside outro?" — gates Fire Eyes departure cutscene; set earlier in enter if debug teleport |
| 0x22f2 | — | 1b | R | enter | Bit 0x01 "In credits" — triggers credits roll if set |
| 0x238f | — | 16b | W | enter | Written 0x0000 in debug teleport branch |
| 0x23bf | PACIFIED | 16b | W | enter | Writes 0x0001 |
| 0x238d | CHANGE_MUSIC | 16b | R | enter | Skips PLAY MUSIC 0x12 if 0x00 |
| 0x22dc | — | 1b | R | enter | Bit 0x08 "windwalker unlocked" — gates windwalker arrival cutscene |
| 0x22ec | — | 1b | R/W | enter, outro sub | Bit 0x20 "unknown intro/outro? flag in prof. lab" — triggers windwalker arrival cutscene; cleared at end of cutscene |
| 0x22ed | — | 1b | R/W | enter, outro sub | Bit 0x40 written in windwalker sub; bit 0x40 → UNLOAD OBJ 17 |
| 0x2288 | — | 1b | R | enter | Bit 0x08 "Talked to defend guy" — switches NPC9/10 talk script |
| 0x228b | — | 1b | R | enter, step-ons | Bit 0x01 "FE visited pre-thraxx (East exit check)" — removes guard NPCs; gates north/east exits |
| 0x2269 | 🫙 | 1b | R/W | B-trigger obj0 | Bit 0x10: Wax gourd (obj 0) looted |
| 0x2293 | — | 1b | R/W | B-triggers | Bits 0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80: objs 4/6/12/11/13/2/5/7 persistence |
| 0x2294 | — | 1b | R/W | B-triggers | Bits 0x01/0x02/0x04/0x08/0x10: objs 8/1/3/9/10 persistence |
| 0x2292 | — | 1b | R/W | enter, B-triggers | Bits 0x20/0x40/0x80: objs 14/15/16 persistence; bit 0x10: respawnable ash objs 18-20 |
| 0x254f | — | 16b | R/W | enter, B-triggers | Written = GameTimer on ash sniff; compared in enter for ash respawn window (GameTimer ≤ $254f + 0x0258) |
| 0x2260 | — | 1b | R | enter, step-on north | Bit 0x10 "Thraxx dead" — checked alongside RAPTORS flag to nudge player, gate north exit |
| 0x225f | RAPTORS | 1b | R | enter, step-on north | Bit 0x80; gates north exit ("We should talk to Fire Eyes first") // TODO: what is bit 0x80 vs 0x40? |
| 0x245f | — | 16b | R/W | enter | Read: != 0x00 skips "let's go talk to Fire Eyes" nudge; Written 0x0001 after nudge fires once |
| 0x234b | FAKE_HOUSE_ID | 16b | W | all hut step-ons | Written before each CHANGE MAP to 0x51 to identify which hut entrance |
| 0x2391 | LOOT_ITEM | 16b | W | all B-triggers | Item type |
| 0x2395 | LOOT_OBJECT | 16b | W | all B-triggers | MAP REF |
| 0x2461 | LOOT_AMOUNT | 16b | W | obj0 gourd only | Written 0x0001 |
| 0x22ea | LOOT_SUCCESSFUL | 1b | R | all B-triggers | Bit 0x01; used to conditionally update persistence flags |
| 0x2409 | SCREEN_SHAKING_X | 16b | W | Fire Eyes outro | Written 0x0001 |
| 0x240b | SCREEN_SHAKING_Y | 16b | W | Fire Eyes outro | Written 0x0001 or 0x0002 |
| 0x242b | — | 16b | W | Fire Eyes outro | Scroll X target; written signed(arg) + 0xd0 |
| 0x242d | — | 16b | W | Fire Eyes outro | Scroll Y target; written signed(arg) + 0x10 |
| 0x23b9 | — | 16b | R/W | Fire Eyes outro | Boy destination X; starts 0x03e8, adjusted |
| 0x23bb | — | 16b | R/W | Fire Eyes outro | Boy destination Y; starts 0x0328, adjusted |
| 0x2834 | — | 1b | W | Fire Eyes outro (sub 0x94cc65) | Sets bit 0x04; related to Fire Eyes departure // TODO: cross-room flag, also used in 0x5c |
| 0x2867 | — | 16b | W | Fire Eyes outro (entity teleport) | Entity X coordinate |
| 0x2869 | — | 16b | W | Fire Eyes outro (entity teleport) | Entity Y coordinate |
| 0x2533 | — | 16b | W | enter (windwalker NPC11 load), credits | Written with last entity ref before companion load |

---

## Objects

| Obj ID | Type | Persistence Flag | Item / Behavior |
|--------|------|-----------------|----------------|
| 0x0000 | gourd 🫙 | $2269 bit 0x10 | Wax; LOOT_AMOUNT=0x0001; tile [3d,11:3e,13] |
| 0x0001 | sniff spot 👃 | $2294 bit 0x02 | Roots; tile [49,29:4a,2a] |
| 0x0002 | sniff spot 👃 | $2293 bit 0x20 | Oil; tile [51,39:54,3a] |
| 0x0003 | sniff spot 👃 | $2294 bit 0x04 | Roots; tile [44,21:46,22] |
| 0x0004 | sniff spot 👃 | $2293 bit 0x01 | Water; tile [4f,13:51,14] |
| 0x0005 | sniff spot 👃 | $2293 bit 0x40 | Oil; tile [4f,0f:50,10] |
| 0x0006 | sniff spot 👃 | $2293 bit 0x02 | Water; tile [43,0c:47,0d] |
| 0x0007 | sniff spot 👃 | $2293 bit 0x80 | Oil; tile [2e,0d:2f,0e] |
| 0x0008 | sniff spot 👃 | $2294 bit 0x01 | Oil; tile [24,16:25,18] |
| 0x0009 | sniff spot 👃 | $2294 bit 0x08 | Roots; tile [29,25:2a,27] |
| 0x000a | sniff spot 👃 | $2294 bit 0x10 | Roots; tile [31,38:34,39] |
| 0x000b | sniff spot 👃 | $2293 bit 0x04 | Water; tile [5e,29:5f,2d] |
| 0x000c | sniff spot 👃 | $2293 bit 0x08 | Water; tile [33,26:36,27] |
| 0x000d | sniff spot 👃 | $2293 bit 0x10 | Water; tile [33,17:35,18]; also triggers SET OBJ 13 STATE=1 on success |
| 0x000e | sniff spot 👃 | $2292 bit 0x20 | Ash; tile [50,29:54,2c] |
| 0x000f | sniff spot 👃 | $2292 bit 0x40 | Ash; tile [4b,1d:4f,20] |
| 0x0010 | sniff spot 👃 | $2292 bit 0x80 | Ash; tile [37,22:3b,25] |
| 0x0011 | — | $22ed bit 0x40 | No B-trigger; enter: UNLOAD if $22ed&0x40; SET STATE=1 during windwalker cutscene // TODO: purpose unknown |
| 0x0012 | sniff spot 👃 (respawnable) | $2292 bit 0x10 | Ash; tile [42,32:43,35]; respawnable: see Notes |
| 0x0013 | sniff spot 👃 (respawnable) | $2292 bit 0x10 | Ash; tile [3f,32:40,35]; respawnable: see Notes |
| 0x0014 | sniff spot 👃 (respawnable) | $2292 bit 0x10 | Ash; tile [40,34:42,35]; respawnable: see Notes |

---

## NPCs

| Sprite | Name | Pos (x,y) | Ref | Talk Script | Condition |
|--------|------|-----------|-----|-------------|-----------|
| 0x08 VILLAGER_1_5 | Old Woman | (0x31, 0x39) | — | 0x1842 "FE Village NPC1" | always |
| 0x05 VILLAGER_1_2 | Boy (Bee Boy) | (0x47, 0x41) | $2853 | 0x1827 "FE Village NPC2/Bee Boy" | always |
| 0x02 BEE | Bee (pet) | (0x47, 0x41) | $2855 | — | always (companion) |
| 0x08 VILLAGER_1_5 | Old Woman | (0x61, 0x61) | $283d | 0x1839 "FE Village NPC3" | always |
| 0x06 VILLAGER_1_3 | Woman | (0x2f, 0x62) | $283f | 0x182a "FE Village NPC4" | always |
| 0x09 VILLAGER_1_6 | Old Man | (0x61, 0x51) | $284f | 0x1824 "FE Village NPC5" | always |
| 0x05 VILLAGER_1_2 | Boy | (0x5d, 0x5a) | $2841 | 0x1836 "FE Village NPC6" | always |
| 0x02 BEE | Bee (pet) | (0x5d, 0x5a) | $2851 | — | always (companion) |
| 0x04 VILLAGER_1_1 | Girl | (0x31, 0x39) | — | 0x1833 "FE Village NPC7" | always |
| 0x03 CHAMELEON | Chameleon (pet) | (0x31, 0x39) | — | — | always (companion) |
| 0x07 VILLAGER_1_4 | Man | (0x3f, 0x3f) | — | 0x182d "FE Village NPC8" | always |
| 0x09 VILLAGER_1_6 | Old Man (gate guard) | (0x17, 0x1f) | — | 0x183f / 0x183c "NPC9 or NPC10" | always (script 0x183f if $2288&0x08; 0x183c if Thraxx alive) |
| 0x04 VILLAGER_1_1 | Girl ("defend person") | (0x39, 0x5b) | $2839 | 0x1830 "FE Village NPC11" | if NOT ($22dc&0x08 OR $22ec&0x20) |
| 0x03 CHAMELEON | Chameleon (pet) | (0x39, 0x5b) | $2837 | — | same as NPC11 (companion) |
| 0x07 VILLAGER_1_4 | Man (quicksand guard) | (0x79, 0x65) | $2843 | — | if NOT $228b&0x01 |
| 0x07 VILLAGER_1_4 | Man (Strongheart proxy?) | (0x41, 0x55) | $283b | 0x1821 "FE Village NPC12" | if NOT $228b&0x01; face SOUTH; script controlled |
| 0x15 FIRE_EYES | Fire Eyes | (0x45, 0x57) | $2835 | — | if $22ec&0x20 set (windwalker flag); otherwise loaded in arrival cutscene |

---

## External Scripts Called

| Target | Call Type | Section | Purpose |
|--------|-----------|---------|---------|
| Global 0x00 | CALL | enter (debug/outro), hut step-ons | Fade-out / stop music |
| Global 0x01 | CALL | enter normal | Fade-in / start music |
| Global 0x27 | CALL | all 8 hut step-ons | Prepare room change north outdoor-indoor |
| Global 0x21 | CALL | step-on south | Prepare room change south outdoor-outdoor |
| Global 0x1d | CALL | step-on east | Prepare room change east outdoor-outdoor |
| Global 0x19 | CALL | step-on west | Prepare room change west outdoor-outdoor |
| Global 0x1f | CALL | Fire Eyes outro | Prepare room change (outro map switch) |
| Global 0x39 | CALL | all sniff spot B-triggers | Loot nature |
| Global 0x3a | CALL | gourd B-trigger | Loot gourd |
| Global 0x5a | CALL | credits | Credits |
| 0x92cc2b | CALL | step-on north, south, east | Unnamed ABS script |
| 0x92de75 | CALL | enter | Cinematic helper |
| 0x92d92a | CALL | Fire Eyes outro | "Outro rain and sky color" |
| 0x92d93e | CALL | Fire Eyes outro | Unnamed ABS (5 args: camera effect) |
| 0x92d95a | CALL | Fire Eyes outro | Unnamed ABS (5 args: timing/camera) |
| 0x929eb9 | CALL | Fire Eyes outro | Unnamed ABS |
| 0x94c1c5 | CALL | step-on [43,2e:44,2f] | "FE Gathering Pt1?" — village gathering cutscene |
| 0x94c99a/c9b8/c9e0/c9fe | CALL | windwalker arrival | 4 unnamed sub-scripts (animation helpers) |
| 0x51 | CHANGE MAP | 8× hut step-ons | Village Huts and Blimp's Hut (various spawns) |
| 0x36 | CHANGE MAP | Fire Eyes outro | Both fire pits (spawn 0xe8, 0x148) |
| 0x41 | CHANGE MAP | step-on north [4b,0a:50,0c] | North jungle (spawn 0x38, 0x268) |
| 0x38 | CHANGE MAP | step-on south [4b,3c:50,3e] | South jungle / Start (spawn 0x310, 0x58) |
| 0x5b | CHANGE MAP | step-on east [5e,34:60,39] | East jungle (spawn 0x8, 0x1b8) |
| 0x26 | CHANGE MAP | step-on west [21,1b:24,1c] | West area with Defend (spawn 0x130, 0x98) |

---

## Notes

- **Hut entrances:** 8 step-on triggers enter 0x51 (Village Huts and Blimp's Hut). Each writes a unique FAKE_HOUSE_ID (1–8) to indicate which hut is entered. Hut 7 has a special case: if `!$228b&0x01` (pre-Thraxx), it calls `0x94c1c5 "FE Gathering Pt1?"` instead of entering — this triggers the village gathering cutscene.
- **East exit guard:** Step-on [5b,35:5c,38] is a blocked zone. Guard NPC ($2843) faces west; if $228b&0x01 is not set, player is pushed back with dialogue: *"No humans or dogs are allowed in the quicksand field without permission from Fire Eyes."* (dog) or *"You should talk to Fire Eyes before you walk into the dangerous quicksand field."* (boy). Once $228b bit 0x01 is set, the step-on becomes pass-through.
- **North exit nudge:** Step-on [4b,0a:50,0c] — if ($2260&0x10 Thraxx dead) AND (!$225f&0x80), the player is stopped and boy says: *"We should talk to Fire Eyes before we move on."* Only fires once per-session ($245f guards it). Otherwise exits north to room 0x41.
- **Fire Eyes outro cutscene:** Gated by `$22f1 bit 0x40`. This is the full farewell scene with earthquake effects, multiple NPCs exchanging dialogue (Fire Eyes, Strongheart, Boy), then CHANGE MAP → 0x36. `$2834 |= 0x04` is set near the end. Uses sub-scripts for camera and timing.
- **Windwalker arrival cutscene:** Gated by `($22ec&0x20) AND NOT ($22dc&0x08)`. Plays SOUND 0x34 + PLAY MUSIC 0x52, loads two SPARK explosions ($2857/$2859), reloads Fire Eyes entity ($2835) at (45,57), plays animation, then player regains control. After this, Fire Eyes says: *"Call me if you need my help."* (script 0x1827 text 0x07d1). $22dc bit 0x08 is set (windwalker unlocked) on completion.
- **Respawnable ash spots (objs 18-20):** All share `$2292 bit 0x10`. When player sniffs them, `$254f` is set to current GameTimer. On re-enter, if GameTimer ≤ $254f + 0x0258 (600 ticks ≈ 10s), they respawn; otherwise `$2292 bit 0x10` is cleared (permanent collect). This is a limited-time respawn window.
- **Credits sequence:** If `$22f2 bit 0x01` is set, a full credits roll fires: Strongheart walks around, all village NPCs march in pairs (VILLAGER_2_1–VILLAGER_2_8 pairs), ends with Global 0x5a "Credits".
- **$2834 bit 0x04:** Set during Fire Eyes outro. This is the same byte used in room 0x5c (bit 0x01 = raptors battle started). // MISMATCH: $2834 used for unrelated flags in different rooms — may be room-specific scratch or multipurpose story flag.
- **$2292 note:** Also used in room 0x38 for sniff spot persistence ($228f–$2292 range). Bit 0x10 in $2292 overlaps with 0x38's "Sniffed Ash #20" but the context here is specifically the Fire Eyes' Village ash cluster.
- **Music:** PLAY MUSIC 0x12 on normal entry. Music 0x8e plays during the Fire Eyes outro (rain scene). Windwalker arrival uses MUSIC 0x52 briefly then returns to 0x12.
