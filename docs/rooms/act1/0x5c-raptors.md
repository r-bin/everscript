# Room 0x5c — Prehistoria - Raptors

**ROM address:** 0x9fff57
**Data address:** 0xa8f590
**Enter script:** 0x9281e7 → 0x93912c
**Act:** 1 (Prehistoria)
**Analyzed:** 2026-04-03

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on triggers | 3 |
| B-triggers | 4 |
| Gourds | 0 |
| Sniff spots | 4 |
| Enemies | 5 |
| NPCs | 0 |

---

## Memory Access

| Address | core.evs Name | Size | Op | Section | Notes |
|---------|--------------|------|----|---------|-------|
| 0x2443 | DOG_WRITE | 16b | W | enter | Writes 0x02 (Wolf) |
| 0x22eb | IN_ANIMATION | 1b | R | enter | Bit 0x20; skips teleport if set |
| 0x22eb | IN_ANIMATION | 1b | W | enter (animation branch) | Clears bit 0x20 |
| 0x22b4 | — | 1b | R | enter | Unloads looted sniff spots: 0x02→Water(obj6); 0x04→Oil(obj8); 0x08→Crystal(obj7); 0x10→Crystal(obj9) |
| 0x238d | CHANGE_MUSIC | 16b | R | enter | Skips music if 0x00 |
| 0x23bf | PACIFIED | 16b | W | enter | Writes 0x0000 |
| 0x242f | CAMERA_PAN_SPEED | 16b | W | enter (sub-routine) | Writes 0x80>>1 = 0x40 // ? |
| 0x2493 | — | 16b | W | enter (sub-routine) | Camera/animation position X; used in entry cutscene |
| 0x2495 | — | 16b | W | enter (sub-routine) | Camera/animation position Y; used in entry cutscene |
| 0x225d | — | 1b | W | enter | Sets bit 0x04; labeled "Desert spin???" in dump |
| 0x225f | RAPTORS | 1b | W | step-on [15,15:18,17] | Sets bit 0x40 (RAPTORS fought) on north exit to village |
| 0x238d | CHANGE_MUSIC | 16b | W | step-on [14,24:1c,25] | Written 0x0000 after music 0x32 set; resets flag |
| 0x2834 | — | 16b | RW | step-on [14,24:1c,25] | Bit 0x01: battle started; bit 0x20: final music speed set |
| 0x2849 | — | 16b | W | step-on [14,24:1c,25] | Written 0x0004 at battle start; tracks raptor count |
| 0x2853 | — | 16b | W | step-on [14,24:1c,25] | Written with entity ref of last-standing raptor |
| 0x2315 | PETAL | 8b | W | step-on [14,24:1c,25] | Incremented by 1 on battle completion (Petal reward) |
| 0x23d3 | — | 16b | W | step-on [14,24:1c,25] | Written 0x0001 before item text, 0x0000 after |
| 0x22ed | — | 1b | R | step-on [14,24:1c,25] | Bit 0x04 = BOY_RAPTORS_SCREEN; tested to gate victory cutscene |
| 0x2391 | LOOT_ITEM | 16b | W | all B-triggers | Item type before calling nature loot global |
| 0x2395 | LOOT_OBJECT | 16b | W | all B-triggers | MAP REF before calling nature loot global |
| 0x2461 | LOOT_AMOUNT | 16b | W | all B-triggers | Written 0x0001 or 0x0002 (extra item quantity) |
| 0x22ea | LOOT_SUCCESSFUL | 1b | R | all B-triggers | Bit 0x01; updates $22b4 flag only on success |
| 0x22b4 | 👃 Water | 1b | R/W | B-trigger obj6 | Bit 0x02: Water sniff looted (LOOT_AMOUNT=0x0002) |
| 0x22b4 | 👃 Crystal | 1b | R/W | B-trigger obj7 | Bit 0x08: Crystal sniff looted (LOOT_AMOUNT=0x0002) |
| 0x22b4 | 👃 Oil | 1b | R/W | B-trigger obj8 | Bit 0x04: Oil sniff looted (LOOT_AMOUNT=0x0001) |
| 0x22b4 | 👃 Crystal | 1b | R/W | B-trigger obj9 | Bit 0x10: Crystal sniff looted (LOOT_AMOUNT=0x0001) |

---

## Objects

