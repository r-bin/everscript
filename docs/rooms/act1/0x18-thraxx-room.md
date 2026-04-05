# 0x18 — Prehistoria: Thraxx' Room

**ROM address:** `0x9ffe47`  
**Data address:** `0xab8ad2`  
**Enter script:** `0x928093` → `0x93d201`  
**Act:** 1 — Prehistoria

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on zones | 3 (2 conditional exits + 1 maggot trigger) |
| B-trigger zones | 2 (Strong Heart cutscene zone + Thraxx weak-point zone) |
| Gourds | 0 |
| Sniff spots | 0 |
| NPCs | 3 (Thraxx left claw, right claw, body) + 1 post-battle (Strong Heart) |
| Music | `0x04` (boss battle) during fight; `0x78`→`0x26` after Wheel found |

---

## Connections

| Direction | Zone | Destination | Notes |
|-----------|------|-------------|-------|
| North (step-on) | `[16,0e:18,10]` | `0x67` Bugmuck exterior @ `0x0058` | Gate: (`$2260&0x10` AND `$22e9&0x08`) OR (`$22e8&0x40` AND `$2264&0x08`); script `0x29` |
| South (step-on) | `[14,23:19,25]` | `0x17` Bug room 2 @ `0x0028` | Same gate conditions; script `0x21` |

---

## Memory Access

| Address | Bits | Category | R/W | Meaning |
|---------|------|----------|-----|---------|
| `$22eb` | `0x20` | ⚙️ | R/W | In animation |
| `$22eb` | `0x04` | ⚙️ | R | Attraction/showcase mode |
| `$2260` | `0x08` | 📖 | R/W | Thraxx maggots triggered — set on maggot step-on; gates Thraxx fight loop |
| `$2260` | `0x10` | 📖 | R | Thraxx dead — set by Thraxx kill script; gates all post-battle paths |
| `$2264` | `0x08` | 💎 | R/W | Wheel obtained — set in B-trigger post-battle (`$22e8&0x40` path) |
| `$22dc` | `0x08` | ⚙️ | R | Unknown — gates alternate-path enter/fight sequences |
| `$22e8` | `0x40` | 📖 | R | "BBM ride done?" or alternate post-Thraxx event flag |
| `$22e8` | `0x80` | 📖 | R/W | Alternate maggot trigger seen — set after `$22dc&0x08` path |
| `$22e9` | `0x08` | 📖 | R/W | Strong Heart cutscene seen — set after post-battle dialogue; required to exit |
| `$2834` | `0x01` | ⚙️ | R/W | Thraxx attack phase A |
| `$2834` | `0x02` | ⚙️ | R/W | Thraxx phase complete gate (set when `$2853 >= 4`) |
| `$2834` | `0x04` | ⚙️ | R/W | Thraxx attack phase C |
| `$2834` | `0x08` | ⚙️ | R/W | Thraxx attack phase D |
| `$2834` | `0x10` | ⚙️ | R/W | Thraxx attack phase E |
| `$2853` | — | 📖 | R/W | Thraxx phase counter (0–3; reaches 4 to finish fight) |
| `$2855` | — | ⚙️ | R/W | Entity ID: maggot 1 |
| `$2857` | — | ⚙️ | R/W | Entity ID: maggot 2 |
| `$2859` | — | ⚙️ | R/W | Entity ID: maggot 3 |
| `$285b` | — | ⚙️ | R/W | Entity ID: maggot 4 |
| `$285d` | — | ⚙️ | R/W | Total maggots spawned counter |
| `$2861` | — | ⚙️ | R/W | Hits within current phase (max 3) |
| `$2865` | — | ⚙️ | R/W | AOE attack timer (fires at >25 ticks) |
| `$2867` | — | ⚙️ | R/W | Phase timer (fires at >30 with `$2834&0x02`) |
| `$2869` | — | ⚙️ | R/W | Entity ID: Thraxx body |
| `$286b` | — | ⚙️ | R/W | Left claw alive flag (1=alive) |
| `$286d` | — | ⚙️ | R/W | Right claw alive flag (1=alive) |
| `$286f` | — | ⚙️ | R/W | Entity ID: left claw (NPC 10) |
| `$2871` | — | ⚙️ | R/W | Entity ID: right claw (NPC 11) |
| `$2881` | — | ⚙️ | R/W | Entity ID: Strong Heart NPC (post-battle) |
| `$287d` | — | ⚙️ | R/W | Thraxx "closed/invulnerable" state register |
| `$287f` | — | ⚙️ | R/W | Thraxx "open/vulnerable" state register |
| `$249b` | — | ⚙️ | R/W | Dynamic obj reference (written `0x0001` on enter) |
| `$23bf` | — | ⚙️ | W | Written `0x0000` |
| `$238d` | — | 🎵 | R | CHANGE MUSIC flag |
| `$285d`–`$287f` | — | ⚙️ | W | Thraxx fight engine registers (bulk init on enter) |

