"""Opcode 0x32: and this is also sound effect. any difference?."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x32")
def test_opcode_32_and_this_is_also_sound_effect_any_difference_vanilla():
    """Opcode 0x32: and this is also sound effect. any difference?.

    Vanilla ROM examples from script_all:
      - [0xaa8117] 32 3f 7f a7 fe f1 08 9b : PLAY SOUND EFFECT 0x3f ??
      - [0xa89a04] 32 02 d8 5a a2 18 a8 80 : PLAY SOUND EFFECT 0x02 ??
      - [0x969304] 32 a2 07 00 19 27 00 ba : PLAY SOUND EFFECT 0xa2 ??
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x32 (PLAY SOUND EFFECT 0x3f ??)
        eval("32 3F 7F A7 FE F1 08 9B");
    """

    expected = """
        32 3F 7F A7 FE F1 08 9B    // (0x32) PLAY SOUND EFFECT 0x3f ??
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x32")
def test_opcode_32_and_this_is_also_sound_effect_any_difference_variations():
    """Variations for Opcode 0x32:
      Variation 1: [0xaa8117] 32 3f 7f a7 fe f1 08 9b (PLAY SOUND EFFECT 0x3f ??)
      Variation 2: [0xa89a04] 32 02 d8 5a a2 18 a8 80 (PLAY SOUND EFFECT 0x02 ??)
      Variation 3: [0x969304] 32 a2 07 00 19 27 00 ba (PLAY SOUND EFFECT 0xa2 ??)
      Variation 4: [0x969204] 32 17 1e a7 0b 00 18 0b (PLAY SOUND EFFECT 0x17 ??)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
