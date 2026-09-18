"""Opcode 0x6C: use sub-instr to get some entity, read 2B unknown."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x6C")
def test_opcode_6c_use_sub_instr_to_get_some_entity_read_2b_unknown_vanilla():
    """Opcode 0x6C: use sub-instr to get some entity, read 2B unknown.

    Vanilla ROM examples from script_all:
      - [0x9384a8] 6c d0 49 79 6c d1 49 79 : UNTRACED INSTR for boy with val1=0x49,val2=0x79
      - [0x9384ac] 6c d1 49 79 2e d0 77 d0 : UNTRACED INSTR for dog with val1=0x49,val2=0x79
      - [0x9384c2] 6c d0 51 65 6c d1 51 65 : UNTRACED INSTR for boy with val1=0x51,val2=0x65
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x6C (UNTRACED INSTR for boy with val1=0x49,val2=0x79)
        eval("6C D0 49 79 6C D1 49 79");
    """

    expected = """
        6C D0 49 79 6C D1 49 79    // (0x6C) UNTRACED INSTR for boy with val1=0x49,val2=0x79
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x6C")
def test_opcode_6c_use_sub_instr_to_get_some_entity_read_2b_unknown_variations():
    """Variations for Opcode 0x6C:
      Variation 1: [0x9384a8] 6c d0 49 79 6c d1 49 79 (UNTRACED INSTR for boy with val1=0x49,val2=0x79)
      Variation 2: [0x9384ac] 6c d1 49 79 2e d0 77 d0 (UNTRACED INSTR for dog with val1=0x49,val2=0x79)
      Variation 3: [0x9384c2] 6c d0 51 65 6c d1 51 65 (UNTRACED INSTR for boy with val1=0x51,val2=0x65)
      Variation 4: [0x9384c6] 6c d1 51 65 2e d0 27 a7 (UNTRACED INSTR for dog with val1=0x51,val2=0x65)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
