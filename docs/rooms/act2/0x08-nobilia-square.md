# 0x08 — Nobilia, Square

| Field | Value |
|-------|-------|
| Room ID | `0x08` |
| ROM header | `0x9ffe07` |
| Data ptr | `0xa5b42e` |
| Enter script | `0x928043` → `0x95e090` |
| Step-on table | `0xa5b43d`, len=`0x001e` (5 entries) |
| B-trigger table | `0xa5b45d`, len=`0x001e` (5 entries) |
| Music | `0x40` (normal) / `0x4a` (market timer expired or credits) |
| Act | act2 |

---

## Stats

| Stat | Value |
|------|-------|
| Sniff spots | 0 |
| Gourds | 0 |
| Exits | 5 |
| NPCs (ambient, pre-Vigor) | 6 |
| NPCs (Sacred Dog ceremony) | 10–12 |

---

## Overview

Large outdoor public square — the civic center of Nobilia. Connects Market to the west, the Fountain area to the north, an Inn building, and the Fire Pit to the south. Houses two sacred dog statues and, after Aegis is fought, a crater.

Three major cutscene paths:

1. **Sacred Dog ceremony** (`MARKET_TIMER_EXPIRED` — `$225d&0x08`): The crowd assembles, the dog is recognized as the Sacred Dog, and the player is escorted to the Arena Holding Room (`0x1e`).
2. **Square outro** (`OUTRO` — `$22f1&0x40`): Farewell scene between boy, Horace, and Madronius; plays music `0x8e`, ends with `CHANGE MAP → 0x3a` (Fire Pit).
3. **Credits** (`$22f2&0x01`): Suppresses dog, hides HUD, spawns NPC 0x64 for credits sequence.

Object states controlled by story flags:
- Objs 0–3, 5–9, 11–12 → `SET STATE 1` during Sacred Dog ceremony (crowd obstacles)
- Obj 13 → `STATE 1` if `Aegis dead`; `STATE 2` if `WINDWALKER_UNLOCKED` or `in credits`
- Obj 14 → unloaded if `Aegis dead`

---

## Exits

| Trigger | Destination | Notes |
|---------|-------------|-------|
| Step-on `[2d,1a:2e,1d]` | `0x3a` Nobilia, Fire pit | South exit |
| Step-on `[03,30:05,31]` | `0x0c` Nobilia, Inn | Sets `$22eb\|=0x40`, `$22ec\|=0x40` before map change |
| Step-on `[14,01:19,03]` | `0x4c` Nobilia, Fountain and snake statues | North exit |
| Step-on `[00,1e:02,22]` | `0x0a` Nobilia, Market | West exit (lower) |
| Step-on `[00,08:02,0c]` | `0x0a` Nobilia, Market | West exit (upper) |

---

## Memory Access

