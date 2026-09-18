"""Opcode 0x7C: give moniez."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_7c_give_moniez():
    """Opcode 0x7C: give moniez."""
    script = """
        currency_get(CURRENCY.TALONS, 0x32);
    """

    expected = """
        7C B0 32 00 00
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x7C")
def test_opcode_7c_give_moniez_variations():
    """Variations for Opcode 0x7C:
      Variation 1: [0x93884e] 7c b0 32 00 00 18 7b 01 (Give 50 Talons (moniez))
      Variation 2: [0x969b0e] 7c 87 f0 00 05 00 00 a0 (Give 5 Currency ($2348)&0xff (moniez))
      Variation 3: [0x96886d] 7c b3 0a 00 00 52 46 0e (Give 10 Jewels (moniez))
      Variation 4: [0x968878] 7c b3 32 00 00 52 49 0e (Give 50 Jewels (moniez))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
