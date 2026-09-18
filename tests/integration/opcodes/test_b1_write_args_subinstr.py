"""Opcode 0xB1: same args as b3, read below // TODO: trace."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xB1")
def test_opcode_b1_same_args_as_b3_read_below_todo_trace_vanilla():
    """Opcode 0xB1: same args as b3, read below // TODO: trace.

    Vanilla ROM examples from script_all:
      - [0xa0ea0a] b1 99 cb bc e7 e8 70 31 : WRITE TO ARGS from 153 sub-instrs:
      - [0x9bdd03] b1 5c e1 b1 5c e2 b1 5c : WRITE TO ARGS from 92 sub-instrs:
      - [0x94d1a6] b1 a3 04 50 00 22 08 55 : WRITE TO ARGS from 163 sub-instrs:
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xB1 (WRITE TO ARGS from 153 sub-instrs:)
        eval("B1 99 CB BC E7 E8 70 31");
    """

    expected = """
        B1 99 CB BC E7 E8 70 31    // (0xB1) WRITE TO ARGS from 153 sub-instrs:
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xB1")
def test_opcode_b1_same_args_as_b3_read_below_todo_trace_variations():
    """Variations for Opcode 0xB1:
      Variation 1: [0xa0ea0a] b1 99 cb bc e7 e8 70 31 (WRITE TO ARGS from 153 sub-instrs:)
      Variation 2: [0x9bdd03] b1 5c e1 b1 5c e2 b1 5c (WRITE TO ARGS from 92 sub-instrs:)
      Variation 3: [0x94d1a6] b1 a3 04 50 00 22 08 55 (WRITE TO ARGS from 163 sub-instrs:)
      Variation 4: [0x9a8004] b1 0c 28 04 b1 95 8d 01 (WRITE TO ARGS from 12 sub-instrs:)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
