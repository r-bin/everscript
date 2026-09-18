"""Opcode 0x17: set value fast."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x17")
def test_opcode_17_set_value_fast_vanilla():
    """Opcode 0x17: set value fast.

    Vanilla ROM examples from script_all:
      - [0x9380bb] 17 3d 01 05 00 a3 3a 0c : WRITE MAP REF? ($2395) = 0x0005
      - [0x938037] 17 3d 01 00 00 a3 3a 0c : WRITE MAP REF? ($2395) = 0x0000
      - [0x93806b] 17 3d 01 02 00 a3 3a 0c : WRITE MAP REF? ($2395) = 0x0002
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x17 (WRITE MAP REF? ($2395) = 0x0005)
        eval("17 3D 01 05 00 A3 3A 0C");
    """

    expected = """
        17 3D 01 05 00 A3 3A 0C    // (0x17) WRITE MAP REF? ($2395) = 0x0005
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x17")
def test_opcode_17_set_value_fast_variations():
    """Variations for Opcode 0x17:
      Variation 1: [0x9380bb] 17 3d 01 05 00 a3 3a 0c (WRITE MAP REF? ($2395) = 0x0005)
      Variation 2: [0x938037] 17 3d 01 00 00 a3 3a 0c (WRITE MAP REF? ($2395) = 0x0000)
      Variation 3: [0x93806b] 17 3d 01 02 00 a3 3a 0c (WRITE MAP REF? ($2395) = 0x0002)
      Variation 4: [0x93809f] 17 3d 01 04 00 a3 3a 0c (WRITE MAP REF? ($2395) = 0x0004)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
