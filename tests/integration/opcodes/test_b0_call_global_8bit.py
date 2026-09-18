"""Opcode 0xB0: same args as b2, read below // TODO: trace."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xB0")
def test_opcode_b0_same_args_as_b2_read_below_todo_trace_vanilla():
    """Opcode 0xB0: same args as b2, read below // TODO: trace.

    Vanilla ROM examples from script_all:
      - [0x92d344] b0 01 82 78 56 09 85 95 : CALL Global (8bit) script 0x56 ("Unnamed Global script 0x56")
      - [0x9daf02] b0 75 5a 9e 0a f1 03 14 : WRITE TO ARGS from 117 sub-instrs:
      - [0xa8ce01] b0 a0 43 28 50 ce 77 30 : WRITE TO ARGS from 160 sub-instrs:
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xB0 (CALL Global (8bit) script 0x56 ("Unnamed Global script 0x56"))
        eval("B0 01 82 78 56 09 85 95");
    """

    expected = """
        B0 01 82 78 56 09 85 95    // (0xB0) CALL Global (8bit) script 0x56 ("Unnamed Global script 0x56")
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xB0")
def test_opcode_b0_same_args_as_b2_read_below_todo_trace_variations():
    """Variations for Opcode 0xB0:
      Variation 1: [0x92d344] b0 01 82 78 56 09 85 95 (CALL Global (8bit) script 0x56 ("Unnamed Global script 0x56"))
      Variation 2: [0x9daf02] b0 75 5a 9e 0a f1 03 14 (WRITE TO ARGS from 117 sub-instrs:)
      Variation 3: [0xa8ce01] b0 a0 43 28 50 ce 77 30 (WRITE TO ARGS from 160 sub-instrs:)
      Variation 4: [0x99b517] b0 04 30 00 09 0d 01 00 (CALL Global (8bit) script 0x06 ("Unnamed Global script 0x06"))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
