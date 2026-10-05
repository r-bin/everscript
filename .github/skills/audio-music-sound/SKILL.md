---
name: audio-music-sound
description: Explains the Secret of Evermore audio subsystem, Sculptured Software Wolfgang v3 sound driver, Berlioz toolchain, music & sound tables, unused songs/sounds, cross-game compatibility, dumping playable SPC files, and avoiding "The Sound Glitch".
---

# Secret of Evermore Audio Subsystem, Music & Sound Reference

Authoritative technical guide to the sound architecture, music sequencing, sound effect dispatching, and hardware mechanics of *Secret of Evermore* (SNES).

---

## 1. Engine Architecture & Toolchain Lineage

Unlike almost all other Square SNES titles that utilized Minoru Akao's proprietary Japanese sound driver (Akao Sound Driver / AKSI, found in *Secret of Mana*, *Final Fantasy IV–VI*, *Chrono Trigger*), *Secret of Evermore* was developed by Square USA in Redmond, Washington.

Square licensed the audio technology from **Sculptured Software** (Salt Lake City, Utah):
* **Sound Driver:** **Wolfgang Sound Driver (Version 3)**, programmed by **Steve Aguirre**.
* **Creation Environment:** Sculptured Software's **Berlioz** audio production package:
  * **`BMus`**: Sequence score editor compiling MIDI / tracker events into Wolfgang bytecode.
  * **`BWave`**: Sample utility converting audio into S-DSP Bit Rate Reduction (BRR) blocks.
* **Soundtrack Composer:** **Jeremy Soule** (with contributions from Julian Soule).

---

## 2. Audio Data Format & Cross-Game Compatibility

### Compatibility with Other Games
1. **Nintendo Standard (N-SPC) & Square (Akao):**
   * **Direct binary sequence drop-in is IMPOSSIBLE.** Wolfgang v3 uses an entirely proprietary bytecode instruction set, channel routing structure, and envelope engine. Passing N-SPC or Akao song streams to the SPC700 will crash the sound driver.
2. **Kinship with Other Wolfgang v3 Games:**
   * Secret of Evermore shares its sound driver version with other Sculptured Software SNES releases, including *Mortal Kombat II*, *Doom* (SNES), *WWF WrestleMania: The Arcade Game*, *The Jungle Book*, and *Pitfall: The Mayan Adventure*.
3. **Playing Custom / Other Games' Music:**
   * Music from other games or MIDI sources must be converted into **Wolfgang v3 sequence bytecode** (using community reverse-engineered tools based on `SNESSculpt` and the 2023 Berlioz documentation).
   * All audio samples must be encoded in Sony 4-bit ADPCM **Bit Rate Reduction (BRR)** format.
   * Total audio footprint (driver code + sequence data + BRR samples) must fit strictly within the SPC700's **64 KB ARAM** limit.

---

## 3. Dumping & Playing Music (`tools/dump_spc.py`)

All 71 songs (`0x00`–`0x46`) in the ROM can be dumped into standard, playable `.spc` files using `tools/dump_spc.py`:

```bash
# Dump all 71 songs to music_spc/
python3 tools/dump_spc.py
```

### Playing Dumped `.spc` Files
The resulting `.spc` files in `music_spc/` are standard `SNES-SPC700 Sound File Data v0.30` files:
* **In Snes9x:** `open -a Snes9x music_spc/01_Boss_Drums_Thraxx.spc`
* **In Mesen:** `open -a Mesen music_spc/10_Standard_Boss_Theme.spc`
* Or drag-and-drop into any SPC player (VLC, IINA, Foobar2000 with foo_gep).

---

## 4. WRAM & Hardware MMIO Registers

The SNES 65c816 CPU interfaces with the audio subsystem via WRAM variables and APU communication ports:

| Address | Emoji & Symbol | Size | Purpose & Behavior |
|---|---|---|---|
| `$0E47` | 🎵 `APU_TRANSFER_BLOCK_COUNT` | Word | Number of bytes/blocks in active SPC700 transfer package (`$8C:805B`). |
| `$0E49` | 🎵 `APU_TRANSFER_PTR` | Word | Pointer tracking current transfer block in ROM (`$8C:805B`). |
| `$0E4B` | 🎵 `ACTIVE_SONG` | Byte | Currently playing song index (`0x00`–`0x46`); checked by SFX dispatcher at `$8C:8236`. |
| `$0E4D` | 🎵 `REQUESTED_SONG` | Byte | Pending song index queued by script opcode `0x33` (`$8C:828F`). |
| `$0E4F` | 🎵 `AUDIO_FADE_PARAM` | Word | Volume fade parameter during music transitions. |
| `$0E51` | 🎵 `APU_COMMAND_LOCK` | Word | Audio subsystem busy lock & spinlock handshake counter (`$8C:81FD`). |
| `$0E65` | 🎵 `APU_INTERRUPT_FLAG` | Word | Audio interrupt communication flag; cleared during APU transfers. |
| `$2140` | 🎵 `APU_IO_0` | Byte | APU Communication Port 0 (Handshake ready `$BBAA`, command trigger). |
| `$2141` | 🎵 `APU_IO_1` | Byte | APU Communication Port 1 (Command parameter / transfer acknowledge). |
| `$2142` | 🎵 `APU_IO_2` | Byte | APU Communication Port 2 (Execution start address, default `$0700`). |
| `$2143` | 🎵 `APU_IO_3` | Byte | APU Communication Port 3 (Command parameter / volume / balance). |

