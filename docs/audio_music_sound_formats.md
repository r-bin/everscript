# Audio: Sound Driver Protocol, Packages & SPC Dumping

How the 65816 loads and drives the SPC700 sound driver, and how
`tools/dump_spc.py` reproduces it to dump playable `.spc` files.

Everything here was verified by disassembling bank `$8C` and by running the
ROM's driver in the SPC700 interpreter inside `tools/dump_spc.py`. The
resulting dumps match all 72 reference rips in the "Secret of Evermore (EMU)"
set (time-aligned spectrogram cosine 0.92–0.999, mostly at offset 0.0 s).

---

## 1. Terms: music id vs. package

| Term | Range | Meaning |
|---|---|---|
| **Package** | `0x00`–`0x46` | An upload unit at `$81:9903` (samples, instrument/SFX tables, sequence). Package `0x00` is the global base bank. |
| **Music id** | `0x00`–`0x45` | The value sent with command `$06`. Music `M` needs package `M + 1` (table `$81:99D8`). |
| **Sound effect** | `0x00`–`0x59` | The value sent with command `$04`. Its package comes from `$81:9A1E` (`0` = base bank only). |

The script opcode `0x33` table (`$8C:8442`) yields **music ids** (`0x00`–`0x45`, all present).
`$0E4B` holds the loaded **package** (`$8C:8236` compares against it), not a music id.

---

## 2. ROM layout

| SNES | ROM | Content |
|---|---|---|
| `$81:80DC` | `0x0180DC` | IPL block list `[len:16][dest:16] data…`, `len = 0` ends (its dest = entry). One block: `$17E0` bytes of driver → SPC `$0700`, entry `$0700`. |
| `$81:9900` | `0x019900` | Last package index (`$46`: 71 packages, pointer table length). |
| `$81:9901` | `0x019901` | Music count (`$46`: music ids `0x00`–`0x45`); also the offset from the music table to the sfx table (`$8C:82FC`). |
| `$81:9902` | `0x019902` | Sound-effect count (`$5A`: driver sfx `0x00`–`0x59`). |
| `$81:9903` | `0x019903` | 71 × 24-bit pointers to packages. |
| `$81:99D8` | `0x0199D8` | 70 bytes: music id → package (always `M + 1` in vanilla). |
| `$81:9A1E` | `0x019A1E` | 90 bytes: sound effect → package (`0` = none). |

**Package format:** `[count:16]`, then `count` × `[len:16][src:24][spc_dest:16]`.
Every read (descriptor and data) walks **bank upper halves only**: past `$xx:FFFF`
it continues at the next bank's `$8000` (`$8C:818D`, `$8C:819E`). A flat copy
garbles every record that crosses a bank.

Package contents seen in practice: BRR samples, 4-byte sample-directory entries
at `$1F00+`, instrument and SFX pointer tables around `$2000`–`$2300`, a
music pointer at `$2E00+`, and the sequence near the top of the sample area.

---

## 3. Command protocol (`$8C:81FD`)

