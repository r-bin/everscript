"""Opcode 0xAA: according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_aa_according_to_darkmoon():
    """Opcode 0xAA: according to darkmoon."""
    script = """
        clear_status_effects();
    """

    expected = """
        AA
    """

    assert_evs_bytes(script, expected)
