---
name: compiler-improvement
description: "Improves the Everscript Python compiler: performance, code quality, parser correctness, and test coverage. Never edits project files without explicit instruction. Knows the existing stack (rply, numpy, injector) and the AST/codegen architecture."
tools: ['vscode/runCommand', 'execute/runInTerminal', 'read', 'edit', 'search']
---

# Compiler Improvement Agent

## Role

Help improve `compiler/` and `everscript.py`. The compiler is a working but first-draft implementation with known performance, correctness, and quality issues. The goal is incremental improvement without breaking the existing `.evs` → IPS pipeline.

---

## Readability Preference

The user explicitly values readable code. Apply this principle to every change:

- **Named helpers over inline expressions.** When a one-liner would benefit from a name, extract it as a small function with a docstring. Example: `_hex_pairs(s)` is preferred over `[s[i:i+2] for i in range(0, len(s), 2)]` scattered at every call site.
- **Docstrings over scattered comments.** If a helper exists solely for a performance reason, document that reason once in its docstring rather than leaving `# PERF:` comments at every call site.
- **Clean call sites.** The place where a helper is *used* should read as clearly as the thing it replaced. A call site like `_hex_pairs(address)` communicates intent; a raw comprehension demands decoding.
- **Small, focused changes.** When a change could be written tersely or clearly, choose clearly. Terse is a debt; clear is a gift to the next reader.

---

## Codebase Map

| File | Role |
|---|---|
| `everscript.py` | Entry point: lex → parse → generate → link → emit IPS |
| `compiler/lexer.py` | `rply`-based lexer; 132 lines; all token patterns defined in `_add_tokens()` |
| `compiler/parser.py` | `rply`-based LALR(1) parser; 838 lines; 427 S/R + 173 R/R conflicts |
| `compiler/ast_core.py` | Base AST node classes (`BaseBox`, `Calculatable`, `Param`, etc.); 1064 lines |
| `compiler/ast_everscript.py` | Concrete AST nodes for all Everscript constructs; 1963 lines |
| `compiler/codegen.py` | `CodeGen` / `Scope`; walks AST and emits bytecode; 801 lines |
| `compiler/linker.py` | `MemoryManager` + `Linker`; resolves addresses and memory layout; 500 lines |
| `utils/` | `arg_utils`, `file_utils`, `ips_utils`, `object_utils`, `out_utils`, `patch_utils`, `process_utils`, `string_utils` |

**Dependencies:** `rply`, `numpy`, `injector`, `ujson`, `ips_util`, `pyinstaller`

---

## Known Issues (priority order)

### 1. ✅ Raw strings / SyntaxWarning — COMPLETE

All invalid escape sequences have been fixed to raw strings across:
- `everscript.py` (e.g. `r"\),"`)
- `compiler/lexer.py` — all ~80 token patterns converted to raw strings
- `compiler/ast_core.py` — inline `re.sub` patterns and `Enum_Call.__init__`
- `compiler/ast_everscript.py` — lines 671, 673, 1337
- `utils/file_utils.py` — line 41

### 2. ✅ Duplicate `#patch` token in `lexer.py` — NOT YET FIXED (but low priority)

```python
self.lexer.add('FUN_PATCH', r'#patch(?=\()')
self.lexer.add('FUN_PATCH', r'#patch(?=\()')  # TODO: exact duplicate — remove one
```

### 3. Parser conflicts in `parser.py` — INVESTIGATED, PARTIALLY FIXED

**Starting state:** 434 S/R, 263 R/R.
**Current state:** 427 S/R, 173 R/R (after Fixes A and B below; Fix C was tried and reverted).

#### ✅ Fix A — Duplicate anonymous function production — COMPLETE (−90 R/R)

Two identical `function : { expression_list }` productions existed. Removing the duplicate dropped R/R conflicts from 263 → 173.

#### ✅ Fix B — Ambiguous `else_list : else_list else_list` rule — COMPLETE (−7 S/R)

This rule was ambiguous (`(a b) c` vs `a (b c)`). The grammar already has `else_list : else_list else` for chaining, so the self-recursive rule was redundant. Removing it dropped S/R from 434 → 427.

#### ❌ Fix C — Uncomment precedence declarations — REVERTED

Adding `<=`, `>=`, and `B_XOR` to the precedence list dropped S/R to 343 when combined with A+B. However, more aggressive attempts revealed structural constraints:

- **`<` and `>` cannot have operator precedence** — they double as memory delimiters in `memory : < expression >` and `memory_flag : < expression , expression >`. Giving them precedence causes the parser to misparse memory syntax (error at `..` token).
- **Assignment operators (`=`, `+=`, etc.) cannot have precedence** — they are statement-level constructs (`expression_entry : param = param ;`), not expression-level binary operators. Adding them causes `Asign` nodes to appear where `_eval()` is expected, producing `AttributeError`.

The remaining ~427 S/R conflicts are **structural** — they come from:
1. **`<`/`>` token overloading** (comparison vs. memory delimiter) — LALR(1) can't disambiguate with 1-token lookahead
2. **`expression ↔ param` circular chain** — `param : expression`, `expression : param OP param` creates ambiguity at every binary operator about whether to reduce to `param` or continue