| Obj ID | Type | Persistence Flag | Item / Behavior |
|--------|------|-----------------|----------------|
| 0x0006 | sniff spot 👃 | $22b4 bit 0x02 | Water; LOOT_AMOUNT=0x0002 |
| 0x0007 | sniff spot 👃 | $22b4 bit 0x08 | Crystal; LOOT_AMOUNT=0x0002 |
| 0x0008 | sniff spot 👃 | $22b4 bit 0x04 | Oil; LOOT_AMOUNT=0x0001 |
| 0x0009 | sniff spot 👃 | $22b4 bit 0x10 | Crystal; LOOT_AMOUNT=0x0001 |

---

## Enemies

| Sprite ID | Name | Position (x,y) | Count | Notes |
|-----------|------|----------------|-------|-------|
| 0x0d (slot 0x1a>>1) | RAPTOR_PURPLE "Raptor" | (0x01, 0x01) ×4; (0x01, 0x01) ×1 | 5 | Kill script 0x17af "Raptors kill"; entity refs $2835/$2837/$2839/$283b/$283d; raptor 4 ($283b) has extra WRITE offset+0x2a=0x50; raptor 5 ($283d) loaded with flags/state 0x22 |
| 0x20 (slot 0x40>>1) | PLACEHOLDER | (0x13,0x19) (0x29,0x1b) (0x13,0x29) (0x29,0x2b) (0x16,0x06) | 5 | Visual/animation entities; entity refs $2855/$2857/$2859/$285b/$285d; $285d used in entry pan animation |

---

## External Scripts Called

| Target | Call Type | Section | Purpose |
|--------|-----------|---------|---------|
| Global 0x00 | CALL | enter (non-animation branch), step-on north/south | Fade-out / stop music |
| Global 0x26 | CALL | step-on [15,15:18,17] | Prepare room change north outdoor-indoor // ? |
| Global 0x21 | CALL | step-on [16,2d:19,2f] | Prepare room change south outdoor-outdoor // ? |
| Global 0x39 | CALL | all B-triggers | Loot nature |
| Global 0x0a | CALL | step-on [14,24:1c,25] | Open message box // ? |
| 0x92cc2b | CALL | step-on [16,2d:19,2f] | Unnamed ABS script |
| 0x92de75 | CALL | enter | Cinematic helper (shared across rooms) |
| 0x93887d | CALL | step-on [14,24:1c,25] (battle loop) | "Progress Raptors" — tracks kill count per loop tick |
| 0x92bf33 | CALL | step-on [14,24:1c,25] (victory) | "Hold up weapon" victory animation |
| 0x25 | CHANGE MAP | step-on [15,15:18,17] | Prehistoria - Fire Eyes' Village (spawn 0x2c8, 0x398) |
| 0x38 | CHANGE MAP | step-on [16,2d:19,2f] | Prehistoria - South Jungle / Start (spawn 0x310, 0x58) |

---

## Notes

- **Battle trigger:** Step-on [14,24:1c,25] starts the raptor gauntlet. Guarded by $2834 bit 0x01 — only fires once. Monitors each raptor's death in a loop; calls 0x93887d "Progress Raptors" each tick until one raptor signals "will die" or $22ed bit 0x04 is set.
- **Victory reward:** "Received 50 Talons" + "Received a Petal" (PETAL++ at $2315). Plays music 0x36, then 0x32, then 0x0a.
- **Battle dialogue:** Boy says: `"I have a strange feeling about this."` (text 0x057f, WINDOWED). This fires at battle start.
- **South exit guard:** Step-on [16,2d:19,2f] is blocked if $2834 bit 0x01 is clear (battle not yet triggered). 0x92cc2b is called before the map change on this exit.
- **$22b4 bits 0x02/0x04/0x08/0x10** control sniff spot persistence. Bits 0x01 and 0x80 are currently unknown.
- **$2834** has no name in core.evs. Bit 0x01 = battle triggered; bit 0x20 = final music speed already set.
- **$225d bit 0x04:** Set after loading enemies, labeled "Desert spin???" in dump. // TODO: purpose unknown
- **Entry cutscene:** On arrival, audio fades up from 0 to 0x80 over time, then PLACEHOLDER entity $285d is animated into position via a sub-routine at 0x93909d (camera tracks to a landing spot at 0xe0, 0xf8).
- **Kill tracking:** $2849 is written 0x0004 at battle start (4 raptors to kill). $2853 is written with the ref of the last raptor that will die.
- **Boy kill script:** Boy's kill script set to 0x17b2 = BOY_RAPTORS_SCREEN during battle — fires if boy dies.
- **Music:** PLAY MUSIC 0x0a on entry (conditional on CHANGE_MUSIC). Volume fades in progressively after entry animation.
