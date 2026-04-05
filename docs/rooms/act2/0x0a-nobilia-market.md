# 0x0a — Nobilia, Market

| Field | Value |
|-------|-------|
| Room ID | `0x0a` |
| ROM header | `0x9ffe0f` |
| Data ptr | `0x9faaeb` |
| Enter script | `0x92804d` → `0x96b630` |
| Step-on table | `0x9faafa`, len=`0x0042` (11 entries) |
| B-trigger table | `0x9fab3e`, len=`0x015c` (58 tile entries, ~32 unique scripts) |
| Music | `0x2e` (normal) / `0x40` (timer expired) |
| Act | act2 |

---

## Overview

The Nobilia open-air market — the largest interactive room in Antiqua. Features:
- A countdown timer that clears out all NPCs when it expires (tying to the City Square story beat)
- 18 ambient market NPCs with individual talk scripts
- Multiple barter stalls (Gloves of Ra, Silver Sheath, Moxa Stick, Bronze Gauntlet, Appraiser, + more)
- A prophet/fortune-teller NPC with a complex prediction state machine
- A "DO NOT TAUNT THE CHICKENS" easter egg
- Two Inn entrances, three North-of-Market exits, one Desert exit, two City Square exits

---

## Memory Access

| Address | Bits | Name | R/W | Meaning |
|---------|------|------|-----|---------|
| `$225d` | `0x08` | Market timer expired | R/W | NPCs fled; mass object reset; blocks trading |
| `$2513` | all | Market entry timer base | R/W | Snapshot of GameTimer on first entry; expires after 0xc4e0 ticks |
| `$22ef` | `0x02` | Reminder dialog shown | R/W | "This place is empty!" message already displayed |
| `$225f` | `0x20` | Vigor defeated | R | Gates post-Vigor market reminder text |
| `$22d9` | `0x08` | Aegis dead | R | Gates alternate market reminder text |
| `$22d8` | `0x80` | Story flag A | R | Part of timer-expiry compound condition |
| `$22d8` | `0x40` | Story flag B | R | Part of timer-expiry compound condition |
| `$236b` | all | Market state / variant | R/W | 0–3 set via `RAND&3` in showcase; selects prophet behavior and OBJ 0x27 state |
| `$22eb` | `0x04` | Showcase mode | R | If set, randomize `$236b` on enter |
| `$22eb` | `0x40` | Inn entry flag | W | Set on Inn step-on before map change |
| `$22ec` | `0x40` | Inn entry variant | W | Set/cleared on Inn step-on |
| `$2261` | `0x01` | Dog unavailable | R | If set, suppresses dog restore after B-triggers |
| `$2261` | `0x10` | Gloves of Ra traded | R/W | Set when Gloves of Ra deal completes |
| `$2263` | `0x01` | Sun Stone held | R | Checked by Silver Sheath trader |
| `$2263` | `0x20` | Silver Sheath traded | W | Set when Silver Sheath deal completes |
| `$2263` | `0x80` | Moxa Stick trade available | R/W | Checked by Moxa Stick trader |
| `$2262` | `0x08` | Moxa Stick held | R | Checked by Gloves of Ra trader |
| `$2834` | `0x01` | Market music set | R/W | Tracks whether `0x40` music already set in main loop |
| `$2834` | `0x02` | Appraiser phase | W | Written during appraisal loop |
| `$2834` | `0x08` | Appraisal done | R | Skips refund offer if set |
| `$2389` | all | Chicken anger counter | R/W | How many times player has taunted chickens; +2 each event |
| `$286d` | all | Chicken visit counter | R/W | Incremented each B-trigger press in chicken area; triggers event at 0xc8 |
| `$244f` | all | Prophet prediction index | R/W | Current fortune state; 0=idle; 3–9=escalating; reset after timer |
| `$2451` | all | Prophet visit counter | R/W | Incremented each visit; affects branching |
| `$254d` | all | Prophet timer base | R/W | Snapshot of GameTimer; resets prediction if elapsed > 0x0e10 |
| `$2413` | all | Unknown | W | Written `0x008c` on entry |
| `$22f3` | `0x08` | Coming from north end | W | Set on Desert exit step-on |
| `$22fd` | all | Desert wrap X? | W | Written `0x0004` on Desert exit |
| `$22fc` | all | Desert wrap Y? | W | Written `0x0011` on Desert exit |
| `$2515` | all | Market minutes remaining | R | Countdown display used in trader "closing soon" dialogs |
| `$2539` | all | Timer snapshot copy | W | Copy of `$2515` made by countdown sub |
| `$251f` | all | Golden jackal count | R/W | Trade good; decremented by Silver Sheath trade |
| `$2521` | all | Tapestry count (large) | R/W | Trade good; decremented by Moxa Stick trade |
| `$2523` | all | Tapestry count (small?) | R/W | Trade good; decremented by stall 17a trade |
| `$2527` | all | Spice count A | R/W | Trade good; decremented by stall 17a |
| `$2529` | all | Spice count B | R/W | Trade good; decremented by Silver Sheath / Bronze Gauntlet / Moxa Stick |
| `$252b` | all | Souvenir spoon count | R/W | Trade good; decremented by Bronze Gauntlet trade |
| `$252d` | all | Tapestry count (Bronze) | R/W | Trade good; decremented by Bronze Gauntlet trade |
| `$251d` | all | Rice count? | R/W | Trade good; decremented by Moxa Stick trade |
| `$2339` | `0xff` (low byte) | Items sold counter | R/W | Incremented each successful trade (`$233a` = +1) |
| `$243f` | all | Received item code | W | Item to add to inventory (after trade) |
| `$243d` | all | Taken item code | W | Item to remove from inventory (after trade) |
| `$2463` | all | "Can't buy" reason | W | Written `0x0007` when trade requirements not met |
| `$2895` | all | Prophet random seed | W | `RAND & 31` used for prediction branching |
| `$2891` | all | Appraisal counter | W | Reset to 0 after full appraisal cycle |
| `$288f` | all | Appraisal loop | W | Reset to 0 each loop in appraiser |
| `$289d` | all | Dialog response | W | Stores player's yes/no choice |
| `$2899` | all | Chicken man visit counter | R/W | +1 each visit; selects dialog line |
| `$2835–$2859` | all | NPC entity refs | W | Entity pointers for 18 spawned market NPCs |

