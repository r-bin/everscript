"""Opcode 0x84: give moniez, like 7c but amount is sub-instr."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x84")
def test_opcode_84_give_moniez_like_7c_but_amount_is_sub_instr_vanilla():
    """Opcode 0x84: give moniez, like 7c but amount is sub-instr.

    Vanilla ROM examples from script_all:
      - [0x92bec6] 84 b9 88 3b 01 00 09 07 : Give $2393 Credits (moniez)
      - [0x92bed5] 84 b0 88 3b 01 00 09 07 : Give $2393 Talons (moniez)
      - [0x92bee4] 84 b3 88 3b 01 00 09 07 : Give $2393 Jewels (moniez)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x84 (Give $2393 Credits (moniez))
        eval("84 B9 88 3B 01 00 09 07");
    """

    expected = """
        84 B9 88 3B 01 00 09 07    // (0x84) Give $2393 Credits (moniez)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x84")
def test_opcode_84_give_moniez_like_7c_but_amount_is_sub_instr_variations():
    """Variations for Opcode 0x84:
      Variation 1: [0x92bec6] 84 b9 88 3b 01 00 09 07 (Give $2393 Credits (moniez))
      Variation 2: [0x92bed5] 84 b0 88 3b 01 00 09 07 (Give $2393 Talons (moniez))
      Variation 3: [0x92bee4] 84 b3 88 3b 01 00 09 07 (Give $2393 Jewels (moniez))
      Variation 4: [0x92bef3] 84 b6 88 3b 01 00 1c df (Give $2393 Gold Coins (moniez))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
