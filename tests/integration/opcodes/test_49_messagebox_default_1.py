"""Opcode 0x49: ."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x49")
def test_opcode_49_opcode_49_vanilla():
    """Opcode 0x49: .

    Vanilla ROM examples from script_all:
      - [0xa1ddbf] 49 c3 d0 9b 20 33 71 9b : UNTRACED INSTR, Open default messagebox?
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x49 (UNTRACED INSTR, Open default messagebox?)
        eval("49 C3 D0 9B 20 33 71 9B");
    """

    expected = """
        49 C3 D0 9B 20 33 71 9B    // (0x49) UNTRACED INSTR, Open default messagebox?
    """

    assert_evs_bytes(script, expected)
