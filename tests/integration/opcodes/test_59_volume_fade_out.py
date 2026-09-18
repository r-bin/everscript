"""Opcode 0x59: fade-out volume according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x59")
def test_opcode_59_fade_out_volume_according_to_darkmoon_vanilla():
    """Opcode 0x59: fade-out volume according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x98a1ed] 59 a7 10 33 74 00 a3 32 : FADE OUT VOLUME
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x59 (FADE OUT VOLUME)
        eval("59 A7 10 33 74 00 A3 32");
    """

    expected = """
        59 A7 10 33 74 00 A3 32    // (0x59) FADE OUT VOLUME
    """

    assert_evs_bytes(script, expected)
