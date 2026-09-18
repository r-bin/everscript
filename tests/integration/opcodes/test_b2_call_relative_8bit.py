"""Opcode 0xB2: like 0xb4 but script is byte-offset?."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xB2")
def test_opcode_b2_like_0xb4_but_script_is_byte_offset_vanilla():
    """Opcode 0xB2: like 0xb4 but script is byte-offset?.

    Vanilla ROM examples from script_all:
      - [0x97c948] b2 02 88 45 02 88 47 02 : CALL Relative (8bit) script 0x97c8e5 ("Unnamed ABS script 0x97c8e5")
      - [0x9a9d34] b2 03 b3 b5 b4 41 1a 01 : CALL Relative (8bit) script 0x9a9c75 ("Unnamed ABS script 0x9a9c75")
      - [0x9aaa73] b2 03 92 00 92 02 b1 02 : CALL Relative (8bit) script 0x9aa975 ("Unnamed ABS script 0x9aa975")
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xB2 (CALL Relative (8bit) script 0x97c8e5 ("Unnamed ABS script 0x97c8e5"))
        eval("B2 02 88 45 02 88 47 02");
    """

    expected = """
        B2 02 88 45 02 88 47 02    // (0xB2) CALL Relative (8bit) script 0x97c8e5 ("Unnamed ABS script 0x97c8e5")
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xB2")
def test_opcode_b2_like_0xb4_but_script_is_byte_offset_variations():
    """Variations for Opcode 0xB2:
      Variation 1: [0x97c948] b2 02 88 45 02 88 47 02 (CALL Relative (8bit) script 0x97c8e5 ("Unnamed ABS script 0x97c8e5"))
      Variation 2: [0x9a9d34] b2 03 b3 b5 b4 41 1a 01 (CALL Relative (8bit) script 0x9a9c75 ("Unnamed ABS script 0x9a9c75"))
      Variation 3: [0x9aaa73] b2 03 92 00 92 02 b1 02 (CALL Relative (8bit) script 0x9aa975 ("Unnamed ABS script 0x9aa975"))
      Variation 4: [0x98a912] b2 04 92 00 92 02 92 04 (CALL Relative (8bit) script 0x98a8b0 ("Unnamed ABS script 0x98a8b0"))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
