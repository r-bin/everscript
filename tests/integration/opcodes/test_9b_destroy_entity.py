"""Opcode 0x9B: unknown, seems to run one sub-instr, dealloc according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_9b_unknown_seems_to_run_one_sub_instr_dealloc_according_to_darkmoon():
    """Opcode 0x9B: unknown, seems to run one sub-instr, dealloc according to darkmoon."""
    script = """
        destroy(BOY);
    """

    expected = """
        9B D0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x9B")
def test_opcode_9b_unknown_seems_to_run_one_sub_instr_dealloc_according_to_darkmoon_variations():
    """Variations for Opcode 0x9B:
      Variation 1: [0x938793] 9b 8d 29 00 5c b4 b1 30 (DESTROY/DEALLOC ENTITY $285d)
      Variation 2: [0x94c962] 9b 8d 23 00 9b 8d 25 00 (DESTROY/DEALLOC ENTITY $2857)
      Variation 3: [0x94c966] 9b 8d 25 00 a3 00 a7 10 (DESTROY/DEALLOC ENTITY $2859)
      Variation 4: [0x94c995] 9b 8d 01 00 00 77 8d 2d (DESTROY/DEALLOC ENTITY $2835)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
