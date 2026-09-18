"""Opcode 0xAE: unknown, modifies current script."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xAE")
def test_opcode_ae_unknown_modifies_current_script_vanilla():
    """Opcode 0xAE: unknown, modifies current script.

    Vanilla ROM examples from script_all:
      - [0x94ce2e] ae 00 02 4a 48 18 d3 01 : UNTRACED INSTR, vals 00 02 4a 48 modifies current script
      - [0x93b134] ae 06 08 09 37 a2 0e 00 : UNTRACED INSTR, vals 06 08 09 37 modifies current script
      - [0x93c805] ae 00 02 15 1b 04 75 00 : UNTRACED INSTR, vals 00 02 15 1b modifies current script
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xAE (UNTRACED INSTR, vals 00 02 4a 48 modifies current script)
        eval("AE 00 02 4A 48 18 D3 01");
    """

    expected = """
        AE 00 02 4A 48 18 D3 01    // (0xAE) UNTRACED INSTR, vals 00 02 4a 48 modifies current script
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xAE")
def test_opcode_ae_unknown_modifies_current_script_variations():
    """Variations for Opcode 0xAE:
      Variation 1: [0x94ce2e] ae 00 02 4a 48 18 d3 01 (UNTRACED INSTR, vals 00 02 4a 48 modifies current script)
      Variation 2: [0x93b134] ae 06 08 09 37 a2 0e 00 (UNTRACED INSTR, vals 06 08 09 37 modifies current script)
      Variation 3: [0x93c805] ae 00 02 15 1b 04 75 00 (UNTRACED INSTR, vals 00 02 15 1b modifies current script)
      Variation 4: [0x93c815] ae 00 02 1b 1b 04 65 00 (UNTRACED INSTR, vals 00 02 1b 1b modifies current script)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
