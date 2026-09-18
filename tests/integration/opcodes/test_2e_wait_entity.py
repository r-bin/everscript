"""Opcode 0x2E: get entity pointer using sub-instr, modify some object in 3bc9+(pointer+0x6c), modify current script (timer?)."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_2e_get_entity_pointer_using_sub_instr_modify_some_object_in_3bc9_pointer_0x6c_modify_current_script_timer():
    """Opcode 0x2E: get entity pointer using sub-instr, modify some object in 3bc9+(pointer+0x6c), modify current script (timer?)."""
    script = """
        wait(BOY);
    """

    expected = """
        2E D0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x2E")
def test_opcode_2e_get_entity_pointer_using_sub_instr_modify_some_object_in_3bc9_pointer_0x6c_modify_current_script_timer_variations():
    """Variations for Opcode 0x2E:
      Variation 1: [0x9384b0] 2e d0 77 d0 a7 1e 76 d0 (Wait for boy (d0) to reach destination)
      Variation 2: [0x938686] 2e d1 bf 77 d0 a7 1e 76 (Wait for dog (d1) to reach destination)
      Variation 3: [0x938394] 2e b2 a3 09 51 64 05 55 (Wait for character #2 ?! to reach destination)
      Variation 4: [0x9390ed] 2e 8d 29 00 1a 02 12 02 (Wait for entity from *$285d to reach destination)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
