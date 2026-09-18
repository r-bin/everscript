"""Opcode 0x46: this."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x46")
def test_opcode_46_this_vanilla():
    """Opcode 0x46: this.

    Vanilla ROM examples from script_all:
      - [0x99b503] 46 00 09 0d 01 00 29 02 : UNTRACED INSTR, Open messagebox? slot=0x00 x=0x09 y=0x0d w=0x01 h=0x00
      - [0x92835e] 46 02 31 46 02 4f 46 02 : UNTRACED INSTR, Open messagebox? slot=0x02 x=0x31 y=0x46 w=0x02 h=0x4f
      - [0x928364] 46 02 6d 46 02 8b 46 02 : UNTRACED INSTR, Open messagebox? slot=0x02 x=0x6d y=0x46 w=0x02 h=0x8b
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x46 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x09 y=0x0d w=0x01 h=0x00)
        eval("46 00 09 0D 01 00 29 02");
    """

    expected = """
        46 00 09 0D 01 00 29 02    // (0x46) UNTRACED INSTR, Open messagebox? slot=0x00 x=0x09 y=0x0d w=0x01 h=0x00
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x46")
def test_opcode_46_this_variations():
    """Variations for Opcode 0x46:
      Variation 1: [0x99b503] 46 00 09 0d 01 00 29 02 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x09 y=0x0d w=0x01 h=0x00)
      Variation 2: [0x92835e] 46 02 31 46 02 4f 46 02 (UNTRACED INSTR, Open messagebox? slot=0x02 x=0x31 y=0x46 w=0x02 h=0x4f)
      Variation 3: [0x928364] 46 02 6d 46 02 8b 46 02 (UNTRACED INSTR, Open messagebox? slot=0x02 x=0x6d y=0x46 w=0x02 h=0x8b)
      Variation 4: [0x92836a] 46 02 a9 46 02 c7 46 02 (UNTRACED INSTR, Open messagebox? slot=0x02 x=0xa9 y=0x46 w=0x02 h=0xc7)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
