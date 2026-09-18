"""Opcode 0x58: fade-in volume according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x58")
def test_opcode_58_fade_in_volume_according_to_darkmoon_vanilla():
    """Opcode 0x58: fade-in volume according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x9387bb] 58 09 0d 15 00 29 31 22 : FADE IN VOLUME
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x58 (FADE IN VOLUME)
        eval("58 09 0D 15 00 29 31 22");
    """

    expected = """
        58 09 0D 15 00 29 31 22    // (0x58) FADE IN VOLUME
    """

    assert_evs_bytes(script, expected)
