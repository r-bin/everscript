"""Opcode 0xAD: store two bytes << 3 to two adresses offsets to $2834."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xAD")
def test_opcode_ad_store_two_bytes_3_to_two_adresses_offsets_to_2834_vanilla():
    """Opcode 0xAD: store two bytes << 3 to two adresses offsets to $2834.

    Vanilla ROM examples from script_all:
      - [0x94ca4e] ad 33 00 35 00 59 55 a5 : WRITE $2867 = 0x1640
      - [0x94ca4e] ad 33 00 35 00 59 55 a5 : WRITE $2869 = 0x0055
      - [0x94ca62] ad 33 00 35 00 55 55 a5 : WRITE $2867 = 0x1540
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xAD (WRITE $2867 = 0x1640)
        eval("AD 33 00 35 00 59 55 A5");
    """

    expected = """
        AD 33 00 35 00 59 55 A5    // (0xAD) WRITE $2867 = 0x1640
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xAD")
def test_opcode_ad_store_two_bytes_3_to_two_adresses_offsets_to_2834_variations():
    """Variations for Opcode 0xAD:
      Variation 1: [0x94ca4e] ad 33 00 35 00 59 55 a5 (WRITE $2867 = 0x1640)
      Variation 2: [0x94ca4e] ad 33 00 35 00 59 55 a5 (WRITE $2869 = 0x0055)
      Variation 3: [0x94ca62] ad 33 00 35 00 55 55 a5 (WRITE $2867 = 0x1540)
      Variation 4: [0x94ca76] ad 33 00 35 00 4f 64 a5 (WRITE $2867 = 0x13c0)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
