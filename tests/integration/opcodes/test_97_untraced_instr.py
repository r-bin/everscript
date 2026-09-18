"""Opcode 0x97: unknown, runs 7 sub-instrs."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x97")
def test_opcode_97_unknown_runs_7_sub_instrs_vanilla():
    """Opcode 0x97: unknown, runs 7 sub-instrs.

    Vanilla ROM examples from script_all:
      - [0x9aabdf] 97 b0 b0 b0 84 00 01 84 : UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, 0x0100, 0x0842, 0x71, 15
      - [0x9aabfa] 97 b0 b0 b0 92 00 84 42 : UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, signed arg0, 0x0842, 0x71, 15
      - [0x92e2f2] 97 b0 b0 b0 92 1a 84 00 : UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, signed arg26, 0x0400, 0x81, 0x7f
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x97 (UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, 0x0100, 0x0842, 0x71, 15)
        eval("97 B0 B0 B0 84 00 01 84");
    """

    expected = """
        97 B0 B0 B0 84 00 01 84    // (0x97) UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, 0x0100, 0x0842, 0x71, 15
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x97")
def test_opcode_97_unknown_runs_7_sub_instrs_variations():
    """Variations for Opcode 0x97:
      Variation 1: [0x9aabdf] 97 b0 b0 b0 84 00 01 84 (UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, 0x0100, 0x0842, 0x71, 15)
      Variation 2: [0x9aabfa] 97 b0 b0 b0 92 00 84 42 (UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, signed arg0, 0x0842, 0x71, 15)
      Variation 3: [0x92e2f2] 97 b0 b0 b0 92 1a 84 00 (UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, signed arg26, 0x0400, 0x81, 0x7f)
      Variation 4: [0x97e3cd] 97 b0 b0 b0 12 00 29 31 (UNTRACED INSTR 0x97, 7 sub-instrs: 0, 0, 0, signed arg0>>1, 0x6fea, 0x28, 3)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
