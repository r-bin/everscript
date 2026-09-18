"""Opcode 0x5D: conditional unload? 2bytes addr:bit, sub-instr for obj/sprite id."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x5D")
def test_opcode_5d_conditional_unload_2bytes_addr_bit_sub_instr_for_obj_sprite_id_vanilla():
    """Opcode 0x5D: conditional unload? 2bytes addr:bit, sub-instr for obj/sprite id.

    Vanilla ROM examples from script_all:
      - [0x9385d4] 5d b0 86 00 5d b1 87 00 : IF $2268 & 0x40 THEN UNLOAD OBJ 0 [91m(TODO: verify this)
      - [0x9385d8] 5d b1 87 00 5d b2 88 00 : IF $2268 & 0x80 THEN UNLOAD OBJ 1 [91m(TODO: verify this)
      - [0x9385dc] 5d b2 88 00 5d b3 89 00 : IF $2269 & 0x01 THEN UNLOAD OBJ 2 [91m(TODO: verify this)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x5D (IF $2268 & 0x40 THEN UNLOAD OBJ 0 [91m(TODO: verify this))
        eval("5D B0 86 00 5D B1 87 00");
    """

    expected = """
        5D B0 86 00 5D B1 87 00    // (0x5D) IF $2268 & 0x40 THEN UNLOAD OBJ 0 [91m(TODO: verify this)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x5D")
def test_opcode_5d_conditional_unload_2bytes_addr_bit_sub_instr_for_obj_sprite_id_variations():
    """Variations for Opcode 0x5D:
      Variation 1: [0x9385d4] 5d b0 86 00 5d b1 87 00 (IF $2268 & 0x40 THEN UNLOAD OBJ 0 [91m(TODO: verify this))
      Variation 2: [0x9385d8] 5d b1 87 00 5d b2 88 00 (IF $2268 & 0x80 THEN UNLOAD OBJ 1 [91m(TODO: verify this))
      Variation 3: [0x9385dc] 5d b2 88 00 5d b3 89 00 (IF $2269 & 0x01 THEN UNLOAD OBJ 2 [91m(TODO: verify this))
      Variation 4: [0x9385e0] 5d b3 89 00 5d b4 8a 00 (IF $2269 & 0x02 THEN UNLOAD OBJ 3 [91m(TODO: verify this))
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
