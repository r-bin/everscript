"""Opcode 0x70: make entity from sub-instr face entity from sub-instr."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_70_make_entity_from_sub_instr_face_entity_from_sub_instr():
    """Opcode 0x70: make entity from sub-instr face entity from sub-instr."""
    script = """
        face_target(BOY, DOG);
    """

    expected = """
        70 D0 D1
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x70")
def test_opcode_70_make_entity_from_sub_instr_face_entity_from_sub_instr_variations():
    """Variations for Opcode 0x70:
      Variation 1: [0x94cc7c] 70 8d 2b 00 d0 3a 2a 8d (Make $285f face boy)
      Variation 2: [0x94cc86] 70 8d 2d 00 d0 3a 2a 8d (Make $2861 face boy)
      Variation 3: [0x94cc90] 70 8d 2f 00 d0 3a 2a 8d (Make $2863 face boy)
      Variation 4: [0x94cc9a] 70 8d 31 00 d0 3a 75 8d (Make $2865 face boy)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
