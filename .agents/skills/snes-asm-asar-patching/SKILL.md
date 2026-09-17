---
name: snes-asm-asar-patching
description: Explains how Asar is used to write 65c816 assembly patches in patches/*.asm, how hooks work, and critical processor state pitfalls that cause ROM crashes.
---

# SNES Assembly & Asar Patch Engineering

While Everscript handles high-level game logic, low-level engine modifications (such as custom controller hotkeys, status effect fixes, damage formula adjustments, and input interceptors) are written in **65c816 SNES assembly** using the **Asar** assembler.

---

## 1. How Asar Works in this Project

Asar takes `.asm` source files, evaluates macros and labels, and assembles them directly into binary patches or ROM offsets.

In the Everscript project:
- Source assembly files live in `patches/*.asm` (e.g. `hotkeys.asm`, `scale_enemies.asm`, `five_status_effects_fix.asm`).
- Assembly patches are referenced in Everscript via the `#patch("name")` directive.
- The utility [ips2asar.py](file:///Users/v/Documents/GitHub/everscript/ips2asar.py) can also disassemble binary IPS patches back into clean, commented Asar assembly files.

---

## 2. Anatomy of an Assembly Hook

To alter vanilla engine behavior without replacing entire subsystems, assembly patches inject **hooks** into vanilla code:

```assembly
; Target: Hook into controller poll routine
org $92E44E            ; Overwrite 4 bytes at vanilla ROM address
    JSL custom_input_hook
    NOP                 ; Fill remaining byte if needed

; Extension ROM space: Place custom hook routine
org $3D82C0
custom_input_hook:
    PHP                 ; Preserve processor status flags (M and X bits!)
    PHB                 ; Preserve Data Bank
    PHD                 ; Preserve Direct Page

    ; --- Custom logic begins ---
    SEP #$20            ; Set Accumulator to 8-bit mode
    LDA $7E0104         ; Read controller input
    CMP #$80            ; Check Start button
    BNE .done
    ; Perform action...

.done:
    PLD                 ; Restore Direct Page
    PLB                 ; Restore Data Bank
    PLP                 ; Restore processor status flags

    ; Replicate the vanilla instruction that was overwritten by the JSL!
    LDA $7E0A35

    RTL                 ; Return Long to caller
```

---

## 3. Why ASM Patches Are Dangerous (Common Crash Causes)

Writing 65c816 assembly without crashing the SNES requires strict adherence to register invariants. The most common failure modes are:

### 3.1 Register Width Desynchronization (`REP` / `SEP`)
- The 65c816 CPU dynamically switches between 8-bit and 16-bit register modes:
  - `SEP #$20`: Accumulator (`A`) becomes 8-bit.
  - `REP #$20`: Accumulator (`A`) becomes 16-bit.
  - `SEP #$10`: Index registers (`X`, `Y`) become 8-bit.
  - `REP #$10`: Index registers (`X`, `Y`) become 16-bit.
- **The Crash:** If an injected hook changes `A` to 8-bit (`SEP #$20`) and returns (`RTL`) without restoring `A` to 16-bit, the vanilla caller will treat the next 16-bit instruction as an 8-bit instruction. Every subsequent instruction will be decoded out-of-phase, immediately crashing the game.
- **Rule:** Always wrap hooks in `PHP` (Push Processor Status) and `PLP` (Pull Processor Status).

### 3.2 Bank Register Corruption (`DB` and `PB`)
- The Data Bank register (`DB`) controls which $64\text{ KB}$ bank 16-bit memory addresses read from.
- If your hook is located in extended ROM (e.g. bank `$3D`), `DB` might be pointing to bank `$3D`. If you then do `LDA $0A35`, the CPU will attempt to read from `$3D0A35` instead of WRAM `$7E0A35`!
- **Rule:** Use 24-bit long addressing (`LDA $7E0A35`) or preserve and set the Data Bank using `PHB / PLB`.

### 3.3 Forgetting Overwritten Vanilla Instructions
- A `JSL` instruction takes 4 bytes (`22 LL HH BB`).
- If you place a `JSL` over a 3-byte vanilla instruction, you will clobber 1 byte of the *next* instruction.
- You must either:
  1. Re-execute the overwritten instructions inside your hook routine before returning.
  2. Use `NOP` (`$EA`) padding if the replacement takes fewer bytes than the original instructions.

---

## 4. Disassembling IPS to Asar with `ips2asar.py`

To inspect what an existing binary IPS patch is doing:
```bash
python3 ips2asar.py patches/scale_enemies.ips patches/scale_enemies.asm
```
This automatically produces disassembled 65c816 mnemonics, extracts `org` offsets, and annotates constants.
