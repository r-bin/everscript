"""Opcode 0xA1: hide currency display according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xA1")
def test_opcode_a1_hide_currency_display_according_to_darkmoon_vanilla():
    """Opcode 0xA1: hide currency display according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x969aae] a1 a6 fc e5 04 68 00 0a : HIDE CURRENCY DISPLAY
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xA1 (HIDE CURRENCY DISPLAY)
        eval("A1 A6 FC E5 04 68 00 0A");
    """

    expected = """
        A1 A6 FC E5 04 68 00 0A    // (0xA1) HIDE CURRENCY DISPLAY
    """

    assert_evs_bytes(script, expected)