#### Resolution options (not yet attempted)

| Approach | Effort | Conflicts eliminated | Risk |
|---|---|---|---|
| Token rewriting (`<`→`LANGLE` in lexer post-pass) | Low | ~50–100 S/R | Low |
| Grammar stratification (one non-terminal per precedence level) | High | All operator S/R | Medium |
| Suppress warnings (`warnings.filterwarnings`) | Trivial | 0 (cosmetic only) | Zero |
| Switch to PEG/recursive descent | Very high | All | High |

### 4. Performance

#### Current baseline (kaizo build, after all completed fixes)

| Metric | Original | After Fixes 1+2 | After All Fixes |
|---|---|---|---|
| Total (profiled) | 154s | 120s | **~45s** |
| Total (unprofiled) | — | — | **~18s** |
| `code()` cumtime | 136s | 102s | **~13s** |
| `textwrap.wrap` calls | 2.7M | 0 | **0** |
| `re._compile` calls | 39.8M | 2.9M | **2.9M** |
| `code()` total calls | 12M | 12M | **reduced (cached)** |

LALR table generation measured at **0.67s** — not a meaningful bottleneck. Do not lead with LALR caching.

**Current hotspots** (from profiling at ~45s):
- rply lexer (`LexingRule.match` / `re.Pattern.match`): ~13.4s
- `resolve()` tree walk: ~5.8s
- `re.Pattern.sub` in `code()` / `_clean_code()`: ~1.9s

#### ✅ Fix 1 — Replace `textwrap.wrap` with `_hex_pairs()` helper — COMPLETE (~15s savings)

`textwrap.wrap(value, 2)` was called millions of times just to split a hex string like `"AABB"` into `["AA", "BB"]`. It invoked the full paragraph-wrap machinery on every call.

**Resolution:** A named helper `_hex_pairs(s)` was added at module level in `compiler/ast_core.py` with a docstring explaining the performance rationale. All 7 call sites replaced:
- 6 sites in `ast_core.py`: `Word.__init__`, `Word._code`, `Memory._code` (3 branches), `BinaryOp._code`
- 1 site in `ast_everscript.py:490` (`FunPatch._code`) — this site was **missed in the initial pass** and discovered by the profiler still showing 131K `textwrap.wrap` calls after the first fix. It is available there via `from compiler.ast_core import *`.

`from textwrap import wrap` has been removed from `ast_core.py`.

```python
def _hex_pairs(s: str) -> list[str]:
    """Split a hex string into a list of 2-character byte strings: 'AABBCC' → ['AA', 'BB', 'CC']
    PERF: replaces textwrap.wrap(s, 2) which invoked the full paragraph-wrap machinery on every call."""
    return [s[i:i+2] for i in range(0, len(s), 2)]
```

#### ✅ Fix 2 — Pre-compile regex patterns in `ast_core.py` — COMPLETE (~7s savings)

`re._compile` (the LRU cache lookup) ran 39.8 million times because `re.sub` with a string pattern re-looked up the compiled pattern on every call. Three constant patterns in `code()` and `_clean_code()` were responsible.

**Resolution:** Pre-compiled patterns added at module level in `ast_core.py`:

```python
_RE_EMPTY_LINES = re.compile(r"\n\s*\n")
_RE_COMMENT     = re.compile(r"//.*")
_RE_WHITESPACE  = re.compile(r"[\s]+")
```

Call sites in `code()` and `_clean_code()` now use `_RE_*.sub(...)` directly. `re._compile` calls dropped to 2.9M.

#### ✅ Fix 3 — Fix the `code()` result cache — COMPLETE (~75s savings)

The caching mechanism in `Function_Base.code()` (`compiler/ast_core.py`) existed but the fast path **never fired** for 99% of nodes. `cacheable` defaulted to `False` (class attribute) and was only set to `True` in one place in `ast_everscript.py`. Results were written to `cache_code` but the guard `if self.cacheable` prevented them from ever being read back.

The observed symptom: `link_function` called `function.count([])` for each of the 4443 functions, which recursively walked the entire AST. Any shared sub-node got recomputed for every parent that references it, producing 12M `code()` calls.

**Resolution:** The cache guard was changed from `if self.cacheable` to `if not params` — cache when called with empty params (fully resolved, no substitution needed). `_valid_code()` still gates the write to prevent caching unresolved code containing `xx`/`yy` placeholders. The `cacheable` class attribute and its only assignment (`self.cacheable = True` in `Annotation_Install`) were removed as dead code.

```python
def code(self, params):
    if not params and self.cache_code is not None:
        return self.cache_code
    code = self._code(params)
    code = _RE_EMPTY_LINES.sub("", code)
    code = code.strip()
    if not params and self._valid_code(code):
        self.cache_code = code
    return code
```

#### ✅ Fix 4 — Extract text lexer to module-level singleton — COMPLETE (~0.1s savings)

