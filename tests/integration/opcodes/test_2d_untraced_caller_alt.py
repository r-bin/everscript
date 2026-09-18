"""Opcode 0x2D: oppisite of 2c?."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x2D")
def test_opcode_2d_oppisite_of_2c_vanilla():
    """Opcode 0x2D: oppisite of 2c?.

    Vanilla ROM examples from script_all:
      - [0x94c3af] 2d 08 80 00 a3 32 09 d7 : UNTRACED INSTR for script caller (0x08)
      - [0xad9001] 2d 00 37 ae 04 a0 02 68 : UNKNOWN INSTR, arg 0x00
      - [0xa4803d] 2d 2b b4 03 04 2a 05 2b : UNKNOWN INSTR, arg 0x2b
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x2D (UNTRACED INSTR for script caller (0x08))
        eval("2D 08 80 00 A3 32 09 D7");
    """

    expected = """
        2D 08 80 00 A3 32 09 D7    // (0x2D) UNTRACED INSTR for script caller (0x08)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x2D")
def test_opcode_2d_oppisite_of_2c_variations():
    """Variations for Opcode 0x2D:
      Variation 1: [0x94c3af] 2d 08 80 00 a3 32 09 d7 (UNTRACED INSTR for script caller (0x08))
      Variation 2: [0xad9001] 2d 00 37 ae 04 a0 02 68 (UNKNOWN INSTR, arg 0x00)
      Variation 3: [0xa4803d] 2d 2b b4 03 04 2a 05 2b (UNKNOWN INSTR, arg 0x2b)
      Variation 4: [0xa080ea] 2d 5a 0f 4d 28 4e 2d 5d (UNKNOWN INSTR, arg 0x5a)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
