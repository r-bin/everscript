"""Opcode 0xBE: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_be_opcode_be():
    """Opcode 0xBE: ."""
    script = """
        control(DOG, True);
    """

    expected = """
        BE
    """

    assert_evs_bytes(script, expected)
