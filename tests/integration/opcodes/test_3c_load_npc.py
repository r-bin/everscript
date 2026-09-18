"""Opcode 0x3C: the >>1 below according to darkmoon (npc addr -> npc index)."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x3C")
def test_opcode_3c_the_1_below_according_to_darkmoon_npc_addr_npc_index_vanilla():
    """Opcode 0x3C: the >>1 below according to darkmoon (npc addr -> npc index).

    Vanilla ROM examples from script_all:
      - [0x93852e] 3c 1e 00 00 04 11 1f 18 : Load NPC 001e>>1 flags/state 0400 at pos 11 1f
      - [0x938539] 3c 1e 00 00 04 11 39 18 : Load NPC 001e>>1 flags/state 0400 at pos 11 39
      - [0x938544] 3c 1e 00 00 04 2d 7d 18 : Load NPC 001e>>1 flags/state 0400 at pos 2d 7d
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x3C (Load NPC 001e>>1 flags/state 0400 at pos 11 1f)
        eval("3C 1E 00 00 04 11 1F 18");
    """

    expected = """
        3C 1E 00 00 04 11 1F 18    // (0x3C) Load NPC 001e>>1 flags/state 0400 at pos 11 1f
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x3C")
def test_opcode_3c_the_1_below_according_to_darkmoon_npc_addr_npc_index_variations():
    """Variations for Opcode 0x3C:
      Variation 1: [0x93852e] 3c 1e 00 00 04 11 1f 18 (Load NPC 001e>>1 flags/state 0400 at pos 11 1f)
      Variation 2: [0x938539] 3c 1e 00 00 04 11 39 18 (Load NPC 001e>>1 flags/state 0400 at pos 11 39)
      Variation 3: [0x938544] 3c 1e 00 00 04 2d 7d 18 (Load NPC 001e>>1 flags/state 0400 at pos 2d 7d)
      Variation 4: [0x93854f] 3c 1e 00 00 04 73 73 18 (Load NPC 001e>>1 flags/state 0400 at pos 73 73)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
