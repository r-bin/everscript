"""Opcode 0xA9: unknown, seems to run 2 subinstrs. prime examples A9 D0 E2 and A9 D1 E2."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xA9")
def test_opcode_a9_unknown_seems_to_run_2_subinstrs_prime_examples_a9_d0_e2_and_a9_d1_e2_vanilla():
    """Opcode 0xA9: unknown, seems to run 2 subinstrs. prime examples A9 D0 E2 and A9 D1 E2.

    Vanilla ROM examples from script_all:
      - [0x938676] a9 d0 e2 a9 d1 e2 6f d0 : UNTRACED INSTR modifies entity boy bits 18
      - [0x938679] a9 d1 e2 6f d0 b0 ca 6f : UNTRACED INSTR modifies entity dog bits 18
      - [0x9383bd] a9 d1 82 34 30 24 1b d3 : UNTRACED INSTR modifies entity dog bits 0x34
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xA9 (UNTRACED INSTR modifies entity boy bits 18)
        eval("A9 D0 E2 A9 D1 E2 6F D0");
    """

    expected = """
        A9 D0 E2 A9 D1 E2 6F D0    // (0xA9) UNTRACED INSTR modifies entity boy bits 18
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xA9")
def test_opcode_a9_unknown_seems_to_run_2_subinstrs_prime_examples_a9_d0_e2_and_a9_d1_e2_variations():
    """Variations for Opcode 0xA9:
      Variation 1: [0x938676] a9 d0 e2 a9 d1 e2 6f d0 (UNTRACED INSTR modifies entity boy bits 18)
      Variation 2: [0x938679] a9 d1 e2 6f d0 b0 ca 6f (UNTRACED INSTR modifies entity dog bits 18)
      Variation 3: [0x9383bd] a9 d1 82 34 30 24 1b d3 (UNTRACED INSTR modifies entity dog bits 0x34)
      Variation 4: [0x93ac2b] a9 92 00 ea b4 03 88 45 (UNTRACED INSTR modifies entity signed arg0 bits 26)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
