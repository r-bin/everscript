# Room 0x33 — Prehistoria - Strong Heart's Exterior

**ROM address:** 0x9ffeb3
**Data address:** 0xadb50c
**Enter script:** 0x92811a → 0x94e5fb
**Act:** 1 (Prehistoria)
**Analyzed:** 2026-04-03

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | 0 |
| NPCs | 0 |

---

## Memory Access

| Address | core.evs Name | Size | Op | Section | Notes |
|---------|--------------|------|----|---------|-------|
| 0x2443 | DOG_WRITE | 16b | W | enter | Writes 0x02 (Wolf) |
| 0x22eb | IN_ANIMATION | 1b | R | enter | Bit 0x20; skips teleport if set |
| 0x22eb | IN_ANIMATION | 1b | W | enter (animation branch) | Clears bit 0x20 |
| 0x23e9 | CAMERA_BOUNDRY_X_START | 16b | W | enter | 0x0000 |
| 0x23eb | CAMERA_BOUNDRY_Y_START | 16b | W | enter | 0x0000 |
| 0x23ed | CAMERA_BOUNDRY_X_END | 16b | W | enter | 0x0140 |
| 0x23ef | CAMERA_BOUNDRY_Y_END | 16b | W | enter | 0x0100 |
| 0x238d | CHANGE_MUSIC | 16b | R | enter | Skips music if 0x00 |
| 0x23bf | PACIFIED | 16b | W | enter | Writes 0x0001 |

---

## External Scripts Called

| Target | Call Type | Section | Purpose |
|--------|-----------|---------|---------|
| Global 0x00 | CALL | enter (non-animation branch), step-on | Fade-out / stop music |
| Global 0x01 | CALL | enter | Fade-in / start music |
| Global 0x27 | CALL | step-on [27,0f:28,10] | Prepare room change north indoor-outdoor // ? |
| Global 0x1d | CALL | step-on [2f,0c:32,0e] | Prepare room change east outdoor-outdoor // ? |
| 0x92de75 | CALL | enter | Cinematic helper (shared across rooms) |
| 0x34 | CHANGE MAP | step-on [27,0f:28,10] | Prehistoria - Strong Heart's Hut (spawn 0x90, 0x118) |
| 0x38 | CHANGE MAP | step-on [2f,0c:32,0e] | Prehistoria - South Jungle / Start (spawn 0x20, 0xf8) |

---

## Notes

- Pure transition room: no objects, no NPCs, no enemies.
- Music 0x12 plays on entry (conditional on CHANGE_MUSIC).
- North exit enters Strong Heart's Hut; east exit returns to South Jungle.
