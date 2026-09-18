"""Opcode 0xA4: 0xa4, some call instr with 16bit addr."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xA4")
def test_opcode_a4_0xa4_some_call_instr_with_16bit_addr_vanilla():
    """Opcode 0xA4: 0xa4, some call instr with 16bit addr.

    Vanilla ROM examples from script_all:
      - [0x93869f] a4 e9 07 a7 3c a3 59 08 : CALL 0x07e9 -> 0x93802b
      - [0x94dc72] a4 17 0d 00 a3 32 09 d7 : CALL 0x0d17 -> 0x94d09d
      - [0x96ab77] a4 c8 01 04 a2 01 09 08 : CALL 0x01c8 -> 0x96b0b8
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xA4 (CALL 0x07e9 -> 0x93802b)
        eval("A4 E9 07 A7 3C A3 59 08");
    """

    expected = """
        A4 E9 07 A7 3C A3 59 08    // (0xA4) CALL 0x07e9 -> 0x93802b
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xA4")
def test_opcode_a4_0xa4_some_call_instr_with_16bit_addr_variations():
    """Variations for Opcode 0xA4:
      Variation 1: [0x93869f] a4 e9 07 a7 3c a3 59 08 (CALL 0x07e9 -> 0x93802b)
      Variation 2: [0x94dc72] a4 17 0d 00 a3 32 09 d7 (CALL 0x0d17 -> 0x94d09d)
      Variation 3: [0x96ab77] a4 c8 01 04 a2 01 09 08 (CALL 0x01c8 -> 0x96b0b8)
      Variation 4: [0x96ab86] a4 68 01 04 93 01 09 08 (CALL 0x0168 -> 0x96b0e0)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
