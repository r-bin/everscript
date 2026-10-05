# Alchemy System, Spell Virtual Machine, and Combat Calculations

Comprehensive reverse-engineered specification of Secret of Evermore's alchemy and spell subsystems, covering ring menu integration, ROM data structures, the bytecode animation virtual machine, damage/healing/buff formulas, and unused spells.

---

## 1. High-Level Architecture Overview

Casting an alchemy formula in Secret of Evermore involves four distinct pipelines executing in sequence:

```
1. Ring Menu Selection
   - Icon ID (e.g. 0x004E ALCHEMY_DEFEND)
   - Lookup at $8E:8000 -> Item descriptor at $8E:827C -> Alchemy Index (0x0E)
   │
   ▼
2. Cost & Target Validation
   - Check ingredients in WRAM ($7E22FF+X) against cost table at $C4:601F
   - Load target flags from $C4:5BF5 (e.g. 0x0008 BOY_DOG_BOTH)
   - Player selects valid target(s)
   │
   ▼
3. Cast Execution & Spell Power Calculation (Routine $91:CCD8)
   - Deduct ingredients from inventory ($7E22FF+X)
   - Award formula XP from table $C4:5B9C to Low Experience ($7E2F52+X)
   - Compute Gross Power: Base Power ($C4:5E6B) * Level Multiplier ($C4:5BA5)
   - Divide Gross Power among active targets: Gross / (Target_Count + 1)
   - Apply random variance: 50% base + RNG(0 .. 50%) -> Final Power
   - Allocate animation slot ($7E3364..$7E3563) and store Final Power at offset +$2A
   │
   ▼
4. Animation VM & Effect Resolution
   - Interpreter at $90:80CE executes bytecode script (Bank $C9 / $91)
   - Emits OAM sprite frames (e.g. Defend barrier ring $CF:36CF)
   - On completion / hit: invokes effect handler (damage, heal, or status buff)
```

---

## 2. Master ROM & WRAM Tables

All 35 alchemy formulas share a common index (`ALCHEMY_INDEX`, step = 2, range `0x00` to `0x44`):

### 2.1 ROM Data Tables (Bank `$C4`)

| Table Name | ROM File Offset | SNES Address | Entry Size | Description |
|---|---|---|---|---|
| **`ALCHEMY_TARGET`** | `0x045BF5` | `$C4:5BF5` | Word (2 B) | Target mask bitfield for targeting cursor. |
| **`ALCHEMY_LEARNED_ADDR`** | `0x045C3B` | `$C4:5C3B` | Word (2 B) | WRAM persistence byte address (`$2258`..`$225C`). |
| **`ALCHEMY_LEARNED_MASK`** | `0x045C81` | `$C4:5C81` | Byte (1 B) | Bitmask within persistence byte (`0x01`..`0x80`). |
| **`ALCHEMY_ANIM_MAP`** | `0x045DDF` | `$C4:5DDF` | Word (2 B) | Animation ID index for dispatch table. |
| **`ALCHEMY_POWER`** | `0x045E6B` | `$C4:5E6B` | Word (2 B) | Base power value. |
| **`CALL_BEAD_POWER`** | `0x045F17` | `$C4:5F17` | Word (2 B) | Base power for 16 Call Bead spells. |
| **`ALCHEMY_COST_DATA`** | `0x04601F` | `$C4:601F` | 4 Bytes | `[Ing1_ID, Ing2_ID, Ing1_Qty, Ing2_Qty]`. |
| **`LEVEL_MULTIPLIERS`** | `0x045BA5` | `$C4:5BA5` | 10 Bytes | Level scale factors for Levels 0 through 9. |
| **`XP_GAIN_PER_CAST`** | `0x045B9C` | `$C4:5B9C` | 10 Bytes | Experience awarded per cast for Levels 0 through 9. |
| **`SCRIPT_PTR_TABLE`** | `0x045802` | `$C4:5802` | 4 Bytes/entry | Bytecode script addresses `[Addr Word, Bank Byte, 0x00]`. |

### 2.2 Level Multiplier & Experience Tables

Formula progression uses two hardcoded tables indexed by current formula Level ($0 \dots 9$):

```
Level:           0     1     2     3     4     5     6     7     8     9
------------------------------------------------------------------------
Multiplier:      2     4     7    11    15    20    26    32    39    46  ($C4:5BA5)
XP Per Cast:    10     5     4     3     2     2     1     1     1     1  ($C4:5B9C)
Casts to Next:  10    20    25    34    50    50   100   100   100     -
```

- Low Experience is stored in `$7E2F52 + Index`. When it reaches 100 (`0x64`), it wraps around and increments High Level at `$7E2F98 + Index`.
- XP awarded per cast decreases with higher levels according to the table above.

### 2.3 WRAM Allocation

- **Learned Flags:** `$7E2258` to `$7E225C` (Persistent SRAM).
  - `$2258`: Acid Rain, Atlas, Barrier, Call Up, Corrosion, Crush, Cure, Defend.
  - `$2259`: Double Drain, Drain, Energize, Escape, Explosion, Fireball, Fire Power, Flash.
  - `$225A`: Force Field, Hard Ball, Heal, Lance, Laser, Levitate, Lightning Storm, Miracle Cure.
  - `$225B`: Nitro, One Up, Reflect, Regrowth, Revealer, Revive, Slow Burn, Speed.
  - `$225C`: Sting (`0x01`), Stop (`0x02`), Super Heal (`0x04`). Bits `0x08`, `0x10`, `0x20`, `0x40`, `0x80` are **unused**.
- **Equipped Formulas:** `$7E0AD2`..`$7E0ADA` (9 ring menu slots).
- **Formula Progress:**
  - `$7E2F52 + Index`: Low Experience word ($0 \dots 99$).
  - `$7E2F98 + Index`: High Level word ($0 \dots 9$).
