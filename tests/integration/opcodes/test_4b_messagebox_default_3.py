"""Opcode 0x4B: ."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x4B")
def test_opcode_4b_opcode_4b_vanilla():
    """Opcode 0x4B: .

    Vanilla ROM examples from script_all:
      - [0xa080cd] 4b 0f 23 25 27 26 4e 0f : UNTRACED INSTR, Open default messagebox?
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x4B (UNTRACED INSTR, Open default messagebox?)
        eval("4B 0F 23 25 27 26 4E 0F");
    """

    expected = """
        4B 0F 23 25 27 26 4E 0F    // (0x4B) UNTRACED INSTR, Open default messagebox?
    """

    assert_evs_bytes(script, expected)