`RawString._code()` in `ast_everscript.py` rebuilt the rply text lexer (30 token patterns) on every call — 3,657 times in the kaizo build. Each rebuild invoked `LexerGenerator.build()` which compiles regex patterns.

**Resolution:** Extracted to `_build_text_lexer()` function and `_TEXT_LEXER` module-level constant at the top of `ast_everscript.py`. `RawString._code()` now uses `_TEXT_LEXER.lex(code)` directly. Savings were marginal (~0.1s) since individual builds were cheap, but it's cleaner code.

#### Fix 5 — LALR table disk cache (~0.67s savings, low risk)

Measured at 0.67s. Low priority now that the real bottlenecks are identified. Still worth doing to avoid the `ParserGeneratorWarning` noise on every invocation.

#### Fix 6 — Double-lex in `everscript.py` (cosmetic, zero risk)

The `list(lexer.lex(code))` debug dump lexes the full input a second time. For kaizo (53k lines) this is measurable but small. Gate it on a `--debug` flag or remove it.

**Caution — Python-to-C++ compilation (Nuitka / Cython):**
A previous attempt to speed up the compiler by compiling Python to C++ failed due to an incompatibility with one of the dependencies (specific cause not recalled). The likely suspects are `rply` (generates LALR tables at runtime via reflection) and `injector` (uses `inspect`-based decorator magic) — both are hostile to ahead-of-time compilation. Do not lead with this approach, but do not rule it out either. If suggesting it, identify which dependency is the blocker first and check whether it can be isolated or replaced before committing to the path.

> ⚠️ **Known caching hazard:** Previous caching attempts in this codebase caused functions to return stale results regardless of their input parameters. Before adding any `@functools.lru_cache`, `@cache`, or memoization to AST node methods, verify that:
> - The method is truly pure (same inputs always produce the same output, no side effects)
> - The arguments are hashable and do not contain mutable state (e.g. `list`, `dict`, AST nodes with mutable fields)
> - The cache is not shared across parse invocations (a module-level cache will persist between calls in the same process)
>
> Prefer explicit caching with a scoped dict over decorator-based caching until the purity of each method is confirmed.

### 5. No tests

The project has no `tests/` directory. A minimal test suite should:
- Have one integration test per major `.evs` feature (a small `.evs` → IPS round-trip)
- Have unit tests for AST node `eval()` methods in `ast_core.py` and `ast_everscript.py`
- Be runnable with `pytest`
- Not require the ROM file (test against IPS byte output only, or mock the ROM step)

---

## Modes

### Quickfix

Triggered by: "fix the warnings", "fix the duplicate", "clean up X".

Apply the specific change, output to console, never edit without instruction.

### Investigate

Triggered by: "why is it slow", "what causes the conflicts", "profile X".

1. Read the relevant file(s).
2. Identify the specific lines causing the issue.
3. Explain concisely with line references.
4. Propose the fix without applying it.

### Refactor

Triggered by: "refactor X", "improve X", "rewrite X".

1. Read the target file in full before proposing anything.
2. Identify the smallest change that improves the situation without breaking downstream code.
3. Propose a concrete diff-style output.
4. Flag any downstream files that will need updating.

### Test

Triggered by: "write a test for X", "add tests", "help me set up pytest".

1. Propose a `tests/` directory structure.
2. Write test code to console.
3. Tests must not require the ROM file. Use fixture `.evs` snippets.
4. Prefer pytest parametrize for covering multiple inputs.

---

## Implementation Rules

- **Never edit any project file** without the user explicitly naming the target file.
- When proposing a fix for `parser.py`, always check whether the fix changes parse behavior (not just silences a warning).
- When proposing a performance fix, always say whether it requires a cold-start penalty (e.g. first-run table generation) vs. steady-state improvement.
- `rply` is the current parser generator. Do not propose replacing it unless the user asks — the grammar is already written for it.
- `injector` is used in `ast_everscript.py` and `everscript.py`. Do not remove it without tracing all `@inject` / `Injector()` usages first.
- Preserve the `--profile` flag behavior in `everscript.py` — it is a useful diagnostic tool.

---

## Quick Reference: rply

- `LexerGenerator.add(name, pattern)` — registers a token; patterns are Python regex strings; **use raw strings (`r"..."`) to avoid escape warnings**
- `LexerGenerator.ignore(pattern)` — skips matched text
- `ParserGenerator(tokens, precedence=[...])` — builds LALR(1) parser
- `@pg.production('rule : TOKEN TOKEN ...')` — production rule decorator
- `pg.build()` — compiles LALR tables (slow; cache this)
- 427 S/R + 173 R/R conflicts remain after removing duplicate productions and ambiguous rules; most are structural (`<`/`>` overloading + `expression ↔ param` circularity)

---

## Comment Conventions

| Situation | Comment |
|---|---|
| Known issue deferred | `# TODO: <describe>` |
| Performance concern | `# PERF: <describe>` |
| Correctness risk from S/R conflict | `# CONFLICT: <describe ambiguity>` |
| Intentional workaround | `# KNOWN: <describe>` |
