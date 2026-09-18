"""Opcode 0xB7: "stop tile flashing", 1 sub-instr, according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xB7")
def test_opcode_b7_stop_tile_flashing_1_sub_instr_according_to_darkmoon_vanilla():
    """Opcode 0xB7: "stop tile flashing", 1 sub-instr, according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0xade903] b7 03 f8 02 d9 02 41 06 : STOP TILE FLASHING 0x02f8 signed GameTimer>>16
      - [0x93f8b4] b7 6d ef df ed db cf df : STOP TILE FLASHING 29 31
      - [0x929498] b7 00 40 6c 01 db 6c 01 : STOP TILE FLASHING -16 28 0xdb signed 28 0x77 signed 29 0x31 signed 30 0xe8 signed 31 0x05 signed 28 0xa6 signed 27 0xb4 signed 27 0xc2 signed 27 0xd0 signed 27 0xdf signed 27 0xed signed 27 0x46 signed 31 0xe8 signed 27
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xB7 (STOP TILE FLASHING 0x02f8 signed GameTimer>>16)
        eval("B7 03 F8 02 D9 02 41 06");
    """

    expected = """
        B7 03 F8 02 D9 02 41 06    // (0xB7) STOP TILE FLASHING 0x02f8 signed GameTimer>>16
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xB7")
def test_opcode_b7_stop_tile_flashing_1_sub_instr_according_to_darkmoon_variations():
    """Variations for Opcode 0xB7:
      Variation 1: [0xade903] b7 03 f8 02 d9 02 41 06 (STOP TILE FLASHING 0x02f8 signed GameTimer>>16)
      Variation 2: [0x93f8b4] b7 6d ef df ed db cf df (STOP TILE FLASHING 29 31)
      Variation 3: [0x929498] b7 00 40 6c 01 db 6c 01 (STOP TILE FLASHING -16 28 0xdb signed 28 0x77 signed 29 0x31 signed 30 0xe8 signed 31 0x05 signed 28 0xa6 signed 27 0xb4 signed 27 0xc2 signed 27 0xd0 signed 27 0xdf signed 27 0xed signed 27 0x46 signed 31 0xe8 signed 27)
      Variation 4: [0x9d9e38] b7 a3 91 02 31 86 1b 6d (STOP TILE FLASHING)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
