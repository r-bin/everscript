"""Opcode 0x87: speed according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x87")
def test_opcode_87_speed_according_to_darkmoon_vanilla():
    """Opcode 0x87: speed according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x939204] 87 82 c8 1a 00 b0 09 12 : SET AUDIO speed to 0xc8
      - [0x9387cf] 87 82 96 09 0d 01 00 dc : SET AUDIO speed to 0x96
      - [0xaa8123] 87 de 7b 0a 03 48 74 a1 : SET AUDIO speed to [invalid 0x5e]
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x87 (SET AUDIO speed to 0xc8)
        eval("87 82 C8 1A 00 B0 09 12");
    """

    expected = """
        87 82 C8 1A 00 B0 09 12    // (0x87) SET AUDIO speed to 0xc8
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x87")
def test_opcode_87_speed_according_to_darkmoon_variations():
    """Variations for Opcode 0x87:
      Variation 1: [0x939204] 87 82 c8 1a 00 b0 09 12 (SET AUDIO speed to 0xc8)
      Variation 2: [0x9387cf] 87 82 96 09 0d 01 00 dc (SET AUDIO speed to 0x96)
      Variation 3: [0xaa8123] 87 de 7b 0a 03 48 74 a1 (SET AUDIO speed to [invalid 0x5e])
      Variation 4: [0xaddc02] 87 80 c8 fb d2 20 c1 32 (SET AUDIO speed to)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
