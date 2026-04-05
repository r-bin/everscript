# Room 0x38 — Prehistoria - South Jungle / Start

**ROM address:** 0x9ffec7
**Data address:** 0x9e8000
**Enter script:** 0x928133 → 0x9384d9
**Act:** 1 (Prehistoria)
**Analyzed:** 2026-04-03

---

## Memory Access

| Address | core.evs Name | Size | Op | Trigger / Object | Notes |
|---------|--------------|------|----|-----------------|-------|
| 0x2443 | DOG_WRITE | 16b | W | enter script | Writes 0x02 (Wolf form) |
| 0x22f1 | — | 8b | R | enter script | Bit 0x40; branches to outro handler if set |
| 0x22eb | IN_ANIMATION | 1b | R | enter script | Bit 0x20; skips entry teleport if already in animation |
| 0x22eb | IN_ANIMATION | 1b | W | enter script (outro branch) | Clears bit 0x20 |
| 0x23e9 | CAMERA_BOUNDRY_X_START | 16b | W | enter script | Camera boundary X start |
| 0x23eb | CAMERA_BOUNDRY_Y_START | 16b | W | enter script | Camera boundary Y start |
| 0x23ed | CAMERA_BOUNDRY_X_END | 16b | W | enter script | Camera boundary X end |
| 0x23ef | CAMERA_BOUNDRY_Y_END | 16b | W | enter script | Camera boundary Y end |
| 0x238d | CHANGE_MUSIC | 16b | R | enter script | Skips music play opcode if 0x00 |
| 0x23bf | PACIFIED | 16b | W | enter script | Writes 0x0001 |
| 0x0b83 | — | 16b | W | enter script | Writes 0x8000 // ? screen fade control |
| 0x238f | TRANSITION_ENTER_DIRECTION | 16b | W | enter script | Writes 0x0000 |
| 0x0ea2 | — | 16b | W | enter script | // ? |
| 0x0eac | — | 16b | W | enter script | // ? |
| 0x239b | PRIZE_RATE_1 | 16b | W | enter script | Enemy drop rate config |
| 0x239d | PRIZE_RATE_2 | 16b | W | enter script | Enemy drop rate config |
| 0x239f | PRIZE_RATE_3 | 16b | W | enter script | Enemy drop rate config |
| 0x23a1 | PRIZE_DROP_1 | 16b | W | enter script | Enemy drop item config |
| 0x23a3 | — | 16b | W | enter script | Enemy drop item config // ? likely PRIZE_DROP_2 |
| 0x23a5 | PRIZE_DROP_3 | 16b | W | enter script | Enemy drop item config |
| 0x23ab | PRIZE_QUANTITY_3 | 16b | W | enter script | Enemy drop quantity config |
| 0x2433 | ENEMY_SPAWNER_QUANTITY | 16b | W | enter script | Sets enemy spawner count |
| 0x234a | — | 16b | W | enter script | Writes 0x63 // ? |
| 0x2441 | GAIN_WEAPON | 16b | W | enter script | Writes 0x02 (Bone Crusher // ?) |
| 0x22ab | FLOWERS_CUTSCENE_WATCHED | 1b | RW | enter script | Bit 0x40; guards intro cutscene; set after cutscene completes |
| 0x22eb | INTRO_DEMO_MODE | 1b | R | enter script | Bit 0x04; suppresses intro cutscene in demo/attract mode |
| 0x242b | CAMERA_PAN_X | 16b | W | enter script | Camera pan target X |
| 0x242d | CAMERA_PAN_Y | 16b | W | enter script | Camera pan target Y |
| 0x242f | CAMERA_PAN_SPEED | 16b | W | enter script | Camera pan speed (default 0x80) |
| 0x2268 | — | 8b | R | enter script | Persistence flags; bit 0x40 = obj 0, bit 0x80 = obj 1 |
| 0x2269 | — | 8b | R | enter script | Persistence flags; 0x01=obj2, 0x02=obj3, 0x04=obj4, 0x08=obj5 |
| 0x228f | — | 8b | R | enter script | Persistence flags; 0x08=obj14, 0x10=obj28, 0x20=obj9, 0x40=obj30, 0x80=obj10 |
| 0x2290 | — | 8b | R | enter script | Persistence flags; 0x01=obj12, 0x02=obj13, 0x04=obj16, 0x08=obj19, 0x10=obj26, 0x20=obj6, 0x40=obj7, 0x80=obj23 |
| 0x2291 | — | 8b | R | enter script | Persistence flags; 0x01=obj24, 0x02=obj27, 0x04=obj8, 0x08=obj11, 0x10=obj29, 0x20=obj15, 0x40=obj17, 0x80=obj18 |
| 0x2292 | — | 8b | R | enter script | Persistence flags; 0x01=obj20, 0x02=obj21, 0x04=obj22, 0x08=obj25 |
| 0x225f | RAPTORS | 1b | R | step-on [40,10:44,12] | Bit 0x40; north exit → 0x25 (Village) if set, 0x5c (Raptors) if clear |
| 0x22ea | LOOT_SUCCESSFUL | 1b | R | all B-triggers | Bit 0x01; updates persistence flag only if loot was accepted |
| 0x2391 | LOOT_ITEM | 16b | W | all B-triggers | Written with item type ID before calling loot global |
| 0x2395 | LOOT_OBJECT | 16b | W | all B-triggers | Written with MAP REF (obj ID) before calling loot global |
| 0x2461 | LOOT_AMOUNT | 16b | W | sniff #9 and sniff #14 B-triggers | Writes 0x0001; grants bonus extra loot // ? |

---

## Objects

| Obj ID | Type | Persistence Flag | Notes |
|--------|------|-----------------|-------|
| 0x0000 | gourd 🫙 | $2268 bit 0x40 | Contains Petal |
| 0x0001 | gourd 🫙 | $2268 bit 0x80 | Contains Oil; labeled "Gourd in south Jungle" in dump |
| 0x0002 | gourd 🫙 | $2269 bit 0x01 | Contains Petal |
| 0x0003 | gourd 🫙 | $2269 bit 0x02 | Contains Shell Hat |
| 0x0004 | gourd 🫙 | $2269 bit 0x04 | Contains Nectar |
| 0x0005 | gourd 🫙 | $2269 bit 0x08 | Contains Money |
| 0x0006 | ? | $2290 bit 0x20 | Persistence flag present; no B-trigger found in dump // TODO: verify type and contents in map data |
| 0x0007 | sniff spot 👃 | $2290 bit 0x40 | Yields Ash |
| 0x0008 | sniff spot 👃 | $2291 bit 0x04 | Yields Water |
| 0x0009 | sniff spot 👃 | $228f bit 0x20 | Yields Roots; LOOT_AMOUNT=1 written (extra item) |
| 0x000a | sniff spot 👃 | $228f bit 0x80 | Yields Roots |
| 0x000b | sniff spot 👃 | $2291 bit 0x08 | Yields Water |
| 0x000c | sniff spot 👃 | $2290 bit 0x01 | Yields Roots |
| 0x000d | sniff spot 👃 | $2290 bit 0x02 | Yields Roots |
| 0x000e | sniff spot 👃 | $228f bit 0x08 | Yields Clay; LOOT_AMOUNT=1 written (extra item) |
| 0x000f | sniff spot 👃 | $2291 bit 0x20 | Yields Water |
| 0x0010 | sniff spot 👃 | $2290 bit 0x04 | Yields Roots |
| 0x0011 | sniff spot 👃 | $2291 bit 0x40 | Yields Water |
| 0x0012 | sniff spot 👃 | $2291 bit 0x80 | Yields Water |
| 0x0013 | sniff spot 👃 | $2290 bit 0x08 | Yields Roots |
| 0x0014 | sniff spot 👃 | $2292 bit 0x01 | Yields Water |
| 0x0015 | sniff spot 👃 | $2292 bit 0x02 | Yields Water |
| 0x0016 | sniff spot 👃 | $2292 bit 0x04 | Yields Water |
| 0x0017 | sniff spot 👃 | $2290 bit 0x80 | Yields Ash |
| 0x0018 | sniff spot 👃 | $2291 bit 0x01 | Yields Ash |
| 0x0019 | sniff spot 👃 | $2292 bit 0x08 | Yields Water |
| 0x001a | sniff spot 👃 | $2290 bit 0x10 | Yields Roots |
| 0x001b | sniff spot 👃 | $2291 bit 0x02 | Yields Ash |
| 0x001c | sniff spot 👃 | $228f bit 0x10 | Yields Clay |
| 0x001d | sniff spot 👃 | $2291 bit 0x10 | Yields Water |
| 0x001e | sniff spot 👃 | $228f bit 0x40 | Yields Roots |

---

## External Scripts Called

| Target | Call Type | Called From | Purpose |
|--------|-----------|-------------|---------|
| Global 0x00 | CALL | enter script; step-on scripts | Fade-out / stop music |
| Global 0x01 | CALL | enter script | Fade-in / start music |
| Global 0x09 | CALL | enter script | // ? unnamed |
| Global 0x0a | CALL | enter script | // ? open message box |
| Global 0x0b | CALL | enter script | // ? close message box |
| Global 0x19 | CALL | step-on [13,18:14,1c] (west exit) | // ? prepare room change west→east outdoor-outdoor |
| Global 0x26 | CALL | step-on [40,10:44,12] (north exit) | // ? prepare room change north→south outdoor-indoor |
| Global 0x39 | CALL | all sniff-spot B-triggers | Loot nature? |
| Global 0x3a | CALL | all gourd B-triggers | Loot gourd? |
| Global 0x59 | CALL | enter script (outro handler, $22f1&0x40 branch) | Attraction mode / ending cutscene sequence // ? |
| 0x92a3ed | CALL | enter script | // ? show status bar layer |
| 0x92c9c5 | CALL | enter script | // ? unnamed ABS script |
| 0x92de75 | CALL | enter script (multiple call sites) | // ? cinematic helper; used across multiple rooms |
| 0x25 | CHANGE MAP | step-on [40,10:44,12] north (if RAPTORS set) | Prehistoria - Fire Eyes' Village |
| 0x33 | CHANGE MAP | step-on [13,18:14,1c] west exit | Prehistoria - Strong Heart's Exterior |
| 0x5c | CHANGE MAP | step-on [40,10:44,12] north (if RAPTORS clear) | Prehistoria - Raptors |

---

## NPCs

| Sprite | Count | Notes |
|--------|-------|-------|
| 0x0b | 14 | Loaded unconditionally via opcode `ba` (LOAD NPC); exact positions not recorded |
| 0x1e | 7 | Loaded via opcode `3c` (Load NPC with flags/state); exact positions not recorded |

---

## Notes

- **Intro cutscene:** The enter script contains the full planetfall intro cutscene. It triggers on first visit when `FLOWERS_CUTSCENE_WATCHED` ($22ab, bit 0x40) is clear and `INTRO_DEMO_MODE` ($22eb, bit 0x04) is not set. The cutscene sets `FLOWERS_CUTSCENE_WATCHED` on completion.
- **Outro handler:** If $22f1 & 0x40 is set on room entry, the enter script branches to an ending-sequence handler (calls Global 0x59). $22f1 has no name in core.evs. // TODO: name this flag
- **North exit is conditional:** Step-on tile [40,10:44,12] leads to room 0x5c (Raptors) or 0x25 (Fire Eyes' Village) depending on `RAPTORS` ($225f bit 0x40).
- **OBJ 0x0006 unresolved:** UNLOAD OBJ 6 is guarded by $2290 bit 0x20 in the enter script, but no B-trigger for OBJ 6 was found. Its type and contents are unknown. // TODO: verify OBJ 6 in map data
- **Sniff spots 0x0009 and 0x000e:** Both write LOOT_AMOUNT ($2461) = 0x0001 before calling the nature loot global, unlike all other sniff spots. This likely means the dog sniffs up an extra item. // TODO: confirm what the bonus item is
- **Music ID not captured:** The music played on normal entry was not recorded during analysis. // TODO: re-read enter script for PLAY MUSIC opcode value
- **$0ea2 / $0eac:** Purpose of these writes is unknown. // TODO: research
- **$234a = 0x63:** Purpose unknown. 0x63 = 99 decimal; could be a timer or counter. // TODO: research
- **GAIN_WEAPON 0x02:** Labeled "Bone Crusher" in the dump disassembly. If correct, this is the dog's starting weapon awarded during intro. // TODO: verify value mapping from game data
- **NPC sprite positions not captured:** Exact coordinates for NPC 0x0b (×14) and NPC 0x1e (×7) were not recorded. // TODO: re-read enter script to capture load positions
