"""Opcode 0x92: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_92_opcode_92():
    """Opcode 0x92: ."""
    script = """
        damage(BOY, 0x05, True);
    """

    expected = """
        92 D0 B5
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x92")
def test_opcode_92_opcode_92_variations():
    """Variations for Opcode 0x92:
      Variation 1: [0x93cb39] 92 d0 b5 92 d1 b5 a7 3c (DAMAGE boy FOR 5 WITH ANIMATION)
      Variation 2: [0x93cb3c] 92 d1 b5 a7 3c 8d 00 a7 (DAMAGE dog FOR 5 WITH ANIMATION)
      Variation 3: [0x93cc2a] 92 d0 82 46 78 d0 00 80 (DAMAGE boy FOR 0x46 WITH ANIMATION)
      Variation 4: [0x93cc7f] 92 d1 82 46 78 d1 00 80 (DAMAGE dog FOR 0x46 WITH ANIMATION)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
