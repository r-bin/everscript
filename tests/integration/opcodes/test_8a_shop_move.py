"""Opcode 0x8A: move shop ring to entity according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x8A")
def test_opcode_8a_move_shop_ring_to_entity_according_to_darkmoon_vanilla():
    """Opcode 0x8A: move shop ring to entity according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0xaccf07] 8a 61 62 ce 91 8c 08 8e : Move shop menu to 17 18 -2
      - [0xacac01] 8a 43 33 33 3c cc c0 99 : Move shop menu to -13 3 3 12 -4
      - [0x93d914] 8a 05 00 01 00 00 0d 05 : Move shop menu to $2839 1
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x8A (Move shop menu to 17 18 -2)
        eval("8A 61 62 CE 91 8C 08 8E");
    """

    expected = """
        8A 61 62 CE 91 8C 08 8E    // (0x8A) Move shop menu to 17 18 -2
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x8A")
def test_opcode_8a_move_shop_ring_to_entity_according_to_darkmoon_variations():
    """Variations for Opcode 0x8A:
      Variation 1: [0xaccf07] 8a 61 62 ce 91 8c 08 8e (Move shop menu to 17 18 -2)
      Variation 2: [0xacac01] 8a 43 33 33 3c cc c0 99 (Move shop menu to -13 3 3 12 -4)
      Variation 3: [0x93d914] 8a 05 00 01 00 00 0d 05 (Move shop menu to $2839 1)
      Variation 4: [0xa4821e] 8a 0a 4b 40 03 5d 9a 01 (Move shop menu to $303d&0x08 0x9a5d signed 0x40 signed 18)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
