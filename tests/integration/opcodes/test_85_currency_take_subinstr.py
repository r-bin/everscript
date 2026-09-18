"""Opcode 0x85: take moniez, like 7d but amount is sub-instr."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x85")
def test_opcode_85_take_moniez_like_7d_but_amount_is_sub_instr_vanilla():
    """Opcode 0x85: take moniez, like 7d but amount is sub-instr.

    Vanilla ROM examples from script_all:
      - [0x96947e] 85 87 f0 00 08 11 01 29 : Take $2369 + 25 Currency ($2348)&0xff (moniez)
      - [0x969364] 85 87 f0 00 0d 27 00 29 : Take $285b * 3 Currency ($2348)&0xff (moniez)
      - [0x969938] 85 87 f0 00 0d 27 00 29 : Take $285b * 10 Currency ($2348)&0xff (moniez)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x85 (Take $2369 + 25 Currency ($2348)&0xff (moniez))
        eval("85 87 F0 00 08 11 01 29");
    """

    expected = """
        85 87 F0 00 08 11 01 29    // (0x85) Take $2369 + 25 Currency ($2348)&0xff (moniez)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x85")
def test_opcode_85_take_moniez_like_7d_but_amount_is_sub_instr_variations():
    """Variations for Opcode 0x85:
      Variation 1: [0x96947e] 85 87 f0 00 08 11 01 29 (Take $2369 + 25 Currency ($2348)&0xff (moniez))
      Variation 2: [0x969364] 85 87 f0 00 0d 27 00 29 (Take $285b * 3 Currency ($2348)&0xff (moniez))
      Variation 3: [0x969938] 85 87 f0 00 0d 27 00 29 (Take $285b * 10 Currency ($2348)&0xff (moniez))
      Variation 4: [0x968d87] 85 87 f0 00 0d 27 00 29 (Take $285b * 9 Currency ($2348)&0xff (moniez))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
