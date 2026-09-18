"""Opcode 0xA0: show currecny amount according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xA0")
def test_opcode_a0_show_currecny_amount_according_to_darkmoon_vanilla():
    """Opcode 0xA0: show currecny amount according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x969a9f] a0 51 87 0f 1d 69 00 30 : SHOW CURRENCY AMOUNT
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xA0 (SHOW CURRENCY AMOUNT)
        eval("A0 51 87 0F 1D 69 00 30");
    """

    expected = """
        A0 51 87 0F 1D 69 00 30    // (0xA0) SHOW CURRENCY AMOUNT
    """

    assert_evs_bytes(script, expected)