- **Ingredient Usage Stats:** `$7E2FDE + Ingredient_ID` (1 byte counter per ingredient type).

---

## 3. Spell Power & Combat Calculations

### 3.1 Gross Power & Multi-Target Division

When a spell is cast, routine `$91:CCD8` performs fixed-point math using the SNES hardware multiplication and division registers (`$4202..$4216`):

1. **Gross Power:**
   $$\text{Gross Power} = \text{Base Power} \times \text{Level Factor}[\text{Level}]$$
   *Executed as `STA $4202` (Base Power in low byte, Level Factor in high byte).*

2. **Target Count Division:**
   $$\text{Divided Power} = \left\lfloor \frac{\text{Gross Power}}{\text{Target Count} + 1} \right\rfloor$$
   - Single target: $\text{Divided Power} = \text{Gross Power} / 2$.
   - Two targets: $\text{Divided Power} = \text{Gross Power} / 3$.
   - Three targets: $\text{Divided Power} = \text{Gross Power} / 4$.
   *(Note: Single target divides by 2; since Level 0 multiplier is 2, Level 0 single-target Divided Power exactly equals Base Power).*

3. **Random Variance (RNG):**
   $$\text{Min Power} = \text{Divided Power} - \left\lfloor \frac{\text{Divided Power}}{2} \right\rfloor = \left\lceil \frac{\text{Divided Power}}{2} \right\rceil$$
   $$\text{Random Add} = \text{RNG}\left(0 \dots \left\lfloor \frac{\text{Divided Power}}{2} \right\rfloor\right)$$
   $$\text{Final Power} = \text{Min Power} + \text{Random Add}$$

   > **Rule:** Final Power has a uniform random variance between **50% and 100%** of Divided Power (average 75%).

### 3.2 Status Buff Calculation (e.g. Defend, Atlas)

For status buffs, `Final Power` is added directly to the character's internal boost stat:

```65c816
; Defend application ($91:B137):
LDA $002A,Y     ; Final Power from animation slot
STA ($62)       ; Save to active status slot parameter
LDA $00A2,X     ; Current boost defense ($7E4F2B)
CLC
ADC ($62)       ; Add Final Power
STA $00A2,X     ; Write updated boost defense
JSL $8F8398     ; Master Stat Recalculation
```

- **Duration Timers:**
  - **Defend:** 3600 frames = **60.0 seconds** (`$0E10`).
  - **Atlas:** 5400 frames = **90.0 seconds** (`$1518`).
  - **Speed:** 3600 frames = **60.0 seconds** (`$0E10`).
- **Master Stat Recalculation (`$8F:8398`):**
  Computes effective defense / attack by summing:
  $$\text{Effective Defense} = \text{Base Defense} + \text{Armor Defense} + \text{Boost Defense} + \text{Charm Bonuses}$$
  - Chocobo Egg (`$2261 & 0x40`): adds stat bonus.
  - Armor Polish (`$2262 & 0x80`): adds armor bonus.
  - Wizard's Coin (`$2263 & 0x04`): adds magic defense bonus.
- When the status timer reaches 0, the removal routine subtracts the stored buff parameter and calls `$8F:8398` to revert stats.

### 3.3 Damaging Spell Calculation

When a damaging spell hits an enemy (routine `$91:9C90`):

1. **Charm Boost:** If magic charm / Thraxx's Claw is active (`$2262 & 0x08`), `Final Power` receives a 25% boost:
   $$\text{Power} = \text{Power} + \left\lfloor \frac{\text{Power}}{4} \right\rfloor$$
2. **Magic Defense Reduction:**
   $$\text{Net Damage} = \text{Power} - \text{Enemy Magic Defense}$$
   *(Enemy Magic Defense is loaded from ROM entity table `$8E001D,X`).*
3. **Clamping:**
   $$\text{Damage} = \text{clamp}(\text{Net Damage}, 1, 999)$$
4. Calls `$8FC0D3` to decrement enemy HP and trigger damage number sprites.

### 3.4 Healing Spell Calculation

When Heal / Super Heal / Miracle Cure resolves (routine `$91:9D16`):

1. `Final Power` is clamped to a maximum of 999 (`0x03E7`).
2. Calls `$8FC09A` to increment target HP up to Max HP and display green heal numbers.

---

## 4. The Animation Bytecode Virtual Machine

Spells do not use hardcoded assembly for their visuals; they execute a dedicated bytecode scripting language interpreted by routine `$90:80CE`.

### 4.1 Animation Slots (`$7E3364`..`$7E3563`)

The engine maintains 8 parallel animation slots of 64 bytes (`0x40`) each:
- `+$00`: Script PC Pointer (Low/Mid Word)
- `+$02`: Script Bank (`$C9` or `$91`)
- `+$05`: Frame Delay Timer
- `+$06`: Current Sprite Frame Pointer
- `+$08`: Sprite Attribute / Offset
- `+$09`: Sprite Graphics Bank (e.g. `$CF`)
- `+$0A`: Sprite Graphics Table Pointer (e.g. `$2F65`)
- `+$0E`: Step / Lifetime Counter
- `+$12`: Spell / Animation Type ID
- `+$26`: Active Flag (`0x00` = active, `0x02` = inactive)
- `+$28`: Source Entity Pointer
- `+$2A`: Calculated `Final Power`
- `+$2E`: Target Entity Pointer 1
- `+$30`: Target Entity Pointer 2

### 4.2 Bytecode Interpreter Loop (`$90:80CE`)

Every frame, the engine loops over active slots:
1. Increments lifetime counter `+$0E`.
2. Reads current opcode byte at `[$5D]` (PC).
3. If bit 7 is clear, shifts left and dispatches via jump table `$90:8000`.
4. If bit 7 is set, executes extended parameter/opcode handlers.

