"""Opcode 0x4E: ."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_4e_opcode_4e():
    """Opcode 0x4E: ."""
    script = """
        attach_to_script(BOY);
    """

    expected = """
        4E D0
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x4E")
def test_opcode_4e_opcode_4e_variations():
    """Variations for Opcode 0x4E:
      Variation 1: [0x99cfa6] 4e 8d 01 00 18 45 02 50 (ATTACH entity $2835 TO SCRIPT)
      Variation 2: [0x92d51e] 4e 92 00 95 ae b1 a9 ae (ATTACH entity signed arg0 TO SCRIPT)
      Variation 3: [0x99989b] 4e 8d 09 00 18 45 02 50 (ATTACH entity $283d TO SCRIPT)
      Variation 4: [0x9badfd] 4e ad 9c ae 3f ae 00 03 (ATTACH entity last entity ($0341) TO SCRIPT)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