---

## NPCs

| NPC | Slot | Usage | Script | Notes |
|-----|------|-------|--------|-------|
| NPC 10 | Left claw | Fight path (Thraxx alive) | `0x17bb` | Stored in `$286f` |
| NPC 11 | Right claw | Fight path (Thraxx alive) | `0x17be` | Stored in `$2871` |
| NPC 14 | Thraxx body | Fight path (Thraxx alive) | `0x17cd` | Stored in `$2869` |
| NPC 85 | Left claw alt | Alternate path (`$22e8&0x40`) | `0x17bb` | Stored in `$286f` |
| NPC 86 | Right claw alt | Alternate path | `0x17be` | Stored in `$2871` |
| NPC 84 | Thraxx body alt | Alternate path | `0x17d0` | Stored in `$2869` |
| NPC `0x7e` | Strong Heart | B-trigger post-battle cutscene | — | `VILLAGER_1_8` |
| NPC `0x001c>>1` | Maggots | Spawned during fight (×4) | `0x17c1`/`0x17c4`/`0x17c7`/`0x17ca` | Killed individually |

---

## Objects

| Obj | State meaning | Notes |
|-----|--------------|-------|
| 0 / `$249b` (=1) | Thraxx body position; `$287f`=vulnerable, `$287d`=invulnerable | Toggled throughout fight |
| 2 | Shown (state 1) when Thraxx dead (post-battle object) | |
| 3 | Shown (state 1) when Thraxx dead | |
| 4 | Barrier; shown state 1 during maggot trigger, hidden state 0 after Strong Heart cutscene | |

---

## Enter Script Branches

| Branch | Condition | Action |
|--------|-----------|--------|
| A — Post-battle (no ride) | `$2260&0x10` AND NOT `$22dc&0x08` | Load post-battle objects, fade in, skip to cinematic |
| B — Post-battle (on ride) | `$22dc&0x08` AND `$22e8&0x40` | Same as Branch A |
| C — Fight (normal) | NOT `$2260&0x10`, NOT both above | Load NPC 10/11/14, spawn 4 maggots, play music `0x04`, enter fight loop |
| D — Fight (alternate) | NOT `$22e8&0x40`, `$2260&0x10`, `$22dc&0x08` | Load NPC 84/85/86 (alternate sprites), same fight loop |
| E — Attraction mode | `$22eb&0x04` | Walk-in animation, fight preview, call global `0x59` |

---

## Thraxx Fight Mechanics

### Weak-point B-trigger (`[16,11:18,12]`)

| Action | Effect |
|--------|--------|
| Player steps on zone | Deal `2 + $2861` damage to Thraxx (`$2869`), increment `$2861` |
| `$2861 > 2` | Advance phase: reset `$2861=0`, sleep 119 ticks, `$2853++`, set obj 0 state `$287f` |
| `$2853 >= 4` | Fight over: set `$2834\|=0x02`, hide obj 0 (state `$287d`) |

Total weak-point hits to defeat: **12** (4 phases × 3 hits each).

### Maggot Spawning (`Thraxx enter part [3]`)

On each timer cycle (every ~60 ticks), one maggot is spawned at a random position (8 possible positions). Each maggot has a unique kill-script that removes it from `$2855`/`$2857`/`$2859`/`$285b`.

### Attack Cycle (`Thraxx enter part [4]`)

Fires every 26 timer cycles. Rotates through 5 attack types (`$2834 bits 0x04`→`0x08`→`0x10`→`0x04`). Notable: bit `0x10` phase triggers a "tentacle attack" using `b5 REVEAL ENTITY` that deals 70 damage to boy and dog.

---

## Step-on Zones

| Zone | Condition | Action |
|------|-----------|--------|
| `[13,21:1a,23]` (maggot trigger) | NOT `$2260&0x08` AND NOT `$2260&0x10` | Enter fight: `$2260\|=0x08`, clear flags, walk to pos (0x17,0x2a) |
| `[13,21:1a,23]` (alternate path) | `$22dc&0x08` AND `$2260&0x10` AND NOT `$22e8&0x80` AND NOT `$22e8&0x40` | Alternate trigger: sets `$22e8\|=0x80`, `$22e9\|=0x08` |
| `[16,0e:18,10]` | (`$2260&0x10` AND `$22e9&0x08`) OR (`$22e8&0x40` AND `$2264&0x08`) | Exit north → `0x67` @ `0x0058` |
| `[14,23:19,25]` | Same gates | Exit south → `0x17` @ `0x0028` |

