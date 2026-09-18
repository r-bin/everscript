"""Opcode 0x77: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_77_opcode_77():
    """Opcode 0x77: ."""
    script = """
        face(BOY, EAST);
    """

    expected = """
        77 D0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x77")
def test_opcode_77_opcode_77_variations():
    """Variations for Opcode 0x77:
      Variation 1: [0x9384b2] 77 d0 a7 1e 76 d0 a7 1e (MAKE boy FACE EAST)
      Variation 2: [0x93841f] 77 d1 a7 20 78 d1 3e 00 (MAKE dog FACE EAST)
      Variation 3: [0x94cae8] 77 8d 29 00 a3 13 51 d4 (MAKE $285d FACE EAST)
      Variation 4: [0x94cd50] 77 8d 07 00 3a 3c 10 00 (MAKE $283b FACE EAST)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
