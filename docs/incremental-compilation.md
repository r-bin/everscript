# Incremental Compilation Design

## Status: Draft / Discussion

---

## 1. Current Architecture (Honest Assessment)

### How it works today

```
kaizo.evs (53K lines, single file)
  ├── #memory(...)           → declares available ROM/RAM pools
  ├── #include("in/core.evs") → 16K lines re-lexed/re-parsed inline
  ├── #patch(...)            → external ASM/IPS patches
  ├── group non_maps()       → strings, enemy data, alchemy, armor (~8K lines)
  ├── group custom_bosses()  → (~1.6K lines)
  ├── group helper_global()  → shared runtime (souls system, hotkeys, etc. ~24K lines)
  ├── area intro_screens()   → contains map blocks
  ├── area mini_games()
  ├── ... 19 areas total, 3 standalone maps
  └── group gourd_trap()
```

The compiler (`everscript.py`) does:
1. Read the entire `.evs` file as one string
2. Lex everything (including `#include` which re-lexes `core.evs`)
3. Parse into AST nodes
4. `CodeGen.generate()` links + generates in one pass
5. Output: single IPS patch file

### What's good

- **Simple mental model**: one file in → one patch out.
- **`#include` for `core.evs` already works** like a C header — it's just re-lexed and re-parsed, contributing enums/constants/functions to the global scope.
- **Memory allocation is centralized**: the `MemoryManager` hands out addresses from declared pools. No conflicts.
- **Map variant system works**: multiple maps sharing one map index (e.g., Ebon Keep/Ivor Tower at `0x7b`) are correctly handled because `_generate_map()` sees all of them at once.

### What's not good

- **53K-line monolith**: `kaizo.evs` is unwieldy. You can't navigate it, can't reuse areas across projects, can't version-control individual rooms meaningfully.
- **Full recompile every time**: change one line in one room → re-lex and re-parse 53K + 16K = ~70K lines. On a big project, this adds up.
- **`#include` is expensive**: `core.evs` is re-lexed and re-parsed from scratch every compile. It creates a brand new `Lexer` and `Parser` instance (see `ast_everscript.py` line 1325–1345). There's no caching.
- **No intermediate format**: the compiler goes straight from source → IPS. There's no "object file" to cache or reuse.
- **Linker and codegen are interleaved**: `CodeGen.generate()` calls `self.linker.link_function()` while generating output. There's no clean separation between "resolve addresses" and "emit bytes."
- **Address allocation is order-dependent**: the `MemoryManager` gives out addresses FIFO from pools. Compiling rooms in a different order (or adding a room) shifts *every subsequent address*. This means you can't just recompile one room — its address might have moved, and every cross-reference would break.

---

## 2. The Vision

Model this after C compilation:

| C concept | EverScript equivalent |
|---|---|
| `.h` header | `core.evs` — shared enums, constants, function signatures |
| `.c` source | Each room/area `.evs` file |
| `.o` object file | Compiled room artifact (relocatable) |
| `Makefile` / project file | `kaizo.evs` — memory pools, patches, room list |
| `ld` linker | Final pass that allocates addresses, resolves cross-refs, emits IPS |

### Desired behavior

1. Changing one room recompiles only that room
2. `core.evs` changes → recompile everything (like changing a header)
3. Project-level changes (memory layout, patches) → relink only
4. Each room file is self-contained and testable

---

## 3. The Hard Problems (Why This Isn't Trivial)

### 3.1 Address allocation is global and order-dependent

The `MemoryManager` allocates script ROM space (`0x928000..0x9bffff` and extension banks), string space, string keys, function keys, and RAM from pools — all first-come, first-served.

If Room A compiles first and gets address `0xB08000`, then Room B gets `0xB08042`, removing Room A or changing its size shifts Room B's address. Every `Call` instruction that references Room B's functions by absolute address would break.

**In C terms**: this is like not having relocatable object files. Every `.o` has hardcoded absolute addresses.