### 4.3 Key Animation Opcodes

| Opcode | Handler | Operands | Function |
|---|---|---|---|
| **`0x00`** | `$90:878A` | none | **End Script.** Releases slot and terminates animation. |
| **`0x01..0x1E`** | `$90:836C` | none | **Set Delay.** Sets frame hold duration to `Opcode / 2` frames. |
| **`0x22..0x2B`** | `$90:8418` | `[Word: FramePtr]` | **Display Frame.** Loads frame from current sprite sheet. |
| **`0x2C`** | `$90:842F` | `[Word: TablePtr] [Byte: Bank]` | **Set Sprite Sheet.** Points to sprite frame table (e.g. `2c 65 2f cf` -> `$CF:2F65`). |
| **`0x38`** | `$90:8B6C` | `[Byte: SlotOffset]` | **Clear Slot Field.** Clears 16-bit field at offset. |
| **`0x3C..0x40`** | `$90:8A13` | various | Coordinate movement and target tracking. |
| **`0x47..0x4B`** | `$90:87BA` | various | Palette cycling and color modulation. |
| **`0x50..0x55`** | `$90:85A8` | various | Sound effect triggers and screen shake. |

---

## 5. Master Table: Formulas, Full Bytecode Scripts, and Behaviors

The table below catalogs every alchemy formula in the game, its ROM identifiers, the full decompiled bytecode animation scripts executed by the VM, ingredient costs, and mechanical behavior.

