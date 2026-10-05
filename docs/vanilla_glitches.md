# Secret of Evermore: Vanilla Glitches & Engine Exploits

This document catalogs notable mechanical glitches, memory oversights, and engine exploits present in the unpatched vanilla release of *Secret of Evermore* (specifically NTSC-U). Each entry details the underlying memory mechanics, engine routines involved, reproduction steps, and their impact on speedruns and ROM hacking.

---

## 1. Summary of Documented Glitches

| Glitch / Exploit | Memory / Subsystem | Primary Mechanism | Impact |
|---|---|---|---|
| **Atlas Attack Underflow** | WRAM `$7E0A47`, `$7E1000` | Mismatched subtraction on death: subtracts `frames_till_next_poison_tick` instead of `atlas_boost` | Boy's attack stat underflows past `0` to `~65,535` |
| **Permanent Status Effects (>4 Buffs)** | WRAM `$7E1000` status slots | Slot eviction without cleanup when applying 5+ status effects | Buffs, shields, and stat boosts never expire |
| **Script Interruption on Room Exit** | Script VM, Step-on triggers, Player input lock | Touching an exit trigger does not instantly lock player input; frame-perfect script activation gets aborted | Breaks story cutscenes; leaves transient flags (e.g. Dog noclip) set |
| **NTSC Bazooka Ammo Count Glitch** | WRAM `$2437` / Ammo registers | Missing decrement instructions for green/blue ammo types | Infinite Heavy Shells (green) & Particle Shells (blue) |
| **AI Companion Trigger Leashing** | Entity coordinates, Trigger evaluation | Pathfinding companion across trigger boundaries while inactive | Bypasses character-specific step-on triggers / event barriers |
| **Wings "Does Not Work Here" Invincibility** | Character invulnerability flags | Error exit path displays message but forgets to clear invincibility bit | Permanent invincibility against damage until map change/death |
| **Loot Quantity Multiplication Glitch** | WRAM `LOOT_AMOUNT` (`$2461`) | Stale quantity value in `$2461` reused by subsequent pickups | Duplicates ingredient and gourd yields (e.g. ×2 to ×4) |

---

## 2. Deep-Dive Glitch Breakdown

### 2.1 Atlas Attack Underflow (Boy's Attack Wrap to ~65,535)

#### Technical Mechanism:
- **Stat Boost Application:** When Atlas is cast, the engine calculates the attack boost based on the alchemy formula level and adds it to the Boy's active attack stat (`$7E0A47`):
  $$\text{Attack} \leftarrow \text{Attack} + \text{atlas\_boost}$$
- **The Death Cleanup Indexing Bug:** When the Boy dies while afflicted with status effects, the engine's death cleanup routine attempts to reverse pending stat buffs. However, due to an indexing error in how status effect slots are handled:
  - If **Poison** resides in Status Slot 0, the engine erroneously reads Slot 0's timer—which represents `frames_till_next_poison_tick`—instead of the stored `atlas_boost` value!
  - It then subtracts this timer value from the Boy's attack stat:
    $$\text{Attack} \leftarrow \text{Attack} - \text{frames\_till\_next\_poison\_tick}$$
  - When dying (or upon resurrection when base attack is low or reinitialized), if $\text{Attack} < \text{frames\_till\_next\_poison\_tick}$, the 16-bit unsigned subtraction underflows past `0x0000` to `0xFFFF - delta` (yielding **60,000+ attack**).
- **Result:** The Boy permanently deals maximum damage, one-shotting virtually every enemy and boss in the game.

#### Exploitation Strategies:
1. **Pixie Dust + Poison + Atlas + Death:**
   - Put **Poison** in Slot 0 (by getting poisoned before casting buffs).
   - Apply **Pixie Dust** (for auto-revive) and cast **Atlas** (granting `+atlas_boost`).
   - Allow poison damage or enemy attacks to kill the Boy.
   - Upon death, the game subtracts `frames_till_next_poison_tick` instead of `atlas_boost`, causing the 16-bit underflow. Pixie Dust instantly revives the Boy with maximum attack power.
2. **Atlas + 4 Other Status Effects (Slot Eviction):**
   - Apply Atlas followed by 4 distinct other buffs/status effects (e.g., Defend, Speed, Barrier, Forcefield).
   - The 5th status effect overwrites Atlas in the 4 active status slots. When recalculation or expiration occurs with corrupted slot pointers, the attack subtraction desynchronizes from the original boost, driving the attack stat into underflow.

