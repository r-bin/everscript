"""Opcode 0xB6: "tile flashing", 4 sub-instr,s according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xB6")
def test_opcode_b6_tile_flashing_4_sub_instr_s_according_to_darkmoon_vanilla():
    """Opcode 0xB6: "tile flashing", 4 sub-instr,s according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x92d933] b6 ba b1 bf b0 00 18 71 : START TILE FLASHING 10 1 15 0
      - [0x92d91f] b6 bf b1 be b5 b6 be b1 : START TILE FLASHING 15 1 14 5
      - [0x92d924] b6 be b1 be b5 00 18 71 : START TILE FLASHING 14 1 14 5
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xB6 (START TILE FLASHING 10 1 15 0)
        eval("B6 BA B1 BF B0 00 18 71");
    """

    expected = """
        B6 BA B1 BF B0 00 18 71    // (0xB6) START TILE FLASHING 10 1 15 0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xB6")
def test_opcode_b6_tile_flashing_4_sub_instr_s_according_to_darkmoon_variations():
    """Variations for Opcode 0xB6:
      Variation 1: [0x92d933] b6 ba b1 bf b0 00 18 71 (START TILE FLASHING 10 1 15 0)
      Variation 2: [0x92d91f] b6 bf b1 be b5 b6 be b1 (START TILE FLASHING 15 1 14 5)
      Variation 3: [0x92d924] b6 be b1 be b5 00 18 71 (START TILE FLASHING 14 1 14 5)
      Variation 4: [0xa3d230] b6 c9 45 68 70 b0 43 68 (START TILE FLASHING -7 -11 24 [unknown 0x70] ? ?)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
