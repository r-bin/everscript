# Script Analysis — Patterns & Global Reference

This file documents cross-cutting patterns, shared flags, and open questions discovered during room analysis.
Update it whenever a pattern is confirmed in 2+ rooms.

---

## Global TODOs

- [ ] Identify ENEMY enum names for all sprite IDs still listed as `?` in room docs (run grep `ENEMY` in `in/core.evs`)
- [ ] Investigate `$0eac` hook slot system — 3 slots (offsets +0, +4, +8) set in every room that loads enemies; map what each slot does
- [ ] Confirm what `$22eb&0x01` does — present in the memory-map entry but never observed set or tested in any room doc so far
- [ ] Map `$22b5–$22d2` (30-byte gap, still unmapped) — probably sniff spots for rooms not yet analyzed
- [ ] Confirm `$225d&0x08` = MARKET_TIMER_EXPIRED vs other meanings in Prehistoria (flag byte is shared)
- [ ] Verify NPC type `0x2a` dual-use: Mammoth Viper Commander in [0x3b] vs WindWalker NPC in [0x36] — same sprite ID used for two unrelated NPCs?
- [ ] Confirm what `$22d9&0x08` does in [0x36] when `$237d==1` (gates OBJ 2 state=1); suspected Aegis dead but not verified for Prehistoria context
- [ ] Room [0x3b]: identify NPC types `0x3c` and `0x3e` by ENEMY enum — currently labelled by raw sprite ID only
- [ ] Room [0x3b]: NPC `0x3e` talk scripts `0x17fa/0x17fd/0x1800` — read and summarize
- [ ] Rooms [0x5c, 0x16, 0x18, ...]: drop tables use emojis but readability varies — standardize
- [ ] All rooms using memory-map emoji format in Memory Access table — reformat to spec (see Format Conformance below)

---

## World State: Act 1 Progression Flags

Flags that permanently change the game world. Listed in approximate chronological order.

| Flag | Meaning | Set in | Read in |
|------|---------|--------|---------|
| `$225f & 0x40` | RAPTORS defeated | [0x5c] exit step-on | [0x25] north/east exits, [0x38] north exit |
| `$2260 & 0x10` | THRAXX dead | [0x18] boss kill | [0x26] Defend guy, [0x5b] Skelesnail spawner |
| `$228b & 0x01` | FE permission granted (visited pre-Thraxx) | [0x51] enter | [0x25] east exit guard, [0x51] various exits |
| `$22dc & 0x08` | WindWalker unlocked | [0x52] top of volcano | [0x16] [0x18] [0x36] [0x3b] [0x52] [0x66] [0x69] — 7 rooms |
| `$2260 & 0x40` | MAGMAR dead (Act 1 boss) | [0x3f] boss kill | [0x3f] south exit step-on |
| `$22f1 & 0x40` | OUTRO active (Act 1 ending) | [0x25] outro branch | [0x36] [0x59] [0x69] |

### Note on `$22dc&0x08` (WindWalker)
The most widely-read story flag in Act 1. It appears in 7 rooms and consistently:
- Skips all enemy spawners (enemies disappear once WW unlocked)
- Changes object states (e.g. [0x3b] obj 0x25 state=1 — probably a path-clearing object)
- Branches music and NPC behavior

---

## Cross-Room Handoff Flags

Flags SET in one room and READ in a different room to coordinate transitions.

