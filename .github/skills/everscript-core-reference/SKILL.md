---
name: everscript-core-reference
description: Explains the structure and contents of in/core/, the authoritative library of Secret of Evermore constants, enums, addresses, and built-in functions.
---

# Everscript Core Reference (`in/core/`)

The directory [in/core/](file:///Users/v/Documents/GitHub/everscript/in/core/) is the authoritative foundation of the Everscript ecosystem. It provides the symbolic vocabulary for all game scripts: every named memory address, ROM entrance, music track, enemy sprite, alchemy formula, and helper function is defined here.

---

## 1. Directory Structure

The master include file [in/core/main.evs](file:///Users/v/Documents/GitHub/everscript/in/core/main.evs) loads two major subsystems:

```
in/core/
├── main.evs
├── [group] 00_general_enums/
│   ├── 01_rom.evs                     # ROM injection addresses & entry points
│   ├── 02_ram.evs                     # WRAM labels: stats, currencies, flags
│   ├── 03_snes.evs                    # SNES hardware registers (PPU, DMA, joypad)
│   ├── 04_debug_helper.evs            # Debug triggers & coordinate overrides
│   └── [group] 05_everscript/         # High-level entity enumerations
│       ├── 00_map.evs                 # Map IDs & entrance enums
│       ├── 01_dialog.evs              # Dialog window positions & styles
│       ├── 02_audio.evs               # MUSIC and SFX audio track IDs
│       ├── 03_sprites.evs             # ENEMY and NPC sprite IDs
│       ├── 04_items.evs               # Consumables, key items, weapon IDs
│       ├── 05_projectile.evs          # Spells, arrows, bombs, boss projectiles
│       ├── 06_alchemy.evs             # Alchemy spells & ingredient requirements
│       ├── 07_animation.evs           # Character animations & pose IDs
│       └── 08_ring_menus.evs          # Ring menu item placements & layouts
│
└── [group] 02_functions/              # Built-in compiler and engine functions
    ├── 00_system.evs                  # Core engine lifecycle & sleep loops
    ├── 03_cutscene_helper.evs         # Camera panning, partner guards, fades
    ├── 07_debug_helper.evs            # Debugging hotkeys and practice hooks
    ├── 09_experimental.evs            # Prototype routines and advanced hooks
    └── [group] 02_everscript_commands/# Script interpreter wrappers (audio, map, items)
```

---

## 2. Key Enums & Namespaces

### 2.1 `enum ADDRESS` (`01_rom.evs`)
Defines ROM locations used for `@inject(ADDRESS.X)` hooks:
- `INTRO_START_PRESSED`: Title screen Start button hook.
- `SOUTH_JUNGLE_ENTER`: Prehistoria entrance script address.
- `FE_EXIT_NORTH`: Fire Eyes village exit trigger.

### 2.2 `enum MEMORY` & `MEMORY_TYPE` (`02_ram.evs`)
Symbolic labels for WRAM addresses:
- `BOY_MAX_HP = <0x0A35>`
- `DOG_MAX_HP = <0x0A7F>`
- `TALONS = <0x0AC6>`, `JEWELS = <0x0AC9>`, `GOLD = <0x0ACC>`, `CREDITS = <0x0ACF>`
- `CURRENT_WEAPON_TYPE = <0x2360>`

### 2.3 Entity Enums (`[group] 05_everscript/`)
- `enum MUSIC`: Symbolic names for audio tracks (e.g. `CAVES_OF_DANGER`, `BOSS_BATTLE`).
- `enum ENEMY`: Sprite IDs for enemies and NPCs.
- `enum ITEM`: Item IDs for consumables (Petals, Nectar), Key Items (Diamond Eye, Wheel), and Armor.

---

## 3. Strict Rules for Working with `in/core/`

1. **Skip `[CUSTOM]` Entries for Vanilla Analysis:**
   - Any constant tagged with `[CUSTOM]` is a romhack modification created for Kaizo or Practice Hack. Never use `[CUSTOM]` entries as evidence for vanilla ROM mechanics.
2. **Never Invent Names:**
   - When referencing game data in your scripts, if a constant does not exist in `in/core/`, do not guess. Look up the raw hex value in `.github/memory-map.md` or the script dump.
3. **Adding New Symbols:**
   - If you identify an unmapped vanilla constant through reverse-engineering, propose adding it to the appropriate sub-module with documentation of its source.
