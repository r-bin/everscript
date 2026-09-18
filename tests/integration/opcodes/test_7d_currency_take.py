"""Opcode 0x7D: take moniez."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_7d_take_moniez():
    """Opcode 0x7D: take moniez."""
    script = """
        currency_take(CURRENCY.TALONS, 0x05);
    """

    expected = """
        7D B0 05 00 00
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x7D")
def test_opcode_7d_take_moniez_variations():
    """Variations for Opcode 0x7D:
      Variation 1: [0x969ace] 7d 87 f0 00 05 00 00 a0 (Take 5 Currency ($2348)&0xff (moniez))
      Variation 2: [0x968c32] 7d 87 f0 00 4b 00 00 18 (Take 75 Currency ($2348)&0xff (moniez))
      Variation 3: [0x9683e4] 7d 87 f0 00 1e 00 00 a0 (Take 30 Currency ($2348)&0xff (moniez))
      Variation 4: [0x95e64d] 7d b3 1e 00 00 55 30 40 (Take 30 Jewels (moniez))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