---

## Enter Script Summary

1. **Default teleport:** `(0x07, 0x4b)` / `$2413 = 0x008c`
2. **Showcase mode** (if `$22eb&0x04`): randomize `$236b = RAND&3`; set OBJ 0x27 to state 1/2/3/4 based on `$236b` (market display variant)
3. **Timer-expired pre-check** (compound condition):
   - If `$22d8&0x80 && $22d8&0x40 && !$22d9&0x08` → set `$22ef|=0x02` + `$225d|=0x08`
   - Else check `$2513`: if nonzero and `!$225f&0x20` and `GameTimer - $2513 > 0xc4e0` → set `$225d|=0x08`; else write `$2513 = GameTimer`
4. **Timer expired path** (if `$225d&0x08`):
   - Fade + stop music
   - Call `0x968000` — mass-set OBJ 0–0x25 to state 1 (all NPCs unloaded/reset)
   - Skip 298 instructions (bypasses NPC spawn block)
5. **Normal path — Spawn 18 NPCs:**

| # | Type | Position (x,y) | Ref | Talk script |
|---|------|----------------|-----|-------------|
| 1 | `0x1c` | `(0x11,0x43)` | `$2835` | `0x191d` |
| 2 | `0x1c` | `(0x4b,0x31)` | `$2837` | `0x1920` |
| 3 | `0x1c` | `(0x41,0x77)` | `$283b` | `0x1944` |
| 4 | `0x1d` | `(0x19,0x15)` | `$283d` | `0x1923` |
| 5 | `0x1d` | `(0x39,0x2d)` | `$2841` | `0x194a` |
| 6 | `0x1b` | `(0x4d,0x8f)` | `$2843` | `0x1929` |
| 7 | `0x1b` | `(0x21,0x77)` | `$2845` | `0x192c` |
| 8 | `0x1b` | `(0x4d,0x17)` | `$2847` | `0x194d` |
| 9 | `0x1a` | `(0x11,0x6d)` | `$2849` | `0x192f` |
| 10 | `0x1a` | `(0x25,0x8d)` | `$284d` | `0x1932` |
| 11 | `0x1a` | `(0x35,0x1b)` | `$284f` | `0x1947` |
| 12 | `0x18` | `(0x15,0x61)` | `$2851` | `0x1935` |
| 13 | `0x18` | `(0x23,0x47)` | `$2853` | `0x1950` |
| 14 | `0x19` | `(0x55,0x4b)` | `$2855` | `0x1938` |
| 15 | `0x19` | `(0x3d,0x8f)` | `$2859` | `0x1953` |
| 16 | `0x19` | `(0x37,0x4b)` | `$2857` | `0x1941`; script-controlled; face north |
| 17 | `0x1a` | `(0x3f,0x43)` | `$284b` | `0x193e`; script-controlled; face west |
| 18 | `0x1d` | `(0x09,0x53)` | `$283f` | `0x193b`; script-controlled; face east |
| 18b | `0x1c` | `(0x0b,0x57)` | `$2839` | `0x1926`; script-controlled; face east |

