# The Ideal Secret of Evermore Map Editor

A design document for a visual room editor for this project. This is a proposal, not a build log — nothing here is implemented in the `everscript` repo. It exists to settle the shape of the tool before writing it, the way `docs/map_encoding.md` settled the byte format before `tools/encode_room.py` was written.

Two requirements shape everything below, and they pull in different directions:

1. **It should eventually work on other SNES action-RPGs** — Secret of Mana and Terranigma are the named targets. Neither has anything like Everscript's compiled bytecode VM, so a design built around "jump from a trigger to its script" (this game's one truly distinctive need) cannot be the foundation — it has to be an optional capability on top of something more general.
2. **Tiling and layers are the hard part.** Not a UI-polish afterthought — the genuinely difficult design problem, and where most of this document's effort goes (§9).

**A third thing shapes it that wasn't known when this document was first drafted: this isn't a greenfield decision.** `/Users/v/Documents/GitHub/everscript-vscode` is an existing, actively-developed VS Code extension for this exact project, with its own architectural constitution (`AI_ARCHITECTURE_GUIDE.md`), a partial room/trigger inspector already shipping (`src/rooms/`), a partial independent attempt at decoding the ROM's map format in JavaScript (`src/maps/`, documented incomplete), and — unexpectedly — an already-forked, already-embedded SNES emulator core built specifically for debugger integration. §2 covers what was found there and how it changes this document's recommendations; every section after it was revised in light of it, not written as if it didn't exist.

**Status of the Secret-of-Evermore-specific prerequisites:** unusually for a romhacking project, the hard part is already done, and it's done in `everscript` (this repo), not `everscript-vscode`. `tools/dump_room.py` and `tools/encode_room.py` give a byte-exact, round-trip-verified read/write path for every one of the 127 vanilla rooms (`docs/map_encoding.md`); `tools/collision.py` decodes the full collision bitfield instead of guessing at it (`docs/map_collision_mechanics.md`); `tools/cuttable_grass.py` decodes the metatile swap table (`docs/cuttable_grass_mechanics.md`); `tools/render_map.py` already draws every one of those as a composited PNG. An editor is a UI wrapped around tooling that already exists and is already tested — see `docs/map_editor_architecture_and_limitations.md` §6 for the up-to-date completeness table.

---

## 1. What already exists, and why it changes the plan

### 1.1 `everscript-vscode` — this project's own extension

This is the most relevant prior art in this whole document, more relevant than any external project, because it's already built for this exact game, already has real users (presumably), and already made a set of architectural commitments a new subsystem has to either follow or explicitly break from.

**What it already has, relevant to a map editor:**

| Capability | Where | Status |
|---|---|---|
| Full Everscript language tooling — hover docs, go-to-definition, find-references, completions, an Outline provider over `fun`/`map`/`area`/`group`/`enum`/`val` declarations | `src/language/` | Shipping |
| A Debug Adapter Protocol implementation for stepping through `.evs` scripts | `src/debugger/` | "Mock" runtime today (`src/debugger/adapter.js` / `mock-runtime.js`), not yet driving real hardware state |
| A ROM-backed room/trigger inspector: parses `.evs` `map`/`area` blocks, cross-references ROM headers and trigger tables, renders an SVG overlay of entrances/enemies/step-on/B-triggers on top of a static image | `src/rooms/` | Shipping, **read-only** — no ROM write path exists anywhere in this subsystem (checked directly: no `writeFile`/save call in `src/rooms/` or `src/maps/`) |
| A JS-native disassembler for room trigger bytecode — reads the map pointer table, trigger tables, and opcodes straight from ROM bytes and produces readable pseudo-instructions | `src/emulator/room-script-model.js` | Shipping — this is a from-scratch JS reimplementation of roughly what SoETilesViewer's `script_all` dumper does (§1.2), used to populate the Rooms tab's "ROM script cards" |
| An independent, from-scratch attempt at decoding the room tilemap/graphics payload in JavaScript | `src/maps/` (`map-pipeline-model.js`, `map-blob-evidence-model.js`, `render-script-model.js`) | **Documented incomplete** in `docs/map-renderer-status.md`: works for rooms `0x33`, `0x34`, `0x51`, `0x5c` under a heuristic "sentinel"/`strict7`/`short6` model; explicitly states **room `0x38` does not parse** under that model at all |
| An embedded SNES emulator core running inside a VS Code webview, with a fork built specifically for debugger hooks | `src/emulator/core/snes9x2005-wasm*` | Shipping — see §1.1.2 |
| An existing pattern for invoking this project's Python compiler from the extension host | `src/extension.js` (`child_process.spawn`, ~line 836), `src/shared/config.js` (`pythonPath`, `compilerPath`) | Shipping — resolves `.venv/bin/python3` and spawns `everscript.py` for the "Build and Run in Emulator" command |

