"""Opcode 0x51: set text from word list in next two bytes + 91d000."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_51_set_text_from_word_list_in_next_two_bytes_91d000():
    """Opcode 0x51: set text from word list in next two bytes + 91d000."""
    script = """
        text(0x0123);
    """

    expected = """
        51 23 01
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x51")
def test_opcode_51_set_text_from_word_list_in_next_two_bytes_91d000_variations():
    """Variations for Opcode 0x51:
      Variation 1: [0x938398] 51 64 05 55 6f d0 b2 b0 (SHOW TEXT 0564 FROM 0x91d564 compressed WINDOWED)
      Variation 2: [0x9383a8] 51 67 05 55 77 d0 a7 18 (SHOW TEXT 0567 FROM 0x91d567 compressed WINDOWED)
      Variation 3: [0x9383b2] 51 6a 05 55 76 d1 3a 6f (SHOW TEXT 056a FROM 0x91d56a compressed WINDOWED)
      Variation 4: [0x9383dc] 51 6d 05 55 78 d1 72 01 (SHOW TEXT 056d FROM 0x91d56d compressed WINDOWED)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
