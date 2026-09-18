"""Opcode 0x45: according to darkmoon, this,."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x45")
def test_opcode_45_according_to_darkmoon_this_vanilla():
    """Opcode 0x45: according to darkmoon, this,.

    Vanilla ROM examples from script_all:
      - [0x928352] 45 02 b9 45 02 d7 45 02 : UNTRACED INSTR, Open messagebox? slot=0x02 x=0xb9 y=0x45 w=0x02 h=0xd7
      - [0x928358] 45 02 f5 45 02 13 46 02 : UNTRACED INSTR, Open messagebox? slot=0x02 x=0xf5 y=0x45 w=0x02 h=0x13
      - [0xa080bb] 45 0f 0e 10 10 12 48 0f : UNTRACED INSTR, Open messagebox? slot=0x0f x=0x0e y=0x10 w=0x10 h=0x12
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x45 (UNTRACED INSTR, Open messagebox? slot=0x02 x=0xb9 y=0x45 w=0x02 h=0xd7)
        eval("45 02 B9 45 02 D7 45 02");
    """

    expected = """
        45 02 B9 45 02 D7 45 02    // (0x45) UNTRACED INSTR, Open messagebox? slot=0x02 x=0xb9 y=0x45 w=0x02 h=0xd7
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x45")
def test_opcode_45_according_to_darkmoon_this_variations():
    """Variations for Opcode 0x45:
      Variation 1: [0x928352] 45 02 b9 45 02 d7 45 02 (UNTRACED INSTR, Open messagebox? slot=0x02 x=0xb9 y=0x45 w=0x02 h=0xd7)
      Variation 2: [0x928358] 45 02 f5 45 02 13 46 02 (UNTRACED INSTR, Open messagebox? slot=0x02 x=0xf5 y=0x45 w=0x02 h=0x13)
      Variation 3: [0xa080bb] 45 0f 0e 10 10 12 48 0f (UNTRACED INSTR, Open messagebox? slot=0x0f x=0x0e y=0x10 w=0x10 h=0x12)
      Variation 4: [0x9a8031] 45 02 88 47 02 b4 1c 5f (UNTRACED INSTR, Open messagebox? slot=0x02 x=0x88 y=0x47 w=0x02 h=0xb4)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
