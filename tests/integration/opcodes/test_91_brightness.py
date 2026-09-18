"""Opcode 0x91: set brightness."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_91_set_brightness():
    """Opcode 0x91: set brightness."""
    script = """
        brightness(0x00);
    """

    expected = """
        91 B0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x91")
def test_opcode_91_set_brightness_variations():
    """Variations for Opcode 0x91:
      Variation 1: [0x94d398] 91 b0 3a 86 82 64 19 05 (Sets brightness to 0)
      Variation 2: [0x94d3ab] 91 8d 05 00 a7 04 19 05 (Sets brightness to $2839)
      Variation 3: [0x93eec7] 91 8d 07 00 a7 04 19 07 (Sets brightness to $283b)
      Variation 4: [0x94857a] 91 8d 11 00 a7 04 19 11 (Sets brightness to $2845)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
