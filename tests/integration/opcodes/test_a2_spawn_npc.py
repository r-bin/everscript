"""Opcode 0xA2: spawn npc (according to darkmoon x/y are 2 sub-instrs)."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xA2")
def test_opcode_a2_spawn_npc_according_to_darkmoon_x_y_are_2_sub_instrs_vanilla():
    """Opcode 0xA2: spawn npc (according to darkmoon x/y are 2 sub-instrs).

    Vanilla ROM examples from script_all:
      - [0x93b139] a2 0e 00 00 00 12 06 29 : SPAWN NPC 0x000e>>1, flags 0x00, x:signed arg6 + 0x20, y:signed arg8 + 16
      - [0x93b153] a2 0a 00 20 00 12 06 29 : SPAWN NPC 0x000a>>1, flags 0x20, x:signed arg6 + 16, y:signed arg8
      - [0x93c88b] a2 1c 00 00 00 92 00 92 : SPAWN NPC 0x001c>>1, flags 0x00, x:signed arg0, y:signed arg2
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xA2 (SPAWN NPC 0x000e>>1, flags 0x00, x:signed arg6 + 0x20, y:signed arg8 + 16)
        eval("A2 0E 00 00 00 12 06 29");
    """

    expected = """
        A2 0E 00 00 00 12 06 29    // (0xA2) SPAWN NPC 0x000e>>1, flags 0x00, x:signed arg6 + 0x20, y:signed arg8 + 16
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xA2")
def test_opcode_a2_spawn_npc_according_to_darkmoon_x_y_are_2_sub_instrs_variations():
    """Variations for Opcode 0xA2:
      Variation 1: [0x93b139] a2 0e 00 00 00 12 06 29 (SPAWN NPC 0x000e>>1, flags 0x00, x:signed arg6 + 0x20, y:signed arg8 + 16)
      Variation 2: [0x93b153] a2 0a 00 20 00 12 06 29 (SPAWN NPC 0x000a>>1, flags 0x20, x:signed arg6 + 16, y:signed arg8)
      Variation 3: [0x93c88b] a2 1c 00 00 00 92 00 92 (SPAWN NPC 0x001c>>1, flags 0x00, x:signed arg0, y:signed arg2)
      Variation 4: [0x96b091] a2 40 00 00 00 52 29 6a (SPAWN NPC 0x0040>>1, flags 0x00, x:*(controlled char + 26), y:*(controlled char + 28) - 8)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
