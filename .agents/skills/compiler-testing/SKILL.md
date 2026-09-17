---
name: compiler-testing
description: Explains how to execute and write unit tests in tests/ using pytest, verify parser conflicts, and validate compiler regressions.
---

# Compiler Testing & Quality Assurance

The Everscript test suite ensures that modifications to the lexer, parser, AST nodes, or codegen do not introduce regressions into the compilation pipeline.

---

## 1. Test Suite Organization

All tests are located in [tests/](file:///Users/v/Documents/GitHub/everscript/tests/) and run via **pytest**:

| Test File | Primary Scope | Typical Checks |
|---|---|---|
| `test_lexer.py` | Tokenization (`compiler/lexer.py`) | Regex pattern matching, keywords, hex literals, raw strings |
| `test_parser_smoke.py` | Parser construction (`compiler/parser.py`) | LALR(1) table build, conflict monitoring, basic grammar rules |
| `test_preprocessor.py` | AST Preprocessing (`compiler/preprocessor.py`) | `#include` resolution, path handling, recursive inlining |
| `test_word.py` | Data Types (`compiler/ast_core.py`) | 16-bit hex/decimal parsing, byte splitting, endianness |

---

## 2. Executing Tests

Always use the Python binary inside the virtual environment:

```bash
# Run all tests
.venv/bin/pytest tests/

# Run a specific test module
.venv/bin/pytest tests/test_lexer.py

# Run with verbose output and test names
.venv/bin/pytest -v tests/

# Run a specific test function by name
.venv/bin/pytest -k "test_hex_pairs"
```

### Baseline Targets:
- **Test Count:** 130 passing tests.
- **Parser Conflicts:** 427 Shift/Reduce conflicts, 174 Reduce/Reduce conflicts.
- Any change that increases the number of parser conflicts indicates newly introduced grammar ambiguity and must be investigated.

---

## 3. Writing New Compiler Tests

When adding a new AST feature, helper function, or fixing a bug:

1. **Create or select the appropriate test file** in `tests/` prefixed with `test_`.
2. **Import test fixtures and compiler modules:**
   ```python
   import pytest
   from compiler.lexer import Lexer
   from compiler.ast_core import _hex_pairs, Word

   def test_hex_pairs_helper():
       assert _hex_pairs("AABBCC") == ["AA", "BB", "CC"]
       assert _hex_pairs("12") == ["12"]
       assert _hex_pairs("") == []
   ```
3. **Smoke Testing Full Script Compilation:**
   To test that a snippet compiles without crashing:
   ```python
   from everscript import handle_parse

   def test_custom_branch_compilation():
       script = """
       fun test() {
           if (<0x225d, 0x08>) {
               <0x0a35> = 500;
           }
       }
       """
       # Verify it compiles through the pipeline without exception
       handle_parse("test_script", script)
   ```