#### 1.1.1 The `src/maps/` finding is the single most load-bearing fact in this section

`docs/map-renderer-status.md` (in `everscript-vscode`) is explicit and honest about its own state: header parsing and trigger tables work, but the tilemap payload decode is a heuristic "sentinel scan" that succeeds on four small/simple rooms and fails on `0x38` — **the exact room this project's own `docs/map_decompression_trace_analysis.md`, `docs/map_encoding.md`, and the Mesen2-trace-verified `tools/dump_room.py`/`encode_room.py` fully and byte-exactly solve**, in both directions, with a 127/127-room verified test suite behind it.

This is not a criticism of that effort — reverse-engineering a custom 2D Markov bitstream and an LZSS variant from scratch, in a second language, without the trace evidence this repo's own work was built on, is genuinely hard, and getting four rooms right is real progress. But it's decisive evidence for one specific decision this document has to make: **the ROM tilemap format should not be decoded a second time in JavaScript.** It's already been decoded once, correctly, with proof (`docs/map_encoding.md` §4), and a second independent implementation — in a different language, without that proof — is how a project ends up with two decoders that quietly disagree on room `0x38`. §5 makes this concrete: the map editor's decode/encode layer is the Python tooling that already works, called from the extension, not reimplemented inside it.

#### 1.1.2 The emulator finding resolves an open question from an earlier draft

An earlier draft of this document flagged "whether Mesen2 (or any emulator) exposes an API suitable for live preview" as unverified and deferred it to a later phase. It doesn't need to be deferred:

- `.gitmodules` in `everscript-vscode` pins two forks of `snes9x2005-wasm`: `r-bin/snes9x2005-wasm` on branch `feature/vscode-debugger-integration`, and a vanilla comparison fork. `r-bin` is this project's own maintainer — this is a **first-party fork, built specifically to hook a WASM SNES core into this exact extension's debugger.**
- `tests/debugger/emulator-health.test.js` documents that the integration has already moved *past* an earlier attempt at wrapping the general-purpose EmulatorJS project (`docs/emulator-integration.md`, now stale) to loading the Emscripten-compiled core directly, specifically because the general-purpose wrapper added complexity the direct approach didn't need.
- This core is proven to load inside VS Code's sandboxed webview today, for the "Open Emulator Panel" / "Build and Run in Emulator" commands.

So the live-preview and behavioral-testing question from an earlier draft's §8.2 has a concrete, already-half-built answer: **extend the existing debugger-integration fork**, not "automate pushing ROMs into an external emulator" and not "embed a second, unrelated emulator." §7 revises the live-preview section on this basis.

### 1.2 SoETilesViewer

Already covered in depth earlier in this project's own reverse-engineering work (`.github/skills/soetilesviewer/SKILL.md`), and confirmed again directly against its source (`SoETilesViewer.pro`, `README.md`) for this document: **Qt5/C++, built with `qmake` or Qt Creator.** Genuinely cross-platform in principle (Qt runs on all three major desktops), but it's a traditional native desktop widget app with its own build toolchain — not something a contributor gets "for free" the way a VS Code extension is already running the moment they open this repo's folder.

Its actual relevance here is narrower than a UI/architecture model, and mostly already realized:

- It documents (and its skill file states outright) that it **cannot decode room tilemap layouts** — no Block 1/3 LZSS, no delta accumulator, no Markov decoder, no 3-slice planar table. It's a viewer for isolated 16×16 background tiles, sprites, and character/monster stat tables, plus the `SoEScriptDumper` companion tool that disassembles script bytecode into `script_all`.
- `everscript-vscode`'s `OPCODE_REGISTRY` (`room-script-model.js`) is already, in effect, a JS-side reimplementation of what `SoEScriptDumper` does for trigger scripts specifically — so the actual useful content from SoETilesViewer (its opcode tables, its ROM resource-table offsets) has already been carried forward into the ecosystem once. There's no indication a second import of that same information is needed.
- Its Qt widget architecture (a `mainwindow.cpp` orchestrating docked panels) is a reasonable, ordinary desktop-app pattern, but it doesn't answer anything this document's actual open questions are about (cross-language IPC, webview canvas performance, script-to-ROM linking) — those are specific to the constraints introduced by choosing VS Code as the shell, which SoETilesViewer never had to solve.

