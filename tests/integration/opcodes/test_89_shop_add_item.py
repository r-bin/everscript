"""Opcode 0x89: add item to shop ring menu according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x89")
def test_opcode_89_add_item_to_shop_ring_menu_according_to_darkmoon_vanilla():
    """Opcode 0x89: add item to shop ring menu according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x92c4c1] 89 82 31 ee 89 82 30 82 : Add item 0x31 priced 30 to shop menu
      - [0x92c4c5] 89 82 30 82 50 89 82 34 : Add item 0x30 priced 0x50 to shop menu
      - [0x92c4ca] 89 82 34 82 3c 89 82 33 : Add item 0x34 priced 0x3c to shop menu
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x89 (Add item 0x31 priced 30 to shop menu)
        eval("89 82 31 EE 89 82 30 82");
    """

    expected = """
        89 82 31 EE 89 82 30 82    // (0x89) Add item 0x31 priced 30 to shop menu
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x89")
def test_opcode_89_add_item_to_shop_ring_menu_according_to_darkmoon_variations():
    """Variations for Opcode 0x89:
      Variation 1: [0x92c4c1] 89 82 31 ee 89 82 30 82 (Add item 0x31 priced 30 to shop menu)
      Variation 2: [0x92c4c5] 89 82 30 82 50 89 82 34 (Add item 0x30 priced 0x50 to shop menu)
      Variation 3: [0x92c4ca] 89 82 34 82 3c 89 82 33 (Add item 0x34 priced 0x3c to shop menu)
      Variation 4: [0x92c4cf] 89 82 33 82 3c 00 09 08 (Add item 0x33 priced 0x3c to shop menu)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
