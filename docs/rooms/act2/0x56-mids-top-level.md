# 0x56 — Antiqua: 'mids Top Level (Boy start)

| Field | Value |
|-------|-------|
| Room ID | 0x56 |
| Act | Antiqua (Act 2) |
| Data | `0xa6c154` |
| Enter script ptr | `0x9281c9` |
| Enter script addr | `0x959a08` |
| Step-ons | 6 |
| B-triggers | 24 |
| Music | 0x20 |
| Dog sprite | Greyhound (0x06) |

---

## Overview

The upper level of the Mammoth Mausoleum ('mids). The boy begins here. The room
shares the boy/dog split mechanic with 0x55 (bottom) and 0x06 (exterior): each
character's current destination is tracked in `$2357` (boy) and `$2358` (dog);
value `2` = top level (this room). Two floor switch / pressure plate objects (OBJs 0–1) gate
platforming elements. Twenty-three gourds fill the room.

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$22e2` | 0x10 | 🔧 Gear puzzle A activated [0x56] — set by step-on [2f,1c:31,1e]; OBJ 0 → state 4+1 |
| `$22e2` | 0x20 | 🔧 Gear puzzle B activated [0x56] — set by B-trigger #24 (boy, weapon #12); OBJ 1 → state 4 |
| `$22e3` | 0x40 | 📖 Dog freed from 'mids [0x55] — if set on enter, both chars routed to top level |
| `$22e4` | 0x04 | 📖 Boy blocked from descending [0x06/0x55/0x56] — if set on descent, dog marked unavail |
| `$22e5` | 0x02 | 📖 'mids split flag A [0x56] — cleared when boy re-enters from split; triggers CALL 0x92a404 |
| `$22e5` | 0x04 | 📖 'mids split flag B [0x56] — cleared when dog re-enters from split; triggers CALL 0x92a422 |
| `$2261` | 0x01 | ⚙️ Dog unavailable [multi-room] — set when dog destination ≠ 2 on this room's enter |
| `$2261` | 0x02 | ⚙️ Boy unavailable [multi-room] — set when boy destination ≠ 2 on this room's enter |
| `$2350` | — | ⚙️ Cleared to 0 on enter (1-byte WRAM) |
| `$2357` | — | 📖 Boy's 'mids destination (0=outside, 1=bottom, 2=top) [0x06/0x55/0x56] |
| `$2358` | — | 📖 Dog's 'mids destination (0=outside, 1=bottom, 2=top) [0x06/0x55/0x56] |
| `$2537` | — | ⚙️ Copy of `($2357)&0xff` written on enter |
| `$227e` | 0x80 | 🫙 Gourd OBJ 2: Petal [0x56] (MAP REF 0x02) |
| `$227f` | 0x01 | 🫙 Gourd OBJ 3: Water×3 [0x56] (MAP REF 0x03) |
| `$227f` | 0x02 | 🫙 Gourd OBJ 4: Herbal Essence [0x56] (MAP REF 0x04) |
| `$227f` | 0x04 | 🫙 Gourd OBJ 5: Limestone×2 [0x56] (MAP REF 0x05) |
| `$227f` | 0x08 | 🫙 Gourd OBJ 6: Nectar [0x56] (MAP REF 0x06) |
| `$227f` | 0x10 | 🫙 Gourd OBJ 7: Dry Ice×2 [0x56] (MAP REF 0x07) |
| `$227f` | 0x20 | 🫙 Gourd OBJ 8: Ethanol×3 [0x56] (MAP REF 0x08) |
| `$227f` | 0x40 | 🫙 Gourd OBJ 9: Wings [0x56] (MAP REF 0x09) |
| `$227f` | 0x80 | 🫙 Gourd OBJ 10: Grease [0x56] (MAP REF 0x0a) |
| `$2280` | 0x01 | 🫙 Gourd OBJ 11: Gunpowder×2 [0x56] (MAP REF 0x0b) |
| `$2280` | 0x02 | 🫙 Gourd OBJ 12: Clay×3 [0x56] (MAP REF 0x0c) |
| `$2280` | 0x04 | 🫙 Gourd OBJ 13: Meteorite×2 [0x56] (MAP REF 0x0d) |
| `$2280` | 0x08 | 🫙 Gourd OBJ 14: Acorns [0x56] (MAP REF 0x0e) |
| `$2280` | 0x10 | 🫙 Gourd OBJ 15: Herbal Essence [0x56] (MAP REF 0x0f) |
| `$2280` | 0x20 | 🫙 Gourd OBJ 16: Biscuit [0x56] (MAP REF 0x10) |
| `$2280` | 0x40 | 🫙 Gourd OBJ 17: Feather×4 [0x56] (MAP REF 0x11) |
| `$2280` | 0x80 | 🫙 Gourd OBJ 18: Nectar [0x56] (MAP REF 0x12) |
| `$2281` | 0x01 | 🫙 Gourd OBJ 19: Honey [0x56] (MAP REF 0x13) |
| `$2281` | 0x02 | 🫙 Gourd OBJ 20: Iron×2 [0x56] (MAP REF 0x14) |
| `$2281` | 0x04 | 🫙 Gourd OBJ 21: Petal [0x56] (MAP REF 0x15) |
| `$2281` | 0x08 | 🫙 Gourd OBJ 22: Call Beads×2 [0x56] (MAP REF 0x16) |
| `$2281` | 0x10 | 🫙 Gourd OBJ 23: Mushroom [0x56] (MAP REF 0x17) |
| `$2281` | 0x20 | 🫙 Gourd OBJ 24: Limestone [0x56] (MAP REF 0x18) |
| `$22eb` | 0x20 | ⚙️ Fall-entry animation handshake [0x64→0x57] — if set on enter: teleport to [0x74,0x6c] + fade; else clear |
| `$23bf` | — | ⚙️ Cleared to 0 on enter |
| `$23c5` | — | ⚙️ Written 0x0280 on enter |
| `$238d` | — | 🎵 CHANGE MUSIC register — if 0x00 on enter, play music 0x20 |
| `$2443` | — | 🐶 Dog sprite — set to Greyhound (0x06) |

---

## Enter Script Summary (`0x959a08`)

1. **Fall-entry guard**: if `$22eb&0x20` set → teleport both to [0x74,0x6c] + fade-out;
   else → clear `$22eb&0x20`.
2. `$0ea2+8=0x01`, `$0eac+8=0x1884` (script hook).
3. **Dog-freed routing** (if `$22e3&0x40`): write `$2357=2`, `$2358=2`; clear
   `$22e4&0x04`; clear `$22e5&0x04`, `$22e5&0x02`; clear `$2261&0x02`, `$2261&0x01`;
   write `$2350=0`.
4. `$0ea2+0=0x40`, `$0eac+0=0x172b`.
5. **Enemy drops**: PRIZE1=0x0801 (rate 10); PRIZE2=0x0001 qty 90 (rate 3);
   PRIZE3=0x0802 (rate 1).
6. `$23c5=0x0280`.
7. **Monster spawner** (sub `0x959946`): NPC 0x72 at 16 positions; NPC 0x74 at
   16 positions; NPC 0x39 at 7 positions (39 enemy spawns).
8. **OBJ state restore** (sub `0x959866`): OBJ 0 → state 4+1 if `$22e2&0x10`, else
   state 0; OBJ 1 → state 4 if `$22e2&0x20`, else state 0.
9. **Gourd OBJ unloads**: OBJ 2 if `$227e&0x80`; OBJs 3–24 per `$227f`–`$2281&0x20`.
10. **Music**: if `$238d==0x00`, play music 0x20 + fade-in.
11. `$0ea2+6=0x01`, `$0eac+6=0x1881`; `$23bf=0`; set Greyhound.
12. `$2537 = ($2357)&0xff`.
13. **Boy/dog split** (skipped if `$22e3&0x40`):
    - Boy dest ≠ 2 → `$2261|=0x02`; switch to DOG, teleport boy off-screen.
    - Boy dest = 2 → `$2261&=0xfd`; if `$22e5&0x02`: CALL 0x92a404, clear flag.
    - Dog dest ≠ 2 → `$2261|=0x01`; switch to BOY, teleport dog off-screen.
    - Dog dest = 2 → `$2261&=0xfe`; if `$22e5&0x04`: CALL 0x92a422, clear flag.
14. CALL 0x92de75 (cinematic); `$2350=0`; END.

---

## Step-on Scripts (6 entries)

| # | Tile | Script addr | Description |
|---|------|-------------|-------------|
| 1 | [2f,1c:31,1e] | `0x95983c` | **Gear puzzle A**: one-way; if `$22e2&0x10` already set → skip; else set `$22e2|=0x10`, play SFX 0x58, OBJ 0 → state 4+1 |
| 2 | [12,1b:14,1c] | `0x95953e` | **Descent → 0x55** `[0x01f0\|0x01f0]`: dog → `$2358=1`; boy + `$22e4&0x04` → set `$22e5|=0x04`, `$2261|=0x01`; boy → `$2357=1`; MAP 0x55 |
| 3 | [6a,42:6c,43] | `0x959519` | **Descent → 0x55** `[0x06a0\|0x0360]`: same split logic as #2, alternate destination coords |
| 4 | [55,30:57,31] | `0x959563` | **Exit → 0x06** `[0x02d8\|0x0198]`: fade-out; dog → `$2358=0`; boy → `$22e4&0x04` check + `$2357=0` |
| 5 | [39,47:3b,48] | `0x9594f3` | **Exit → 0x06** `[0x0230\|0x0270]`: fade-out; dog → `$2358=0`; boy → `$2357=0`; if `$2358==0` → `$22e5|=0x04` |
| 6 | [49,47:4b,48] | `0x9594cd` | **Exit → 0x06** `[0x02f0\|0x0270]`: fade-out; dog → `$2358=0`; boy → `$2357=0`; if `$2358==0` → `$22e5|=0x04` |

---

## Exits

| Destination | Trigger | Coords |
|-------------|---------|--------|
| 0x55 'mids bottom | Step-on #2 | `[0x01f0\|0x01f0]` |
| 0x55 'mids bottom | Step-on #3 | `[0x06a0\|0x0360]` |
| 0x06 Outside of 'mids | Step-on #4 | `[0x02d8\|0x0198]` |
| 0x06 Outside of 'mids | Step-on #5 | `[0x0230\|0x0270]` |
| 0x06 Outside of 'mids | Step-on #6 | `[0x02f0\|0x0270]` |

---

## B-triggers (24 entries)

### Gourds (#1–#23)

| # | Tile | Flag | OBJ | Item | MAP REF |
|---|------|------|-----|------|---------|
| 1 | [6a,15:6c,17] | `$2281&0x20` | 24 | Limestone×3 | 0x18 |
| 2 | [63,15:65,17] | `$2281&0x10` | 23 | Mushroom | 0x17 |
| 3 | [4f,15:51,17] | `$2281&0x08` | 22 | Call Beads×2 | 0x16 |
| 4 | [49,17:4b,19] | `$2281&0x04` | 21 | Petal | 0x15 |
| 5 | [47,17:49,19] | `$2281&0x02` | 20 | Iron×2 | 0x14 |
| 6 | [47,2a:49,2c] | `$2281&0x01` | 19 | Honey | 0x13 |
| 7 | [43,3e:45,40] | `$2280&0x80` | 18 | Nectar | 0x12 |
| 8 | [32,41:34,43] | `$2280&0x40` | 17 | Feather×4 | 0x11 |
| 9 | [32,3b:34,3d] | `$2280&0x20` | 16 | Biscuit | 0x10 |
| 10 | [32,35:34,37] | `$2280&0x10` | 15 | Herbal Essence | 0x0f |
| 11 | [28,41:2a,43] | `$2280&0x08` | 14 | Acorns | 0x0e |
| 12 | [28,3b:2a,3d] | `$2280&0x04` | 13 | Meteorite×2 | 0x0d |
| 13 | [28,35:2a,37] | `$2280&0x02` | 12 | Clay×3 | 0x0c |
| 14 | [24,41:26,43] | `$2280&0x01` | 11 | Gunpowder×2 | 0x0b |
| 15 | [24,3b:26,3d] | `$227f&0x80` | 10 | Grease | 0x0a |
| 16 | [24,35:26,37] | `$227f&0x40` | 9 | Wings | 0x09 |
| 17 | [1a,41:1c,43] | `$227f&0x20` | 8 | Ethanol×3 | 0x08 |
| 18 | [1a,3b:1c,3d] | `$227f&0x10` | 7 | Dry Ice×2 | 0x07 |
| 19 | [1a,35:1c,37] | `$227f&0x08` | 6 | Nectar | 0x06 |
| 20 | [16,41:18,43] | `$227f&0x04` | 5 | Limestone×2 | 0x05 |
| 21 | [16,3b:18,3d] | `$227f&0x02` | 4 | Herbal Essence | 0x04 |
| 22 | [16,35:18,37] | `$227f&0x01` | 3 | Water×3 | 0x03 |
| 23 | [1a,1d:1c,1f] | `$227e&0x80` | 2 | Petal | 0x02 |

### Gear Puzzle (#24)

| # | Tile | Condition | Effect |
|---|------|-----------|--------|
| 24 | [37,1e:39,22] | boy + `$235f==12` (weapon index 12) | set `$22e2\|=0x20`, play SFX 0x58, OBJ 1 → state 4 |

---

## NPCs

| NPC ID | Count | Notes |
|--------|-------|-------|
| 0x72 | 16 positions | Enemy spawner (always active) |
| 0x74 | 16 positions | Enemy spawner (always active) |
| 0x39 | 7 positions | Enemy spawner (always active) |

---

## Notes

- **Boy/dog split**: entering with `$2357≠2` (boy not here) → player switches to dog, boy teleported off-screen; entering with `$2358≠2` (dog not here) → player switches to boy, dog teleported off-screen. Overridden when `$22e3&0x40` (dog freed).
- **Floor switch / pressure plate A** (step-on, [2f,1c:31,1e]): one-way toggle, sets `$22e2&0x10` permanently.
- **Floor switch / pressure plate B** (B-trigger #24): requires boy with WEAPON_INDEX ≥ 0x12 (SPEAR_1 / Horn Spear); sets `$22e2&0x20`.
- **Gourd continuity**: 0x55 uses `$227c–$227e&0x40`; 0x56 continues at `$227e&0x80–$2281&0x20`; 0x57 continues at `$2281&0x40` onward.
- `$22e2` bit usage spans both floors: bits 0x01–0x08 are the Lotus Bridge switch puzzle in 0x55; bits 0x10–0x20 are floor switch puzzles in 0x56; bit 0x40 = enemy group (NPC 0x3a) defeated flag (0x55) // TODO: verify ENEMY 0x3a name.
