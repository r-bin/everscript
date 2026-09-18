"""Opcode 0x99: Enter Mode 7 Worldmap on Windwalker according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x99")
def test_opcode_99_enter_mode_7_worldmap_on_windwalker_according_to_darkmoon_vanilla():
    """Opcode 0x99: Enter Mode 7 Worldmap on Windwalker according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x97cd54] 99 e5 b0 b0 b0 b0 b0 18 : WINDWALK args 21 0 0 0 0 0
      - [0x97c6e7] 99 e6 b0 b0 b0 b0 b0 18 : WINDWALK args 22 0 0 0 0 0
      - [0x9acdd3] 99 e7 b0 b0 b0 b0 b0 18 : WINDWALK args 23 0 0 0 0 0
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x99 (WINDWALK args 21 0 0 0 0 0)
        eval("99 E5 B0 B0 B0 B0 B0 18");
    """

    expected = """
        99 E5 B0 B0 B0 B0 B0 18    // (0x99) WINDWALK args 21 0 0 0 0 0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x99")
def test_opcode_99_enter_mode_7_worldmap_on_windwalker_according_to_darkmoon_variations():
    """Variations for Opcode 0x99:
      Variation 1: [0x97cd54] 99 e5 b0 b0 b0 b0 b0 18 (WINDWALK args 21 0 0 0 0 0)
      Variation 2: [0x97c6e7] 99 e6 b0 b0 b0 b0 b0 18 (WINDWALK args 22 0 0 0 0 0)
      Variation 3: [0x9acdd3] 99 e7 b0 b0 b0 b0 b0 18 (WINDWALK args 23 0 0 0 0 0)
      Variation 4: [0x9bb704] 99 e4 b0 b0 b0 b0 b0 18 (WINDWALK args 20 0 0 0 0 0)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