The CPU waits until `$2142` (the driver's echo) equals its counter `$9F`,
increments `$9F` (skipping `0`), then writes:

| Port | Value |
|---|---|
| `$2140`/`$2141` | Parameter (Y register, 16-bit) |
| `$2142` | Counter |
| `$2143` | Command |

`$8C:81D4` then waits for the echo of the new counter.

| Cmd | Parameter | Effect | Sent by |
|---|---|---|---|
| `$02` | – | Sent after every package upload | `$8C:801F`, `$8C:8236` |
| `$04` | sfx | Play sound effect | `$8C:82E3` |
| `$06` | music id | Play music | `$8C:828F` |
| `$0E` | – | Driver jumps to the IPL ROM (`$FFC0`) for an upload | `$8C:801F`, `$8C:8236` |
| `$1A` | `$0000` | Sent before a music change | `$8C:828F` |
| `$1C` | `$8080` | Sent before a music change | `$8C:828F` |
| `$28` | volume | Music volume (`$8C:8619` steps it for fades; `$30` ≈ 1/6 of full output) | `$8C:8619` |
| `$36`, `$3E` | ? | Seen at `$8C:85DF` / `$8C:8614`; effect not verified | |

### Upload (`$0E` + `$8C:805B`)
1. Command `$0E`: the driver enters the IPL ROM, which **clears SPC `$01`–`$EF`** and shows `$BBAA` on `$2140/41`.
2. `$8C:805B` streams every record of the package with the standard IPL handshake.
3. It finishes with `$2142/43 = $0700`, `$2141 = 0`: the IPL jumps to `$0700` and the driver starts fresh on top of the uploaded data (it writes `$01` to `$F6`, so `$9F = 1`).
4. Command `$02`.

### Sequences
- **Boot** (`$8C:801F`): IPL-upload the driver from `$81:80DC` → `$0E` + package `0` → `$02`.
- **Music `M`** (`$8C:828F`): `$1C $8080` → `$1A $0000` → if package `M + 1` is not loaded: `$0E` + package → `$02` → `$06 M`.
- **Sound effect `S`** (`$8C:82E3`): if its package is non-zero and not loaded, upload it like music → `$04 S`.

The driver sets DSP `DIR = $02` and echo `ESA = $D4` at run time.

---

## 4. Dumping (`tools/dump_spc.py`)

```bash
python tools/dump_spc.py                # out/music_spc, out/music_wav, out/reference_wav
python tools/dump_spc.py --no-wav       # .spc only
python tools/dump_spc.py --no-compare   # skip the reference comparison
```

- The script runs the ROM's driver in its own SPC700 interpreter (CPU, timers, DSP register file; no audio) and plays the CPU side of §3.
- The snapshot is taken when the driver acknowledges `$06`/`$04`, so a player starts the track at its first tick.
- **Ports:** the input ports are stored in RAM `$F4`–`$F7`. Players that zero them produce identical audio (tested with libgme).
- **WAV and comparison:** WAVs are rendered with libgme (`brew install game-music-emu`). The comparison needs numpy.

### Tracks that are not plain music ids
| Track | Source |
|---|---|
| Music `0x27` | Empty sequence (`F2 7F FA 00 F0`); package `0x28` only carries SFX samples. Not dumped. |
| Music `0x28` | No reference rip; close to Major Enemy (`0x10`) but not the same. Dumped as `xx_Unused_0x28`. |
| "Explosion" | Sound effect `0x42` (package `0x43`). |
| "Applause" | Sound effect `0x56` (package `0x42`). |
| "Takeoff!" | Sound effect `0x3B` (base bank). |
| "Windy Cave" | Distant Wind (music `0x2D`) at volume `$28 $30`. |

The "Quiet Plaza" reference rip was also recorded at volume `$30`. The dump is at full volume.

### The reference rips
The "Secret of Evermore (EMU)" rips use **another build of the same driver** (code and zero page relocated, e.g. `CALL $109F` vs. the ROM's `CALL $1073` at `$0710`). Compare them by sound, not by ARAM bytes. Their samples, sample directory and sequences match the ROM byte for byte.

---

## 5. Sound effects

### Dispatch path (disassembly)
Script opcode `0x30` (`sound()`) at `$8C:D6BD`:
1. Reads the script's SFX byte and looks it up in `$8C:8362`. A negative entry (`$FFFF`) means muted, and nothing is sent.
2. Otherwise it calls **`$8C:82DC`**: store the sfx in `$0E4F` → `$04 S` (`$8C:831D`).

`$8C:82DC` **does not load the effect's package.** The entry that does (`$8C:82E3`: look up `$81:9A1E`, then `$8C:8236`) has no direct `JSL` callers in the ROM. So a sound effect plays against whatever package the current music loaded.

### What a sound effect needs in ARAM
- **Base-bank effects:** 62 of the 90 entries in `$81:9A1E` are `0`. Their samples and definitions come with package `0`, which is uploaded at boot and never replaced.
  - `// MISMATCH:` `music_sound_compatibility_table.md` and the skill count **82** universal sounds. That count is over the script-level ids (`$8C:8362`), not the 90 internal entries. Not reconciled here.
- **Package effects:** the other 28 entries name 21 different packages (`0x02`, `0x08`, `0x11`, `0x16`, `0x1F`, `0x22`, `0x23`, `0x28`, `0x29`, `0x2B`, `0x2E`, `0x30`, `0x32`, `0x3A`, `0x3C`, `0x3F`, `0x41`, `0x42`, `0x43`, `0x44`, `0x46`). Their samples and definitions arrive only with that package.
- **Pointer tables:** packages write 2-byte pointers into shared tables at `$2070`–`$2350`. The base bank writes 190 of them, and each package overwrites some. Which slot belongs to which effect or instrument is **not decoded yet**, so there is no simple "slot = sfx id" rule.

### Behaviour on a mismatch (interpreter)
Sending `$04 S` while another package is loaded was tested for 4 mismatched pairs: music `$00` + sfx `$42` / `$56`, and music `$15` + sfx `$3E` / `$52`. The driver **acknowledged within ~35 instructions and kept accepting commands**; it did not hang. Matched pairs (music `$42` + `$42`, music `$41` + `$56`) behave the same. What a mismatched effect sounds like, and where the in-game lag or freeze comes from, is open (see [`the_sound_glitch.md`](the_sound_glitch.md)).

---

## 6. ARAM layout and budget

Measured over all 70 music ids (driver + package `0` + package `M + 1`, echo buffer at its largest seen size, EDL 5):

| SPC range | Content |
|---|---|
| `$0000`–`$01FF` | Zero page (driver variables; IPL clears `$01`–`$EF` on every upload), I/O, stack |
| `$0200`–`$021F` | **Per-voice sample directory**: DSP `DIR = $02`, and the driver keys voice *v* with `SRCN = v`. It writes the real sample's start/loop into entry *v* before key-on. |
| `$0700`–`$1EDF` | Driver (`$17E0` bytes) |
| `$1EE0`–`$23FF` | Sample directory at `$1F00` (4 bytes per sample) and the pointer tables of §5 |
| `$2400`–`$3ABF` | **Unused in every package** (5,822 bytes) |
| `$3AC0`–`$678D` | Base-bank samples (package `0`) |
| `$678E`– | Song samples, then the sequence (Main Title: `$C231`–`$C3A9`) |
| `$D400`–`$FBFF` | Echo buffer (`ESA = $D4`; EDL 5 in many reference rips = 10 KB) |
| `$FFC0`–`$FFFF` | IPL ROM (enabled, `$F1 = $87`/`$B7`) |

- Free ARAM per music track, all gaps counted: **8,934–35,700 bytes, median 16,685**.
- Space between the top of song data and `$D400`: **26–26,738 bytes, median 7,757**. Package `0x3B` (music `0x3A`, Regal Castle) ends at `$D3E5`.
- Timers set by the driver: `$FA = $FB = $A0` and `$FC = $20`. Timer 0 therefore ticks at 50 Hz (160 × 128 cycles). Which timer drives the tempo is not verified.

### What this means for custom audio
- **Music from other games:** there are no `.spc` files in the ROM to swap. Other games' sequences target other drivers, so a song has to be rewritten as Wolfgang bytecode (opcode table **not decoded yet**) with BRR samples. Driver + base bank + new package must fit. That leaves a song package about 36 KB (36,674 bytes) with a 10 KB echo buffer, or about 46 KB without echo. The largest vanilla package is 27,738 bytes.
- **Uploading a whole foreign SPC** (its ARAM + jump to its driver) is mechanically possible, because each music change already is a full IPL upload. But Evermore's driver and its sound effects are gone until the driver, package `0` and a package are uploaded again. Not tested.
- **Effects in a map that doesn't have them:** add their samples and table entries to that map's music package. This needs the pointer tables of §5 decoded and a package writer; neither exists yet.
- **All effects everywhere:** not possible for the fullest packages (Regal Castle has 26 bytes left below the echo buffer). Moving an effect into package `0` costs its size in every song. The per-effect sample sizes are not measured yet.

---

## 7. Watching the driver live

The interpreter in `tools/dump_spc.py` can log every DSP write (`$F2`/`$F3`) with its cycle time. That gives a driver-independent note list:
- A note is a `KON` (`$4C`) bit.
- Its pitch is `P(H/L)` of that voice. Its sample is the voice's `$0200` entry at that moment, not `SRCN`.
- It ends at `KOF` (`$5C`) or the next `KON` on the voice.
- Reads of the sequence range show which sequence bytes the driver consumed on each tick.

Checked against libgme: each voice soloed with `gme_mute_voices`. Key-ons land at a **constant** offset of −30 to −60 ms from the audible attack, with no drift over 24 s (voice 2: −32 ms at every note). The likely cause is the timer phase at load, which the SPC format doesn't store; this is not verified.

Main Title (music `$00`), first 30 s: 229 notes on all 8 voices, using sample-directory entries `0x0E`–`0x12` (the 5 samples of package `0x01`), and 1,983 sequence-byte reads in 8 tracks from the pointer table at `$C231`.

A panel built on this in the emulator would read DSP registers, ARAM and the driver's read address straight from the core every frame (mockup: https://claude.ai/artifact/QHt9cxWViSqToKoiHRjRwr). Whether the bundled snes9x core exposes APU RAM and DSP registers is not checked yet.
