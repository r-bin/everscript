# Everscript Compiler — Code Review & Improvement Plan

**Scope:** `everscript.py`, `compiler/`, `utils/`  
**Sources:** code audit + architecture notes from `docs/incremental-compilation.md` + developer wishlist  
**Status:** living document — check items off as they are fixed

---

## Priorities at a Glance

These are ordered by impact. Fix the bugs first, then DX (developer experience) improvements, then big-ticket architecture work.

| Priority | Theme | Why now |
|----------|-------|---------|
| 🔴 P1 | **Bug fixes** (wrong output, silent errors) | Can produce broken IPS patches today |
| 🟠 P2 | **DX: type safety, output folder, circular imports, `0d3`** | Daily pain when writing or running `.evs` files |
| 🟡 P3 | **Code quality / dead code / game-agnosticism** | Makes Python side hard to read and change |
| 🟢 P4 | **Named params, nullables, overrides, room filter** | Language completeness + iteration speed |
| 🔵 P5 | **Tests + docs** | Pre-req for safe refactoring |
| ⚪ P6 | **Incremental compilation, IR, architecture** | Performance, large-project ergonomics |

---

## 1. `everscript.py`

### 1.1 No `if __name__ == "__main__"` guard ❌
`main()` is called unconditionally at the bottom of the file. In Python, every `.py` file is also a *module* — if anything ever imports `everscript`, the whole compilation pipeline runs immediately. The fix is:
```python
if __name__ == "__main__":
    main()
```

### 1.2 Module-level side effects (init runs on import) ❌
Six lines at the top of the file do real work before `main()` is even called:
```python
lexer = Lexer().get_lexer()
linker = Linker()
generator = CodeGen(linker)
pg = Parser(generator)
pg.parse()
parser = pg.get_parser()
```
This means `CodeGen.__init__` (which prints `"CodeGen.init()"`) runs at import time, not when you actually compile something. Move all of this inside `main()` or a dedicated `_build_pipeline()` helper.

### 1.3 Profile flag logic is inverted ⚠️
```python
if not args.profile:
    parser_out = handle_parse(..., True)   # always passes True!
else:
    parser_out = handle_parse(..., args.profile)
```
When `--profile` is *not* passed, timing is still active (passed `True`). The two branches should be swapped, or the `not` removed.

### 1.4 `handle_parse` parameters `rom_file` and `patches_dir` are unused ⚠️
They're accepted but never referenced inside the function body. Either remove them or use them.

### 1.5 Lexer runs twice (wasted work) ⚠️
```python
out_utils.dump(re.sub(..., f"{list(lexer.lex(code))}"), "lexer.txt")  # lex #1
lexed = lexer.lex(code)                                                 # lex #2
```
The debug dump lexes the entire input, then it's lexed again for parsing. Lex once, store the result, dump from that.

### 1.6 `import os` inside a function ℹ️
```python
def main():
    import os
    if os.path.isdir(args.input_file):
```
Python style (and PEP 8) puts all imports at the top of the file. Local imports are only justified for circular-import avoidance or optional heavy dependencies.

---

## 2. `compiler/lexer.py`

### 2.1 Duplicate `FUN_PATCH` token ❌
```python
self.lexer.add('FUN_PATCH', r'#patch(?=\()')
self.lexer.add('FUN_PATCH', r'#patch(?=\()')  # TODO: duplicate token — remove one
```
Exact duplicate. The TODO note is already there — just delete one.

### 2.2 `<` and `>` are each defined twice ❌
First definitions use negative lookahead to avoid consuming `<<`/`>>`:
```python
self.lexer.add('<', r'\<(?!\<)')
self.lexer.add('>', r'\>(?!\>)')
```
Then later, unconditional versions are added again:
```python
self.lexer.add('>', r'\>')
self.lexer.add('<', r'\<')
```
In rply, rules are tested in the order they were added. The second pair will never match anything the first pair left unreachable (they're strictly broader), but they silently add dead rules and make the lexer harder to reason about. Remove the second pair.

### 2.3 `\n` token is defined but never used ⚠️
```python
self.lexer.add('\n', '\n')
```
`\n` does not appear in the parser's accepted token list (it's commented out: `#'\n'`). The token is emitted by the lexer and then immediately discarded by the parser, or — since the ignore pattern `[ \t\r\f\v\n]+` is added last — it may never even be emitted depending on rply's rule priority. Either use it in the parser or remove it.

### 2.4 `NAME_IDENTIFIER` regex requires ≥ 2 characters ⚠️
```python
self.lexer.add('NAME_IDENTIFIER', r'[a-z_][a-z0-9][a-z0-9_]*(?=\()')
```
This requires at least one character from `[a-z_]` and then at least one from `[a-z0-9]`, so a single-character function name like `f(...)` would not be matched. If this is intentional (to avoid collision with keywords) it should have a comment; if not, it's a silent bug.

---

## 3. `compiler/parser.py`

