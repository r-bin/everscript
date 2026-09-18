"""Opcode 0x75: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_75_opcode_75():
    """Opcode 0x75: ."""
    script = """
        face(BOY, SOUTH);
    """

    expected = """
        75 D0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x75")
def test_opcode_75_opcode_75_variations():
    """Variations for Opcode 0x75:
      Variation 1: [0x9384ba] 75 d0 a7 1e 74 d0 a7 0a (MAKE boy FACE SOUTH)
      Variation 2: [0x93841b] 75 d1 a7 0c 77 d1 a7 20 (MAKE dog FACE SOUTH)
      Variation 3: [0x94cb51] 75 8d 29 00 b4 05 b0 b0 (MAKE $285d FACE SOUTH)
      Variation 4: [0x94cb64] 75 8d 27 00 a7 04 29 b9 (MAKE $285b FACE SOUTH)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