> [!NOTE]
> The repository includes a targeted assembly fix in [**`patches/five_status_effects_fix.asm`**](file:///Users/v/Documents/GitHub/everscript/patches/five_status_effects_fix.asm), which properly isolates slot cleanup and prevents lingering boost subtractions.

---

### 2.2 Permanent Status Effects (>4 Status Effects Overwrite)

#### Technical Mechanism:
- The engine allocates exactly **4 status effect slots** per playable entity in WRAM (`!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_1` through `_4`).
- Each slot tracks the active status ID, its remaining duration timer, and associated visual outline flags.
- **The Bug:** When a 5th status effect is applied, the engine does not prevent the application, nor does it properly retire the oldest status effect. Instead, it clobbers an existing slot.
- **The Result:** The status effect that was displaced no longer has an active timer in any of the 4 slots. Because the expiration routine only checks the 4 tracked slots, the displaced status effect **never triggers an expiration check**. Its attribute bits (e.g. Barrier invulnerability, Forcefield defense, or Speed buffs) remain active indefinitely until room reload or character death.

---

### 2.3 Script Interruption on Room Exit & Dog Noclip

#### Technical Mechanism:
- **Delayed Input Lock on Exit:** In vanilla Secret of Evermore, touching a room exit trigger (step-on transition) does **not** instantly freeze player movement or lock controller input. There is a multi-frame window during the transition initiation before the screen fade-out and room reload occur.
- **Frame-Perfect Script Interruption:** Because the player can still act during this transition window, it is possible to hit an exit trigger and then **frame-perfectly activate another script** (such as stepping on a story-progressing cutscene trigger, talking to an NPC, or activating a boss trigger).
- **Aborting the Story Script:** When the engine completes the room transition, the active Script VM thread is aborted immediately:
  - Any movement locks or cutscene locks intended to hold the player are bypassed.
  - Partial story state flags may be written while subsequent cleanup instructions are skipped, creating major sequence breaks in story progression.

#### The Dog Noclip Exploit:
- Certain in-game cutscenes or scripted events temporarily grant the Dog (or Boy) the **noclip** attribute bit (ignoring collision geometry via Opcode `0xA9` or direct entity writes) to allow automated pathfinding through walls.
- Normally, the script clears this bit before returning control to the player.
- **The Glitch:** If the player triggers a room transition while a script has enabled noclip for the Dog, the script VM terminates upon leaving the room before executing the clearance instruction.
- **Impact:** The Dog enters the new map with the noclip attribute still active in WRAM (`$7E1100`), allowing the companion to run freely through walls, trees, chasm barriers, and solid geometry.

---

### 2.4 NTSC Bazooka Ammo Decrement Oversight

#### Technical Mechanism:
- The Bazooka supports three ammunition types:
  1. **Red Shells:** Standard Explosive Shells
  2. **Green Shells:** Heavy Shells (Thunderball)
  3. **Blue Shells:** Particle Shells (Cryo-Blast)
- **The Bug:** In the North American NTSC-U release, the weapon firing handler correctly decrements the inventory byte for Red Shells, but omits the decrement branch for Green and Blue ammunition.
- **Impact:** Firing Green and Blue shells consumes zero ammunition, granting infinite shots as long as the player has at least 1 shell of that type in inventory. (Corrected in PAL releases).

---

### 2.5 AI Companion "Trigger Leashing"

#### Technical Mechanism:
- **Trigger Bounds Logic:** In-game event triggers (step-on and boundary triggers at `$1064`) check coordinates against the active entity or player controlled character (`$8FACCE..$8FAD08`).
- **AI Pathfinding Quirks:** When controlling one character, the inactive character follows via engine AI.
- **The Exploit:** By positioning the active character outside a trigger boundary and directing the AI companion across the threshold (or switching characters while holding directional input), the companion can traverse past puzzle switches, barrier gates, or boss encounter triggers without activating them.
- This allows setting up boss arena positions, sequence-breaking barrier doors, or retrieving out-of-reach items without tripping room events.

---

### 2.6 Wings "Does Not Work Here" Invincibility

#### Technical Mechanism:
- **Pre-Execution Setup:** Activating the Wings item from the ring menu initiates an escape sequence that immediately marks the party entities with an invulnerability / invincibility flag to prevent dying during the teleport fade-out.
- **Error Branch:** If the Wings are activated in a restricted zone (e.g. boss rooms, certain indoor chambers, or non-teleportable areas), the engine branches to an error handler that shows the message box *"Does not work here"*.
- **The Bug:** The error routine fails to clear the invulnerability flag that was applied at the start of the sequence.
- **Impact:** The player becomes completely immune to enemy damage and knockback for the remainder of the session (cleared only upon map reloading or saving).

---

### 2.7 Loot Quantity Multiplication Glitch (`LOOT_AMOUNT` `$2461`)

#### Technical Mechanism:
- **Shared Quantity Register:** When an enemy drops multiple items (enemy remains) or a high-value chest opens, the engine writes the reward multiplier to WRAM **`LOOT_AMOUNT` (`$2461`)**.
- **Timing Window:** `$2461` is a temporary register that is expected to be consumed and cleared by the immediate pickup routine. However, there is a latency window of approximately **0.5 seconds** (several frames) before the register is reset.
- **The Exploit:** If the player collects multi-item enemy remains (or a gourd that sets `$2461 > 1`) and immediately collects an ingredient spot or gourd that defaults to a quantity of 1 within that half-second window, the second pickup reads the stale value sitting in `$2461`.
- **Impact:** The player receives the higher quantity for the second item (e.g. obtaining 2–4 rare ingredients or gourd items from a spot intended to yield only 1).

---

## 3. Preservation & ROM Hacking Policy

- **Vanilla Tracking:** These quirks are part of the original SNES binary behavior. When writing new scripts or designing Kaizo challenges in `in/kaizo/`, agents and developers must distinguish these known vanilla behaviors from new compilation regressions (see [**`vanilla_bugs_and_oddities.md`**](file:///Users/v/Documents/GitHub/everscript/vanilla_bugs_and_oddities.md)).
- **Speedrunning Relevance:** Many of these exploits (Atlas underflow, Wings invincibility, dog noclip, script interruption) form the core backbone of vanilla Any% and low-level speedrun routes.
