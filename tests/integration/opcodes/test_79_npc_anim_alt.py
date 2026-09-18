"""Opcode 0x79: similar to 78, used after washing ashore in Crustacia."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x79")
def test_opcode_79_similar_to_78_used_after_washing_ashore_in_crustacia_vanilla():
    """Opcode 0x79: similar to 78, used after washing ashore in Crustacia.

    Vanilla ROM examples from script_all:
      - [0x938402] 79 d0 18 00 b0 78 d0 16 : UNTRACED INSTR for boy, 0x0018 0 changes sprite/animation/...?
      - [0x94c918] 79 8d 01 00 96 00 b0 ba : UNTRACED INSTR for $2835, 0x0096 0 changes sprite/animation/...?
      - [0x94ddc8] 79 88 03 02 00 00 b0 80 : UNTRACED INSTR for $245b, 0x0000 0 changes sprite/animation/...?
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x79 (UNTRACED INSTR for boy, 0x0018 0 changes sprite/animation/...?)
        eval("79 D0 18 00 B0 78 D0 16");
    """

    expected = """
        79 D0 18 00 B0 78 D0 16    // (0x79) UNTRACED INSTR for boy, 0x0018 0 changes sprite/animation/...?
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x79")
def test_opcode_79_similar_to_78_used_after_washing_ashore_in_crustacia_variations():
    """Variations for Opcode 0x79:
      Variation 1: [0x938402] 79 d0 18 00 b0 78 d0 16 (UNTRACED INSTR for boy, 0x0018 0 changes sprite/animation/...?)
      Variation 2: [0x94c918] 79 8d 01 00 96 00 b0 ba (UNTRACED INSTR for $2835, 0x0096 0 changes sprite/animation/...?)
      Variation 3: [0x94ddc8] 79 88 03 02 00 00 b0 80 (UNTRACED INSTR for $245b, 0x0000 0 changes sprite/animation/...?)
      Variation 4: [0x93d954] 79 8d 0b 00 78 00 b0 78 (UNTRACED INSTR for $283f, 0x0078 0 changes sprite/animation/...?)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
