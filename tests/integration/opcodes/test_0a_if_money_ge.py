"""Opcode 0x0A: RJMP if moniez>=amount according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x0A")
def test_opcode_0a_rjmp_if_moniez_amount_according_to_darkmoon_vanilla():
    """Opcode 0x0A: RJMP if moniez>=amount according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x969ab5] 0a 87 f0 00 05 00 00 07 : IF Currency ($2348)&0xff (moniez) >= 5 THEN SKIP 7 (to 0x969ac5)
      - [0x968c1b] 0a 87 f0 00 4b 00 00 0c : IF Currency ($2348)&0xff (moniez) >= 75 THEN SKIP 12 (to 0x968c30)
      - [0x968c73] 0a 87 f0 00 4b 00 00 0c : IF Currency ($2348)&0xff (moniez) >= 75 THEN SKIP 12 (to 0x968c88)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x0A (IF Currency ($2348)&0xff (moniez) >= 5 THEN SKIP 7 (to 0x969ac5))
        // eval("0A 87 F0 00 05 00 00 07");

        if_currency(MEMORY.CURRENCY_CURRENT >= 0d5) {
            nop();
        }
    """

    expected = """
        0A 87 F0 00 05 00 00 07    // (0x0A) IF Currency ($2348)&0xff (moniez) >= 5 THEN SKIP 7 (to 0x969ac5)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x0A")
def test_opcode_0a_rjmp_if_moniez_amount_according_to_darkmoon_variations():
    """Variations for Opcode 0x0A:
      Variation 1: [0x969ab5] 0a 87 f0 00 05 00 00 07 (IF Currency ($2348)&0xff (moniez) >= 5 THEN SKIP 7 (to 0x969ac5))
      Variation 2: [0x968c1b] 0a 87 f0 00 4b 00 00 0c (IF Currency ($2348)&0xff (moniez) >= 75 THEN SKIP 12 (to 0x968c30))
      Variation 3: [0x968c73] 0a 87 f0 00 4b 00 00 0c (IF Currency ($2348)&0xff (moniez) >= 75 THEN SKIP 12 (to 0x968c88))
      Variation 4: [0x9683c8] 0a 87 f0 00 1e 00 00 0d (IF Currency ($2348)&0xff (moniez) >= 30 THEN SKIP 13 (to 0x9683de))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")

# todo: remove test_opcode_0a_rjmp_if_moniez_amount_according_to_darkmoon_variations. variations with arithmatic would be more interesting: "if_currency(MEMORY.CURRENCY_CURRENT >= <0x2834>) {}"