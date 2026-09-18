"""Opcode 0x4A: ."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x4A")
def test_opcode_4a_opcode_4a_vanilla():
    """Opcode 0x4A: .

    Vanilla ROM examples from script_all:
      - [0xa481ab] 4a 00 50 00 56 00 5c 00 : UNTRACED INSTR, Open default messagebox?
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x4A (UNTRACED INSTR, Open default messagebox?)
        eval("4A 00 50 00 56 00 5C 00");
    """

    expected = """
        4A 00 50 00 56 00 5C 00    // (0x4A) UNTRACED INSTR, Open default messagebox?
    """

    assert_evs_bytes(script, expected)
