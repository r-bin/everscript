"""Opcode 0x9E: alchemy attack according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x9E")
def test_opcode_9e_alchemy_attack_according_to_darkmoon_vanilla():
    """Opcode 0x9E: alchemy attack according to darkmoon.

    Vanilla ROM examples from script_all:
      - [0x97a4cb] 9e 8d 00 00 92 02 82 2d : $2834 CASTS SPELL signed arg2 POWER 0x2d ON boy
      - [0x95888c] 9e 8d 04 00 82 22 82 28 : $2838 CASTS SPELL 0x22 POWER 0x28 ON boy
      - [0x95893e] 9e 8d 06 00 82 28 82 28 : $283a CASTS SPELL 0x28 POWER 0x28 ON boy
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x9E ($2834 CASTS SPELL signed arg2 POWER 0x2d ON boy)
        eval("9E 8D 00 00 92 02 82 2D");
    """

    expected = """
        9E 8D 00 00 92 02 82 2D    // (0x9E) $2834 CASTS SPELL signed arg2 POWER 0x2d ON boy
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x9E")
def test_opcode_9e_alchemy_attack_according_to_darkmoon_variations():
    """Variations for Opcode 0x9E:
      Variation 1: [0x97a4cb] 9e 8d 00 00 92 02 82 2d ($2834 CASTS SPELL signed arg2 POWER 0x2d ON boy)
      Variation 2: [0x95888c] 9e 8d 04 00 82 22 82 28 ($2838 CASTS SPELL 0x22 POWER 0x28 ON boy)
      Variation 3: [0x95893e] 9e 8d 06 00 82 28 82 28 ($283a CASTS SPELL 0x28 POWER 0x28 ON boy)
      Variation 4: [0x99c4f7] 9e 8d 0c 00 92 00 92 02 ($2840 CASTS SPELL signed arg0 POWER signed arg2 ON boy)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
