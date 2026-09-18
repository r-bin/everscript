"""Opcode 0xBD: hope this is right."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_bd_hope_this_is_right():
    """Opcode 0xBD: hope this is right."""
    script = """
        control(BOY, False);
    """

    expected = """
        BD
    """

    assert_evs_bytes(script, expected)
