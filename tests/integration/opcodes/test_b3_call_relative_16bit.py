"""Opcode 0xB3: like 0xb4 but script is relative 16bit?."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xB3")
def test_opcode_b3_like_0xb4_but_script_is_relative_16bit_vanilla():
    """Opcode 0xB3: like 0xb4 but script is relative 16bit?.

    Vanilla ROM examples from script_all:
      - [0x97cd3d] b3 05 8d 00 00 92 00 92 : CALL Relative (16bit) script 0x97c9a9 ("Unnamed ABS script 0x97c9a9")
      - [0x97cd9b] b3 02 92 04 92 06 4a fb : CALL Relative (16bit) script 0x97c8e5 ("Unnamed ABS script 0x97c8e5")
      - [0x96d2f5] b3 02 b1 b0 a8 fe 00 19 : CALL Relative (16bit) script 0x96d19d ("Unnamed ABS script 0x96d19d")
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xB3 (CALL Relative (16bit) script 0x97c9a9 ("Unnamed ABS script 0x97c9a9"))
        eval("B3 05 8D 00 00 92 00 92");
    """

    expected = """
        B3 05 8D 00 00 92 00 92    // (0xB3) CALL Relative (16bit) script 0x97c9a9 ("Unnamed ABS script 0x97c9a9")
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xB3")
def test_opcode_b3_like_0xb4_but_script_is_relative_16bit_variations():
    """Variations for Opcode 0xB3:
      Variation 1: [0x97cd3d] b3 05 8d 00 00 92 00 92 (CALL Relative (16bit) script 0x97c9a9 ("Unnamed ABS script 0x97c9a9"))
      Variation 2: [0x97cd9b] b3 02 92 04 92 06 4a fb (CALL Relative (16bit) script 0x97c8e5 ("Unnamed ABS script 0x97c8e5"))
      Variation 3: [0x96d2f5] b3 02 b1 b0 a8 fe 00 19 (CALL Relative (16bit) script 0x96d19d ("Unnamed ABS script 0x96d19d"))
      Variation 4: [0x97c6ce] b3 05 8d 00 00 88 61 01 (CALL Relative (16bit) script 0x97c3d9 ("Unnamed ABS script 0x97c3d9"))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
