"""Opcode 0x2A: disable/freeze character from sub-instr."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_2a_disable_freeze_character_from_sub_instr():
    """Opcode 0x2A: disable/freeze character from sub-instr."""
    script = """
        control(BOY, True);
    """

    expected = """
        BC
    """

    assert_evs_bytes(script, expected)

# todo: does not test opcode 2a, remove it


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x2A")
def test_opcode_2a_disable_freeze_character_from_sub_instr_variations():
    """Variations for Opcode 0x2A:
      Variation 1: [0x94cc78] 2a 8d 2b 00 70 8d 2b 00 (Make $285f script controlled)
      Variation 2: [0x94cc82] 2a 8d 2d 00 70 8d 2d 00 (Make $2861 script controlled)
      Variation 3: [0x94cc8c] 2a 8d 2f 00 70 8d 2f 00 (Make $2863 script controlled)
      Variation 4: [0x94cc96] 2a 8d 31 00 70 8d 31 00 (Make $2865 script controlled)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
