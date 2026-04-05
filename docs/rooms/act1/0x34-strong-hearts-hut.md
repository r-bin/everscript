# Room 0x34 — Prehistoria - Strong Heart's Hut

**ROM address:** 0x9ffeb7
**Data address:** 0xadbd79
**Enter script:** 0x92811f → 0x94e795
**Act:** 1 (Prehistoria)
**Analyzed:** 2026-04-03

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on triggers | 1 |
| B-triggers | 3 |
| Gourds | 3 |
| Sniff spots | 0 |
| Enemies | 0 |
| NPCs | 1 |

---

## Memory Access

| Address | core.evs Name | Size | Op | Section | Notes |
|---------|--------------|------|----|---------|-------|
| 0x2443 | DOG_WRITE | 16b | W | enter | Writes 0x02 (Wolf) |
| 0x22eb | IN_ANIMATION | 1b | R | enter | Bit 0x20; skips teleport if set |
| 0x22eb | IN_ANIMATION | 1b | W | enter (animation branch) | Clears bit 0x20 |
| 0x22ee | — | 1b | W | enter | Clears bit 0x01; labeled "unknown intro/outro? flag in prof. lab" in dump |
| 0x2273 | — | 1b | R | enter | Bit 0x01 → UNLOAD OBJ 0; bit 0x02 → UNLOAD OBJ 1; bit 0x04 → UNLOAD OBJ 2 |
| 0x2455 | VENDOR_ENTITY | 16b | W | enter | Written with last-loaded entity ref; used as talk-script target for Strongheart NPC |
| 0x238d | CHANGE_MUSIC | 16b | R | enter | Skips music if 0x00 |
| 0x23bf | PACIFIED | 16b | W | enter | Writes 0x0001 |
| 0x2391 | LOOT_ITEM | 16b | W | obj0, obj1, obj2 B-triggers | Item type before calling gourd loot global |
| 0x2395 | LOOT_OBJECT | 16b | W | obj0, obj1, obj2 B-triggers | MAP REF before calling gourd loot global |
| 0x22ea | LOOT_SUCCESSFUL | 1b | R | obj0, obj1, obj2 B-triggers | Bit 0x01; updates $2273 flag only on success |
| 0x2273 | 🫙 Oil | 1b | R/W | B-trigger obj0 | Bit 0x01: Oil gourd (obj 0) looted |
| 0x2273 | 🫙 Wax | 1b | R/W | B-trigger obj1 | Bit 0x02: Wax gourd (obj 1) looted |
| 0x2273 | 🫙 Wax | 1b | R/W | B-trigger obj2 | Bit 0x04: Wax gourd (obj 2) looted |

---

## Objects

| Obj ID | Type | Persistence Flag | Item / Behavior |
|--------|------|-----------------|----------------|
| 0x0000 | gourd 🫙 | $2273 bit 0x01 | Oil |
| 0x0001 | gourd 🫙 | $2273 bit 0x02 | Wax |
| 0x0002 | gourd 🫙 | $2273 bit 0x04 | Wax |

---

## NPCs

| Sprite ID | Name | Position (x,y) | Dialogue / Behavior |
|-----------|------|----------------|-------------------|
| 0x7e | VILLAGER_1_8 (Strongheart) | (0x13, 0x11) | Talk script 0x1863; labeled "Strong Heart (inside Hut)" in dump |

---

## External Scripts Called

| Target | Call Type | Section | Purpose |
|--------|-----------|---------|---------|
| Global 0x00 | CALL | step-on | Fade-out / stop music |
| Global 0x01 | CALL | enter | Fade-in / start music |
| Global 0x22 | CALL | step-on [0b,17:0d,18] | Prepare room change south indoor-outdoor // ? |
| Global 0x3a | CALL | obj0, obj1, obj2 B-triggers | Loot gourd |
| 0x92de75 | CALL | enter | Cinematic helper (shared across rooms) |
| 0x33 | CHANGE MAP | step-on [0b,17:0d,18] | Prehistoria - Strong Heart's Exterior (spawn 0x98, 0xa8) |

---

## Notes

- Music 0x26 plays on entry (conditional on CHANGE_MUSIC).
- Enter script sets audio volume to 0xff before fade-out on exit (step-on sets it to 0xff first).
- $22ee bit 0x01 is cleared on entry; the same bit is also manipulated in the Professor's lab — purpose unclear. // TODO: name this flag
- Gourd obj1 and obj2 both contain Wax.
- $2273 bits 0x08/0x10/0x20/0x40/0x80 are currently unknown.
