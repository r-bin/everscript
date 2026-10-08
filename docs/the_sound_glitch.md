# The Sound Glitch

"The sound glitch" is the vanilla bug where sound effects buzz or drop out, the game lags, or it freezes, usually around room-specific sounds. This page separates what is verified from what is not. Protocol details: [`audio_music_sound_formats.md`](audio_music_sound_formats.md).

---

## Verified

- **The sound opcode never loads a package.** Opcode `0x30` → `$8C:8362` lookup → `$8C:82DC` → command `$04 S`. The package-loading entry `$8C:82E3` has no direct `JSL` callers (§5 of the protocol doc).
- **28 of the 90 internal sound effects need a package** (`$81:9A1E` non-zero). They only find their samples and definitions in ARAM while the music using that package is loaded.
- **The driver survives a mismatch in the interpreter.** For 4 tested pairs (music `$00` + sfx `$42`/`$56`, music `$15` + sfx `$3E`/`$52`), it acked the command within ~35 instructions and kept accepting commands.
- **The CPU side can stall.** Every command goes through `$8C:81FD`. It runs with interrupts off (`SEI`) and polls `$2142` until the driver echoes the previous counter, for up to `$2800` loop passes before giving up. A driver that is slow to echo stalls the CPU there.

## Not verified

- `// TODO:` What a mismatched effect plays. Its definition comes from whatever the shared pointer tables (`$2070`–`$2350`) hold for the loaded package; those tables are not decoded.
- `// TODO:` Whether a mismatched effect can make the driver miss echoes, and so stall `$8C:81FD`. This is the most likely link to the lag, but it is unproven. Only 4 pairs were tried, for ~0.2 s each.
- `// TODO:` The freeze. No hang was reproduced.
- `// MISMATCH:` `music_sound_compatibility_table.md` §1.3 shows an "active song verification" on the sound-effect path at `$8C:8236`. In the ROM, `$8C:8236` is the package loader, and the opcode `0x30` path (`$8C:82DC`) never reaches it. The disassembly in this file takes precedence until shown otherwise.

## How to test further

1. Run every (music, sfx) pair in the interpreter of `tools/dump_spc.py`. Record the ack latency, any stuck program counter, and the DSP writes.
2. Render the mismatched pairs with libgme and listen.
3. Reproduce a reported glitch in the emulator with the debugger core, and break on `$8C:81FD` to see whether the CPU is spinning there.
