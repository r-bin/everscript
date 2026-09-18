"""Opcode 0x8C: open save menu according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_8c_open_save_menu_according_to_darkmoon():
    """Opcode 0x8C: open save menu according to darkmoon."""
    script = """
        save(0x0867);
    """

    expected = """
        8C 67 08
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x8C")
def test_opcode_8c_open_save_menu_according_to_darkmoon_variations():
    """Variations for Opcode 0x8C:
      Variation 1: [0x94d42c] 8c 67 08 a7 1e a3 02 04 (Show save menu 0x0867)
      Variation 2: [0x92c7d9] 8c f4 02 00 09 08 f1 01 (Show save menu 0x02f4)
      Variation 3: [0x92c7e6] 8c f7 02 00 09 08 f1 01 (Show save menu 0x02f7)
      Variation 4: [0x92c7f3] 8c fa 02 00 09 08 f1 01 (Show save menu 0x02fa)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
