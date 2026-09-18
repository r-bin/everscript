"""Opcode 0xB9: relative teleport according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xB9")
def test_opcode_b9_relative_teleport_according_to_darkmoon_vanilla():
    """Opcode 0xB9: relative teleport according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x99eaee] b9 8d 01 00 b0 12 03 29 : Teleport $2835 by x:0, y:signed arg3 - signed arg5
      - [0x99eb2d] b9 8d 01 00 92 09 12 03 : Teleport $2835 by x:signed arg9, y:signed arg3 - signed arg5
      - [0x9bac73] b9 d0 b0 8d 01 00 b9 d1 : Teleport boy by x:0, y:$2835
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xB9 (Teleport $2835 by x:0, y:signed arg3 - signed arg5)
        eval("B9 8D 01 00 B0 12 03 29");
    """

    expected = """
        B9 8D 01 00 B0 12 03 29    // (0xB9) Teleport $2835 by x:0, y:signed arg3 - signed arg5
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xB9")
def test_opcode_b9_relative_teleport_according_to_darkmoon_variations():
    """Variations for Opcode 0xB9:
      Variation 1: [0x99eaee] b9 8d 01 00 b0 12 03 29 (Teleport $2835 by x:0, y:signed arg3 - signed arg5)
      Variation 2: [0x99eb2d] b9 8d 01 00 92 09 12 03 (Teleport $2835 by x:signed arg9, y:signed arg3 - signed arg5)
      Variation 3: [0x9bac73] b9 d0 b0 8d 01 00 b9 d1 (Teleport boy by x:0, y:$2835)
      Variation 4: [0x9bac79] b9 d1 b0 8d 01 00 3a 19 (Teleport dog by x:0, y:$2835)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
