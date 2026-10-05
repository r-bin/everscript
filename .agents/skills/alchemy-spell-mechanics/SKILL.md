---
name: alchemy-spell-mechanics
description: Explains the Secret of Evermore alchemy formula subsystem, ROM master tables ($C4), animation bytecode VM ($90), damage/heal/buff math, status timers, and spell adding feasibility.
---

# Alchemy & Spell Mechanics in Secret of Evermore

This skill provides an authoritative operational reference for reverse-engineering, modifying, or balancing Alchemy formulas in Secret of Evermore. Detailed reference tables and decompiled scripts live in [`docs/alchemy_system_and_spell_mechanics.md`](file:///Users/v/Documents/GitHub/everscript/docs/alchemy_system_and_spell_mechanics.md).

---

## 1. Core Architecture & Pipeline

```
1. Ring Menu Selection
   - Icon ID (e.g. 0x004E ALCHEMY_DEFEND)
   - Lookup at $8E:8000 -> Item descriptor at $8E:827C -> Alchemy Index (0x0E)
2. Cost & Target Validation
   - Cost table at $C4:601F checked against WRAM inventory ($7E22FF+X)
   - Target flags loaded from $C4:5BF5 (e.g. 0x0008 BOY_DOG_BOTH, 0x2010 ENEMY_ALL)
3. Cast Execution & Spell Power Calculation ($91:CCD8)
   - Deducts ingredients from $7E22FF+X and increments usage stat at $7E2FDE+X
   - Adds experience to $7E2F52+X using table $C4:5B9C (10 XP at Lv0 down to 1 XP at Lv6+)
   - Gross Power = Base Power ($C4:5E6B) * Level Multiplier ($C4:5BA5)
   - Divided Power = Gross Power / (Target_Count + 1)
   - Random Variance: Final Power = 50% min + RNG(0 .. 50% Divided Power)
   - Allocates animation slot ($7E3364..$7E3563) and stores Final Power at offset +$2A
4. Animation VM & Effect Resolution ($90:80CE)
   - Interprets bytecode script in Bank $C9 or $91
   - Drives OAM sprite frames (e.g. Defend ring 0xCF:0x36CF)
   - Invokes effect handler: damage ($91:9C90), healing ($91:9D16), or status buff ($91:B137)
```

---

## 2. ROM Master Tables (Bank `$C4`)

All 35 vanilla formulas share a common index (`0x00` to `0x44`, step 2):

| Table Name | ROM Address | SNES Address | Size | Description |
|---|---|---|---|---|
| `ALCHEMY_TARGET` | `0x045BF5` | `$C4:5BF5` | 35 words | Target cursor bitfield (`BOY`, `PARTY`, `ENEMY_ALL`, etc.). |
| `ALCHEMY_LEARNED_ADDR` | `0x045C3B` | `$C4:5C3B` | 35 words | Target WRAM persistence byte address (`$2258`..`$225C`). |
| `ALCHEMY_LEARNED_MASK` | `0x045C81` | `$C4:5C81` | 35 bytes | Bitmask within persistence byte (`0x01`..`0x80`). |
| `ALCHEMY_ANIM_MAP` | `0x045DDF` | `$C4:5DDF` | 35 words | Animation sequence ID index into `$91:80A6`. |
| `ALCHEMY_POWER` | `0x045E6B` | `$C4:5E6B` | 35 words | Base power (0 for utility, 15 for Defend, up to 112 for Nitro). |
| `CALL_BEAD_POWER` | `0x045F17` | `$C4:5F17` | 16 words | Base power for 16 Call Bead spells. |
| `ALCHEMY_COST_DATA` | `0x04601F` | `$C4:601F` | 35 * 4 B | `[Ing1_ID, Ing2_ID, Ing1_Qty, Ing2_Qty]`. |
| `LEVEL_MULTIPLIERS` | `0x045BA5` | `$C4:5BA5` | 10 bytes | Factors: `[2, 4, 7, 11, 15, 20, 26, 32, 39, 46]` for Lv0..Lv9. |
| `XP_GAIN_PER_CAST` | `0x045B9C` | `$C4:5B9C` | 10 bytes | XP gains: `[10, 5, 4, 3, 2, 2, 1, 1, 1, 1]` for Lv0..Lv9. |
| `SCRIPT_PTR_TABLE` | `0x045802` | `$C4:5802` | 4 B/entry | Bytecode script addresses `[Addr Word, Bank Byte, 0x00]`. |

---

## 3. Combat Math & Formula Engine

### 3.1 Gross Power & Multi-Target Division
$$\text{Gross Power} = \text{Base Power} \times \text{Level Factor}[\text{Level}]$$
$$\text{Divided Power} = \left\lfloor \frac{\text{Gross Power}}{\text{Target Count} + 1} \right\rfloor$$
- Single target divides by 2.
- Multi-target divides evenly across all active targets.

### 3.2 Random Variance
$$\text{Min Power} = \left\lceil \frac{\text{Divided Power}}{2} \right\rceil, \quad \text{Random Add} = \text{RNG}\left(0 \dots \left\lfloor \frac{\text{Divided Power}}{2} \right\rfloor\right)$$
$$\text{Final Power} = \text{Min Power} + \text{Random Add}$$
- Final Power uniformly varies between **50% and 100%** of Divided Power (average 75%).

### 3.3 Status Buffs (Defend, Atlas, Speed)
- `Final Power` is directly added to boost stats:
  - **Defend:** Boost Defense (`$7E4F2B`). Duration = 3600 frames (60.0s, `$0E10`).
  - **Atlas:** Boost Attack (`$7E4F29`). Duration = 5400 frames (90.0s, `$1518`).
  - **Speed:** Speed flags / animation rates (`$7E4F2F`). Duration = 3600 frames (60.0s).
- Calls master recalculation routine `$8F:8398` to recompute total stats including equipment and charms:
  - Chocobo Egg (`$2261 & 0x40`)
  - Armor Polish (`$2262 & 0x80`)
  - Wizard's Coin (`$2263 & 0x04`)

### 3.4 Damage & Healing
- **Damage (`$91:9C90`):**
  - Charm boost: +25% if `$2262 & 0x08` set.
  - Subtraction: $\text{Net Damage} = \text{Power} - \text{Enemy Magic Defense}$ (from `$8E001D,X`).
  - Clamped between 1 and 999.
- **Healing (`$91:9D16`):**
  - Directly adds `Final Power` to target HP (capped at 999).

---

## 4. Animation VM & Bytecode

The animation VM is driven by interpreter loop `$90:80CE` reading 8 slots at `$7E3364..$7E3563` (64 bytes each):

- `0x00`: Terminate script / release slot (`$90:878A`).
- `0x01..0x1E`: Frame hold delay timer (`$90:836C`).
- `0x22..0x2B`: Render sprite frame at offset with flags (`$90:8418`).
- `0x2C`: Switch sprite bank and frame table pointer (`$90:842F`).
- `0x2D`: Loop back to script start (`$90:877D`).
- `0x2E`: Play sound effect ID (`$90:8921`).
- `0x38`: Clear slot attribute field (`$90:8B6C`).
- `0xDD`: Palette flash effect.

---

## 5. Cut Content & Adding New Formulas

- **Cut/Unused Vanilla Spells:**
  1. `REGROWTH` (`0x36`): Base power 2, target party, 1 Acorn + 2 Water. Periodic HP regen.
  2. `SLOW BURN` (`0x3C`): Base power 1, target all enemies, 1 Iron + 1 Brimstone. Lingering DoT.
  3. `STOP` (`0x42`): Target all enemies, 2 Wax + 1 Crystal. Enemy AI freeze.
  4. `REFLECT` (`0x34`): Target party, 2 Grease + 1 Iron. Magic reflection.
  5. `LASER` (`0x28`): Cut formula re-using Acid Rain animation.
- **Expansion Capacity:**
  - SRAM byte `$225C` has **5 unused bits** (`0x08`..`0x80`), allowing up to 40 formulas without SRAM layout changes.
  - Adding beyond 35 requires relocating WRAM level tables (`$7E2F52`, `$7E2F98`) which collide with ingredient usage counters at `$7E2FDE`.
  - ROM tables in Bank `$C4` must be repointed if expanding beyond 35 entries because currency strings start immediately at `$C4:60AB`.