| Idx | Formula Name | Target | Base Pwr | Cost | Anim ID | Whole Decompiled Script(s) | Visual / Mechanical Behavior & Comments |
|:---:|---|---|:---:|---|:---:|---|---|
| `0x00` | **Acid Rain** | All Enemies | 17 | 1 Ash<br>3 Water | `0x02` | `0xC9:0x4D44`: `FRAME(0x4C8E,6f) → FRAME(0x4C9A,7f) → FRAME(0x4CBE,7f) → FRAME(0x4CF1,12f) → FRAME(0x4D24,3f) → SFX(0x1A) → FRAME(0x4CF1,6f) → FRAME(0x4D61,4f) → SFX(0x1A) → FRAME(0x4CF1,25f) → FRAME(0x4DBC,5f) → SFX(0x2D) → FRAME(0x4E2B,4f) → FRAME(0x4E7C,4f)` | Green acid storm cloud over all enemies. Screen-wide damage ticks. |
| `0x02` | **Atlas** | Boy | 25 | 1 Ash<br>1 Atlas Ring | `0x18` | `0x91:0x8B2A`: `Sequence Handler (inline visual script)` | Golden aura pillars. Grants +Final_Power attack to Boy for 90s (5400 frames). |
| `0x04` | **Barrier** | Party | 25 | 1 Limestone<br>2 Bone | `0x24` | `0xC9:0x5492`: `FRAME(0x0261,5f) → FRAME(0x026D,5f) → FRAME(0x0274,5f) → FRAME(0x0280,5f) → FRAME(0x028C,5f) → FRAME(0x02DD,5f) → FRAME(0x02E4,5f) → FRAME(0x0308,5f) → FRAME(0x033B,5f) → FRAME(0x037D,5f) → FRAME(0x03FB,5f) → FRAME(0x041F,5f)` | Hexagonal shield barriers surround party. Absorbs physical attacks. |
| `0x06` | **Call Up** | Boy | 0 | 1 Meteorite<br>1 Dry Ice | `0x3E` | `0xC9:0x576D`: `FRAME(0x19D5,5f) → SFX(0x26) → FRAME(0x19DC,5f) → FRAME(0x19F6,5f) → FRAME(0x19DC,5f) → FRAME(0x1A10,2f) → SFX(0x1A) → FRAME(0x1A1C,2f) → FRAME(0x1A36,2f) → FRAME(0x1A73,2f) → FRAME(0x1AA6,2f) → FRAME(0x1AE3,2f) → FRAME(0x1B16,2f) → FRAME(0x1B53,2f)`<br>`0xC9:0x532F`: `FRAME(0x7447,4f) → SFX(0x1A) → FRAME(0x744E,4f) → FRAME(0x748B,4f) → FRAME(0x74B4,4f) → SFX(0x1A) → SHEET(0xCF:0x74BB) → 0x04 → SHEET(0xCF:0x74F8) → 0x04 → CLR(+9) → FRAME(0x7447,4f) → SFX(0x1A) → FRAME(0x744E,4f) → FRAME(0x748B,4f) → FRAME(0x74B4,4f)` | Blue spiral charging aura into Boy. Restores Call Bead inventory count. |
| `0x08` | **Corrosion** | Single Enemy | 25 | 1 Mushrooms<br>3 Water | `0x28` | `0x91:0x8F20`: `Sequence Handler (inline visual script)` | Bubbling acidic goo anchored on target enemy hitbox. Periodic ticks. |
| `0x0A` | **Crush** | All Enemies | 62 | 1 Limestone<br>1 Wax | `0x14` | `0xC9:0x50BF`: `FRAME(0x6967,1f) → FRAME(0x69AE,22f) → FRAME(0x6A22,7f) → FRAME(0x6A78,10f) → FRAME(0x6AB5,10f) → FLASH → FRAME(0x6ACA,3f) → FRAME(0x6AE4,4f) → FRAME(0x6AFE,4f) → FRAME(0x6B18,4f) → FRAME(0x6B32,5f) → FRAME(0x6B4C,5f) → FRAME(0x6B66,5f)` | Massive stone fist crushes target(s) with screen shake and dust. |
| `0x0C` | **Cure** | Party | 0 | 2 Root<br>1 Oil | `0x00` | `0xC9:0x45FA`: `FRAME(0x30EE,4f) → SFX(0x17) → FRAME(0x30F5,4f) → FRAME(0x30FC,4f) → FRAME(0x3108,4f) → FRAME(0x3114,4f) → FRAME(0x3120,4f) → FRAME(0x312C,4f) → FRAME(0x3141,4f) → FRAME(0x315B,4f) → FRAME(0x3175,4f) → FRAME(0x3199,4f) → FRAME(0x31D1,4f)` | Green cleansing sparkle pillar. Removes poison, plague, confound, stop. |
| `0x0E` | **Defend** | Party | 15 | 1 Clay<br>1 Ash | `0x04` | `0xC9:0x45AD`: `FRAME(0x2EF0,7f) → FRAME(0x2EFC,7f) → FRAME(0x2F03,7f) → FRAME(0x2F0F,7f) → FRAME(0x2F24,7f) → FRAME(0x2F2B,7f) → FRAME(0x2F37,7f) → SHEET(0xCF:0x2F65) → FRAME(0x2F93,7f) → CLR(+9) → FRAME(0x2FC1,7f) → FRAME(0x3003,7f) → FRAME(0x3045,7f)` | Defensive energy ring (0xCF:0x36CF) surrounds target. +Defense for 60s (3600 frames). |
| `0x10` | **Double Drain** | All Enemies | 50 | 2 Ethanol<br>2 Vinegar | `0x22` | `0xC9:0x4983`: `FRAME(0x4236,2f) → FRAME(0x423D,2f) → FRAME(0x4244,2f) → FRAME(0x424B,2f) → FRAME(0x4252,2f) → LOOP`<br>`0xC9:0x499D`: `FRAME(0x4252,2f) → FRAME(0x424B,2f) → FRAME(0x4244,2f) → FRAME(0x423D,2f) → FRAME(0x4236,2f) → LOOP` | Energy whirlwind siphons HP from all enemies simultaneously to party. |
| `0x12` | **Drain** | All Enemies | 25 | 1 Ethanol<br>2 Root | `0x12` | `0xC9:0x4983`: `FRAME(0x4236,2f) → FRAME(0x423D,2f) → FRAME(0x4244,2f) → FRAME(0x424B,2f) → FRAME(0x4252,2f) → LOOP`<br>`0xC9:0x499D`: `FRAME(0x4252,2f) → FRAME(0x424B,2f) → FRAME(0x4244,2f) → FRAME(0x423D,2f) → FRAME(0x4236,2f) → LOOP` | Red energy spiral siphons HP from single enemy to caster. |
| `0x14` | **Energize** | Party | 0 | 1 Crystal<br>1 Iron | `0x40` | `0xC9:0x532F`: `FRAME(0x7447,4f) → SFX(0x1A) → FRAME(0x744E,4f) → FRAME(0x748B,4f) → FRAME(0x74B4,4f) → SFX(0x1A) → SHEET(0xCF:0x74BB) → 0x04 → SHEET(0xCF:0x74F8) → 0x04 → CLR(+9) → FRAME(0x7447,4f) → SFX(0x1A) → FRAME(0x744E,4f) → FRAME(0x748B,4f) → FRAME(0x74B4,4f)`<br>`0xC9:0x56C6`: `FRAME(0x1793,4f) → SFX(0x40) → FRAME(0x17C1,4f) → FRAME(0x17EF,4f) → FRAME(0x1831,4f) → FRAME(0x184B,4f) → FRAME(0x1831,4f) → SFX(0x44) → FRAME(0x184B,4f) → FRAME(0x1831,4f) → SFX(0x44) → FRAME(0x184B,4f) → FRAME(0x1831,4f) → SFX(0x44) → FRAME(0x184B,4f)` | Charging flash fills weapon charge meter to 100% (or max level 3). |
| `0x16` | **Escape** | 0x0208 | 0 | 1 Wax<br>1 Vinegar | `0x20` | `0xC9:0x4FAD`: `FRAME(0x5BF2,6f) → FRAME(0x5D80,6f) → FRAME(0x5DCC,6f) → FRAME(0x5E13,6f) → FRAME(0x5E50,6f) → FRAME(0x5E92,6f) → FRAME(0x5ED4,6f) → FRAME(0x5F11,6f) → FRAME(0x5F58,6f) → FRAME(0x5F9F,6f) → LOOP` | Spinning teleport ring warps party out of caves/dungeons to entrance. |
| `0x18` | **Explosion** | All Enemies | 87 | 2 Ethanol<br>1 Ash | `0x30` | `0xC9:0x47B6`: `FRAME(0x39EA,4f) → FRAME(0x39FF,4f) → FRAME(0x3A06,4f) → FRAME(0x3A0D,4f) → FRAME(0x3A22,6f) → FRAME(0x3A29,4f) → FRAME(0x3A30,4f) → FRAME(0x0001,6f) → FRAME(0x3A37,4f) → SFX(0x19) → FRAME(0x3A43,4f) → FRAME(0x3A58,4f) → FRAME(0x3A72,6f)` | Massive chemical explosion ripples across enemy positions. |
| `0x1A` | **Fireball** | All Enemies | 62 | 1 Brimstone<br>2 Ash | `0x1E` | `0xC9:0x4781`: `0x05 → 0xDE → 0xBA → CLR(+207) → 0xC6 → CLR(+207) → 0xE0 → CLR(+207) → 0xEC → CLR(+207) → 0x06 → 0x39 → 0xCF → 0x12 → 0x39 → 0xCF → SHEET(0x38:0xCF39) → 0x39 → 0xCF → 0x05 → 0xDE → 0x52 → 0x39 → 0xCF → 0x5E → 0x39 → 0xCF → 0x78 → 0x39 → 0xCF → 0x84 → 0x39 → 0xCF → 0x9E → 0x39 → 0xCF → 0xAA → 0x39 → 0xCF → 0xC4 → 0x39 → 0xCF → 0xD0 → 0x39 → 0xCF → LOOP` | Hurls high-speed searing fireball projectile from caster to target. |
| `0x1C` | **Fire Power** | All Enemies | 112 | 1 Feather<br>1 Brimstone | `0x2A` | `0xC9:0x52D4`: `FRAME(0x73F3,2f) → FRAME(0x73FA,1f) → FRAME(0x7401,3f) → FRAME(0x7408,1f) → FRAME(0x73F3,2f) → FRAME(0x73FA,1f) → FRAME(0x740F,3f) → FRAME(0x7416,1f) → FRAME(0x741D,2f) → FRAME(0x7424,1f) → FRAME(0x740F,2f) → FRAME(0x7416,1f)`<br>`0xC9:0x4834`: `SFX(0x19) → FRAME(0x3BE2,3f) → FRAME(0x3C06,2f) → FRAME(0x3C48,3f) → FRAME(0x3C8F,3f) → FRAME(0x3CD6,2f) → FRAME(0x3CFA,3f) → 0x37 → 0x06 → 0x14 → FLASH → FRAME(0x3D0F,6f) → SFX(0x19) → FRAME(0x3D16,5f) → FRAME(0x3D35,5f) → FRAME(0x3D4A,5f) → FRAME(0x3D64,5f)` | Pillars of roaring fire erupt under enemies. Max base power (112). |
| `0x1E` | **Flash** | All Enemies | 27 | 1 Wax<br>2 Oil | `0x06` | `0xC8:0x057F`: `0x02 → 0xDF → FRAME(0xCC43,2f) → 0x3F → 0x43 → 0xCC → 0x02 → 0xDF → 0x59 → 0x43 → 0xCC → 0x02 → 0xDF → 0x6E → 0x43 → 0xCC → 0x02 → 0xDF → 0x83 → 0x43 → 0xCC → 0x02 → 0xDF → 0x9D → 0x43 → 0xCC → LOOP`<br>`0xC9:0x4834`: `SFX(0x19) → FRAME(0x3BE2,3f) → FRAME(0x3C06,2f) → FRAME(0x3C48,3f) → FRAME(0x3C8F,3f) → FRAME(0x3CD6,2f) → FRAME(0x3CFA,3f) → 0x37 → 0x06 → 0x14 → FLASH → FRAME(0x3D0F,6f) → SFX(0x19) → FRAME(0x3D16,5f) → FRAME(0x3D35,5f) → FRAME(0x3D4A,5f) → FRAME(0x3D64,5f)` | Early game burning embers projectile fired at target enemy. |
| `0x20` | **Force Field** | Party | 0 | 1 Grease<br>1 Iron | `0x42` | `0xC9:0x56C6`: `FRAME(0x1793,4f) → SFX(0x40) → FRAME(0x17C1,4f) → FRAME(0x17EF,4f) → FRAME(0x1831,4f) → FRAME(0x184B,4f) → FRAME(0x1831,4f) → SFX(0x44) → FRAME(0x184B,4f) → FRAME(0x1831,4f) → SFX(0x44) → FRAME(0x184B,4f) → FRAME(0x1831,4f) → SFX(0x44) → FRAME(0x184B,4f)`<br>`0xC9:0x45FA`: `FRAME(0x30EE,4f) → SFX(0x17) → FRAME(0x30F5,4f) → FRAME(0x30FC,4f) → FRAME(0x3108,4f) → FRAME(0x3114,4f) → FRAME(0x3120,4f) → FRAME(0x312C,4f) → FRAME(0x3141,4f) → FRAME(0x315B,4f) → FRAME(0x3175,4f) → FRAME(0x3199,4f) → FRAME(0x31D1,4f)` | Pulsating golden dome. Grants complete physical invulnerability. |
| `0x22` | **Hard Ball** | All Enemies | 21 | 1 Crystal<br>1 Clay | `0x10` | `0xC9:0x4810`: `0x08 → 0xDF → 0x99 → 0x3B → 0xCF → 0x08 → 0xDF → 0xA0 → 0x3B → 0xCF → LOOP` | Heavy stone projectile launched directly at enemy hitbox. |
| `0x24` | **Heal** | Party | 32 | 1 Root<br>1 Water | `0x08` | `0xC9:0x4683`: `SFX(0x17) → FRAME(0x349D,6f) → FRAME(0x34A4,6f) → FRAME(0x34AB,6f) → FRAME(0x34B2,6f) → FRAME(0x34B9,6f) → FRAME(0x34C0,6f) → FRAME(0x34C7,6f) → FRAME(0x34EB,6f) → FRAME(0x350F,6f) → FRAME(0x3533,6f) → FRAME(0x3557,6f) → FRAME(0x3594,6f)` | Rising healing sparkle column. Restores Final_Power HP (clamped to 999). |
| `0x26` | **Lance** | All Enemies | 50 | 1 Iron<br>1 Acorn | `0x26` | `0xC9:0x4FAD`: `FRAME(0x5BF2,6f) → FRAME(0x5D80,6f) → FRAME(0x5DCC,6f) → FRAME(0x5E13,6f) → FRAME(0x5E50,6f) → FRAME(0x5E92,6f) → FRAME(0x5ED4,6f) → FRAME(0x5F11,6f) → FRAME(0x5F58,6f) → FRAME(0x5F9F,6f) → LOOP`<br>`0xC9:0x4F84`: `FRAME(0x5BF2,7f) → FRAME(0x5C43,8f) → FRAME(0x5C7B,8f) → FRAME(0x5C90,6f) → FRAME(0x5CDC,6f) → FRAME(0x5D19,6f) → FRAME(0x5D47,6f) → FRAME(0x5D66,6f) → FLASH → FRAME(0x5BF2,6f) → FRAME(0x5D80,6f) → FRAME(0x5DCC,6f) → FRAME(0x5E13,6f)` | Magic spear projectile flies straight through enemy hitboxes. |
| `0x28` | **Laser** | All Enemies | 0 | 1 Crystal<br>1 Brimstone | `0x02` | `0xC9:0x4D44`: `FRAME(0x4C8E,6f) → FRAME(0x4C9A,7f) → FRAME(0x4CBE,7f) → FRAME(0x4CF1,12f) → FRAME(0x4D24,3f) → SFX(0x1A) → FRAME(0x4CF1,6f) → FRAME(0x4D61,4f) → SFX(0x1A) → FRAME(0x4CF1,25f) → FRAME(0x4DBC,5f) → SFX(0x2D) → FRAME(0x4E2B,4f) → FRAME(0x4E7C,4f)` | Unused/cut formula. Reuses Acid Rain script and sequence. Base power 0. |
| `0x2A` | **Levitate** | 0x0022 | 0 | 1 Water<br>1 Mud Pepper | `0x0A` | `0xC9:0x4FE0`: `SHEET(0xCF:0x5FDC) → SFX(0x45) → FRAME(0x6014,8f) → FRAME(0x6042,8f) → FRAME(0x6075,8f) → FRAME(0x60AD,8f) → FRAME(0x60EF,8f) → FRAME(0x6127,8f) → FRAME(0x616E,8f) → FRAME(0x61A6,8f) → FRAME(0x61E8,8f) → LOOP`<br>`0xC9:0x4EE7`: `FRAME(0x55C2,5f) → FRAME(0x55C9,5f) → FRAME(0x55D0,5f) → FRAME(0x55D7,5f) → SFX(0x41) → FRAME(0x55DE,5f) → FRAME(0x55E5,5f) → FRAME(0x55EC,5f) → FRAME(0x55F8,5f) → SHEET(0xCF:0x5604) → 0x05 → SFX(0x46) → SHEET(0xCF:0x562D) → 0x05 → SHEET(0xCF:0x5656)` | Puzzle utility. Telekinetically lifts heavy stone boulders into the air. |
| `0x2C` | **Lightning Storm** | All Enemies | 87 | 1 Iron<br>2 Ash | `0x32` | `0xC9:0x4E84`: `FRAME(0x5495,7f) → FRAME(0x54A1,7f) → FRAME(0x54AD,7f) → FRAME(0x54D6,12f) → FRAME(0x5509,3f) → SFX(0x1A) → FRAME(0x5555,3f) → FRAME(0x54D6,5f) → FRAME(0x5509,3f) → FRAME(0x54D6,10f) → FRAME(0x54AD,7f) → FRAME(0x54A1,7f) → FRAME(0x5495,7f)`<br>`0xC9:0x4A97`: `FRAME(0x45CE,1f) → FRAME(0x45DA,1f) → FRAME(0x45CE,1f) → FRAME(0x45E6,1f) → FRAME(0x45CE,1f) → FRAME(0x45DA,1f) → FRAME(0x45CE,1f) → FRAME(0x45E6,1f) → FRAME(0x45F2,1f) → FRAME(0x45FE,1f) → FRAME(0x45F2,1f) → FRAME(0x460A,1f)` | White screen flash with jagged lightning bolts striking all enemies. |
| `0x2E` | **Miracle Cure** | Party | 37 | 2 Root<br>1 Vinegar | `0x0E` | `0xC9:0x45FA`: `FRAME(0x30EE,4f) → SFX(0x17) → FRAME(0x30F5,4f) → FRAME(0x30FC,4f) → FRAME(0x3108,4f) → FRAME(0x3114,4f) → FRAME(0x3120,4f) → FRAME(0x312C,4f) → FRAME(0x3141,4f) → FRAME(0x315B,4f) → FRAME(0x3175,4f) → FRAME(0x3199,4f) → FRAME(0x31D1,4f)` | Restores HP (Base 37) and cleanses all status ailments simultaneously. |
| `0x30` | **Nitro** | All Enemies | 112 | 1 Gunpowder<br>2 Grease | `0x3A` | `0xC9:0x47B6`: `FRAME(0x39EA,4f) → FRAME(0x39FF,4f) → FRAME(0x3A06,4f) → FRAME(0x3A0D,4f) → FRAME(0x3A22,6f) → FRAME(0x3A29,4f) → FRAME(0x3A30,4f) → FRAME(0x0001,6f) → FRAME(0x3A37,4f) → SFX(0x19) → FRAME(0x3A43,4f) → FRAME(0x3A58,4f) → FRAME(0x3A72,6f)` | Supreme explosion. Screen shake and devastating fire damage. Base 112. |
| `0x32` | **One Up** | Boy | 0 | 1 Feather<br>1 Root | `0x2C` | `0xC9:0x4727`: `FRAME(0x36FD,8f) → SFX(0x43) → FRAME(0x3704,8f) → FRAME(0x370B,8f) → FRAME(0x3720,8f) → FRAME(0x3727,8f) → FRAME(0x372E,8f) → FRAME(0x3735,8f) → FRAME(0x374A,8f) → FRAME(0x3751,8f) → FRAME(0x375D,8f) → FRAME(0x3764,8f) → SFX(0x42) → FRAME(0x377E,8f)` | Golden wings aura revives companion Dog with 100% full health restore. |
| `0x34` | **Reflect** | Party | 0 | 2 Grease<br>1 Iron | `0x3C` | `0xC9:0x561B`: `FRAME(0x0C23,5f) → SFX(0x3E) → FRAME(0x0C2A,5f) → FRAME(0x0C31,5f) → FRAME(0x0C38,5f) → FRAME(0x0C4D,5f) → FRAME(0x0C62,5f) → SFX(0x2E) → FRAME(0x0C90,5f) → FRAME(0x0CC3,5f) → FRAME(0x0D37,5f) → SFX(0x40) → FRAME(0x0DC9,5f) → FRAME(0x0E56,5f)`<br>`0xC9:0x576D`: `FRAME(0x19D5,5f) → SFX(0x26) → FRAME(0x19DC,5f) → FRAME(0x19F6,5f) → FRAME(0x19DC,5f) → FRAME(0x1A10,2f) → SFX(0x1A) → FRAME(0x1A1C,2f) → FRAME(0x1A36,2f) → FRAME(0x1A73,2f) → FRAME(0x1AA6,2f) → FRAME(0x1AE3,2f) → FRAME(0x1B16,2f) → FRAME(0x1B53,2f)` | Unused/cut formula. Mirror barrier intended to bounce hostile spells. |
| `0x36` | **Regrowth** | Party | 2 | 1 Acorn<br>2 Water | `0x2E` | `0xC9:0x529A`: `FRAME(0x72D5,7f) → SFX(0x4F) → FRAME(0x72EF,7f) → FRAME(0x7309,7f) → FRAME(0x7323,7f) → FRAME(0x733D,7f) → FRAME(0x7357,7f) → FRAME(0x7371,7f) → FRAME(0x738B,7f) → FRAME(0x73A5,7f) → FRAME(0x73BF,7f) → FRAME(0x73D9,7f) → LOOP`<br>`0xC9:0x47B6`: `FRAME(0x39EA,4f) → FRAME(0x39FF,4f) → FRAME(0x3A06,4f) → FRAME(0x3A0D,4f) → FRAME(0x3A22,6f) → FRAME(0x3A29,4f) → FRAME(0x3A30,4f) → FRAME(0x0001,6f) → FRAME(0x3A37,4f) → SFX(0x19) → FRAME(0x3A43,4f) → FRAME(0x3A58,4f) → FRAME(0x3A72,6f)` | Unused/cut formula. Regeneration buff granting passive periodic HP ticks. |
| `0x38` | **Revealer** | 0x4002 | 0 | 2 Ash<br>1 Wax | `0x1C` | `0xC9:0x4CAB`: `FRAME(0x4997,5f) → FRAME(0x499E,5f) → FRAME(0x49A5,5f) → FRAME(0x49AC,5f) → FRAME(0x49B3,5f) → FRAME(0x49AC,5f) → FRAME(0x49A5,5f) → FRAME(0x499E,5f) → LOOP` | Glowing alchemy powder reveals invisible bridges across chasms. |
| `0x3A` | **Revive** | 0x1400 | 12 | 3 Root<br>1 Bone | `0x1A` | `0xC9:0x4CAB`: `FRAME(0x4997,5f) → FRAME(0x499E,5f) → FRAME(0x49A5,5f) → FRAME(0x49AC,5f) → FRAME(0x49B3,5f) → FRAME(0x49AC,5f) → FRAME(0x49A5,5f) → FRAME(0x499E,5f) → LOOP` | Target restricted to downed Dog. Revives with partial calculated HP. |
| `0x3C` | **Slow Burn** | All Enemies | 1 | 1 Iron<br>1 Brimstone | `0x34` | `0xC9:0x4A97`: `FRAME(0x45CE,1f) → FRAME(0x45DA,1f) → FRAME(0x45CE,1f) → FRAME(0x45E6,1f) → FRAME(0x45CE,1f) → FRAME(0x45DA,1f) → FRAME(0x45CE,1f) → FRAME(0x45E6,1f) → FRAME(0x45F2,1f) → FRAME(0x45FE,1f) → FRAME(0x45F2,1f) → FRAME(0x460A,1f)`<br>`0xC9:0x45FA`: `FRAME(0x30EE,4f) → SFX(0x17) → FRAME(0x30F5,4f) → FRAME(0x30FC,4f) → FRAME(0x3108,4f) → FRAME(0x3114,4f) → FRAME(0x3120,4f) → FRAME(0x312C,4f) → FRAME(0x3141,4f) → FRAME(0x315B,4f) → FRAME(0x3175,4f) → FRAME(0x3199,4f) → FRAME(0x31D1,4f)` | Unused/cut formula. Applies lingering burning damage ticks over time. |
| `0x3E` | **Speed** | Party | 25 | 1 Wax<br>2 Water | `0x0C` | `0xC9:0x4EE7`: `FRAME(0x55C2,5f) → FRAME(0x55C9,5f) → FRAME(0x55D0,5f) → FRAME(0x55D7,5f) → SFX(0x41) → FRAME(0x55DE,5f) → FRAME(0x55E5,5f) → FRAME(0x55EC,5f) → FRAME(0x55F8,5f) → SHEET(0xCF:0x5604) → 0x05 → SFX(0x46) → SHEET(0xCF:0x562D) → 0x05 → SHEET(0xCF:0x5656)` | Afterimage trail effect. Increases walking and attack charge speed for 60s. |
| `0x40` | **Sting** | All Enemies | 75 | 2 Water<br>1 Vinegar | `0x16` | `0xC9:0x5014`: `FRAME(0x6220,6f) → FRAME(0x622C,6f) → FRAME(0x6238,6f) → FRAME(0x624D,6f) → FRAME(0x6271,6f) → FRAME(0x629A,6f) → FRAME(0x62BE,6f) → SFX(0x33) → FRAME(0x62E7,6f) → FRAME(0x6306,6f) → SFX(0x33) → FRAME(0x632A,6f) → FRAME(0x6358,6f) → SFX(0x33)` | Swarm of sharp energy needles rapidly drill into enemy hitboxes. |
| `0x42` | **Stop** | All Enemies | 0 | 2 Wax<br>1 Crystal | `0x38` | `0xC9:0x55B8`: `FRAME(0x0BF2,4f) → FRAME(0x0BF9,4f) → FRAME(0x0BF2,4f) → FRAME(0x0BF9,4f) → FRAME(0x0C00,4f) → FRAME(0x0C07,4f) → FRAME(0x0C00,4f) → FRAME(0x0C07,4f) → FRAME(0x0C0E,4f) → FRAME(0x0C15,4f) → FRAME(0x0C0E,4f) → FRAME(0x0C15,32f)`<br>`0xC9:0x47B6`: `FRAME(0x39EA,4f) → FRAME(0x39FF,4f) → FRAME(0x3A06,4f) → FRAME(0x3A0D,4f) → FRAME(0x3A22,6f) → FRAME(0x3A29,4f) → FRAME(0x3A30,4f) → FRAME(0x0001,6f) → FRAME(0x3A37,4f) → SFX(0x19) → FRAME(0x3A43,4f) → FRAME(0x3A58,4f) → FRAME(0x3A72,6f)` | Unused/cut formula. Time freeze effect halting enemy frames and AI. |
| `0x44` | **Super Heal** | 0x0208 | 62 | 2 Ethanol<br>1 Acorn | `0x36` | `0xC9:0x4683`: `SFX(0x17) → FRAME(0x349D,6f) → FRAME(0x34A4,6f) → FRAME(0x34AB,6f) → FRAME(0x34B2,6f) → FRAME(0x34B9,6f) → FRAME(0x34C0,6f) → FRAME(0x34C7,6f) → FRAME(0x34EB,6f) → FRAME(0x350F,6f) → FRAME(0x3533,6f) → FRAME(0x3557,6f) → FRAME(0x3594,6f)`<br>`0xC9:0x4CD4`: `SHEET(0xCF:0x49BA) → SFX(0x3F) → FRAME(0x49E8,5f) → FRAME(0x49F4,5f) → FRAME(0x4A00,5f) → FRAME(0x4A15,5f) → FRAME(0x4A2F,5f) → FRAME(0x4A4E,5f) → FRAME(0x4A72,5f) → FRAME(0x4A9B,5f) → FRAME(0x4AC9,5f) → FRAME(0x4AF7,5f) → FRAME(0x4B2F,5f)`<br>`0xC9:0x4CD4`: `SHEET(0xCF:0x49BA) → SFX(0x3F) → FRAME(0x49E8,5f) → FRAME(0x49F4,5f) → FRAME(0x4A00,5f) → FRAME(0x4A15,5f) → FRAME(0x4A2F,5f) → FRAME(0x4A4E,5f) → FRAME(0x4A72,5f) → FRAME(0x4A9B,5f) → FRAME(0x4AC9,5f) → FRAME(0x4AF7,5f) → FRAME(0x4B2F,5f)` | Major full-party heal. Dual ascending green light pillars on Boy & Dog. |

