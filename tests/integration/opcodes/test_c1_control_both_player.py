"""Opcode 0xC1: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_c1_opcode_c1():
    """Opcode 0xC1: ."""
    script = """
        control(CHARACTER.BOTH);
    """

    expected = """
        C1
    """

    assert_evs_bytes(script, expected)
