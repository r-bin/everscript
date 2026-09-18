"""Opcode 0x31: according to darkmoon this."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x31")
def test_opcode_31_according_to_darkmoon_this_vanilla():
    """Opcode 0x31: according to darkmoon this.

    Vanilla ROM examples from script_all:
      - [0xa2838f] 31 0e 05 30 0e 05 32 0e : PLAY SOUND EFFECT 0x0e ??
      - [0x928002] 31 00 1c 0f 61 00 77 16 : PLAY SOUND EFFECT 0x00 ??
      - [0x94d19f] 31 a4 1d 00 0c 82 01 b1 : PLAY SOUND EFFECT 0xa4 ??
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x31 (PLAY SOUND EFFECT 0x0e ??)
        eval("31 0E 05 30 0E 05 32 0E");
    """

    expected = """
        31 0E 05 30 0E 05 32 0E    // (0x31) PLAY SOUND EFFECT 0x0e ??
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x31")
def test_opcode_31_according_to_darkmoon_this_variations():
    """Variations for Opcode 0x31:
      Variation 1: [0xa2838f] 31 0e 05 30 0e 05 32 0e (PLAY SOUND EFFECT 0x0e ??)
      Variation 2: [0x928002] 31 00 1c 0f 61 00 77 16 (PLAY SOUND EFFECT 0x00 ??)
      Variation 3: [0x94d19f] 31 a4 1d 00 0c 82 01 b1 (PLAY SOUND EFFECT 0xa4 ??)
      Variation 4: [0xa48012] 31 9f 03 23 1e 25 1f a2 (PLAY SOUND EFFECT 0x9f ??)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
