"""Opcode 0xBB: damage showing number according to darmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xBB")
def test_opcode_bb_damage_showing_number_according_to_darmoon_vanilla():
    """Opcode 0xBB: damage showing number according to darmoon.

    Vanilla ROM examples from script_all:
      - [0x98ad09] bb d2 92 00 18 5b 02 ba : DAMAGE controlled char FOR signed arg0 SHOWING NUMBER
      - [0x98ad1a] bb d3 92 02 19 11 00 d8 : DAMAGE non-controlled char FOR signed arg2 SHOWING NUMBER
      - [0x9c8900] bb 13 b1 51 99 b1 38 33 : DAMAGE arg177 dog [invalid 0x19] FOR ? SHOWING NUMBER
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xBB (DAMAGE controlled char FOR signed arg0 SHOWING NUMBER)
        eval("BB D2 92 00 18 5B 02 BA");
    """

    expected = """
        BB D2 92 00 18 5B 02 BA    // (0xBB) DAMAGE controlled char FOR signed arg0 SHOWING NUMBER
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xBB")
def test_opcode_bb_damage_showing_number_according_to_darmoon_variations():
    """Variations for Opcode 0xBB:
      Variation 1: [0x98ad09] bb d2 92 00 18 5b 02 ba (DAMAGE controlled char FOR signed arg0 SHOWING NUMBER)
      Variation 2: [0x98ad1a] bb d3 92 02 19 11 00 d8 (DAMAGE non-controlled char FOR signed arg2 SHOWING NUMBER)
      Variation 3: [0x9c8900] bb 13 b1 51 99 b1 38 33 (DAMAGE arg177 dog [invalid 0x19] FOR ? SHOWING NUMBER)
      Variation 4: [0x93b90b] bb c4 00 5d bc c5 00 5d (DAMAGE -12 FOR [invalid 0x5d] SHOWING NUMBER)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
