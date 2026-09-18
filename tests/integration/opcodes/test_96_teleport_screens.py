"""Opcode 0x96: relative teleport player screens and scroll according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_96_relative_teleport_player_screens_and_scroll_according_to_darkmoon():
    """Opcode 0x96: relative teleport player screens and scroll according to darkmoon."""
    script = """
        teleport_screen(0x00, 0x02);
    """

    expected = """
        96 B0 B2
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x96")
def test_opcode_96_relative_teleport_player_screens_and_scroll_according_to_darkmoon_variations():
    """Variations for Opcode 0x96:
      Variation 1: [0x96e378] 96 b0 b2 04 1c 00 09 06 (Teleport player by 0, 2 screens)
      Variation 2: [0x96e342] 96 b2 b0 10 a5 00 06 a5 (Teleport player by 2, 0 screens)
      Variation 3: [0x96e31e] 96 ce b0 10 a5 00 06 a5 (Teleport player by -2, 0 screens)
      Variation 4: [0x96e3e1] 96 b0 ce 09 85 9b 04 0f (Teleport player by 0, -2 screens)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
