"""Opcode 0xA6: 0xa6, looks like a call with a relative 16bit offset."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xA6")
def test_opcode_a6_0xa6_looks_like_a_call_with_a_relative_16bit_offset_vanilla():
    """Opcode 0xA6: 0xa6, looks like a call with a relative 16bit offset.

    Vanilla ROM examples from script_all:
      - [0x9386bf] a6 9c fc 00 a6 a6 fc 00 : RCALL -868 (to 0x93835b): Unknown
      - [0x9386c3] a6 a6 fc 00 08 85 e1 02 : RCALL -858 (to 0x938369): Prehistoria - planetfall
      - [0x939220] a6 7d fe 00 a3 00 a3 21 : RCALL -387 (to 0x93909d): Unknown
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xA6 (RCALL -868 (to 0x93835b): Unknown)
        eval("A6 9C FC 00 A6 A6 FC 00");
    """

    expected = """
        A6 9C FC 00 A6 A6 FC 00    // (0xA6) RCALL -868 (to 0x93835b): Unknown
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xA6")
def test_opcode_a6_0xa6_looks_like_a_call_with_a_relative_16bit_offset_variations():
    """Variations for Opcode 0xA6:
      Variation 1: [0x9386bf] a6 9c fc 00 a6 a6 fc 00 (RCALL -868 (to 0x93835b): Unknown)
      Variation 2: [0x9386c3] a6 a6 fc 00 08 85 e1 02 (RCALL -858 (to 0x938369): Prehistoria - planetfall)
      Variation 3: [0x939220] a6 7d fe 00 a3 00 a3 21 (RCALL -387 (to 0x93909d): Unknown)
      Variation 4: [0x94ce71] a6 b0 fe a3 1f 22 1d 29 (RCALL -336 (to 0x94cd21): FE Village call outro)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
