# Map Editor as a VS Code Plugin — Repo, Lexer Reuse, and What to Redo

Assumes the decision already made in `docs/map_editor_design.md`: the map editor is a VS Code
extension, Python backend, no plugin/registry system (§3–§5 there). This document answers four
follow-up questions the design doc didn't settle -- repo placement, lexer/parser reuse, the language
and IPC/packaging choice underneath the JS↔Python boundary, and what in `everscript-vscode` has
already been tried and failed -- each grounded in what's actually in
`/Users/v/Documents/GitHub/everscript-vscode` today, not in how a fresh extension would ideally
look.

---

## 1. Should it be in this repo?

"This repo" has to mean one of three things, and they have different answers.

### 1.1 In `everscript` (this repo), as Python tooling — **yes, already true**

The map editor's actual hard part — decode, encode, collision, cuttable grass, rendering — has to
live in `everscript`, because that's where the verified, byte-exact, tested implementation already
is (`tools/dump_room.py`, `encode_room.py`, `collision.py`, `cuttable_grass.py`,
`render_map.py`). This isn't a choice to make; `docs/map_editor_design.md` §1.1.1 already found the
alternative (reimplementing this in the extension's own language) tried and stalled. Nothing in
this section changes that.

### 1.2 In `everscript-vscode`, as the extension's UI — **yes, extend it, don't fork it**

This is the live question, and `map_editor_design.md` §3 already answered it: extend the existing
extension rather than publish a second one. Restated with the reasoning specific to "should it be
in this repo":

- `everscript-vscode` already has a room/trigger inspector (`src/rooms/`), a ROM-backed script
  disassembler (`src/emulator/room-script-model.js`), and — critically — a **first-party forked,
  embedded SNES core** (`r-bin/snes9x2005-wasm`, branch `feature/vscode-debugger-integration`).
  None of that is replicable cheaply in a new extension; it's not "some code that happens to
  exist," it's the actual hard infrastructure (WASM core embedding, webview CSP configuration that
  took multiple broken releases to get right — §3) that a second extension would have to solve
  from scratch.
- A second extension means a second activation lifecycle, a second settings surface
  (`everscript.repoPath`/`everscript.romPath` already exist and are consumed by `src/rooms/` —
  duplicating them invites the two extensions' settings to drift), and the Rooms tab either stays
  a read-only toy forever or gets rebuilt inside the new extension, which is strictly worse than
  extending it in place.

**Concretely:** a new top-level subsystem directory in `everscript-vscode`, sibling to `debugger/`,
`rooms/`, `emulator/`, `language/` — following `AI_ARCHITECTURE_GUIDE.md`'s existing rules (file
size limits, single-state ownership, the directional dependency graph). `map_editor_design.md` §3
already spelled this out; nothing here overrides it.

### 1.3 As a single merged repo — **revised: yes, if a shared release cycle is genuinely fine**

An earlier draft of this document said no here, on the grounds that `everscript` and
`everscript-vscode` have independent versioning and release cadences that merging would needlessly
couple. That's still true as a description of today — but it's an argument against merging *if
keeping the cadences separate is a goal*. Told explicitly that a shared release cycle isn't a
problem, the calculus changes, because a monorepo unlocks something a two-repo setup makes
needlessly awkward: **shipping the map-server as a compiled binary inside the `.vsix`**, so
installing the extension doesn't also require the user to have a Python interpreter and a `.venv`
set up. See §3.3 -- that's the concrete thing this buys, not merging for its own sake.

What doesn't change: the dependency direction. The extension depends on the compiler/map-server,
never the reverse, and that stays true whether they're one repo or two — a monorepo with `compiler/`
and `tools/` on one side and `src/` (the extension) on the other, in clearly separated top-level
directories, is not "merging two projects into a mess," it's choosing one Git history and one CI
pipeline for two components that already depend on each other in one direction.

---

## 2. Should the lexer/parser be reused, so highlighting always works?

Short answer: **yes for tokenization, and the current setup is worse than "not reused" — it's
three independent, hand-maintained approximations of the same grammar, none of which is the real
one.** This was checked directly, not assumed.

### 2.1 What exists today: three grammars, zero of them authoritative