**Conclusion:** valuable as a historical format reference (already mined once), not a model to follow for the editor's own architecture.

---

## 2. Frameworks and languages

Answered directly, since it was asked directly, and grounded in what `everscript-vscode` has already committed to rather than proposed fresh — building a second, differently-opinionated JS codebase next to an existing one is its own maintenance cost, and nothing found while researching this section justifies paying it.

| Layer | Choice | Why |
|---|---|---|
| **ROM format logic** (decode/encode, collision, cuttable grass, object packing) | **Python**, already written — `tools/dump_room.py`, `encode_room.py`, `collision.py`, `cuttable_grass.py` | Already exists, already byte-exact-verified for 127/127 rooms. §1.1.1's finding is the direct argument against re-deriving this in JS: it's already been tried once, in this exact ecosystem, and it stalled on the hardest room. |
| **Extension host** | **Plain JavaScript**, CommonJS, targeting what `everscript-vscode`'s own `tsconfig.json` already targets (ES2020, `allowJs`, `checkJs: false`, `strict: false`) | Matches the existing codebase byte-for-byte rather than introducing TypeScript as a second convention next to it. `AI_ARCHITECTURE_GUIDE.md` §2.1–2.5's file-size limits, single-state-ownership rule, and directional dependency graph (`parser → model → renderer → UI`) apply to a new map subsystem exactly as they apply to `rooms/` and `debugger/` today. |
| **Webview UI** | **Vanilla JS + HTML5 `<canvas>`**, no framework | `src/rooms/webview/` and `src/emulator/webview/` are both already framework-free (hand-built HTML strings and DOM calls). `AI_ARCHITECTURE_GUIDE.md` §2.5, "Anti-Abstraction," explicitly forbids the kind of abstraction pyramid a React/Vue/Svelte integration would add for one panel. A tilemap canvas is squarely inside what raw Canvas 2D already does well; nothing here needs a component framework. |
| **Extension ↔ Python IPC** | **Newline-delimited JSON over stdio**, hand-rolled, via `child_process.spawn` | The `everscript` repo's `dependencies: []` (zero runtime npm packages) is a deliberate posture, matching `AI_ARCHITECTURE_GUIDE.md`'s aversion to "giant shared helpers" and "abstraction pyramids." A JSON-RPC library is an unnecessary dependency for a protocol this simple, and `child_process.spawn` invoking a Python entry point is *already the established pattern* (`src/extension.js` ~line 836, spawning `everscript.py`) — a map-server is the same mechanism, long-lived instead of one-shot. |
| **Emulator core** | The existing **`snes9x2005-wasm`** fork (`r-bin/snes9x2005-wasm`, `feature/vscode-debugger-integration` branch), Emscripten/WASM, loaded directly (not via a general wrapper) | Already built, already proven inside this exact webview sandbox, already has debugger-hook intent baked into the branch it lives on (§1.1.2). |
| **Tests, Python side** | **pytest**, already in use — `tests/integration/maps/` (143 passing) | No change; a map-server is a thin RPC shell around already-tested code, and its own tests should extend that suite (§8). |
| **Tests, JS side** | The existing hand-rolled `assert`-based `test()` runner (see any `tests/*.test.js` in `everscript-vscode`) | No Jest/Mocha/Vitest is in use anywhere in that repo today; introducing one for a single new subsystem breaks the "one way to do things" property a small codebase depends on. |

The one place this table diverges from "just copy what's already there" is the ROM format logic staying in Python rather than following `everscript-vscode`'s all-JS convention — and that divergence is the direct, evidence-based conclusion of §1.1.1, not a stylistic preference.

---

## 3. Platform: extend `everscript-vscode`, don't start a second extension

An earlier draft of this document spent real effort arguing "VS Code extension vs. a native cross-platform app," using yaze (C++23/ImGui, genuinely cross-platform natively) as the counter-example to "only Electron/VS Code gets you cross-platform for free." That argument is now moot for a more direct reason: **the VS Code extension for this project already exists**, already has users, already has a debugger, a language server's worth of tooling, and a room inspector. The question isn't "should this be a VS Code extension" anymore — it's "does the map editor live inside `everscript-vscode`, or as a second extension next to it," and the answer is the first one, for the same reason argued before but stronger: a second extension means two activation lifecycles, two settings surfaces, and a room inspector (`src/rooms/`) that would need to either stay a read-only toy forever or be rebuilt inside the new extension anyway, duplicating work that's already shipped.

