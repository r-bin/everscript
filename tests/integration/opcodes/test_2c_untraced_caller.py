"""Opcode 0x2C: ."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x2C")
def test_opcode_2c_opcode_2c_vanilla():
    """Opcode 0x2C: .

    Vanilla ROM examples from script_all:
      - [0x94c381] 2c 08 77 ae a7 08 76 8d : UNTRACED INSTR for script caller (0x08)
      - [0xacfc02] 2c 80 35 2c 54 93 19 04 : UNKNOWN INSTR, arg 0x80
      - [0xa0d703] 2c 28 a7 e3 e6 89 59 26 : UNKNOWN INSTR, arg 0x28
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x2C (UNTRACED INSTR for script caller (0x08))
        eval("2C 08 77 AE A7 08 76 8D");
    """

    expected = """
        2C 08 77 AE A7 08 76 8D    // (0x2C) UNTRACED INSTR for script caller (0x08)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x2C")
def test_opcode_2c_opcode_2c_variations():
    """Variations for Opcode 0x2C:
      Variation 1: [0x94c381] 2c 08 77 ae a7 08 76 8d (UNTRACED INSTR for script caller (0x08))
      Variation 2: [0xacfc02] 2c 80 35 2c 54 93 19 04 (UNKNOWN INSTR, arg 0x80)
      Variation 3: [0xa0d703] 2c 28 a7 e3 e6 89 59 26 (UNKNOWN INSTR, arg 0x28)
      Variation 4: [0xa49847] 2c 9c 76 4d 1f 15 6b 0a (UNKNOWN INSTR, arg 0x9c)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