| Address | Bits | Name | R/W | Meaning |
|---------|------|------|-----|---------|
| `$22eb` | `0x20` | IN_ANIMATION | R | Suppresses normal enter when set; cleared via `$22eb &= 0xdf` on outro path |
| `$22eb` | `0x08` | DEBUG | R | Overrides `IN_ANIMATION` check on enter |
| `$22eb` | `0x40` | Inn entry animation | W | Set on Inn step-on before map change |
| `$22ec` | `0x40` | Inn entry variant | W | Set on Inn step-on before map change |
| `$22f1` | `0x40` | OUTRO | R | Triggers Square outro cutscene; plays music 0x8e, ends at 0x3a |
| `$22f2` | `0x01` | in credits | R | Triggers credits path; suppresses NPCs and dog |
| `$2261` | `0x01` | Dog unavailable | R/W | Read: suppress dog restore; Set (credits path): `$2261 \|= 0x01` |
| `$2261` | `0x02` | Boy unavailable | W | Set during credits path: `$2261 \|= 0x02` |
| `$225d` | `0x08` | MARKET_TIMER_EXPIRED | R/W | Triggers Sacred Dog ceremony; cleared at start; also clears `$22ef&0x02` |
| `$22ef` | `0x02` | Market reminder dialog shown | W | Cleared (`&= 0xfd`) at start of Sacred Dog path |
| `$225f` | `0x20` | Vigor defeated | R | Selects post-Vigor crowd vs pre-Vigor ambient NPCs |
| `$22d9` | `0x08` | Aegis dead | R | Gates obj 13 / obj 14 state; enables crater-guard extra line |
| `$22dc` | `0x08` | WINDWALKER_UNLOCKED | R | Co-gates obj 13 state (val:2 if set or in credits) |
| `$2515` | all | Market minutes remaining | R | Post-Vigor: selects which crowd NPCs load based on trade count (`<8`, `<6`, `<5`, `<3`) |
| `$2443` | all | CHANGE_DOGGO | W | Written `0x06` (Greyhound) on enter |
| `$238d` | all | CHANGE_MUSIC | R/W | If 0: play music on enter; written `0x0001` before MAP CHANGE to `0x1e` |
| `$23bf` | all | PACIFIED | W | Written `0x0001` on normal enter |
| `$238f` | all | TRANSITION_ENTER_DIRECTION | W | Written `0x0000` in outro path |
| `$2409` | all | SCREEN_SHAKING_X | W | Outro cutscene: written 1→2→3 |
| `$240b` | all | SCREEN_SHAKING_Y | W | Outro cutscene: written 0→1→3 |
| `$2413` | all | Camera pan X target | W | Outro cutscene |
| `$2415` | all | Camera pan Y target | W | Outro cutscene |
| `$242f` | all | CAMERA_PAN_SPEED | W | Written `0x0014`, `0x0020` during Sacred Dog ceremony |
| `$242b` | all | Camera scroll X | W | Written during Sacred Dog ceremony |
| `$242d` | all | Camera scroll Y | W | Written during Sacred Dog ceremony |
| `$2443` | all | CHANGE_DOGGO | W | Written `0x06` (Greyhound) |
| `$2852` | all | Entity ref: Madronius | W | NPC `0x8a` loaded at (2c,33) in outro |
| `$2854` | all | Entity ref: Horace | W | NPC `0x64` loaded at (2a,33) in outro |
| `$2836` | all | Entity ref: crowd NPC | W | Ceremony crowd NPCs (`$2836`–`$284a`) |
| `$2842` | all | Entity ref: crowd NPC | W | |
| `$283e` | all | Entity ref: crowd NPC | W | |
| `$2846` | all | Entity ref: crowd NPC | W | |
| `$283c` | all | Entity ref: crowd NPC | W | |
| `$2840` | all | Entity ref: crowd NPC | W | |
| `$2844` | all | Entity ref: crowd NPC | W | |
| `$2838` | all | Entity ref: crowd NPC | W | |
| `$2848` | all | Entity ref: crowd NPC | W | |
| `$284a` | all | Entity ref: crowd NPC | W | |
| `$284c` | all | Entity ref: herald/crier NPC | W | NPC `0x62` at (2b,2a); omitted during credits |
| `$284e` | all | Entity ref: Tiny | W | NPC `0x8c` at (28,2f); omitted during credits |
| `$2856` | all | Crater guard dialogue toggle | R/W | Session-local; `0=first visit` text / `1=repeat` text |

---

## NPCs

### Pre-Vigor ambient state (loaded when `!MARKET_TIMER_EXPIRED && !in_credits`)

| Sprite | Pos (x,y) | Talk script | Notes |
|--------|-----------|-------------|-------|
| NPC `0x18` | (0x15, 0x15) | `0x18f6` | |
| NPC `0x19` | (0x11, 0x21) | `0x18f9` | |
| NPC `0x1a` | (0x13, 0x2d) | `0x18fc` | |
| NPC `0x1b` | (0x33, 0x13) | `0x18ff` | |
| NPC `0x1c` | (0x11, 0x4b) | `0x1902` | |
| NPC `0x1b` | (0x19, 0x5f) | `0x1905` | |