**Concretely:** a new top-level subsystem directory, sibling to `debugger/`, `rooms/`, `emulator/`, `language/` — call it `src/map-editor/` or fold the write-capable pieces into `src/rooms/` directly once it has somewhere to write to. Either way, it inherits `AI_ARCHITECTURE_GUIDE.md`'s existing rules rather than writing new ones: the directional dependency graph gets a new terminus (`rom-readers` becomes `rom-readers` *and* `rom-writer`, both read-only-from-VS-Code's-perspective since the actual mutation happens in the spawned Python process), and the subsystem-isolation rule (`rooms` may read ROM via `rom-readers` but not call `debugger`) extends naturally to "map-editor may call the map-server but not call `debugger` directly either."

If a genuinely different shell is ever wanted for a future non-Everscript game (§4), that's a second frontend against the Python backend described in §5 — not a rewrite of it, and not a reason to delay building inside `everscript-vscode` now.

---

## 4. A shared data shape, not a plugin system

The multi-game goal (Secret of Mana, Terranigma) still needs an answer, and an earlier draft's answer — a `GamePlugin` interface with a runtime registry — directly contradicts `AI_ARCHITECTURE_GUIDE.md` §2.5's explicit, named prohibition: *"Forbidden patterns: … dependency injection systems, registries."* That's not a minor style note in that document; the whole section is framed as "prefer duplication over coupling." The plugin idea needs correcting to fit, and the correction turns out to be more honest about how this space actually works anyway:

**There is no plugin loader.** A second game gets its **own map-server entry point** — a new small Python module (or, if it ever needs to live entirely outside this repo, a new sibling repo altogether, the way `everscript-vscode` already sits next to `everscript`) that implements the same *shape* of response the "soe" server returns, because that shape is documented (below), not because both implementations share a base class or get discovered through a registry. This is "duplication over coupling" applied literally: the SoE server and a hypothetical SoM server are two files that happen to agree on a JSON shape, with no runtime relationship to each other at all. Nothing yaze, Tilemap Studio, or any tool surveyed in §6 actually does differently, once you look past marketing language like "plugin architecture" — yaze doesn't support Zelda-3-shaped edits to a different game either; genericity in this space lives at the level of "the same *kind* of tool, rebuilt per game," not a live extensibility mechanism.

**The shared shape** — call it a `RoomModel`, returned by any server's `open_room` — is a normalized structure the webview renders generically:

```
RoomModel:
    width, height: int             # in the server's own tile units
    layers: [Layer]                # see below -- described by *kind*, not by name
    triggers: [Trigger]            # empty list if the game/room has none
    objects: [PlacedObject]
    metadata: dict                 # anything server-specific the UI treats as opaque
```

Each `Layer` declares a **kind**, and the webview ships one generic editing tool per kind — written once, reused by any server whose `RoomModel` includes a layer of that kind:

| Kind | Data shape | Generic tool | SoE example |
|---|---|---|---|
| `grid` | 2D array of tile/metatile references into a per-room palette | Paint / stamp / rectangle-select, with the palette browser from §9.2 | Layer 1 (canopy), Layer 2 (terrain) |
| `bitfield-grid` | 2D array of small structured values, each with named sub-fields | A property-inspector-driven brush (§9.1) — pick field values, not raw numbers, but the raw value is always visible | Collision words (plane, drift, gate, geometry) |
| `boxes` | A list of axis-aligned rectangles, each with typed metadata | Drag-to-place / drag-to-resize, with a metadata panel per box | B-triggers, step-on triggers |
| `stamped-objects` | A list of placed, possibly multi-state objects with a footprint and a graphic | Click-to-place from a catalog, with a state scrubber (§9.3) | Section 3 objects (gourds, bridges, sewer gates) |

A server for a game with no scripting layer simply never emits a `boxes`-kind layer with script metadata attached — the generic `boxes` tool still works for, say, enemy spawn zones, because the tool only ever knew about rectangles and typed metadata, never about Everscript specifically. This is what makes §8 (script integration) an optional capability layered on top of the `boxes` tool rather than baked into it: the tool renders and edits boxes; a separate, SoE-specific panel adds "and here's the script this box's `scriptId` metadata field points to" only when talking to a server that happens to return that field.

If a Secret of Mana server needs a `Layer` kind not in this table, that's real, welcome vocabulary growth — a sign the shape is doing its job by being extended, the same way a second game's ROM format is expected to teach this project things the first one didn't. What would indicate the design is wrong is a server needing to reach past this JSON shape into VS Code-specific or SoE-specific code to be renderable at all; that should never be necessary. `smkerz/secret-of-mana-hacking` (§6) is the natural starting point for that server whenever it's undertaken — not reviewed in depth for this document.

