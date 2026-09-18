"""Opcode 0x71: face each other."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_71_face_each_other():
    """Opcode 0x71: face each other."""
    script = """
        face_each(BOY, DOG);
    """

    expected = """
        71 D0 D1
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x71")
def test_opcode_71_face_each_other_variations():
    """Variations for Opcode 0x71:
      Variation 1: [0x95cb84] 71 d0 d1 a3 07 51 dc 0b (Make boy and dog face each other)
      Variation 2: [0x98d7fb] 71 8d 01 00 d2 3a 09 d7 (Make $2835 and controlled char face each other)
      Variation 3: [0x94c668] 71 8d 05 00 d0 a7 09 a3 (Make $2839 and boy face each other)
      Variation 4: [0x92a040] 71 ae d2 3a 5a 00 5b 2d (Make entity attached to script? and controlled char face each other)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