### 3.2 Cross-room dependencies

The `group helper_global()` block defines ~24K lines of shared runtime code (souls system, hotkeys, init functions, etc.). Rooms call into this code via `Call(self, function)`, which resolves to absolute addresses at compile time.

If a room is compiled separately, it can't know the address of `default_init_room()` yet — that address depends on how much code came before it in the final layout.

### 3.3 Map variant dispatch is global

`_generate_map()` in `codegen.py` processes ALL maps sharing a map index together. For example, if `ebon_keep_sewers` and `ivor_tower_sewers` both use map index `0x79`, the codegen creates a dispatcher that checks the variant flag (`$2266`) and calls the right `trigger_enter`. This requires seeing both rooms simultaneously.

### 3.4 String deduplication is global

`CodeGen.add_string()` deduplicates: if two rooms use the same string, it allocates it once. Per-room compilation would lose this, wasting string keys (a finite resource: `0x0546..0x232b`).

### 3.5 The "non-maps" aren't rooms

`group non_maps()`, `group custom_bosses()`, `group helper_global()` are not room scripts — they're:
- Direct ROM patches (enemy data tables, alchemy costs, armor values)
- Globally callable utility functions (souls system, death handlers)
- Hotkey handlers injected at fixed addresses

These don't fit the "compile each room separately" model. They're more like a **shared library** that every room links against.

---

## 4. Proposed Architecture

### 4.1 Compilation units

Split the project into these categories:

```
in/kaizo/
├── kaizo.evs              # PROJECT MANIFEST (memory, patches, room directories)
├── kaizo_shared.evs       # non-map code: non_maps, custom_bosses, helper_global
│                          #   (depends on core.evs + kaizo.evs enums)
└── rooms/
    ├── intro_screens.evs  # area with 2 maps
    ├── mini_games.evs     # area with 1 map
    ├── shrine_area.evs
    ├── inbetwixx.evs
    ├── town.evs
    ├── bog.evs            # could group nearby areas
    ├── ...
    └── experimental.evs
```

Each room file:
```
#include("in/core.evs")
#include("in/kaizo/kaizo_shared.evs")

area inbetwixx_center() {
    map inbetwixx(CROSSING) {
        ...
    };
};
```

### 4.2 Two-phase compilation

#### Phase 1: Parse (per-file, cacheable)

Each compilation unit is parsed independently:
1. Parse `core.evs` → symbol table (enums, constants, function signatures)
2. Parse `kaizo_shared.evs` with `core.evs` symbols → shared symbol table + function list
3. Parse each room file with core + shared symbols → room AST + function list + string list + map registrations

**Output per room**: a serializable IR containing:
- List of functions with their bytecode (but **placeholder addresses**)
- List of strings
- List of map trigger registrations
- List of external dependencies (calls to shared functions)
- Memory requirements (how many RAM bytes/flags needed)
- Source hash (for change detection)

#### Phase 2: Link (global, always runs)

The linker sees ALL room IRs + shared IR:
1. **Allocate addresses** from memory pools (deterministic order: shared first, then rooms sorted by name)
2. **Resolve cross-references** (patch placeholder addresses with real ones)
3. **Handle map variants** (generate dispatchers for rooms sharing a map index)
4. **Deduplicate strings** (across all rooms)
5. **Emit final IPS patch**

### 4.3 Change detection (the incremental part)

```
.cache/
├── core.evs.hash
├── kaizo_shared.ir        # cached Phase 1 output
├── kaizo_shared.hash
└── rooms/
    ├── inbetwixx.ir
    ├── inbetwixx.hash
    ├── town.ir
    ├── town.hash
    └── ...
```