### 3.1 Every production function is named `parse` ❌
```python
@self.pg.production('program_list : program_list program')
def parse(p):
    ...
@self.pg.production('program : enum')
def parse(p):   # overwrites the previous `parse`
    ...
```
Python allows this because rply's `@production` decorator captures the function *before* the name binding is overwritten. It works, but the local name `parse` is constantly shadowed. In a debugger or stack trace, every frame just says `parse`. A much clearer convention is to name each function after its production rule, e.g. `def p_program_list_extend(p)`.

### 3.2 `FUNCTION_CALL` and `FUNCTION_STRING` in parser token list but not in lexer ❌
```python
'FUNCTION_CALL', 'FUNCTION_STRING',
```
Neither appears in `lexer.py`. If these tokens can never be emitted, any grammar rule that uses them is dead code. If they're supposed to exist, they're missing from the lexer.

### 3.3 `TODO()` used as a catch-all error handler ⚠️
```python
case _:
    TODO()
```
`TODO()` raises `Exception("")` — an empty message. When this fires in production you get `Exception` with no context about what the unexpected value was. Pass the value in: `TODO(f"unhandled case: {inverted!r}")`.

### 3.4 Scope is pushed before the map name is known ⚠️
The `scope` production fires on `MAP`/`AREA` alone, creating a nameless scope. The name is only attached later when the enclosing `object_map` or `area` rule fires. This is fine structurally but means any error inside the scope body will report from a nameless scope.

### 3.5 Native functions use positional index into `p` without bounds checking ⚠️
```python
"entrance": (lambda p: MapEntrance(self.generator, p[2][0], p[2][1], p[2][2], p[2][3] if len(p[2])>=4 else None)),
```
Most lambdas do `p[2][0]`, `p[2][1]` etc. If the wrong number of arguments is passed, you get `IndexError: list index out of range` with no hint of which function or argument was wrong.

---

## 4. `compiler/codegen.py`

