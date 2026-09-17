"""Tests for compiler/codegen.py — code generation internals, scopes, and helper contracts."""

from compiler.codegen import Scope
from tests.helpers import compare_evs_bytes


# ---------------------------------------------------------------------------
# Helper Contracts
# ---------------------------------------------------------------------------

def test_compare_evs_bytes_contract():
    """Verify compare_evs_bytes returns True on match and False on mismatch/failure."""
    script = """
        end();
    """

    expected = """
        00      // (00) END
    """

    assert compare_evs_bytes(script, expected) is True
    assert compare_evs_bytes(script, "FF // wrong bytes") is False
    assert compare_evs_bytes("invalid_syntax{{{", "00") is False


# ---------------------------------------------------------------------------
# Codegen Scope & Internal Tests
# ---------------------------------------------------------------------------

def test_scope_types():
    """Verify Scope.Type enum definitions."""
    assert Scope.Type.DEFAULT == "DEFAULT"
    assert Scope.Type.MAP == "MAP"
    assert Scope.Type.AREA == "AREA"
    assert Scope.Type.OBJECT == "OBJECT"
    assert Scope.Type.NATIVE_FUNCTION == "NATIVE_FUNCTION"
