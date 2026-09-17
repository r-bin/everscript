# Everscript Architecture & Project Structure

Everscript is a domain-specific programming language and optimizing compiler designed for the Super Nintendo Entertainment System (SNES) action-RPG **Secret of Evermore** (Square, 1995). It allows developers to author game events, map scripts, custom bosses, dialogue, and engine modifications in a clean C-like syntax, which compiles into binary IPS patches directly applicable to the ROM.

---

## 1. System Pipeline Overview

```
Source Files (.evs) + #includes + #patches
               │
               ▼
   Lexer (compiler/lexer.py)              ──► out/lexer.txt, out/lexer_include.txt
               │
               ▼
   Parser (compiler/parser.py)            ──► Abstract Syntax Tree (AST)
               │
               ▼
   CodeGen (compiler/codegen.py)          ──► Bytecode Generation & Scopes
               │
               ▼
   Linker (compiler/linker.py)            ──► out/memory_map.txt, out/patch.txt
               │
               ▼
   IPS Converter (utils/file_utils.py)    ──► out/everscript.ips
               │
               ▼ (Optional)
   Target ROM (Secret of Evermore.smc)    ──► Patched SNES ROM
```

---

## 2. Directory Layout & Roles

```
.
├── AGENTS.md                  # Universal system instructions for AI agents
├── architecture.md            # This project architecture reference
├── everscript.py              # Main CLI entry point
├── make.py                    # Build automation (PyInstaller compilation)
├── everscript.spec            # PyInstaller packaging specification
├── dev_notes.md               # Active developer backlog and Kaizo task tracking
├── vanilla_bugs_and_oddities.md # Catalogue of known vanilla engine bugs
│
├── compiler/                  # The Python-based Everscript compiler
│   ├── lexer.py               # RPLY-based tokenization (50+ token rules)
│   ├── parser.py              # LALR(1) parser building the AST
│   ├── ast_core.py            # Base AST nodes, caching, code emission, and helpers
│   ├── ast_everscript.py      # Concrete language AST nodes (loops, branches, memory)
│   ├── codegen.py             # Scope management and bytecode instruction formatting
│   └── linker.py              # Bank-aware ROM/RAM memory manager and allocator
│
├── in/                        # Everscript source code (.evs)
│   ├── core/                  # Authoritative base library: enums, addresses, functions
│   │   ├── [group] 00_general_enums/  # ROM addresses, WRAM labels, SNES registers, audio/sprite/item IDs
│   │   └── [group] 02_functions/      # Built-in helper functions, cutscene helpers, AI moves
│   ├── kaizo/                 # The Kaizo overhaul project (high-difficulty romhack)
│   │   ├── [area] rooms/      # Per-area room logic, puzzles, triggers
│   │   ├── [group] custom_bosses/ # Multi-phase custom boss AI scripts
│   │   ├── [group] non_maps/  # General helpers, hotkeys, cutscenes
│   │   └── main.evs           # Main entry point for the Kaizo project
│   ├── practice/              # Practice Hack (speedrun/testing debug tools)
│   ├── custom_bosses/         # Standalone custom boss prototypes
│   └── evermizer_contributions/ # Patches integrated upstream into the Evermore Randomizer
│
├── patches/                   # Low-level binary, assembly, and script patches
│   ├── *.asm                  # 65c816 SNES assembly hooks assembled via Asar
│   ├── *.ips                  # Pre-compiled binary IPS patches
│   ├── *.evs                  # Standalone Everscript patch declarations
│   └── *.sliver               # Memory structure definitions
│
├── utils/                     # Utility modules
│   ├── file_utils.py          # File I/O, temporary files, text-to-IPS binary serializer
│   ├── ips_utils.py           # ROM diff generation and IPS patch application
│   ├── ips2asar.py            # Transpiler converting binary IPS patches to Asar ASM
│   ├── patch_utils.py         # Patch loading and dependency resolution
│   ├── out_utils.py           # Output dumping helpers into out/
│   └── process_utils.py       # External CLI process execution
│
├── tests/                     # Automated test harness (pytest)
│   ├── test_lexer.py          # Tokenizer regression tests
│   ├── test_parser_smoke.py   # Parser initialization and conflict validation
│   ├── test_preprocessor.py   # Include and memory preprocessor tests
│   └── test_word.py           # Hex/word literal conversion tests
│
├── docs/                      # Architectural documentation and room reverse-engineering
│   ├── review.md              # Living compiler audit and improvement roadmap (P1-P6)
│   ├── patterns.md            # Cross-room flag patterns, story states, and transitions
│   ├── progress.md            # Room documentation progress tracker (116/116 complete)
│   ├── incremental-compilation.md # Design for dependency graph caching
│   ├── return-feature.md      # Design doc for function return values
│   └── rooms/                 # Detailed documentation of all 116 rooms in the vanilla game
│
├── out/                       # Generated compiler artifacts
│   ├── everscript.ips         # Final generated binary ROM patch
│   ├── patch.txt              # Human-readable annotated assembly with ROM addresses & bytecode
│   ├── patch.clean.txt        # Stripped single-line stream fed into the IPS generator
│   ├── memory_map.txt         # Complete ROM/RAM allocation and free-space report
│   ├── lexer.txt              # Token stream of the main input file
│   └── lexer_include.txt      # Token stream of all transitively included files
│
├── .agents/skills/            # On-demand AI skills for Antigravity, Copilot, and Cursor
└── .github/                   # GitHub Actions workflows and AI references
    ├── memory-map.md          # Authoritative Secret of Evermore RAM map
    ├── compiler-reference.md  # Detailed compiler internals and dump file specs
    └── workflows/             # PyInstaller CI builds for Linux and Windows
```

---

## 3. Core Compilation Concepts

### 3.1 Memory Directives (`#memory(...)`)
Everscript source files declare available ROM and RAM address ranges at the top:
```csharp
#memory(
    string_key(0x0546)..string_key(0x232b),    // ROM text pointers
    function_key(0x0000)..function_key(0x232b),  // ROM script pointers
    0x300000..0x3fffff,                         // Extended ROM free space (1MB)
    <0x2272>..<0x2558>,                         // Persistent WRAM range
    <0x2834>..<0x28ff>                          // Temporary session WRAM range
)
```
The `MemoryManager` in [compiler/linker.py](file:///Users/v/Documents/GitHub/everscript/compiler/linker.py) ensures allocations never cross $64\text{ KB}$ SNES bank boundaries without explicit banking trampolines.

### 3.2 Injection Points (`@inject(...)`)
Functions can overwrite vanilla scripts or hook into ROM routines via address decorators:
```csharp
@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER)
@count_limit(0x20)
fun custom_jungle_enter() {
    // Custom logic
}
```
- `@install()`: Informs the linker to install the function into the patch.
- `@inject(addr)`: Target address where the call or jump hook is placed.
- `@count_limit(N)`: Enforces that the emitted code cannot exceed $N$ bytes, preventing accidental clobbering of neighboring routines.

### 3.3 Patch Merging (`#patch(...)`)
Everscript seamlessly merges low-level `.asm` (via Asar) and `.ips` patches declared via `#patch("name")`. This allows high-level event scripting to coexist with low-level assembly engine hacks (such as input interceptors, weapon charge modifications, and status effect fixes).
