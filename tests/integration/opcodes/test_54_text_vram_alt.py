"""Opcode 0x54: like 0x55, but 1 byte "destination in vram"."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x54")
def test_opcode_54_like_0x55_but_1_byte_destination_in_vram_vanilla():
    """Opcode 0x54: like 0x55, but 1 byte "destination in vram".

    Vanilla ROM examples from script_all:
      - [0x9bbd69] 54 01 a7 08 47 01 06 14 : CLEAR TEXT IN #1
      - [0xa080b3] 54 2c 42 0f 14 10 18 12 : CLEAR TEXT IN #44
      - [0xa3d22e] 54 81 b6 c9 45 68 70 b0 : CLEAR TEXT IN #129
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x54 (CLEAR TEXT IN #1)
        eval("54 01 A7 08 47 01 06 14");
    """

    expected = """
        54 01 A7 08 47 01 06 14    // (0x54) CLEAR TEXT IN #1
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x54")
def test_opcode_54_like_0x55_but_1_byte_destination_in_vram_variations():
    """Variations for Opcode 0x54:
      Variation 1: [0x9bbd69] 54 01 a7 08 47 01 06 14 (CLEAR TEXT IN #1)
      Variation 2: [0xa080b3] 54 2c 42 0f 14 10 18 12 (CLEAR TEXT IN #44)
      Variation 3: [0xa3d22e] 54 81 b6 c9 45 68 70 b0 (CLEAR TEXT IN #129)
      Variation 4: [0xa080ad] 54 36 3f 0f 52 27 54 2c (CLEAR TEXT IN #54)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
