"""Opcode 0x1D: counter-part to 0x1c? what's the difference to 0x19?."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x1D")
def test_opcode_1d_counter_part_to_0x1c_what_s_the_difference_to_0x19_vanilla():
    """Opcode 0x1D: counter-part to 0x1c? what's the difference to 0x19?.

    Vanilla ROM examples from script_all:
      - [0x93a3b6] 1d 71 00 d8 09 08 d1 01 : WRITE $28a5 = GameTimer&0xffff
      - [0x93a053] 1d 63 00 d8 09 08 d1 01 : WRITE $2897 = GameTimer&0xffff
      - [0x939fd8] 1d 61 00 d8 09 08 d1 01 : WRITE $2895 = GameTimer&0xffff
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x1D (WRITE $28a5 = GameTimer&0xffff)
        eval("1D 71 00 D8 09 08 D1 01");
    """

    expected = """
        1D 71 00 D8 09 08 D1 01    // (0x1D) WRITE $28a5 = GameTimer&0xffff
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x1D")
def test_opcode_1d_counter_part_to_0x1c_what_s_the_difference_to_0x19_variations():
    """Variations for Opcode 0x1D:
      Variation 1: [0x93a3b6] 1d 71 00 d8 09 08 d1 01 (WRITE $28a5 = GameTimer&0xffff)
      Variation 2: [0x93a053] 1d 63 00 d8 09 08 d1 01 (WRITE $2897 = GameTimer&0xffff)
      Variation 3: [0x939fd8] 1d 61 00 d8 09 08 d1 01 (WRITE $2895 = GameTimer&0xffff)
      Variation 4: [0x93a1c6] 1d 69 00 d8 09 08 d1 01 (WRITE $289d = GameTimer&0xffff)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
