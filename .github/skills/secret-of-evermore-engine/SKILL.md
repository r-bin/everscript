---
name: secret-of-evermore-engine
description: Explains how the Secret of Evermore engine functions, including player/companion mechanics, enter scripts, step-on triggers, B-triggers, entity slots, and dog AI quirks.
---

# Secret of Evermore Game Engine Mechanics

Secret of Evermore runs on an engine originally derived from *Secret of Mana* (Square, 1993), but heavily refactored by Square USA. Understanding the engine's core execution loops and entity models is essential for writing bug-free scripts and custom rooms.

---

## 1. Dual-Protagonist System (Boy & Dog)

- **1 Active Player:** At any given frame, exactly one character is player-controlled.
- **Companion AI:** The non-controlled character is driven by engine AI routines:
  - When controlling the Boy, the Dog follows, sniffs out alchemy ingredients, or attacks nearby enemies according to its behavioral aggression settings.
  - When controlling the Dog, the Boy follows and attacks.
  - Pressing `SELECT` toggles active control between Boy and Dog.
- **Engine Quirk (Companion Desync):**
  - If a script teleports the Boy or loads a new room without explicitly synchronizing the companion, the Dog can spawn at coordinate `(0, 0)` or get pulled across transition boundaries inappropriately.
  - Cutscene scripts must use standard partner freeze/guard flags (`$22EB & 0x20`) during scripted sequences.

---

## 2. Room Execution & Trigger Architecture

Every room in Evermore has three primary execution pipelines:

```
Room Load
    │
    ▼
1. Enter Script ──► Sets music, camera lock, spawns NPCs/enemies, evaluates story flags
    │
    ▼
Active Gameplay Loop (Every Frame)
    ├──► 2. Step-On Triggers (Checks player coordinates against tile bounding boxes)
    └──► 3. B-Triggers (Checks player proximity + B-button press or weapon swing)
```

### 2.1 Enter Scripts
- Executed synchronously when the player transitions into a room.
- Standard tasks:
  1. Call `init_map(...)` with coordinate boundaries.
  2. Set room music: `music(MUSIC.CAVES_OF_DANGER)`.
  3. Load enemies and NPCs using sprite IDs and spawn coordinates.
  4. Branch on progression flags (e.g., if boss is defeated, skip boss cutscene and leave room in cleared state).

### 2.2 Step-On Triggers
- Defined as rectangular coordinate bounding boxes: `[x0, y0 : x1, y1]`.
- Continuously polled by the engine against player tile coordinates.
- Used for:
  - Room exits: calling `map_transition(MAP.NEXT_ROOM, ENTRANCE, DIRECTION)`.
  - Environmental traps: pit falls, quicksand, pressure plates.
  - Cutscene triggers: stepping past an invisible line starts a scripted sequence.

### 2.3 B-Triggers (Interactions)
- Activated when the player presses the **B button** facing an object, or strikes it with a weapon:
  - **Chests & Gourds:** Displays loot animation, writes persistence flag (`$2268..$22AA`), awards item/ingredient.
  - **NPC Dialogue:** Pauses player movement, displays text dialog window via string keys.
  - **Sniff Spots:** When the Dog's nose animates near a sniff coordinate, pressing B digs up hidden alchemy ingredients.
  - **Obstacles:** Striking an axe-barrier or spear-post checks current weapon (`$235F` / `$2360`) and clears obstacle tiles if criteria are met.

---

## 3. Entity Tables & Enemy Spawning

- The engine maintains a fixed table of active sprite/entity slots in WRAM (`$7E1000..$7E1FFF`).
- When loading an enemy:
  - Sprite graphic patterns are loaded into VRAM.
  - Hitbox definitions, HP, attack power, and AI routine pointers are assigned.
  - Three prize slots are loaded: drop item 1, drop item 2, drop item 3, along with their respective drop rates and quantities.
- An engine hook system at `$0EAC` tracks 3 active slots (offsets `+0`, `+4`, `+8`) in every room that manages enemy instances.
