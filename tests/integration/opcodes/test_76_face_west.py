"""Opcode 0x76: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_76_opcode_76():
    """Opcode 0x76: ."""
    script = """
        face(BOY, WEST);
    """

    expected = """
        76 D0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x76")
def test_opcode_76_opcode_76_variations():
    """Variations for Opcode 0x76:
      Variation 1: [0x9384b6] 76 d0 a7 1e 75 d0 a7 1e (MAKE boy FACE WEST)
      Variation 2: [0x9383b6] 76 d1 3a 6f d1 cc b0 a9 (MAKE dog FACE WEST)
      Variation 3: [0x94cb03] 76 8d 27 00 3a a3 0e 51 (MAKE $285b FACE WEST)
      Variation 4: [0x94cde6] 76 8d 01 00 a7 20 75 8d (MAKE $2835 FACE WEST)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
