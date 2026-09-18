---
name: compiler-testing
description: Explains how to execute and write unit tests in tests/ using pytest, verify parser conflicts, and validate compiler regressions.
---

# Compiler Testing & Quality Assurance

The Everscript test suite ensures that modifications to the lexer, parser, AST nodes, or codegen do not introduce regressions into the compilation pipeline.

---

## 1. Test Suite Organization

Tests are organized into two primary tiers under [tests/](file:///Users/v/Documents/GitHub/everscript/tests/) and run via **pytest**:

### A. Compiler Module Tests (`tests/compiler/` mirroring `compiler/`):
Fast unit tests targeting individual compiler components in isolation:
| Test File | Target Module | Scope & Typical Checks |
|---|---|---|
| `test_lexer.py` | `compiler/lexer.py` | Tokenization regexes, keywords, hex/decimal literals, comments |
| `test_parser.py` | `compiler/parser.py` | Grammar rules, LALR conflict monitoring, AST node generation |
| `test_preprocessor.py` | `compiler/preprocessor.py` | `#include` / `#import` resolution, relative paths, circular guards |
| `test_ast_core.py` | `compiler/ast_core.py` | 16-bit hex/decimal conversion, `Word` sizing, byte splitting |
| `test_codegen.py` | `compiler/codegen.py` | Jump distance calculation, branch skipping, codegen contracts |

### B. Opcode Integration Tests (`tests/integration/opcodes/`):
Integration tests verifying bytecode generation for the Secret of Evermore VM instruction set.
- **Strict 1 file per opcode rule**: Each opcode has its own test file named `test_<hex_2_digits>_<mnemonic>.py`.
- **Examples:** `test_00_end.py`, `test_08_branch_if.py`, `test_09_branch_if_not.py`, `test_22_change_map.py`, `test_3a_yield.py`.
- Uses shared pipeline compilation helpers from `tests/helpers.py`.

### C. Map Decompression Integration Tests (`tests/integration/maps/`):
Integration tests verifying ROM map decompression pipelines against ground-truth Mesen2 PPU Memory Viewer dumps.
- **Strict 1 file per map rule**: Each verified map has its own test file named `test_room_<hex_2_digits>_vram.py`.
- **Example:** `test_room_0x33_vram.py` tests Strong Heart's Exterior ($20 \times 16$) header, tile palette, metatiles, and VRAM words against emulator dumps.
- Uses extraction routines from `tools/dump_room.py`.

---

## 2. Executing Tests

Always use the Python binary inside the virtual environment:

```bash
# Run all tests
.venv/bin/pytest tests/

# Run compiler module tests (fastest, ~15s)
.venv/bin/pytest tests/compiler/

# Run all opcode integration tests (~1.5m)
.venv/bin/pytest tests/integration/opcodes/

# Run map decompression VRAM regression tests
.venv/bin/pytest tests/integration/maps/

# Run a specific test with verbose output
.venv/bin/pytest tests/integration/maps/test_room_0x33_vram.py -v
```

### Baseline Targets:
- **Test Count:** ~165+ tests passing across compiler and opcode suites.
- **Parser Conflicts:** 427 Shift/Reduce conflicts, 174 Reduce/Reduce conflicts.
- Any change that increases the number of parser conflicts indicates newly introduced grammar ambiguity and must be investigated.

---

## 3. Rules for Creating Tests

### Rule 1: Where to Place New Tests
1. **Adding a unit test for a compiler module?**
   - Place in `tests/compiler/test_<module>.py` mirroring the module in `compiler/`.
   - Test functions or classes in isolation without invoking `#include("in/core")` unless required.
2. **Adding or verifying a VM Opcode?**
   - **MUST** be placed in `tests/integration/opcodes/test_<hex_2_digits>_<name>.py`.
   - Never combine unrelated opcodes into a scratchpad file.
   - Use lowercase 2-digit hex prefix (e.g. `00`, `0c`, `a7`, `b4`).
3. **Testing multi-statement control flow or compiler mechanics?**
   - Place in `tests/compiler/test_codegen.py` (e.g., nested `if/else`, while loops, forward jump counting).

### Rule 2: Opcode Test Structure & Conventions
Every opcode test file should follow this standard template:

```python
"""Opcode 0x00: end.

Opcode 0x00: END / return.
"""

from tests.helpers import assert_evs_bytes


def test_opcode_00_end():
    """Opcode 0x00: END / return."""
    assert_evs_bytes("end();", "00 // (00) END")
```

- **Docstring**: Always state the opcode hex and mnemonic.
- **Helper**: Always import and use `assert_evs_bytes` from `tests.helpers`.
- **Comments in Expected Bytes**: Include disassembler-style comments explaining each emitted byte:
  ```python
  assert_evs_bytes(
      "if(<ACTIVE> == <BOY>) { end(); }",
      "09 52 29 50 A2 01 00 00 // 09=if, 52=ACTIVE, 29 50=BOY, A2===, 01 00=skip 1, 00=end"
  )
  ```
- **Custom Function Name**: If testing a multi-function snippet with `@install`, provide `name="<fn_name>"` to `assert_evs_bytes`:
  ```python
  code = """
  @install()
  fun target(a) { yield(); }
  fun test_af() { target(0x12); }
  """
  assert_evs_bytes(code, "AF 01 E2 xx xx xx // AF=call params", name="test_af")
  ```

### Rule 3: Exact Science & Empirical Verification (`AGENTS.md`)
1. **Never guess expected bytes**: Verify against `script_all` dump or Mesen2 debugger trace logs.
2. **Calculator Opcode Inversions**:
   - `A2` = `==` (`0x22 | 0x80`)
   - `A3` = `!=` (`0x23 | 0x80`)
   - Opcode `09` is `BRANCH_IF_NOT` (skips if condition is false).
3. **Explicit Mismatch Handling**: If a test documents a known compiler quirk, discrepancy, or upstream bug, annotate it explicitly:
   ```python
   @pytest.mark.xfail(reason="MISMATCH: <description of discrepancy>")
   def test_opcode_bug_repro():
       ...
   ```
