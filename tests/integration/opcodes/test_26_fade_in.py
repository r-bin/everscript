"""Opcode 0x26: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_26_opcode_26():
    """Opcode 0x26: ."""
    script = """
        _fade_in();
    """

    expected = """
        26
    """

    assert_evs_bytes(script, expected)
