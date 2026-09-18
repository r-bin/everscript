"""Opcode 0x20: Teleport both characters (Unknown, writes to boy data and does more stuff)."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_20_teleport_both_characters_unknown_writes_to_boy_data_and_does_more_stuff():
    """Opcode 0x20: Teleport both characters (Unknown, writes to boy data and does more stuff)."""
    script = """
        teleport(CHARACTER.BOTH, 0x46, 0x89);
    """

    expected = """
        20 46 89
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x20")
def test_opcode_20_teleport_both_characters_unknown_writes_to_boy_data_and_does_more_stuff_variations():
    """Variations for Opcode 0x20:
      Variation 1: [0x9384f3] 20 46 89 29 75 5e 00 a5 (Teleport both to 46 89)
      Variation 2: [0x9385bb] 20 43 93 0c 9d 04 b1 08 (Teleport both to 43 93)
      Variation 3: [0x94e605] 20 1d 15 a3 00 04 04 00 (Teleport both to 1d 15)
      Variation 4: [0x94e79f] 20 13 1d a3 00 04 04 00 (Teleport both to 13 1d)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
