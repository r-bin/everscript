"""Opcode 0x9F: prepare currecny display according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x9F")
def test_opcode_9f_prepare_currecny_display_according_to_darkmoon_vanilla():
    """Opcode 0x9F: prepare currecny display according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x969a9e] 9f a0 51 87 0f 1d 69 00 : PREPARE CURRENCY DISPLAY
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x9F (PREPARE CURRENCY DISPLAY)
        eval("9F A0 51 87 0F 1D 69 00");
    """

    expected = """
        9F A0 51 87 0F 1D 69 00    // (0x9F) PREPARE CURRENCY DISPLAY
    """

    assert_evs_bytes(script, expected)