| Flag | Set in | Read in | Purpose |
|------|--------|---------|---------|
| `$225e & 0x40` | [0x3c] exit step-on `[0f,45:11,47]` | [0x3b] enter | Spawn Viper Commander on re-entry |
| `$22eb & 0x20` | every indoor or cutscene room before CHANGE MAP | destination room enter | Animation-skip guard — skip entry teleport if already mid-animation |
| `$22eb & 0x10` | [0x5b] east step-on, [0x67] north step-on | [0x59] enter | Marks which edge the player entered the desert from |
| `$22eb & 0x40` | [0x0a] inn step-ons | [inn room] enter | Trigger special entry animation at inn |
| `$22ec & 0x40` | [0x0a] inn step-on (south door) | [inn room] enter | Variant of inn entry |
| `$22ec & 0x08` | [0x52] | [0x69] | Descending from Top of Volcano (triggers descent cinematic) |
| `$22ec & 0x10` | [0x52] step-on `[0f,0c:11,0d]` | [0x69] enter | Same descent handoff flag |
| `$22ee & 0x01` | [0x52] outro branch; [0x51] FE→hut | [0x3c] [0x3e] [0x50] enter | Intro/outro flag from Prof. Lab; teleports to alternate entry point |
| `$22f1 & 0x40` | [0x25] outro cutscene | [0x36] [0x59] [0x69] | Act 1 outro active |
| `$22f3 & 0x08` | [0x0a] desert step-on | [0x1b?] | Entering market from north end |
| `$22ed & 0x08` | [0x6a] waterfall cutscene | [0x68] enter | Trigger Crustacia intro |
| `$22e5 & 0x08` | WW landing sequence (overworld) | [0x36] enter | WindWalker landing |
| `$2355` (word) | [0x36] outro | [0x36] | WW fire pit phase: 1=first, 2=second |
| `$237d` (word) | [0x36] | [0x36] [0x5b] | WW destination state: 0/1=fire pit, 4=Omnitopia |
| `$234b` (word) | FAKE_HOUSE_ID: [0x25] sets 1–8 | [0x51] enter | Which hut the player entered |
| `$22f2 & 0x02` | [0x65] west exit step-on | [0x66] enter | Leafpad activated |

---

## Sniff Flag Organization

**No sniff flags are reused across rooms.** 193 unique sniff bits documented in Act 1. Each room owns a unique contiguous address range.

Known sniff flag address ranges by room:

| Room | Addresses | Count |
|------|-----------|-------|
| [0x38] South Jungle / Start | `$2268&0x40`, `$2268&0x80` | 2 |
| [0x26] West area with Defend | `$2268&0x02/0x04/0x08` | 3 |
| [0x5b] East Jungle | `$2294`, `$2295`, `$2296` | 13 |
| [0x67] Bugmuck Exterior | (unknown range) | ? |
| [0x65] Swamp Main | (unknown range) | ? |
| [0x3e] Pipe Side Rooms | `$22b0&0x40/0x80`, `$22b1` bits 0–6 | 9 |
| [0x3b] Volcano Room 2 | `$22ab&0x80`, `$22ac`, `$22ad`, `$22ae` | 25 |
| [0x36] Fire Pits | `$22d3&0x04/0x08/0x10/0x20` | 4 |

---

## Shared External Scripts

Scripts called from 2 or more rooms. These are engine utilities, not room-specific logic.

| Address | Purpose | Rooms |
|---------|---------|-------|
| `0x92de75` | Cinematic helper — stops player, sets camera, etc. | [0x25] [0x33] [0x34] [0x38] [0x51] [0x5c] |
| `0x94c1c5` | Fire Eyes village gathering cutscene (Pt 1) | [0x25] [0x51] |
| `0x92cc2b` | ABS script (purpose unknown) | [0x25] [0x5c] |
| `0x92d92a` | Outro rain and sky color | [0x36] |
| `0x94b4ce` | Magmar intro cutscene | [0x3f] [0x3e] (attract mode) |
| `0x94e8df` | WindWalker landing animation | [0x53] |
| `0x94e9d8` | WindWalker flight animation | [0x53] |
| `0x94e7e1` | Waterfall fall animation | [0x6a] |
| `0x92dc1b` | WindWalker second fire pit handler | [0x36] |
| `0x97c756` / `0x97c760` | WW flight sequence bookkeeping | [0x36] |

---

## Common Engine Patterns

### 1. Animation-skip guard (`$22eb & 0x20`)
**Used in:** [0x16] [0x17] [0x18] [0x26] [0x3d] [0x3f] [0x53] [0x59] [0x5b] [0x67] [0x6a] — 11+ rooms

Pattern: the very first thing in every enter script:
```
IF $22eb & 0x20: (already in animation — skip teleport, just continue)
ELSE: teleport boy+dog to default entry position; clear $22eb&0x20
```
Set by the *previous* room before CHANGE MAP when the transition is part of a cutscene or indoor→outdoor animation. The destination room detects this and skips the "arriving from outside" animation.