### Post-Vigor ceremony crowd (loaded when `Vigor defeated`; varies by `$2515`)

| Sprite | Pos (x,y) | Entity ref | Talk script | Condition |
|--------|-----------|------------|-------------|-----------|
| NPC `0x36` | (0x2d, 0x37) | `$2842` | — | always |
| NPC `0x34` | (0x2a, 0x3a) | `$283e` | `0x190b` | `$2515 < 8` |
| NPC `0x38` | (0x2e, 0x3e) | `$2846` | `0x190e` | `$2515 < 6` |
| NPC `0x30` | (0x2d, 0x43) | `$2836` | `0x191a` | `$2515 < 3` |
| NPC `0x32` | (0x30, 0x43) | `$283c` | `0x1917` | `$2515 < 3` |
| NPC `0x34` | (0x2c, 0x48) | `$2840` | — | always |
| NPC `0x36` | (0x2f, 0x48) | `$2844` | — | always |
| NPC `0x30` | (0x2b, 0x4b) | `$2838` | — | always |
| NPC `0x38` | (0x2e, 0x4c) | `$2848` | — | always |
| NPC `0x3a` | (0x29, 0x40) | `$284a` | `0x1911` | `$2515 < 5` |
| NPC `0x62` | (0x2b, 0x2a) | `$284c` | — | if `!in_credits` |
| NPC `0x8c` (Tiny) | (0x28, 0x2f) | `$284e` | — | if `!in_credits` |

---

## B-Triggers

| Tile region | Script | Notes |
|-------------|--------|-------|
| `[17,2d:19,2e]` | `0x95d7ed` | Palace entrance guard; dog gets special "Sacred Dog" line; boy gets rules speech; extra line added if `Aegis dead` |
| `[11,16:13,17]` | `0x95d7b7` | Small sacred dog statue guard; dog: "You look like this statue"; boy: "Do not play on the statue" |
| `[19,16:1b,17]` | `0x95d7d2` | Large sacred dog statue guard; dog: "You're the Sacred Dog!"; boy: "I protect the statue" |
| `[13,03:15,04]` | `0x95d817` | Palace gate guard (north); dog and boy both denied entry; dog gets longer speech |
| `[15,1b:17,1c]` | `0x95d832` | Crater guard; uses `$2856` to alternate two dialogue lines |

---

## Notes

- **Entry path branches**: Three mutually exclusive paths based on flag priority: `$22f1&0x40` (OUTRO) → cutscene to Fire Pit; `$22f2&0x01` (in credits) → credits sequence; normal path uses `MARKET_TIMER_EXPIRED` check.
- **`$22eb&0x08` (DEBUG flag)**: overrides the `IN_ANIMATION` branch guard on enter — the only room in act2 observed to read DEBUG on entry.
- **Sacred Dog trigger (`$225d&0x08`)**: Set in [0x0a Nobilia Market] when the trade-countdown timer reaches zero. This room clears it immediately on entering the ceremony path.
- **Crowd tier system**: Post-Vigor, four NPC groups are conditionally loaded based on `$2515` (minutes remaining on market timer). Higher trade count → more crowd NPCs.
- **`$2856` crater guard toggle**: Session-local (lives in `$2834–$28fb` scratchpad range). Resets to 0 every visit. First B-trigger interaction shows full guard speech; subsequent ones show a shorter repeat.
- **Obj 13 / Obj 14**: After Aegis is killed (`$22d9&0x08`), obj 14 (Sacred Dog Statue prop) is unloaded and obj 13 (crater) state is set to 1. If `WINDWALKER_UNLOCKED` is also set, obj 13 state is 2 instead. In credits, obj 13 state is also 2 (same as post-WindWalker).
- **Two west exits**: Both step-ons transition to `0x0a` (Market) — one through the upper corridor, one through the lower. Neither sets the Inn animation flags.
- **Inn step-on**: Sets both `$22eb|=0x40` and `$22ec|=0x40` before the map change — these flags control the Inn entry cutscene direction in [0x0c].
