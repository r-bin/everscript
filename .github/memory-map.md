# Secret of Evermore RAM Map

| Address | Name | Type | Notes |
|---------|------|------|-------|
| 0x0100 | ⚙️ MEMORY.FRAME_COUNTER_1 | Word | |
| 0x0102 | ⚙️ MEMORY.FRAME_COUNTER_2 | Word |
| 0x0104 | MEMORY.INPUT_P1 | Word |
| 0x0341 | MEMORY.LAST_ENTITY | Word |
| 0x07a4 | MEMORY.RING_MENU_WEAPON | Word | [pointer] |
| 0x07c8 | MEMORY.RING_MENU_CONSUMABLES | Word | [pointer] |
| 0x0810 | MEMORY.RING_MENU_BOY | Word | [pointer] |
| 0x0834 | MEMORY.RING_MENU_DOG | Word | [pointer] |
| 0x0a35 | MEMORY.BOY_MAX_HP | Word |
| 0x0a47 | MEMORY.BOY_HIT | Word |
| 0x0a49 | MEMORY.BOY_XP | Word |
| 0x0a4b | MEMORY.BOY_XP_2 | Word | High word |
| 0x0a50 | MEMORY.BOY_LEVEL | Word |
| 0x0a7f | MEMORY.DOG_MAX_HP | Word |
| 0x0a9a | MEMORY.DOG_LEVEL | Word |
| 0x0aba | MEMORY.CURRENT_WEAPON | Byte |
| 0x0ABE | MEMORY.CURRENT_ARMOR_COLLAR | Word |
| 0x0AC0 | MEMORY.CURRENT_ARMOR_CHEST | Word |
| 0x0AC2 | MEMORY.CURRENT_ARMOR_HELM | Word |
| 0x0AC4 | MEMORY.CURRENT_ARMOR_GLOVE | Word |
| 0x0ac6 | MEMORY.TALONS | Word |
| 0x0ac9 | MEMORY.JEWELS | Word |
| 0x0acc | MEMORY.GOLD | Word |
| 0x0acf | MEMORY.CREDITS | Word |
| 0x0AD2…0x0ADA | MEMORY.SELECTED_ALCHEMY_0…8 | Byte×9 |
| 0x0ADB | MEMORY.CURRENT_WEAPON (buggy) | Byte | Use 0x235f instead |
| 0x0ADD | MEMORY.LEVEL_FIST | Word | Unused |
| 0x0ADF | ⚔️ MEMORY.LEVEL_1_SWORD | Word |
| 0x0AE1 | ⚔️ MEMORY.LEVEL_2_SWORD | Word |
| 0x0AE3 | ⚔️ MEMORY.LEVEL_3_SWORD | Word |
| 0x0AE5 | ⚔️ MEMORY.LEVEL_4_SWORD | Word |
| 0x0AE7 | ⚔️ MEMORY.LEVEL_1_AXE | Word |
| 0x0AE9 | ⚔️ MEMORY.LEVEL_2_AXE | Word |
| 0x0AEB | ⚔️ MEMORY.LEVEL_3_AXE | Word |
| 0x0AED | ⚔️ MEMORY.LEVEL_4_AXE | Word |
| 0x0AEF | ⚔️ MEMORY.LEVEL_1_SPEAR | Word |
| 0x0AF1 | ⚔️ MEMORY.LEVEL_2_SPEAR | Word |
| 0x0AF3 | ⚔️ MEMORY.LEVEL_3_SPEAR | Word |
| 0x0AF5 | ⚔️ MEMORY.LEVEL_4_SPEAR | Word |
| 0x0AF7 | ⚔️ MEMORY.LEVEL_BAZOOKA | Word |
| 0x0B07 | ⚔️ MEMORY.LEVEL_DOG | Word |
| 0x0B09 | MEMORY.BOY_COMBATIVENESS | Word |
| 0x0B0d | MEMORY.DOG_COMBATIVENESS | Word |
| 0x0B19 | ⚙️ MEMORY.TIMER_1 | Word |
| 0x0B1B | ⚙️ MEMORY.TIMER_2 | Word |
| 0x0b83 | ⚙️ ? | Word | Written 0x8000 by opcode 0x27 (Fade-out screen); used in room [0x38] |
| 0x0ba1 | MEMORY.RING_MENU_SHOP | Word | [pointer] |
| 0x0bfe | MEMORY.RING_MENU_BOY_ARMOR_CHEST | Word | [pointer] |
| 0x0c23 | MEMORY.RING_MENU_BOY_ARMOR_HELM | Word | [pointer] |
| 0x0c47 | MEMORY.RING_MENU_BOY_ARMOR_ARMLET | Word | [pointer] |
| 0x0c6b | MEMORY.RING_MENU_DOG_ARMOR | Word | [pointer] |
| 0x0c8f | MEMORY.RING_MENU_WEAPON_BAZOOKA | Word | [pointer] |
| 0x0cb5 | MEMORY.RING_MENU_CONSUMABLES_CALLBEADS_INNER | Word | [pointer] |
| 0x0cd9 | MEMORY.RING_MENU_CONSUMABLES_CALLBEADS | Word | [pointer] |
| 0x0ea2 | ? | Word | Paired with $0eac; written by opcode 0x3f (NPC script setup); "set in lots of places" |
| 0x0eac | ? | Word | Paired with $0ea2; holds NPC script addresses; written by opcode 0x3f |
| 0x0ec2 | MEMORY.POINTER_NEXT_PROJECTILE_SLOT | Word |
| 0x0ec6 | MEMORY.COPY_INPUT_P1 | Word |
| 0x0f5a | MEMORY.RING_MENU_DEBUG | Word | [pointer] |
| 0x1278…0x1286 | ⚙️ MEMORY.PALETTE_SLOT_1…8 | Word×4 | Palette slots 1–8 |
| 0x128e | ⚙️ MEMORY.ANIMATION_START_COPY | Word |
| 0x1290 | ⚙️ MEMORY.ANIMATION_START | Word |
| 0x1292…0x1371 | ⚙️ MEMORY.ANIMATION_STACK | — | Animation structs |
| 0x2210…0x2233 | MEMORY.BOY_NAME | Byte×35 [SRAM] | |
| 0x2234…0x2257 | MEMORY.DOG_NAME | Byte×35 [SRAM] | |
| 0x2258 | ⚗️ ACID_RAIN (0x01)<br>⚗️ ATLAS (0x02)<br>⚗️ BARRIER (0x04)<br>⚗️ CALL_UP (0x08)<br>⚗️ CORROSION (0x10)<br>⚗️ CRUSH (0x20)<br>⚗️ CURE (0x40)<br>⚗️ DEFEND (0x80) | Byte [SRAM] | |
| 0x2259 | ⚗️ DOUBLE_DRAIN (0x01)<br>⚗️ DRAIN (0x02)<br>⚗️ ENERGIZE (0x04)<br>⚗️ ESCAPE (0x08)<br>⚗️ EXPLOSION (0x10)<br>⚗️ FIREBALL (0x20)<br>⚗️ FIRE_POWER (0x40)<br>⚗️ FLASH (0x80) | Byte [SRAM] | |
| 0x225a | ⚗️ FORCE_FIELD (0x01)<br>⚗️ HARD_BALL (0x02)<br>⚗️ HEAL (0x04)<br>⚗️ LANCE (0x08)<br>⚗️ LASER (0x10)<br>⚗️ LEVITATE (0x20)<br>⚗️ LIGHTNING_STORM (0x40)<br>⚗️ MIRACLE_CURE (0x80) | Byte [SRAM] | |
| 0x225b | ⚗️ NITRO (0x01)<br>⚗️ ONE_UP (0x02)<br>⚗️ REFLECT (0x04)<br>⚗️ REGROWTH (0x08)<br>⚗️ REVEALER (0x10)<br>⚗️ REVIVE (0x20)<br>⚗️ SLOW_BURN (0x40)<br>⚗️ SPEED (0x80) | Byte [SRAM] | |
| 0x225c | STING (0x01)<br>STOP (0x02)<br>SUPER_HEAL (0x04)<br>? (0x08/0x10/0x20)<br>FE call beads? (0x40)<br>? (0x80) | Byte [SRAM] | |
| 0x225d | ? | Byte [SRAM] | Story flag range; seen in Prehistoria scripts |
| 0x225e | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40)<br>📖 Talked to Blimp in hut? [0x51] (0x80) | Byte [SRAM] | Story flag range; seen in Prehistoria scripts |
| 0x225f | 📖 BLIMP_BRIDGE (0x01)<br>📖 Levitate hint shown? [0x51] (0x02)<br>? (0x04/0x08/0x10/0x20)<br>📖 RAPTORS (0x40)<br>📖 Village post-thraxx msg shown? [0x51] (0x80) | Byte [SRAM] | Story progress flags |
| 0x2260 | ? (0x01/0x02/0x04/0x08)<br>📖 THRAXX (0x10)<br>? (0x20)<br>📖 MAGMAR (0x40)<br>? (0x80) | Byte [SRAM] | Story progress flags |
| 0x2261 | 📖 DOG_UNAVAILABLE (0x01)<br>📖 BOY_UNAVAILABLE (0x02)<br>? (0x04/0x08/0x10)<br>💎 ARMOR_POLISH (0x20)<br>💎 CHOCOBO_EGG (0x40)<br>💎 INSECT_INCENSE (0x80) | Byte [SRAM] | Story progress flags |
| 0x2262 | 💎 JADE_DISK (0x01)<br>💎 JAGUAR_RING (0x02)<br>💎 MAGIC_GOURD (0x04)<br>💎 MOXA_STICK (0x08)<br>💎 ORACLE_BONE (0x10)<br>💎 RUBY_HEART (0x20)<br>💎 SILVER_SHEATH (0x40)<br>💎 STAFF_OF_LIFE (0x80) | Byte [SRAM] | |
| 0x2263 | 💎 SUN_STONE (0x01)<br>💎 THUGS_CLOAK (0x02)<br>💎 WIZARDS_COIN (0x04)<br>? (0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | |
| 0x2264 | 💎 DIAMOND_EYE (0x01)<br>💎 DIAMOND_EYES (0x02)<br>💎 GAUGE (0x04)<br>💎 WHEEL (0x08)<br>💎 QUEENS_KEY (0x10)<br>💎 ENERGY_CORE (0x20)<br>🫙 roots gourd obj0 [0x51] (0x40)<br>🫙 water gourd obj1 [0x51] (0x80) | Byte [SRAM] | |
| 0x2265 | 🫙 water gourd obj2 [0x51] (0x01)<br>🫙 water gourd obj3 [0x51] (0x02)<br>🫙 money gourd obj4 [0x51] (0x04)<br>🫙 nectar gourd obj5 [0x51] (0x08)<br>🫙 water gourd obj6 [0x51] (0x10)<br>🫙 water gourd obj7 [0x51] (0x20)<br>🫙 clay gourd obj8 [0x51] (0x40)<br>🫙 money gourd obj9 [0x51] (0x80) | Byte [SRAM] | Object persistence flags:<br>Act1 Huts [0x51] |
| 0x2266 | 🫙 clay gourd obj10 [0x51] (0x01)<br>🫙 water gourd obj11 [0x51] (0x02)<br>🫙 roots gourd obj13 [0x51] (0x04)<br>🫙 roots gourd obj12 [0x51] (0x08)<br>? (0x10)<br>🫙 roots gourd obj14 [0x51] (0x20)<br>🫙 water gourd obj15 [0x51] (0x40)<br>🫙 call beads/biscuit obj17 [0x51] (0x80) | Byte [SRAM] | Object persistence flags:<br>Act1 Huts [0x51] |
| 0x2267 | 🫙 water gourd obj16 [0x51] (0x01)<br>🫙 petal gourd obj18 [0x51] (0x02)<br>🫙 clay gourd obj19 [0x51] (0x04)<br>🫙 water gourd obj20 [0x51] (0x08)<br>🫙 water gourd obj21 [0x51] (0x10)<br>🫙 water gourd obj22 [0x51] (0x20)<br>🫙 water gourd obj23 [0x51] (0x40)<br>? (0x80) | Byte [SRAM] | Object persistence flags:<br>Act1 Huts [0x51] |
| 0x2268 | 🫙 water gourd obj24 [0x51] (0x01)<br>🫙 gourd obj0 [0x26] (0x02)<br>🫙 clay gourd obj1 [0x26] (0x04)<br>🫙 ash gourd obj2 [0x26] (0x08)<br>? (0x10/0x20)<br>🫙 GOURD_1 obj0 (0x40)<br>🫙 oil gourd obj1 [0x38] (0x80) | Byte [SRAM] | Object persistence flags:<br>[0x38] South Jungle / Start<br>[0x26] West area with Defend<br>[0x51] Act1 Huts |
| 0x2269 | 🫙 petal gourd obj2 [0x38] (0x01)<br>🫙 shell hat gourd obj3 [0x38] (0x02)<br>🫙 nectar gourd obj4 [0x38] (0x04)<br>🫙 money gourd obj5 [0x38] (0x08)<br>? (0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start |
| 0x226a | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x226b | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x226c | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x226d | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x226e | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x226f | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2270 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2271 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2272 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2273 | 🫙 oil gourd obj0 [0x34] (0x01)<br>🫙 wax gourd obj1 [0x34] (0x02)<br>🫙 wax gourd obj2 [0x34] (0x04)<br>? (0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>Strong Heart's Hut |
| 0x2274 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2275 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2276 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2277 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2278 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2279 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x227a | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x227b | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x227c | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x227d | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x227e | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x227f | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2280 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2281 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2282 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2283 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2284 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2285 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2286 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2287 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2288 | ? (0x01/0x02/0x04)<br>📖 talked to Defend guy [0x26] (0x08)<br>? (0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>West area with Defend [0x26] |
| 0x2289 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x228a | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x228b | 📖 FE visited pre-thraxx? [0x51] (0x01)<br>? (0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>0x01 tested in [0x51] east exit and FE First Encounter |
| 0x228c | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x228d | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x228e | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x228f | ? (0x01/0x02/0x04)<br>👃 sniff obj14 [0x38] (0x08)<br>👃 sniff obj28 [0x38] (0x10)<br>👃 sniff obj9 [0x38] (0x20)<br>👃 sniff obj30 [0x38] (0x40)<br>👃 sniff obj10 [0x38] (0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start |
| 0x2290 | 👃 sniff obj12 [0x38] (0x01)<br>👃 sniff obj13 [0x38] (0x02)<br>👃 sniff obj16 [0x38] (0x04)<br>👃 sniff obj19 [0x38] (0x08)<br>👃 sniff obj26 [0x38] (0x10)<br>👃 sniff obj6 [0x38] (0x20)<br>👃 sniff obj7 [0x38] (0x40)<br>👃 sniff obj23 [0x38] (0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start |
| 0x2291 | 👃 sniff obj24 [0x38] (0x01)<br>👃 sniff obj27 [0x38] (0x02)<br>👃 sniff obj8 [0x38] (0x04)<br>👃 sniff obj11 [0x38] (0x08)<br>👃 sniff obj29 [0x38] (0x10)<br>👃 sniff obj15 [0x38] (0x20)<br>👃 sniff obj17 [0x38] (0x40)<br>👃 sniff obj18 [0x38] (0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start |
| 0x2292 | 👃 sniff obj20 [0x38] (0x01)<br>👃 sniff obj21 [0x38] (0x02)<br>👃 sniff obj22 [0x38] (0x04)<br>👃 sniff obj25 [0x38] (0x08)<br>? (0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>South Jungle / Start |
| 0x2293 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2294 | ? (0x01/0x02/0x04/0x08/0x10)<br>👃 roots sniff obj1 [0x5b] (0x20)<br>👃 roots sniff obj2 [0x5b] (0x40)<br>👃 roots sniff obj5 [0x5b] (0x80) | Byte [SRAM] | Object persistence flags:<br>East jungle [0x5b] |
| 0x2295 | 👃 roots sniff obj6 [0x5b] (0x01)<br>👃 roots sniff obj7 [0x5b] (0x02)<br>👃 water sniff obj0 [0x5b] (0x04)<br>👃 water sniff obj11 [0x5b] (0x08)<br>👃 water sniff obj12 [0x5b] (0x10)<br>👃 water sniff obj3 [0x5b] (0x20)<br>👃 water sniff obj4 [0x5b] (0x40)<br>👃 clay sniff obj13 [0x5b] (0x80) | Byte [SRAM] | Object persistence flags:<br>East jungle [0x5b] |
| 0x2296 | 👃 clay sniff obj8 [0x5b] (0x01)<br>👃 clay sniff obj9 [0x5b] (0x02)<br>👃 clay sniff obj10 [0x5b] (0x04)<br>? (0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>East jungle [0x5b] |
| 0x2297 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2298 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x2299 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x229a | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x229b | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x229c | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x229d | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x229e | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x229f | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a0 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a1 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a2 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a3 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a4 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a5 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a6 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a7 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a8 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22a9 | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22aa | ? (0x01/0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags |
| 0x22ab | ? (0x01/0x02/0x04/0x08/0x10/0x20)<br>📖 FLOWERS_CUTSCENE_WATCHED (0x40)<br>? (0x80) | Byte [SRAM] | |
| 0x22ac…0x22b3 | (gap) | Byte×8 [SRAM] | Unmapped |
| 0x22b4 | ? (0x01)<br>👃 sniff obj6 [0x5c] (0x02)<br>👃 sniff obj8 [0x5c] (0x04)<br>👃 sniff obj7 [0x5c] (0x08)<br>👃 sniff obj9 [0x5c] (0x10)<br>? (0x20/0x40/0x80) | Byte [SRAM] | Object persistence flags:<br>Raptors [0x5c] |
| 0x22b5…0x22d9 | (gap) | Byte×37 [SRAM] | Unmapped |
| 0x22da | ? (0x01)<br>⚔️ SWORD_1 (0x02)<br>⚔️ SWORD_2 (0x04)<br>⚔️ SWORD_3 (0x08)<br>⚔️ SWORD_4 (0x10)<br>⚔️ AXE_1 (0x20)<br>⚔️ AXE_2 (0x40)<br>⚔️ AXE_3 (0x80) | Byte [SRAM] | Bone Crusher (SWORD_1)<br>Gladiator Sword (SWORD_2)<br>Crusader Sword (SWORD_3)<br>Neutron Blade (SWORD_4)<br>Spider's Claw (AXE_1)<br>Bronze Axe (AXE_2)<br>Knight Basher (AXE_3) |
| 0x22db | ⚔️ AXE_4 (0x01)<br>⚔️ SPEAR_1 (0x02)<br>⚔️ SPEAR_2 (0x04)<br>⚔️ SPEAR_3 (0x08)<br>⚔️ SPEAR_4 (0x10)<br>⚔️ BAZOOKA (0x20)<br>? (0x40/0x80) | Byte [SRAM] | Atom Smasher (AXE_4)<br>Horn Spear (SPEAR_1)<br>Bronze Spear (SPEAR_2)<br>Lance (SPEAR_3)<br>Laser Lance (SPEAR_4)<br>Bazooka (BAZOOKA) |
| 0x22dc | ? (0x01/0x02/0x04)<br>📖 WINDWALKER_UNLOCKED (0x08)<br>? (0x10/0x20/0x40/0x80) | Byte [SRAM] | |
| 0x22e5 | 📖 Defeated raptors? [0x51] (0x20)<br>? (0x01/0x02/0x04/0x08/0x10/0x40/0x80) | Byte [SRAM] | Set in FE Cutscene 1 [0x51]; read in FE First Encounter |
| 0x22ea | ⚙️ LOOT_SUCCESSFUL (0x01)<br>⚙️ ? (0x02)<br>⚙️ EMPTY_SRAM (0x04)<br>⚙️ ? (0x08/0x10/0x20/0x40)<br>⚙️ SHOW_HUD (0x80) | Byte [SRAM] | |
| 0x22eb | ⚙️ ? (0x01)<br>⚙️ START_PRESSED (0x02)<br>⚙️ INTRO_DEMO_MODE (0x04)<br>⚙️ DEBUG (0x08)<br>⚙️ ? (0x10)<br>⚙️ IN_ANIMATION (0x20)<br>⚙️ ? (0x40/0x80) | Byte [SRAM] | [BOOLEAN] |
| 0x22ec | ? (0x01/0x02/0x04/0x08/0x10)<br>? (0x20)<br>? (0x40/0x80) | Byte [SRAM] | 0x20 set in FE Cutscene 3 [0x51] |
| 0x22ed | ? (0x01)<br>? (0x02)<br>? (0x04)<br>? (0x08/0x10/0x20/0x40)<br>? (0x80) | Byte [SRAM] | 0x04 tested in [0x5c] raptor fight (set by BOY_RAPTORS_SCREEN, core.evs line 189); also gates FE Cutscene 1 in [0x51]; 0x02 in shop_buy (core.evs line 7461); 0x80 in sewers pit-fall (core.evs line 11976) |
| 0x22ee | ? (0x01)<br>? (0x02) | Byte [SRAM] | 0x01 cleared in [0x34] enter script (dumper: "intro/outro? flag in prof. lab"); also set as FE→hut transition flag in [0x51] (teleports boy/dog, then cleared); 0x02 written True/False in shop_buy (core.evs line 7468) |
| 0x22f1 | ? (0x01/0x02/0x04/0x08/0x10)<br>FE visited or post-WW? [0x51] (0x20)<br>OUTRO (0x40)<br>? (0x80) | Byte [SRAM] | |
| 0x22f2 | in credits (0x01)<br>? (0x02/0x04/0x08/0x10/0x20/0x40/0x80) | Byte [SRAM] | Seen in [0x5b] enter: branches to credits cutscene path |
| 0x22f3 | ? (0x01/0x02/0x04/0x08/0x10)<br>📖 SALABOG (0x20)<br>? (0x40/0x80) | Byte [SRAM] | |
| 0x22fc | MEMORY.DESERT_Y | Byte [SRAM] | |
| 0x22fd | MEMORY.DESERT_X | Byte [SRAM] | |
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
| 0x2345 | AMMO_1 | Byte [SRAM] | |
| 0x2346 | AMMO_2 | Byte [SRAM] | |
| 0x2347 | AMMO_3 | Byte [SRAM] | |
| 0x2348 | MEMORY.CURRENCY_CURRENT | Byte [SRAM] | |
| 0x234a | ? | Byte [SRAM] | Written 0x63 (=99) in room [0x38] enter script after intro; opcode 0x14; purpose unknown |
| 0x234b | MEMORY.FAKE_HOUSE_ID | Word [SRAM] | |
| 0x2355 | MEMORY.WINDWALKER_TYPE | Word [SRAM] | |
| 0x235f | MEMORY.CURRENT_WEAPON | Byte [SRAM] | |
| 0x2360 | MEMORY.CURRENT_WEAPON_TYPE | Byte [SRAM] | |
| 0x2363 | MEMORY.DOG_READ | Word [SRAM] | |
| 0x237b | MEMORY.WINDWALKER_LOCATION | Word [SRAM] | |
| 0x237d | MEMORY.WINDWALKER_LOCATION_HELPER | Word [SRAM] | |
| 0x238d | ⚙️ MEMORY.CHANGE_MUSIC | Word [SRAM] | [BOOLEAN] |
| 0x238f | MEMORY.TRANSITION_ENTER_DIRECTION | Word [SRAM] | |
| 0x2391 | MEMORY.LOOT_ITEM | Word [SRAM] | |
| 0x2393 | MEMORY.LOOT_AMOUNT_CURRENCY | Word [SRAM] | |
| 0x2395 | MEMORY.LOOT_OBJECT | Word [SRAM] | |
| 0x239b | MEMORY.PRIZE_RATE_1 | Word [SRAM] | |
| 0x239d | MEMORY.PRIZE_RATE_2 | Word [SRAM] | |
| 0x239f | MEMORY.PRIZE_RATE_3 | Word [SRAM] | |
| 0x23a1 | MEMORY.PRIZE_DROP_1 | Word [SRAM] | |
| 0x23a3 | MEMORY.PRIZE_DROP_2 | Word [SRAM] | |
| 0x23a5 | MEMORY.PRIZE_DROP_3 | Word [SRAM] | |
| 0x23a7 | MEMORY.PRIZE_QUANTITY_1 | Word [SRAM] | |
| 0x23a9 | MEMORY.PRIZE_QUANTITY_2 | Word [SRAM] | |
| 0x23ab | MEMORY.PRIZE_QUANTITY_3 | Word [SRAM] | |
| 0x23ad | ⚙️ MEMORY.FADE_X | Word [SRAM] | Usually 0x80 (center) |
| 0x23af | ⚙️ MEMORY.FADE_Y | Word [SRAM] | Usually 0x70 (center) | |
| 0x23b1 | ⚙️ MEMORY.FADE_START | Word [SRAM] | |
| 0x23b3 | ⚙️ MEMORY.FADE_STEP | Word [SRAM] | |
| 0x23b5 | ⚙️ MEMORY.FADE_TRIGGER | Word [SRAM] | |
| 0x23bf | MEMORY.PACIFIED | Word [SRAM] | [BOOLEAN] |
| 0x23c1 | MEMORY.UNKNOWN_1 | Word [SRAM] | Used in: sandpits, bugmuck, bbm_2, swamp, pipemaze_rooms, waterfall, swamp_bridge, greenhouse (1=?) |
| 0x23c5 | ⚙️ MEMORY.ENEMY_SPAWNER_UNKNOWN_1 | Word [SRAM] | Usually 0x0280 or 0x0500 |
| 0x23d1 | MEMORY.NEXT_PROJECTILE_DAMAGE | Word [SRAM] | |
| 0x23d3 | ? | Word [SRAM] | Written 0x0001 before item-received text, 0x0000 after; seen in room [0x5c] |
| 0x23d5 | MEMORY.NEXT_DAMAGE_NO_KNOCKBACK | Word [SRAM] | |
| 0x23d7 | MEMORY.UNKNOWN_2 | Word [SRAM] | Used in: sterling grab, reactor room (1=?) |
| 0x23d9 | MEMORY.UNKNOWN_ETERNAL_DUST_DROP_PROPERTY | Word [SRAM] | Boss rush |
| 0x23db | MEMORY.Z_AFTER_TELEPORT | Word [SRAM] | |
| 0x23dd | ⚙️ MEMORY.ENEMY_SPAWNER_UNKNOWN_2 | Word [SRAM] | Mostly 0x0000 and 0xffff, once 0x0064 |
| 0x23e9 | ⚙️ MEMORY.CAMERA_BOUNDRY_X_START | Word [SRAM] | |
| 0x23eb | ⚙️ MEMORY.CAMERA_BOUNDRY_Y_START | Word [SRAM] | |
| 0x23ed | ⚙️ MEMORY.CAMERA_BOUNDRY_X_END | Word [SRAM] | |
| 0x23ef | ⚙️ MEMORY.CAMERA_BOUNDRY_Y_END | Word [SRAM] | |
| 0x2401 | ⚙️ MEMORY.CAMERA_X_MIN | Word [SRAM] | |
| 0x2403 | ⚙️ MEMORY.CAMERA_X_MAX | Word [SRAM] | |
| 0x2405 | ⚙️ MEMORY.CAMERA_Y_MIN | Word [SRAM] | |
| 0x2407 | ⚙️ MEMORY.CAMERA_Y_MAX | Word [SRAM] | |
| 0x240d | MEMORY.VENDOR_RECOMMEND_CURRENCY_CHANGE | Word [SRAM] | |
| 0x2413 | — | Word [SRAM] | Camera pan X target; written in FE Cutscenes 2 & 3 [0x51] |
| 0x2415 | — | Word [SRAM] | Camera pan Y target; written in FE Cutscenes 2 & 3 [0x51] |
| 0x241b | ⚙️ MEMORY.FOREGROUND_OFFSET_X | Word [SRAM] | Dark forest only |
| 0x241d | ⚙️ MEMORY.FOREGROUND_OFFSET_Y | Word [SRAM] | Dark forest only |
| 0x242b | ⚙️ MEMORY.CAMERA_PAN_X | Word [SRAM] | |
| 0x242d | ⚙️ MEMORY.CAMERA_PAN_Y | Word [SRAM] | |
| 0x242f | ⚙️ MEMORY.CAMERA_PAN_SPEED | Word [SRAM] | Default 0x80 (core.evs line 690) |
| 0x2433 | ⚙️ MEMORY.ENEMY_SPAWNER_QUANTITY | Word [SRAM] | |
| 0x2437 | ⚙️ MEMORY.MAP_PALETTE | Word [SRAM] | thraxx (0=orange, 7=white); waterfall (7=normal, 0=?); ivor/ebon (7=ebon/ivor, 4=?); greenhouse (6=dark?); storage (7=dark?) |
| 0x2441 | MEMORY.GAIN_WEAPON | Byte [SRAM] | |
| 0x2443 | MEMORY.DOG_WRITE | Byte [SRAM] | Character ID (e.g. 0x02 = wolf) |
| 0x2445 | MEMORY.ALCHEMY_REWARD_PRESELECTION | Word [SRAM] | |
| 0x2455 | MEMORY.VENDOR_ENTITY | Word [SRAM] | |
| 0x2457 | MEMORY.VENDOR_SHOP_ITEMS_SELL | Word [SRAM] | |
| 0x2459 | MEMORY.VENDOR_SHOP_ITEMS_BUY / SHOP_RING_MENU_AND_POSITION_ID | Word [SRAM] | Shared address |
| 0x245b | — | Word [SRAM] | Blimp entity ref; written in [0x51] zone 9 enter |
| 0x2461 | MEMORY.LOOT_AMOUNT | Word [SRAM] | |
| 0x2493 | ? | Word [SESSION] | Cutscene entity X position; written and incremented to steer entity during Raptors intro cutscene [0x5c] |
| 0x2495 | ? | Word [SESSION] | Cutscene entity Y position; written and incremented to steer entity during Raptors intro cutscene [0x5c] |
| 0x2517 | MEMORY.ANNIHILATION_AMULET | Word [SRAM] | |
| 0x2519 | MEMORY.BEAD | Word [SRAM] | |
| 0x251b | MEMORY.CERAMIC_POT | Word [SRAM] | |
| 0x251d | MEMORY.CHICKEN | Word [SRAM] | |
| 0x251f | MEMORY.GOLDEN_JACKAL | Word [SRAM] | |
| 0x2521 | MEMORY.JEWELED_SCARAB | Word [SRAM] | |
| 0x2523 | MEMORY.LIMESTONE_TABLET | Word [SRAM] | |
| 0x2525 | MEMORY.PERFUME | Word [SRAM] | |
| 0x2527 | MEMORY.RICE | Word [SRAM] | |
| 0x2529 | MEMORY.SPICE | Word [SRAM] | |
| 0x252b | MEMORY.SPOON | Word [SRAM] | |
| 0x252d | MEMORY.TAPESTRY | Word [SRAM] | |
| 0x252f | MEMORY.TICKET_FOR_EXHIBITION | Word [SRAM] | |
| 0x2533 | MEMORY.NEXT_ENEMY_FOLLOWS_ENTITY | Word [SRAM] | Consumed after enemy added |
| 0x2537 | MEMORY.STRING_PARAMETER_1 | Word [SRAM] | |
| 0x2539 | MEMORY.STRING_PARAMETER_2 | Word [SRAM] | |
| 0x253b | MEMORY.STRING_PARAMETER_3 | Word [SRAM] | |
| 0x253c…0x2544 | (gap) | Byte×9 [SRAM] | Unmapped |
| 0x2545 | — | Word [SESSION] | Dialog response preselect (save menu yes/no) [0x51] |
| 0x2547…0x2F51 | (gap: ~2570 bytes) | Byte×2570 [SRAM] | Unmapped |
| 0x2F52…0x2F96 | MEMORY.LEVEL_LOW_* | Word×23 | Low-level alchemy spell levels |
| 0x2F98…0x2Fdc | MEMORY.LEVEL_HIGH_* | Word×23 | High-level alchemy spell levels |
| 0x2Fdd…0x2833 | (gap: 1400+ bytes) | Byte×1400 | Unmapped |
| 0x2834…0x28fb | General-purpose RAM | Byte×200 | Examples: entity slots, attack slots, dark forest layout |
| 0x28fc…0x4EB2 | (gap: 6100+ bytes) | Byte×6100 | Unmapped |

