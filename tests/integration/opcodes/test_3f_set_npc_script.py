"""Opcode 0x3F: set NPC script."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x3F")
def test_opcode_3f_set_npc_script_vanilla():
    """Opcode 0x3F: set NPC script.

    Vanilla ROM examples from script_all:
      - [0x938504] 3f b1 40 00 2b 17 18 43 : WRITE $0ea2+0=0x40, $0eac+0=0x172b (unknown): Unknown 0eac+0 (set in lots of places)?
      - [0x9385af] 3f d0 00 02 ac 17 08 85 : WRITE boy+x68=0x200, boy+x66=0x17ac (set script): Unnamed NPC Kill script 0x17ac
      - [0x93915d] 3f 8d 01 00 00 02 af 17 : WRITE $2835+x68=0x200, $2835+x66=0x17af (set script): Raptors kill
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x3F (WRITE $0ea2+0=0x40, $0eac+0=0x172b (unknown): Unknown 0eac+0 (set in lots of places)?)
        eval("3F B1 40 00 2B 17 18 43");
    """

    expected = """
        3F B1 40 00 2B 17 18 43    // (0x3F) WRITE $0ea2+0=0x40, $0eac+0=0x172b (unknown): Unknown 0eac+0 (set in lots of places)?
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x3F")
def test_opcode_3f_set_npc_script_variations():
    """Variations for Opcode 0x3F:
      Variation 1: [0x938504] 3f b1 40 00 2b 17 18 43 (WRITE $0ea2+0=0x40, $0eac+0=0x172b (unknown): Unknown 0eac+0 (set in lots of places)?)
      Variation 2: [0x9385af] 3f d0 00 02 ac 17 08 85 (WRITE boy+x68=0x200, boy+x66=0x17ac (set script): Unnamed NPC Kill script 0x17ac)
      Variation 3: [0x93915d] 3f 8d 01 00 00 02 af 17 (WRITE $2835+x68=0x200, $2835+x66=0x17af (set script): Raptors kill)
      Variation 4: [0x939170] 3f 8d 03 00 00 02 af 17 (WRITE $2837+x68=0x200, $2837+x66=0x17af (set script): Raptors kill)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
