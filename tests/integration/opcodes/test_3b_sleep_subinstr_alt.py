"""Opcode 0x3B: the same according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x3B")
def test_opcode_3b_the_same_according_to_darkmoon_vanilla():
    """Opcode 0x3B: the same according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x97ac57] 3b 39 29 31 9a 5c e1 b1 : SLEEP 9 + 1 TICKS
      - [0x97ad9a] 3b b9 5c e9 b1 a7 08 30 : SLEEP 9 TICKS
      - [0x97a7c5] 3b 2a 29 37 24 29 36 9c : SLEEP (RAND & 7)<<6 TICKS
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x3B (SLEEP 9 + 1 TICKS)
        eval("3B 39 29 31 9A 5C E1 B1");
    """

    expected = """
        3B 39 29 31 9A 5C E1 B1    // (0x3B) SLEEP 9 + 1 TICKS
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x3B")
def test_opcode_3b_the_same_according_to_darkmoon_variations():
    """Variations for Opcode 0x3B:
      Variation 1: [0x97ac57] 3b 39 29 31 9a 5c e1 b1 (SLEEP 9 + 1 TICKS)
      Variation 2: [0x97ad9a] 3b b9 5c e9 b1 a7 08 30 (SLEEP 9 TICKS)
      Variation 3: [0x97a7c5] 3b 2a 29 37 24 29 36 9c (SLEEP (RAND & 7)<<6 TICKS)
      Variation 4: [0x97e95c] 3b 02 3f 29 2a 29 02 7f (SLEEP 0x3f + (RAND & 0x7f) TICKS)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