6. **NPC main loop** (RCALL `0x95ebb0`): position-based culling — unloads any NPC that has wandered outside its valid zone. Each NPC ref checked; if outside bounding box, DESTROY; else reposition to `(0x02e8, 0x00b8)`.
7. **Music:** if `$225d&0x08` → play `0x40`; else → play `0x2e`
8. **Showcase walk** (if showcase mode): Horn Spear weapon displayed; Greyhound dog; boy walks through market path
9. **Dog unavailable check:** if `$2261&0x01` → suppress dog sprite / call global `0x36`
10. **`$22eb&0x40` special entry animation** check (unlocks after Inn entry; plays door animation)
11. **Reminder dialog** (if `$225d&0x08` AND `!$22ef&0x02`):
    - If `!$225f&0x20` (Vigor not defeated): *"This place is empty! The big meeting in the city square is probably starting!"*
    - Elif `!$22d9&0x08` (Aegis alive): *"We've got to go to the city square. That guy with the Diamond Eyes is probably placing them in the statue right now!"*
12. **Main timer countdown loop** (if `!$225f&0x20` AND `!$225d&0x08`): each loop checks `GameTimer - $2513 > 0xc4e0`; when expired → set `$225d|=0x08` + set music `0x40`

---

## Step-ons

| Tile rect | Dest | Condition | Notes |
|-----------|------|-----------|-------|
| `[0b,2e:0f,2f]` | — | always | Write `$244f = 0x0000` (reset prophet prediction) |
| `[0a,2a:0b,2f]` | — | always | Write `$244f = 0x0000` |
| `[0a,29:10,2a]` | — | always | Write `$244f = 0x0000` |
| `[1a,06:20,09]` | 0x1c "Nobilia, North of Market" @ `[0x0260\|0x01c0]` | always | North exit (middle) |
| `[2d,06:31,09]` | 0x1c @ `[0x0390\|0x01c0]` | always | North exit (east) |
| `[0b,06:0e,09]` | 0x1c @ `[0x0040\|0x01c0]` | always | North exit (west) |
| `[33,0d:35,11]` | 0x09 "Square during Aegis fight" @ `[0x0108\|0x0208]` | if `$22d8&0xC0 && !$22d9&0x08` (pre-boss: clear `$225d&0xf7`, call global `0x2e`) | East exit → Square |
| `[33,0d:35,11]` | 0x08 "Nobilia, Square" @ `[0x0008\|0x00a0]` | else (post-boss or normal) | East exit → Square |
| `[34,24:35,29]` | 0x09 @ `[0x0108\|0x0208]` | same condition as above | East exit (south) |
| `[34,24:35,29]` | 0x08 @ `[0x0008\|0x0200]` | else | East exit (south) |
| `[07,27:08,2a]` | 0x1b "Desert of Doom" @ `[0x01d8\|0x00c8]` | always | West desert exit; sets `$22f3\|=0x08`, `$22fd=4`, `$22fc=0x11` |
| `[32,22:34,23]` | 0x0c "Nobilia, Inn" @ `[0x0058\|0x0208]` | always | Inn north door 1; sets `$22eb\|=0x40`, clears `$22ec&0xbf` |
| `[31,40:33,41]` | 0x0c "Nobilia, Inn" @ `[0x0068\|0x00d8]` | always | Inn north door 2; sets `$22eb\|=0x40`, sets `$22ec\|=0x40` |

