"""Opcode 0x44: open messagebox and wait for next frame?."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x44")
def test_opcode_44_open_messagebox_and_wait_for_next_frame_vanilla():
    """Opcode 0x44: open messagebox and wait for next frame?.

    Vanilla ROM examples from script_all:
      - [0x948021] 44 00 0a 11 14 06 51 f4 : UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0a y=0x11 w=0x14 h=0x06
      - [0x948039] 44 00 02 11 14 07 51 f7 : UNTRACED INSTR, Open messagebox? slot=0x00 x=0x02 y=0x11 w=0x14 h=0x07
      - [0x948045] 44 00 0a 11 14 07 51 fa : UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0a y=0x11 w=0x14 h=0x07
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x44 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0a y=0x11 w=0x14 h=0x06)
        eval("44 00 0A 11 14 06 51 F4");
    """

    expected = """
        44 00 0A 11 14 06 51 F4    // (0x44) UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0a y=0x11 w=0x14 h=0x06
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x44")
def test_opcode_44_open_messagebox_and_wait_for_next_frame_variations():
    """Variations for Opcode 0x44:
      Variation 1: [0x948021] 44 00 0a 11 14 06 51 f4 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0a y=0x11 w=0x14 h=0x06)
      Variation 2: [0x948039] 44 00 02 11 14 07 51 f7 (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x02 y=0x11 w=0x14 h=0x07)
      Variation 3: [0x948045] 44 00 0a 11 14 07 51 fa (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x0a y=0x11 w=0x14 h=0x07)
      Variation 4: [0x948060] 44 00 02 11 14 03 51 fd (UNTRACED INSTR, Open messagebox? slot=0x00 x=0x02 y=0x11 w=0x14 h=0x03)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
