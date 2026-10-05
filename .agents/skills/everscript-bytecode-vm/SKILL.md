---
name: everscript-bytecode-vm
description: Explains the Secret of Evermore script bytecode virtual machine, opcode structure, calculator expressions, and partially understood bytecodes.
---

# Everscript Bytecode & The Evermore Script VM

The Secret of Evermore game engine does not run 65c816 assembly for event logic; instead, it executes a custom, proprietary **bytecode scripting language** via an in-engine Virtual Machine (VM). The Everscript compiler's primary job is converting high-level `.evs` syntax into these exact bytecodes.

---

## 1. Bytecode Stream Format

Bytecode in Evermore is organized into linear instruction streams:
```
[1 Byte Opcode] [Variable-length parameters / calculator tokens...]
```

When an event triggers (such as room entry or stepping on a trigger), the engine's script interpreter reads the opcode byte, indexes a ROM jump table, and executes the corresponding native 65c816 routine to handle the instruction.

---

## 2. Key Opcodes Reference

| Hex Opcode | Mnemonic / Operation | Parameters | Description |
|---|---|---|---|
| `0x00` | `END` / `RETURN` | None | Terminates current script execution or returns from call. |
| `0x0C` | `WRITE FLAG` | Address (Word), Flag (Byte), Value | Writes a single bit in persistent WRAM (`$2258..$23FF`). |
| `0x10` | `JUMP` | Target Offset (Word) | Unconditional jump within the script. |
| `0x11` | `BRANCH IF FALSE` | Calc Expr, Target Offset (Word) | Evaluates calculator expression; branches if zero/false. |
| `0x22` | `CHANGE MAP` | Map ID (Byte), X (Byte), Y (Byte) | Transitions to a new map at the designated coordinates. |
| `0x29` | `CALL SCRIPT` | Script Address (3 Bytes Long) | Calls a subroutine script at a 24-bit ROM address. |
| `0x30` | `PLAY SOUND` | Sound ID (Word) | Triggers a sound effect in the SPC700 audio queue. |
| `0x48` | `SHOW TEXT` | String Key (Word) | Opens a dialogue window and displays the indexed text. |

---

## 3. The Calculator Expression Engine

Conditional branching (`if`, `while`) and math operations are handled by an internal **calculator stack**:
- Instructions like `0x11` (Branch If False) do not take raw comparison values; they take a sequence of calculator tokens terminating in an evaluation opcode.
- Calculator tokens allow:
  - Reading a byte or word from WRAM (`Memory(addr)`).
  - Pushing integer literals (`0x00`..`0xFFFF`).
  - Bitwise testing (`&`, `|`, `^`).
  - Relational comparisons (`==`, `!=`, `<`, `>`, `<=`, `>=`).
- Example in `out/patch.txt`:
  ```
  308000 0007 // function='Function(...)', count='7'
  0C 2B 00 B1 // calculator([Opcode(0C/write flag), '2B 00', [...]])
  ```

---

## 4. Undocumented & Partially Known Opcodes

Because Secret of Evermore was reverse-engineered without official source code, **not all opcodes are fully understood**:
- Some opcodes have unknown parameter flags or secondary side effects on engine registers.
- If the compiler encounters an unmapped bytecode:
  - The AST emits a raw bytecode sequence or calculator node.
  - The opcode is documented with a question mark in disassembly dumps: `(30) PLAY SOUND EFFECT 0x58 ??`.
  - To investigate unknown opcodes, use the breakpoint workflow in [mesen2-debugging-re](file:///Users/v/Documents/GitHub/everscript/.agents/skills/mesen2-debugging-re/SKILL.md) to inspect the interpreter dispatch routine.