---

## B-triggers

58 tile entries / ~32 unique scripts. The B-trigger grid covers the full market layout.

### Documented Interactions

#### Chicken Easter Egg — `[10,1e:12,1f]`, `[11,20:12,21]`, `[0e,1f:0f,20]`
- **Dog:** *"I'm sorry buddy. I don't have any dog treats— just chicken feed."*
- **Timer expired:** Chicken-man market-closing dialog (2 variants based on `$2899` visit counter)
- **Normal:** *"These chickens aren't for sale. They're my friends."* / *"And you're not."* (if `$2389 != 0`)
- **Taunt mechanic** (increments `$286d`; at 0xc8 threshold → `$2389>>1` anger tier):
  - Tier 0: Show text "HEY, YOU" / "YES, -YOU-" then DAMAGE player for max HP-1, spawn NPC `0x20` explosion, screen shake; "DO NOT TAUNT THE CHICKENS"
  - Tier 1 (`$2389==2`): HEAL player 0x3e7, then instant kill again; "YOU WERE WARNED" / "YOU WILL REGRET THAT"
  - Tier 2+: HEAL + instant kill; "I CAN DO THIS ALL DAY"
- **`$2389` += 2** each event; `$286d` reset to 0

#### Prophet / Fortune Teller — `[0d,2c:0f,2d]`
- **`$236b == 1`:** Route to chicken man east-egg dialog (CALL `0x96b0b8`)
- **`$236b == 2`:** Route to chicken man dialog (CALL `0x96b0e0`)
- **`$236b == 3`:** *"Baskets don't talk."* (boy only; dog: "The sacred dog! I'm a big fan!")
- **`$236b == 0` / else:** Complex prediction state machine using `$244f` (0–9+ state), `$2451` visit counter, `$2895` random rolls; delivers fortune dialog at `0x96ad2a`
- **Timer expired:** *"I predict that all of the merchants will soon leave to attend the meeting in the square"*
- `$22eb&0x80` gates re-prediction; `$254d` timer resets `$236b=0` / `$244f=0` if elapsed > `0x0e10`

#### Gloves of Ra Trader — `[2a,47:2d,48]`
- Dog: rejected ("no trade with dog")
- Timer expired: RCALL `0x96808f` *"We're not trading anymore today…"*
- Already traded (`$2261&0x10`): *"I traded my best item to you already."*
- Has Moxa Stick (`$2262&0x08`) → offer Gloves of Ra: yes → take Moxa Stick, give `$243f=0x000c` (Gloves of Ra); set `$2261|=0x10`, `$2339+1`
- Else (Bronze Gauntlet offer): 2 tapestries (`$252d>1`) + 1 souvenir spoon (`$252b`) → `$252d-=2`, `$252b-=1`, give `$243d=0x000c` (item?), `$2339+1`
- Can't trade: `$2463=0x0007`

#### Silver Sheath Trader — `[24,47:27,48]`
- Already traded (`$2263&0x20`): *"You've already traded for my most valuable item."*
- Offer: Silver Sheath for Sun Stone OR golden jackal + 10 spice
  - Sun Stone (`$2263&0x01`): yes → take Sun Stone (`$243d=0x0012`), give `$243f=0x0016` (Silver Sheath)
  - Other goods (`$251f` + `$2529>=10`): → `$251f-=1`, `$2529-=10`, give `$243d=0x000c`(?)
- `$2263|=0x20` on success

#### Appraiser — `[20,47:23,48]`
- Dog: *"I would appraise your valuables, but you don't seem to have any."*
- Timer expired: *"The market is closing. I'll appraise your valuables if you come back tomorrow."*
- Fee: 5 jewels per appraisal; `$2348` currency
- Loop: calls `0x969b8a` "Nobilia market - appraisal dialog" + `0x969b35`; sets `$2834|=0x02`; asks repeat; refunds 5 jewels if `$2834&0x08` incomplete

#### Moxa Stick Trader — `[14,46:17,47]`
- Already traded (`$2263&0x80`): *"I gave you my only Moxa Stick."*
- Offer Moxa Stick for: 12 spice (`$2529>=12`) + 1 tapestry (`$2521`) + 2 rice? (`$251d>=2`): → `$2529-=12`, `$2521-=1`, `$251d-=2`, give `$243d=0x000c`