---

## B-trigger Zones

### `[16,0b:18,0f]` — Post-Battle Zone

**Branch 1** (NOT `$22e9&0x08` AND `$2260&0x10`):
- Flash white, load NPC `0x7e` (Strong Heart) at `(0x16, 0x15)`
- Play post-battle dialogue: Strong Heart thanks player for rescue ("I am Strong Heart, from the village of Fire Eyes...")
- After dialogue: `$22e9 |= 0x08` (gate satisfied — exits now unlock)

**Branch 2** (`$22e8&0x40` AND `$2260&0x10`):
- Set `$2264 |= 0x08` (Wheel)
- Flash white, show **"Found a Wheel"** item jingle (music `0x78` → `0x26`)

### `[16,11:18,12]` — Thraxx Weak Point

See *Thraxx Fight Mechanics* section above.

---

## External Scripts

| Opcode / Callee | Purpose |
|----------------|---------|
| `0x00` | Fade-out / stop music |
| `0x01` | Fade-in / start music |
| `0x02` | Open message box |
| `0x07` | Open message box |
| `0x0a` | Open message box |
| `0x21` | Prepare room change: south exit |
| `0x29` | Unnamed global — post-Thraxx exit |
| `0x59` | Attraction mode, after Thraxx |
| `0x93ca69` | Thraxx enter part [2] — hide body |
| `0x93ca75` | Thraxx enter part [1] — set body state |
| `0x93ca9f` | Thraxx maggot trigger part — claw animations + screen shake |
| `0x93cb12` | Thraxx enter part [4] — AOE attack cycle |
| `0x93cb65` | Thraxx enter part [5] — alternate attack cycle |
| `0x93c7f7` | Thraxx enter part [3] — random maggot spawn |
| `0x93c702` | Post-Thraxx cutscene — Strong Heart dialogue |
| `0x17bb` | NPC kill script: left claw |
| `0x17be` | NPC kill script: right claw |
| `0x17c1`–`0x17ca` | NPC kill scripts: maggots 1–4 |
| `0x17cd` | Thraxx damage/kill script |
| `0x17d0` | Alternate Thraxx kill script |
| `0x92de75` | Cinematic script |
| `0x92d7b1` | Fade to/from/flash white A |

---

## Enter Script Summary

1. Init Thraxx registers: `$285d=0`, `$286b=1`, `$286d=1`, `$287d=0`, `$287f=1`, `$2865=0`, `$2867=0`, `$249b=1`.
2. In-animation branch (standard); teleport both to `(0x17, 0x35)`.
3. Check `$22eb&0x08` (debug): skip if not set.
4. **Branch dispatch:**
   - A/B: Thraxx dead → show post-battle objects, fade in, skip.
   - C: Normal fight → load NPCs 10/11/14, spawn 4 maggots, enter timed fight loop, play music `0x04`.
   - D: Alternate fight → same as C with NPCs 84/85/86.
5. Fight loop runs until `$2834|=0x02` is set (fight over).
6. If attraction mode: run intro cinematic.
7. Write HUD registers (`$2413=0x0098`, `$2415=0x0048`).
8. Call cinematic script `0x92de75`.

---

## Notes

- **Thraxx** is the first boss of Act 1 (Prehistoria). This room contains the complete fight engine inline rather than as a separate combat room.
- **`$2260 bit 0x10` (Thraxx dead)** is set by the Thraxx kill script (`0x17cd`/`0x17d0`) — not in this room's script. It propagates back to affect 0x25 (Fire Eyes' Village), 0x5b (East Jungle), 0x26 (West area), and 0x67 (Bugmuck exterior).
- **NPC `0x7e` = VILLAGER_1_8** = Strong Heart, appearing post-battle for the rescue cutscene.
- **`$22dc bit 0x08`** gates the "alternate path" enter sequences throughout Act 1 (appears in 0x16 BBM as well). Likely set when the player returns via the BBM ride route.
  - `// TODO: identify where $22dc bit 0x08 is set`
- **Wheel (`$2264 bit 0x08`)** is obtained here only in the `$22e8&0x40` path. This is presumably the "BBM ride" completion reward.
- **No sniff spots or gourds** — purely a boss encounter room.
- **Music `0x04`** = boss battle theme; only room in Act 1 that uses it.
