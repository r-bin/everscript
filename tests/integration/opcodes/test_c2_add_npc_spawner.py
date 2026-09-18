"""Opcode 0xC2: unknown, reads 3 bytes, accesses rom, writes to some object."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xC2")
def test_opcode_c2_unknown_reads_3_bytes_accesses_rom_writes_to_some_object_vanilla():
    """Opcode 0xC2: unknown, reads 3 bytes, accesses rom, writes to some object.

    Vanilla ROM examples from script_all:
      - [0x93b23e] c2 0b 2f 45 c2 0b 1d 2d : Add NPC 0x0b spawner at 0x2f,0x45
      - [0x93b242] c2 0b 1d 2d c2 0b 35 1d : Add NPC 0x0b spawner at 0x1d,0x2d
      - [0x93b246] c2 0b 35 1d c2 0b 31 2d : Add NPC 0x0b spawner at 0x35,0x1d
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xC2 (Add NPC 0x0b spawner at 0x2f,0x45)
        eval("C2 0B 2F 45 C2 0B 1D 2D");
    """

    expected = """
        C2 0B 2F 45 C2 0B 1D 2D    // (0xC2) Add NPC 0x0b spawner at 0x2f,0x45
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xC2")
def test_opcode_c2_unknown_reads_3_bytes_accesses_rom_writes_to_some_object_variations():
    """Variations for Opcode 0xC2:
      Variation 1: [0x93b23e] c2 0b 2f 45 c2 0b 1d 2d (Add NPC 0x0b spawner at 0x2f,0x45)
      Variation 2: [0x93b242] c2 0b 1d 2d c2 0b 35 1d (Add NPC 0x0b spawner at 0x1d,0x2d)
      Variation 3: [0x93b246] c2 0b 35 1d c2 0b 31 2d (Add NPC 0x0b spawner at 0x35,0x1d)
      Variation 4: [0x93b24a] c2 0b 31 2d c2 0b 0d 18 (Add NPC 0x0b spawner at 0x31,0x2d)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