#### Stall 17a — `[10,46:13,47]`
- Timer expired: RCALL `0x968083`
- Already traded (`$2263&0x10`): RCALL `0x96811a` (closing-time countdowns)
- Offer for 5 spice (`$2527>=5`) + 1 tapestry (`$2523`): → `$2527-=5`, `$2523-=1`, give `$243d=0x0016`

### Remaining B-trigger Tile Grid (scripts not fully read)

| Tile rect | ID | Area description |
|-----------|----|-----------------|
| `[26,3c:29,3d]` | 0x17d | Market stall row 4 (east) |
| `[20,3c:23,3d]` | 0x180 | Market stall row 4 |
| `[14,3c:17,3d]` | 0x183 | Market stall row 4 |
| `[10,3c:13,3d]` | 0x186 | Market stall row 4 (west) |
| `[0a,3e:0b,41]` | 0x189 | West corridor stall (north) |
| `[0a,34:0b,37]` | 0x18c | West corridor stall (south) |
| `[30,32:31,35]` | 0x18f | Northeast corner stall |
| `[2a,2f:2d,30]` | 0x192 | Market stall row 3 (east) |
| `[1c,2e:1d,2f]` | 0x195 | Market stall row 3 |
| `[14,2f:17,30]` | 0x198 | Market stall row 3 |
| `[10,2f:13,30]` | 0x19b | Market stall row 3 (west) |
| `[14,23:17,24]` | 0x19e | Market stall row 2 |
| `[1a,23:1d,24]` | 0x1a1 | Market stall row 2 |
| `[2b,23:2e,24]` | 0x1a4 | Market stall row 2 (east) |
| `[27,17:2a,18]` | 0x1a7 | Market stall row 1 (east) |
| `[23,17:26,18]` | 0x1aa | Market stall row 1 |
| `[1d,17:20,18]` | 0x1ad | Market stall row 1 |
| `[1a,17:1d,18]` | 0x1b0 | Market stall row 1 (west) |
| `[0b,1f:0c,20]` | 0x1b3 | Near chicken pen |
| `[29,0a:2c,0b]` | 0x1b6 | North entrance stall (east) |
| `[21,0b:24,0c]` | 0x1b9 | North entrance stall |
| `[19,0c:1b,0d]` | 0x1bc | North entrance stall (west) |
| `[0a,11:0b,14]` | 0x1bf | Northwest corner area |
| `[0a,0a:0b,0d]` | 0x1c2 | Northwest corner area (north) |

All stall interactions share the same pattern: dog rejection, timer-expired routing (to one of `0x96808f`/`0x968088`/`0x968083` depending on tier), "already traded" gate flag, offer dialog with accept/reject, RCALL `0x9680ab` on reject (random "Kids…Always looking" / "Yeesh, Tourists!" / "Fine. Have a nice day!" responses), inventory check on accept.

---

## Shared Subroutines

| Address | Name |
|---------|------|
| `0x968083` | Market timer sub 1 — "We're packing up to attend the big meeting" |
| `0x96808f` | Market timer sub 2 — "The big meeting in the City Square is about to happen" |
| `0x968096` | Market timer sub 3 — "We're not trading anymore today" |
| `0x9680ab` | Market reject sub — random "window-shopping" insult dialog |
| `0x96811a` | Market countdown sub — "We'll be closing in N minutes" (reads `$2515`) |
| `0x968000` | Mass NPC reset — SET OBJ 0–0x25 STATE=1 (bulk unload) |
| `0x95ebb0` | NPC proximity cull loop — destroy + reposition wandered-off NPCs |
| `0x969b8a` | Appraiser dialog |
| `0x969b35` | Appraiser sub-loop |
| `0x96ad2a` | Prophet easter-egg dialog (Nobilia market fortune) |
| `0x92cd89`/`0x92cd90`/`0x92cd97` | "No trade with dog" stubs |
| `0x92cdb3` | "Can't buy (not enough …)" stub |
| `0x92cc6c` | Unknown script in square (called by countdown sub when `!$225f&0x20`) |
