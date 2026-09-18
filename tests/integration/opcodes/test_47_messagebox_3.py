"""Opcode 0x47: and this are the same as 0x44."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x47")
def test_opcode_47_and_this_are_the_same_as_0x44_vanilla():
    """Opcode 0x47: and this are the same as 0x44.

    Vanilla ROM examples from script_all:
      - [0x95df8e] 47 00 0c 13 14 08 51 44 : UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0c y=0x13 w=0x14 h=0x08
      - [0x99dc87] 47 00 04 14 1b 07 51 aa : UNTRACED INSTR, Open messagebox? slot=0x00 x=0x04 y=0x14 w=0x1b h=0x07
      - [0x99de7a] 47 00 04 17 1b 03 a7 10 : UNTRACED INSTR, Open messagebox? slot=0x00 x=0x04 y=0x17 w=0x1b h=0x03
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x47 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0c y=0x13 w=0x14 h=0x08)
        eval("47 00 0C 13 14 08 51 44");
    """

    expected = """
        47 00 0C 13 14 08 51 44    // (0x47) UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0c y=0x13 w=0x14 h=0x08
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x47")
def test_opcode_47_and_this_are_the_same_as_0x44_variations():
    """Variations for Opcode 0x47:
      Variation 1: [0x95df8e] 47 00 0c 13 14 08 51 44 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0c y=0x13 w=0x14 h=0x08)
      Variation 2: [0x99dc87] 47 00 04 14 1b 07 51 aa (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x04 y=0x14 w=0x1b h=0x07)
      Variation 3: [0x99de7a] 47 00 04 17 1b 03 a7 10 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x04 y=0x17 w=0x1b h=0x03)
      Variation 4: [0x99debd] 47 00 04 10 18 04 09 07 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x04 y=0x10 w=0x18 h=0x04)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
