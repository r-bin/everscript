"""Opcode 0x98: switch character."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_98_switch_character():
    """Opcode 0x98: switch character."""
    script = """
        player_control(BOY);
    """

    expected = """
        98 D0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x98")
def test_opcode_98_switch_character_variations():
    """Variations for Opcode 0x98:
      Variation 1: [0x95cbb8] 98 d0 6c d0 14 0b 2e d1 (SWITCH CHAR TO boy)
      Variation 2: [0x96d684] 98 d1 1b d3 01 d5 01 06 (SWITCH CHAR TO dog)
      Variation 3: [0x96cd66] 98 d3 00 3f b1 40 00 2b (SWITCH CHAR TO non-controlled char)
      Variation 4: [0xa39102] 98 00 a1 04 97 dc 42 80 (SWITCH CHAR TO)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
