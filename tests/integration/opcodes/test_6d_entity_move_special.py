"""Opcode 0x6D: identical code path to 6f but stz $12 instead of #$1->$12. No clue where this is used."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x6D")
def test_opcode_6d_identical_code_path_to_6f_but_stz_12_instead_of_1_12_no_clue_where_this_is_used_vanilla():
    """Opcode 0x6D: identical code path to 6f but stz $12 instead of #$1->$12. No clue where this is used.

    Vanilla ROM examples from script_all:
      - [0x94c8ae] 6d d0 b0 b5 6d d1 b2 b5 : Make boy walk by 0,5
      - [0x94c8b2] 6d d1 b2 b5 2e 8d 01 00 : Make dog walk by 2,5
      - [0x94c3a3] 6d ae cd b0 2e ae 75 8d : Make entity attached to script? walk by -3,0
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x6D (Make boy walk by 0,5)
        eval("6D D0 B0 B5 6D D1 B2 B5");
    """

    expected = """
        6D D0 B0 B5 6D D1 B2 B5    // (0x6D) Make boy walk by 0,5
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x6D")
def test_opcode_6d_identical_code_path_to_6f_but_stz_12_instead_of_1_12_no_clue_where_this_is_used_variations():
    """Variations for Opcode 0x6D:
      Variation 1: [0x94c8ae] 6d d0 b0 b5 6d d1 b2 b5 (Make boy walk by 0,5)
      Variation 2: [0x94c8b2] 6d d1 b2 b5 2e 8d 01 00 (Make dog walk by 2,5)
      Variation 3: [0x94c3a3] 6d ae cd b0 2e ae 75 8d (Make entity attached to script? walk by -3,0)
      Variation 4: [0x94da90] 6d d0 cf b0 2e d0 74 d0 (Make boy walk by -1,0)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
