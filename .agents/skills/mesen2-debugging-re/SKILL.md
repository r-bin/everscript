---
name: mesen2-debugging-re
description: Explains how to use the Mesen2 emulator debugger, memory viewer, trace logger, and breakpoints to reverse-engineer unknown vanilla Evermore game mechanics.
---

# Mesen2 Debugging & Reverse Engineering

**Mesen2** is an open-source, cycle-accurate SNES emulator equipped with advanced debugging suites. When reverse-engineering undocumented Secret of Evermore engine features or diagnosing game-crashing bugs, Mesen2 is the primary tool.

---

## 1. Key Mesen2 Developer Tools

Mesen2 includes dedicated debugging windows accessible via `Debug` in the menu bar:

1. **CPU Debugger (`Ctrl+D`):**
   - Shows disassembled 65c816 assembly in real-time.
   - Displays all CPU registers: Accumulator (`A`), Index (`X`, `Y`), Program Counter (`PC`), Stack Pointer (`S`), Direct Page (`D`), Data Bank (`DB`), Program Bank (`PB`), and Processor Status flags (`N V M X D I Z C`).
   - Single-step through code (`Step Into`, `Step Over`, `Step Out`).

2. **Memory Viewer & Hex Editor:**
   - Displays real-time contents of **WRAM** (`$7E0000..$7FFFFF`), **SRAM** (Cartridge Save RAM), **VRAM** (Video RAM), and **OAM** (Object Attribute Memory / Sprites).
   - Allows live editing of RAM values to test hypotheses without re-compiling.

3. **Trace Logger:**
   - Records every instruction executed by the CPU to a text file.
   - Useful for capturing the exact sequence of events leading up to a crash or softlock.

4. **Event Viewer & PPU Debugger:**
   - Visualizes scanline rendering, sprite layers, background tilemaps, and DMA transfers.

---

## 2. Reverse-Engineering Unknowns: The Breakpoint Workflow

When an in-game behavior is undocumented (e.g. what memory address controls an enemy attack, or what instruction writes to a story flag):

### Scenario: Finding What Sets a Persistence Flag
1. Open **Memory Viewer** in Mesen2.
2. Locate the suspect address in WRAM (e.g. `$7E2260`).
3. Add a **Breakpoint**:
   - Type: `Memory Access`
   - Address: `$7E2260`
   - Break on: `Write`
4. Resume emulation and trigger the in-game event (e.g. defeat Thraxx, loot a gourd).
5. The emulator halts at the exact 65c816 instruction writing to `$7E2260`.
6. Inspect the call stack:
   - If written by the Evermore script interpreter, check the `PC` to locate the bytecode address in ROM.
   - Cross-reference with `script_all` to see the opcode context.

### Scenario: Diagnosing a Crash After an ASM Hook
1. Add a **Break on Execute** breakpoint at your hook's injection address (e.g. `$92E44E`).
2. Trigger the action. When execution pauses:
   - Note the status of the `M` and `X` flags in the register panel (0 = 16-bit, 1 = 8-bit).
   - Single-step (`F11`) through your custom hook.
   - Confirm that upon reaching `RTL`, the `M` and `X` flags, `DB`, and `D` registers are completely identical to their state prior to the hook.

---

## 3. Demystifying Unknown Bytecodes

If the compiler encounters an unmapped opcode:
1. Break on the script interpreter's main opcode fetch loop in ROM (located in bank `$00` / `$90`).
2. Step through the jump table dispatch for the unknown opcode byte.
3. Observe which CPU registers and WRAM addresses the dispatch routine accesses.
4. Document the parameter count and stack effect in `compiler/codegen.py` and `.github/compiler-reference.md`.
