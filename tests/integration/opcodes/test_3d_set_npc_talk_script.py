"""Opcode 0x3D: set NPC talk script."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x3D")
def test_opcode_3d_set_npc_talk_script_vanilla():
    """Opcode 0x3D: set NPC talk script.

    Vanilla ROM examples from script_all:
      - [0x94e7c3] 3d 88 fd 01 63 18 09 88 : WRITE $2455+x66=0x1863, $2455+x68=0x0040 (talk script): Strong Heart (inside Hut)
      - [0x94ceac] 3d ad 42 18 ba 05 47 41 : WRITE last entity ($0341)+x66=0x1842, last entity ($0341)+x68=0x0040 (talk script): FE Village NPC1
      - [0x94ceb8] 3d 8d 1f 00 27 18 1c db : WRITE $2853+x66=0x1827, $2853+x68=0x0040 (talk script): FE Village NPC2/Bee Boy
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x3D (WRITE $2455+x66=0x1863, $2455+x68=0x0040 (talk script): Strong Heart (inside Hut))
        eval("3D 88 FD 01 63 18 09 88");
    """

    expected = """
        3D 88 FD 01 63 18 09 88    // (0x3D) WRITE $2455+x66=0x1863, $2455+x68=0x0040 (talk script): Strong Heart (inside Hut)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x3D")
def test_opcode_3d_set_npc_talk_script_variations():
    """Variations for Opcode 0x3D:
      Variation 1: [0x94e7c3] 3d 88 fd 01 63 18 09 88 (WRITE $2455+x66=0x1863, $2455+x68=0x0040 (talk script): Strong Heart (inside Hut))
      Variation 2: [0x94ceac] 3d ad 42 18 ba 05 47 41 (WRITE last entity ($0341)+x66=0x1842, last entity ($0341)+x68=0x0040 (talk script): FE Village NPC1)
      Variation 3: [0x94ceb8] 3d 8d 1f 00 27 18 1c db (WRITE $2853+x66=0x1827, $2853+x68=0x0040 (talk script): FE Village NPC2/Bee Boy)
      Variation 4: [0x94ced2] 3d 8d 09 00 39 18 ba 06 (WRITE $283d+x66=0x1839, $283d+x68=0x0040 (talk script): FE Village NPC3)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