### 2. INTRO_DEMO_MODE (`$22eb & 0x04`)
**Used in:** [0x0a] [0x16] [0x18] [0x3f] [0x5b]

When set on game startup (attract mode), certain rooms randomize their visual state (`$236b`) or play their intro cutscene automatically without player input. Used for the title screen demo loop.

### 3. DEBUG flag (`$22eb & 0x08`)
**Used in:** [0x18] [0x25] [0x36]

| Room | Effect when `$22eb & 0x08` is set |
|------|----------------------------------|
| [0x36] Both Fire Pits | Forces `$22f1\|=0x40` (outro active) + `$22dc\|=0x08` (WindWalker unlocked) — instant Act 1 ending skip |
| [0x18] Thraxx Room | Skips a conditional check (exact effect not fully documented) |
| [0x25] Fire Eyes Village | Triggers debug teleport branch (`$238f = 0x0000`); skips normal entry |

// TODO: Read [0x18] Thraxx debug branch fully. Read [0x25] debug teleport target.

### 4. PACIFIED / `$23bf`
**Used in:** [0x16] [0x17] [0x18] [0x59] [0x5b] [0x67]

Written `0x0000` in these rooms. Purpose: likely disables random enemy aggression or a specific combat flag. Always written at enter, never read in any documented room.

### 5. UNKNOWN_1 / `$23c1`
**Used in:** [0x17] [0x59] [0x67]

Written `0x0001`. Appears alongside sandpits, Bugmuck exterior, quicksand desert. May control some environmental hazard behavior.

### 6. Enemy hook slots (`$0eac`)
**Used in:** [0x59] [0x5b] [0x67]

Three hook addresses at `$0eac+0`, `$0eac+4`, `$0eac+8`. Each written to a script address before enemy spawners are loaded. Likely callbacks for enemy AI or arena events. // TODO: reverse-engineer hook system.

### 7. CHANGE MAP with spawn offset notation
Step-ons use `@ [X|Y]` format: X=pixel X spawn, Y=pixel Y spawn in destination room.
Example: `0x25 @ [0x0098|0x0380]` = Fire Eyes Village, spawn at pixel (0x98, 0x380).

### 8. Prize / drop table
Set in enter script before enemy spawners load. Always uses three slots:
- `PRIZE_RATE_1/2/3` (`$239b/$239d/$239f`) — drop probability thresholds
- `PRIZE_DROP_1/2/3` (`$23a1/$23a3/$23a5`) — item IDs
- `PRIZE_QUANTITY_1/2/3` (`$23a7/$23a9/$23ab`) — amounts

---

## Gated Passages (Story Flags → Blocked / Conditional Exits)

| Room | Exit | Condition | Behavior when blocked |
|------|------|-----------|----------------------|
| [0x25] FE Village | East (to quicksand) | `$228b & 0x01` must be set | Guard NPC pushes player back with dialog: *"No humans or dogs allowed…"* |
| [0x25] FE Village | North / East | `$225f & 0x40` (RAPTORS) + `$2260 & 0x10` (THRAXX) | Step-on is conditional; nudges player back if preconditions not met |
| [0x38] South Jungle | North | `$225f & 0x40` (RAPTORS) | If set → 0x25 Village; if clear → 0x5c Raptors |
| [0x3f] Boss Room | South | `$2260 & 0x40` (MAGMAR dead) | Step-on zone only activates after boss kill |
| [0x0a] Market | East (boss-fight) | `$225f & 0x20` (Vigor defeated) | If clear → 0x09 Square during Aegis fight; if set → 0x08 normal Square |
| [0x52] Top of Volcano | (WW path) | `$22dc & 0x08` (WW unlocked) | Different cutscene plays; CHANGE MAP goes to 0x69 instead of staying |

---

## Weapon-Gated Passages (Metroidvania Barriers)

Certain B-triggers and step-ons read `CURRENT_WEAPON` (`$235f`) or `CURRENT_WEAPON_TYPE` (`$2360`) to prevent access unless the player has obtained or equipped a specific weapon. These are intentional progression gates — never mistake them for alchemy checks.