---

## 6. Unused Alchemy & Feasibility of Adding More

### 6.1 Unused & Cut Spells in Vanilla ROM

Several formulas exist partially or completely in the ROM data tables but are never taught in vanilla gameplay:

1. **`REGROWTH` (Index `0x36`):**
   - Base power = 2, target = `BOY_DOG_BOTH` (`0x0008`), cost = 1 Acorn + 2 Water.
   - Intended as a periodic HP regeneration status effect (Status 0x28 handler).
   - No alchemist NPC in vanilla grants this formula.
2. **`SLOW BURN` (Index `0x3C`):**
   - Base power = 1, target = `ENEMY_ALL` (`0x2010`), cost = 1 Iron + 1 Brimstone.
   - Designed as long-duration residual damage over time.
3. **`STOP` (Index `0x42`):**
   - Base power = 0, target = `ENEMY_ALL` (`0x2010`), cost = 2 Wax + 1 Crystal.
   - Status freeze effect; animation exists at `$9406`.
4. **`REFLECT` (Index `0x34`):**
   - Base power = 0, target = `BOY_DOG_BOTH` (`0x0008`), cost = 2 Grease + 1 Iron.
   - Status spell reflection; animation exists at `$95DC`.
5. **`LASER` (Index `0x28`):**
   - Cut early in development; reuses Acid Rain animation pointer (`$86F0`); zero base power.
