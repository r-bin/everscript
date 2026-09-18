"""Opcode 0x95: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_95_opcode_95():
    """Opcode 0x95: ."""
    script = """
        heal(BOY, 0x05, False);
    """

    expected = """
        95 D0 B5
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x95")
def test_opcode_95_opcode_95_variations():
    """Variations for Opcode 0x95:
      Variation 1: [0x94d368] 95 d1 84 e7 03 0c aa 04 (HEAL dog FOR 0x03e7)
      Variation 2: [0x94d3d3] 95 d0 84 e7 03 a7 10 78 (HEAL boy FOR 0x03e7)
      Variation 3: [0x96b14e] 95 d2 84 e7 03 a5 2b 04 (HEAL controlled char FOR 0x03e7)
      Variation 4: [0x95ad2e] 95 8d 09 00 84 e7 03 0d (HEAL $283d FOR 0x03e7)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
