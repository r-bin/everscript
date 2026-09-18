"""Opcode 0x52: set text from word list in next two bytes + 91d000."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_52_set_text_from_word_list_in_next_two_bytes_91d000():
    """Opcode 0x52: set text from word list in next two bytes + 91d000."""
    script = """
        _subtext(0x0123);
    """

    expected = """
        52 23 01
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x52")
def test_opcode_52_set_text_from_word_list_in_next_two_bytes_91d000_variations():
    """Variations for Opcode 0x52:
      Variation 1: [0x938857] 52 82 05 a7 14 14 bd 00 (SHOW TEXT 0582 FROM 0x91d582 compressed UNWINDOWED)
      Variation 2: [0x938865] 52 85 05 18 7b 01 b0 30 (SHOW TEXT 0585 FROM 0x91d585 compressed UNWINDOWED)
      Variation 3: [0x94dc11] 52 9c 09 a7 78 14 c4 00 (SHOW TEXT 099c FROM 0x91d99c compressed UNWINDOWED)
      Variation 4: [0x94ddd9] 52 d5 09 a3 00 33 78 a3 (SHOW TEXT 09d5 FROM 0x91d9d5 compressed UNWINDOWED)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
