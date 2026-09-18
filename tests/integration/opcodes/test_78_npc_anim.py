"""Opcode 0x78: unknown. changes NPC sprite/animation (maybe also other parameters)."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x78")
def test_opcode_78_unknown_changes_npc_sprite_animation_maybe_also_other_parameters_vanilla():
    """Opcode 0x78: unknown. changes NPC sprite/animation (maybe also other parameters).

    Vanilla ROM examples from script_all:
      - [0x9383e0] 78 d1 72 01 b0 a7 0f 78 : UNTRACED INSTR for dog, 0x0172 0 changes sprite/animation/...?
      - [0x938407] 78 d0 16 00 b0 a3 0a 51 : UNTRACED INSTR for boy, 0x0016 0 changes sprite/animation/...?
      - [0x938414] 78 d0 14 00 b0 a7 20 75 : UNTRACED INSTR for boy, 0x0014 0 changes sprite/animation/...?
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x78 (UNTRACED INSTR for dog, 0x0172 0 changes sprite/animation/...?)
        eval("78 D1 72 01 B0 A7 0F 78");
    """

    expected = """
        78 D1 72 01 B0 A7 0F 78    // (0x78) UNTRACED INSTR for dog, 0x0172 0 changes sprite/animation/...?
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x78")
def test_opcode_78_unknown_changes_npc_sprite_animation_maybe_also_other_parameters_variations():
    """Variations for Opcode 0x78:
      Variation 1: [0x9383e0] 78 d1 72 01 b0 a7 0f 78 (UNTRACED INSTR for dog, 0x0172 0 changes sprite/animation/...?)
      Variation 2: [0x938407] 78 d0 16 00 b0 a3 0a 51 (UNTRACED INSTR for boy, 0x0016 0 changes sprite/animation/...?)
      Variation 3: [0x938414] 78 d0 14 00 b0 a7 20 75 (UNTRACED INSTR for boy, 0x0014 0 changes sprite/animation/...?)
      Variation 4: [0x938423] 78 d1 3e 00 b2 3a a3 0b (UNTRACED INSTR for dog, 0x003e 2 changes sprite/animation/...?)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
