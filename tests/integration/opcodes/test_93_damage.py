"""Opcode 0x93: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_93_opcode_93():
    """Opcode 0x93: ."""
    script = """
        damage(BOY, 0x05, False);
    """

    expected = """
        93 D0 B5
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x93")
def test_opcode_93_opcode_93_variations():
    """Variations for Opcode 0x93:
      Variation 1: [0x98a42e] 93 d2 92 00 30 66 52 9d (DAMAGE controlled char FOR signed arg0)
      Variation 2: [0x978705] 93 8d 0f 00 84 e8 03 9c (DAMAGE $2843 FOR 0x03e8)
      Variation 3: [0x97871d] 93 8d 11 00 84 e8 03 9c (DAMAGE $2845 FOR 0x03e8)
      Variation 4: [0x978735] 93 8d 13 00 84 e8 03 9c (DAMAGE $2847 FOR 0x03e8)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
