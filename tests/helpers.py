"""Shared bytecode compilation and verification helpers for Everscript tests."""

import re
from compiler.lexer import Lexer
from compiler.linker import Linker
from compiler.codegen import CodeGen
from compiler.parser import Parser
from utils.file_utils import file_utils


def clean_byte_string(byte_str: str) -> str:
    """Normalize a bytecode string by stripping comments, collapsing whitespace, and uppercasing hex tokens."""
    # Strip line comments (// ...)
    byte_str = re.sub(r"//.*", "", byte_str)
    # Strip block comments (/* ... */)
    byte_str = re.sub(r"/\*.*?\*/", "", byte_str, flags=re.DOTALL)
    # Convert hex tokens to uppercase
    byte_str = byte_str.upper()
    # Collapse all whitespace into single space
    byte_str = re.sub(r"\s+", " ", byte_str).strip()
    return byte_str


def compile_snippet(evs_code: str, name: str = "_test_snippet") -> str:
    """Compile an EVS code snippet and return the cleaned bytecode string."""
    if "fun " not in evs_code:
        full_source = f"""
#include("in/core")
fun {name}() {{
    {evs_code}
}}
"""
    else:
        full_source = evs_code
        if "#include" not in evs_code and "#import" not in evs_code:
            full_source = '#include("in/core")\n' + full_source

    linker = Linker()
    generator = CodeGen(linker)
    pg = Parser(generator)
    pg.parse()
    parser = pg.get_parser()
    lexer = Lexer().get_lexer()

    parser.parse(lexer.lex(full_source))

    fn = generator.current_scope().functions.get(name)
    if fn is None:
        for k in reversed(list(generator.current_scope().functions.keys())):
            if k != "_trigger_nop":
                fn = generator.current_scope().functions[k]
                break

    if fn is None:
        raise ValueError(f"No function generated for snippet: {evs_code}")

    raw_code = fn.code([])
    return file_utils.clean(raw_code)


def compare_evs_bytes(evs_code: str, expected_bytes: str, name: str = "_test_snippet") -> bool:
    """Return True if the compiled bytecode matches expected_bytes, False otherwise."""
    try:
        actual_clean = clean_byte_string(compile_snippet(evs_code, name=name))
        expected_clean = clean_byte_string(expected_bytes)
        return actual_clean == expected_clean
    except Exception:
        return False


def assert_evs_bytes(evs_code: str, expected_bytes: str, name: str = "_test_snippet"):
    """Assert that the compiled bytecode for an EVS snippet matches expected_bytes."""
    actual = compile_snippet(evs_code, name=name)
    actual_clean = clean_byte_string(actual)
    expected_clean = clean_byte_string(expected_bytes)

    assert actual_clean == expected_clean, (
        f"\nBytecode mismatch for EVS snippet:\n  {evs_code.strip()}\n"
        f"Expected: {expected_clean}\n"
        f"Actual:   {actual_clean}\n"
    )

