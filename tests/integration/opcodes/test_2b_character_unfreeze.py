"""Opcode 0x2B: enables/unfreeze character from sub-instr."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x2B")
def test_opcode_2b_enables_unfreeze_character_from_sub_instr_vanilla():
    """Opcode 0x2B: enables/unfreeze character from sub-instr.

    Vanilla ROM examples from script_all:
      - [0x94d443] 2b 8d 03 00 80 00 a3 32 : Make $2837 player/AI controlled
      - [0x94d844] 2b 8d 01 00 00 81 6f 8d : Make $2835 player/AI controlled
      - [0x94de42] 2b 88 03 02 80 00 a3 32 : Make $245b player/AI controlled
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x2B (Make $2837 player/AI controlled)
        eval("2B 8D 03 00 80 00 A3 32");
    """

    expected = """
        2B 8D 03 00 80 00 A3 32    // (0x2B) Make $2837 player/AI controlled
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x2B")
def test_opcode_2b_enables_unfreeze_character_from_sub_instr_variations():
    """Variations for Opcode 0x2B:
      Variation 1: [0x94d443] 2b 8d 03 00 80 00 a3 32 (Make $2837 player/AI controlled)
      Variation 2: [0x94d844] 2b 8d 01 00 00 81 6f 8d (Make $2835 player/AI controlled)
      Variation 3: [0x94de42] 2b 88 03 02 80 00 a3 32 (Make $245b player/AI controlled)
      Variation 4: [0x94e5db] 2b d2 18 d3 01 cf 18 d7 (Make controlled char player/AI controlled)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
