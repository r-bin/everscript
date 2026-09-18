"""Opcode 0x9A: change font according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x9A")
def test_opcode_9a_change_font_according_to_darkmoon_vanilla():
    """Opcode 0x9A: change font according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x92d021] 9a b2 51 1a 04 9a b0 51 : CHANGE FONT TO 2
      - [0x92d026] 9a b0 51 1d 04 9a b2 51 : CHANGE FONT TO 0
      - [0xa0fd03] 9a 81 eb 01 36 80 eb 46 : CHANGE FONT TO 0xeb signed
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x9A (CHANGE FONT TO 2)
        eval("9A B2 51 1A 04 9A B0 51");
    """

    expected = """
        9A B2 51 1A 04 9A B0 51    // (0x9A) CHANGE FONT TO 2
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x9A")
def test_opcode_9a_change_font_according_to_darkmoon_variations():
    """Variations for Opcode 0x9A:
      Variation 1: [0x92d021] 9a b2 51 1a 04 9a b0 51 (CHANGE FONT TO 2)
      Variation 2: [0x92d026] 9a b0 51 1d 04 9a b2 51 (CHANGE FONT TO 0)
      Variation 3: [0xa0fd03] 9a 81 eb 01 36 80 eb 46 (CHANGE FONT TO 0xeb signed)
      Variation 4: [0xadaa03] 9a 0d ea 82 7b 20 9e e8 (CHANGE FONT TO $ab1e [unknown 0x7b])
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
