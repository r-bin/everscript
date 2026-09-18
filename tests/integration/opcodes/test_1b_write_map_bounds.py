"""Opcode 0x1B: set two values fast."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_1b_set_two_values_fast():
    """Opcode 0x1B: set two values fast."""
    script = """
        init_map(0x00, 0x10, 0x0400, 0x04b0);
    """

    expected = """
        1B 91 01 93 01 00 10 1B 95 01 97 01 00 04 B0 04
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x1B")
def test_opcode_1b_set_two_values_fast_variations():
    """Variations for Opcode 0x1B:
      Variation 1: [0x9384df] 1b 91 01 93 01 00 02 1b (WRITE MAP X start ($23e9) = 0x0000)
      Variation 2: [0x9384df] 1b 91 01 93 01 00 02 1b (WRITE MAP Y start ($23eb) = 0x0010)
      Variation 3: [0x9384e6] 1b 95 01 97 01 80 96 08 (WRITE MAP X end   ($23ed) = 0x0400)
      Variation 4: [0x9384e6] 1b 95 01 97 01 80 96 08 (WRITE MAP Y end   ($23ef) = 0x04b0)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