On each build:
1. Hash `core.evs` → if changed, invalidate ALL caches (it's a universal header)
2. Hash `kaizo_shared.evs` → if changed, invalidate shared cache (rooms may still be valid if shared only changed function bodies, not signatures — but to keep it simple: invalidate all rooms too)
3. Hash each room file → if changed, re-run Phase 1 for that room
4. Always run Phase 2 (linking is fast since it's just address assignment + byte patching)

### 4.4 The manifest (`kaizo.evs`)

```
#memory(
    string_key(0x0546)..string_key(0x232b),
    function_key(0x0000)..function_key(0x1668),
    ...
)

#patch(
    "assassin_silversheath",
    "save_file_growth",
    ...
)

#shared("in/kaizo/kaizo_shared.evs")

#rooms("in/kaizo/rooms/")
// or explicit:
// #room("in/kaizo/rooms/inbetwixx.evs")
// #room("in/kaizo/rooms/town.evs")
```

---

## 5. What About the Non-Maps?

The non-map code in kaizo falls into distinct categories:

| Category | Example | Where it goes | Why |
|---|---|---|---|
| ROM data patches | enemy stats, armor values, alchemy costs | `kaizo_shared.evs` | Fixed addresses, no relocation needed |
| Globally injected code | hotkey handlers (`@inject(ADDRESS.HOTKEY_START)`) | `kaizo_shared.evs` | Injected at fixed vanilla addresses |
| Shared utility functions | `default_init_room()`, `souls_handle_*()`, death handlers | `kaizo_shared.evs` | Called by rooms, needs stable addresses |
| Room-local code | everything inside a `map`/`area` block | `rooms/*.evs` | Only that room uses it |
| Shared enums/constants | `SOULS_MEMORY`, `CUSTOM_FLAG`, `BUTTON_MAP` | `kaizo_shared.evs` (top) | Referenced by rooms as identifiers |

The key insight: **`kaizo_shared.evs` is both a header (for its enums) and a compilation unit (for its functions).** This is the same as how `core.evs` works today — it defines both constants and installable functions.

### The circular dependency concern

> "rooms are dependant on core.evs and kaizo.evs, which would be a loop"

This is **not** a loop. The dependency graph is a DAG:

```
core.evs (enums, constants, vanilla function signatures)
    ↓
kaizo_shared.evs (project enums + shared functions, depends on core)
    ↓
rooms/*.evs (depend on core + shared, but shared does NOT depend on rooms)
```

Rooms call shared functions. Shared functions do NOT call room functions. This is enforced naturally: shared code can't reference a room's local function because it's not in scope.

If a shared function *did* need to call room-specific code, it would use `reference()` / indirect calls (function keys), which are resolved at link time — not a compile-time dependency.

---

## 6. Implementation Roadmap

### Phase A: Source splitting (no compiler changes)

**Effort**: Low. **Risk**: None.

1. Split `kaizo.evs` into `kaizo.evs` (manifest) + `kaizo_shared.evs` + `rooms/*.evs`
2. `kaizo.evs` uses `#include` to inline everything back together
3. Compilation works exactly as before — just better file organization
4. You can already do this today with the existing `#include`

```
// kaizo.evs
#memory(...)
#include("in/core.evs")
#patch(...)
#include("in/kaizo/kaizo_shared.evs")
#include("in/kaizo/rooms/intro_screens.evs")
#include("in/kaizo/rooms/inbetwixx.evs")
// ...
```

**This is the immediate win**: version control, navigation, and mental model improve dramatically even without compiler changes.

### Phase B: Cache `core.evs` parsing

**Effort**: Medium. **Risk**: Low.

The `Include` class (ast_everscript.py line 1319) currently creates a fresh `Lexer` and `Parser` for each `#include`. Caching the parsed symbol table of `core.evs` (keyed by file hash) avoids re-parsing 16K lines every compile.

This requires serializing the scope/symbol state after parsing `core.evs` — which means making the AST nodes serializable (e.g., with `pickle`).

### Phase C: Relocatable IR + two-phase build

**Effort**: High. **Risk**: Medium.

This is the real incremental compilation. Requires:

1. **IR format**: Define a serializable intermediate representation for compiled functions (bytecode with placeholder addresses)
2. **Separate `CodeGen.generate()` into `compile()` and `link()`**: compile produces IR, link resolves addresses
3. **Deterministic address allocation**: rooms must be assigned addresses in a fixed, deterministic order so that adding a room doesn't shift existing ones (e.g., sorted by name, or by explicit ordering in manifest)
4. **Relocation table**: each IR records which bytes need patching with final addresses

### Phase D: Parallel compilation

**Effort**: Medium (after Phase C). **Risk**: Low.

Once rooms are independent compilation units, they can be compiled in parallel (`multiprocessing.Pool`). Each room only needs the symbol tables from core + shared, not any mutable state.

---

## 7. Honest Assessment: Is This Worth It?

### Compile time today

The project is ~70K lines total (kaizo + core). On modern hardware with Python + rply, this likely takes 2–10 seconds. The question is whether incremental compilation saves enough time to justify the compiler refactor.

**If compile time is under 5 seconds**: Phase A (source splitting) gives you 90% of the quality-of-life improvement. Stop there.

**If compile time is 10+ seconds**: Phase B (caching core.evs) probably halves it. Worth doing.

**If you have 50+ rooms and compile time is 30+ seconds**: Phase C is justified.

### What I'd actually recommend

1. **Do Phase A now.** It's purely organizational and immediately improves the project. No compiler changes. Each room becomes a self-contained file that `kaizo.evs` includes.

2. **Measure compile time.** Add timing to each phase (lex, parse core, parse shared, parse rooms, generate, link). Find where time actually goes.

3. **Do Phase B if core.evs parsing is the bottleneck.** It probably is — 16K lines re-lexed + re-parsed is expensive, and it never changes during a session.

4. **Defer Phase C until you actually need it.** The compiler refactor is substantial and risky. The current architecture works; it's just not optimized for incremental builds.

### Risk: Address stability

The biggest risk with incremental compilation is address instability. In the SNES ROM hack context, if you distribute a save file that has function key indices baked in, and then recompile with different addresses, the save breaks. Today's monolithic compile guarantees deterministic output. A two-phase system needs to be equally deterministic, or you'll get subtle bugs.

---

## 8. Concrete File Layout After Phase A

```
in/kaizo/
├── kaizo.evs                    # manifest: memory, patches, includes
├── kaizo_shared.evs             # non-map code (was: groups before maps)
│   ├── group non_maps()         #   strings, enemy data, alchemy, armor
│   ├── group custom_bosses()    #   boss AI modifications
│   └── group helper_global()    #   souls system, hotkeys, init, death, etc.
│       ├── group souls()
│       ├── group hotkeys()
│       └── group init()
└── rooms/
    ├── intro_screens.evs        # area intro_screens: intro_1, intro_2
    ├── mini_games.evs           # area mini_games: hacking minigame
    ├── shrine_area.evs          # area shrine_area
    ├── inbetwixx_center.evs     # area inbetwixx_center: inbetwixx map
    ├── north_inbetwixx.evs
    ├── west_inbetwixx.evs
    ├── altus_plateau.evs
    ├── northwest_inbetwixx.evs
    ├── east_inbetwixx.evs
    ├── southern_jungle.evs
    ├── town.evs                 # area town + standalone maps
    ├── bog.evs                  # bog_curve, bog_bridges, bog_crossing
    ├── ship_caves.evs
    ├── desert_bug.evs
    ├── metro.evs
    ├── dungeon_isaac.evs
    ├── dungeon_volcano.evs
    ├── dungeon_podunk.evs
    ├── experimental.evs
    └── gourd_trap.evs           # group gourd_trap
```

The new `kaizo.evs`:
```
#memory(
    string_key(0x0546)..string_key(0x232b),
    function_key(0x0000)..function_key(0x1668),
    function_key(0x1986)..function_key(0x1B78),
    function_key(0x4D79)..function_key(0x4D79 + (0d3 * 0d200)),
    0x300000..0x3fffff,
    <0x2267>..<0x22D9>,
    <0x22dd>..<0x22e9>,
    <0x236D>..<0x2378>,
    <0x253d>..<0x2558>,
    <0x2463>..<0x2500>,
    <0x2834>..<0x2890>
)
#include("in/core.evs")

#patch(
    "assassin_silversheath",
    "assassin_bazooka_ammo",
    "assassin_bazooka_charge",
    "save_file_growth",
    "no_alchemy_xp",
    "temp_jaguar_ring(!ROM_EXTENSION=$FE6000)",
    "debug_menu__generic(!ROM_EXTENSION=$FE0000)",
    "_hook_input(!ROM_EXTENSION=$FE5000)",
        "hotkeys(!ROM_EXTENSION=$FD0000, !ROM_HOOK=$FE5000, !WITH_HOTKEY_B=0)",
    "menu_close",
    "five_status_effects_fix(!ROM_EXTENSION=$FE7000)",
    "scale_enemies(!ROM_EXTENSION=$FE8000, !WITH_DEBUG_PALETTE=0)",
    "scale_boy(!BOY_HP_INCREMENT=3, !DOG_HP_INCREMENT=3, !BOY_ATTACK_INCREMENT=1, !BOY_ATTACK_DIVISOR=2)",
)

// shared code (non-room code)
#include("in/kaizo/kaizo_shared.evs")

// rooms
#include("in/kaizo/rooms/intro_screens.evs")
#include("in/kaizo/rooms/mini_games.evs")
#include("in/kaizo/rooms/shrine_area.evs")
#include("in/kaizo/rooms/inbetwixx_center.evs")
#include("in/kaizo/rooms/north_inbetwixx.evs")
#include("in/kaizo/rooms/west_inbetwixx.evs")
#include("in/kaizo/rooms/altus_plateau.evs")
#include("in/kaizo/rooms/northwest_inbetwixx.evs")
#include("in/kaizo/rooms/east_inbetwixx.evs")
#include("in/kaizo/rooms/southern_jungle.evs")
#include("in/kaizo/rooms/town.evs")
#include("in/kaizo/rooms/bog.evs")
#include("in/kaizo/rooms/ship_caves.evs")
#include("in/kaizo/rooms/desert_bug.evs")
#include("in/kaizo/rooms/metro.evs")
#include("in/kaizo/rooms/dungeon_isaac.evs")
#include("in/kaizo/rooms/dungeon_volcano.evs")
#include("in/kaizo/rooms/dungeon_podunk.evs")
#include("in/kaizo/rooms/experimental.evs")
#include("in/kaizo/rooms/gourd_trap.evs")
```

---

## 9. Future: Directive-Based Manifest

If Phase C is ever implemented, `kaizo.evs` could evolve from `#include` chains to a proper manifest:

```
#memory(...)
#patch(...)

#shared("in/core.evs")
#shared("in/kaizo/kaizo_shared.evs")

#rooms("in/kaizo/rooms/")   // auto-discover all .evs files
// or:
// #room("in/kaizo/rooms/inbetwixx_center.evs")
// #room("in/kaizo/rooms/town.evs")
```

Where `#shared` means "parse once, make symbols available to all rooms" and `#rooms` means "compile each file as an independent unit, link together at the end."

But this requires the Phase C compiler refactor. Until then, `#include` chains are the pragmatic choice.

---

## 10. Open Questions

1. **Ordering**: Does the order rooms appear in the final output matter for gameplay? (e.g., do save files reference function key indices that would shift?)
2. **Compile time measurement**: What's the actual bottleneck today — lexing, parsing, codegen, or linking? Measure before optimizing.
3. **Area grouping**: Should each area be its own file, or should small related areas be grouped? (e.g., all bog areas in one `bog.evs`?)
4. **Shared function stability**: If `kaizo_shared.evs` changes, do ALL rooms need recompilation? Or only rooms that call the changed function? (The simple answer is "all rooms" — the precise answer requires dependency tracking per-function, which is Phase D complexity.)
