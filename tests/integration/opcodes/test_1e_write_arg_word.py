"""Opcode 0x1E: ."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x1E")
def test_opcode_1e_opcode_1e_vanilla():
    """Opcode 0x1E: .

    Vanilla ROM examples from script_all:
      - [0x96d081] 1e 00 0e 21 00 29 0e 23 : WRITE SCRIPT arg0 = $2855 - $2857
      - [0x96d099] 1e 00 b0 04 0f 00 1e 00 : WRITE SCRIPT arg0 = 0
      - [0x96d09f] 1e 00 04 ff ff 29 0e 23 : WRITE SCRIPT arg0 = (0xffff - $2857) + $2855
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x1E (WRITE SCRIPT arg0 = $2855 - $2857)
        eval("1E 00 0E 21 00 29 0E 23");
    """

    expected = """
        1E 00 0E 21 00 29 0E 23    // (0x1E) WRITE SCRIPT arg0 = $2855 - $2857
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x1E")
def test_opcode_1e_opcode_1e_variations():
    """Variations for Opcode 0x1E:
      Variation 1: [0x96d081] 1e 00 0e 21 00 29 0e 23 (WRITE SCRIPT arg0 = $2855 - $2857)
      Variation 2: [0x96d099] 1e 00 b0 04 0f 00 1e 00 (WRITE SCRIPT arg0 = 0)
      Variation 3: [0x96d09f] 1e 00 04 ff ff 29 0e 23 (WRITE SCRIPT arg0 = (0xffff - $2857) + $2855)
      Variation 4: [0x96d0be] 1e 00 0e 25 00 29 33 9d (WRITE SCRIPT arg0 = $2859>>3)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
