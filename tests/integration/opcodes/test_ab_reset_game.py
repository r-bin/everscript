"""Opcode 0xAB: according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_ab_according_to_darkmoon():
    """Opcode 0xAB: according to darkmoon."""
    script = """
        reboot();
    """

    expected = """
        AB
    """

    assert_evs_bytes(script, expected)
