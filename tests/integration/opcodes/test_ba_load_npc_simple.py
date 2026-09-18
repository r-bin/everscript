"""Opcode 0xBA: code similar to 3c, but arg1 is only 1B and arg2 is 0."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xBA")
def test_opcode_ba_code_similar_to_3c_but_arg1_is_only_1b_and_arg2_is_0_vanilla():
    """Opcode 0xBA: code similar to 3c, but arg1 is only 1B and arg2 is 0.

    Vanilla ROM examples from script_all:
      - [0x938577] ba 0b 49 79 ba 0b 6b 81 : LOAD NPC 0b at 49 79
      - [0x93857b] ba 0b 6b 81 ba 0b 51 65 : LOAD NPC 0b at 6b 81
      - [0x93857f] ba 0b 51 65 ba 0b 45 4d : LOAD NPC 0b at 51 65
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xBA (LOAD NPC 0b at 49 79)
        eval("BA 0B 49 79 BA 0B 6B 81");
    """

    expected = """
        BA 0B 49 79 BA 0B 6B 81    // (0xBA) LOAD NPC 0b at 49 79
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xBA")
def test_opcode_ba_code_similar_to_3c_but_arg1_is_only_1b_and_arg2_is_0_variations():
    """Variations for Opcode 0xBA:
      Variation 1: [0x938577] ba 0b 49 79 ba 0b 6b 81 (LOAD NPC 0b at 49 79)
      Variation 2: [0x93857b] ba 0b 6b 81 ba 0b 51 65 (LOAD NPC 0b at 6b 81)
      Variation 3: [0x93857f] ba 0b 51 65 ba 0b 45 4d (LOAD NPC 0b at 51 65)
      Variation 4: [0x938583] ba 0b 45 4d ba 0b 19 53 (LOAD NPC 0b at 45 4d)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
