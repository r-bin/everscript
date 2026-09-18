"""Opcode 0x6E: get entity pointer using sub-instr, create some object in 3bc9+*3bc7, attach to pointer+0x6c."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x6E")
def test_opcode_6e_get_entity_pointer_using_sub_instr_create_some_object_in_3bc9_3bc7_attach_to_pointer_0x6c_vanilla():
    """Opcode 0x6E: get entity pointer using sub-instr, create some object in 3bc9+*3bc7, attach to pointer+0x6c.

    Vanilla ROM examples from script_all:
      - [0x938766] 6e d2 1c 1f 6e d3 20 1f : Make controlled char walk to x=0x1c,y=0x1f
      - [0x93876a] 6e d3 20 1f 2e d2 2e d3 : Make non-controlled char walk to x=0x20,y=0x1f
      - [0x94ccfe] 6e 8d 29 00 79 65 b4 05 : Make $285d walk to x=0x79,y=0x65
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x6E (Make controlled char walk to x=0x1c,y=0x1f)
        eval("6E D2 1C 1F 6E D3 20 1F");
    """

    expected = """
        6E D2 1C 1F 6E D3 20 1F    // (0x6E) Make controlled char walk to x=0x1c,y=0x1f
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x6E")
def test_opcode_6e_get_entity_pointer_using_sub_instr_create_some_object_in_3bc9_3bc7_attach_to_pointer_0x6c_variations():
    """Variations for Opcode 0x6E:
      Variation 1: [0x938766] 6e d2 1c 1f 6e d3 20 1f (Make controlled char walk to x=0x1c,y=0x1f)
      Variation 2: [0x93876a] 6e d3 20 1f 2e d2 2e d3 (Make non-controlled char walk to x=0x20,y=0x1f)
      Variation 3: [0x94ccfe] 6e 8d 29 00 79 65 b4 05 (Make $285d walk to x=0x79,y=0x65)
      Variation 4: [0x94cdde] 6e 8d 01 00 45 57 a7 78 (Make $2835 walk to x=0x45,y=0x57)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
