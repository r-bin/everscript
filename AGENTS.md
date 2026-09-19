# Global Agent Guidelines (Everscript Project)

These instructions apply to all AI assistants and agent environments working in this repository (Antigravity, GitHub Copilot, Claude Code, Cursor, etc.). Individual tasks may specialize workflows, but must never violate these core principles.

> **Single source of truth.** This file (`/AGENTS.md`, repo root — the canonical location per the open [AGENTS.md standard](https://agents.md)) is the only place these rules are written. Every other AI-config entry point is a symlink or one-line import that resolves back here — edit this file, never the aliases:
> - `/CLAUDE.md` → one-line `@AGENTS.md` import (Claude Code's official bridge pattern for sharing AGENTS.md)
> - `.github/copilot-instructions.md` → symlink to this file (Copilot's required fixed path)
> - `.github/skills/` → canonical skills folder (Copilot's own official skills path); `.agents/skills/` and `.claude/skills/` are symlinks to it (Antigravity's and Claude Code's own official skills paths, respectively)
> - `.github/agents/*.agent.md` → Copilot-only custom subagent definitions (VS Code `chatagent` schema). Not portable to other tools — maintained separately, not duplicated here.

---

## 1. Non-Negotiable Core Principle: ROM Hacking is Exact Science

> [!CAUTION]
> **Treat all information about the ROM, memory, and game mechanics as strict empirical science.**
> In binary ROM hacking, hallucinations, guesswork, and imprecise approximations are **catastrophically destructive**—a single wrong offset, misplaced bit, or fabricated identifier causes silent save corruption, memory clobbering, or system lockups.
>
> **The Golden Rule: Rather say "I don't know" than guess.**
> - If an address, opcode, flag, parameter, coordinate, or mechanic is not 100% verified by disassembly, debugging, or documented in `in/core/`: **explicitly state that you do not know**.
> - An honest question mark (`?`) or unresolved `// TODO:` is infinitely superior to a plausible-sounding hallucination.
> - **Never invent names, symbols, or enum identifiers.** Use raw hex (e.g. `<0x22eb, 0x01>`, `0x38`) whenever an authoritative label is absent.
> - Distinguish empirical facts (observed in `script_all` or verified in Mesen2) from hypotheses. Never present a conjecture as fact.

---

## 2. Operating Guardrails

1. **Explicit Inconsistency Handling:**
   - If sources disagree (e.g. dump coordinates vs. a stub file, constant values vs. comments), **never silently pick a side**.
   - Flag discrepancies explicitly in comments: `// MISMATCH: <description>` or `// TODO: <unresolved issue>`.

2. **File Editing Safety:**
   - **Do not modify project source files** (`.evs`, `.py`, `.asm`, `.md`) without explicit instruction naming the target file.
   - For unsolicited suggestions or exploratory code, print to chat/console.

3. **Boolean Inference:**
   - Only use `True` / `False` when the field is confirmed boolean (tagged `[BOOLEAN]` in `core.evs` or documented 0/1 flag). Otherwise, use raw values (e.g. `0x01`, `0x00`).

4. **Vanilla vs. Custom Separation:**
   - Skip `[CUSTOM]` entries in `in/core/` when researching vanilla mechanics; those are romhack additions.

---

## 3. Core Repository Reference

| Resource | Path | Description |
|---|---|---|
| **Architecture Guide** | [architecture.md](file:///Users/v/Documents/GitHub/everscript/architecture.md) | Full compilation pipeline and repository layout. |
| **Authoritative Constants** | [in/core/main.evs](file:///Users/v/Documents/GitHub/everscript/in/core/main.evs) | Single source of truth for addresses, enums, functions. |
| **WRAM Map** | [.github/memory-map.md](file:///Users/v/Documents/GitHub/everscript/.github/memory-map.md) | Single source of truth for vanilla Evermore RAM. |
| **Kaizo Todo / Backlog** | [dev_notes.md](file:///Users/v/Documents/GitHub/everscript/dev_notes.md) | Active bugs, boss tuning, and scope for Kaizo release. |
| **Vanilla Oddities** | [vanilla_bugs_and_oddities.md](file:///Users/v/Documents/GitHub/everscript/vanilla_bugs_and_oddities.md) | Catalog of vanilla bugs to distinguish from new regressions. |
| **Script Dump** | `/Users/v/Documents/GitHub/SoETilesViewer/SoEScriptDumper/script_all` | Raw disassemblies from sibling SoETilesViewer project. |

---

## 4. On-Demand Skills (`.github/skills/`)

Operational workflows and runbooks live in `.github/skills/` (aliased at `.agents/skills/` and `.claude/skills/` for tool-native discovery — same files, don't duplicate). Consult these skills on demand when performing specialized tasks:

- **Classification & Standards:**
  - `data-classification-emojis`: Standard emoji taxonomy (📖, 🚪, 🌿, 🧪, 💎, ⚔️, 🛡️, ⚗️, 🫙, 👃, 🧑, 🐶, ⚙️).
- **Compiler & Pipeline:**
  - `everscript-workflow`: End-to-end `.evs` $\to$ IPS compilation steps.
  - `compiler-testing`: Running `pytest` and checking parser conflicts.
  - `pyinstaller-packaging`: Standalone binary generation via `make.py` & `everscript.spec`.
- **Memory & Hardware:**
  - `snes-memory-mapping`: ROM file offsets vs. SNES 24-bit address bus (HiROM/slow/fast ROM).
  - `wram-memory-mapping`: SNES WRAM structure, endianness, direct page, player stats.
  - `secret-of-evermore-engine`: Engine architecture (1 player + dog AI, enter/step-on/B-triggers).
- **Patching & ASM:**
  - `snes-asm-asar-patching`: Writing 65c816 hooks in `patches/` with Asar safely without crashing.
  - `ips-patch-format`: Binary IPS structure and patch utilities.
- **Reverse Engineering & Debugging:**
  - `mesen2-debugging-re`: Using Mesen2 debugger, memory viewer, and breakpoints to discover unknown data.
  - `everscript-core-reference`: Structure of `in/core/` and how to extend constants.
  - `everscript-bytecode-vm`: The script virtual machine, bytecode format, and opcodes.
- **Game Design & Mechanics:**
  - `kaizo-design-philosophy`: Kaizo difficulty, boss tuning, and backlog triage.
  - `metroidvania-mechanics`: Weapon gates (`$235F`/`$2360`) and ability barriers.
  - `rom-map-data`: Experimental ROM map loading, geometry, and tileset routines.
