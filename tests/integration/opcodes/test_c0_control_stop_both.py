"""Opcode 0xC0: see 2A."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_c0_see_2a():
    """Opcode 0xC0: see 2A."""
    script = """
        control(CHARACTER.NONE);
    """

    expected = """
        C0
    """

    assert_evs_bytes(script, expected)