The raw comparison values in the dump are **decimal**. Translate them using the `WEAPON_INDEX` and `WEAPON_TYPE` enums in `in/core.evs`; do not hardcode the tables here.

**Known weapon gates by room:**

| Room | Mechanism | Requirement | Notes |
|------|-----------|-------------|-------|
| [0x55] 'mids Bottom | Lotus Bridge switch B-triggers #19–23 | CURRENT_WEAPON ≥ 0x12 (SPEAR_1 / Horn Spear) | Frees dog if all 5 pressed in sequence |
| [0x56] 'mids Top | Floor switch B-trigger #24 | CURRENT_WEAPON ≥ 0x12 (SPEAR_1) | Opens platform element |
| [0x57] 'mids Basement | Rock wall B-triggers #9/10/11 | WEAPON_INDEX 0x0c–0x10 (AXE_2 / Bronze Axe – AXE_4) | 3 walls; B-trigger #1 requires 0x0e–0x10 (AXE_3+) |
| [0x29] Halls Main | Spear switch step-on | CURRENT_WEAPON_TYPE == 0x04 (SPEAR) | Opens boss door; no level check |

// TODO: audit all rooms for `$235f`/`$2360` checks and add to this table.

---

## WindWalker — What It Is and How It Works

The **WindWalker** is a flying machine (not an alchemy spell). It is constructed/activated mid-Act 1 and enables flight between regions.

- **Unlock flag:** `$22dc&0x08` — set at the top of the volcano [0x52]. Once set, persists for the rest of the game.
- **Effect in 7 rooms** ([0x16] [0x18] [0x36] [0x3b] [0x52] [0x66] [0x69]): enemies despawn, alternate music, new paths open.
- **Flight sequence:** scripted via `0x94e8df` (landing animation) and `0x94e9d8` (flight animation); bookkeeping via `0x97c756` / `0x97c760` in [0x36].
- **Fire pit state:** `$2355` (word) tracks which fire pit the WW is positioned at: 1 = first, 2 = second.
- **Destination:** `$237d` (word): 0/1 = fire pit, 4 = Omnitopia portal.
- **Route:** [0x36] Both Fire Pits → [0x69] Volcano Overworld → [0x52] Top of Volcano → Act 2/3.

**Do NOT confuse with:**
- **Levitate** — an alchemy spell that briefly floats the character; separate mechanic, not `$22dc&0x08`.
- `$22e2&0x80` in [0x57] — tracks WindWalker obstacles removed in that room specifically (local flag, not the global WW unlock).

---

## `$22eb&0x20` — Animation-Skip Guard (Better Name Discussion)

