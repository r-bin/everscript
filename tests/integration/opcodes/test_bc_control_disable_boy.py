"""Opcode 0xBC: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_bc_opcode_bc():
    """Opcode 0xBC: ."""
    script = """
        control(BOY, True);
    """

    expected = """
        BC
    """

    assert_evs_bytes(script, expected)
