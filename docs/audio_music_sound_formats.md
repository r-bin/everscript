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
| `$81:9900` | `0x019900` | Music count (`$46`). |
| `$81:9901` | `0x019901` | Sound-effect count (`$5A`). |
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
