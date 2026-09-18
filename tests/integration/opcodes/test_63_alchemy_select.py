"""Opcode 0x63: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_63_opcode_63():
    """Opcode 0x63: ."""
    script = """
        select_alchemy();
    """

    expected = """
        63
    """

    assert_evs_bytes(script, expected)