---

## 5. Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  everscript-vscode                                                │
│  ┌───────────────────────┐   ┌─────────────────────────────────┐│
│  │ New subsystem, e.g.    │   │ Normal editor tabs (.evs)        ││
│  │ src/map-editor/        │   │  - opened by "Jump to Script"    ││
│  │  - Custom Editor       │   │    (only when the "soe" server   ││
│  │    Provider for rooms  │   │    reports script metadata,      ││
│  │  - spawns/owns the     │   │    §8)                           ││
│  │    map-server process, │   └─────────────────────────────────┘│
│  │    same child_process  │                                       │
│  │    pattern already     │                                       │
│  │    used for everscript.py                                      │
│  │    (src/extension.js ~836)                                     │
│  └──────────┬────────────┘                                       │
│             │ postMessage                                        │
│  ┌──────────▼────────────┐                                       │
│  │ Webview (room canvas) │  generic Layer-kind renderer + tools   │
│  │  HTML5 canvas,        │  (§4, §9) -- no SoE-specific code,     │
│  │  vanilla JS           │  matching src/rooms/webview's existing │
│  │                       │  framework-free style                  │
│  └───────────────────────┘                                       │
└─────────────────┬─────────────────────────────────────────────────┘
                   │ newline-delimited JSON over stdio
┌─────────────────▼─────────────────────────────────────────────────┐
│  everscript map-server  (Python, long-lived process, lives in the  │
│  everscript repo, not everscript-vscode)                           │
│   - wraps tools/dump_room.py, encode_room.py, collision.py,        │
│     cuttable_grass.py -- no new decode/encode logic, this is a     │
│     thin RPC shell around code that is already tested              │
│   - retires the decode responsibility of everscript-vscode's own   │
│     src/maps/ (§1.1.1); that subsystem's ROM-header/trigger-table  │
│     reading is still useful and can stay, but tilemap payload      │
│     decode should come from here instead of the sentinel model     │
└─────────────────────────────────────────────────────────────────┘
```

### 5.1 The Custom Editor Provider

VS Code's [Custom Editor API](https://code.visualstudio.com/api/extension-guides/custom-editors) lets an extension register itself as the editor for a file type — double-click, get the visual editor instead of a hex dump. There is no natural "room file" in this ROM (rooms are byte ranges inside one `.smc`), so the provider is registered against a **virtual document scheme** (`soe-room:0x38`) rather than a real file, opened via a command ("Open Room…", a room picker, or a gutter action from a trigger's `.evs` source — see §8.3). This is the same mechanism a hex editor or image previewer extension uses; it is not exotic.

### 5.2 The map-server process

**Why a long-lived process instead of shelling out per-edit:** `dump_room()` re-parses and fully decompresses a room's Markov grid and LZSS blocks from scratch — cheap once (the whole 127-room sweep in `tests/integration/maps/` runs in seconds), too slow to pay on every mouse-drag if invoked as a fresh subprocess per tile paint. A server process holds one room's decoded `RoomModel` in memory, mutates it in response to edits, and only calls into `rebuild_model()`/`write_room_into_rom()` when the user saves.

**Surface (illustrative, not final):**

```
open_room(room_id)              -> RoomModel (§4), with derived data already
                                    computed (collision.planes_used, drift
                                    vectors, cuttable_grass tiles)
edit_layer(layer_id, op)        -> op is shaped by the layer's kind (§4):
                                    set_cell(x, y, value) for grid/bitfield-grid,
                                    add/edit/delete_box for boxes,
                                    add/edit/delete_object for stamped-objects
validate()                      -> runs the same checks
                                    tests/integration/maps/test_encode_room.py
                                    runs (ascending-metatile-order, invariant
                                    checks) and returns friendly errors
                                    instead of a raised exception
render(layer_ids)                -> a PNG for the webview, generated by the
                                    existing tools/render_map.py renderer
save()                          -> rebuild_model() + write_room_into_rom(),
                                    reports the new blob size and whether it
                                    fit in place or was relocated