---

## 5. ROM Tables & Dispatch Mechanism

The engine validates audio through four sequential tables:

```text
Opcode 0x30 sound(SFX_ID) ───► $8C:8362 (Table 1: 120 words) ───► Internal Sound Index (0..89)
                                                                        │
                                                                        ▼
                                                             $81:9A1E (Table 2: 90 bytes)
                                                                        │
                                                      ┌─────────────────┴─────────────────┐
                                                      ▼                                   ▼
                                              Req Song = 0x00                     Req Song != 0x00
                                           (82 Universal Sounds)                (28 Exclusive Sounds)
                                                      │                                   │
                                                      │                         Compare with $0E4B
                                                      │                                   │
                                                      │                        ┌──────────┴──────────┐
                                                      │                        ▼                     ▼
                                                      │                     Matches               Mismatch
                                                      │                        │                     │
                                                      ▼                        ▼                     ▼
                                              [ PLAY SAMPLE ]          [ PLAY SAMPLE ]     [ THE SOUND GLITCH ]
```

1. **SFX Opcode Table (`$8C:8362`, ROM `0x0C8362`):**
   * 120 16-bit words indexing script parameters `0x00, 0x02, ... 0xEE`.
   * `0xFFFF` = Hard-muted / disabled (`BMI` branch bypasses APU entirely).
2. **Song Dependency Table 2 (`$81:9A1E`, ROM `0x019A1E`):**
   * 90 byte entries corresponding to internal sound indices `0..89`.
   * **Indices `0..61` (82 Sounds):** Song `0x00` (Master Global Bank). Always resident in ARAM; playable under ANY music.
   * **Indices `62..89` (28 Sounds):** Non-zero song required. Only playable when matching song is playing.
3. **Music Opcode Table (`$8C:8442`, ROM `0x0C8442`):**
   * 73 16-bit words translating script opcode `0x33` parameters (`0x02`–`0x90`) to internal song index (`0x00`–`0x46`).
4. **Master Song Pointer Table (`$81:9903`, ROM `0x019903`):**
   * 71 24-bit SNES pointers (`$8A:A7BE`–`$8B:8E8E`) to 7-byte song upload descriptor packets.

---

## 6. Unused Music Tracks & Sound Effects

### Unused Music
* **Song `0x46` (Song 70, `$8B:8E8E`):** Completely unmapped in opcode `0x33` table! Contains full sequence data in ROM, but has no script opcode to trigger it.
* **Song `0x0c` (Song 12, Opcode `0x1a`):** Mapped in engine, but has **0 calls** across all 127 rooms and events.
* **Song `0x26` (Song 38, Opcode `0x4e`):** Mapped in engine, but has **0 calls** across all vanilla scripts.

### Unused / Hard-Muted Sounds
* **11 Hard-Muted Sounds (`0xFFFF`):** `0x0e`, `0x16`, `0x18`, `0x26`, `0x28`, `0x62`, `0xce`, `0xd2`, `0xd4`, `0xd6`, `0xe0`.
* **Orphaned Context Sounds:**
  * `0x78`: Requires orphaned Song `0x46`.
  * `0xca`, `0xcc`: Requires Song `0x2b` (`PUPPET_SHOW`), never called in puppet scripts.
  * `0xb6`: Requires Song `0x32` (`HALLS_3`), uncalled.
  * `0x12`: Requires Song `0x44` (`BOSS_BOSSRUSH`), uncalled.

---

## 7. Rules for Avoiding "The Sound Glitch"

When scripting rooms, cutscenes, or custom Kaizo encounters:
1. **Always consult [`docs/music_sound_compatibility_table.md`](../../docs/music_sound_compatibility_table.md):**
   * Verify that any non-global sound (`0x22`, `0x40`, `0x58`, `0x5e`, `0x60`, `0x6a`, `0x6c`, `0x6e`, `0x72`, `0x76`, `0x7a`, `0xa6`, etc.) matches the room's active music track.
2. **Never change music during a multi-phase boss fight** without accounting for boss SFX:
   * E.g. Calling `THRAXX_DAMAGE` (`0x22`) under `BOSS_BOSSRUSH` (`0x8a`) causes severe audio lag and crash.
3. **Safe Fallback:** The **82 Universal Sounds** (weapons, dog barks, alchemy spells, menu clicks) are 100% safe under every background music track in the game.
