"""Opcode 0x5A: unknown, checks timer of unframed messages."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_5a_unknown_checks_timer_of_unframed_messages():
    """Opcode 0x5A: unknown, checks timer of unframed messages."""
    script = """
        clear_subtext();
    """

    expected = """
        5A
    """

    assert_evs_bytes(script, expected)
