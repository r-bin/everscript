# Secret of Evermore: Music & Sound Compatibility Reference

Authoritative hardware and ROM-level mapping of which sound effects are allowed and supported under each background music track in Secret of Evermore.

> **Source:** Reverse-engineered directly from the SNES ROM dispatch routines at `$8C:D6BE` (SFX opcode dispatcher), `$8C:8362` (SFX translation table), `$81:9A1E` (Table 2: Song requirement table), and `$8C:8442` (Music opcode conversion table).
> 
> See [`docs/the_sound_glitch.md`](file:///Users/v/Documents/GitHub/everscript/docs/the_sound_glitch.md) for full architectural explanation of the APU desynchronization and CPU spinlocks.

---

## 1. Engine Audio Dispatch Architecture

The Secret of Evermore engine resolves sound effects and music through a strict three-tier hardware validation system:

1. **SFX Opcode Dispatch Table (`$8C:8362`):**
   When `sound(sfx_id)` (opcode `0x30`) is executed, the raw word argument indexes `$8C:8362,X`:
   - If the value is `0xFFFF`, the sound is **hard-muted/invalid** by the engine and immediately ignored.
   - If valid, it returns an **internal sound index** (`0..89`).

2. **Song Dependency Table (`$81:9A1E` / Table 2):**
   The internal sound index looks up the required song in Table 2:
   - **`0x00` (Global Base Bank):** The sound samples are part of the master soundbank loaded with Song 0. These **82 sounds are permanently resident** and allowed under **EVERY** music track.
   - **Non-zero (`0x01`–`0x46`):** The sound requires a **specific music track's soundbank** to be loaded into SPC700 Audio RAM.

3. **Active Song Verification (`$8C:8236`):**
   Before emitting the audio command to the SPC700 via `$2140`–`$2143`, the engine compares the required song with `$0E4B` (the active song):
   ```assembly
   LDA [$A0]       ; Load required song index from Table 2
   BEQ allowed     ; Song 0 = Always resident, allowed!
   CMP $0E4B       ; Compare with currently playing song
   BEQ allowed     ; Matches current song soundbank, allowed!
   ; MISMATCH: Sound samples missing from SPC700 ARAM -> "The Sound Glitch"
   ```

---

## 2. Master Table: Music Track $\to$ Allowed Sounds

Every music track supports all **82 Global Base Sounds** (listed in [§3](#3-the-82-universal-global-sounds)).
The table below catalogs every music opcode and whether it unlocks additional context-specific sound effects.

| Opcode `0x33` ID | `enum MUSIC` Constant | Song Index | Soundbank Type | Exclusive SFX Allowed |
|:---|:---|:---|:---|:---|
| `0x02` | `MUSIC_0x02` | `0x02` | **Special Context Bank** | `0x22` `THRAXX_DAMAGE` |
| `0x04` | `BOSS_DRUMS` | `0x01` | Standard Bank | *Standard Global SFX only* |
| `0x06` | `MUSIC_0x06` | `0x00` | Standard Bank | *Standard Global SFX only* |
| `0x08` | `MUSIC_0x08` | `0x06` | Standard Bank | *Standard Global SFX only* |
| `0x0a` | `JUNGLE_AMBIENT` | `0x08` | **Special Context Bank** | `0x1e` `SFX_0x1e` |
| `0x0c` | `SWAMP_AMBIENT` | `0x07` | Standard Bank | *Standard Global SFX only* |
| `0x0e` | `MUSIC_0x0e` | `0x15` | Standard Bank | *Standard Global SFX only* |
| `0x12` | `UNKNOWN_PREHISTORIA_AMBIENT` | `0x05` | Standard Bank | *Standard Global SFX only* |
| `0x14` | `BUGMUCK_AMBIENT_MELODY` | `0x09` | Standard Bank | *Standard Global SFX only* |
| `0x16` | `MUSIC_0x16` | `0x0a` | Standard Bank | *Standard Global SFX only* |
| `0x18` | `MUSIC_0x18` | `0x0b` | Standard Bank | *Standard Global SFX only* |
| `0x1a` | `MUSIC_0x1a` | `0x0c` | Standard Bank | *Standard Global SFX only* |
| `0x1c` | `MUSIC_0x1c` | `0x0d` | Standard Bank | *Standard Global SFX only* |
| `0x1e` | `HALLS_1` | `0x0e` | Standard Bank | *Standard Global SFX only* |
| `0x20` | `PYRAMID` | `0x21` | Standard Bank | *Standard Global SFX only* |
| `0x22` | `MUSIC_0x22` | `0x0f` | Standard Bank | *Standard Global SFX only* |
| `0x24` | `BOSS` | `0x10` | Standard Bank | *Standard Global SFX only* |
| `0x26` | `CAVE_AMBIENT_PIANO` | `0x11` | **Special Context Bank** | `0x6a` `DRAGON_ROAR` |
| `0x28` | `MUSIC_0x28` | `0x2a` | Standard Bank | *Standard Global SFX only* |
| `0x2a` | `MUSIC_0x2a` | `0x12` | Standard Bank | *Standard Global SFX only* |
| `0x2c` | `MUSIC_0x2c` | `0x13` | Standard Bank | *Standard Global SFX only* |
| `0x2e` | `MUSIC_0x2e` | `0x14` | Standard Bank | *Standard Global SFX only* |
| `0x30` | `SPACE_NOISE` | `0x16` | Standard Bank | *Standard Global SFX only* |
| `0x32` | `BOSS_JUNGLE` | `0x18` | Standard Bank | *Standard Global SFX only* |
| `0x34` | `MUSIC_0x34` | `0x17` | Standard Bank | *Standard Global SFX only* |
| `0x36` | `FANFARE` | `0x19` | Standard Bank | *Standard Global SFX only* |
| `0x38` | `MUSIC_0x38` | `0x1c` | Standard Bank | *Standard Global SFX only* |
| `0x3a` | `WATER_AMBIENT_SEAGULLS` | `0x1b` | Standard Bank | *Standard Global SFX only* |
| `0x3c` | `MUSIC_0x3c` | `0x1d` | Standard Bank | *Standard Global SFX only* |
| `0x3e` | `SPACE` | `0x1f` | **Special Context Bank** | `0x48` `SFX_0x48`<br>`0x4a` `SFX_0x4a` |
| `0x40` | `WIND_AMBIENT_BIRDS_2` | `0x1e` | Standard Bank | *Standard Global SFX only* |
| `0x42` | `INN_GUITAR` | `0x20` | Standard Bank | *Standard Global SFX only* |
| `0x44` | `MUSIC_0x44` | `0x22` | **Special Context Bank** | `0x58` `THRAXX_BRIDGE_COLLAPSING` |
| `0x46` | `WATERFALL_AMBIENT` | `0x23` | **Special Context Bank** | `0xa6` `SFX_0xa6` |
| `0x48` | `MUSIC_0x48` | `0x24` | Standard Bank | *Standard Global SFX only* |
| `0x4a` | `MYSTERY` | `0x25` | Standard Bank | *Standard Global SFX only* |
| `0x4e` | `MUSIC_0x4e` | `0x26` | Standard Bank | *Standard Global SFX only* |
| `0x50` | `MUSIC_0x50` | `0x1a` | Standard Bank | *Standard Global SFX only* |
| `0x52` | `MUSIC_0x52` | `0x27` | Standard Bank | *Standard Global SFX only* |
| `0x54` | `BOSS_ARENA` | `0x28` | **Special Context Bank** | `0x60` `SFX_0x60` |
| `0x56` | `MUSIC_0x56` | `0x29` | **Special Context Bank** | `0x7a` `VIGOR_ROLLING` |
| `0x58` | `PUPPET_SHOW` | `0x2b` | **Special Context Bank** | `0xca` `SFX_0xca`<br>`0xcc` `SFX_0xcc` |
| `0x5a` | `BOSS_MINI` | `0x2c` | Standard Bank | *Standard Global SFX only* |
| `0x5c` | `MUSIC_0x5c` | `0x2d` | Standard Bank | *Standard Global SFX only* |
| `0x5e` | `HALLS_2` | `0x2e` | **Special Context Bank** | `0xc2` `SFX_0xc2` |
| `0x60` | `ACT3` | `0x2f` | Standard Bank | *Standard Global SFX only* |
| `0x62` | `EBON_KEEP` | `0x30` | **Special Context Bank** | `0x72` `WATER_PLOP` |
| `0x64` | `MUSIC_0x64` | `0x31` | Standard Bank | *Standard Global SFX only* |
| `0x66` | `HALLS_3` | `0x32` | **Special Context Bank** | `0xb6` `SFX_0xb6` |
| `0x68` | `WIND_AMBIENT_BIRDS` | `0x33` | Standard Bank | *Standard Global SFX only* |
| `0x6a` | `MUSIC_0x6a` | `0x34` | Standard Bank | *Standard Global SFX only* |
| `0x6c` | `WING_AMBIENT_VOID` | `0x36` | Standard Bank | *Standard Global SFX only* |
| `0x6e` | `MUSIC_0x6e` | `0x38` | Standard Bank | *Standard Global SFX only* |
| `0x70` | `MUSIC_0x70` | `0x37` | Standard Bank | *Standard Global SFX only* |
| `0x72` | `SEWER_AMBIENT_WATER` | `0x39` | Standard Bank | *Standard Global SFX only* |
| `0x74` | `MUSIC_0x74` | `0x3a` | **Special Context Bank** | `0x76` `ELEVATOR_DOOR` |
| `0x76` | `MUSIC_0x76` | `0x3b` | Standard Bank | *Standard Global SFX only* |
| `0x78` | `FANFARE_ITEM` | `0x3c` | **Special Context Bank** | `0x70` `SFX_0x70` |
| `0x7a` | `JUNGLE_AMBIENT_BIRDS` | `0x3d` | Standard Bank | *Standard Global SFX only* |
| `0x7c` | `MUSIC_0x7c` | `0x3f` | **Special Context Bank** | `0x40` `PURCHASE`<br>`0xb8` `SFX_0xb8` |
| `0x7e` | `MUSIC_0x7e` | `0x40` | Standard Bank | *Standard Global SFX only* |
| `0x80` | `PIG_RACE` | `0x41` | **Special Context Bank** | `0x6c` `SQUEEK` |
| `0x82` | `MUSIC_0x82` | `0x3e` | Standard Bank | *Standard Global SFX only* |
| `0x84` | `WIND_AMBIENT_PLANE` | `0x42` | **Special Context Bank** | `0x5e` `SANDPIT_SWALLOW`<br>`0x6e` `ARENA_CHEER` |
| `0x86` | `MUSIC_0x86` | `0x43` | **Special Context Bank** | `0x42` `SFX_0x42`<br>`0x46` `DOOR`<br>`0x64` `SFX_0x64` |
| `0x88` | `MUSIC_0x88` | `0x35` | Standard Bank | *Standard Global SFX only* |
| `0x8a` | `BOSS_BOSSRUSH` | `0x44` | **Special Context Bank** | `0x12` `SFX_0x12`<br>`0x14` `SFX_0x14` |
| `0x8c` | `ALARM` | `0x45` | Standard Bank | *Standard Global SFX only* |
| `0x8e` | `MUSIC_0x8e` | `0x03` | Standard Bank | *Standard Global SFX only* |
| `0x90` | `MUSIC_0x90` | `0x04` | Standard Bank | *Standard Global SFX only* |

---

## 3. The 82 Universal Global Sounds

These sound effects map to `Required Song = 0x00` in Table 2 (`$81:9A1E`). They are permanently resident in SPC700 ARAM and **never cause a sound glitch under any music track**:

| SFX Hex | `enum SOUND` / Description | Internal Index | Category |
|:---|:---|:---|:---|
| `0x00` | `NONE` | `0x03` | Generic / Ambient |
| `0x02` | `MENU_WHEEL_TURN` | `0x03` | UI / Interface |
| `0x04` | `MENU_WHEEL_OPEN` | `0x01` | UI / Interface |
| `0x06` | `MENU_WHEEL_CLOSE` | `0x02` | UI / Interface |
| `0x08` | `GORE_FLOWER` | `0x00` | Generic / Ambient |
| `0x0a` | `HEAVY_IMPACT` | `0x0f` | Generic / Ambient |
| `0x0c` | `SFX_0x0c` | `0x04` | Generic / Ambient |
| `0x10` | `AXE_ATTACK` | `0x16` | Combat / Weapons |
| `0x1a` | `SPIDER_ATTACK` | `0x05` | Combat / Weapons |
| `0x1c` | `FLOWER_VORE` | `0x06` | Generic / Ambient |
| `0x20` | `AXE_ATTACK` | `0x07` | Combat / Weapons |
| `0x24` | `DOG_ATTACK` | `0x10` | Combat / Weapons |
| `0x2a` | `SWORD_ATTACK` | `0x07` | Combat / Weapons |
| `0x2c` | `MECHANICAL_MOVEMENT` | `0x09` | Generic / Ambient |
| `0x2e` | `HEAL_START` | `0x0b` | Alchemy / Spells |
| `0x30` | `HEAL_END` | `0x0c` | Alchemy / Spells |
| `0x32` | `GORE_EXPLOSION` | `0x0d` | Generic / Ambient |
| `0x34` | `TESLA` | `0x0a` | Generic / Ambient |
| `0x36` | `TELEPORTER` | `0x0e` | Generic / Ambient |
| `0x38` | `CLICK_1` | `0x03` | UI / Interface |
| `0x3a` | `CLICK_2` | `0x03` | UI / Interface |
| `0x3c` | `IMPACT` | `0x0f` | Generic / Ambient |
| `0x3e` | `GORE_MOSQUITO` | `0x11` | Generic / Ambient |
| `0x44` | `GENERIC_GOOD` | `0x12` | Generic / Ambient |
| `0x4c` | `UNKNOWN_ALCHEMY` | `0x13` | Alchemy / Spells |
| `0x4e` | `BIRD` | `0x14` | Generic / Ambient |
| `0x50` | `WEIRD_SOUND` | `0x15` | Generic / Ambient |
| `0x52` | `GENERIC_BAD` | `0x17` | Generic / Ambient |
| `0x54` | `TEMPLE_BRIDGE_COLLAPSING` | `0x16` | Mechanisms / Triggers |
| `0x56` | `MENU_WHEEL_OPEN_2` | `0x01` | UI / Interface |
| `0x5a` | `MAGMA_HARDENING` | `0x2b` | Mechanisms / Triggers |
| `0x5c` | `DOG_MAZE_HINT` | `0x28` | Combat / Weapons |
| `0x66` | `MOSQUITO_ATTACK` | `0x29` | Combat / Weapons |
| `0x68` | `FLOWER_ATTACK` | `0x2a` | Combat / Weapons |
| `0x74` | `NITRO_START` | `0x2c` | Alchemy / Spells |
| `0x7c` | `SFX_0x7c` | `0x19` | Generic / Ambient |
| `0x7e` | `UNKNOWN_ALCHEMY_2` | `0x1a` | Alchemy / Spells |
| `0x80` | `SFX_0x80` | `0x1b` | Generic / Ambient |
| `0x82` | `SFX_0x82` | `0x1c` | Generic / Ambient |
| `0x84` | `SFX_0x84` | `0x1d` | Generic / Ambient |
| `0x86` | `HOVER_SOUNDS` | `0x1e` | Generic / Ambient |
| `0x88` | `UNKNOWN_ALCHEMY_3` | `0x1f` | Alchemy / Spells |
| `0x8a` | `LEVITATE` | `0x20` | Alchemy / Spells |
| `0x8c` | `UNKNOWN_ALCHEMY_4` | `0x21` | Alchemy / Spells |
| `0x8e` | `PROJECTILE_SHOOTING` | `0x22` | Alchemy / Spells |
| `0x90` | `UNKNOWN_ALCHEMY_5` | `0x23` | Alchemy / Spells |
| `0x92` | `UNKNOWN_ALCHEMY_6` | `0x24` | Alchemy / Spells |
| `0x94` | `SFX_0x94` | `0x25` | Generic / Ambient |
| `0x96` | `UNKNOWN_ALCHEMY_7` | `0x26` | Alchemy / Spells |
| `0x98` | `UNKNOWN_ALCHEMY_8` | `0x27` | Alchemy / Spells |
| `0x9a` | `SFX_0x9a` | `0x2d` | Generic / Ambient |
| `0x9c` | `ACT4_SWITCH` | `0x2e` | Mechanisms / Triggers |
| `0x9e` | `UNKNOWN_ALCHEMY_9` | `0x2f` | Alchemy / Spells |
| `0xa0` | `SFX_0xa0` | `0x30` | Generic / Ambient |
| `0xa2` | `SFX_0xa2` | `0x31` | Generic / Ambient |
| `0xa4` | `SFX_0xa4` | `0x32` | Generic / Ambient |
| `0xa8` | `SFX_0xa8` | `0x33` | Generic / Ambient |
| `0xaa` | `SFX_0xaa` | `0x34` | Generic / Ambient |
| `0xac` | `SFX_0xac` | `0x35` | Generic / Ambient |
| `0xae` | `SFX_0xae` | `0x36` | Generic / Ambient |
| `0xb0` | `ACT4_DOOR_OPENING` | `0x37` | Mechanisms / Triggers |
| `0xb2` | `FAN_ACTIVATED` | `0x38` | Mechanisms / Triggers |
| `0xb4` | `SFX_0xb4` | `0x39` | Generic / Ambient |
| `0xba` | `SFX_0xba` | `0x3a` | Generic / Ambient |
| `0xbc` | `SFX_0xbc` | `0x3b` | Generic / Ambient |
| `0xbe` | `SFX_0xbe` | `0x3c` | Generic / Ambient |
| `0xc0` | `SFX_0xc0` | `0x3d` | Generic / Ambient |
| `0xc4` | `SFX_0xc4` | `0x08` | Generic / Ambient |
| `0xc6` | `CLICKING` | `0x18` | UI / Interface |
| `0xc8` | `SFX_0xc8` | `0x03` | Generic / Ambient |
| `0xd0` | `SFX_0xd0` | `0x12` | Generic / Ambient |
| `0xd8` | `SFX_0xd8` | `0x00` | Generic / Ambient |
| `0xda` | `SFX_0xda` | `0x01` | Generic / Ambient |
| `0xdc` | `SFX_0xdc` | `0x02` | Generic / Ambient |
| `0xde` | `SFX_0xde` | `0x03` | Generic / Ambient |
| `0xe2` | `SFX_0xe2` | `0x02` | Generic / Ambient |
| `0xe4` | `SFX_0xe4` | `0x01` | Generic / Ambient |
| `0xe6` | `SFX_0xe6` | `0x00` | Generic / Ambient |
| `0xe8` | `SFX_0xe8` | `0x06` | Generic / Ambient |
| `0xea` | `SFX_0xea` | `0x08` | Generic / Ambient |
| `0xec` | `SFX_0xec` | `0x07` | Generic / Ambient |
| `0xee` | `SFX_0xee` | `0x15` | Generic / Ambient |

---

## 4. The 28 Music-Exclusive Sound Effects

These sound effects require a **specific soundbank** in SPC700 Audio RAM. Calling any of these sounds while a different music track is playing causes **"the sound glitch"** (severe lag spikes or crash).

| SFX Hex | `enum SOUND` Constant | Required Song Index | Required Music Track(s) | Observed Glitch / Crash Behavior |
|:---|:---|:---|:---|:---|
| `0x22` | `THRAXX_DAMAGE` | `0x02` | `0x02` `UNKNOWN` | Thraxx damage screech; causes glitch if called in `BOSS_BOSSRUSH` (`0x8a`). |
| `0x1e` | `SFX_0x1e` | `0x08` | `0x0a` `JUNGLE_AMBIENT` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x6a` | `DRAGON_ROAR` | `0x11` | `0x26` `CAVE_AMBIENT_PIANO` | Dragon roar; silent or audio buzz if called outside Boss music. |
| `0x48` | `SFX_0x48` | `0x1f` | `0x3e` `SPACE` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x4a` | `SFX_0x4a` | `0x1f` | `0x3e` `SPACE` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x58` | `THRAXX_BRIDGE_COLLAPSING` | `0x22` | `0x44` `UNKNOWN` | Thraxx bridge collapse rumble. |
| `0xa6` | `SFX_0xa6` | `0x23` | `0x46` `WATERFALL_AMBIENT` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x60` | `SFX_0x60` | `0x28` | `0x54` `BOSS_ARENA` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x7a` | `VIGOR_ROLLING` | `0x29` | `0x56` `UNKNOWN` | Vigor rolling attack rumble. |
| `0xca` | `SFX_0xca` | `0x2b` | `0x58` `PUPPET_SHOW` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0xcc` | `SFX_0xcc` | `0x2b` | `0x58` `PUPPET_SHOW` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0xc2` | `SFX_0xc2` | `0x2e` | `0x5e` `HALLS_2` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x72` | `WATER_PLOP` | `0x30` | `0x62` `EBON_KEEP` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0xb6` | `SFX_0xb6` | `0x32` | `0x66` `HALLS_3` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x76` | `ELEVATOR_DOOR` | `0x3a` | `0x74` `UNKNOWN` | Elevator door open/close sound. |
| `0x70` | `SFX_0x70` | `0x3c` | `0x78` `FANFARE_ITEM` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x40` | `PURCHASE` | `0x3f` | `0x7c` `UNKNOWN` | Crashes game if called in `MYSTERY` (`0x4a`) or `SEWER_AMBIENT_WATER` (`0x72`). |
| `0xb8` | `SFX_0xb8` | `0x3f` | `0x7c` `UNKNOWN` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x6c` | `SQUEEK` | `0x41` | `0x80` `PIG_RACE` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x5e` | `SANDPIT_SWALLOW` | `0x42` | `0x84` `WIND_AMBIENT_PLANE` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x6e` | `ARENA_CHEER` | `0x42` | `0x84` `WIND_AMBIENT_PLANE` | Arena crowd cheer; loops via engine register `<0x2834, 0x04>`. |
| `0x42` | `SFX_0x42` | `0x43` | `0x86` `UNKNOWN` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x46` | `DOOR` | `0x43` | `0x86` `UNKNOWN` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x64` | `SFX_0x64` | `0x43` | `0x86` `UNKNOWN` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x12` | `SFX_0x12` | `0x44` | `0x8a` `BOSS_BOSSRUSH` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x14` | `SFX_0x14` | `0x44` | `0x8a` `BOSS_BOSSRUSH` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |
| `0x78` | `SFX_0x78` | `0x46` | Internal Song `0x46` | Soundbank sample mismatch; causes DSP stall or CPU spinlock. |

---

## 5. Invalid / Hard-Muted Sound Effects (`0xFFFF`)

These sound IDs map to `0xFFFF` in `$8C:8362`. When passed to opcode `0x30`, the engine branch condition `BMI` bypasses APU dispatch entirely, producing silence:

| SFX Hex | Status in Engine Table (`$8C:8362`) | Result |
|:---|:---|:---|
| `0x0e` (`SFX_0x0e`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0x16` (`SFX_0x16`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0x18` (`SFX_0x18`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0x26` (`SFX_0x26`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0x28` (`SFX_0x28`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0x62` (`SFX_0x62`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0xce` (`SFX_0xce`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0xd2` (`SFX_0xd2`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0xd4` (`SFX_0xd4`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0xd6` (`SFX_0xd6`) | `0xFFFF` | Hard-muted (ignored by engine) |
| `0xe0` (`SFX_0xe0`) | `0xFFFF` | Hard-muted (ignored by engine) |
