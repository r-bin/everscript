"""Opcode 0x0B: if moniez<amount."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x0B")
def test_opcode_0b_if_moniez_amount_vanilla():
    """Opcode 0x0B: if moniez<amount.

    Vanilla ROM examples from script_all:
      - [0x969ac5] 0b 87 f0 00 05 00 00 25 : IF Currency ($2348)&0xff (moniez) < 5 THEN SKIP 37 (to 0x969af3)
      - [0x95e646] 0b b3 1e 00 00 ac 00 7d : IF Jewels (moniez) < 30 THEN SKIP 172 (to 0x95e6f9)
      - [0x98d832] 0b b6 28 00 00 b2 00 7d : IF Gold Coins (moniez) < 40 THEN SKIP 178 (to 0x98d8eb)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x0B (IF Currency ($2348)&0xff (moniez) < 5 THEN SKIP 37 (to 0x969af3))
        eval("0B 87 F0 00 05 00 00 25");
    """

    expected = """
        0B 87 F0 00 05 00 00 25    // (0x0B) IF Currency ($2348)&0xff (moniez) < 5 THEN SKIP 37 (to 0x969af3)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x0B")
def test_opcode_0b_if_moniez_amount_variations():
    """Variations for Opcode 0x0B:
      Variation 1: [0x969ac5] 0b 87 f0 00 05 00 00 25 (IF Currency ($2348)&0xff (moniez) < 5 THEN SKIP 37 (to 0x969af3))
      Variation 2: [0x95e646] 0b b3 1e 00 00 ac 00 7d (IF Jewels (moniez) < 30 THEN SKIP 172 (to 0x95e6f9))
      Variation 3: [0x98d832] 0b b6 28 00 00 b2 00 7d (IF Gold Coins (moniez) < 40 THEN SKIP 178 (to 0x98d8eb))
      Variation 4: [0x98d989] 0b b6 32 00 00 b0 00 7d (IF Gold Coins (moniez) < 50 THEN SKIP 176 (to 0x98da40))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
