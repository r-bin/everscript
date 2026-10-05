# Secret of Evermore Room Audio & Sound Support Reference

Complete authoritative mapping of all 127 vanilla rooms (`0x00`–`0x7e`), their loaded background music soundtracks, and the sound effects (SFX) supported and triggered in their scripts.

> **Crucial Architecture Rule:** Due to the Sony SPC700 coprocessor's 64 KB Audio RAM budget, Secret of Evermore does not maintain a universal SFX library. Instead, the active background music track (`enum MUSIC`) loads a bespoke soundbank (BRR samples + sequence data) into ARAM. Calling a sound effect (`enum SOUND`) whose BRR samples or definition table do not exist in the active room's soundbank triggers **"the sound glitch"** (severe CPU lag spikes or a complete system freeze). See [`docs/the_sound_glitch.md`](file:///Users/v/Documents/GitHub/everscript/docs/the_sound_glitch.md) for full hardware analysis.

---

## Table of Contents
- [Act 0: Podunk & Intro (1965 / 1995)](#act-0-podunk--intro-1965--1995)
- [Act 1: Prehistoria](#act-1-prehistoria)
- [Act 2: Antiqua](#act-2-antiqua)
- [Act 3: Gothica](#act-3-gothica)
- [Act 4: Omnitopia](#act-4-omnitopia)
- [Global Sound Effects Baseline](#global-sound-effects-baseline)

---

## Act 0: Podunk & Intro (1965 / 1995)

| ID | Room Name | Loaded Music / Soundbank | Supported Sound Effects (SFX) |
|:---|:---|:---|:---|
| `0x02` | Intro - Mansion Exterior 1965 | `0x52` | `0x60`<br>`0x34` `TESLA`<br>`0xaa`<br>`0x64` |
| `0x03` | Intro - Mansion Exterior 1995 | `0x00` | `0x70`<br>`0x24` `DOG_ATTACK`<br>`0x3c` `IMPACT`<br>`0x3e` `GORE_MOSQUITO`<br>`0x42` |
| `0x15` | Brian's Test Ground | *Developer Soundboard*<br>(Triggers test transitions for all music IDs) | *Developer Soundboard*<br>(Triggers test play for all SFX IDs `0x00`–`0xef`) |
| `0x31` | Intro - Podunk 1965 | `0x38` | *Global UI SFX only* |
| `0x32` | Intro - Podunk 1995 | `0x90`<br>`0x4a` `MYSTERY` | `0x34` `TESLA`<br>`0x3c` `IMPACT`<br>`0x42`<br>`0x24` `DOG_ATTACK` |
| `0x61` | Opening - Scrolling over Machine | `0x06` | *Global UI SFX only* |

## Act 1: Prehistoria

| ID | Room Name | Loaded Music / Soundbank | Supported Sound Effects (SFX) |
|:---|:---|:---|:---|
| `0x01` | Prehistoria - Exterior of Blimp's Hut | `0x0c` `SWAMP_AMBIENT`<br>`0x24` `BOSS` | `0x6a` `DRAGON_ROAR` |
| `0x16` | Prehistoria - BBM | `0x14` `BUGMUCK_AMBIENT_MELODY` | `0x58` `THRAXX_BRIDGE_COLLAPSING` |
| `0x17` | Prehistoria - Bug room 2 | `0x14` `BUGMUCK_AMBIENT_MELODY` | *Global UI SFX only* |
| `0x18` | Prehistoria - Thraxx' room | `0x04` `BOSS_DRUMS`<br>`0x78` `FANFARE_ITEM`<br>`0x26` `CAVE_AMBIENT_PIANO` | `0x22` `THRAXX_DAMAGE`<br>`0x10` `AXE_ATTACK` |
| `0x25` | Prehistoria - Fire Eyes' Village | `0x8e`<br>`0x12` `UNKNOWN_PREHISTORIA_AMBIENT`<br>`0x52` | `0x34` `TESLA`<br>`0x64` |
| `0x26` | Prehistoria - West area with Defend | `0x12` `UNKNOWN_PREHISTORIA_AMBIENT` | *Global UI SFX only* |
| `0x27` | Prehistoria - Mammoth Graveyard | `0x2a`<br>`0x5a` `BOSS_MINI` | *Global UI SFX only* |
| `0x33` | Prehistoria - Strong Heart's Exterior | `0x12` `UNKNOWN_PREHISTORIA_AMBIENT` | *Global UI SFX only* |
| `0x34` | Prehistoria - Strong Heart's Hut | `0x26` `CAVE_AMBIENT_PIANO` | *Global UI SFX only* |
| `0x35` | Act1 Quicksand, Bugmuck and Volcano caves + Act2 West Alchemy Cave | `0x5c`<br>`0x26` `CAVE_AMBIENT_PIANO` | `0x3c` `IMPACT` |
| `0x36` | Prehistoria - Both fire pits (one room) | `0x84` `WIND_AMBIENT_PLANE`<br>`0x40` `WIND_AMBIENT_BIRDS_2` | *Global UI SFX only* |
| `0x38` | Prehistoria - South jungle / Start | `0x0a` `JUNGLE_AMBIENT` | `0x24` `DOG_ATTACK`<br>`0x10` `AXE_ATTACK`<br>`0x0c` |
| `0x3b` | Prehistoria - Volcano Room 2 | `0x08` | *Global UI SFX only* |
| `0x3c` | Prehistoria - Volcano Room 1 | `0x5c`<br>`0x08` | *Global UI SFX only* |
| `0x3d` | Prehistoria - Pipe maze | `0x86` | *Global UI SFX only* |
| `0x3e` | Prehistoria - Side rooms of pipe maze | `0x86` | `0x44` `GENERIC_GOOD`<br>`0x3c` `IMPACT` |
| `0x3f` | Prehistoria - Volcano Boss Room | `0x16`<br>`0x52`<br>`0x24` `BOSS` | `0x34` `TESLA`<br>`0x64` |
| `0x41` | Prehistoria - North jungle | `0x7a` `JUNGLE_AMBIENT_BIRDS` | *Global UI SFX only* |
| `0x50` | Prehistoria - Sky above Volcano | `0x26` `CAVE_AMBIENT_PIANO` | *Global UI SFX only* |
| `0x51` | Prehistoria - Village Huts and Blimp's Hut | `0x28`<br>`0x0c` `SWAMP_AMBIENT`<br>`0x12` `UNKNOWN_PREHISTORIA_AMBIENT`<br>`0x78` `FANFARE_ITEM` | `0x44` `GENERIC_GOOD` |
| `0x52` | Prehistoria - Top of Volcano | `0x26` `CAVE_AMBIENT_PIANO` | `0x3c` `IMPACT` |
| `0x59` | Prehistoria - Quick sand desert | `0x6c` `WING_AMBIENT_VOID` | `0x5e` `SANDPIT_SWALLOW` |
| `0x5a` | Prehistoria - Acid rain guy | `0x46` `WATERFALL_AMBIENT` | *Global UI SFX only* |
| `0x5b` | Prehistoria - East jungle | `0x0a` `JUNGLE_AMBIENT` | *Global UI SFX only* |
| `0x5c` | Prehistoria - Raptors | `0x0a` `JUNGLE_AMBIENT`<br>`0x32` `BOSS_JUNGLE`<br>`0x36` `FANFARE` | `0x3c` `IMPACT`<br>`0x44` `GENERIC_GOOD` |
| `0x65` | Prehistoria - Swamp (main area) | `0x0c` `SWAMP_AMBIENT` | `0x72` `WATER_PLOP` |
| `0x66` | Prehistoria - West of swamp | `0x0c` `SWAMP_AMBIENT` | `0x72` `WATER_PLOP` |
| `0x67` | Prehistoria - Bugmuck exterior | `0x14` `BUGMUCK_AMBIENT_MELODY` | *Global UI SFX only* |
| `0x69` | Prehistoria - Volcano path | `0x0a` `JUNGLE_AMBIENT`<br>`0x78` `FANFARE_ITEM` | `0x3c` `IMPACT` |

## Act 2: Antiqua

| ID | Room Name | Loaded Music / Soundbank | Supported Sound Effects (SFX) |
|:---|:---|:---|:---|
| `0x04` | Antiqua - Crustacia fire pit | `0x3a` `WATER_AMBIENT_SEAGULLS` | *Global UI SFX only* |
| `0x05` | Antiqua - Between 'mids and halls | `0x40` `WIND_AMBIENT_BIRDS_2`<br>`0x4a` `MYSTERY`<br>`0x5a` `BOSS_MINI` | `0x3c` `IMPACT`<br>`0x58` `THRAXX_BRIDGE_COLLAPSING` |
| `0x06` | Antiqua - Outside of 'mids | `0x40` `WIND_AMBIENT_BIRDS_2` | `0x38` `CLICK_1`<br>`0x76` `ELEVATOR_DOOR` |
| `0x07` | Antiqua - West of Crustacia | `0x3a` `WATER_AMBIENT_SEAGULLS` | `0x58` `THRAXX_BRIDGE_COLLAPSING` |
| `0x08` | Antiqua - Nobilia, Square | `0x8e`<br>`0x84` `WIND_AMBIENT_PLANE`<br>`0x4a` `MYSTERY`<br>`0x40` `WIND_AMBIENT_BIRDS_2` | `0x24` `DOG_ATTACK`<br>`0x46` `DOOR`<br>`0x42` |
| `0x09` | Antiqua - Nobilia, Square during Aegis fight | `0x02`<br>`0x30` `SPACE_NOISE`<br>`0x24` `BOSS` | `0x34` `TESLA`<br>`0x9e` `UNKNOWN_ALCHEMY_9`<br>`0x64` |
| `0x0a` | Antiqua - Nobilia, Market | `0x40` `WIND_AMBIENT_BIRDS_2`<br>`0x2e` | `0x46` `DOOR`<br>`0x42`<br>`0x48`<br>`0x40` `PURCHASE`<br>`0x4a`<br>`0x44` `GENERIC_GOOD` |
| `0x0b` | Antiqua - Nobilia, Palace grounds | `0x4a` `MYSTERY` | `0x5a` `MAGMA_HARDENING`<br>`0x72` `WATER_PLOP`<br>`0x44` `GENERIC_GOOD` |
| `0x0c` | Antiqua - Nobilia, Inn | `0x42` `INN_GUITAR`<br>`0x50` | `0x40` `PURCHASE` |
| `0x1b` | Antiqua - Desert of Doom | `0x16` | `0x44` `GENERIC_GOOD`<br>`0x5a` `MAGMA_HARDENING` |
| `0x1c` | Antiqua - Nobilia, North of Market | `0x40` `WIND_AMBIENT_BIRDS_2`<br>`0x2e` | `0x48` |
| `0x1d` | Antiqua - Nobilia, Arena (Vigor Fight) | `0x54` `BOSS_ARENA`<br>`0x7e` | `0x6e` `ARENA_CHEER`<br>`0x3c` `IMPACT`<br>`0x3e` `GORE_MOSQUITO` |
| `0x1e` | Antiqua - Nobilia, Arena Holding Room | `0x02` | `0x76` `ELEVATOR_DOOR`<br>`0x44` `GENERIC_GOOD` |
| `0x23` | Antiqua - Halls SW | `0x5e` `HALLS_2` | `0x76` `ELEVATOR_DOOR`<br>`0x2c` `MECHANICAL_MOVEMENT` |
| `0x24` | Antiqua - Halls NW | `0x1e` `HALLS_1` | `0x3c` `IMPACT`<br>`0x5a` `MAGMA_HARDENING`<br>`0x58` `THRAXX_BRIDGE_COLLAPSING`<br>`0x00` `NONE` |
| `0x28` | Antiqua - Halls Collapsing Bridge | `0x66` `HALLS_3` | `0x76` `ELEVATOR_DOOR`<br>`0x2c` `MECHANICAL_MOVEMENT`<br>`0x54` `TEMPLE_BRIDGE_COLLAPSING`<br>`0x00` `NONE` |
| `0x29` | Antiqua - Halls main room | `0x1e` `HALLS_1` | `0x76` `ELEVATOR_DOOR`<br>`0x5a` `MAGMA_HARDENING` |
| `0x2a` | Antiqua - Halls Boss Room | `0x24` `BOSS` | *Global UI SFX only* |
| `0x2b` | Antiqua - Outside of halls | `0x68` `WIND_AMBIENT_BIRDS` | *Global UI SFX only* |
| `0x2c` | Antiqua - Halls SE | `0x5a` `BOSS_MINI`<br>`0x1e` `HALLS_1` | `0x5a` `MAGMA_HARDENING` |
| `0x2d` | Antiqua - Halls NE | `0x66` `HALLS_3` | `0x00` `NONE`<br>`0x2c` `MECHANICAL_MOVEMENT`<br>`0x5a` `MAGMA_HARDENING`<br>`0x76` `ELEVATOR_DOOR` |
| `0x2e` | Antiqua - Blimp's Cave | `0x26` `CAVE_AMBIENT_PIANO` | *Global UI SFX only* |
| `0x2f` | Antiqua - Horace's camp | `0x22` | *Global UI SFX only* |
| `0x30` | Antiqua - Crustacia inside pirate ship | `0x2c`<br>`0x5c` | *Global UI SFX only* |
| `0x3a` | Antiqua - Nobilia, Fire pit | `0x84` `WIND_AMBIENT_PLANE`<br>`0x40` `WIND_AMBIENT_BIRDS_2` | *Global UI SFX only* |
| `0x4b` | Antiqua - Oglin cave | `0x44` | *Global UI SFX only* |
| `0x4c` | Antiqua - Nobilia, Fountain and snake statues | `0x56` | *Global UI SFX only* |
| `0x4d` | Antiqua - Nobilia, Inside palace (Horace cutscene) | `0x4a` `MYSTERY` | `0x76` `ELEVATOR_DOOR` |
| `0x4f` | Antiqua - East of Crustacia | `0x3a` `WATER_AMBIENT_SEAGULLS`<br>`0x52` | `0xa4`<br>`0x64` |
| `0x53` | Antiqua - Act2 Start Cutscene | `0x64` | `0x3c` `IMPACT` |
| `0x55` | Antiqua - 'mids bottom level (Dog start) | `0x20` `PYRAMID` | `0x72` `WATER_PLOP`<br>`0x68` `FLOWER_ATTACK`<br>`0x38` `CLICK_1`<br>`0x76` `ELEVATOR_DOOR`<br>`0x58` `THRAXX_BRIDGE_COLLAPSING` |
| `0x56` | Antiqua - 'mids top level (Boy start) | `0x20` `PYRAMID` | `0x58` `THRAXX_BRIDGE_COLLAPSING` |
| `0x57` | Antiqua - 'mids basement level (Tiny) | `0x20` `PYRAMID`<br>`0x5a` `BOSS_MINI` | `0x36` `TELEPORTER`<br>`0x58` `THRAXX_BRIDGE_COLLAPSING` |
| `0x58` | Antiqua - 'mids boss room (Rimsala) | `0x24` `BOSS` | `0x5a` `MAGMA_HARDENING`<br>`0x76` `ELEVATOR_DOOR` |
| `0x64` | Antiqua - Cave entrance under 'mids | `0x44` | `0x36` `TELEPORTER` |
| `0x68` | Antiqua - Crustacia exterior | `0x3a` `WATER_AMBIENT_SEAGULLS`<br>`0x2c` | *Global UI SFX only* |
| `0x6a` | Antiqua - Act2 Start Cutscene - waterfall | `0x64` | *Global UI SFX only* |
| `0x6b` | Antiqua - Waterfall | `0x46` `WATERFALL_AMBIENT` | `0x3c` `IMPACT`<br>`0x3e` `GORE_MOSQUITO` |
| `0x6d` | Antique - Aquagoth Room | `0x24` `BOSS` | `0x76` `ELEVATOR_DOOR` |

## Act 3: Gothica

| ID | Room Name | Loaded Music / Soundbank | Supported Sound Effects (SFX) |
|:---|:---|:---|:---|
| `0x0d` | Gothica - Ebon Keep Hall (Stairs, behind Verm) | `0x6e` | `0x42`<br>`0x46` `DOOR` |
| `0x0e` | Gothica - Ebon Keep Dining Room | `0x6e` | *Global UI SFX only* |
| `0x0f` | Gothica - Ebon Keep West Room (Naris) | `0x6e` | *Global UI SFX only* |
| `0x10` | Gothica - Ebon Keep Stained Glass Hallway | `0x6e`<br>`0x5a` `BOSS_MINI`<br>`0x36` `FANFARE` | `0x24` `DOG_ATTACK` |
| `0x11` | Gothica - Ebon Keep Queen's Room | `0x8e`<br>`0x18` | `0x44` `GENERIC_GOOD`<br>`0x42` |
| `0x12` | Gothica - Ebon Keep sewers | `0x2a` | *Global UI SFX only* |
| `0x13` | Gothica - Between Ebon Keep sewers, Dark Forest and Swamp | `0x68` `WIND_AMBIENT_BIRDS` | *Global UI SFX only* |
| `0x14` | Gothica - Ebon Keep Tinker's Room | `0x70`<br>`0x78` `FANFARE_ITEM` | *Global UI SFX only* |
| `0x19` | Gothica - Chessboard | `0x60` `ACT3`<br>`0x24` `BOSS` | `0x58` `THRAXX_BRIDGE_COLLAPSING`<br>`0x3c` `IMPACT` |
| `0x1a` | Gothica - Below chessboard | `0x6c` `WING_AMBIENT_VOID` | `0x44` `GENERIC_GOOD` |
| `0x1f` | Gothica - Doubles room in forest | `0x5a` `BOSS_MINI`<br>`0x68` `WIND_AMBIENT_BIRDS` | *Global UI SFX only* |
| `0x20` | Gothica - Timberdrake room in forest | `0x68` `WIND_AMBIENT_BIRDS`<br>`0x24` `BOSS` | *Global UI SFX only* |
| `0x21` | Gothica - Dark forest entrance (save point) | `0x46` `WATERFALL_AMBIENT` | *Global UI SFX only* |
| `0x22` | Gothica - Dark Forest | `0x68` `WIND_AMBIENT_BIRDS` | *Global UI SFX only* |
| `0x37` | Gothica - Gomi's Tower | `0x68` `WIND_AMBIENT_BIRDS`<br>`0x24` `BOSS` | `0x6a` `DRAGON_ROAR` |
| `0x39` | Gothica - Ebon Keep Fire pit | `0x84` `WIND_AMBIENT_PLANE`<br>`0x70`<br>`0x52` | *Global UI SFX only* |
| `0x40` | Gothica - Swamp south of Gomi's Tower | `0x84` `WIND_AMBIENT_PLANE`<br>`0x68` `WIND_AMBIENT_BIRDS` | `0x64` |
| `0x4e` | Gothica - Ivor Tower, west alley (market) | `0x6a` | *Global UI SFX only* |
| `0x5d` | Gothica - Ebon Keep Courtyard (South of Verm) | `0x6a`<br>`0x62` `EBON_KEEP` | *Global UI SFX only* |
| `0x5e` | Gothica - Ebon Keep Front Room (Verm) | `0x66` `HALLS_3`<br>`0x6e`<br>`0x24` `BOSS` | *Global UI SFX only* |
| `0x5f` | Gothica - Ebon Keep Verm side rooms | `0x66` `HALLS_3`<br>`0x6e` | *Global UI SFX only* |
| `0x60` | Gothica - Ebon Keep Storage Room | `0x5c` | *Global UI SFX only* |
| `0x62` | Gothica - Ivor Tower, west square (trailers) | `0x76`<br>`0x7e`<br>`0x80` `PIG_RACE` | `0x32` `GORE_EXPLOSION`<br>`0x42`<br>`0x3c` `IMPACT`<br>`0x46` `DOOR` |
| `0x63` | Gothica - Ivor Tower, inside trailers | `0x76` | `0x42`<br>`0x46` `DOOR` |
| `0x6c` | Gothica - SE of Ivor Tower (Well) | `0x60` `ACT3` | `0x5a` `MAGMA_HARDENING`<br>`0x6c` `SQUEEK`<br>`0x72` `WATER_PLOP` |
| `0x6e` | Gothica - Ivor Tower Hall | `0x74` | `0x46` `DOOR`<br>`0x0c`<br>`0x42`<br>`0x62`<br>`0x24` `DOG_ATTACK` |
| `0x6f` | Gothica - Ivor Tower Dining Room | `0x74` | `0x24` `DOG_ATTACK` |
| `0x70` | Gothica - Ivor Tower Exterior Bridges and Balconies | `0x82` | *Global UI SFX only* |
| `0x71` | Gothica - Ivor Tower East Room + Kitchen | `0x80` `PIG_RACE`<br>`0x82` | `0x24` `DOG_ATTACK`<br>`0x46` `DOOR`<br>`0x42`<br>`0x5a` `MAGMA_HARDENING`<br>`0xb8`<br>`0x5e` `SANDPIT_SWALLOW` |
| `0x72` | Gothica - Ivor Tower East Upper Floor | `0x82` | `0x46` `DOOR`<br>`0x5e` `SANDPIT_SWALLOW` |
| `0x73` | Gothica - Ivor Tower Dog Maze Underground | `0x5c` | `0x5c` `DOG_MAZE_HINT`<br>`0x5a` `MAGMA_HARDENING` |
| `0x74` | Gothica - Ebon Keep and Ivory Tower dungeon + pipe room | `0x72` `SEWER_AMBIENT_WATER` | `0x76` `ELEVATOR_DOOR`<br>`0x46` `DOOR`<br>`0x42`<br>`0x5c` `DOG_MAZE_HINT`<br>`0x0c`<br>`0x66` `MOSQUITO_ATTACK` |
| `0x75` | Gothica - Ivor Tower Stariwell to dungeon | `0x5c` | *Global UI SFX only* |
| `0x76` | Gothica - South of Ivor Tower (Gate) | `0x60` `ACT3` | `0x44` `GENERIC_GOOD` |
| `0x77` | Gothica - Ivor Tower Puppet Show / Mungola | `0x5a` `BOSS_MINI`<br>`0x58` `PUPPET_SHOW`<br>`0x52`<br>`0x36` `FANFARE`<br>`0x84` `WIND_AMBIENT_PLANE` | `0x2e` `HEAL_START`<br>`0x64`<br>`0x32` `GORE_EXPLOSION`<br>`0x44` `GENERIC_GOOD` |
| `0x78` | Gothica - Ivor Tower Queen's Room | `0x18` | *Global UI SFX only* |
| `0x79` | Gothica - Ivor Tower Sewers | `0x56` | `0x46` `DOOR` |
| `0x7a` | Gothica - Ivor Tower Sewers Exterior (landing spot) | `0x56` | *Global UI SFX only* |
| `0x7b` | Gothica - Ebon Keep and Ivor Tower Exterior Bottom Half | `0x6a`<br>`0x62` `EBON_KEEP` | `0x42`<br>`0x46` `DOOR`<br>`0x40` `PURCHASE` |
| `0x7c` | Gothica - Ebon Keep and Ivor Tower Exterior Top Half | `0x6a`<br>`0x62` `EBON_KEEP` | `0x42`<br>`0x76` `ELEVATOR_DOOR`<br>`0x46` `DOOR` |
| `0x7d` | Gothica - Ebon Keep and Ivor Tower Interior | `0x6a`<br>`0x62` `EBON_KEEP`<br>`0x50` | `0x42`<br>`0x46` `DOOR`<br>`0x44` `GENERIC_GOOD`<br>`0x40` `PURCHASE` |

## Act 4: Omnitopia

| ID | Room Name | Loaded Music / Soundbank | Supported Sound Effects (SFX) |
|:---|:---|:---|:---|
| `0x00` | Omnitopia - Alarm room | `0x5c`<br>`0x8c` `ALARM`<br>`0x78` `FANFARE_ITEM` | `0xaa`<br>`0xb2` `FAN_ACTIVATED` |
| `0x42` | Omnitopia - Reactor room and Reactor control | `0x1c`<br>`0x78` `FANFARE_ITEM` | `0x44` `GENERIC_GOOD` |
| `0x43` | Omnitopia - Control room | `0x3c` | `0xb0` `ACT4_DOOR_OPENING` |
| `0x44` | Omnitopia - Greenhouse (dark or both?) | `0x0a` `JUNGLE_AMBIENT`<br>`0x7c`<br>`0x78` `FANFARE_ITEM` | *Global UI SFX only* |
| `0x45` | Omnitopia - Secret boss room | `0x88`<br>`0x24` `BOSS` | *Global UI SFX only* |
| `0x46` | Omnitopia - Professor's lab and ship area, (also?) Intro | `0x30` `SPACE_NOISE`<br>`0x8e`<br>`0x3c`<br>`0x5c`<br>`0x00`<br>`0x52`<br>`0x38`<br>`0x78` `FANFARE_ITEM` | `0xc2`<br>`0xb0` `ACT4_DOOR_OPENING`<br>`0x34` `TESLA`<br>`0xaa`<br>`0x64`<br>`0xb2` `FAN_ACTIVATED`<br>`0x60`<br>`0x3c` `IMPACT`<br>`0x70`<br>`0x44` `GENERIC_GOOD`<br>`0x9c` `ACT4_SWITCH`<br>`0xa4` |
| `0x47` | Omnitopia - Storage room | `0x88`<br>`0x7c`<br>`0x78` `FANFARE_ITEM` | *Global UI SFX only* |
| `0x48` | Omnitopia - Metroplex tunnels (rimsalas, spheres) | `0x3e` `SPACE` | `0xb0` `ACT4_DOOR_OPENING` |
| `0x49` | Omnitopia - Junkyard (Landing spot) | `0x6c` `WING_AMBIENT_VOID` | `0x78` |
| `0x4a` | Omnitopia - Final Boss Room | `0x3c`<br>`0x00`<br>`0x24` `BOSS` | `0x34` `TESLA`<br>`0x8a` `LEVITATE`<br>`0xb2` `FAN_ACTIVATED` |
| `0x54` | Omnitopia - Shops | `0x88`<br>`0x50` | `0xb0` `ACT4_DOOR_OPENING`<br>`0x40` `PURCHASE` |
| `0x7e` | Omnitopia - Jail | `0x88` | `0xb0` `ACT4_DOOR_OPENING`<br>`0xaa` |

---

## Global Sound Effects Baseline

A minimal set of universal interface and interaction sound effects are resident in ARAM across virtually all standard soundbanks without triggering memory desync:
- `0x02` `MENU_WHEEL_TURN` (Ring menu turn)
- `0x04` `MENU_WHEEL_OPEN` (Ring menu open)
- `0x06` `MENU_WHEEL_CLOSE` (Ring menu close)
- `0x38` `CLICK_1` (Menu selection cursor)
- `0x3a` `CLICK_2` (Sub-menu confirmation)
- `0x44` `CLICK_3` / `GENERIC_GOOD` (Item pickup / reward chime)

> [!WARNING]
> Even seemingly universal sounds can fail if triggered in incompatible contexts. For example, `PURCHASE = 0x40` causes a hard crash when played during `MYSTERY` (`0x4a`) music or `SEWER_AMBIENT_WATER` (`0x72`). Always wrap unverified sound triggers with [`smart_sound()`](file:///Users/v/Documents/GitHub/everscript/in/core/%5Bgroup%5D%2002_functions/%5Bgroup%5D%2002_everscript_commands/01_audio.evs#L31) or verify the room's active music enum before calling `sound()`.