### 4.1 `_Splice` class is dead code with bugs ❌
```python
class _Splice():
    def before(self):
        return list[:self.index]   # BUG: `list` is the builtin, not `self.list`

    def after(self):
        return list[self.index:]   # same bug
```
`_Splice` is defined but never instantiated anywhere in the codebase. The `before()` and `after()` methods reference the bare name `list` (Python's built-in list type) instead of `self.list` — they would crash immediately if called. Delete the whole class.

### 4.2 `print(f"CodeGen.init()")` in `__init__` ⚠️
Debug print left in the constructor. Fires on every run. Remove it.

### 4.3 `get_function` does three separate searches for the same thing ⚠️
```python
def get_function(self, name, scope=None, with_exception=False):
    # search 1: reversed scope chain
    for scope in reversed(self.scopes): ...
    
    # search 2: provided scope (BUG: shadows loop variable above)
    if scope:
        if name in scope.functions.keys(): ...
    
    # search 3: linear scan of self.code
    for f in self.code:
        if f.name == name: ...   # TODO: returns the last match, not scope-correct one
```
The comment on search 3 admits it returns the wrong result. Also `scope` the parameter is shadowed by `scope` the loop variable in search 1, so search 2 always uses the last scope from the loop, not the original parameter. This is a real latent bug.

### 4.4 `.format()` called with ignored second argument ⚠️
Throughout `get_memory_allocation()` and `_generate_string()`:
```python
'{:06X}'.format(address, 'x')
```
`'{:06X}'.format(value, extra)` — the `'x'` is a second positional argument but the format string `{:06X}` only uses index 0. The extra argument is silently ignored. The intent was probably `f'{address:06X}'`.

### 4.5 Hardcoded ROM addresses in `_wipe_strings` ⚠️
```python
address = 0x11d000
repeat = 0x232D
```
Magic numbers embedded in logic. Should be named constants at the top of the file or in a config module.

### 4.6 `correct_address` is all `# TODO` comments ⚠️
```python
def correct_address(self, address:int)->int:
    if address >= 0xC00000: # TODO
        address -= 0xC00000
    elif address >= 0x800000: # TODO
        address -= 0x800000
    elif address >= 0x400000: # TODO
        address -= 0x400000
    if address > (4 * 1024 * 1024):
        TODO()
    return address
```
Every branch is marked TODO. The silent address-stripping is load-bearing but undocumented.

---

## 5. `compiler/linker.py`

### 5.1 Module-level singleton `_MapDataHandler = MapDataHandler()` ⚠️
Runs at import time. The 127-entry map table is built unconditionally every time the module is loaded. Not a real problem today, but ties initialization order to import order.

### 5.2 `allocate_memory` size==2 deletion logic appears buggy ⚠️
```python
del memory_list[i + 1]
del memory_list[i]
```
If `m2` is at index `i-1` and `m` is at index `i`, this deletes `i+1` (a third unrelated element) and then `i` (which is `m`), leaving `m2` in place. Likely should be `del memory_list[i]` then `del memory_list[i-1]` (reverse order to avoid index shift). The `# TODO` comment acknowledges the uncertainty.

### 5.3 Double-space in `raise` statement (style) ℹ️
```python
raise  Exception(f"function '{function.name}' cannot be linked")
```
Extra space — minor, but inconsistent.

### 5.4 `link_function` and `link_dependency` don't deduplicate ⚠️
If the same function is linked twice (which can happen through `add_dependency`), it gets two addresses allocated. There's no guard against double-linking.

---

## 6. `compiler/preprocessor.py`

### 6.1 `import re` inside `_dir_sort_key` ❌
```python
def _dir_sort_key(entry: str):
    import re   # re is already imported at module top!
    ...
```
`re` is already imported at the module level. This local import runs on every call to `_dir_sort_key` (which is called per directory entry). Remove it.

### 6.2 No cycle detection for recursive imports ❌
If file A `#import`s file B and file B `#import`s file A, `_resolve_imports` will recurse until Python's recursion limit is hit, giving an opaque `RecursionError`. A simple `visited: set[str]` passed through the call chain would catch this cleanly.

### 6.3 Diamond imports produce duplicate content ⚠️
If A imports B and C, and both B and C import D, D's content is pasted twice. No deduplication. Whether this is intentional (for `#include`-style paste semantics) or a bug depends on use case, but it should be documented.

---

## 7. `compiler/ast_core.py`

### 7.1 `Function_Base` code cache uses `not params` — subtle edge case ⚠️
```python
def code(self, params):
    if not params and self.cache_code is not None:
        return self.cache_code
```
`not params` is `True` for both `None` and `[]` (empty list). So calling `code([])` uses and populates the cache, while `code(None)` also uses it. This is probably intended, but the semantics should be clear: the cache is only valid for "no-parameter" evaluation.

### 7.2 `Resolvable.resolve` uses `match self:` as a type switch ℹ️
```python
def resolve(self, params, with_exception=True):
    match self:
        case Identifier(): ...
        case Param(): ...
        case BinaryOp(): ...
```
This is a valid Python 3.10+ pattern but unusual in a method — `self` is already bound, so it reads like `switch(typeof(self))`. Works fine but is uncommon. `isinstance` chains would be more readable to most Python developers.

### 7.3 `TODO()` raises a blank `Exception` — already noted ⚠️
Same issue as parser: `TODO(message="")` by default. All call sites should pass a meaningful message.

---

## 8. `utils/arg_utils.py`

### 8.1 `getopt` instead of `argparse` ⚠️
`getopt` is the low-level C-style option parser. `argparse` (stdlib since 2.7) provides:
- automatic `--help` generation
- type validation
- clearer error messages
- positional argument handling without manually checking `args`

This is a first-project choice that's worth updating.

### 8.2 `-v` / `--version` in help text but missing from `getopt` options string ❌
```python
opts, args = getopt.getopt(argv, "hpr:s:o:", ["profile", "rom=", ...])
```
`v`/`version` are shown in the help but not listed in the opts string, so passing `-v` falls through to the `GetoptError` handler and prints help instead of the version. Either remove it from the help text or add `"v"` and `"version"` to the `getopt` call.

### 8.3 `help()` shadows Python's built-in ⚠️
```python
def help():
    print(...)
    sys.exit()
```
`help` is a Python built-in. Shadowing it in the local scope is harmless here but is bad practice and surprising to readers. Rename to `print_help()` or `show_usage()`.

### 8.4 `injector` is imported and instantiated but never used ❌
```python
from injector import Injector, inject
_injector = Injector()
```
`_injector` is created but never used. Same pattern appears in several other utils files. Dead code — remove.

---

## 9. `utils/out_utils.py`

### 9.1 `OutUtils.__init__` parses `sys.argv` a second time ⚠️
```python
def __init__(self):
    args = arg_utils.parse()
    self._out = args.output_dir
```
`arg_utils.parse()` is called once in `main()` and again here in the `OutUtils` constructor. `sys.argv` is parsed twice. If the two calls ever disagree (e.g. after a future refactor), you get subtle bugs. Pass the `args` object in as a parameter instead of re-parsing.

### 9.2 `clean_out` removes then recreates the directory non-atomically ⚠️
```python
def clean_out(self):
    if os.path.exists(self._out) ...:
        shutil.rmtree(self._out)
    os.mkdir(self._out)
```
On a networked or shared filesystem there's a window between `rmtree` and `mkdir` where the directory doesn't exist. More importantly, if `rmtree` succeeds but `mkdir` fails for any reason, the output directory is gone. A safer pattern is to recreate the content inside it or use a temp directory + rename.

---

## Summary Table

| # | File | Issue | Severity |
|---|------|-------|----------|
| 1.1 | everscript.py | No `__main__` guard | ❌ |
| 1.2 | everscript.py | Module-level init runs on import | ❌ |
| 1.3 | everscript.py | Profile flag logic inverted | ⚠️ |
| 1.4 | everscript.py | `rom_file`/`patches_dir` unused in `handle_parse` | ⚠️ |
| 1.5 | everscript.py | Lexer runs twice | ⚠️ |
| 1.6 | everscript.py | `import os` inside function | ℹ️ |
| 2.1 | lexer.py | Duplicate `FUN_PATCH` token | ❌ |
| 2.2 | lexer.py | `<` and `>` defined twice | ❌ |
| 2.3 | lexer.py | `\n` token defined but unused | ⚠️ |
| 2.4 | lexer.py | `NAME_IDENTIFIER` requires ≥ 2 chars | ⚠️ |
| 3.1 | parser.py | All production functions named `parse` | ❌ |
| 3.2 | parser.py | `FUNCTION_CALL`/`FUNCTION_STRING` not in lexer | ❌ |
| 3.3 | parser.py | `TODO()` used with empty message | ⚠️ |
| 3.4 | parser.py | Scope pushed before map name is known | ⚠️ |
| 3.5 | parser.py | Native function lambdas lack bounds checking | ⚠️ |
| 4.1 | codegen.py | `_Splice` is dead code with bugs | ❌ |
| 4.2 | codegen.py | Debug `print` in `CodeGen.__init__` | ⚠️ |
| 4.3 | codegen.py | `get_function` searches three times, bug in scope variable | ❌ |
| 4.4 | codegen.py | `.format()` called with ignored second argument | ⚠️ |
| 4.5 | codegen.py | Hardcoded ROM addresses in `_wipe_strings` | ⚠️ |
| 4.6 | codegen.py | `correct_address` all TODO, undocumented | ⚠️ |
| 5.1 | linker.py | Module-level `_MapDataHandler` singleton | ℹ️ |
| 5.2 | linker.py | size==2 deletion logic appears buggy | ❌ |
| 5.3 | linker.py | Double space in `raise` | ℹ️ |
| 5.4 | linker.py | `link_function` does not deduplicate | ⚠️ |
| 6.1 | preprocessor.py | `import re` inside `_dir_sort_key` | ❌ |
| 6.2 | preprocessor.py | No cycle detection for recursive imports | ❌ |
| 6.3 | preprocessor.py | Diamond imports duplicate content | ⚠️ |
| 7.1 | ast_core.py | Cache uses `not params` — subtle semantics | ⚠️ |
| 7.2 | ast_core.py | `match self:` as type switch (unusual) | ℹ️ |
| 7.3 | ast_core.py | `TODO()` blank exception | ⚠️ |
| 8.1 | arg_utils.py | `getopt` instead of `argparse` | ⚠️ |
| 8.2 | arg_utils.py | `-v`/`--version` missing from getopt string | ❌ |
| 8.3 | arg_utils.py | `help()` shadows built-in | ⚠️ |
| 8.4 | arg_utils.py | `injector` imported but unused | ❌ |
| 9.1 | out_utils.py | `sys.argv` parsed twice | ⚠️ |
| 9.2 | out_utils.py | `clean_out` non-atomic rmtree + mkdir | ⚠️ |

**Severity key:** ❌ = real bug or will cause confusion / ⚠️ = code smell or latent bug / ℹ️ = style / minor

---

## Wishlist — Language & DX Improvements

Items added by the developer. Each has a recommendation and a rough implementation sketch.

---

### W1. `<<= 0d3` does not work (short decimal literals) 🔴 P1

**Symptom:** `x <<= 0d3` silently produces wrong output or a parse error, while `x <<= 0d0003` works.

**Root cause:** `Word.__init__` uses `len(value) >= 4` to decide whether a decimal literal is 1-byte or 2-bytes. `"3"` has length 1 → `_value_count = 1` (byte). `"0003"` has length 4 → `_value_count = 2` (word). When the shift operation's right-hand size is 1 byte, the calculator opcode picks the wrong type prefix (`0x02 = byte` vs `0x04 = word`), producing a different number of bytes in the output and mis-aligning everything that follows.

**Fix (small, standalone):** When `_value_count = 1` but the context is a compound-assignment operator (`<<=`, `>>=`, `*=`, etc.), the right-hand side is always a *shift amount* or *scale factor* — a byte is fine. The problem is only when an argument is supposed to be a 16-bit operand and you pass a 1-byte-sized literal. The cleanest fix without touching the whole type system is: **always infer size from the left-hand side in compound assignments.** In `parser.py` where `Asign(left, ShiftLeft(left, right))` is constructed, call `right.value._value_count = left.resolve(...).value_count()` or simply document and enforce that `0d3` is a legal byte-size shift amount.

**Better long-term fix:** See W2 (type system).

---

### W2. Parameter type safety in EverScript functions 🟠 P2

**Symptom:** `code(0x62, index, 0x0000 + to, 0x0000 + state, "...")` — the `0x0000 +` idiom is the only way to force a 16-bit word. Without it, if `to` resolves to a small value (≤ 0xFF), `Word.__init__` packs it as 1 byte and the `code()` call emits the wrong number of bytes.

**What's needed:** A way to declare that a parameter *must* be emitted as a specific size, regardless of value.

**Recommended design:**

Use the existing `T_BYTE` / `T_WORD` keywords as type annotations on function arguments:
```
fun tile_animate(index, Byte to, Word state) {
    code(0x62, index, to, state, "...");
}
```
- `Byte arg` → caller's value is padded/truncated to 1 byte when emitted
- `Word arg` → always 2 bytes (little-endian)
- `signed Byte arg` / `signed Word arg` → signed interpretation (already partially implemented via the `signed` prefix and operand codes `0x01`/`0x03`)

The type annotation on the arg declaration becomes the `_value_count` override for any `Word` or `Arg` AST node produced for that slot.

**What already exists:** The `SIGNED` keyword applied to `Arg` nodes (`expression.signed = True`), and the operand table already has `signed byte (0x01)`, `byte (0x02)`, `signed word (0x03)`, `word (0x04)`. The machinery is there — it just isn't wired to function argument declarations.

---

### W3. `signed` prefix is half-implemented 🟠 P2

**Symptom:** `signed arg[x]` sets `Arg.signed = True` in the parser, but it's unclear whether this flag propagates correctly through `calculate()` into the right operand code. The `Operand` table has both signed and unsigned variants for bytes and words, but the AST nodes (`Arg`, `Memory`) don't consistently check the `signed` flag when choosing the operand.

**Audit needed:** Trace the path from `signed Arg` → `Arg.calculate()` → `Operand("signed word" vs "read signed word")` and verify all branches emit the right opcode. If any branch falls through to the unsigned default, that's a silent wrong-value bug.

**Recommended action before W2:** Do this audit first, since W2 expands the use of signed/unsigned and must build on a correct foundation.

---

### W4. Python-side type safety 🟡 P3

**Symptom:** Type annotations exist (`linker:Linker`, `function:Function`, etc.) but are not enforced at runtime, and many parameters are typed as `any` or left unannotated. Errors appear as `AttributeError` deep in `_code()` rather than at the call site.

**What already exists:** Python type hints throughout the codebase. The `mypy` or `pyright` static type checker could be run today and would surface dozens of issues.

**Recommended steps:**
1. Run `mypy --ignore-missing-imports compiler/` and review the output.
2. Replace `any` annotations with specific types where known.
3. Add `assert isinstance(x, ExpectedType)` at the top of functions that are currently protected only by duck typing.
4. For the `Param` / `Identifier` ambiguity (callers pass either), define a union type `ParamLike = Param | Identifier`.

---

### W5. Named parameters in EverScript: `f(y=1)` 🟢 P4

**What's wanted:** Allow calling a function while only providing values for specific arguments by name, letting the rest default (or remain null).
```
fun move(x, y, speed) { ... };
move(y=10);   // only pass y, x and speed keep their default
```

**Current state:** The parser already has the `?` nullable marker on `FunctionArg` and the `Param(name, value)` infrastructure. The `handle_params` and `merge_params` methods in `Function_Base` partially implement this, but the call site in the parser (`NAME_IDENTIFIER ( param_list )`) wraps positional values in `Param(None, expr)` — name is always `None`.

**Implementation sketch:**
1. Add a new grammar rule: `named_param : IDENTIFIER = expression` → `Param(name, value)`.
2. Allow `param_list` to contain either `param` or `named_param`.
3. In `get_function` + the call-site lambda, match named params to the function's `arg_list` by name.
4. Error if a required (non-nullable) arg has no positional or named value.

This is a ~50-line parser change + `handle_params` fix.

---

### W6. Nullables in EverScript — `!= NONE` handling 🟢 P4

**What's wanted:** Clean nullable argument semantics. Today `arg? : EnumType` marks an arg as nullable, but checking `if(arg != NONE)` is described as broken or awkward.

**Current state:** The `?` marker exists on `FunctionArg`. The `Is` / `!IS` operators check `value == None` at the Python level. But `None` is not a first-class EverScript value, so comparing against it in generated code is not meaningful.

**Recommended design:** Nullable should mean *the argument slot was not filled at the call site*, not that the value at runtime is null. The compiler should:
- At compile time: if a nullable arg is not supplied, the code block that uses it is *skipped entirely* (conditional compilation, not runtime check).
- The `is None` / `!is None` tests should operate at compile time as `if arg was supplied { ... }`.

This eliminates the need for any `!= NONE` at the bytecode level.

---

### W7. Tests 🔵 P5

**What's wanted:** Tests for everything that makes sense.

**Recommended starting points** (easiest to hardest):

1. **Lexer unit tests:** Feed a string to `Lexer().get_lexer().lex()`, assert the token sequence. Easy, fast, catches regressions in lexer rule ordering. Start with the ambiguous cases: `<<` vs `<<=`, `--` vs `-`, `0d3` vs `0d0003`.

2. **`Word` / `BinaryOp` codegen unit tests:** Create a `Word(3)`, call `.code([])`, assert `"03"`. Then test `ShiftLeft(Arg(0), Word(3)).calculate(...)`. Catches the `0d3` class of bug and the `.format(x, 'x')` silent-no-op bug.

3. **Parser smoke tests:** Parse small EverScript snippets end-to-end and assert the AST structure or the raw patch output. Start with:
   - `x <<= 0d3;`
   - `if(x == 0x01) { ... }`
   - A single `fun` with one argument

4. **Preprocessor tests:** `preprocess("#import(\"file.evs\")", ...)` against a temp directory tree. Tests the sort order, `[group]` wrapping, and `_shared.evs` priority.

5. **Integration / golden-file tests:** Compile a known-good small `.evs` file and compare the IPS output byte-for-byte against a stored reference. Catches any silent regression anywhere in the pipeline.

**Suggested test runner:** `pytest` — already in the Python ecosystem, supports parameterization, fixtures, and good error output.

---

### W8. JavaDoc / docstrings 🔵 P5

**What's wanted:** Docstrings in Python and equivalent documentation in EverScript source (future).

**Current state:** No docstrings anywhere. Many function signatures use `any` or no type hints.

**Recommended approach:**
- Add docstrings to `Lexer`, `Parser`, `CodeGen`, `Linker`, `MemoryManager`, and the major AST classes.
- For EverScript itself, the language doesn't support doc comments yet. Add `//` comment support in the `fun` declaration syntax as a first step (the lexer already ignores `//.*\n` — just preserve it in a `Function.doc` field during parsing).
- Keep docs short and machine-maintainable. One-line summary + param table is enough.

---

### W9. Incremental compilation ⚪ P6

*Summarized from `docs/incremental-compilation.md`.*

**The core problem:** The compiler is a single-pass monolith. Every change recompiles everything. Address allocation is FIFO and order-dependent, so changing one room can shift every subsequent address — you can't safely recompile in isolation.

**Why it's P6:** This requires replacing the entire compilation model. It's the right long-term direction but has no quick fixes. Prerequisites are:
- Tests (W7) — to verify the new model produces identical output
- Type system (W2) — so the intermediate format knows sizes
- A relocatable intermediate format (new work)

**Rough target architecture:**
- Each `.evs` file compiles to a `.evo` object file (relocatable, addresses expressed as symbols)
- `kaizo.evs` becomes the linker script (memory pools, symbol assignments)
- Final link pass allocates addresses and resolves all symbol references

**Estimated complexity:** Large. Worth designing carefully before starting.

---

### W10. Per-script output folders — don't clobber other hacks 🟠 P2

**Symptom:** `out/` is wiped on every compile (`clean_out` calls `shutil.rmtree`). If you build Practice ROM, then compile EverScript, the Practice ROM is gone.

**Root cause:** `OutUtils.init_out()` always cleans the same single `out/` directory regardless of what script was compiled.

**Fix:** Derive the output folder from the input file name instead of hardcoding `out/`. For example:
```
everscript kaizo/main.evs  →  out/kaizo/
everscript practice/main.evs  →  out/practice/
```
Only the folder matching the current input is cleared. Other hacks under `out/` are untouched.

**Implementation:** Change `OutUtils._out` initialization to:
```python
self._out = os.path.join(args.output_dir, Path(args.input_file).stem)
```
`clean_out` then only removes `out/<script_name>/`, never the parent. One-line change + a test.

---

### W11. Circular include detection 🟠 P2

**Symptom:** File A `#import`s B, B `#import`s A → Python `RecursionError` with no useful message. Already noted as issue 6.2, but the developer confirms this happens in practice.

**How `#import` and `#include` differ:**
- `#import` is the preprocessor (static text substitution, in `preprocessor.py`).
- `#include` is parsed at the parser level (re-lexes and re-parses in `Include.eval()`).

**Both paths need cycle detection:**

For `#import`, pass a `frozenset` of already-resolved absolute paths through `_resolve_imports`:
```python
def _resolve_imports(source, base_dir, _depth=0, _visited=frozenset()):
    def replacer(match):
        abs_path = os.path.normpath(os.path.join(base_dir, match.group(1)))
        if abs_path in _visited:
            raise ImportError(f"Circular #import: {abs_path} already imported")
        ...
```
For `#include`, the `Include` class needs access to a per-compilation set of already-included files, stored on the `generator` or passed through.

---

### W12. Compiler game-agnosticism violations 🟡 P3

**Goal:** The compiler should be a general-purpose EverScript-to-IPS tool. The game-specific knowledge belongs in `in/core.evs` and `in/`, not in `compiler/`.

**Current violations found:**

| File | Line | Violation |
|------|------|-----------|
| `compiler/codegen.py` | `Memory(0x2265)`, `Memory(0x2266)`, `Memory(0x244c)` | SoE RAM addresses for map index, variant, and entrance index hardcoded in the map trigger generator |
| `compiler/linker.py` | `_MapDataHandler` / `MapData` | 127-entry SoE-specific map table with trigger counts and ROM addresses baked into the linker |
| `compiler/linker.py` | `address_trigger_enter_base = 0x92801b` | ROM address for SoE's trigger-enter dispatch table |
| `compiler/codegen.py` | `_wipe_strings` address `0x11d000`, `0x232D` | SoE string bank addresses |

**Recommended move:** All `MapData`, `MapDataHandler`, and the ROM constants in `codegen.py`/`linker.py` belong in a game config file (e.g. `in/core.evs` or a companion `game.json`). The compiler should receive these as declarations, not have them compiled in. This is the prerequisite for using EverScript on a different game.

---

### W13. Python performance — what's realistic 🟡 P3

**Context:** The compiler runs hundreds of times per day. Speed matters.

**What to check first (free wins):**

1. **`#include` rebuilds the lexer and parser from scratch every call.** `Include.eval()` calls `Lexer().get_lexer()`, `Parser(self.generator)`, `pg.parse()` on every `#include`. For `core.evs` this is a full re-parse of ~16K lines on every compile. **Fix:** Cache the built lexer (it's stateless). The parser is harder because it's tied to the `generator` instance, but the grammar itself is static — consider separating grammar compilation from generator binding.

2. **`Function_Base.code()` caching is already there** but only fires when `params=[]`. Verify hot paths actually hit the cache.

3. **rply is pure Python and relatively slow.** No easy fix here without changing libraries.

**Regarding Python-to-C++ (Cython / Nuitka / PyPy):**

- **PyPy** is the easiest experiment: install PyPy, run the compiler unchanged, compare wall-clock time. PyPy JIT-compiles hot loops and typically gives 3–10× speedup on compiler-like workloads with zero code changes. Main risk: rply's compatibility with PyPy (generally fine since rply is pure Python).
- **Nuitka** (`python -m nuitka --standalone everscript.py`) compiles to C and then to a native binary. You tried this before — the failure is usually missing imports or extension modules that Nuitka doesn't detect. The fix is typically adding `--include-package=rply` etc. Worth retrying with `--follow-imports` and checking the compilation log.
- **Cython** requires annotating hot functions with types. Only useful if you identify specific bottlenecks via profiling first. More work than PyPy.

**Recommended order:** Profile first (`--profile` flag already exists). Find the top-3 hot functions. Then try PyPy. If PyPy isn't enough, consider Nuitka.

---

### W14. `--override` flag for SYSTEM values at compile time 🟢 P4

**What's wanted:** Override named constants from `core.evs` on the command line, without editing the file.

**Example use case:** `core.evs` defines `SYSTEM.STARTING_ROOM = 0x38`. When testing, you want to start in room `0x12` without touching `core.evs`.

**Recommended design:**
```
everscript --override SYSTEM.STARTING_ROOM=0x12 kaizo/main.evs
```

**Implementation:** After `preprocess()` and before `parser.parse()`, inject a synthetic preamble that re-declares the overridden identifiers:
```python
overrides_code = "\n".join(f"val {k} = {v};" for k, v in args.overrides.items())
code = overrides_code + "\n" + code
```
If EverScript identifiers are scoped, this works because later `val` declarations shadow earlier ones. If not, the enum/constant lookup needs a "last wins" policy — which it already appears to have (see `get_function` search 3: "returns the last method with the same name").

---

### W15. `--room` / `--entrance` filter for faster iteration 🟢 P4

**What's wanted:** Compile only one specific room when testing, skipping all others. E.g.:
```
everscript --room 0x38 --entrance 0 kaizo/main.evs
```

**How it relates to incremental compilation (W9):** This is a lighter-weight version of the same idea. It doesn't require a relocatable object format — it just skips generating the other rooms' map functions.

**Implementation sketch:**
- Add `--room` / `--entrance` args.
- In `CodeGen._generate_map()`, filter `variants` to only the specified `map_index`.
- All `@weak` functions that are only reachable from the skipped rooms are automatically dead and won't be linked (this already partially works via `add_dependency`).
- Caveat: the output patch will be incomplete (missing other rooms), so it's only useful for testing that specific room, not for shipping.

**Relationship to `@weak`:** Functions annotated `@weak` are already excluded from compilation unless they're pulled in via `add_dependency`. The `@weak` machinery is the right foundation here — `--room` essentially makes all rooms *except* the target `@weak` for that build.

---

### W16. Dead code elimination / unused code 🟡 P3

**What's wanted:** Code that is never reachable should not be compiled into the patch.

**Current state:** `@weak` functions are excluded if nothing calls them (`installed_functions = [f for f in self.code if f.install and not f.weak]`). Functions added via `add_dependency` are included even if the call path is broken. There's no whole-program reachability analysis.

**Quick wins:**
1. Any `fun` that has `@weak` and no callers in `self.dependencies` is already skipped — this works.
2. Anonymous functions created internally (e.g. the map trigger wrappers) are always linked even if the map itself is excluded. Fixing this requires the map-filter from W15.
3. `map_code` functions are always emitted regardless of whether their room is reachable from the start.

**Deeper fix (requires W9):** True dead code elimination requires a call graph. Build the graph during codegen, do a reachability pass from all installed non-weak entry points, and exclude everything unreachable. This is standard in linkers and straightforward once the incremental format exists.

---

### W17. EverScript doc comments (JavaDoc-style) ⚪ P5

**What's wanted:** Document functions in-source:
```
/// @param x  X position in tile units
/// @param y  Y position in tile units
/// @returns  nothing
fun move_entity(x, y) { ... }
```

**What needs to change:**
1. **Lexer:** The current ignore rule strips `//.*\n`. Change it to preserve `///` lines and emit a `DOC_COMMENT` token.
2. **Parser:** Add a production rule that allows a `doc_comment_list` before a `function` declaration and attaches it to the `Function` AST node as `Function.doc`.
3. **Tooling:** The VS Code highlighter (`everscript-vscode`) can then display the doc on hover.

This is a clean, isolated feature. Lexer + parser change is ~20 lines each.

---

### W18. Alternative parsing approaches 🔵 P6

**Context:** This is a first compiler. Some things are done in an unusual way because they weren't known upfront.

**Observations about the current approach:**

- **rply (LALR parser):** Good choice for a real language. LALR parsers are robust and well-understood. The main cost is the opaque error messages from rply when a grammar is ambiguous (you get "unexpected token X" with no context). Consider wrapping the parser error to show surrounding source text.

- **Manual lexer rules (rply):** Also fine. The duplicate-token issues (issues 2.1, 2.2) are rply's rules-added-in-order behavior. A PEG parser (e.g. `lark` with `parser="earley"` or `parser="lalr"`) handles ambiguity more explicitly and produces better errors. Not worth switching now, but worth knowing.

- **AST by hand:** The `ast_core.py` + `ast_everscript.py` approach of building AST nodes as Python classes is standard and works well. Python's `dataclasses` or `attrs` would reduce boilerplate for simple node types (like `Word`, `Param`, `Identifier`) — they auto-generate `__init__`, `__repr__`, `__eq__`.

- **Code generation by string concatenation:** The current `_code()` → string approach works but makes optimization passes (dead-code, constant folding) harder because you've already lost structure. A proper IR (intermediate representation) — even a simple list of typed instructions — would make W16 and W9 much easier. This is the biggest architectural gap between "toy compiler" and "production compiler."

- **The calculator sub-language (opcodes 0x00–0x2f):** This is the most complex part. It's essentially a stack machine, and the current implementation assembles it by recursive `calculate()` calls that emit opcode sequences. This works but is hard to debug when it goes wrong. A proper stack-machine assembler with explicit push/pop tracking would catch mismatches (pushing 2 words but the operation expects 1).

---

### W19. The opcode table is incomplete and unverified ⚠️

**Context:** The `Operand._operands` and `Operand._opcodes` tables in `ast_core.py` were reverse-engineered from SoETilesViewer dumps. Several entries are commented out as "WARN: Invalid sub-instr" or left as `#_:`. The todo.md has untraced opcodes (`0x62`, `0x6c`, `0x47`, `0x78`, etc.).

**Risks:**
- A `code()` call with an opcode that happens to work in tested cases but misbehaves on edge cases.
- Missing opcodes mean some game behaviors are inaccessible from EverScript.

**Recommended action:**
- Keep a separate `docs/opcodes.md` that explicitly lists: known-good, known-bad, unknown, and untested opcodes.
- Add an assertion in `Operand.__init__` that raises a clear error if an unknown operand name is used, rather than silently producing wrong bytes.

---



### Sprint 1 — Fix bugs, delete dead code (no behavior change for working code)
1. `W1` — Fix `0d3` / short decimal in compound assignments (investigate and either fix or clearly document)
2. `4.1` — Delete `_Splice`
3. `2.1` — Remove duplicate `FUN_PATCH` token
4. `2.2` — Remove duplicate `<` / `>` tokens
5. `6.1` — Remove `import re` from `_dir_sort_key`
6. `4.2` — Remove `print("CodeGen.init()")` debug statement
7. `1.1` + `1.2` — Add `__main__` guard, move pipeline init into `main()`
8. `8.2` — Add `v`/`version` to getopt options string
9. `8.4` — Remove unused `injector` imports
10. `W10` — Per-script output folders (one-liner, prevents clobbering hacks)

### Sprint 2 — Code quality (makes the Python readable)
11. `4.3` — Fix `get_function` scope variable shadow bug
12. `4.4` — Replace `.format(x, 'x')` with f-strings throughout
13. `3.3` / `7.3` — Pass meaningful messages to `TODO()` everywhere
14. `1.3` — Fix profile flag inversion
15. `1.5` — Lex once, reuse for dump
16. `8.1` — Replace `getopt` with `argparse`
17. `9.1` — Stop parsing `sys.argv` twice
18. `W11` — Circular import detection (`#import` + `#include`)
19. `W13` — Profile, then try PyPy; retry Nuitka with `--follow-imports`
20. `W19` — Add assertion in `Operand.__init__` for unknown operand names

### Sprint 3 — Type safety audit (pre-req for W2)
21. `W3` — Audit `signed` prefix end-to-end
22. `W4` — Run mypy, fix critical type errors
23. `5.2` — Fix linker size==2 delete bug (requires understanding, test first)
24. `W12` — Identify and begin moving game-specific constants out of `compiler/`

### Sprint 4 — Language features
25. `W2` — EverScript argument type annotations (`Byte`, `Word`, `signed Byte`)
26. `W5` — Named parameters in EverScript (`f(y=1)`)
27. `W6` — Nullable compile-time semantics
28. `W14` — `--override` flag for SYSTEM values
29. `W15` — `--room` / `--entrance` filter for fast iteration
30. `W17` — EverScript doc comments (`///` → `DOC_COMMENT` token → `Function.doc`)

### Sprint 5 — Tests + docs
31. `W7` — Lexer unit tests
32. `W7` — Word/codegen unit tests
33. `W7` — Parser smoke tests
34. `W7` — Integration / golden-file tests
35. `W8` — Python docstrings
36. `W19` — `docs/opcodes.md` — known-good / unknown / untested opcode table

### Sprint 6 — Architecture
37. `W16` — Dead code elimination (call graph reachability pass)
38. `W18` — Evaluate IR / stack-machine assembler design (spike, not full implementation)
39. `W9` — Incremental compilation (design doc → prototype)
40. `W12` — Complete game-agnosticism refactor (move `MapDataHandler` + ROM constants to config)
