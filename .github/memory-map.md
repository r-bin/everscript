
# Secret of Evermore RAM Map

## Emoji Legend

| Emoji | Category | Examples |
|-------|----------|----------|
| 📖 | Story flags | plot progress, quest triggers |
| 🌿 | Ingredients | wax, ash, roots, clay |
| 🧪 | Consumables | petals, nectar, biscuits |
| 💎 | Rare/key items | wheel, diamond eyes, keys |
| ⚔️ | Weapons | sword, spear, bazooka |
| 🛡️ | Armor | armor, helmet |
| 🏺 | Trading goods | rice, spice, beads, perfume |
| 💰 | Currency | talons, jewels, gold coins |
| ⚗️ | Alchemy spells | hard ball, crush, heal, call beads |
| 🫙 | Gourds/chests | gourd, chest |
| 👃 | Sniff spots | scent flags |
| 🧑 | Protagonist/boy | boy |
| 🐶 | Protagonist/dog | dog |
| ⚙️ | System/engine | engine, core system flags |
| 🎥 | System/camera | camera position, scroll |
| 🎵 | System/music | music, sound, sfx |
| 🎁 | Loot | loot item, loot amount, loot object |


| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x0100 | ⚙️ FRAME_COUNTER_1 | Word | |
| 0x0102 | ⚙️ FRAME_COUNTER_2 | Word | |
| 0x0104 | ⚙️ INPUT_P1 | Word | |
| 0x0341 | ⚙️ LAST_ENTITY | Word | |
| 0x07a4 | ⚙️ RING_MENU_WEAPON | Word | [pointer] |
| 0x07c8 | ⚙️ RING_MENU_CONSUMABLES | Word | [pointer] |
| 0x0810 | ⚙️ RING_MENU_BOY | Word | [pointer] |
| 0x0834 | ⚙️ RING_MENU_DOG | Word | [pointer] |
| 0x0a35 | 🧑 BOY_MAX_HP | Word | |
| 0x0a47 | 🧑 BOY_HIT | Word | |
| 0x0a49 | 🧑 BOY_XP | Word | |
| 0x0a4b | 🧑 BOY_XP_2 | Word | High word |
| 0x0a50 | 🧑 BOY_LEVEL | Word | |
| 0x0a7f | 🐶 DOG_MAX_HP | Word | |
| 0x0a9a | 🐶 DOG_LEVEL | Word | |
| 0x0aba | ⚔️ CURRENT_WEAPON | Byte | |
| 0x0abe | 🛡️ CURRENT_ARMOR_COLLAR | Word | |
| 0x0ac0 | 🛡️ CURRENT_ARMOR_CHEST | Word | |
| 0x0ac2 | 🛡️ CURRENT_ARMOR_HELM | Word | |
| 0x0ac4 | 🛡️ CURRENT_ARMOR_GLOVE | Word | |
| 0x0ac6 | 💰 TALONS | Word | |
| 0x0ac9 | 💰 JEWELS | Word | |
| 0x0acc | 💰 GOLD | Word | |
| 0x0acf | 💰 CREDITS | Word | |
| 0x0ad2…0x0ada | ⚗️ SELECTED_ALCHEMY_0…8 | Byte×9 | |
| 0x0adb | CURRENT_WEAPON (buggy) | Byte | Use 0x235f instead |
| 0x0add | ⚔️ LEVEL_FIST | Word | Unused |
| 0x0adf | ⚔️ LEVEL_1_SWORD | Word | |
| 0x0ae1 | ⚔️ LEVEL_2_SWORD | Word | |
| 0x0ae3 | ⚔️ LEVEL_3_SWORD | Word | |
| 0x0ae5 | ⚔️ LEVEL_4_SWORD | Word | |
| 0x0ae7 | ⚔️ LEVEL_1_AXE | Word | |
| 0x0ae9 | ⚔️ LEVEL_2_AXE | Word | |
| 0x0aeb | ⚔️ LEVEL_3_AXE | Word | |
| 0x0aed | ⚔️ LEVEL_4_AXE | Word | |
| 0x0aef | ⚔️ LEVEL_1_SPEAR | Word | |
| 0x0af1 | ⚔️ LEVEL_2_SPEAR | Word | |
| 0x0af3 | ⚔️ LEVEL_3_SPEAR | Word | |
| 0x0af5 | ⚔️ LEVEL_4_SPEAR | Word | |
| 0x0af7 | ⚔️ LEVEL_BAZOOKA | Word | |
| 0x0b07 | ⚔️ LEVEL_DOG | Word | |
| 0x0b09 | 🧑 BOY_COMBATIVENESS | Word | |
| 0x0b0d | 🐶 DOG_COMBATIVENESS | Word | |
| 0x0b19 | ⚙️ TIMER_1 | Word | |
| 0x0b1b | ⚙️ TIMER_2 | Word | |
| 0x0b83 | ⚙️ ? | Word | Written 0x8000 by opcode 0x27 (Fade-out screen); used in room [0x38] |
| 0x0ba1 | ⚙️ RING_MENU_SHOP | Word | [pointer] |
| 0x0bfe | ⚙️ RING_MENU_BOY_ARMOR_CHEST | Word | [pointer] |
| 0x0c23 | ⚙️ RING_MENU_BOY_ARMOR_HELM | Word | [pointer] |
| 0x0c47 | ⚙️ RING_MENU_BOY_ARMOR_ARMLET | Word | [pointer] |
| 0x0c6b | ⚙️ RING_MENU_DOG_ARMOR | Word | [pointer] |
| 0x0c8f | ⚙️ RING_MENU_WEAPON_BAZOOKA | Word | [pointer] |
| 0x0cb5 | ⚙️ RING_MENU_CONSUMABLES_CALLBEADS_INNER | Word | [pointer] |
| 0x0cd9 | ⚙️ RING_MENU_CONSUMABLES_CALLBEADS | Word | [pointer] |
| 0x0ea2 | ? | Word | Paired with $0eac; written by opcode 0x3f (NPC script setup); "set in lots of places" |
| 0x0eac | ? | Word | Paired with $0ea2; holds NPC script addresses; written by opcode 0x3f |
| 0x0ec2 | ⚙️ POINTER_NEXT_PROJECTILE_SLOT | Word | |
| 0x0ec6 | ⚙️ COPY_INPUT_P1 | Word | |
| 0x0f5a | ⚙️ RING_MENU_DEBUG | Word | [pointer] |
| 0x1278…0x1286 | ⚙️ PALETTE_SLOT_1…8 | Word×4 | Palette slots 1–8 |
| 0x128e | ⚙️ ANIMATION_START_COPY | Word | |
| 0x1290 | ⚙️ ANIMATION_START | Word | |
| 0x1292…0x1371 | ⚙️ ANIMATION_STACK | — | Animation structs |
| 0x2210…0x2233 | 🧑 BOY_NAME | Byte×35 [SRAM] | |
| 0x2234…0x2257 | 🐶 DOG_NAME | Byte×35 [SRAM] | |
| 0x2258 | ⚗️ ACID_RAIN (0x01)<br>⚗️ ATLAS (0x02)<br>⚗️ BARRIER (0x04)<br>⚗️ CALL_UP (0x08)<br>⚗️ CORROSION (0x10)<br>⚗️ CRUSH (0x20)<br>⚗️ CURE (0x40)<br>⚗️ DEFEND (0x80) | Byte [SRAM] | ATLAS taught in [0x0c] Inn (Atlas merchant step-on); BARRIER taught in [0x4d] palace (Horace, Path C first meeting) |
| 0x2259 | ⚗️ DOUBLE_DRAIN (0x01)<br>⚗️ DRAIN (0x02)<br>⚗️ ENERGIZE (0x04)<br>⚗️ ESCAPE (0x08)<br>⚗️ EXPLOSION (0x10)<br>⚗️ FIREBALL (0x20)<br>⚗️ FIRE_POWER (0x40)<br>⚗️ FLASH (0x80) | Byte [SRAM] | |
| 0x225a | ⚗️ FORCE_FIELD (0x01)<br>⚗️ HARD_BALL (0x02)<br>⚗️ HEAL (0x04)<br>⚗️ LANCE (0x08)<br>⚗️ LASER (0x10)<br>⚗️ LEVITATE (0x20)<br>⚗️ LIGHTNING_STORM (0x40)<br>⚗️ MIRACLE_CURE (0x80) | Byte [SRAM] | |
| 0x225b | ⚗️ NITRO (0x01)<br>⚗️ ONE_UP (0x02)<br>⚗️ REFLECT (0x04)<br>⚗️ REGROWTH (0x08)<br>⚗️ REVEALER (0x10)<br>⚗️ REVIVE (0x20)<br>⚗️ SLOW_BURN (0x40)<br>⚗️ SPEED (0x80) | Byte [SRAM] | |
| 0x225c | ⚗️ STING (0x01)<br>⚗️ STOP (0x02)<br>⚗️ SUPER_HEAL (0x04)<br>? (0x08/0x10/0x20)<br>FE call beads? (0x40)<br>📖 Horace call beads [0x09] (0x80) | Byte [SRAM] | 0x80 set and checked in Aegis kill script [0x09]; awarded by Horace after Aegis defeated |
| 0x225d | ? (0x01/0x02/0x04)<br>📖 MARKET_TIMER_EXPIRED (0x08)<br>? (0x10/0x20/0x40)<br>📖 NPC 0x3e #1 position-shifted [0x3b] (0x80) | Byte [SRAM] | Story flag range; seen in Prehistoria scripts |
| 0x225e | 📖 NPC 0x3e #2 position-shifted [0x3b] (0x01)<br>📖 NPC 0x3e #3 position-shifted [0x3b] (0x02)<br>📖 NPC 0x3c #1 position-shifted [0x3b] (0x04)<br>📖 NPC 0x3c #2 position-shifted [0x3b] (0x08)<br>📖 NPC 0x3c #3 position-shifted [0x3b] (0x10)<br>? (0x20)<br>📖 Viper Commander spawn pending [0x3b] (0x40)<br>📖 Talked to Blimp in hut? [0x51] (0x80) | Byte [SRAM] | Story flag range; seen in Prehistoria scripts |
| 0x225f | 📖 BLIMP_BRIDGE (0x01)<br>📖 Levitate hint shown? [0x51] (0x02)<br>? (0x04)<br>📖 Pipe Maze switch pressed [0x3d/0x3e] (0x08)<br>📖 Pipe Maze Raptor shown [0x3e] (0x10)<br>📖 Vigor defeated [0x09] (0x20)<br>📖 RAPTORS (0x40)<br>📖 Village post-Thraxx msg shown [0x51/0x6a] (0x80) | Byte [SRAM] | Story progress flags; 0x20 set in Aegis kill script [0x09] |
| 0x2260 | ? (0x01/0x02/0x04/0x08)<br>📖 THRAXX (0x10)<br>📖 Magmar fight started [0x3f] (0x20)<br>📖 MAGMAR (0x40)<br>⚙️ Crustacia indoors — Monk shop proximity [0x30] (0x80) | Byte [SRAM] | Story progress flags; 0x80 set after first Monk amulet shop interaction in [0x30] |
| 0x2261 | ⚙️ DOG_UNAVAILABLE (0x01)<br>⚙️ BOY_UNAVAILABLE (0x02)<br>? (0x04/0x08)<br>📖 Gloves of Ra traded [0x0a] (0x10)<br>💎 ARMOR_POLISH (0x20)<br>💎 CHOCOBO_EGG (0x40)<br>💎 INSECT_INCENSE (0x80) | Byte [SRAM] | Story progress flags |
| 0x2262 | 💎 JADE_DISK (0x01)<br>💎 JAGUAR_RING (0x02)<br>💎 MAGIC_GOURD (0x04)<br>💎 MOXA_STICK (0x08)<br>💎 ORACLE_BONE (0x10)<br>💎 RUBY_HEART (0x20)<br>💎 SILVER_SHEATH (0x40)<br>💎 STAFF_OF_LIFE (0x80) | Byte [SRAM] | |
| 0x2263 | 💎 SUN_STONE (0x01)<br>💎 THUGS_CLOAK (0x02)<br>💎 WIZARDS_COIN (0x04)<br>? (0x08/0x10)<br>📖 Silver Sheath traded [0x0a] (0x20)<br>? (0x40)<br>📖 Moxa Stick trade available [0x0a] (0x80) | Byte [SRAM] | |
| 0x2264 | 💎 DIAMOND_EYE (0x01)<br>💎 DIAMOND_EYES (0x02)<br>💎 GAUGE (0x04)<br>💎 WHEEL (0x08)<br>💎 QUEENS_KEY (0x10)<br>💎 ENERGY_CORE (0x20)<br>🫙 roots gourd obj0 [0x51] (0x40)<br>🫙 water gourd obj1 [0x51] (0x80) | Byte [SRAM] | |
| 0x2265 | 🫙 water gourd obj2 [0x51] (0x01)<br>🫙 water gourd obj3 [0x51] (0x02)<br>🫙 money gourd obj4 [0x51] (0x04)<br>🫙 nectar gourd obj5 [0x51] (0x08)<br>🫙 water gourd obj6 [0x51] (0x10)<br>🫙 water gourd obj7 [0x51] (0x20)<br>🫙 clay gourd obj8 [0x51] (0x40)<br>🫙 money gourd obj9 [0x51] (0x80) | Byte [SRAM] | Object persistence flags:<br>Act1 Huts [0x51] |
| 0x2266 | 🫙 clay gourd obj10 [0x51] (0x01)<br>🫙 water gourd obj11 [0x51] (0x02)<br>🫙 roots gourd obj13 [0x51] (0x04)<br>🫙 roots gourd obj12 [0x51] (0x08)<br>? (0x10)<br>🫙 roots gourd obj14 [0x51] (0x20)<br>🫙 water gourd obj15 [0x51] (0x40)<br>🫙 call beads/biscuit obj17 [0x51] (0x80) | Byte [SRAM] | Object persistence flags:<br>Act1 Huts [0x51] |
| 0x2267 | 🫙 water gourd obj16 [0x51] (0x01)<br>🫙 petal gourd obj18 [0x51] (0x02)<br>🫙 clay gourd obj19 [0x51] (0x04)<br>🫙 water gourd obj20 [0x51] (0x08)<br>🫙 water gourd obj21 [0x51] (0x10)<br>🫙 water gourd obj22 [0x51] (0x20)<br>🫙 water gourd obj23 [0x51] (0x40)<br>? (0x80) | Byte [SRAM] | Object persistence flags:<br>Act1 Huts [0x51] |
| 0x2268 | 🫙 water gourd obj24 [0x51] (0x01)<br>🫙 gourd obj0 [0x26] (0x02)<br>🫙 clay gourd obj1 [0x26] (0x04)<br>🫙 ash gourd obj2 [0x26] (0x08)<br>🫙 Nectar gourd obj1 [0x41] (0x10) // MISMATCH: dumper labels as “Gourd in south Jungle”<br>🫙 Clay gourd obj0 [0x41] (0x20) // MISMATCH: dumper labels as “Gourd in south Jungle”<br>🫙 petal gourd obj0 [0x38] (0x40)<br>🫙 oil gourd obj1 [0x38] (0x80) | Byte [SRAM] | Object persistence flags:<br>[0x38] South Jungle / Start<br>[0x26] West area with Defend<br>[0x41] North Jungle<br>[0x51] Act1 Huts |
| 0x2269 | 🫙 petal gourd obj2 [0x38] (0x01)<br>🫙 shell hat gourd obj3 [0x38] (0x02)<br>🫙 nectar gourd obj4 [0x38] (0x04)<br>🫙 money gourd obj5 [0x38] (0x08)<br>🫙 Wax gourd obj0 [0x25] (0x10)<br>? (0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start [0x38]<br>Fire Eyes' Village [0x25] |
| 0x226a | ? (0x01)<br>🫙 Gourd MAP REF 0x07 looted (Wax) [0x3e] (0x02)<br>🫙 Gourd MAP REF 0x00 looted (Wax alt / Oil; gates OBJ 0 in sub-rooms 1/7) [0x3e] (0x04)<br>🫙 Gourd MAP REF 0x01 looted (Oil; gates OBJ 1 in sub-room 7) [0x3e] (0x08)<br>🫙 Gourd MAP REF 0x02 looted (Clay alt; gates OBJ 2 in sub-room 4) [0x3e] (0x10)<br>🫙 Gourd MAP REF 0x03 looted (Ash; gates OBJ 3 in sub-room 8) [0x3e] (0x20)<br>🫙 Gourd MAP REF 0x02 looted (Clay; $24c3==10; gates OBJ 2 in sub-room 10) [0x3e] (0x40)<br>🫙 Gourd MAP REF 0x00 looted (Oil; $24c3==7; gates OBJ 0 in sub-room 7) [0x3e] (0x80) | Byte [SRAM] | Object persistence + puzzle state flags [0x3e] |
| 0x226b | 🫙 Gourd MAP REF 0x0f looted (Call Beads) [0x4f] (0x01)<br>🫙 Gourd MAP REF 0x10 looted (200 Gold Coins) [0x4f] (0x02)<br>🫙 Gourd MAP REF 0x03 looted (Water) [0x30] (0x04)<br>🫙 Gourd MAP REF 0x01 looted (Clay) [0x30] (0x08)<br>🫙 Gourd MAP REF 0x06 looted (Wax) [0x30] (0x10)<br>🫙 Gourd MAP REF 0x05 looted (Water) [0x30] (0x20)<br>🫙 Gourd MAP REF 0x04 looted (Nectar) [0x30] (0x40)<br>🫙 Gourd MAP REF 0x02 looted (Nectar) [0x30] (0x80) | Byte [SRAM] | Object persistence flags — East of Crustacia [0x4f] gourds (low 2 bits); Crustacia Pirate Ship [0x30] gourds (high 6 bits); enter script unloads OBJ 1–6 based on these bits |
| 0x226c | 🫙 Petal gourd obj0 [0x59] (0x01)<br>🫙 Wax gourd obj1 [0x59] (0x02)<br>🫙 Crystal gourd obj2 [0x59] (0x04)<br>🫙 Clay gourd obj0x27 [0x59] (0x08)<br>🫙 Biscuit gourd obj0x28 [0x59] (0x10)<br>🫙 Clay gourd obj0x29 [0x59] (0x20)<br>🫙 Water gourd obj0x2a [0x59] (0x40)<br>? (0x80) // TODO: 8th gourd unidentified | Byte [SRAM] | Object persistence flags — Quick Sand Desert [0x59] |
| 0x226d | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40)<br>🫙 Gourd MAP REF 0x03 looted (Mud Pepper, DOG ONLY) [0x3b] (0x80) | Byte [SRAM] | Object persistence flags |
| 0x226e | 🫙 Gourd MAP REF 0x04 looted (Mud Pepper) [0x3b] (0x01)<br>🫙 Gourd MAP REF 0x05 looted (Petal) [0x3b] (0x02)<br>🫙 Gourd MAP REF 0x06 looted (Clay) [0x3b] (0x04)<br>🫙 Gourd MAP REF 0x07 looted (Roots) [0x3b] (0x08)<br>🫙 Gourd MAP REF 0x08 looted (Roots) [0x3b] (0x10)<br>🫙 Gourd MAP REF 0x0a looted (Water) [0x3b] (0x20)<br>🫙 Gourd MAP REF 0x0b looted (Money 100, DOG ONLY) [0x3b] (0x40)<br>? (0x80) | Byte [SRAM] | Object persistence flags — Volcano Room 2 [0x3b] |
| 0x226f | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40)<br>🫙 Petal gourd obj6 [0x67] (0x80) | Byte [SRAM] | Object persistence flags:<br>Bugmuck Exterior [0x67] |
| 0x2270 | 🫙 Biscuit gourd obj7 [0x67] (0x01)<br>🫙 Clay gourd obj8 [0x67] (0x02)<br>🫙 Water gourd obj9 [0x67] (0x04)<br>🫙 Crystal gourd obj10 [0x67] (0x08)<br>🫙 Petal gourd obj11 [0x67] (0x10)<br>🫙 Mammoth Guard gourd obj12 [0x67] (0x20)<br>🫙 Crystal gourd obj13 [0x67] (0x40)<br>? (0x80) | Byte [SRAM] | Object persistence flags — Bugmuck Exterior [0x67] |
| 0x2271 | ⚙️ Chest 1 (chestplate) opened [0x1e] (0x01)<br>🫙 Gourd MAP REF 0x02 looted (Petal) [0x1e] (0x02)<br>🫙 Gourd MAP REF 0x03 looted (Wax) [0x1e] (0x04)<br>🫙 Gourd MAP REF 0x04 looted (Call Beads) [0x1e] (0x08)<br>⚙️ Chest 2 (gauntlet) opened [0x1e] (0x10)<br>🫙 Gourd MAP REF 0x06 looted (Wax) [0x1e] (0x20)<br>🫙 Gourd MAP REF 0x07 looted (Call Beads) [0x1e] (0x40)<br>⚙️ Chest 3 (helmet) opened [0x1e] (0x80) | Byte [SRAM] | Object persistence flags — Arena Holding Room [0x1e] |
| 0x2272 | ⚙️ Special trigger OBJ 0 loaded [0x05] (0x01)<br>⚙️ Special trigger OBJ 1 loaded [0x05] (0x02)<br>🫙 Gourd MAP REF 0x06 looted (Water) [0x05] (0x04)<br>🫙 Gourd MAP REF 0x05 looted (Water) [0x05] (0x08)<br>🫙 Gourd MAP REF 0x07 looted (Limestone) [0x05] (0x10)<br>🫙 Gourd MAP REF 0x08 looted (Wax) [0x05] (0x20)<br>📖 OBJ 0 interaction trigger fired [0x13] (0x40)<br>? (0x80) | Byte [SRAM] | Object persistence flags — Between 'Mids and Halls [0x05]; bits 0x01/0x02 are set by conditional B-triggers (alchemy level check, $235f≥12 AND $2360==2) rather than gourd loots; 0x40 set by B-trigger in [0x13] crossroads (same conditional pattern) |
| 0x2273 | 🫙 oil gourd obj0 [0x34] (0x01)<br>🫙 wax gourd obj1 [0x34] (0x02)<br>🫙 wax gourd obj2 [0x34] (0x04)<br>🫙 Gourd MAP REF 0x00 looted (Wax) [0x2e] (0x08)<br>🫙 Gourd MAP REF 0x01 looted (Ash) [0x2e] (0x10)<br>? (0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>Strong Heart's Hut [0x34]<br>Blimp's Cave [0x2e] |
| 0x2274 | ? (0x01/0x02)<br>🫙 Gourd OBJ 13: Wax×3 [0x2d] (0x04)<br>🫙 Gourd OBJ 12: Ash×5 [0x2d] (0x08)<br>🫙 Gourd OBJ 10: Brimstone×3 [0x2d] (0x10)<br>🫙 Gourd OBJ 11: Wax×4 [0x2d] (0x20)<br>🫙 Nectar gourd obj0x37 [0x65] (0x40)<br>🫙 Wax gourd obj0x35 [0x65] (0x80) | Byte [SRAM] | Object persistence flags — Halls NE [0x2d] (MAP REFs 0x0a–0x0d) and Swamp Main Area [0x65] |
| 0x2275 | 🫙 Biscuit gourd obj0x36 [0x65] (0x01)<br>🫙 Oil gourd obj0x3b [0x65] (0x02)<br>🫙 Call Beads gourd obj0x3a [0x65] (0x04)<br>🫙 Roots gourd obj0x39 [0x65] (0x08) — also sets $2461=0x0001<br>🫙 Clay gourd obj0x38 [0x65] (0x10) — also sets $2461=0x0002<br>? (0x20)<br>🫙 Gourd MAP REF 0x01 looted (Acorns×1) [0x7d room 1 west] (0x40)<br>? (0x80) | Byte [SRAM] | Object persistence flags — Swamp Main Area [0x65] (bits 0x01–0x10); 0x40 = west-castle Room 1 B-trigger gourd at [61,2b] in [0x7d] |
| 0x2276 | 🫙 Gourd MAP REF 0x01 looted (west R2) [0x7d room 2 west] (0x01)<br>? (0x02/0x04/0x08/0x10)<br>🫙 Gourd MAP REF 0x20 looted (west lobby OBJ 0) [0x7d room 5 west] (0x20)<br>🫙 Gourd MAP REF 0x40 looted (Water×5) [0x7d room 6 west] (0x40)<br>🫙 Gourd MAP REF 0x80 looted (Vinegar×3) [0x7d room 6 west] (0x80) | Byte [SRAM] | Object persistence flags — Ebon Keep/Ivor Tower Interior [0x7d] west-castle gourd byte 0; 0x20=lobby OBJ 0 unload flag; 0x40=[70,12] room 6 west; 0x80=[73,12] room 6 west |
| 0x2277 | 🫙 Gourd MAP REF 0x01 looted (Petal×1) [0x7d room 6 west] (0x01)<br>🫙 Gourd MAP REF 0x02 looted (Gold-Plated Vest) [0x7d room 7 west] (0x02)<br>🫙 Gourd MAP REF 0x04 looted (Amulet of Annihilation) [0x7d room 7 west] (0x04)<br>🫙 Gourd MAP REF 0x08 looted (Nectar×3) [0x7d room 7 west] (0x08)<br>🫙 Gourd MAP REF 0x10 looted (Ash×5) [0x7d room 4 west] (0x10)<br>🫙 Gourd MAP REF 0x20 looted (Biscuit) [0x7d room 4 west] (0x20)<br>🫙 Gourd MAP REF 0x40 looted (Amulet of Annihilation) [0x7d room 6 west] (0x40)<br>🫙 Gourd MAP REF 0x80 looted (Ethanol×2) [0x7d room 8 west] (0x80) | Byte [SRAM] | Object persistence flags — [0x7d] west-castle gourd byte 1; all 8 bits used |
| 0x2278 | 🫙 Gourd MAP REF 0x01 looted (Ash×5) [0x7d room 8 west] (0x01)<br>🫙 Gourd MAP REF 0x02 looted (Limestone) [0x7d room 7 west] (0x02)<br>🫙 Gourd MAP REF 0x04 looted (Amulet of Annihilation) [0x7d room 1 west] (0x04)<br>🫙 Gourd MAP REF 0x08 looted (Gold×100) [0x7d room 1 west] (0x08)<br>🫙 Gourd MAP REF 0x10 looted (Acorns) [0x7d room 1 west] (0x10)<br>? (0x20)<br>🫙 Gourd MAP REF 0x40 looted (Honey×1) [0x7d room 1 east] (0x40)<br>? (0x80) | Byte [SRAM] | Object persistence flags — [0x7d] mixed west/east gourd byte 2; 0x01–0x10 = room 1 west / room 7–8 west; 0x40 = room 1 east B-trigger gourd at [61,2b] |
| 0x2279 | 🫙 Gourd MAP REF 0x01 looted (Wax×3) [0x7d room 2 east] (0x01)<br>? (0x02)<br>? (0x04)<br>? (0x08)<br>? (0x10)<br>🫙 Gourd MAP REF 0x20 looted (Call Beads) [0x7d room 1 east] (0x20)<br>🫙 Gourd MAP REF 0x40 looted (Wax×2) [0x7d room 6 east] (0x40)<br>🫙 Gourd MAP REF 0x80 looted (Ash×7) [0x7d room 6 east] (0x80) | Byte [SRAM] | Object persistence flags — [0x7d] east-castle gourd byte 3; 0x01=room 2 east [61,2b]; 0x20=room 1 east [15,12]; 0x40=room 6 east [70,12]; 0x80=room 6 east [73,12]; bits 0x02–0x10 used by enter script OBJ management (rooms 3–4, exact items uncertain) |
| 0x227a | 🫙 Gourd MAP REF 0x01 looted (Iron×4) [0x7d room 6 east] (0x01)<br>🫙 Gourd MAP REF 0x02 looted (Brimstone×1) [0x7d room 7 east] (0x02)<br>🫙 Gourd MAP REF 0x04 looted (Nectar) [0x7d room 7 east] (0x04)<br>🫙 Gourd MAP REF 0x08 looted (Ethanol×2) [0x7d room 7 east] (0x08)<br>🫙 Gourd MAP REF 0x10 looted (Ethanol×2) [0x7d room 4 east] (0x10)<br>🫙 Gourd MAP REF 0x20 looted (Vinegar×2) [0x7d room 4 east] (0x20)<br>🫙 Gourd MAP REF 0x40 looted (Limestone×1) [0x7d room 6 east] (0x40)<br>🫙 Gourd MAP REF 0x80 looted (Vinegar×5) [0x7d room 8 east] (0x80) | Byte [SRAM] | Object persistence flags — [0x7d] east-castle gourd byte 4; all 8 bits accounted for |
| 0x227b | 🫙 Gourd MAP REF 0x01 looted (Water×5) [0x7d room 8 east] (0x01)<br>🫙 Gourd MAP REF 0x02 looted (Crystal×1) [0x7d room 7 east] (0x02)<br>🫙 Gourd MAP REF 0x04 looted (Gold×50) [0x7d room 1 east] (0x04)<br>🫙 Gourd MAP REF 0x08 looted (Feather×1) [0x7d room 1 east] (0x08)<br>🫙 Gourd MAP REF 0x10 looted (Limestone×2) [0x7d room 1 east] (0x10)<br>📖 OBJ 31 collected [0x7d room 5 east] (0x20)<br>? (0x40)<br>⚗️ Horace's Aura collected [0x76] (0x80) | Byte [SRAM] | Object persistence flags — [0x7d] east-castle gourd byte 5 + [0x76] item flag; 0x01–0x10 = room 8/7/1 east gourds; 0x20 = room 5 east OBJ 31 unload flag; 0x80 = Horace's Aura spell tile in [0x76] |
| 0x227c | 🏺 Amulet of Annihilation found [0x76] (0x01)<br>🫙 Ash gourd looted [0x76 at 0a,39] (0x02)<br>🫙 Atlas Medallion gourd looted [0x76 at 15,46] (0x04)<br>? (0x08/0x10)<br>🫙 Gourd OBJ 20: Wings [0x55] (0x20)<br>🫙 Gourd OBJ 21: Call Beads [0x55] (0x40)<br>🫙 Gourd OBJ 22: Nectar [0x55] (0x80) | Byte [SRAM] | Object persistence flags — bits 0x01–0x04 = [0x76] South of Ivor Tower (Gate) items ($2517+=1 on 0x01); bits 0x20/0x40/0x80 = 'mids bottom [0x55] gourd byte 1: OBJs 20–22; enter script unloads those OBJs if set |
| 0x227d | 🫙 Gourd OBJ 0x21: Pixie Dust [0x55] (0x01)<br>🫙 Gourd OBJ 0x2b: Bone×2 [0x55] (0x02)<br>🫙 Gourd OBJ 0x22: Wax+1 [0x55] (0x04)<br>🫙 Gourd OBJ 0x2e: Biscuit [0x55] (0x08)<br>🫙 Gourd OBJ 23: Petal [0x55] (0x10)<br>🫙 Gourd OBJ 24: Biscuit [0x55] (0x20)<br>🫙 Gourd OBJ 25: Vinegar×2 [0x55] (0x40)<br>🫙 Gourd OBJ 26: Limestone+1 [0x55] (0x80) | Byte [SRAM] | Object persistence flags — 'mids bottom [0x55] gourd byte 2; full byte used by [0x55]; enter script unloads OBJs if bits set |
| 0x227e | 🫙 Gourd OBJ 27: Honey [0x55] (0x01)<br>🫙 Gourd OBJ 28: Ash×2 [0x55] (0x02)<br>🫙 Gourd OBJ 29: Roots [0x55] (0x04)<br>🫙 Gourd OBJ 30: Herbal Essence [0x55] (0x08)<br>🫙 Gourd OBJ 31: Call Beads [0x55] (0x10)<br>🫙 Gourd OBJ 0x20: Horace's Regenerate [0x55] (0x20)<br>🫙 Gourd OBJ 0x23: Dry Ice×2 [0x55] (0x40)<br>🫙 Gourd OBJ 2: Petal [0x56] (0x80) | Byte [SRAM] | Object persistence flags — 'mids bottom [0x55] gourd byte 3 / 'mids top [0x56] gourd byte 0; bits 0x01–0x40 = [0x55] OBJs 27–31/0x20/0x23; 0x80 = [0x56] OBJ 2; enter scripts unload OBJs if set |
| 0x227f | 🫙 Gourd OBJ 3: Water×3 [0x56] (0x01)<br>🫙 Gourd OBJ 4: Herbal Essence [0x56] (0x02)<br>🫙 Gourd OBJ 5: Limestone×2 [0x56] (0x04)<br>🫙 Gourd OBJ 6: Nectar [0x56] (0x08)<br>🫙 Gourd OBJ 7: Dry Ice×2 [0x56] (0x10)<br>🫙 Gourd OBJ 8: Ethanol×3 [0x56] (0x20)<br>🫙 Gourd OBJ 9: Wings [0x56] (0x40)<br>🫙 Gourd OBJ 10: Grease [0x56] (0x80) | Byte [SRAM] | Object persistence flags — 'mids top [0x56] gourd byte 1; full byte = OBJs 3–10; enter script unloads OBJs 3–10 if bits set (MAP REFs 0x03–0x0a) |
| 0x2280 | 🫙 Gourd OBJ 11: Gunpowder×2 [0x56] (0x01)<br>🫙 Gourd OBJ 12: Clay×3 [0x56] (0x02)<br>🫙 Gourd OBJ 13: Meteorite×2 [0x56] (0x04)<br>🫙 Gourd OBJ 14: Acorns [0x56] (0x08)<br>🫙 Gourd OBJ 15: Herbal Essence [0x56] (0x10)<br>🫙 Gourd OBJ 16: Biscuit [0x56] (0x20)<br>🫙 Gourd OBJ 17: Feather×4 [0x56] (0x40)<br>🫙 Gourd OBJ 18: Nectar [0x56] (0x80) | Byte [SRAM] | Object persistence flags — 'mids top [0x56] gourd byte 2; full byte = OBJs 11–18; enter script unloads OBJs 11–18 if bits set (MAP REFs 0x0b–0x12) |
| 0x2281 | 🫙 Gourd OBJ 19: Honey [0x56] (0x01)<br>🫙 Gourd OBJ 20: Iron×2 [0x56] (0x02)<br>🫙 Gourd OBJ 21: Petal [0x56] (0x04)<br>🫙 Gourd OBJ 22: Call Beads×2 [0x56] (0x08)<br>🫙 Gourd OBJ 23: Mushroom [0x56] (0x10)<br>🫙 Gourd OBJ 24: Limestone×3 [0x56] (0x20)<br>🫙 Gourd OBJ 7: Honey [0x57] (0x40)<br>🫙 Gourd OBJ 8: Herbal Essence [0x57] (0x80) | Byte [SRAM] | Object persistence flags — 'mids top [0x56] gourd byte 3 / 'mids basement [0x57] gourd byte 0; bits 0x01–0x20 = OBJs 19–24 [0x56] (MAP REFs 0x13–0x18); 0x40/0x80 = OBJs 7–8 [0x57] (MAP REFs 0x07–0x08) |
| 0x2282 | 🫙 Gourd OBJ 9: Pixie Dust [0x57] (0x01)<br>🫙 Gourd OBJ 10: Ethanol×3 [0x57] (0x02)<br>🫙 Gourd OBJ 11: Wings [0x57] (0x04)<br>🫙 Gourd OBJ 12: Call Beads [0x57] (0x08)<br>🫙 Gourd OBJ 13: Biscuit [0x57] (0x10)<br>? (0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags — 'mids basement [0x57] gourd byte 1; bits 0x01–0x10 = OBJs 9–13 (MAP REFs 0x09–0x0d); enter script unloads if bits set |
| 0x2283 | 🫙 Gourd OBJ 1: Nectar×1 [0x29] (0x08)<br>🫙 Gourd OBJ 2: Vinegar×1 [0x29] (0x10)<br>🫙 Gourd OBJ 6: Wings×1 [0x23] (0x20)<br>🫙 Gourd OBJ 7: Nectar×1 [0x23] (0x40)<br>🫙 Gourd OBJ 8: Brimstone×2 [0x23] (0x80)<br>? (0x01/0x02/0x04) | Byte [SRAM] | Object persistence flags — Halls main room [0x29] gourds (MAP REFs 0x01–0x02); Halls SW [0x23] gourds (MAP REFs 0x06–0x08) |
| 0x2284 | 🧪 Honey×2 gourd (OBJ 0x20) [0x28] (0x01)<br>⚔️ Cryo-Blast Projectiles crate looted [0x44] (0x02)<br>🌿 Dry Ice crate looted [0x47] (0x04)<br>🌿 Acorns crate looted [0x47] (0x08)<br>🫙 Honey gourd crate looted [0x47] (0x10)<br>⚔️ Thunderball Ammo crate looted [0x47] (0x20)<br>🛡️ Protector Ring crate looted [0x47] (0x40)<br>🫙 Particle Bombs / Nectar gourd looted [0x47] (0x80) | Byte [SRAM] | Object persistence flags — cross-room: 0x01 = Halls Collapsing Bridge [0x28] Honey×2 gourd (MAP REF 0x20); 0x02–0x80 = Omnitopia Storage Room [0x47] crates OBJ 0–5 + Particle Bombs; enter scripts unload each OBJ if corresponding bit set |
| 0x2285 | 🌿 Meteorite crate looted [0x47] (0x01)<br>🫙 Gourd OBJ 14: Pixie Dust×1 [0x24] (0x02)<br>🫙 Gourd OBJ 15: Call Beads×1 [0x24] (0x04)<br>🫙 Gourd OBJ 16: Brimstone×2 [0x24] (0x08)<br>🫙 Gourd OBJ 17: Ash×1 [0x24] (0x10)<br>🫙 Gourd MAP REF 0x01 looted (Honey×1) [0x79] (0x20)<br>🫙 Gourd MAP REF 0x02 looted (Mushroom×2) [0x79] (0x40)<br>🫙 Gourd MAP REF 0x03 looted (Water×5) [0x79] (0x80) | Byte [SRAM] | Object persistence flags — 0x01 = Omnitopia Storage Room [0x47] Meteorite crate (OBJ 6); 0x02–0x10 = Halls NW [0x24] gourds (MAP REFs 0x0e–0x11); 0x20/0x40/0x80 = Ivor Tower Sewers [0x79] gourds 1–3 |
| 0x2286 | 🫙 Gourd MAP REF 0x04 looted (Acorns×2) [0x79] (0x01)<br>🫙 Gourd MAP REF 0x05 looted (Iron×3) [0x79] (0x02)<br>🫙 Gourd MAP REF 0x06 looted (Oil×2) [0x79] (0x04)<br>🫙 Gourd MAP REF 0x07 looted (Biscuit×1) [0x79] (0x08)<br>🫙 Gourd MAP REF 0x08 looted (Call Beads×1) [0x79] (0x10)<br>🫙 Gourd MAP REF 0x09 looted (Acorns×1) [0x12] (0x20)<br>🫙 Gourd MAP REF 0x0a looted (Water×3) [0x12] (0x40)<br>🫙 Gourd MAP REF 0x0b looted (Ethanol×3) [0x12] (0x80) | Byte [SRAM] | Object persistence flags — 0x01–0x10 = Ivor Tower Sewers [0x79] gourds 4–8; 0x20/0x40/0x80 = Ebon Keep Sewers [0x12] gourds (OBJs 9–11) |
| 0x2287 | 🫙 Gourd MAP REF 0x0c looted (Ash×4) [0x12] (0x01)<br>🫙 Gourd MAP REF 0x0d looted (Pixie Dust×1) [0x12] (0x02)<br>🫙 Gourd MAP REF 0x00 looted (Feather×2) [0x60] (0x04)<br>🫙 Gourd MAP REF 0x01 looted (Brimstone×3) [0x60] (0x08)<br>🫙 Gourd MAP REF 0x02 looted (Acorns×1) [0x60] (0x10)<br>⚔️ Laser Lance (SPEAR_4) hidden item looted [0x46] (0x20)<br>🫙 Gourd MAP REF 0x00 looted (Call Beads×2) [0x4b] (0x40)<br>? (0x80) | Byte [SRAM] | Object persistence flags — 0x01/0x02 = Ebon Keep Sewers [0x12] gourds (OBJs 12–13); 0x04/0x08/0x10 = Ebon Keep Storage Room [0x60] gourds (MAP REFs 0x00–0x02); 0x20 = Laser Lance hidden item in Professor's Lab Ship Area [0x46] (OBJ 1, B-trigger `$2287|=0x20`); 0x40 = Call Beads gourd at Oglin Cave entrance [0x4b] (OBJ 0) |
| 0x2288 | ? (0x01/0x02)<br>📖 Received gift from Fire Eyes' Village huts [0x51] (0x04)<br>📖 talked to Defend guy [0x26] (0x08)<br>? (0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>West area with Defend [0x26]; 0x04 cleared in [0x6a] (Act 1→2 transition) |
| 0x2289 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x228a | 📖 Gate/door opened — OBJs 3+10 revealed [0x29] (0x10)<br>📖 OBJ 0 one-time reveal [0x24] / OBJ 8 removed in [0x29] (0x20)<br>📖 Ruins SE switch activated [0x2c] / OBJ 7 removed in [0x29] (0x40)<br>📖 OBJ 13 secret door opened [0x28] (0x80)<br>? (0x01/0x02/0x04/0x08) | Byte [SRAM] | Object persistence flags — cross-room: 0x10 set by gate-trigger step-on [10,05:12,07] in [0x29] (one-time); 0x20 set by step-on [20,07:22,09] in [0x24], also read in [0x29] to unload OBJ 8; 0x40 tagged as "Ruins SE switch activated" in [0x2c] disasm, also read in [0x29] to unload OBJ 7; 0x80 = one-time step-on [30,52:32,54] in [0x28] (OBJ 13 secret door) |
| 0x228b | 📖 FE visited pre-thraxx? [0x51] (0x01)<br>? (0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>0x01 tested in [0x51] east exit and FE First Encounter |
| 0x228c | 👃 Sniffed Water (#2) [0x65] (0x01)<br>👃 Sniffed Water (#3) [0x65] (0x02)<br>👃 Sniffed Water (#5) [0x65] (0x04)<br>👃 Sniffed Water (#6) [0x65] (0x08)<br>👃 Sniffed Water (#7) [0x65] (0x10)<br>👃 Sniffed Water (#9) [0x65] (0x20)<br>👃 Sniffed Water (#10) [0x65] (0x40)<br>👃 Sniffed Water (#15) [0x65] (0x80) | Byte [SRAM] | Sniff spot flags — Swamp Main Area [0x65] |
| 0x228d | 👃 Sniffed Water (#16) [0x65] (0x01)<br>👃 Sniffed Water (#19) [0x65] (0x02)<br>👃 Sniffed Water (#20) [0x65] (0x04)<br>👃 Sniffed Water (#21) [0x65] (0x08)<br>👃 Sniffed Roots (#0) [0x65] (0x10)<br>👃 Sniffed Roots (#1) [0x65] (0x20)<br>👃 Sniffed Roots (#4) [0x65] (0x40)<br>👃 Sniffed Roots (#8) [0x65] (0x80) | Byte [SRAM] | Sniff spot flags — Swamp Main Area [0x65] |
| 0x228e | 👃 Sniffed Roots (#12) [0x65] (0x01)<br>👃 Sniffed Roots (#13) [0x65] (0x02)<br>👃 Sniffed Roots (#14) [0x65] (0x04)<br>👃 Sniffed Roots (#17) [0x65] (0x08)<br>👃 Sniffed Roots (#18) [0x65] (0x10)<br>👃 Sniffed Oil (#61) [0x65] (0x20)<br>👃 Sniffed Oil (#11) [0x65] (0x40)<br>👃 Sniffed Oil (#60) [0x65] (0x80) | Byte [SRAM] | Sniff spot flags — Swamp Main Area [0x65] |
| 0x228f | ? (0x01)<br>👃 Sniffed Oil (#22) [0x65] (0x02)<br>👃 Sniffed Water (#0) [0x66] (0x04)<br>👃 clay sniff obj14 [0x38] (0x08)<br>👃 clay sniff obj28 [0x38] (0x10)<br>👃 roots sniff obj9 [0x38] (0x20)<br>👃 roots sniff obj30 [0x38] (0x40)<br>👃 roots sniff obj10 [0x38] (0x80) | Byte [SRAM] | Object persistence flags:<br>Swamp Main Area [0x65]<br>West of Swamp [0x66]<br>South Jungle / Start [0x38] |
| 0x2290 | 👃 roots sniff obj12 [0x38] (0x01)<br>👃 roots sniff obj13 [0x38] (0x02)<br>👃 roots sniff obj16 [0x38] (0x04)<br>👃 roots sniff obj19 [0x38] (0x08)<br>👃 roots sniff obj26 [0x38] (0x10)<br>? obj6 [0x38] (0x20) // TODO: type unknown, no B-trigger found<br>👃 ash sniff obj7 [0x38] (0x40)<br>👃 ash sniff obj23 [0x38] (0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start [0x38] |
| 0x2291 | 👃 ash sniff obj24 [0x38] (0x01)<br>👃 ash sniff obj27 [0x38] (0x02)<br>👃 water sniff obj8 [0x38] (0x04)<br>👃 water sniff obj11 [0x38] (0x08)<br>👃 water sniff obj29 [0x38] (0x10)<br>👃 water sniff obj15 [0x38] (0x20)<br>👃 water sniff obj17 [0x38] (0x40)<br>👃 water sniff obj18 [0x38] (0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start [0x38] |
| 0x2292 | 👃 water sniff obj20 [0x38] (0x01)<br>👃 water sniff obj21 [0x38] (0x02)<br>👃 water sniff obj22 [0x38] (0x04)<br>👃 water sniff obj25 [0x38] (0x08)<br>👃 Sniffed Ash (#18/#19/#20) [0x25] (0x10) — 3 respawnable spots share this bit<br>👃 Sniffed Ash (#14) [0x25] (0x20)<br>👃 Sniffed Ash (#15) [0x25] (0x40)<br>👃 Sniffed Ash (#16) [0x25] (0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start [0x38]<br>Fire Eyes' Village [0x25] |
| 0x2293 | 👃 Sniffed Water (#4) [0x25] (0x01)<br>👃 Sniffed Water (#6) [0x25] (0x02)<br>👃 Sniffed Water (#11) [0x25] (0x04)<br>👃 Sniffed Water (#12) [0x25] (0x08)<br>👃 Sniffed Water (#13) [0x25] (0x10)<br>👃 Sniffed Oil (#2) [0x25] (0x20)<br>👃 Sniffed Oil (#5) [0x25] (0x40)<br>👃 Sniffed Oil (#7) [0x25] (0x80) | Byte [SRAM] | Sniff spot flags — Fire Eyes' Village [0x25] |
| 0x2294 | 👃 Sniffed Oil (#8) [0x25] (0x01)<br>👃 Sniffed Roots (#1) [0x25] (0x02)<br>👃 Sniffed Roots (#3) [0x25] (0x04)<br>👃 Sniffed Roots (#9) [0x25] (0x08)<br>👃 Sniffed Roots (#10) [0x25] (0x10)<br>👃 Sniffed Roots (#1) [0x5b] (0x20)<br>👃 Sniffed Roots (#2) [0x5b] (0x40)<br>👃 Sniffed Roots (#5) [0x5b] (0x80) | Byte [SRAM] | Object persistence flags:<br>Fire Eyes' Village [0x25]<br>East Jungle [0x5b] |
| 0x2295 | 👃 roots sniff obj6 [0x5b] (0x01)<br>👃 roots sniff obj7 [0x5b] (0x02)<br>👃 water sniff obj0 [0x5b] (0x04)<br>👃 water sniff obj11 [0x5b] (0x08)<br>👃 water sniff obj12 [0x5b] (0x10)<br>👃 water sniff obj3 [0x5b] (0x20)<br>👃 water sniff obj4 [0x5b] (0x40)<br>👃 clay sniff obj13 [0x5b] (0x80) | Byte [SRAM] | Object persistence flags:<br>East jungle [0x5b] |
| 0x2296 | 👃 Sniffed Clay (#8) [0x5b] (0x01)<br>👃 Sniffed Clay (#9) [0x5b] (0x02)<br>👃 Sniffed Clay (#10) [0x5b] (0x04)<br>👃 Ash sniff obj23 [0x59] (0x08)<br>👃 Ash sniff obj24 [0x59] (0x10)<br>👃 Ash sniff obj25 [0x59] (0x20)<br>👃 Ash sniff obj26 [0x59] (0x40)<br>👃 Ash sniff obj27 [0x59] (0x80) | Byte [SRAM] | Object persistence flags:<br>East Jungle [0x5b]<br>Quick sand desert [0x59] |
| 0x2297 | 👃 Ash sniff obj28 [0x59] (0x01)<br>👃 Ash sniff obj29 [0x59] (0x02)<br>👃 Wax sniff obj22 [0x59] (0x04)<br>👃 Wax sniff obj45 [0x59] (0x08)<br>👃 Wax sniff obj46 [0x59] (0x10)<br>👃 Wax sniff obj44 [0x59] (0x20)<br>👃 Roots sniff obj30 [0x59] (0x40)<br>👃 Roots sniff obj31 [0x59] (0x80) | Byte [SRAM] | Object persistence flags:<br>Quick sand desert [0x59] |
| 0x2298 | 👃 Roots sniff obj32 [0x59] (0x01)<br>👃 Roots sniff obj33 [0x59] (0x02)<br>👃 Roots sniff obj34 [0x59] (0x04)<br>👃 Clay sniff obj35 [0x59] (0x08)<br>👃 Clay sniff obj36 [0x59] (0x10)<br>👃 Clay sniff obj37 [0x59] (0x20)<br>👃 Clay sniff obj38 [0x59] (0x80) | Byte [SRAM] | Object persistence flags:<br>Quick sand desert [0x59] |
| 0x2299 | 👃 Sniffed Oil (#14) [0x67] (0x01)<br>👃 Sniffed Oil (#15) [0x67] (0x02)<br>👃 Sniffed Oil (#16) [0x67] (0x04)<br>👃 Sniffed Oil (#17) [0x67] (0x08)<br>👃 Sniffed Oil (#18) [0x67] (0x10)<br>👃 Sniffed Oil (#19) [0x67] (0x20)<br>👃 Sniffed Oil (#20) [0x67] (0x40)<br>👃 Sniffed Oil (#21) [0x67] (0x80) | Byte [SRAM] | Sniff spot flags — Bugmuck Exterior [0x67] |
| 0x229a | 👃 Sniffed Roots (#22) [0x67] (0x01)<br>👃 Sniffed Roots (#23) [0x67] (0x02)<br>👃 Sniffed Roots (#24) [0x67] (0x04)<br>👃 Sniffed Roots (#25) [0x67] (0x08)<br>👃 Sniffed Roots (#26) [0x67] (0x10)<br>👃 Sniffed Roots (#27) [0x67] (0x20)<br>👃 Sniffed Roots (#28) [0x67] (0x40)<br>👃 Sniffed Ash (#29) [0x67] (0x80) | Byte [SRAM] | Sniff spot flags — Bugmuck Exterior [0x67] |
| 0x229b | 👃 Sniffed Ash (#30) [0x67] (0x01)<br>👃 Sniffed Ash (#31) [0x67] (0x02)<br>👃 Sniffed Ash (#32) [0x67] (0x04)<br>👃 Sniffed Ash (#33) [0x67] (0x08)<br>👃 Sniffed Crystal (#34) [0x67] (0x10)<br>👃 Sniffed Crystal (#36) [0x67] (0x20)<br>👃 Sniffed Crystal (#37) [0x67] (0x40)<br>👃 Sniffed Clay (#38) [0x67] (0x80) | Byte [SRAM] | Sniff spot flags — Bugmuck Exterior [0x67] |
| 0x229c | 👃 Sniffed Clay (#39) [0x67] (0x01)<br>👃 Sniffed Clay (#40) [0x67] (0x02)<br>👃 Sniffed Clay (#41) [0x67] (0x04)<br>👃 Sniffed Wax (#35) [0x67] (0x08)<br>👃 Sniffed Wax (#42) [0x67] (0x10)<br>👃 Sniffed Wax (#43) [0x67] (0x20)<br>👃 Sniffed Wax (#44) [0x67] (0x40)<br>👃 Sniffed Wax (#45) [0x67] (0x80) | Byte [SRAM] | Sniff spot flags — Bugmuck Exterior [0x67] |
| 0x229d | 👃 Sniffed Wax (#46) [0x67] (0x01)<br>👃 Sniffed Wax (#47) [0x67] (0x02)<br>👃 Sniffed Water (#16) [0x16] (0x04)<br>👃 Sniffed Water (#17) [0x16] (0x08)<br>👃 Sniffed Clay (#18) [0x16] (0x10)<br>👃 Sniffed Clay (#19) [0x16] (0x20)<br>👃 Sniffed Clay (#20) [0x16] (0x40)<br>👃 Sniffed Clay (#21) [0x16] (0x80) | Byte [SRAM] | Sniff spot flags — Bugmuck Exterior [0x67]<br>BBM [0x16] |
| 0x229e | 👃 Sniffed Clay (#22) [0x16] (0x01)<br>👃 Sniffed Clay (#23) [0x16] (0x02)<br>👃 Sniffed Roots (#24) [0x16] (0x04)<br>👃 Sniffed Roots (#25) [0x16] (0x08)<br>👃 Sniffed Roots (#26) [0x16] (0x10)<br>👃 Sniffed Roots (#27) [0x16] (0x20)<br>👃 Sniffed Oil (#28) [0x16] (0x40)<br>👃 Sniffed Oil (#29) [0x16] (0x80) | Byte [SRAM] | Sniff spot flags — BBM [0x16] |
| 0x229f | 👃 Sniffed Oil (#30) [0x16] (0x01)<br>👃 Sniffed Oil (#31) [0x16] (0x02)<br>👃 Sniffed Oil (#32) [0x16] (0x04)<br>👃 Sniffed Oil (#33) [0x16] (0x08)<br>👃 Sniffed Oil (#34) [0x16] (0x10)<br>👃 Sniffed Oil (#35) [0x16] (0x20)<br>👃 Sniffed Ash (#36) [0x16] (0x40)<br>👃 Sniffed Ash (#37) [0x16] (0x80) | Byte [SRAM] | Sniff spot flags — BBM [0x16] |
| 0x22a0 | 👃 Sniffed Ash (#38) [0x16] (0x01)<br>👃 Sniffed Ash (#39) [0x16] (0x02)<br>👃 Sniffed Water (#0) [0x17] (0x04)<br>👃 Sniffed Water (#1) [0x17] (0x08)<br>👃 Sniffed Water (#2) [0x17] (0x10)<br>👃 Sniffed Clay (#3) [0x17] (0x20)<br>👃 Sniffed Clay (#4) [0x17] (0x40)<br>👃 Sniffed Clay (#5) [0x17] (0x80) | Byte [SRAM] | Sniff spot flags — BBM [0x16]<br>Bug Room 2 [0x17] |
| 0x22a1 | 👃 Sniffed Roots (#6) [0x17] (0x01)<br>👃 Sniffed Roots (#7) [0x17] (0x02)<br>👃 Sniffed Roots (#8) [0x17] (0x04)<br>👃 Sniffed Oil (#9) [0x17] (0x08)<br>👃 Sniffed Oil (#10) [0x17] (0x10)<br>👃 Sniffed Oil (#11) [0x17] (0x20)<br>👃 Sniffed Water (#2) [0x41] (0x40)<br>👃 Sniffed Water (#3) [0x41] (0x80) | Byte [SRAM] | Sniff spot flags — Bug Room 2 [0x17]<br>North Jungle [0x41] |
| 0x22a2 | 👃 Sniffed Water (#4) [0x41] (0x01)<br>👃 Sniffed Water (#5) [0x41] (0x02)<br>👃 Sniffed Water (#6) [0x41] (0x04)<br>👃 Sniffed Water (#7) [0x41] (0x08)<br>👃 Sniffed Oil (#8) [0x41] (0x10)<br>👃 Sniffed Oil (#9) [0x41] (0x20)<br>👃 Sniffed Roots (#10) [0x41] (0x40)<br>👃 Sniffed Roots (#11) [0x41] (0x80) | Byte [SRAM] | Sniff spot flags — North Jungle [0x41] |
| 0x22a3 | 👃 Sniffed Roots (#12) [0x41] (0x01)<br>👃 Sniffed Roots (#13) [0x41] (0x02)<br>👃 Sniffed Roots (#14) [0x41] (0x04)<br>👃 Sniffed Clay (#15) [0x41] (0x08)<br>👃 Sniffed Clay (#16) [0x41] (0x10)<br>👃 Sniffed Clay (#17) [0x41] (0x20)<br>👃 Sniffed Ash (#18) [0x41] (0x40)<br>👃 Sniffed Ash (#19) [0x41] (0x80) | Byte [SRAM] | Sniff spot flags — North Jungle [0x41] |
| 0x22a4 | 👃 Sniffed Ash (#20) [0x41] (0x01)<br>👃 Sniffed Wax (#21) [0x41] (0x02)<br>👃 Sniffed Wax (#22) [0x41] (0x04)<br>👃 Sniffed Water (#3) [0x27] (0x08)<br>👃 Sniffed Water (#1) [0x27] (0x10)<br>👃 Sniffed Water (#19) [0x27] (0x20)<br>👃 Sniffed Water (#30) [0x27] (0x40)<br>👃 Sniffed Clay (#9) [0x27] (0x80) | Byte [SRAM] | Sniff spot flags — North Jungle [0x41]<br>Mammoth Graveyard [0x27] |
| 0x22a5 | 👃 Sniffed Clay (#4) [0x27] (0x01)<br>👃 Sniffed Clay (#5) [0x27] (0x02)<br>👃 Sniffed Clay (#10) [0x27] (0x04)<br>👃 Sniffed Clay (#20) [0x27] (0x08)<br>👃 Sniffed Clay (#23) [0x27] (0x10)<br>👃 Sniffed Roots (#11) [0x27] (0x20)<br>👃 Sniffed Roots (#21) [0x27] (0x40)<br>👃 Sniffed Roots (#29) [0x27] (0x80) | Byte [SRAM] | Sniff spot flags — Mammoth Graveyard [0x27] |
| 0x22a6 | 👃 Sniffed Roots (#16) [0x27] (0x01)<br>👃 Sniffed Roots (#26) [0x27] (0x02)<br>👃 Sniffed Roots (#18) [0x27] (0x04)<br>👃 Sniffed Oil (#13) [0x27] (0x08)<br>👃 Sniffed Oil (#25) [0x27] (0x10)<br>👃 Sniffed Oil (#8) [0x27] (0x20)<br>👃 Sniffed Oil (#2) [0x27] (0x40)<br>👃 Sniffed Ash (#17) [0x27] (0x80) | Byte [SRAM] | Sniff spot flags — Mammoth Graveyard [0x27] |
| 0x22a7 | 👃 Sniffed Ash (#15) [0x27] (0x01)<br>👃 Sniffed Ash (#14) [0x27] (0x02)<br>👃 Sniffed Ash (#7) [0x27] (0x04)<br>👃 Sniffed Ash (#6) [0x27] (0x08)<br>👃 Sniffed Ash (#12) [0x27] (0x10)<br>👃 Sniffed Ash (#22) [0x27] (0x20)<br>👃 Sniffed Ash (#24) [0x27] (0x40)<br>👃 Sniffed Wax (#28) [0x27] (0x80) | Byte [SRAM] | Sniff spot flags — Mammoth Graveyard [0x27] |
| 0x22a8 | 👃 Sniffed Wax (#27) [0x27] (0x01)<br>? (0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Sniff spot flags — Mammoth Graveyard [0x27] |
| 0x22a9 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22aa | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22ab | ? (0x01/0x02/0x04/0x08/0x10/0x20)<br>📖 FLOWERS_CUTSCENE_WATCHED (0x40)<br>👃 Sniffed Water (#12) [0x3b] (0x80) | Byte [SRAM] | |
| 0x22ac | 👃 Sniffed Water (#13) [0x3b] (0x01)<br>👃 Sniffed Water (#14) [0x3b] (0x02)<br>👃 Sniffed Water (#15) [0x3b] (0x04)<br>👃 Sniffed Water (#16) [0x3b] (0x08)<br>👃 Sniffed Clay (#17) [0x3b] (0x10)<br>👃 Sniffed Clay (#18) [0x3b] (0x20)<br>👃 Sniffed Clay (#19) [0x3b] (0x40)<br>👃 Sniffed Clay (#20) [0x3b] (0x80) | Byte [SRAM] | Sniff spot flags — Volcano Room 2 [0x3b] |
| 0x22ad | 👃 Sniffed Clay (#21) [0x3b] (0x01)<br>👃 Sniffed Clay (#22) [0x3b] (0x02)<br>👃 Sniffed Clay (#23) [0x3b] (0x04)<br>👃 Sniffed Roots (#24) [0x3b] (0x08)<br>👃 Sniffed Oil (#25) [0x3b] (0x10)<br>👃 Sniffed Oil (#26) [0x3b] (0x20)<br>👃 Sniffed Ash (#27) [0x3b] (0x40)<br>👃 Sniffed Ash (#28) [0x3b] (0x80) | Byte [SRAM] | Sniff spot flags — Volcano Room 2 [0x3b] |
| 0x22ae | 👃 Sniffed Ash (#29) [0x3b] (0x01)<br>👃 Sniffed Ash (#30) [0x3b] (0x02)<br>👃 Sniffed Ash (#31) [0x3b] (0x04)<br>👃 Sniffed Ash (#32) [0x3b] (0x08)<br>👃 Sniffed Ash (#33) [0x3b] (0x10)<br>👃 Sniffed Wax (#34) [0x3b] (0x20)<br>👃 Sniffed Wax (#35) [0x3b] (0x40)<br>👃 Sniffed Wax (#36) [0x3b] (0x80) | Byte [SRAM] | Sniff spot flags — Volcano Room 2 [0x3b] |
| 0x22af | (gap) | Byte×1 [SRAM] | Unmapped |
| 0x22b0 | ? (0x01/0x02/0x04/0x08/0x10/0x20)<br>👃 Sniffed Water (#8) [0x3e] (0x40)<br>👃 Sniffed Water (#9) [0x3e] (0x80) | Byte [SRAM] | Sniff spot flags — Pipe Side Rooms [0x3e] |
| 0x22b1 | 👃 Sniffed Water (#10) [0x3e] (0x01)<br>👃 Sniffed Clay (#11) [0x3e] (0x02)<br>👃 Sniffed Roots (#12) [0x3e] (0x04)<br>👃 Sniffed Oil (#13) [0x3e] (0x08)<br>👃 Sniffed Ash (#15) [0x3e] (0x10)<br>👃 Sniffed Ash (#14) [0x3e] (0x20)<br>👃 Sniffed Wax (#16) [0x3e] (0x40)<br>? (0x80) | Byte [SRAM] | Sniff spot flags — Pipe Side Rooms [0x3e] |
| 0x22b2 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40)<br>👃 Sniffed Water (#9) [0x66] (0x80) | Byte [SRAM] | Sniff spot flags — West of Swamp [0x66] |
| 0x22b3 | 👃 Sniffed Water (#13) [0x66] (0x01)<br>👃 Sniffed Water (#1) [0x66] (0x02)<br>👃 Sniffed Roots (#2) [0x66] (0x04)<br>👃 Sniffed Roots (#3) [0x66] (0x08)<br>👃 Sniffed Roots (#8) [0x66] (0x10)<br>👃 Sniffed Oil (#10) [0x66] (0x20)<br>👃 Sniffed Oil (#11) [0x66] (0x40)<br>👃 Sniffed Wax (#12) [0x66] (0x80) | Byte [SRAM] | Sniff spot flags — West of Swamp [0x66] |
| 0x22b4 | 👃 Sniffed Wax (#4) [0x66] (0x01)<br>👃 Sniffed Water (#6) [0x5c] (0x02)<br>👃 Sniffed Oil (#8) [0x5c] (0x04)<br>👃 Sniffed Crystal (#7) [0x5c] (0x08)<br>👃 Sniffed Crystal (#9) [0x5c] (0x10)<br>👃 Sniffed Ethanol (#1) [0x4f] (0x20)<br>👃 Sniffed Ethanol (#2) [0x4f] (0x40)<br>👃 Sniffed Ethanol (#3) [0x4f] (0x80) | Byte [SRAM] | Object persistence flags:<br>Raptors [0x5c]<br>West of Swamp [0x66]<br>East of Crustacia [0x4f] (high bits) |
| 0x22b5 | 👃 Sniffed Ethanol (#4) [0x4f] (0x01)<br>👃 Sniffed Roots (#5) [0x4f] (0x02)<br>👃 Sniffed Limestone (#6) [0x4f] (0x04)<br>👃 Sniffed Limestone (#7) [0x4f] (0x08)<br>👃 Sniffed Wax (#8) [0x4f] (0x10)<br>👃 Sniffed Wax (#9) [0x4f] (0x20)<br>👃 Sniffed Wax (#10) [0x4f] (0x40)<br>👃 Sniffed Vinegar (#11) [0x4f] (0x80) | Byte [SRAM] | Sniff persistence flags — East of Crustacia [0x4f] sniffs #4–#11; full byte used by [0x4f] |
| 0x22b6 | 👃 Sniffed Bone (#12) [0x4f] (0x01)<br>👃 Sniffed Brimstone (#13) [0x4f] (0x02)<br>👃 Sniffed Brimstone (#14) [0x4f] (0x04)<br>👃 Sniffed Water (#1) [0x1c] (0x08)<br>👃 Sniffed Water (#2) [0x1c] (0x10)<br>👃 Sniffed Water (#3) [0x1c] (0x20)<br>👃 Sniffed Oil (#4) [0x1c] (0x40)<br>👃 Sniffed Oil (#5) [0x1c] (0x80) | Byte [SRAM] | Sniff persistence flags — East of Crustacia [0x4f] (low bits) + North of Market [0x1c] (high bits) |
| 0x22b7 | 👃 Sniffed Crystal (#6) [0x1c] (0x01)<br>👃 Sniffed Crystal (#7) [0x1c] (0x02)<br>👃 Sniffed Clay (#8) [0x1c] (0x04)<br>👃 Sniffed Clay (#9) [0x1c] (0x08)<br>👃 Sniffed Clay (#10) [0x1c] (0x10)<br>👃 Sniffed Vinegar (#11) [0x1c] (0x20)<br>👃 Sniffed Vinegar (#12) [0x1c] (0x40)<br>👃 Sniffed Vinegar (#13) [0x1c] (0x80) | Byte [SRAM] | Sniff spot flags — North of Market [0x1c] |
| 0x22b8 | 👃 Sniffed Atlas Medallion (#14) [0x1c] (0x01)<br>👃 Sniffed Brimstone×2 (#0) [0x2b] (0x02)<br>👃 Sniffed Brimstone (#1) [0x2b] (0x04)<br>👃 Sniffed Brimstone×3 (#2) [0x2b] (0x08)<br>👃 Sniffed Brimstone×2 (#3) [0x2b] (0x10)<br>👃 Sniffed Limestone (#4) [0x2b] (0x20)<br>👃 Sniffed Limestone×2 (#5) [0x2b] (0x40)<br>👃 Sniffed Limestone×3 (#6) [0x2b] (0x80) | Byte [SRAM] | 0x01 = key-item sniff [0x1c]; 0x02–0x80 = sniff persistence flags [0x2b] spots #0–6 (Brimstone×2/1/3/2, Limestone×1/2/3); gates OBJ unload 0–6 on [0x2b] entry |
| 0x22b9 | 👃 Sniffed Bone×2 (#7) [0x2b] (0x01)<br>👃 Sniffed Bone×2 (#8) [0x2b] (0x02)<br>👃 Sniffed Bone×2 (#9) [0x2b] (0x04)<br>👃 Sniffed Ethanol×2 (#10) [0x2b] (0x08)<br>👃 Sniffed Ethanol (#11) [0x2b] (0x10)<br>👃 Sniffed Ethanol×4 (#12) [0x2b] (0x20)<br>👃 Sniffed Ash (#13) [0x2b] (0x40)<br>👃 Sniffed Ash×3 (#14) [0x2b] (0x80) | Byte [SRAM] | Sniff persistence flags — Outside of Halls [0x2b] sniffs #7–14 (Bone×2×3, Ethanol×2/1/4, Ash×1/3); gates OBJ unload 7–14 on [0x2b] entry |
| 0x22ba | 👃 Sniffed Ethanol (#2) [0x2f] (0x20)<br>👃 Sniffed Crystal (#16) [0x2f] (0x10)<br>👃 Sniffed Clay (#17) [0x2f] (0x08)<br>👃 Sniffed Roots (#18) [0x2f] (0x80)<br>👃 Sniffed Roots (#19) [0x2f] (0x40)<br>👃 Sniffed Clay (#20) [0x2f] (0x04)<br>👃 Sniffed Oil (#21) [0x2f] (0x02)<br>👃 Sniffed Ash (#15) [0x2b] (0x01) | Byte [SRAM] | 0x02–0x80 = sniff flags [0x2f] Horace's Camp sniffs #2/#4–#21 (non-sequential bit assignment); 0x01 = sniff #15 [0x2b] (Outside of Halls); all bits gate OBJ unload on respective room entry |
| 0x22bb | 👃 Sniffed Roots (#3) [0x2f] (0x01)<br>👃 Sniffed Limestone (#5) [0x2f] (0x02)<br>👃 Sniffed Limestone (#6) [0x2f] (0x04)<br>👃 Sniffed Wax (#4) [0x2f] (0x08)<br>👃 Sniffed Water (#15) [0x2f] (0x10)<br>👃 Sniffed Water (#7) [0x2f] (0x20)<br>👃 Sniffed Vinegar (#8) [0x2f] (0x40)<br>👃 Sniffed Ash (#9) [0x2f] (0x80) | Byte [SRAM] | Sniff persistence flags — Horace's Camp [0x2f] sniffs #3–#9 + #15; also gates OBJ unload on room entry |
| 0x22bc | 👃 Sniffed Bone (#10) [0x2f] (0x01)<br>👃 Sniffed Bone (#11) [0x2f] (0x02)<br>👃 Sniffed Bone (#12) [0x2f] (0x04)<br>👃 Sniffed Brimstone (#13) [0x2f] (0x08)<br>👃 Sniffed Brimstone (#14) [0x2f] (0x10)<br>👃 Sniffed Oil (#1) [0x4b] (0x20)<br>👃 Sniffed Oil (#2) [0x4b] (0x40)<br>👃 Sniffed Oil (#3) [0x4b] (0x80) | Byte [SRAM] | Sniff persistence flags — [0x2f] Horace's Camp sniffs #10–#14 (bits 0x01–0x10); [0x4b] Oglin Cave Oil sniffs #1–#3 (bits 0x20–0x80) |
| 0x22bd | 👃 Sniffed Clay (#4) [0x4b] (0x01)<br>👃 Sniffed Clay (#5) [0x4b] (0x02)<br>👃 Sniffed Clay (#6) [0x4b] (0x04)<br>👃 Sniffed Clay (#7) [0x4b] (0x08)<br>👃 Sniffed Crystal (#8) [0x4b] (0x10)<br>👃 Sniffed Crystal (#9) [0x4b] (0x20)<br>👃 Sniffed Ethanol (#10) [0x4b] (0x40)<br>👃 Sniffed Ethanol (#11) [0x4b] (0x80) | Byte [SRAM] | Sniff persistence flags — Oglin Cave [0x4b] sniffs #4–#11 |
| 0x22be | 👃 Sniffed Ethanol (#12) [0x4b] (0x01)<br>👃 Sniffed Roots (#13) [0x4b] (0x02)<br>👃 Sniffed Limestone (#14) [0x4b] (0x04)<br>👃 Sniffed Limestone (#15) [0x4b] (0x08)<br>👃 Sniffed Limestone (#16) [0x4b] (0x10)<br>👃 Sniffed Limestone (#17) [0x4b] (0x20)<br>👃 Sniffed Wax (#18) [0x4b] (0x40)<br>👃 Sniffed Wax (#19) [0x4b] (0x80) | Byte [SRAM] | Sniff persistence flags — Oglin Cave [0x4b] sniffs #12–#19 |
| 0x22bf | 👃 Sniffed Water (#20) [0x4b] (0x01)<br>👃 Sniffed Water (#21) [0x4b] (0x02)<br>👃 Sniffed Water (#22) [0x4b] (0x04)<br>👃 Sniffed Water (#23) [0x4b] (0x08)<br>👃 Sniffed Vinegar (#24) [0x4b] (0x10)<br>👃 Sniffed Vinegar (#25) [0x4b] (0x20)<br>👃 Sniffed Ash (#26) [0x4b] (0x40)<br>👃 Sniffed Bone (#27) [0x4b] (0x80) | Byte [SRAM] | Sniff persistence flags — Oglin Cave [0x4b] sniffs #20–#27 |
| 0x22c0 | 👃 Sniffed Bone (#28) [0x4b] (0x01)<br>👃 Sniffed Bone (#29) [0x4b] (0x02)<br>👃 Sniffed Brimstone (#30) [0x4b] (0x04)<br>👃 Sniffed Brimstone (#31) [0x4b] (0x08)<br>👃 Sniffed Ethanol (#1) [0x07] (0x10)<br>👃 Sniffed Ethanol (#2) [0x07] (0x20)<br>👃 Sniffed Vinegar (#3) [0x07] (0x40)<br>👃 Sniffed Limestone (#4) [0x07] (0x80) | Byte [SRAM] | Sniff persistence flags — [0x4b] Oglin Cave Bone/Brimstone sniffs #28–#31 (bits 0x01–0x08); [0x07] West of Crustacia sniffs #1–#4 (bits 0x10–0x80) |
| 0x22c1 | 👃 Sniffed Limestone (#5) [0x07] (0x01)<br>👃 Sniffed Brimstone (#6) [0x07] (0x02)<br>👃 Sniffed Brimstone (#7) [0x07] (0x04)<br>👃 Sniffed Wax (#8) [0x07] (0x08)<br>👃 Sniffed Ash (#9) [0x07] (0x10)<br>👃 Sniffed Roots (#10) [0x07] (0x20)<br>👃 Sniffed Water (#11) [0x07] (0x40)<br>👃 Sniffed Water (#12) [0x07] (0x80) | Byte [SRAM] | Sniff persistence flags — West of Crustacia [0x07] sniffs #5–#12; full byte used by [0x07]; enter script unloads objs 5–12 if bits set |
| 0x22c2 | 👃 Sniffed Gunpowder (#10) [0x7e] (0x01)<br>👃 Sniffed Gunpowder (#11) [0x7e] (0x02)<br>👃 Sniffed Grease (#12) [0x7e] (0x04)<br>👃 Sniffed Grease (#13) [0x7e] (0x08)<br>👃 Sniffed Meteorite (#14) [0x7e] (0x10)<br>👃 Sniffed Dry Ice (#15) [0x7e] (0x20)<br>👃 Sniffed Iron (#16) [0x7e] (0x40)<br>👃 Sniffed Iron (#17) [0x7e] (0x80) | Byte [SRAM] | Sniff persistence flags — Omnitopia Jail [0x7e] sniff spots #10–#17; enter script unloads OBJ indices 0x0a–0x11 if corresponding bits set |
| 0x22c3 | 👃 Sniffed Crystal (#18) [0x7e] (0x01)<br>👃 Sniffed Wax (#19) [0x7e] (0x02)<br>👃 Sniffed Brimstone (#20) [0x7e] (0x04)<br>👃 Sniffed Brimstone (#21) [0x7e] (0x08)<br>👃 Sniffed Wax (#16) [0x06] (0x10)<br>👃 Sniffed Wax (#17) [0x06] (0x20)<br>👃 Sniffed Wax (#18) [0x06] (0x40)<br>👃 Sniffed Wax (#19) [0x06] (0x80) | Byte [SRAM] | Sniff persistence flags — Omnitopia Jail [0x7e] sniffs #18–#21 (bits 0x01–0x08); Outside of 'mids [0x06] sniffs #16–#19 (bits 0x10–0x80) |
| 0x22c4 | 👃 Sniffed Ash (#20) [0x06] (0x01)<br>👃 Sniffed Ash (#21) [0x06] (0x02)<br>👃 Sniffed Bone (#22) [0x06] (0x04)<br>👃 Sniffed Bone (#23) [0x06] (0x08)<br>👃 Sniffed Bone (#24) [0x06] (0x10)<br>👃 Sniffed Brimstone (#25) [0x06] (0x20)<br>👃 Sniffed Brimstone (#26) [0x06] (0x40)<br>👃 Sniffed Brimstone (#27) [0x06] (0x80) | Byte [SRAM] | Sniff persistence flags — Outside of 'mids [0x06] sniffs #20–#27; enter script unloads OBJs 20–27 if bits set |
| 0x22c5 | 👃 Sniffed Brimstone (#28) [0x06] (0x01)<br>👃 Sniffed Water (#29) [0x06] (0x02)<br>👃 Sniffed Limestone (#30) [0x06] (0x04)<br>👃 Sniffed Limestone (#31) [0x06] (0x08)<br>👃 Sniffed Roots (#32) [0x06] (0x10)<br>👃 Sniffed Roots (#33) [0x06] (0x20)<br>👃 Sniffed Roots (#34) [0x06] (0x40)<br>👃 Sniffed Vinegar (#35) [0x06] (0x80) | Byte [SRAM] | Sniff persistence flags — Outside of 'mids [0x06] sniffs #28–#35; enter script unloads OBJs 28–35 if bits set |
| 0x22c6 | 📖 Free Call Bead given [0x4c] (0x01)<br>👃 Sniffed Iron (#4) [0x76] (0x02)<br>👃 Sniffed Iron (#5) [0x76] (0x04)<br>👃 Sniffed Acorns (#6) [0x76] (0x08)<br>👃 Sniffed Acorns (#7) [0x76] (0x10)<br>👃 Sniffed Mushroom (#8) [0x76] (0x20)<br>👃 Sniffed Mushroom (#9) [0x76] (0x40)<br>👃 Sniffed Mushroom (#10) [0x76] (0x80) | Byte [SRAM] | Set when fountain plaza easter egg awards a Call Bead; prevents re-award. Bits 0x02–0x80 = sniff persistence flags [0x76] South of Ivor Tower (Gate) sniffs #4–#10 |
| 0x22c7 | 👃 Sniffed Feather (#11) [0x76] (0x01)<br>👃 Sniffed Feather (#12) [0x76] (0x02)<br>👃 Sniffed Brimstone (#13) [0x76] (0x04)<br>👃 Sniffed Water (#14) [0x76] (0x08)<br>👃 Sniffed Roots (#15) [0x76] (0x10)<br>👃 Sniffed Roots (#16) [0x76] (0x20)<br>👃 Sniffed Ethanol (#17) [0x76] (0x40)<br>👃 Sniffed Ash (#18) [0x76] (0x80) | Byte [SRAM] | Sniff persistence flags [0x76] South of Ivor Tower (Gate) sniffs #11–#18; enter script unloads OBJs 11–18 if bits set |
| 0x22c8 | 👃 Sniffed Ash (#19) [0x76] (0x01)<br>? (0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Bit 0x01 = sniff #19 persistence flag [0x76]; enter script unloads OBJ 19 if set; remaining bits unmapped |
| 0x22c9…0x22ce | (gap) | Byte×6 [SRAM] | Unmapped |
| 0x22cf | ? (0x01/0x02/0x04/0x08)<br>💰 2500 Gold Coins chest looted [0x0b] (0x10)<br>👃 Sniffed Vinegar (#3) [0x0b] (0x20)<br>👃 Sniffed Vinegar (#4) [0x0b] (0x40)<br>👃 Sniffed Water (#1) [0x0b] (0x80) | Byte [SRAM] | Object persistence flags — Palace Grounds [0x0b] |
| 0x22d0 | 👃 Sniffed Water (#2) [0x0b] (0x01)<br>👃 Sniffed Water (#5) [0x0b] (0x02)<br>👃 Sniffed Roots (#6) [0x0b] (0x04)<br>👃 Sniffed Roots (#7) [0x0b] (0x08)<br>👃 Sniffed Bone (#8) [0x0b] (0x10)<br>👃 Sniffed Bone (#9) [0x0b] (0x20)<br>👃 Sniffed Limestone (#10) [0x0b] (0x40)<br>👃 Sniffed Vinegar (#7) [0x4c] (0x80) | Byte [SRAM] | Sniff spot flags — Palace Grounds [0x0b] + Fountain Plaza [0x4c] |
| 0x22d1 | 👃 Sniffed Water (#3) [0x4c] (0x01)<br>👃 Sniffed Water (#4) [0x4c] (0x02)<br>👃 Sniffed Limestone (#5) [0x4c] (0x04)<br>👃 Sniffed Limestone (#6) [0x4c] (0x08)<br>👃 Sniffed Ethanol (#9) [0x05] (0x10)<br>👃 Sniffed Ethanol (#10) [0x05] (0x20)<br>👃 Sniffed Roots (#11) [0x05] (0x40)<br>👃 Sniffed Roots (#12) [0x05] (0x80) | Byte [SRAM] | Sniff spot flags — Fountain Plaza [0x4c] (low bits) + Between 'Mids and Halls [0x05] (high bits) |
| 0x22d2 | 👃 Sniffed Roots (#13) [0x05] (0x01)<br>👃 Sniffed Roots (#14) [0x05] (0x02)<br>👃 Sniffed Limestone (#15) [0x05] (0x04)<br>👃 Sniffed Limestone (#16) [0x05] (0x08)<br>👃 Sniffed Wax (#17) [0x05] (0x10)<br>👃 Sniffed Wax (#18) [0x05] (0x20)<br>👃 Sniffed Water (#19) [0x05] (0x40)<br>👃 Sniffed Vinegar (#20) [0x05] (0x80) | Byte [SRAM] | Sniff spot flags — Between 'Mids and Halls [0x05] |
| 0x22d3 | 👃 Sniffed Vinegar (#21) [0x05] (0x01)<br>👃 Sniffed Bone (#22) [0x05] (0x02)<br>👃 Sniffed Ash (#5) [0x36] (0x04)<br>👃 Sniffed Clay (#6) [0x36] (0x08)<br>👃 Sniffed Oil (#3) [0x36] (0x10)<br>👃 Sniffed Oil (#4) [0x36] (0x20)<br>? (0x40/0x80) | Byte [SRAM] | Sniff spot flags — Between 'Mids and Halls [0x05] (low bits) + Fire Pit area [0x36] (mid bits) |
| 0x22d4…0x22d7 | (gap) | Byte×4 [SRAM] | Unmapped |
| 0x22d8 | ⚙️ OBJ 0 triggered [0x07] (0x20)<br>📖 Diamond Eye #1 obtained / Rimsala beaten [0x58] (0x40)<br>📖 Diamond Eye #2 obtained — Megatuar defeated (Halls) [0x2a] (0x80)<br>🛡️ Hidden item: Iron Bracer GLOVE_3_1 (0x041f) looted [0x74] (0x04)<br>? (0x01/0x02/0x08/0x10) | Byte [SRAM] | 0x20 set by B-trigger in [0x07] when alchemy conditions met (`$235f≥12` AND `$2360==2`); controls whether to unload OBJ 0 on room entry; 0x40 gates Rimsala fight setup in [0x58] enter (if set: skip NPC load, play music only); 0x80 set in Megatuar kill script 0x1998 (labeled "Diamond Eye Halls"), together 0x40+0x80 checked in [0x05] Diamond Eyes theft trigger; 0x04 set by west-castle B-trigger at [2a,1b:2b,1c] in [0x74] via `"Loot nature?"` (0x39) when `$22ea&0x01` |
| 0x22d9 | 📖 Horace met/Madronius spawned [0x2f] (0x01)<br>? (0x02/0x04)<br>📖 Aegis dead [0x09] (0x08)<br>? (0x10)<br>📖 Diamond Eyes stolen (Madronius theft) [0x05] (0x20)<br>📖 First Sting Man greeting shown [0x1b] (0x40)<br>? (0x80) | Byte [SRAM] | 0x01 SET in [0x2f] Horace first-meet step-on; read in [0x09] Aegis kill for dialogue variant and in [0x2f] enter to conditionally load Madronius; 0x08 set in Aegis kill [0x09], gates crater/statue objects in [0x08] and dialogue in [0x08]/[0x0a]; 0x20 set in [0x05] at start of Diamond Eyes theft cutscene, prevents replay; 0x40 set first time talking to Sting Man shuttle NPC in [0x1b], prevents re-intro dialog |
| 0x22da | ? (0x01)<br>⚔️ SWORD_1 (0x02)<br>⚔️ SWORD_2 (0x04)<br>⚔️ SWORD_3 (0x08)<br>⚔️ SWORD_4 (0x10)<br>⚔️ AXE_1 (0x20)<br>⚔️ AXE_2 (0x40)<br>⚔️ AXE_3 (0x80) | Byte [SRAM] | Bone Crusher (SWORD_1)<br>Gladiator Sword (SWORD_2)<br>Crusader Sword (SWORD_3)<br>Neutron Blade (SWORD_4)<br>Spider's Claw (AXE_1)<br>Bronze Axe (AXE_2)<br>Knight Basher (AXE_3) |
| 0x22db | ⚔️ AXE_4 (0x01)<br>⚔️ SPEAR_1 (0x02)<br>⚔️ SPEAR_2 (0x04)<br>⚔️ SPEAR_3 (0x08)<br>⚔️ SPEAR_4 (0x10)<br>⚔️ BAZOOKA (0x20)<br>⚗️ Horace's Aura alchemy known [0x76] (0x40)<br>⚗️ Horace's Regenerate owned [0x55] (0x80) | Byte [SRAM] | Atom Smasher (AXE_4)<br>Horn Spear (SPEAR_1)<br>Bronze Spear (SPEAR_2)<br>Lance (SPEAR_3)<br>Laser Lance (SPEAR_4)<br>Bazooka (BAZOOKA); 0x40 set in [0x76] B-trigger when Horace's Aura spell tile collected ($22db|=0x40); 0x80 set when Horace's Regenerate chest opened in [0x55] (boy-only, requires `$225c&0x80`) |
| 0x22dc | ? (0x01/0x02/0x04)<br>📖 WINDWALKER_UNLOCKED (0x08)<br>? (0x10/0x20/0x40/0x80) | Byte [SRAM] | Set in [0x4d] on first direct (non-animation) entry to palace interior |
| 0x22dd | 📖 Verminator dead [0x5e] (0x01)<br>📖 Sterling dead [0x37] (0x02)<br>📖 Timberdrake dead [0x20] (0x04)<br>📖 East castle (Ebon Keep) active [0x13→0x12, 0x7b, 0x7c, 0x7d] (0x40)<br>? (0x08/0x10/0x20/0x80) | Byte [SRAM] | 0x01 set in Verminator kill script [0x5e]; gates east-castle staircase in [0x74] to 0x0d and music switch in [0x5f]; 0x02 set in Sterling kill script [0x37]; gates Sterling NPC spawn in [0x37] and Mungola boss path in [0x77]; 0x04 set in Timberdrake kill script [0x20]; gates Timberdrake spawn and music in [0x20]; 0x40 set by step-on [15,12:17,13] in [0x13] before CHANGE MAP to 0x12 (Ebon Keep Sewers); also used throughout [0x7b]/[0x7c]/[0x7d] to control music dispatch, NPC loading, gourd contents, and top-gate destination (east=0x5d Ebon Keep Courtyard, west=0x6e Ivor Tower Hall) |
| 0x22de | ? (0x01/0x08/0x10/0x20/0x40)<br>📖 North gate trigger stepped [0x7c] (0x02)<br>📖 Queen Below Chessboard cutscene watched [0x78] (0x04)<br>📖 Talked to Cecil [0x7d room 5 east] (0x80) | Byte [SRAM] | 0x02 set by in-room gate step-on [34,0b:3a,0c] in [0x7c] when east castle flag set; 0x04 set in [0x78] during "Queen Below Chessboard" cutscene path (one-shot guard; prevents replay on re-entry); 0x80 set by Cecil NPC interact in [0x7d] sub-area 5 east hall |
| 0x22df | ⚙️ NPC position flag [0x07] (0x04)<br>📖 Rock scene pending [0x4f] (0x10)<br>📖 Rock landed (Crustacia rock) [0x4f] (0x20)<br>⚙️ Crustacia elevator top position [0x68] (0x02)<br>? (0x01/0x08/0x40/0x80) | Byte [SRAM] | 0x02: set when elevator is in upper position ([0x68] step-on), cleared when returned to bottom; 0x04: NPC 0x20 at west [0x11,0x0f] vs east [0x31,0x0f] in [0x07]; toggled by step-ons, persists between entries; 0x10: set externally to trigger rock-landing cutscene on next [0x4f] entry; 0x20: set during rock cutscene (`$22df|=0x20`), gates OBJ 17 on re-entry, prevents replay // TODO: identify where `$22df&0x10` is set |
| 0x22e0 | ⚙️ Gear puzzle active [0x06] (0x02)<br>⚙️ Left gear turned [0x06] (0x04)<br>⚙️ Right gear turned [0x06] (0x08)<br>⚙️ 'mids bottom gear A [0x55] (0x10)<br>⚙️ 'mids bottom gear B [0x55] (0x20)<br>⚙️ 'mids bottom gear C [0x55] (0x40)<br>⚙️ 'mids bottom gear D [0x55] (0x80)<br>? (0x01) | Byte [SRAM] | Gear/pulley puzzle state: [0x06] 0x02/0x04/0x08 for outside gear puzzle; [0x55] 0x10/0x20/0x40/0x80 for four internal gear puzzles; each bit activates OBJ pair (A=OBJ4/0; B=OBJ5/2; C=OBJ6/1; D=OBJ7/3) |
| 0x22e1 | ⚙️ Mechanism A-1 activated [0x55] (0x01)<br>⚙️ Mechanism A-2 activated [0x55] (0x02)<br>⚙️ Mechanism B activated [0x55] (0x04)<br>⚙️ Mechanism C entry dir [0x55] (0x08)<br>⚙️ Mechanism D entry dir [0x55] (0x10)<br>⚙️ Exit N-left done [0x55] (0x20)<br>⚙️ Exit N-right done [0x55] (0x40)<br>⚙️ Neutron Blade step 2 — OBJ 12 [0x55] (0x80) | Byte [SRAM] | 'mids bottom mechanism and puzzle state flags; OBJ state restored on entry from these bits (sub `0x95900a`) |
| 0x22e2 | ⚙️ Neutron Blade step 3 — OBJ 13 [0x55] (0x01)<br>⚙️ Neutron Blade step 1 — OBJ 14 [0x55] (0x02)<br>⚙️ Neutron Blade step 5 — OBJ 15 + dog freed [0x55] (0x04)<br>⚙️ Neutron Blade step 4 — OBJ 16 [0x55] (0x08)<br>⚙️ Gear puzzle A activated [0x56] (0x10)<br>⚙️ Gear puzzle B activated [0x56] (0x20)<br>📖 Sons of Shyness defeated [0x55] (0x40)<br>⚙️ WindWalker obstacles removed [0x57] (0x80) | Byte [SRAM] | 'mids Neutron Blade + gear puzzle state; 0x01–0x08 = Neutron Blade steps [0x55]; 0x04 also sets `$22e3\|=0x40` (dog freed); 0x10 = gear A set by step-on [2f,1c:31,1e] [0x56]; 0x20 = gear B set by B-trigger [37,1e:39,22] (boy + weapon #12) [0x56]; 0x40 gates extra spawners on room entry; 0x80 = WindWalker obstacles (OBJ 1/2/3) removed [0x57]; gates switch logic + OBJ hide on enter // TODO: where is 0x40 set (Sons kill script?) |
| 0x22e3 | 📖 WindWalker gate opened [0x57] (0x01)<br>📖 Rock wall 1 (OBJ 4) destroyed [0x57] (0x02)<br>📖 Rock wall 2 (OBJ 5) destroyed [0x57] (0x04)<br>📖 Rock wall 3 (OBJ 6) destroyed [0x57] (0x08)<br>📖 Rock wall 4 (OBJ 14) destroyed [0x57] (0x10)<br>📖 Tiny defeated [0x57] (0x20)<br>📖 Dog freed from 'mids [0x06] (0x40)<br>📖 "Dog can't go up this way" message shown [0x06] (0x80) | Byte [SRAM] | 0x01 = WindWalker gate opened in [0x57] (gates NPC position + OBJ 3 restore); 0x02/0x04/0x08/0x10 = rock walls destroyed by WindWalker/weapon B-triggers [0x57]; 0x20 = Tiny defeated (SET in [0x57], READ in [0x4d]: Horace post-Tiny eulogy branch); 0x40 gates dog-freed enter cutscene and reunite sequence in [0x06], also read in [0x55] enter; 0x80 set by step-on [34,4b:38,4c] in [0x06] when dog tries the steep north path |
| 0x22e4 | 📖 Sons encounter triggered [0x55] (0x01)<br>📖 Reunite cutscene played [0x06] (0x02)<br>⚙️ Boy blocked at north exit (dog inside 'mids) [0x06] (0x04)<br>⚙️ Dog assigned to bottom gear entry [0x06] (0x08)<br>⚙️ Boy assigned to bottom gear entry [0x06] (0x10)<br>⚙️ Dog on L gear [0x06] (0x20)<br>⚙️ Dog on R gear [0x06] (0x40)<br>⚙️ Boy on L gear [0x06] (0x80) | Byte [SRAM] | 0x01 set by Sons encounter step-on in [0x55], prevents replay; 0x02 prevents reunite cutscene replay [0x06]; 0x04 set when dog is inside 'mids and boy tries to go north; 0x08/0x10 track gear trigger assignments; 0x20/0x40/0x80 track active gear assignments |
| 0x22e5 | ⚙️ Boy on R gear [0x06] (0x01)<br>⚙️ 'mids split state flag A [0x06] (0x02)<br>⚙️ 'mids split state flag B [0x06] (0x04)<br>⚙️ WW Landing flag [0x36] (0x08)<br>? (0x10)<br>📖 Defeated raptors? [0x51] (0x20)<br>📖 West castle collapsed [0x75] (0x40)<br>? (0x80) | Byte [SRAM] | 0x01/0x02/0x04 used by 'mids gear puzzle and split logic in [0x06]; cleared in dog-freed enter sequence; 0x08 set before loading fire pit for WindWalker landing sequence [0x36]; 0x20 set in FE Cutscene 1 [0x51]; 0x40 read in [0x75] to force-unload OBJ 0–4 (stairwell in ruins when west castle has collapsed) |
| 0x22e6 | ? (0x01/0x02)<br>📖 Reactor ON [0x42] (0x04)<br>📖 Codes generated [0x43/0x54] (0x08)<br>📖 Alarm disabled [0x00/0x43] (0x10)<br>📖 Storage lights on [0x47] (0x20)<br>📖 Greenhouse lights on [0x44] (0x40)<br>📖 // MISMATCH: Particle Bombs sold [0x47] vs Secret boss defeated [0x45] (0x80) | Byte [SRAM] | Omnitopia persistent state flags; 0x04 = reactor switched on [0x42]; 0x08 = access codes generated on first visit to [0x43] or [0x54]; 0x10 = alarm disabled when correct code entered [0x43], suppresses alarm zones in [0x00]; 0x20 = storage room lights on [0x47], prerequisite for B-trigger loot; 0x40 = greenhouse lights on [0x44]; 0x80 // MISMATCH — [0x47] stores doc says "Particle Bombs already sold", [0x45] boss room doc says "Boss defeated" — both claim this same SRAM bit |
| 0x22e7 | 📖 Jail warden (GUARD_BOT) defeated [0x7e] (0x01)<br>? (0x02)<br>📖 Switch puzzle throw-animation activated [0x29] (0x04)<br>⚙️ OBJ 3 bridge-reveal camera pan done [0x24] (0x08)<br>? (0x10/0x20/0x40/0x80) | Byte [SRAM] | 0x01 set by warden kill script in [0x7e], enables prisoner cell lever interactions and assigns code values to `$2839`/`$283b`/`$283d`; 0x04 set (one-time) when boy steps on switch tile [1c,12:1e,13] in [0x29] — prevents re-throw animation; success flag is `$2834&0x04`; 0x08 set after first B-trigger camera pan in [0x24] at [25,22:26,24] — prevents repeat pan |
| 0x22e8 | ? (0x01/0x02/0x04)<br>⚙️ Tornado/dust devil first-heal done [0x1b] (0x08)<br>📖 Pig-race gate passed [0x7c] (0x10)<br>? (0x20/0x40/0x80) | Byte [SRAM] | 0x08 set on first full-heal by the dust devil (tornado step-on [2c,18:2d,19]) in Desert of Doom [0x1b]; gates repeat healing so boy is only healed once per playthrough by the tornado. 0x10 set after pig-race winner guard cutscene in [0x7c] ($234b=0x89); keeps gate (OBJ 0) permanently open on subsequent entries |
| 0x22e9 | 🛡️ Titanium Vest looted [0x00] (0x01)<br>🛡️ Old Reliable armor looted [0x42] (0x02)<br>? (0x04/0x08/0x10)<br>📖 Potty-mouth curse [0x1b] (0x20)<br>📖 Minitaur defeated [0x2c] (0x40)<br>? (0x80) | Byte [SRAM] | 0x01 = Titanium Vest chest in Alarm Room [0x00] (OBJ 10) looted; enter script unloads OBJ 10 if set; 0x02 = Old Reliable armor chest in Reactor Room [0x42] (OBJ 31) looted; enter script unloads OBJ 31 if set; 0x20 tested in Desert of Doom shuttle dialog: if set, Sting Man demands 3× Amulet of Annihilation and delivers unique "Potty mouth…" lecture; flag presumably set elsewhere in the game (Crustacia dialog); 0x40 read in [0x2c] enter — if set, skip Minitaur spawn, unload OBJ 0, play normal music 0x1e instead of boss music 0x5a |
| 0x22ea | ⚙️ LOOT_SUCCESSFUL (0x01)<br>⚙️ ? (0x02)<br>⚙️ EMPTY_SRAM (0x04)<br>⚙️ ? (0x08/0x10/0x20/0x40)<br>⚙️ SHOW_HUD (0x80) | Byte [SRAM] | |
| 0x22eb | ⚙️ ? (0x01)<br>⚙️ START_PRESSED (0x02)<br>⚙️ INTRO_DEMO_MODE (0x04)<br>⚙️ DEBUG (0x08)<br>⚙️ ? (0x10)<br>⚙️ IN_ANIMATION (0x20)<br>📖 Door-open animation pending [0x0a/0x08/0x7b/0x7c/0x7d] (0x40)<br>📖 Prophet prediction gate [0x0a] (0x80) | Byte [SRAM] | [BOOLEAN]; 0x40 set in [0x0a/0x08] for inn entry animation; also set in [0x7b]/[0x7c]/[0x7d] interior exit scripts so enter script plays door-open SFX+animation on next exterior entry; general "play entry animation next time" flag |
| 0x22ec | ? (0x01/0x02/0x04/0x08)<br>📖 East hall sub-state [0x7d] (0x10)<br>📖 Walk-in monologue from spy cutscene [0x1c] (0x20)<br>📖 Inn entry variant [0x0a/0x08] (0x40)<br>? (0x80) | Byte [SRAM] | 0x10 controls NPC set loaded in [0x7d] sub-areas 6/7/8: when set = east hall NPC configuration; 0x20 set in FE Cutscene 3 [0x51]; also set in [0x4d] spy-cutscene exit, cleared after walk-in speech in [0x1c] |
| 0x22ed | ? (0x01)<br>? (0x02)<br>? (0x04)<br>📖 Crustacia intro to be shown [0x6d kill→0x6c] (0x08)<br>? (0x10)<br>📖 Warehouse merchant greeting seen [0x0c] (0x20)<br>? (0x40)<br>⚙️ Falling into a pit [0x05/0x06] (0x80) | Byte [SRAM] | 0x08 set by Aquagoth kill script [0x6d] before CHANGE MAP to 0x6c; consumed in [0x6c] SE Well enter script to trigger well intro cutscene (dog emerges as Poodle); // TODO: MISMATCH — prior note said "consumed in [0x68] (Crustacia)" but script evidence shows consumption in [0x6c]; 0x04 tested in [0x5c] raptor fight (set by BOY_RAPTORS_SCREEN, core.evs line 189); also gates FE Cutscene 1 in [0x51]; 0x02 in shop_buy (core.evs line 7461); 0x80 set in [0x05] and [0x06] pit-fall step-ons before loading Horace's camp, tells destination the player arrived via pit-fall (noted as "Falling into a pit" in sewers script, core.evs line 11976) |
| 0x22ee | 📖 Arena/Halls arrival routing flag [0x1e/0x29] (0x01)<br>⚙️ Ingredient shop open [0x54] (0x02)<br>📖 Side rooms corridor dialog shown [0x3e] (0x04)<br>? (0x08/0x10/0x20)<br>📖 Crush dialog in-progress [0x4f] (0x40)<br>📖 Mungola defeated / castle collapse triggered [0x77→0x78] (0x80) | Byte [SRAM] | 0x01 read in [0x1e] enter — if set, skip Pompolonius intro and teleport to exit positions; also read in [0x30] section 1 entry — if set, teleport boy/dog to [0x24,0x19/0x1d] then clear; set by Sacred Dog ceremony in [0x08] before CHANGE MAP to [0x1e]; cleared in [0x34] enter script; also set as FE→hut transition flag in [0x51]; also read in [0x29] enter — if set, teleport both to north entrance [0x3f,0x0d] and clear; // TODO: MISMATCH — [0x7d] room 5 east uses $22ee&0x01 as "entry from professor's lab" reposition flag (teleports boy to [69,11] and clears); may share semantic with "special entry routing" but target room differs; 0x02 = ingredient shop currently open flag in [0x54] (written True/False in shop_buy, core.evs line 7468); 0x40 set at start of Crush cutscene in [0x4f], cleared at end; 0x80 set in [0x77] on Mungola kill before CHANGE MAP to 0x78; consumed in [0x78] enter to trigger castle-collapse escape cutscene |
| 0x22ef | ? (0x01)<br>📖 Market reminder dialog shown [0x0a/0x08] (0x02)<br>? (0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | 0x02 gates "This place is empty!" message in [0x0a]; cleared by Sacred Dog cutscene in [0x08] and again at start of Aegis kill script [0x09] |
| 0x22f1 | ? (0x01/0x02/0x04/0x08/0x10)<br>FE visited or post-WW? [0x51] (0x20)<br>📖 OUTRO [0x08/0x6a/0x3a/0x46] (0x40)<br>📖 Outro phase 2 — friends-arrive cutscene [0x46] (0x80) | Byte [SRAM] | 0x40 triggers Square outro cutscene in [0x08]; also set before loading [0x3a] fire pit for WindWalker launch cinematic; also used as outro active flag in [0x46] Professor's Lab; 0x80 set in [0x46] second outro phase when Horace + Fire Eyes drop in |
| 0x22f2 | 📖 in credits [0x08] (0x01)<br>? (0x02)<br>⚙️ Elevator initialized [0x68] (0x04)<br>⚙️ Dog 'stay here' instruction shown [0x68] (0x08)<br>📖 "Tiny and his shame must have left" message shown [0x57] (0x10)<br>📖 "Tiny must be around" hint shown [0x57] (0x20)<br>📖 Horace met post-WindWalker [0x4d] (0x40)<br>📖 Palace gate guard easter egg seen [0x4c] (0x80) | Byte [SRAM] | 0x01: [0x5b] enter branches to credits; 0x04 set on first elevator use in [0x68]; 0x08 set on first dog staircase 'stay here' prompt in [0x68]; 0x40 set in [0x4d] when Horace gives Oglin warning; 0x80 set in [0x4c] left guard B-trigger on 2nd denied visit |
| 0x22f3 | 📖 Crush dialog to be shown [0x4d→0x4f] (0x01)<br>? (0x02/0x04)<br>📖 Coming from north end of Desert [0x1b → 0x0a] (0x08)<br>📖 Shuttle accepted / ride paid [0x1b] (0x10)<br>📖 SALABOG (0x20)<br>⚙️ Spike panel state changed in [0x23] (0x40)<br>📖 Wings drop cutscene trigger [0x29] (0x80) | Byte [SRAM] | 0x01 set in [0x4d] Path A2 when dog enters the palace (Sacred Dog ceremony scene); consumed in [0x4f] enter script to trigger Crush introduction cutscene (awards Crush formula + ingredient shop 0x000b), then cleared; 0x08 set in [0x1b] north-exit tile before loading 0x0a, tells the Market the player arrived from the desert north end; 0x10 set when player pays Sting Man for shuttle ride, cleared after ride animation completes; 0x40 set during [0x23] spike toggle step-ons when any panel changes state — gates SFX 0x76 ×3 within the same script execution (not consumed/cleared by enter script); 0x80 set before CHANGE MAP to [0x29] when falling through spike floor — consumed in [0x29] enter to trigger Wings-fall cutscene (spike ceiling animation + rotating landing dialogue), then cleared |
| 0x22f4 | 📖 First-entry intro cutscene flag [0x4b] (0x01)<br>📖 Boy in special entry state [0x70/0x72] (0x02)<br>? (0x04)<br>📖 Prison door 1 open [0x74] (0x08)<br>📖 Prison door 2 open [0x74] (0x10)<br>📖 Prison door 3 open [0x74] (0x20)<br>📖 Prison door 4 open [0x74] (0x40)<br>📖 Prison door 5 open [0x74] (0x80) | Byte [SRAM] | 0x01: when set on entry to Oglin Cave [0x4b], triggers boy look-around animation (WEST→NORTH→SOUTH); not cleared by this room — persists as a "cave entered" marker; set externally before first entry; 0x02 read in [0x70] and [0x72]: if set, teleports boy out-of-map and disables SELECT (boy unavailable during special entry sequence); 0x08–0x80 = Ebon Keep / Ivor Tower Dungeon [0x74] prison doors 1–5 (set by step-ons; cleared/set by enter script based on escape state; bulk-set `$22f4|=0xf8` on escape, bulk-clear `$22f4&=~0xf8` on fresh entry) |
| 0x22f5 | 📖 Prison door 6 open [0x74] (0x01)<br>📖 Prison door 7 open [0x74] (0x02)<br>📖 Post-door-event flag [0x11→0x0d] (0x04)<br>📖 Sterling escort cutscene flag [0x7a] (0x08)<br>📖 Puppet show dialog seen [0x77] (0x10)<br>📖 Pig race pending — barker NPC not loaded [0x62] (0x20)<br>⚙️ Naris age flag toggle [0x0f] (0x40)<br>⚙️ Naris older-sprite loaded [0x0f] (0x80) | Byte [SRAM] | 0x01/0x02: Dungeon [0x74] prison doors 6–7 (bulk-set `$22f5|=0x03` on escape, bulk-clear `$22f5&=~0x03`); 0x04 set by step-on [1e,49:21,4c] in [0x11] Queen's Room south exit, consumed in [0x0d] enter to trigger door-open OBJ sequence then cleared; 0x08 set before escort cutscene in [0x7a] (Ivor Tower Sewers Exterior), cleared after cinematic; 0x10 set in [0x77] on first puppet-show viewing (one-shot guard for entry dialog); 0x20 read in [0x62] enter to skip barker NPC load when pig race is in progress in [0x4e]; 0x40 toggled on every entry to [0x0f] — when set: load older Naris (NPC 0x55), when clear: load younger Naris (NPC 0x51); 0x80 set/cleared alongside 0x40 to track which Naris sprite is currently active |
| 0x22f6 | ? (0x01)<br>📖 GATE_BOT #1 killed [0x48] (0x02)<br>📖 GATE_BOT #2 killed [0x48] (0x04)<br>📖 GATE_BOT #3 killed [0x48] (0x08)<br>📖 GATE_BOT #4 killed [0x48] (0x10)<br>📖 GATE_BOT #5 killed [0x48] (0x20)<br>📖 GATE_BOT #6 killed [0x48] (0x40)<br>📖 GATE_BOT #7 killed [0x48] (0x80) | Byte [SRAM] | Metroplex Tunnels [0x48] GATE_BOT kill persistence flags — robots #1–7; enter script unloads each robot OBJ if bit set |
| 0x22f7 | 📖 GATE_BOT #8 killed [0x48] (0x01)<br>📖 GATE_BOT #9 killed [0x48] (0x02)<br>📖 GATE_BOT #10 killed [0x48] (0x04)<br>📖 GATE_BOT #11 killed [0x48] (0x08)<br>📖 GATE_BOT #12 killed [0x48] (0x10)<br>📖 GATE_BOT #13 killed [0x48] (0x20)<br>📖 GATE_BOT #14 killed [0x48] (0x40)<br>📖 GATE_BOT #15 killed [0x48] (0x80) | Byte [SRAM] | Metroplex Tunnels [0x48] GATE_BOT kill persistence flags — robots #8–15; full byte used |
| 0x22f8 | ⚙️ Enemy group initialized [0x48] (0x01)<br>📖 First Omnitopia entry — ship landing [0x49] (0x02)<br>⚙️ Hatch-entry flag [all Omnitopia rooms] (0x04)<br>⚙️ Returned from alarm / first-visit init [0x43/0x44/0x47] (0x08)<br>⚙️ Dog entered alarm room [0x43] (0x10)<br>📖 FAN_BOT #1 killed [0x43] (0x20)<br>⚙️ FAN_BOT #1 cleanup shown [0x43] (0x40)<br>📖 FAN_BOT #2 killed [0x43] (0x80) | Byte [SRAM] | Omnitopia cross-room session/persistent flags; 0x02 set before ship-landing cutscene in [0x49] (first entry), cleared by cutscene; 0x04 set before every cross-room CHANGE MAP from any Omnitopia room, cleared on fade-in; 0x08 = multi-use: "returned from alarm" reposition trigger in [0x43] OR "first-visit init" gate in [0x44]/[0x47]; 0x10 set when dog enters alarm room [0x43]; 0x20/0x80 = FAN_BOT kill flags set by kill scripts in [0x43] |
| 0x22f9 | ⚙️ FAN_BOT #2 cleanup shown [0x43] (0x01)<br>📖 Knock hole visible (OBJ 2 state=9) [0x43] (0x02)<br>📖 Secret door open [0x43/0x45] (0x04)<br>⚙️ Arrived from jail hatch [0x49] (0x08)<br>📖 Lab cutscene phase 2 queued [0x46] (0x10)<br>⚙️ Energy core teleporter used [0x49] (0x20)<br>⚙️ Returned to jail from junkyard [0x7e/0x49] (0x40)<br>? (0x80) | Byte [SRAM] | Omnitopia cross-room flags; 0x04 = set when exiting [0x45] secret boss room, enables duct slide-down in [0x43]; 0x08 = triggers hatch fade-in spawn in [0x49]; 0x10 = set in [0x46] before CHANGE MAP → 0x19 for phase 2 lab cutscene; 0x20 = set when energy core teleporter first used in [0x49]; 0x40 = set on `[26,15]` step-on in [0x49] before CHANGE MAP to jail, triggers special `0x9b9692` path in [0x7e] |
| 0x22fa…0x22fb | (gap) | Byte×2 [SRAM] | Unmapped |
| 0x22fc | ⚙️ Desert Wrap Y counter [0x1b] (full byte) | Byte [SRAM] | Range 0–17 (0x11). Incremented when player walks off the north wrap edge (y≈0x22–0x23 tiles), teleporting +2 screens south. Decremented when walking off the south wrap edge (y≈0x68–0x69), teleporting −2 screens north. Clamped at max 17 on north overflow (no exit). When decremented below 0 from value 0, exits to 0x4f (East of Crustacia). The north-exit tile [3b,0c:3c,10] exits to 0x0a (Nobilia Market) independently of this counter. |
| 0x22fd | ⚙️ Desert Wrap X counter [0x1b] (full byte) | Byte [SRAM] | Range 0–7. Decremented on left/east-edge wrap (x≈0x22–0x23), teleporting +2 screens east. Incremented on right/west-edge wrap (x≈0x6b–0x6c), teleporting −2 screens west. Clamps to 0–7; no exit condition on overflow. |
| 0x22fe | ⚙️ WW landing attempt counter [0x36] | Byte [SRAM] | 0 = first entry; incremented on first outro pass; gates WindWalker NPC load |
| 0x22ff | 🌿 WAX | Byte [SRAM] | |
| 0x2300 | 🌿 WATER | Byte [SRAM] | |
| 0x2301 | 🌿 VINEGAR | Byte [SRAM] | |
| 0x2302 | 🌿 ROOT | Byte [SRAM] | |
| 0x2303 | 🌿 OIL | Byte [SRAM] | |
| 0x2304 | 🌿 MUSHROOM | Byte [SRAM] | |
| 0x2305 | 🌿 MUD_PEPPER | Byte [SRAM] | |
| 0x2306 | 🌿 METEORITE | Byte [SRAM] | |
| 0x2307 | 🌿 LIMESTONE | Byte [SRAM] | |
| 0x2308 | 🌿 IRON | Byte [SRAM] | |
| 0x2309 | 🌿 GUNPOWDER | Byte [SRAM] | |
| 0x230a | 🌿 GREASE | Byte [SRAM] | |
| 0x230b | 🌿 FEATHER | Byte [SRAM] | |
| 0x230c | 🌿 ETHANOL | Byte [SRAM] | |
| 0x230d | 🌿 DRY_ICE | Byte [SRAM] | |
| 0x230e | 🌿 CRYSTAL | Byte [SRAM] | |
| 0x230f | 🌿 CLAY | Byte [SRAM] | |
| 0x2310 | 🌿 BRIMSTONE | Byte [SRAM] | |
| 0x2311 | 🌿 BONE | Byte [SRAM] | |
| 0x2312 | 🌿 ATLAS_MEDALLION | Byte [SRAM] | |
| 0x2313 | 🌿 ASH | Byte [SRAM] | |
| 0x2314 | 🌿 ACORN | Byte [SRAM] | |
| 0x2315 | 🧪 PETAL | Byte [SRAM] | |
| 0x2316 | 🧪 NECTAR | Byte [SRAM] | |
| 0x2317 | 🧪 HONEY | Byte [SRAM] | |
| 0x2318 | 🧪 DOG_BISCUIT | Byte [SRAM] | |
| 0x2319 | 🧪 WINGS | Byte [SRAM] | |
| 0x231a | 🧪 HERBAL_ESSENCE | Byte [SRAM] | |
| 0x231b | 🧪 PIXIE_DUST | Byte [SRAM] | |
| 0x231c | 🧪 CALL_BEADS | Byte [SRAM] | |
| 0x231d | 🛡️ CHEST_1_1 | Byte [SRAM] | |
| 0x231e | 🛡️ CHEST_1_2 | Byte [SRAM] | |
| 0x231f | 🛡️ CHEST_1_3 | Byte [SRAM] | |
| 0x2320 | 🛡️ CHEST_2_1 | Byte [SRAM] | |
| 0x2321 | 🛡️ CHEST_2_2 | Byte [SRAM] | |
| 0x2322 | 🛡️ CHEST_2_3 | Byte [SRAM] | |
| 0x2323 | 🛡️ CHEST_3_1 | Byte [SRAM] | |
| 0x2324 | 🛡️ CHEST_3_2 | Byte [SRAM] | |
| 0x2325 | 🛡️ CHEST_3_3 | Byte [SRAM] | |
| 0x2326 | 🛡️ CHEST_4_1 | Byte [SRAM] | |
| 0x2327 | 🛡️ CHEST_4_2 | Byte [SRAM] | |
| 0x2328 | 🛡️ CHEST_4_3 | Byte [SRAM] | |
| 0x2329 | 🛡️ HELM_1_1 | Byte [SRAM] | |
| 0x232a | 🛡️ HELM_1_2 | Byte [SRAM] | |
| 0x232b | 🛡️ HELM_1_3 | Byte [SRAM] | |
| 0x232c | 🛡️ HELM_2_1 | Byte [SRAM] | |
| 0x232d | 🛡️ HELM_2_2 | Byte [SRAM] | |
| 0x232e | 🛡️ HELM_2_3 | Byte [SRAM] | |
| 0x232f | 🛡️ HELM_3_1 | Byte [SRAM] | |
| 0x2330 | 🛡️ HELM_3_2 | Byte [SRAM] | |
| 0x2331 | 🛡️ HELM_3_3 | Byte [SRAM] | |
| 0x2332 | 🛡️ HELM_4_1 | Byte [SRAM] | |
| 0x2333 | 🛡️ HELM_4_2 | Byte [SRAM] | |
| 0x2334 | 🛡️ HELM_4_3 | Byte [SRAM] | |
| 0x2335 | 🛡️ GLOVE_1_1 | Byte [SRAM] | |
| 0x2336 | 🛡️ GLOVE_1_2 | Byte [SRAM] | |
| 0x2337 | 🛡️ GLOVE_1_3 | Byte [SRAM] | |
| 0x2338 | 🛡️ GLOVE_2_1 | Byte [SRAM] | |
| 0x2339 | 🛡️ GLOVE_2_2 | Byte [SRAM] | |
| 0x233a | 🛡️ GLOVE_2_3 | Byte [SRAM] | |
| 0x233b | 🛡️ GLOVE_3_1 | Byte [SRAM] | |
| 0x233c | 🛡️ GLOVE_3_2 | Byte [SRAM] | |
| 0x233d | 🛡️ GLOVE_3_3 | Byte [SRAM] | |
| 0x233e | 🛡️ GLOVE_4_1 | Byte [SRAM] | |
| 0x233f | 🛡️ GLOVE_4_2 | Byte [SRAM] | |
| 0x2340 | 🛡️ GLOVE_4_3 | Byte [SRAM] | |
| 0x2341 | 🛡️ COLLAR_1 | Byte [SRAM] | |
| 0x2342 | 🛡️ COLLAR_2 | Byte [SRAM] | |
| 0x2343 | 🛡️ COLLAR_3 | Byte [SRAM] | |
| 0x2344 | 🛡️ COLLAR_4 | Byte [SRAM] | |
| 0x2345 | ⚔️ AMMO_1 | Byte [SRAM] | |
| 0x2346 | ⚔️ AMMO_2 | Byte [SRAM] | |
| 0x2347 | ⚔️ AMMO_3 | Byte [SRAM] | |
| 0x2348 | 💰 CURRENCY_CURRENT | Byte [SRAM] | |
| 0x234a | ? | Byte [SRAM] | Written 0x63 (=99) in room [0x38] enter script after intro; opcode 0x14; purpose unknown |
| 0x234b | FAKE_HOUSE_ID | Word [SRAM] | // MISMATCH: `$234c` (high byte of this Word) is used independently as pirate ship section ID (1–5) set by [0x68] step-ons and read by [0x30] enter; may conflict with FAKE_HOUSE_ID high byte or high byte is repurposed |
| 0x234d…0x234e | (gap) | Byte×2 [SRAM] | Unmapped |
| 0x234f | ⚙️ East castle prison exit door number [0x74] | Byte [SRAM] | 0 = not yet escaped; nonzero = door number used to exit (1–7); set by `0x98ab37` post-escape routing script; read by [0x74] enter alongside `$2351` (west) to determine escape state |
| 0x2350 | ⚙️ Dog staircase state [0x68] | Byte [SRAM] | 0 = normal; 1 = dog left at L-stair top; 2 = dog left at R-stair top; 3 = dog at south-L; 4 = dog at south-R; checked on exit step-ons in [0x30] (clears if 1 or 2); checked in [0x30] enter to suppress/hide dog if != 0 |
| 0x2351 | ⚙️ West castle prison exit door number [0x74] | Byte [SRAM] | 0 = not yet escaped; nonzero = door number used to exit (1–7); set by `0x98ab37` post-escape routing script; read by [0x74] enter to skip re-imprisonment and set all door flags open |
| 0x2352 | ⚙️ Companion warning dialog active [0x78] | Byte [SRAM] | Low byte; read by Queen's Key step-on in [0x78] as a prerequisite; session-local routing state |
| 0x2353 | 📖 Queen's Key on boy [0x78] | Byte [SRAM] | 0 = not yet given; 0x0001 = key picked up; set by Queen's Key step-on [1c,47:23,48] in [0x78]; read as prerequisite for `$2264|=0x10` |
| 0x2354 | 📖 Queen's mission given [0x78] | Word [SRAM] | 0 = not given; 0x0001 = mission briefing delivered; set at end of default Queen audience in [0x78]; read on re-entry to determine NPC load variant |
| 0x2355 | ⚙️ WINDWALKER_TYPE / WW landing phase | Word [SRAM] | Low byte: 1 = first fire pit (OBJ 0 state 1), 2 = second fire pit (OBJ 0 state 2) [0x36] |
| 0x2357 | ⚙️ Boy's 'mids destination [0x06] | Byte [SRAM] | 0 = outside; 1 = bottom (0x55); 2 = top (0x56); set by 'mids entry step-ons in [0x06], read in [0x06]/[0x55] enter scripts to handle boy/dog split |
| 0x2358 | ⚙️ Dog's 'mids destination [0x06] | Byte [SRAM] | 0 = outside; 1 = bottom (0x55); 2 = top (0x56); set by 'mids entry step-ons in [0x06], read in [0x06]/[0x55] enter scripts to handle boy/dog split |
| 0x2359…0x235e | (gap) | Byte×6 [SRAM] | Unmapped |
| 0x235f | CURRENT_WEAPON | Byte [SRAM] | |
| 0x2360 | CURRENT_WEAPON_TYPE | Byte [SRAM] | |
| 0x2363 | DOG_READ | Word [SRAM] | |
| 0x236b | ⚙️ Market state / variant | Word [SRAM] | 0–3; randomized via RAND&3 in showcase mode; selects prophet behavior and OBJ 0x27 state [0x0a] |
| 0x236d | ⚙️ ACCESS_CODE_D1 | Word [SRAM] | Access code digit 1 (range 1–3); generated once on first visit to [0x43] or [0x54]; displayed as OBJ 3 state in control room |
| 0x236f | ⚙️ ACCESS_CODE_D2 | Word [SRAM] | Access code digit 2 (range 1–3) |
| 0x2371 | ⚙️ ACCESS_CODE_D3 | Word [SRAM] | Access code digit 3 (range 1–3) |
| 0x2373 | ⚙️ SECRET_CODE_D1 | Word [SRAM] | Secret door code digit 1 (range 1–3); used to unlock [0x45] secret boss room |
| 0x2375 | ⚙️ SECRET_CODE_D2 | Word [SRAM] | Secret door code digit 2 (range 1–3) |
| 0x2377 | ⚙️ SECRET_CODE_D3 | Word [SRAM] | Secret door code digit 3 (range 1–3) |
| 0x237b | WINDWALKER_LOCATION / previous WW destination | Word [SRAM] | Set to previous $237d value during WW landing [0x36] |
| 0x237d | WINDWALKER_LOCATION_HELPER / WW destination state | Word [SRAM] | 0/1 = fire pit landing; 2 = second landing; 4 = Omnitopia selected [0x36] |
| 0x238d | ⚙️ CHANGE_MUSIC | Word [SRAM] | [BOOLEAN] |
| 0x238f | TRANSITION_ENTER_DIRECTION | Word [SRAM] | |
| 0x2391 | 🎁 LOOT_ITEM | Word [SRAM] | |
| 0x2393 | 🎁 LOOT_AMOUNT_CURRENCY | Word [SRAM] | |
| 0x2395 | 🎁 LOOT_OBJECT | Word [SRAM] | |
| 0x239b | PRIZE_RATE_1 | Word [SRAM] | |
| 0x239d | PRIZE_RATE_2 | Word [SRAM] | |
| 0x239f | PRIZE_RATE_3 | Word [SRAM] | |
| 0x23a1 | PRIZE_DROP_1 | Word [SRAM] | |
| 0x23a3 | PRIZE_DROP_2 | Word [SRAM] | |
| 0x23a5 | PRIZE_DROP_3 | Word [SRAM] | |
| 0x23a7 | PRIZE_QUANTITY_1 | Word [SRAM] | |
| 0x23a9 | PRIZE_QUANTITY_2 | Word [SRAM] | |
| 0x23ab | PRIZE_QUANTITY_3 | Word [SRAM] | |
| 0x23ad | ⚙️ FADE_X | Word [SRAM] | Usually 0x80 (center) |
| 0x23af | ⚙️ FADE_Y | Word [SRAM] | Usually 0x70 (center) | |
| 0x23b1 | ⚙️ FADE_START | Word [SRAM] | |
| 0x23b3 | ⚙️ FADE_STEP | Word [SRAM] | |
| 0x23b5 | ⚙️ FADE_TRIGGER | Word [SRAM] | |
| 0x23bf | PACIFIED | Word [SRAM] | [BOOLEAN]; written 0x0001 on enter in [0x08] Nobilia Square |
| 0x23c1 | UNKNOWN_1 | Word [SRAM] | Used in: sandpits, bugmuck, bbm_2, swamp, pipemaze_rooms, waterfall, swamp_bridge, greenhouse (1=?) |
| 0x23c5 | ⚙️ ENEMY_SPAWNER_UNKNOWN_1 | Word [SRAM] | Usually 0x0280 or 0x0500 |
| 0x23d1 | NEXT_PROJECTILE_DAMAGE | Word [SRAM] | |
| 0x23d3 | ? | Word [SRAM] | Written 0x0001 before item-received text, 0x0000 after; seen in room [0x5c] |
| 0x23d5 | NEXT_DAMAGE_NO_KNOCKBACK | Word [SRAM] | |
| 0x23d7 | UNKNOWN_2 | Word [SRAM] | Used in: sterling grab, reactor room (1=?) |
| 0x23d9 | UNKNOWN_ETERNAL_DUST_DROP_PROPERTY | Word [SRAM] | Boss rush |
| 0x23db | Z_AFTER_TELEPORT | Word [SRAM] | |
| 0x23dd | ⚙️ ENEMY_SPAWNER_UNKNOWN_2 | Word [SRAM] | Mostly 0x0000 and 0xffff, once 0x0064 |
| 0x23e9 | 🎥 CAMERA_BOUNDRY_X_START | Word [SRAM] | |
| 0x23eb | 🎥 CAMERA_BOUNDRY_Y_START | Word [SRAM] | |
| 0x23ed | 🎥 CAMERA_BOUNDRY_X_END | Word [SRAM] | |
| 0x23ef | 🎥 CAMERA_BOUNDRY_Y_END | Word [SRAM] | |
| 0x2401 | 🎥 CAMERA_X_MIN | Word [SRAM] | |
| 0x2403 | 🎥 CAMERA_X_MAX | Word [SRAM] | |
| 0x2405 | 🎥 CAMERA_Y_MIN | Word [SRAM] | |
| 0x2407 | 🎥 CAMERA_Y_MAX | Word [SRAM] | |
| 0x240d | VENDOR_RECOMMEND_CURRENCY_CHANGE | Word [SRAM] | |
| 0x2413 | — | Word [SRAM] | Camera pan X target; written in FE Cutscenes 2 & 3 [0x51] |
| 0x2415 | — | Word [SRAM] | Camera pan Y target; written in FE Cutscenes 2 & 3 [0x51] |
| 0x241b | 🎥 FOREGROUND_OFFSET_X | Word [SRAM] | Dark forest only |
| 0x241d | 🎥 FOREGROUND_OFFSET_Y | Word [SRAM] | Dark forest only |
| 0x242b | 🎥 CAMERA_PAN_X | Word [SRAM] | |
| 0x242d | 🎥 CAMERA_PAN_Y | Word [SRAM] | |
| 0x242f | 🎥 CAMERA_PAN_SPEED | Word [SRAM] | Default 0x80 (core.evs line 690) |
| 0x2433 | ⚙️ ENEMY_SPAWNER_QUANTITY | Word [SRAM] | |
| 0x2437 | ⚙️ MAP_PALETTE | Word [SRAM] | thraxx (0=orange, 7=white); waterfall (7=normal, 0=?); ivor/ebon (7=ebon/ivor, 4=?); greenhouse (6=dark?); storage (7=dark?) |
| 0x2441 | GAIN_WEAPON | Byte [SRAM] | |
| 0x2443 | DOG_WRITE | Byte [SRAM] | Character ID (e.g. 0x02 = wolf) |
| 0x2445 | ALCHEMY_REWARD_PRESELECTION | Word [SRAM] | |
| 0x2449 | ⚙️ SAVE_SPOT_ID | Word [SRAM] | 0x0016 = Omnitopia Shops healing station [0x54]; 0x001b = Junkyard energy core [0x49]; written before save sub call |
| 0x244f | 📖 Prophet prediction index [0x0a] | Word [SRAM] | Current fortune state: 0=idle; 3–9=escalating predictions; reset after timer expires |
| 0x2451 | 📖 Prophet visit counter [0x0a] | Word [SRAM] | Incremented each B-trigger visit; affects branching |
| 0x2455 | VENDOR_ENTITY | Word [SRAM] | |
| 0x2457 | VENDOR_SHOP_ITEMS_SELL | Word [SRAM] | |
| 0x2459 | VENDOR_SHOP_ITEMS_BUY / SHOP_RING_MENU_AND_POSITION_ID | Word [SRAM] | Shared address |
| 0x245b | — | Word [SRAM] | Blimp entity ref; written in [0x51] zone 9 enter |
| 0x2493 | ? | Word [SESSION] | Cutscene entity X position; written and incremented to steer entity during Raptors intro cutscene [0x5c] |
| 0x2495 | ? | Word [SESSION] | Cutscene entity Y position; written and incremented to steer entity during Raptors intro cutscene [0x5c] |
| 0x249d | ? | Word [SESSION] | entity X pos for ABS call |
| 0x24fd | ⚙️ ENTRY_ORIGIN_CODE | Word [SRAM] | Entry-origin code; written before every CHANGE MAP from [0x48] Metroplex Tunnels; read by routing function `0x9ad5c8` to determine spawn position |
| 0x24ff | ⚙️ SAVED_BOY_X | Word [SRAM] | Boy X position saved before entering alarm room from [0x43]; restored on return |
| 0x2501 | ⚙️ SAVED_BOY_Y | Word [SRAM] | Boy Y position saved before entering alarm room from [0x43] |
| 0x2503 | ⚙️ SAVED_DOG_X | Word [SRAM] | Dog X position saved before entering alarm room from [0x43] |
| 0x2505 | ⚙️ SAVED_DOG_Y | Word [SRAM] | Dog Y position saved before entering alarm room from [0x43] |
| 0x2513 | ⚙️ Market entry timer base [0x0a] | Word [SRAM] | Snapshot of GameTimer on first market entry; market expires after 0xc4e0 ticks (~5.7 min) |
| 0x2515 | ⚙️ Market minutes remaining [0x0a/0x08] | Word [SRAM] | Countdown display value; decremented each minute; shown in trader "closing soon" dialogs |
| 0x2517 | 🏺 ANNIHILATION_AMULET | Word [SRAM] | |
| 0x2519 | 🏺 BEADS | Word [SRAM] | Trading goods inventory; sold by beads vendor in [0x7b] |
| 0x251b | 🏺 CERAMIC_POT | Word [SRAM] | |
| 0x251d | 🏺 CHICKEN | Word [SRAM] | |
| 0x251f | 🏺 GOLDEN_JACKAL | Word [SRAM] | |
| 0x2521 | 🏺 JEWELED_SCARAB | Word [SRAM] | |
| 0x2523 | 🏺 LIMESTONE_TABLET | Word [SRAM] | |
| 0x2525 | 🏺 PERFUME | Word [SRAM] | |
| 0x2527 | 🏺 RICE | Word [SRAM] | |
| 0x2529 | 🏺 SPICE | Word [SRAM] | |
| 0x252b | 🏺 SPOON | Word [SRAM] | |
| 0x252d | 🏺 TAPESTRY | Word [SRAM] | |
| 0x252f | 🏺 TICKET_FOR_EXHIBITION | Word [SRAM] | |
| 0x2533 | NEXT_ENEMY_FOLLOWS_ENTITY | Word [SRAM] | Consumed after enemy added |
| 0x2537 | STRING_PARAMETER_1 | Word [SRAM] | |
| 0x2539 | STRING_PARAMETER_2 | Word [SRAM] | |
| 0x253b | STRING_PARAMETER_3 | Word [SRAM] | |
| 0x253c…0x2544 | (gap) | Byte×9 [SRAM] | Unmapped |
| 0x2545 | — | Word [SESSION] | Dialog response preselect (save menu yes/no) [0x51] |
| 0x2547…0x254c | (gap) | Byte×6 [SRAM] | Unmapped |
| 0x254d | 📖 Prophet timer base [0x0a] | Word [SRAM] | Snapshot of GameTimer; resets prediction index if elapsed > 0x0e10 ticks |
| 0x254f…0x2f51 | (gap: ~2563 bytes) | Byte×2563 [SRAM] | Unmapped |
| 0x2f52 | ⚗️ LEVEL_LOW_ACID_RAIN | Word [SRAM] | |
| 0x2f54 | ⚗️ LEVEL_LOW_ATLAS | Word [SRAM] | |
| 0x2f56 | ⚗️ LEVEL_LOW_BARRIER | Word [SRAM] | |
| 0x2f58 | ⚗️ LEVEL_LOW_CALL_UP | Word [SRAM] | |
| 0x2f5a | ⚗️ LEVEL_LOW_CORROSION | Word [SRAM] | |
| 0x2f5c | ⚗️ LEVEL_LOW_CRUSH | Word [SRAM] | |
| 0x2f5e | ⚗️ LEVEL_LOW_CURE | Word [SRAM] | |
| 0x2f60 | ⚗️ LEVEL_LOW_DEFEND | Word [SRAM] | |
| 0x2f62 | ⚗️ LEVEL_LOW_DOUBLE_DRAIN | Word [SRAM] | |
| 0x2f64 | ⚗️ LEVEL_LOW_DRAIN | Word [SRAM] | |
| 0x2f66 | ⚗️ LEVEL_LOW_ENERGIZE | Word [SRAM] | |
| 0x2f68 | ⚗️ LEVEL_LOW_ESCAPE | Word [SRAM] | |
| 0x2f6a | ⚗️ LEVEL_LOW_EXPLOSION | Word [SRAM] | |
| 0x2f6c | ⚗️ LEVEL_LOW_FIREBALL | Word [SRAM] | |
| 0x2f6e | ⚗️ LEVEL_LOW_FIRE_POWER | Word [SRAM] | |
| 0x2f70 | ⚗️ LEVEL_LOW_FLASH | Word [SRAM] | |
| 0x2f72 | ⚗️ LEVEL_LOW_FORCE_FIELD | Word [SRAM] | |
| 0x2f74 | ⚗️ LEVEL_LOW_HARD_BALL | Word [SRAM] | |
| 0x2f76 | ⚗️ LEVEL_LOW_HEAL | Word [SRAM] | |
| 0x2f78 | ⚗️ LEVEL_LOW_LANCE | Word [SRAM] | |
| 0x2f7a | ⚗️ LEVEL_LOW_LASER | Word [SRAM] | |
| 0x2f7c | ⚗️ LEVEL_LOW_LEVITATE | Word [SRAM] | |
| 0x2f7e | ⚗️ LEVEL_LOW_LIGHTNING_STORM | Word [SRAM] | |
| 0x2f80 | ⚗️ LEVEL_LOW_MIRACLE_CURE | Word [SRAM] | |
| 0x2f82 | ⚗️ LEVEL_LOW_NITRO | Word [SRAM] | |
| 0x2f84 | ⚗️ LEVEL_LOW_ONE_UP | Word [SRAM] | |
| 0x2f86 | ⚗️ LEVEL_LOW_REFLECT | Word [SRAM] | |
| 0x2f88 | ⚗️ LEVEL_LOW_REGROWTH | Word [SRAM] | |
| 0x2f8a | ⚗️ LEVEL_LOW_REVEALER | Word [SRAM] | |
| 0x2f8c | ⚗️ LEVEL_LOW_REVIVE | Word [SRAM] | |
| 0x2f8e | ⚗️ LEVEL_LOW_SLOW_BURN | Word [SRAM] | |
| 0x2f90 | ⚗️ LEVEL_LOW_SPEED | Word [SRAM] | |
| 0x2f92 | ⚗️ LEVEL_LOW_STING | Word [SRAM] | |
| 0x2f94 | ⚗️ LEVEL_LOW_STOP | Word [SRAM] | |
| 0x2f96 | ⚗️ LEVEL_LOW_SUPER_HEAL | Word [SRAM] | |
| 0x2f98 | ⚗️ LEVEL_HIGH_ACID_RAIN | Word [SRAM] | |
| 0x2f9a | ⚗️ LEVEL_HIGH_ATLAS | Word [SRAM] | |
| 0x2f9c | ⚗️ LEVEL_HIGH_BARRIER | Word [SRAM] | |
| 0x2f9e | ⚗️ LEVEL_HIGH_CALL_UP | Word [SRAM] | |
| 0x2fa0 | ⚗️ LEVEL_HIGH_CORROSION | Word [SRAM] | |
| 0x2fa2 | ⚗️ LEVEL_HIGH_CRUSH | Word [SRAM] | |
| 0x2fa4 | ⚗️ LEVEL_HIGH_CURE | Word [SRAM] | |
| 0x2fa6 | ⚗️ LEVEL_HIGH_DEFEND | Word [SRAM] | |
| 0x2fa8 | ⚗️ LEVEL_HIGH_DOUBLE_DRAIN | Word [SRAM] | |
| 0x2faa | ⚗️ LEVEL_HIGH_DRAIN | Word [SRAM] | |
| 0x2fac | ⚗️ LEVEL_HIGH_ENERGIZE | Word [SRAM] | |
| 0x2fae | ⚗️ LEVEL_HIGH_ESCAPE | Word [SRAM] | |
| 0x2fb0 | ⚗️ LEVEL_HIGH_EXPLOSION | Word [SRAM] | |
| 0x2fb2 | ⚗️ LEVEL_HIGH_FIREBALL | Word [SRAM] | |
| 0x2fb4 | ⚗️ LEVEL_HIGH_FIRE_POWER | Word [SRAM] | |
| 0x2fb6 | ⚗️ LEVEL_HIGH_FLASH | Word [SRAM] | |
| 0x2fb8 | ⚗️ LEVEL_HIGH_FORCE_FIELD | Word [SRAM] | |
| 0x2fba | ⚗️ LEVEL_HIGH_HARD_BALL | Word [SRAM] | |
| 0x2fbc | ⚗️ LEVEL_HIGH_HEAL | Word [SRAM] | |
| 0x2fbe | ⚗️ LEVEL_HIGH_LANCE | Word [SRAM] | |
| 0x2fc0 | ⚗️ LEVEL_HIGH_LASER | Word [SRAM] | |
| 0x2fc2 | ⚗️ LEVEL_HIGH_LEVITATE | Word [SRAM] | |
| 0x2fc4 | ⚗️ LEVEL_HIGH_LIGHTNING_STORM | Word [SRAM] | |
| 0x2fc6 | ⚗️ LEVEL_HIGH_MIRACLE_CURE | Word [SRAM] | |
| 0x2fc8 | ⚗️ LEVEL_HIGH_NITRO | Word [SRAM] | |
| 0x2fca | ⚗️ LEVEL_HIGH_ONE_UP | Word [SRAM] | |
| 0x2fcc | ⚗️ LEVEL_HIGH_REFLECT | Word [SRAM] | |
| 0x2fce | ⚗️ LEVEL_HIGH_REGROWTH | Word [SRAM] | |
| 0x2fd0 | ⚗️ LEVEL_HIGH_REVEALER | Word [SRAM] | |
| 0x2fd2 | ⚗️ LEVEL_HIGH_REVIVE | Word [SRAM] | |
| 0x2fd4 | ⚗️ LEVEL_HIGH_SLOW_BURN | Word [SRAM] | |
| 0x2fd6 | ⚗️ LEVEL_HIGH_SPEED | Word [SRAM] | |
| 0x2fd8 | ⚗️ LEVEL_HIGH_STING | Word [SRAM] | |
| 0x2fda | ⚗️ LEVEL_HIGH_STOP | Word [SRAM] | |
| 0x2fdc | ⚗️ LEVEL_HIGH_SUPER_HEAL | Word [SRAM] | |
| 0x2fdd…0x2833 | (gap: 1400+ bytes) | Byte×1400 | Unmapped |
| 0x2834 | ⚙️ One-time B-trigger #1 (NPC spawn) [0x55] (0x01)<br>⚙️ Switch OBJ 8 [0x55] (0x02)<br>⚙️ Switch OBJ 9 [0x55] (0x04)<br>⚙️ Switch OBJ 11 [0x55] (0x08)<br>⚙️ Switch OBJ 10 [0x55] (0x10)<br>⚙️ Lever OBJ 17 [0x55] (0x20)<br>⚙️ Lever OBJ 18 [0x55] (0x40)<br>⚙️ Lever OBJ 19 [0x55] (0x80) | Byte [SRAM] | One-time switch/lever trigger flags — 'mids bottom [0x55]: each bit set on first activation, prevents repeat; loads NPC 0x59 (switch) or 0x5a (lever) and sets OBJ state 1 |
| 0x2835 | ⚙️ Bridge trap instability bits OBJ 22-29 (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) [0x28]; NPC slot pointer [0x2c][0x29] | Byte [RAM] | Session-local in [0x28] — bits 0x01–0x80 correspond to OBJs 22–29 first-crossing state; all cleared in fall reset sub; reused as NPC slot register ($2835) in other Halls rooms |
| 0x2836 | ⚙️ Bridge trap 2nd-hit flag OBJ 17 [0x28] (0x04)<br>⚙️ Bridge trap 2nd-hit flag OBJ 18 [0x28] (0x08)<br>⚙️ Bridge trap 2nd-hit flag OBJ 19 [0x28] (0x10)<br>⚙️ Bridge trap 2nd-hit flag OBJ 20 [0x28] (0x20)<br>⚙️ Bridge trap 2nd-hit flag OBJ 21 [0x28] (0x40)<br>⚙️ Bridge trap 2nd-hit flag OBJ 22 [0x28] (0x80)<br>? OBJ 30/31 instability bits (0x01/0x02) | Byte [RAM] | Session-local; set on first crossing of each bridge section; triggers big fall sub on second crossing; all bits cleared in fall reset sub at `0x97ab84`; 0x01/0x02 possibly OBJ 30/31 instability (unconfirmed) |
| 0x2837 | ⚙️ Bridge trap 2nd-hit flag OBJ 23 [0x28] (0x01)<br>⚙️ Bridge trap 2nd-hit flag OBJ 24 [0x28] (0x02)<br>⚙️ Bridge trap 2nd-hit flag OBJ 25 [0x28] (0x04)<br>? OBJ 26-31 2nd-hit bits (0x08/0x10/0x20/0x40/0x80) | Byte [RAM] | Session-local; same pattern as `$2836`; 0x08–0x80 extrapolated for OBJs 26–30 (unconfirmed) |
| 0x2838 | ⚙️ Fall-sub re-entry guard [0x28] (0x02)<br>⚙️ Dog-close active [0x28] (0x04)<br>⚙️ Camera wide-view activated [0x28] (0x10) | Byte [RAM] | Session-local — 0x02: prevents double-trigger of big fall sub (set on fall entry, cleared in OBJ reset); 0x04: dog proximity flag for bridge section dog-close tiles; 0x10: one-time camera wide-view trigger |
| 0x2839…×0x28fb | General-purpose RAM | Byte×195 | Examples: entity slots, attack slots, dark forest layout; `$2856` = crater guard dialogue toggle [0x08] (session-local) |
| 0x28fc…0x4eb2 | (gap: 6100+ bytes) | Byte×6100 | Unmapped |

