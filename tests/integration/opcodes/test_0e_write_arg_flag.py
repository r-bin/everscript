"""Opcode 0x0E: like 0c and 0d but for script args, not memory, and adress is only 8bit."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x0E")
def test_opcode_0e_like_0c_and_0d_but_for_script_args_not_memory_and_adress_is_only_8bit_vanilla():
    """Opcode 0x0E: like 0c and 0d but for script args, not memory, and adress is only 8bit.

    Vanilla ROM examples from script_all:
      - [0x96abf5] 0e 00 b1 09 08 f7 01 29 : Script arg0 bit 0x01 = 1
      - [0x99eabc] 0e 00 b0 1a 0b 12 07 29 : Script arg0 bit 0x01 = 0
      - [0x978311] 0e 01 b1 0e 02 b1 09 51 : Script arg0 bit 0x02 = 1
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x0E (Script arg0 bit 0x01 = 1)
        eval("0E 00 B1 09 08 F7 01 29");
    """

    expected = """
        0E 00 B1 09 08 F7 01 29    // (0x0E) Script arg0 bit 0x01 = 1
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x0E")
def test_opcode_0e_like_0c_and_0d_but_for_script_args_not_memory_and_adress_is_only_8bit_variations():
    """Variations for Opcode 0x0E:
      Variation 1: [0x96abf5] 0e 00 b1 09 08 f7 01 29 (Script arg0 bit 0x01 = 1)
      Variation 2: [0x99eabc] 0e 00 b0 1a 0b 12 07 29 (Script arg0 bit 0x01 = 0)
      Variation 3: [0x978311] 0e 01 b1 0e 02 b1 09 51 (Script arg0 bit 0x02 = 1)
      Variation 4: [0x978314] 0e 02 b1 09 51 29 52 a2 (Script arg0 bit 0x04 = 1)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