6. **16 Call Bead Spells:**
   - Spells like `Heat Wave`, `Storm`, `Life Spark`, `Confound`, `Regenerate`, `Aura`, `Shield`, `Electra Bolt`, and `Plague` have complete animations and effect routines in ROM Banks `$8F` and `$91`, but are wired exclusively through the Call Bead system rather than the Alchemy ring menu.

### 6.2 Constraints on Adding New Alchemy

| Subsystem | Capacity | Limiting Factor | Expansion Strategy |
|---|---|---|---|
| **Learned Flags** | 40 slots | Byte `$225C` has **5 unused bits** (`0x08`..`0x80`). | Can add up to 5 formulas without modifying SRAM structure. |
| **WRAM Level Tables** | Exactly 35 slots | `$7E2F52..$7E2F74` (XP) and `$7E2F98..$7E2FBA` (Level) abut `$7E2FDE` (ingredient counters). | Adding past 35 requires relocating the XP/Level tables to higher unused WRAM. |
| **ROM Master Tables** | Exactly 35 entries | Tables at `$C4:5BF5` (Target), `$C4:5E6B` (Power), and `$C4:601F` (Cost) are followed immediately by currency strings ("talons\0"). | Repoint table pointers in Bank `$C4` to expanded ROM (e.g. `!ROM_EXTENSION = $FE0000`). |
| **Ring Menu UI** | 9 equipped slots | Ring menu stores 9 active slots (`$0AD2..$0ADA`). | Selection menu dynamically displays any learned formula from the flag bitfield. |
| **Animation VM** | Unlimited | Opcode interpreter supports arbitrary scripts in expanded ROM. | Author new bytecode sequences in expanded bank using Asar or Everscript `@install`. |