```

Every one of these is a thin wrapper. The server adds no new ROM-format knowledge; it is strictly a JSON face on `tools/*.py`, which is what keeps this proposal small — the risk in a map editor is almost always the format decoding, and that risk is already retired for this game.

---

## 6. External prior art (condensed)

Kept for the design lessons that don't come from this project's own ecosystem, and demoted below §§1–5 because none of it turned out to be as directly load-bearing as what was already sitting in `everscript-vscode`.

| Tool | Game | Stack | Cross-platform | Transferable idea |
|---|---|---|---|---|
| [yaze](https://github.com/scawful/yaze) | Zelda 3 | C++23, ImGui, built-in SNES emulator, CLI companion (`z3ed`) | Yes, natively | Core-plus-multiple-frontends (desktop, CLI, WASM preview) — the same shape §3/§5 land on independently |
| [ZScream](https://github.com/Zarby89/ZScreamDungeon) | Zelda 3 | — | Windows | Open source displacing a closed-source incumbent (Hyrule Magic) — the same pattern SMEDIT and this document's overall goal follow |
| [Tilemap Studio](https://github.com/Rangi42/tilemap-studio) | Multi-console | C++, FLTK | Yes | Closest existing precedent for "one generic tile/layer editor, several formats" |
| SMILE → [SMEDIT](https://github.com/kennycason/super_metroid_editor) | Super Metroid | Kotlin, Compose Multiplatform | Yes | A from-scratch cross-platform rewrite of an old Windows-only tool; considered and not chosen here specifically because it has no equivalent of `everscript-vscode` to build on |
| Lunar Magic | SMW | Win32 | No | Map16 — reuse a pre-built palette of blocks instead of painting raw tiles; §9.2 explains why SoE gets this for free from its own ROM format |
| RainbowZ Editor, Temporal Flux, TerraCraft, Hyrule Magic, hackofmana.com's SoM editor | DKC1, Chrono Trigger, Terranigma, Zelda 3 (old), Secret of Mana | Various, closed | No | Named for completeness; not open, nothing to inspect |
| [secret-of-mana-hacking](https://github.com/smkerz/secret-of-mana-hacking) | Secret of Mana | — | — | Early room/world-map compression research; the starting point for a future SoM server (§4), not reviewed in depth here |

---

## 7. Live preview and emulator integration

Revised entirely from an earlier draft, which treated this as an open question ("does Mesen2 have an API?"). It doesn't need to be: §1.1.2 found a first-party fork already built for exactly this.

**Static room geometry** (what a room looks like, independent of gameplay behavior) doesn't need an emulator at all — `tools/render_map.py` is already a from-scratch, verified, pure-Python **PPU-only** renderer (Mode 1 compositing, no CPU emulation), and that's what `render()` in §5.2 already uses. This covers everything in §9's editing surface.

**Gameplay behavior** (the weapon-hitbox interaction that drives cutting grass, drift physics, NPC AI, script execution) is a different problem, and this is where `everscript-vscode`'s `snes9x2005-wasm` fork on `feature/vscode-debugger-integration` matters: rather than automating an external emulator (an earlier draft's proposal) or embedding a second, unrelated one, the map editor's "test this edit live" feature should be built as an extension of that already-in-progress debugger integration — load the edited ROM (post-`save()`) into the same embedded core, and use whatever state-inspection hooks that fork already provides (or is being built to provide) rather than inventing a second mechanism next to it. This wasn't knowable from outside the project; it's a direct benefit of the map editor and the debugger sharing one host extension (§3) instead of being separate tools that happen to both touch ROMs.

What isn't yet known, and is worth checking before this is scoped as a phase: exactly what the `feature/vscode-debugger-integration` branch currently exposes versus what it's aiming toward — this document's research went as far as confirming the fork exists and why it replaced the EmulatorJS-wrapper approach, not as far as reading its diff against upstream `snes9x2005-wasm` in detail.

---

## 8. Script integration (an optional capability)

Secret of Evermore's distinctive need, not a universal one — §4 already established that it's layered on top of the generic `boxes` tool rather than built into it.

### 8.1 What already exists

Two separate halves of this problem exist today, in two different places, and neither is the other:

- **Disassembling a trigger's compiled script from raw ROM bytes** is already solved, twice: once in C++ by SoETilesViewer's `SoEScriptDumper` (`script_all`), and again independently in JavaScript by `everscript-vscode`'s `room-script-model.js` (`OPCODE_REGISTRY`), which is what powers the Rooms tab's "ROM script cards" today. Both work on any compiled bytecode, vanilla or custom, because they operate on bytes, not source.
- **Mapping a compiled bytecode address back to the `.evs` source file and line that produced it** does not exist anywhere in either repo. This is the actual gap, and it's specific to *this project's own custom scripts* — vanilla, unmodified triggers have no `.evs` source to map to in the first place, so the disassembly above is already the right (and only possible) answer for them.

### 8.2 The gap: no source map

Everscript's compiler pipeline (`compiler/linker.py`, in `everscript`) already produces `out/patch.txt`, an address-annotated bytecode listing — but nothing today records the mapping from a compiled bytecode address back to a `(file, line)` in the `.evs` source that produced it. This is the one piece of new work this design depends on that isn't already built somewhere in the ecosystem:

**Proposed addition:** the linker emits `out/source_map.json` — `{address: {file, line}}` — built from information the compiler already tracks internally while emitting bytecode (every AST node it lowers already knows its source position). This is additive to the existing pipeline, not a redesign of it: `docs/incremental-compilation.md` and `docs/return-feature.md` are the precedent for documenting a compiler change like this before building it.

With that map, "jump to script" for a trigger becomes: look up `script_id` in `source_map.json` → if found, open the `.evs` file at that line in a normal VS Code tab; if not found (a vanilla, uncompiled room), fall back to the disassembly `room-script-model.js` already produces, labeled clearly as disassembly rather than source. This mirrors the project's own vanilla-vs-custom distinction (`AGENTS.md` §2.4) rather than blurring it.

### 8.3 The reverse direction

Given `source_map.json`, the inverse falls out for free: a CodeLens or gutter icon in an open `.evs` file, on any line that calls `loot()`, sets a B-trigger, or otherwise addresses a room, linking back to "Open Room 0x38 at this trigger." This is what makes the tool feel like one editor instead of a map tool that happens to sit next to a text editor.

---

## 9. Tiling and layers, made easy

This is the part flagged as genuinely hard, and it deserves a direct answer rather than a features list. Four separate things make SNES tile/layer editing hard, and each has a specific answer below.

### 9.1 Hard part 1: more than two layers overlap the same coordinates

Secret of Evermore isn't just Layer 1 over Layer 2 — `tools/collision.py` decodes up to **four elevation planes occupying the identical (x, y) grid**, plus plane-transparency, plus forced-walkable drift tiles, plus entity-specific gates, all in the *same* collision word (`docs/map_collision_mechanics.md`). A single flat canvas showing "the" collision at a coordinate is actively wrong for a bridge tile, which has different geometry depending on which plane the entity asking is on.

**Answer: plane is a view filter, not a separate document.** The room is one canvas; a plane selector changes which plane's geometry the collision layer evaluates and draws solid, while other planes present at that tile are ghosted (dashed outlines), matching what `render_full_composition()` already does for the static PNG export. This generalizes past SoE: any `bitfield-grid` layer (§4) whose values encode more than "solid/open" gets the same treatment.

The ordinary Layer 1 / Layer 2 case is not hard by comparison — visibility toggles plus an active-layer selector, the same pattern every image editor and every tool in §6 already uses. No reason to reinvent that particular wheel.

### 9.2 Hard part 2: metatile palettes are large and painting individual 8×8 tiles is tedious

This is the problem Lunar Magic's Map16 abstraction exists to solve for SMW: instead of hand-placing 8×8 CHR tiles, you build and reuse a palette of pre-assembled 16×16 blocks.

**Secret of Evermore already has this, in the ROM format itself.** Every room already works at the 16×16 metatile level — `dump_room()`'s `metatile_count` (over 1000 for a large room like `0x38`) is the room's own pre-built block palette, decoded straight from Block 3's planar table. There's no need to invent a Map16-equivalent abstraction for this game; there's a need for a **good browser** over the one the ROM already provides: thumbnails (rendered once, cached), a search/filter by usage (highlight every cell on the canvas using a given metatile — the direct equivalent of Lunar Magic's map16 highlighting), and grouping by the tile-family boundaries `dump_room()` already reports.

This is also where the multi-game abstraction earns its keep: a game whose format doesn't pre-bake a metatile table would need the Map16-style *construction* UI — compose-and-save-to-palette — that SoE's server can skip entirely. That's a second, more involved variant of the `grid`-kind tool (§4), not a different architecture.

### 9.3 Hard part 3: what a room looks like depends on object state

Section 3 objects (gourds, cut bushes, sewer gates — `docs/map_objects.md`) have multiple states, each stamping different metatiles over the same footprint. A cuttable-grass tile (`docs/cuttable_grass_mechanics.md`) likewise has an "intact" and a "cut" appearance from the same swap-table record. A static render of "the room" is really a render of *one* state combination.

**Answer: a state scrubber per object, and per cuttable region**, local to the object's property panel — not a global room-wide "game state" concept (out of scope; no attempt here to simulate story-flag-driven room variation). Selecting a state re-renders just that object's footprint with the alternate metatiles, using the same rendering path as the base composite.

### 9.4 Hard part 4: the same UI has to serve games with different layer structures

Already addressed structurally in §4 — repeated here because it's a tiling/layers problem specifically. The risk with any "generic" editor is that "generic" quietly means "generic across the two games the author actually tried," and the third game needs a rewrite anyway. The concrete discipline against that: every editing tool in this document is written once, against a `Layer` **kind**, never against a game id or a layer name. What would falsify the design is a server needing to reach past that shape into shell-specific or game-specific UI code to be rendered or edited; that's the thing to watch for once a second server is actually attempted (§4).

---

## 10. Editing surface: what's in v1, what's deliberately out

### 10.1 In v1 (Secret of Evermore only, one server)

- Layer visibility/active-layer switching (§9.1's easy half) and the plane view-filter (§9.1's hard half).
- The metatile palette browser with usage-highlight (§9.2).
- Collision editing by decoded meaning (plane, drift direction, entity gate, forced-walkable) via the `bitfield-grid` tool, with the raw hex word always visible alongside — per `AGENTS.md`'s golden rule, the tool should never hide the ground truth behind its own abstraction. Bits 12 and 15–14 are marked **UNVERIFIED** in `docs/map_collision_mechanics.md` §2 and must be exposed as a raw sub-field too, never silently zeroed on edit.
- Cuttable grass as a first-class property of a metatile, rather than requiring hand-editing Section 4 bytes.
- Section 3 objects with the state scrubber (§9.3), and triggers with the drag-box tool and script link (§8).

### 10.2 Deliberately out of v1

- **A second game server.** §4 exists so this is additive later, not so it's attempted alongside the first one. Building two before either is proven is how the shared shape ends up wrong in ways neither game's author notices.
- **A world-map / room-adjacency view** stitching rooms by their step-on trigger destinations. Per the same principle that removed room-ID hardcoding from `render_map.py`, adjacency must be *derived* from trigger target coordinates, never hand-mapped.
- **Full behavioral live-preview** (§7's second half) — scoped as a phase once the `snes9x2005-wasm` fork's current capabilities are actually read, not assumed.

---

## 11. Validation and testing

An editor is software with the same correctness bar as the rest of this project's tooling, not a GUI exempted from it:

- **Reuse, don't re-derive.** `save()` should call exactly the checks `tests/integration/maps/test_encode_room.py` already runs (`verify_rebuild`-style: re-decode after encode, compare) before writing to the ROM buffer, so a bug can't reach disk silently. A future server is expected to bring its own equivalent checks.
- **Golden-file regression tests for the server**, not just the UI: script a sequence of JSON requests (open a known room, paint a tile, add a trigger, save) and assert the resulting blob decodes to the expected model — the same style as the existing `tests/integration/maps/test_room_0x*_vram.py` fixtures, driven through the JSON surface instead of calling `dump_room()` directly.
- **The extension host and webview**, per §2, follow `everscript-vscode`'s existing hand-rolled `assert`-based test convention — no new test framework for one subsystem.

---

## 12. Rough phases

Not a schedule — an ordering that keeps every phase shippable and useful on its own:

1. **Wire the existing `src/rooms/` inspector to the new Python map-server for tile/collision rendering**, in place of `src/maps/`'s sentinel-based decode. This is closer to a migration than new construction: the Rooms tab's trigger/entity overlay, image display, and ROM script cards all keep working; only the tilemap payload source changes, from a heuristic that fails on `0x38` to one verified on all 127 rooms.
2. **Tile and collision editing**, save-in-place only — proves out the JSON edit/undo loop, the `grid` and `bitfield-grid` tools, and §9.1's plane view-filter against the lowest-risk data.
3. **Objects, triggers, cuttable grass**, the state scrubber (§9.3), and the relocation path in `save()`.
4. **`source_map.json`** and bidirectional script linking (§8) — sequenced after the generic core is proven so it's built as a capability on top rather than woven through it.
5. **The metatile palette browser** (§9.2) with usage-highlighting.
6. **Read what `feature/vscode-debugger-integration` actually exposes today**, and scope live behavioral preview (§7) as a concrete phase once that's known rather than assumed.
7. **A second game server.** The actual test of §4: point the same shell and the same generic tools at a different ROM format and see what `Layer` kind is missing. Secret of Mana or Terranigma, whichever has more existing reverse-engineering to build on at the time.
