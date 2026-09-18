"""Opcode 0x6F: get entity pointer using sub-instr, run 2 sub-instrs to get X and Y. Looks imilar to 6e."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x6F")
def test_opcode_6f_get_entity_pointer_using_sub_instr_run_2_sub_instrs_to_get_x_and_y_looks_imilar_to_6e_vanilla():
    """Opcode 0x6F: get entity pointer using sub-instr, run 2 sub-instrs to get X and Y. Looks imilar to 6e.

    Vanilla ROM examples from script_all:
      - [0x93867c] 6f d0 b0 ca 6f d1 b0 cb : Make boy walk by 0,-6 directly
      - [0x938680] 6f d1 b0 cb 2e d0 2e d1 : Make dog walk by 0,-5 directly
      - [0x938695] 6f d0 b7 ce 2e d0 74 d0 : Make boy walk by 7,-2 directly
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x6F (Make boy walk by 0,-6 directly)
        eval("6F D0 B0 CA 6F D1 B0 CB");
    """

    expected = """
        6F D0 B0 CA 6F D1 B0 CB    // (0x6F) Make boy walk by 0,-6 directly
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x6F")
def test_opcode_6f_get_entity_pointer_using_sub_instr_run_2_sub_instrs_to_get_x_and_y_looks_imilar_to_6e_variations():
    """Variations for Opcode 0x6F:
      Variation 1: [0x93867c] 6f d0 b0 ca 6f d1 b0 cb (Make boy walk by 0,-6 directly)
      Variation 2: [0x938680] 6f d1 b0 cb 2e d0 2e d1 (Make dog walk by 0,-5 directly)
      Variation 3: [0x938695] 6f d0 b7 ce 2e d0 74 d0 (Make boy walk by 7,-2 directly)
      Variation 4: [0x93836f] 6f d1 ba b0 a7 2d 18 d7 (Make dog walk by 10,0 directly)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
