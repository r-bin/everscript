"""Opcode 0x74: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_74_opcode_74():
    """Opcode 0x74: ."""
    script = """
        face(BOY, NORTH);
    """

    expected = """
        74 D0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x74")
def test_opcode_74_opcode_74_variations():
    """Variations for Opcode 0x74:
      Variation 1: [0x9384be] 74 d0 a7 0a 6c d0 51 65 (MAKE boy FACE NORTH)
      Variation 2: [0x94cb45] 74 d1 6f d0 b0 cf 6f d1 (MAKE dog FACE NORTH)
      Variation 3: [0x94e3a3] 74 8d 01 00 04 20 00 09 (MAKE $2835 FACE NORTH)
      Variation 4: [0x94b545] 74 8d 0e 00 a7 0c a3 06 (MAKE $2842 FACE NORTH)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
