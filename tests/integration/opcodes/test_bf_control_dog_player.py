"""Opcode 0xBF: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_bf_opcode_bf():
    """Opcode 0xBF: ."""
    script = """
        control(DOG, False);
    """

    expected = """
        BF
    """

    assert_evs_bytes(script, expected)
