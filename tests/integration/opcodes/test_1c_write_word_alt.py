"""Opcode 0x1C: what's the difference to 0x18? $04 maybe?."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x1C")
def test_opcode_1c_what_s_the_difference_to_0x18_04_maybe_vanilla():
    """Opcode 0x1C: what's the difference to 0x18? $04 maybe?.

    Vanilla ROM examples from script_all:
      - [0x94cd88] 1c db 02 8d 13 00 ba 03 : WRITE $2533 = $2847
      - [0x94cdbc] 1c db 02 8d 11 00 ba 02 : WRITE $2533 = $2845
      - [0x94cebe] 1c db 02 ad ba 02 47 41 : WRITE $2533 = last entity ($0341)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x1C (WRITE $2533 = $2847)
        eval("1C DB 02 8D 13 00 BA 03");
    """

    expected = """
        1C DB 02 8D 13 00 BA 03    // (0x1C) WRITE $2533 = $2847
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x1C")
def test_opcode_1c_what_s_the_difference_to_0x18_04_maybe_variations():
    """Variations for Opcode 0x1C:
      Variation 1: [0x94cd88] 1c db 02 8d 13 00 ba 03 (WRITE $2533 = $2847)
      Variation 2: [0x94cdbc] 1c db 02 8d 11 00 ba 02 (WRITE $2533 = $2845)
      Variation 3: [0x94cebe] 1c db 02 ad ba 02 47 41 (WRITE $2533 = last entity ($0341))
      Variation 4: [0x94cf02] 1c db 02 8d 0d 00 ba 02 (WRITE $2533 = $2841)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
