"""Opcode 0x48: according to darkmoon the same as 44 but default values instead of operands."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x48")
def test_opcode_48_according_to_darkmoon_the_same_as_44_but_default_values_instead_of_operands_vanilla():
    """Opcode 0x48: according to darkmoon the same as 44 but default values instead of operands.

    Vanilla ROM examples from script_all:
      - [0xa7e601] 48 18 39 0e 0d 8c 9b 12 : UNTRACED INSTR, Open default messagebox?
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x48 (UNTRACED INSTR, Open default messagebox?)
        eval("48 18 39 0E 0D 8C 9B 12");
    """

    expected = """
        48 18 39 0E 0D 8C 9B 12    // (0x48) UNTRACED INSTR, Open default messagebox?
    """

    assert_evs_bytes(script, expected)
