"""Opcode 0xB5: "Draw Lightning/Reveal Hidden NPC????" according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xB5")
def test_opcode_b5_draw_lightning_reveal_hidden_npc_according_to_darkmoon_vanilla():
    """Opcode 0xB5: "Draw Lightning/Reveal Hidden NPC????" according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x93cbf8] b5 ea 8d 35 00 08 53 02 : REVEAL ENTITY?? args 26 $2869 $24ab + 20 $24af - 0x30 0 signed arg0 signed arg2 0x3c
      - [0x93cc11] b5 ea 8d 35 00 08 53 02 : REVEAL ENTITY?? args 26 $2869 $24ab - 20 $24af - 0x30 0 signed arg0 signed arg2 0x3c
      - [0x93cc4d] b5 ea 8d 35 00 08 53 02 : REVEAL ENTITY?? args 26 $2869 $24ab + 20 $24af - 0x30 0 signed arg4 signed arg6 0x3c
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xB5 (REVEAL ENTITY?? args 26 $2869 $24ab + 20 $24af - 0x30 0 signed arg0 signed arg2 0x3c)
        eval("B5 EA 8D 35 00 08 53 02");
    """

    expected = """
        B5 EA 8D 35 00 08 53 02    // (0xB5) REVEAL ENTITY?? args 26 $2869 $24ab + 20 $24af - 0x30 0 signed arg0 signed arg2 0x3c
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xB5")
def test_opcode_b5_draw_lightning_reveal_hidden_npc_according_to_darkmoon_variations():
    """Variations for Opcode 0xB5:
      Variation 1: [0x93cbf8] b5 ea 8d 35 00 08 53 02 (REVEAL ENTITY?? args 26 $2869 $24ab + 20 $24af - 0x30 0 signed arg0 signed arg2 0x3c)
      Variation 2: [0x93cc11] b5 ea 8d 35 00 08 53 02 (REVEAL ENTITY?? args 26 $2869 $24ab - 20 $24af - 0x30 0 signed arg0 signed arg2 0x3c)
      Variation 3: [0x93cc4d] b5 ea 8d 35 00 08 53 02 (REVEAL ENTITY?? args 26 $2869 $24ab + 20 $24af - 0x30 0 signed arg4 signed arg6 0x3c)
      Variation 4: [0x93cc66] b5 ea 8d 35 00 08 53 02 (REVEAL ENTITY?? args 26 $2869 $24ab - 20 $24af - 0x30 0 signed arg4 signed arg6 0x3c)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