| # | What | Where | How it understands `.evs` syntax |
|---|---|---|---|
| 1 | Syntax highlighting | `src/language/syntaxes/everscript.tmLanguage.json` (266 lines) | Hand-written TextMate regex grammar |
| 2 | Hover docs / completions data | `src/language/data/index.json` (231 KB, generated) | `tools/generate_data.py` — **hand-rolled `re.match()` calls** (`r'^enum\s+(\w+)\s*\{'`, `r'^fun\s+(\w+)\s*\(([^)]*)\)'`) scraping `in/core/*.evs` line by line |
| 3 | The actual language | `compiler/lexer.py` + `compiler/parser.py` in **this repo** | A real `rply` LALR(1) grammar — the one that determines what `.evs` code actually means |

None of these three is derived from either of the others. `generate_data.py` does not import
`compiler.lexer` or `compiler.parser` — it re-derives "what does an enum declaration look like" and
"what does a function declaration look like" from scratch, in Python regex, as a second guess at
the same grammar `compiler/parser.py` already implements correctly. It also isn't wired into any
build script in `package.json` (`build:core:*` there builds the WASM emulator cores, unrelated) —
it's a manual step, so even its own regex-based understanding can go stale against `in/core/`
without anything noticing.

This is the same shape of problem `map_editor_design.md` §1.1.1 found for ROM decoding
(`src/maps/`'s independent sentinel-based decoder failing on room `0x38` while `everscript`'s
verified decoder already solved it) — a second, weaker reimplementation of something already
solved correctly, one repo over. It should be named as the same category of problem, because the
fix is the same shape too: point at the real implementation instead of re-deriving it.

### 2.2 What "reuse" can and can't mean here

VS Code's syntax highlighting is a fast, synchronous, regex-based TextMate grammar for a reason —
it has to paint every keystroke with no perceptible delay, and it runs in the renderer, not a spawned
process. `compiler/lexer.py`'s `rply`-based lexer cannot be that; it's Python, it would need a
process round-trip per edit, and `docs/vscode-highlighter-spec.md` §"Grammar Strategy" already
records that Semantic Highlighting was considered and explicitly turned off "for performance." That
was the right call for *that* use case, and this document isn't proposing to reverse it for
baseline highlighting.

Where reuse is unambiguously right, and unambiguously not what's happening today:

- **Tokenization for anything that isn't paint-every-keystroke.** `compiler/lexer.py`'s `Lexer` is
  standalone — `Lexer().get_lexer()` needs no `Linker`/`CodeGen`/`Parser` machinery, just
  `rply.LexerGenerator`. `generate_data.py`'s regex scraping of enum and function declarations is
  exactly the kind of thing this could replace directly: spawn the same map-server-style Python
  process the map editor already needs (§5.2 of `map_editor_design.md`), call the real lexer/parser
  against `in/core/`, and emit `index.json` from the real AST instead of from six regex patterns
  that don't know about multi-line signatures, default arguments, or nested annotations. This is a
  strictly additive change to an already-manual, already-disconnected step — low risk, and it
  removes one of the three grammars rather than adding a fourth.
- **Semantic tokens as a second, richer layer on top of the TextMate baseline** — the same pattern
  TypeScript's own VS Code extension uses (fast approximate grammar first paint, a language server
  correcting it a moment later). This is a real option, not the one `vscode-highlighter-spec.md`
  already rejected, because it doesn't replace the TextMate grammar — it augments it, only for the
  cases the regex grammar structurally can't get right (e.g. distinguishing a user-defined function
  call from a core-library one, which needs to know what's actually declared where — `index.json`
  again, but live instead of stale). Whether this is worth building is a genuine open question, not
  a "yes" — see the TODOs.
- **Go-to-definition / find-references correctness.** These already exist in `src/language/` and
  already work by scanning `.evs` text with `src/language/`'s own logic, independent of both the
  TextMate grammar and `generate_data.py`. Whether *this* should also route through the real parser
  is a separate, larger question (it would mean `everscript-vscode`'s core navigation features
  depend on a spawned Python process being available) and is explicitly **not** proposed here — the
  map-server dependency (§5.2 in the design doc) is scoped to the map editor, not to language
  features that already work.

### 2.3 What this means concretely

Not "rewrite the grammar." Specifically:

1. Fix `generate_data.py` to import and drive `compiler.lexer`/`compiler.parser` instead of
   regexing `in/core/*.evs` by hand. Wire it into a build step (there isn't one today) so
   `index.json` can't silently drift.
2. Leave `everscript.tmLanguage.json` as the fast baseline grammar — it's the right tool for
   paint-every-keystroke highlighting and nothing here argues otherwise.
3. Treat semantic tokens (item 2 above) as a candidate future enhancement to evaluate on its own
   merits, not as part of fixing item 1.

---

## 3. Language choice: what's fixed, what's a real decision, and what connects them

Prompted directly: "what language did we use before, what can a VS Code extension actually be
written in, and what's the path of least resistance vs. the most interesting technically." These
are three different questions with three different kinds of answer — one is a hard constraint, one
is already decided by §2's evidence, and one is a genuine, open engineering choice.

### 3.1 Not a choice: the extension host is JavaScript/TypeScript, full stop

VS Code extensions run in a Node.js extension host process. The `vscode` API — commands, custom
editor providers, webview panels, everything an extension registers — is a Node/JS API with no
equivalent binding in Python, Rust, Go, or anything else. There is no way to write `extension.js`'s
equivalent in another language; `everscript-vscode`'s existing `src/extension.js` and every file
under `src/` being plain JavaScript isn't a stylistic choice being revisited here, it's the only
option. (TypeScript is available as a compile-to-JS option, and `everscript-vscode`'s own
`tsconfig.json` already permits it — `allowJs: true` — but §2 of `map_editor_design.md` already
covered why matching the existing plain-JS convention beats introducing TypeScript as a second one.)

A webview's content is an embedded browser page, so it's JS/HTML/CSS too — or WASM driven by JS,
which is exactly what the embedded `snes9x2005-wasm` emulator core already is (C compiled to WASM,
loaded and driven from JS). That precedent matters for §3.3 below: WASM-in-the-extension is not a
hypothetical for this project, it's already shipping.

### 3.2 Not really a choice either: the ROM-format logic stays Python

This was already settled by evidence, not preference. `map_editor_design.md` §1.1.1 and this
document's §2.1 both found the same failure mode: `everscript-vscode` independently re-derived two
different pieces of this project's domain logic in JavaScript — the ROM tilemap decoder
(`src/maps/`) and the `.evs` grammar (`generate_data.py`) — and both are demonstrably worse than the
Python originals (one fails outright on room `0x38`, the other is a six-regex approximation of an
LALR grammar). A third re-derivation, of the newer collision/cuttable-grass/encoding logic this
session's work in `everscript` just finished verifying byte-exact across 127 rooms, would be
repeating a mistake this project has now made twice. The map-server's logic is Python because that's
where the already-correct implementation is, not because Python is preferred in the abstract.

### 3.3 The actual open question: how does JS talk to that Python, and how does it ship

This is where "least resistance" and "technically interesting" genuinely point at different
answers, and where the monorepo decision (§1.3) changes which answer is best.

**Option A — hand-rolled newline-delimited JSON over `child_process.spawn`.** What
`map_editor_design.md` §5.2 originally proposed. Least resistance in the narrowest sense: zero new
dependencies on either side, and it's *literally* the mechanism `everscript-vscode` already uses
today to invoke `everscript.py` for the "Build and Run" command (`src/extension.js` ~line 836) —
not a new pattern, an extension of one already in production. Downside: request/response
correlation, partial-read framing, and concurrent-request handling are all things this option makes
you write yourself, badly, the first time.

**Option B — `vscode-jsonrpc` on the Node side, a small JSON-RPC 2.0 responder on the Python
side.** The more idiomatic answer, and arguably the more interesting one without being exotic:
`vscode-jsonrpc` is the actual library Microsoft's own Language Server Protocol client/server pairs
are built on — it's the framing and correlation layer underneath every LSP-based extension
(Python's, Rust's, C++'s). Using it here means borrowing a small, single-purpose, already-hardened
library for exactly the problem Option A makes you solve by hand, without adopting full LSP
*semantics* (`textDocument/didChange` and friends don't fit "edit a tile grid," and nothing here
proposes pretending they do — just the transport). This would be `everscript-vscode`'s first runtime
npm dependency (today's `dependencies: []` is real), which is worth being deliberate about, but a
dependency this narrowly scoped and this widely proven is a reasonable one to take. On the Python
side, a JSON-RPC 2.0 responder over stdio is not a lot of code to hand-write (matching the framing
`vscode-jsonrpc` expects), or a minimal existing package can supply it — either way, small.

**Option C — freeze the map-server with PyInstaller and ship the binary inside the `.vsix`.** This
is where the monorepo pays off, and it's the answer to "coolest without being reckless": the map
tools (`dump_room.py`, `encode_room.py`, `collision.py`, `cuttable_grass.py`, `render_map.py`) were
checked directly while writing this document and have **zero third-party dependencies** — no numpy,
no PIL, standard library only. `everscript.spec`/`make.py` already prove out PyInstaller for this
exact project on a much larger target (the full compiler, which *does* pull in `numpy`/`rply`/etc.).
Freezing the much smaller, dependency-free map-server subset is strictly easier than what's already
working. Bundled into the `.vsix` (which a monorepo's single CI pipeline can do as one release step:
freeze, copy into `dist/`, package), a user installs one extension and the map editor works —
no `everscript.pythonPath`/`repoPath` settings to configure, no separate Python install, none of the
"does this contributor's machine have a working `.venv`" friction `src/shared/config.js` exists to
paper over today. This isn't a different transport from Option A/B — it's still
`child_process.spawn` talking JSON to a subprocess, just spawning a bundled binary instead of
`python3 tools/map_server.py`. It's additive on top of whichever of A/B is chosen, not a fourth
alternative to them.

**Named and set aside — WASM-compiled Python (Pyodide/MicroPython) running in-process in the
webview or extension host, avoiding a subprocess entirely.** Technically real (Pyodide runs full
CPython in WASM today, including precompiled `numpy` wheels), and it would remove the IPC boundary
altogether — genuinely the "coolest" option by some measure. Set aside because the map tools'
biggest practical cost with a subprocess approach is protocol plumbing (Option B solves that
directly) and installation friction (Option C solves that directly); Pyodide's multi-megabyte WASM
runtime and multi-second cold start would be paid to solve a problem — "the map tools need a
compiled-extension-heavy Python environment" — that §3.3's own fact-check just established doesn't
exist for this specific code. Worth remembering if the map-server ever grows a real dependency on
something like `numpy`; not worth adopting pre-emptively.

**Recommendation:** B for the transport (idiomatic, small, reusable if this project ever adds
another spawned-process feature), C for packaging once the monorepo is in place (removes the
biggest real friction for anyone other than the maintainer installing the extension), A only as the
zero-effort placeholder if B is more than the map editor's first cut warrants — worth being honest
that A working today is a real reason it might be what actually gets built first, with B as a
follow-up hardening pass rather than a prerequisite.

---

## 4. What was tried in `everscript-vscode` and needs redoing

Found directly in that repo's own status docs and changelog — not inferred. Two are already
covered by `map_editor_design.md` and are only summarized here for completeness; the rest are new.

### 4.1 The ROM tilemap decoder (`src/maps/`) — *(already covered, §1.1.1 of the design doc)*

Sentinel/`strict7`/`short6` heuristic scan; works on 4 simple rooms, explicitly fails on `0x38`.
Superseded by calling into `everscript`'s verified decoder — no new work needed here beyond what
`map_editor_design.md` §12 phase 1 already schedules.

### 4.2 The language-data grammar (`tools/generate_data.py`) — *(new, this document, §2.1 above)*

Regex-based re-derivation of the enum/function grammar `compiler/parser.py` already implements
correctly, with no build-time wiring to catch drift. Redo per §2.3.

### 4.3 The embedded emulator webview — multiple real regressions, now stabilizing

`docs/emulator-v0.2.71-revert-notes.md` and `CHANGELOG.md` document a genuinely rough integration,
not a smooth one:

- **v0.2.73 / v0.2.74**: two successive CSP (`Content-Security-Policy`) header changes each broke
  the webview's inline boot script — `script-src 'nonce-${nonce}' ${cspSource}` and later
  `script-src ${cspSource} 'unsafe-inline'` both failed because `cspSource` resolves to a
  single-label wildcard (`https://*.vscode-cdn.net`) that doesn't match VS Code's actual
  multi-level resource-server subdomain. Fixed by reverting to the wildcard `script-src * blob:
  data:` that had worked since v0.2.70.
- **v0.2.71**: introduced Unicode box-drawing characters (`─`) as comment dividers inside an HTML
  template literal; non-ASCII bytes in that position threw `Invalid or unexpected token` in the
  webview's JS parser before `onRuntimeInitialized` ever fired, so the `ready` handshake silently
  never happened and ROM loading looked broken with no useful error.
- **v0.2.71 rollback**: the same release's script-lifecycle-detection and script-stack detail panel
  features caused `Timeout waiting for webview ready message` in the live extension (separately
  from the two bugs above) and were rolled back wholesale, then reintroduced incrementally behind a
  new regression test (`debugger/tests/emulator-runtime.test.js`, which opens the real panel HTML
  and asserts the `webviewBoot`/`ready` handshake completes — validated against the historical
  broken commit to confirm the test actually catches the regression it's named for).

**What needs redoing:** nothing structurally — the process that recovered from this (isolate to
the smallest reproducible slice, write a regression test that opens the actual panel HTML and fails
against the known-bad historical commit, reintroduce features one at a time behind that test) is
exactly right and is the model to follow for the map editor's own webview work. What's still open
per the revert notes themselves: **the script-stack lifecycle-derived break behavior is still
excluded**, reintroduced only up to "the read-only script detail panel," with the riskier
break-on-lifecycle-event behavior deliberately held back pending more test coverage. If the map
editor's live-preview feature (`map_editor_design.md` §7, §12 phase 6) builds on this fork, it
inherits this in-progress state, not a finished one — check what's actually merged before assuming
the debugger integration branch is feature-complete.

### 4.4 The DAP (Debug Adapter Protocol) implementation — mock, not real, and should stay legible about that

`src/debugger/mock-runtime.js` says so in its own header comment: *"No actual bytecode execution —
this is a source-level mock for the DAP."* Variable inspection returns literal placeholder strings
(`'0x0000  (mock)'`). This is a reasonable scaffold — it lets the DAP protocol surface (breakpoints,
stepping UI, call stack panel) get built and tested before real execution exists — but it means
"Debug .evs script" today does not reflect real WRAM/script-VM state.

**What needs redoing, if the map editor's script-linking feature** (`map_editor_design.md` §8) is
meant to connect a trigger to a *live, debuggable* view of its script, not just a static jump to
source: the mock runtime needs to become a real one, backed by the same embedded `snes9x2005-wasm`
fork already being extended for the emulator panel (§4.3). This is real, substantial, unstarted
work, not a small gap — the mock runtime is 406 lines of plausible-looking scaffold with none of it
reading actual emulator state. Flagging it now so the map editor's phase 6 (`map_editor_design.md`
§12) doesn't assume "the debugger already works" when it means "the debugger's UI already works and
its data is invented."

### 4.5 The Rooms tab's own settings/data cleanup — in progress, worth finishing first

`docs/rooms-settings-cleanup-dossier.md` (status: "In progress") already overlaps directly with
what the map editor needs: consolidating `everscript.repoPath`-derived settings, making Rooms tab
data ROM-backed instead of "client-side placeholder text," and — its own listed known gap —
"many room-script opcodes still depend on a real sub-instruction model." That last point is a
second, narrower instance of §4.2's problem: `room-script-model.js`'s `OPCODE_REGISTRY` disassembles
fixed-width opcodes correctly but doesn't yet decode the variable-length "calculator" sub-instruction
format that `out/patch.txt` (from `everscript`'s own compiler output) already renders correctly, as
the very `patch.txt` excerpt used to find the jump-distance bug in this session's earlier work
shows (`calculator([Opcode(09/if), ...])`). This is worth finishing *before* building the map
editor's trigger panel on top of it, rather than inheriting an incomplete disassembler into a new
feature.

---

## 5. TODOs

Grouped by the four sections above, roughly in the order they'd need to happen. Not a sprint plan —
an ordering that avoids building the map editor's trigger/script panel on top of infrastructure
that's still labeled "in progress" or "mock" elsewhere in the same extension.

### 5.1 Repo placement (§1)

- [ ] Confirm with whoever maintains `everscript-vscode` releases that a new subsystem
      (`src/map-editor/` or similar) is welcome there rather than as a separate extension —
      this document assumes yes based on the architecture, not based on having asked.
- [ ] Add the map-editor subsystem to `AI_ARCHITECTURE_GUIDE.md`'s ownership-domain list and
      dependency-direction rules (§2.3–2.4 there) *before* writing code against it, the same way
      `debugger`/`rooms`/`emulator` are already documented.
- [ ] Decide whether the map-server (Python, spawned) lives under `everscript/tools/` (as
      `map_editor_design.md` §5 assumes) or gets a dedicated location — it's ROM-format logic, so
      §1.1 says `everscript`, but confirm it doesn't collide with the CLI-tool conventions
      `tools/*.py` already has (each currently has its own `--help`, its own `if __name__ ==
      "__main__"` entry point; a long-lived server process is a different shape and should say so
      in its own module docstring).

### 5.2 Lexer/parser reuse (§2)

- [ ] Rewrite `tools/generate_data.py` (in `everscript-vscode`) to import `compiler.lexer` /
      `compiler.parser` from `everscript` instead of hand-rolled regex. Requires deciding how
      `everscript-vscode` locates its `everscript` checkout at build time — `src/shared/config.js`
      already resolves `repoPath`/`pythonPath` for the compiler-spawning use case; reuse that
      resolution rather than inventing a second one.
- [ ] Wire the rewritten `generate_data.py` into an actual build/CI step (`package.json` `scripts`)
      so `index.json` regenerates automatically instead of silently drifting from `in/core/`.
- [ ] Add a test that fails when `index.json` is stale against a freshly-generated one — the
      concrete, checkable version of "always works" rather than a hope.
- [ ] Write down the semantic-tokens option (§2.2) as a scoped proposal with its own cost/benefit —
      do not build it opportunistically alongside the map editor; it's a separable, VS Code
      API-shaped decision with its own risk (another webview/extension-host boundary to get right,
      per §4.3's history).
- [ ] Explicitly out of scope for this pass: routing go-to-definition/find-references through the
      real parser. Revisit only if a concrete correctness bug in the current text-scanning approach
      is found — don't preemptively add a process dependency to features that work today.

### 5.3 Language / IPC / packaging (§3)

- [ ] Decide monorepo vs. two-repo before writing the map-server, not after — Option C (§3.3)
      only makes sense with one CI pipeline able to freeze the Python side and copy the binary into
      the extension's `dist/` as part of the same release.
- [ ] If two repos stay: implement Option A (hand-rolled newline JSON over `child_process.spawn`)
      first, matching the existing `everscript.py`-spawning pattern exactly. Cheapest correct
      starting point regardless of which longer-term option is chosen.
- [ ] If `vscode-jsonrpc` (Option B) is adopted: this is `everscript-vscode`'s first runtime npm
      dependency (`dependencies: []` today) — flag that explicitly in the PR that adds it rather
      than letting it slip in as an implementation detail of the map editor.
- [ ] Before committing to Option C (PyInstaller-in-`.vsix`): confirm the freeze actually stays
      dependency-free as the map-server grows past the five tools checked in §3.3 -- re-run the
      same "grep for third-party imports" check this document did, don't assume it still holds.
- [ ] Explicitly not now: Pyodide/WASM-Python. Revisit only if the map-server picks up a real
      dependency on something like `numpy` that makes "no subprocess at all" newly attractive --
      don't adopt it pre-emptively for its own sake.

### 5.4 Rework before/alongside the map editor (§4)

- [ ] `src/maps/`: retire its tilemap-decode responsibility in favor of the map-server
      (`map_editor_design.md` §12 phase 1). Keep its header/trigger-table reading if
      `parse_blob_layout`-equivalent logic isn't yet available client-side, but don't extend the
      sentinel model further.
- [ ] `emulator/`: before building the map editor's live-preview feature on the
      `feature/vscode-debugger-integration` fork, read what that branch currently exposes versus
      what `map_editor_design.md` §7 assumes (this document does not know, per its own §4.3 note)
      — specifically whether the lifecycle-derived break behavior held back in the v0.2.71 rollback
      is needed for anything the map editor wants, or whether the map editor only needs ROM
      loading + the read-only script-stack view that's already reintroduced.
- [ ] `debugger/`: decide whether the map editor's script-linking feature needs the DAP to be real
      (§4.4) or only needs static source navigation (`map_editor_design.md` §8, the
      `source_map.json` proposal, which needs no runtime emulator at all). If it's the latter — and
      §8 as written is the latter — explicitly scope the mock-to-real debugger work as a separate,
      later initiative, not a dependency of the map editor.
- [ ] `rooms/`: finish or explicitly de-scope the sub-instruction "calculator" opcode decoding gap
      (§4.5) before wiring the map editor's trigger panel to `room-script-model.js`'s disassembly
      output, since an incomplete disassembly presented as complete is worse than the map editor
      falling back to "no script preview available" for the affected opcodes.
- [ ] Cross-reference: once `src/maps/` is retired (item 1 above), re-check whether
      `rooms-settings-cleanup-dossier.md`'s "make vanilla Rooms data ROM-backed instead of
      client-side placeholder text" is already satisfied by the map-server, or still needs its own
      work — likely satisfied, but confirm rather than assume.
