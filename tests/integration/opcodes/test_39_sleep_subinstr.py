"""Opcode 0x39: sleep from subinstr according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x39")
def test_opcode_39_sleep_from_subinstr_according_to_darkmoon_vanilla():
    """Opcode 0x39: sleep from subinstr according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0xa281de] 39 63 c2 58 20 53 2a a8 : SLEEP 19 -14 TICKS
      - [0xaac001] 39 99 99 99 99 99 83 7d : SLEEP [invalid 0x19] TICKS
      - [0xa39901] 39 aa 9c 31 50 d8 5e 8e : SLEEP RAND TICKS
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x39 (SLEEP 19 -14 TICKS)
        eval("39 63 C2 58 20 53 2A A8");
    """

    expected = """
        39 63 C2 58 20 53 2A A8    // (0x39) SLEEP 19 -14 TICKS
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x39")
def test_opcode_39_sleep_from_subinstr_according_to_darkmoon_variations():
    """Variations for Opcode 0x39:
      Variation 1: [0xa281de] 39 63 c2 58 20 53 2a a8 (SLEEP 19 -14 TICKS)
      Variation 2: [0xaac001] 39 99 99 99 99 99 83 7d (SLEEP [invalid 0x19] TICKS)
      Variation 3: [0xa39901] 39 aa 9c 31 50 d8 5e 8e (SLEEP RAND TICKS)
      Variation 4: [0x92bc03] 39 01 29 04 1e 04 a2 06 (SLEEP 0x29 signed 0x041e TICKS)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
