"""Opcode 0x9C: runs 1 sub-instr, decrements scripts attached to entity? according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x9C")
def test_opcode_9c_runs_1_sub_instr_decrements_scripts_attached_to_entity_according_to_darkmoon_vanilla():
    """Opcode 0x9C: runs 1 sub-instr, decrements scripts attached to entity? according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x96b0b4] 9c 92 00 00 a7 05 30 4a : DECREMENT SCRIPT COUNTER FOR ENTITY signed arg0 ?
      - [0x9a8d23] 9c 8d 05 00 9c 8d 07 00 : DECREMENT SCRIPT COUNTER FOR ENTITY $2839 ?
      - [0x9a8d27] 9c 8d 07 00 19 09 00 b2 : DECREMENT SCRIPT COUNTER FOR ENTITY $283b ?
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x9C (DECREMENT SCRIPT COUNTER FOR ENTITY signed arg0 ?)
        eval("9C 92 00 00 A7 05 30 4A");
    """

    expected = """
        9C 92 00 00 A7 05 30 4A    // (0x9C) DECREMENT SCRIPT COUNTER FOR ENTITY signed arg0 ?
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x9C")
def test_opcode_9c_runs_1_sub_instr_decrements_scripts_attached_to_entity_according_to_darkmoon_variations():
    """Variations for Opcode 0x9C:
      Variation 1: [0x96b0b4] 9c 92 00 00 a7 05 30 4a (DECREMENT SCRIPT COUNTER FOR ENTITY signed arg0 ?)
      Variation 2: [0x9a8d23] 9c 8d 05 00 9c 8d 07 00 (DECREMENT SCRIPT COUNTER FOR ENTITY $2839 ?)
      Variation 3: [0x9a8d27] 9c 8d 07 00 19 09 00 b2 (DECREMENT SCRIPT COUNTER FOR ENTITY $283b ?)
      Variation 4: [0x99c637] 9c 8d 0c 00 19 0c 00 b0 (DECREMENT SCRIPT COUNTER FOR ENTITY $2840 ?)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
