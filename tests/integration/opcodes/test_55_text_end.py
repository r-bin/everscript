"""Opcode 0x55: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_55_opcode_55():
    """Opcode 0x55: ."""
    script = """
        text_end();
    """

    expected = """
        55
    """

    assert_evs_bytes(script, expected)
