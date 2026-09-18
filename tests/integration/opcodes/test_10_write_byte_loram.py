"""Opcode 0x10: same as 0x18, but only writes 1 byte, not two."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x10")
def test_opcode_10_same_as_0x18_but_only_writes_1_byte_not_two_vanilla():
    """Opcode 0x10: same as 0x18, but only writes 1 byte, not two.

    Vanilla ROM examples from script_all:
      - [0x97cbfb] 10 a6 00 06 a6 00 29 31 : WRITE $22fe = (($22fe)&0xff) + 1
      - [0x94e8cf] 10 a2 00 e0 10 a3 00 e4 : WRITE $22fa = 0x0010
      - [0x94e8d3] 10 a3 00 e4 29 75 5e 00 : WRITE $22fb = 0x0014
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x10 (WRITE $22fe = (($22fe)&0xff) + 1)
        eval("10 A6 00 06 A6 00 29 31");
    """

    expected = """
        10 A6 00 06 A6 00 29 31    // (0x10) WRITE $22fe = (($22fe)&0xff) + 1
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x10")
def test_opcode_10_same_as_0x18_but_only_writes_1_byte_not_two_variations():
    """Variations for Opcode 0x10:
      Variation 1: [0x97cbfb] 10 a6 00 06 a6 00 29 31 (WRITE $22fe = (($22fe)&0xff) + 1)
      Variation 2: [0x94e8cf] 10 a2 00 e0 10 a3 00 e4 (WRITE $22fa = 0x0010)
      Variation 3: [0x94e8d3] 10 a3 00 e4 29 75 5e 00 (WRITE $22fb = 0x0014)
      Variation 4: [0x95ea90] 10 a5 00 b4 10 a4 00 e1 (WRITE DESERT WRAP X? ($22fd) = 0x0004)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
