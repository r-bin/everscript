"""Opcode 0xAC: alchemy attack according to darkmoon, exclude dog if dead."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xAC")
def test_opcode_ac_alchemy_attack_according_to_darkmoon_exclude_dog_if_dead_vanilla():
    """Opcode 0xAC: alchemy attack according to darkmoon, exclude dog if dead.

    Vanilla ROM examples from script_all:
      - [0x93cb56] ac 8d 35 00 b0 82 32 d0 : $2869 CASTS SPELL 0 POWER 0x32 ON boy, dog if alive
      - [0x93cb87] ac 8d 35 00 82 28 82 c8 : $2869 CASTS SPELL 0x28 POWER 0xc8 ON boy, dog if alive
      - [0x93cbb3] ac 8d 35 00 b2 82 c8 d0 : $2869 CASTS SPELL 2 POWER 0xc8 ON boy, dog if alive
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xAC ($2869 CASTS SPELL 0 POWER 0x32 ON boy, dog if alive)
        eval("AC 8D 35 00 B0 82 32 D0");
    """

    expected = """
        AC 8D 35 00 B0 82 32 D0    // (0xAC) $2869 CASTS SPELL 0 POWER 0x32 ON boy, dog if alive
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xAC")
def test_opcode_ac_alchemy_attack_according_to_darkmoon_exclude_dog_if_dead_variations():
    """Variations for Opcode 0xAC:
      Variation 1: [0x93cb56] ac 8d 35 00 b0 82 32 d0 ($2869 CASTS SPELL 0 POWER 0x32 ON boy, dog if alive)
      Variation 2: [0x93cb87] ac 8d 35 00 82 28 82 c8 ($2869 CASTS SPELL 0x28 POWER 0xc8 ON boy, dog if alive)
      Variation 3: [0x93cbb3] ac 8d 35 00 b2 82 c8 d0 ($2869 CASTS SPELL 2 POWER 0xc8 ON boy, dog if alive)
      Variation 4: [0x95ae99] ac 8d 07 00 e8 82 4b d0 ($283b CASTS SPELL 24 POWER 0x4b ON boy, dog if alive)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
