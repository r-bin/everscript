"""Opcode 0x7E: exchange moniez."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x7E")
def test_opcode_7e_exchange_moniez_vanilla():
    """Opcode 0x7E: exchange moniez.

    Vanilla ROM examples from script_all:
      - [0x92bfc1] 7e b2 b9 b1 b0 a0 a5 cb : Exchange 2 Credits to 1 Talons (moniez)
      - [0x92bff6] 7e b4 b9 b1 b3 a0 a5 96 : Exchange 4 Credits to 1 Jewels (moniez)
      - [0x92c027] 7e b8 b9 b1 b6 a0 a5 65 : Exchange 8 Credits to 1 Gold Coins (moniez)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x7E (Exchange 2 Credits to 1 Talons (moniez))
        eval("7E B2 B9 B1 B0 A0 A5 CB");
    """

    expected = """
        7E B2 B9 B1 B0 A0 A5 CB    // (0x7E) Exchange 2 Credits to 1 Talons (moniez)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x7E")
def test_opcode_7e_exchange_moniez_variations():
    """Variations for Opcode 0x7E:
      Variation 1: [0x92bfc1] 7e b2 b9 b1 b0 a0 a5 cb (Exchange 2 Credits to 1 Talons (moniez))
      Variation 2: [0x92bff6] 7e b4 b9 b1 b3 a0 a5 96 (Exchange 4 Credits to 1 Jewels (moniez))
      Variation 3: [0x92c027] 7e b8 b9 b1 b6 a0 a5 65 (Exchange 8 Credits to 1 Gold Coins (moniez))
      Variation 4: [0x92c0e4] 7e b1 b3 b4 b9 a0 a6 a8 (Exchange 1 Jewels to 4 Credits (moniez))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
