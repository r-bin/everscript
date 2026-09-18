"""Opcode 0x42: Teleport entity from sub-instr to byte,byte."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_42_teleport_entity_from_sub_instr_to_byte_byte():
    """Opcode 0x42: Teleport entity from sub-instr to byte,byte."""
    script = """
        teleport(BOY, 0x17, 0x1f);
    """

    expected = """
        42 D0 17 1F
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x42")
def test_opcode_42_teleport_entity_from_sub_instr_to_byte_byte_variations():
    """Variations for Opcode 0x42:
      Variation 1: [0x94cd31] 42 d0 17 1f 42 d1 17 1f (Teleport boy to 1f, 17)
      Variation 2: [0x94cd35] 42 d1 17 1f c0 1b d3 01 (Teleport dog to 1f, 17)
      Variation 3: [0x94e29f] 42 d0 5a 14 42 d1 5a 1a (Teleport boy to 14, 5a)
      Variation 4: [0x94e2a3] 42 d1 5a 1a 76 d0 76 d1 (Teleport dog to 1a, 5a)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
