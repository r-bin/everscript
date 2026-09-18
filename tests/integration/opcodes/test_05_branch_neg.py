"""Opcode 0x05: 0x05, unconditional negative branch."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x05")
def test_opcode_05_0x05_unconditional_negative_branch_vanilla():
    """Opcode 0x05: 0x05, unconditional negative branch.

    Vanilla ROM examples from script_all:
      - [0x93921e] 05 ec a6 7d fe 00 a3 00 : SKIP -20 (to 0x93920a)
      - [0x9390ff] 05 cd 43 8d 29 00 08 3b : SKIP -51 (to 0x9390cc)
      - [0x938825] 05 97 09 05 aa 04 94 4e : SKIP -105 (to 0x9387bc)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x05 (SKIP -20 (to 0x93920a))
        eval("05 EC A6 7D FE 00 A3 00");
    """

    expected = """
        05 EC A6 7D FE 00 A3 00    // (0x05) SKIP -20 (to 0x93920a)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x05")
def test_opcode_05_0x05_unconditional_negative_branch_variations():
    """Variations for Opcode 0x05:
      Variation 1: [0x93921e] 05 ec a6 7d fe 00 a3 00 (SKIP -20 (to 0x93920a))
      Variation 2: [0x9390ff] 05 cd 43 8d 29 00 08 3b (SKIP -51 (to 0x9390cc))
      Variation 3: [0x938825] 05 97 09 05 aa 04 94 4e (SKIP -105 (to 0x9387bc))
      Variation 4: [0x94d3ba] 05 e8 a7 3c 6f 8d 03 00 (SKIP -24 (to 0x94d3a2))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
