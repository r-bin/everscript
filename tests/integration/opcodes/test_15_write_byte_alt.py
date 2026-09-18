"""Opcode 0x15: same as 0x11."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x15")
def test_opcode_15_same_as_0x11_vanilla():
    """Opcode 0x15: same as 0x11.

    Vanilla ROM examples from script_all:
      - [0xaccb03] 15 83 2f 06 11 3f ff ff : WRITE $57b7 = ($6169)&0xff [unknown 0x7f]
      - [0x9c9217] 15 bd 19 a1 40 88 16 60 : WRITE $41f1 =
      - [0xa080c9] 15 15 1a 16 4b 0f 23 25 : WRITE $4249 = - -5 arg4&0x08
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x15 (WRITE $57b7 = ($6169)&0xff [unknown 0x7f])
        eval("15 83 2F 06 11 3F FF FF");
    """

    expected = """
        15 83 2F 06 11 3F FF FF    // (0x15) WRITE $57b7 = ($6169)&0xff [unknown 0x7f]
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x15")
def test_opcode_15_same_as_0x11_variations():
    """Variations for Opcode 0x15:
      Variation 1: [0xaccb03] 15 83 2f 06 11 3f ff ff (WRITE $57b7 = ($6169)&0xff [unknown 0x7f])
      Variation 2: [0x9c9217] 15 bd 19 a1 40 88 16 60 (WRITE $41f1 =)
      Variation 3: [0xa080c9] 15 15 1a 16 4b 0f 23 25 (WRITE $4249 = - -5 arg4&0x08)
      Variation 4: [0xa080ca] 15 1a 16 4b 0f 23 25 27 (WRITE $3e4e = -5 arg4&0x08)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
