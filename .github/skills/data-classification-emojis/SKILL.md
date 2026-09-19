---
name: data-classification-emojis
description: Standard emoji taxonomy and classification rules for Secret of Evermore bit flags, persistent WRAM, objects, and Metroidvania barriers.
---

# Data Classification & Emoji Legend

To maintain clarity and immediate visual recognition across memory maps, room documentation, and disassembly analyses, all Secret of Evermore data is classified using a standardized emoji taxonomy.

---

## 1. Master Emoji Taxonomy

| Category | Emoji | Scope & Meaning | Examples |
|---|:---:|---|---|
| **Story / Progress** | 📖 | Plot flags, quest switches, scene states, boss defeats | Raptors defeated (`$225F&0x40`), WindWalker (`$22DC&0x08`) |
| **Metroidvania Gates** | 🚪 | Ability barriers, weapon gates, locked doors | Axe-2 rubble, Spear switches, Levitate gates |
| **Ingredients** | 🌿 | Alchemy ingredients in inventory or sniff spots | Wax, ash, root, clay, water, dry ice, vinegar |
| **Consumables** | 🧪 | Usable inventory recovery items | Petals, nectar, honey, biscuits, call beads |
| **Rare / Key Items** | 💎 | Unique progression items, charms, story artifacts | Wheel, diamond eyes, gauge, thimble, silver collar |
| **Weapons** | ⚔️ | Swords, axes, spears, bazooka, weapon levels | Bone Crusher, Knight's Basher, Lance, Particle Bomb |
| **Armor** | 🛡️ | Helmets, vests, bracers, shields, dog collars | Grass Vest, Bronze Helmet, Chitin Armband, Spikester |
| **Trading Goods** | 🏺 | Nobilia market barter goods | Rice, spice, beads, perfume, chickens, ceramic pots |
| **Currency** | 💰 | World currencies per time period | Talons (`$0AC6`), Jewels (`$0AC9`), Gold (`$0ACC`), Credits (`$0ACF`) |
| **Alchemy Spells** | ⚗️ | Formula declarations, active spell slots | Hard ball, crush, heal, sting, corrosion, acid rain |
| **Gourds / Chests** | 🫙 | Persistent loot containers in rooms (`$2268..$22AA`) | Map ref gourds, pots, treasure boxes |
| **Sniff Spots** | 👃 | Hidden dog discovery spots, bonus yield tracking | Ingredient sniff locations, bonus loot (`$2461`) |
| **Protagonist / Boy** | 🧑 | Player stats, direct page variables, level | Boy Max HP (`$0A35`), attack (`$0A47`), XP (`$0A49`) |
| **Companion / Dog** | 🐶 | Dog stats, AI state, aggression settings | Dog Max HP (`$0A7F`), Dog level (`$0A9A`) |
| **System & Engine** | ⚙️ | Engine flags, frame counters, joypad inputs | Frame counter (`$0100`), P1 Input (`$0104`), ring pointers |
| **Camera & Viewport** | 🎥 | Camera locks, scroll limits, panning targets | Viewport coordinates, scroll boundary triggers |
| **Music & Audio** | 🎵 | Background tracks, sound effect triggers | Music enum IDs, SPC700 sound triggers |
| **Loot & Drops** | 🎁 | Enemy drop tables, prize slots | Prize slot item IDs, drop rates, drop quantities |

---

## 2. Formatting & Documentation Rules

### 2.1 Metroidvania Gates (`🚪`)
- **Strict Rule:** Never label a weapon/alchemy gate with decorative or flavour words like "candles", "lights", or "braziers". Always use the functional term (barrier, gate, locked door) prefixed with `🚪`.
- In Memory Access tables: `🚪 Axe-2 stone rubble barrier [0x3C]` or `🚪 Spear chasm switch [0x18]`.

### 2.2 Gourds and Pickup Containers (`🫙`)
- Every persistent pickup must be recorded as an individual bit row in `.github/memory-map.md`.
- Format: `🫙 Gourd MAP REF 0xNN looted (ItemName) [0xROOM] (0xBIT)`.

### 2.3 Sniff Spots (`👃`)
- Every sniff location must be documented per bit flag.
- Format: `👃 Sniffed IngredientName (#N) [0xROOM] (0xBIT)`.
- If the script writes `$2461` (`NEXT_ADD`), note the bonus yield added for subsequent visits.

### 2.4 Multi-Bit Bitfield Representation
When documenting bitfield bytes in tables, use HTML breaks (`<br>`) for individual bits:
```markdown
| Address | Name | Type | Notes |
|---|---|---|---|
| 0x2260 | 📖 THRAXX dead (0x10)<br>📖 MAGMAR dead (0x40)<br>? (0x01/0x02/0x04/0x08/0x20/0x80) | Byte [SRAM] | Boss persistence flags |
```