**Current label:** `IN_ANIMATION` / animation-skip guard.
**Documented in:** Common Engine Patterns section above (Pattern #1).

This flag is more precisely a "cutscene transition in progress" guard. It tells the destination room to skip its normal entry teleport because the player is already mid-animation. Renaming candidates:
- `ANIM_TRANSITION` — transition mid-animation
- `SKIP_ENTRY_TELEPORT` — functional description
- `IN_CUTSCENE_TRANSITION` — broader semantic

Current usage is consistent across 11+ rooms. Until a rename is confirmed, always document it as `IN_ANIMATION` per the memory-map existing label.

---

## Act Progression: Boss Kills → Story Flags → World Changes

Each major boss kill sets a story flag that permanently alters traversal, spawns, and music across multiple rooms.

| Boss | Kill flag | Rooms affected | Key changes |
|------|-----------|----------------|-------------|
| RAPTORS | `$225f&0x40` | [0x25] [0x38] | NE exit to quicksand opens; Thraxx door guard changes |
| THRAXX | `$2260&0x10` | [0x26] [0x5b] | Defend NPC changes dialogue; Skelesnail spawner despawns |
| MAGMAR | `$2260&0x40` | [0x3f] | South exit step-on activates |
| WindWalker obtained | `$22dc&0x08` | [0x16] [0x18] [0x36] [0x3b] [0x52] [0x66] [0x69] | 7 rooms: all enemies despawn, music/NPC changes |
| Megatuar | `$22d8&0x80` | [varies] | // TODO: identify rooms that read this flag |
| Aquagoth | (no persistence flag written in kill script) | [0x6c→0x6d] | Bucket ride + CHANGE MAP to 0x6c; `$22ed&0x08` triggers Crustacia intro |

**Chain:** RAPTORS + THRAXX → WW obtainable → MAGMAR → Act 1 ends → Act 2 begins.

// TODO: map Act 2 + Act 3 boss kill chains. Document which flags are read in which rooms to control world state.

---

## Desert Wrap-Around Mechanics

The quicksand desert [0x59] uses a tile-overflow counter system to simulate an infinite looping desert.

- `$22fc` — Y counter (increments as player walks north, wraps at threshold)
- `$22fd` — X counter (increments as player walks east, wraps at threshold)
- `$22eb&0x10` — set by [0x5b] east step-on or [0x67] north step-on: marks which edge the player entered from (east or north)
- **Exit north:** after enough wraps, exits to [0x0a] Nobilia Market
- **Exit east:** wraps back from [0x59] west edge; eventually exits east to [0x59] east neighbor

// TODO: document exact wrap thresholds and exit conditions from script dump for [0x59].

---

## Weird Gourds and Sniff Spots

Unusual persistence flags or shared-byte situations worth flagging.

| Room | Flag | Issue |
|------|------|-------|
| [0x06] Outside of 'mids | `$22ba&0x01` | Used by river/ferry object, NOT a sniff spot. The nearby rooms [0x2b] Outside of Halls and [0x2f] Horace's Camp use `$22ba` for sniff spots starting at bit 0x02 — bit 0x01 is reserved for the ferry object. |
| [0x4b] Oglin Cave | `$2287&0x40` | Call Beads gourd — same byte as 0x12 Ebon Keep sewer gourds (`$2287&0x01/0x02`); byte is shared across two rooms. |
| [0x55] 'mids Bottom | `$227c–$227e` + `$2834` | `$2834` bits 0x01–0x20 are WRAM switch flags (session-local); do NOT confuse with the `$227c–$227e` SRAM gourd persistence flags in the same room. |
| [0x58] 'mids Boss (Rimsala) | `$2834` | WRAM session-local crystal-alive flags; same address used by [0x55] switch flags but different sessions — no actual conflict since both clear on entry. |
| All candle-light spots [0x12] | (no persistence) | Candle-light B-triggers in 0x12 have no gourd/sniff persistence flag — they call a lighting sub and reveal OBJ state each visit. Not collected once and gone. |

---

## Format Conformance

Tracks which room docs use non-spec formats that need updating.

### Memory Access table format
**Spec format** (required):
```
| Address | core.evs Name | Size | Op | Section | Notes |
```

Rooms using the **memory-map emoji format** instead (`| Address | Bit | Type | Description |`):
- [0x3b] Volcano Room 2
- [0x3e] Side Rooms Pipe Maze
- [0x36] Both Fire Pits
- [0x3f] Volcano Boss Room
- [0x53] Act 2 Start Cutscene
- [0x6a] Act 2 Start Cutscene Waterfall
- [0x0a] Nobilia Market (uses `| Address | Bits | Name | R/W | Meaning |`)

Rooms using a hybrid format with emojis as category:
- [0x5b] East Jungle (`| Address | Bits | Category | R/W | Meaning |`)

### NPC/Enemy identification
Rooms that identify enemies by raw sprite ID instead of ENEMY enum name:
- [0x3b]: `NPC 0x3c`, `NPC 0x3e`, `NPC 0x2a`, `NPC 0x29` — all need ENEMY enum lookup
- [0x0a]: 18 NPCs identified by raw type IDs `0x18–0x1c`, `0x62`, `0x8c`

### Combined NPC/Enemy sections
Spec requires separate `## Enemies` and `## NPCs` sections. Rooms with combined `## NPCs / Enemies`:
- [0x3b] Volcano Room 2

### Unconfirmed names (invented)
- [0x3f]: "Alma" and "evil twin" — not in ENEMY enum, guessed from dialog. Mark as `// ?` or remove.
