"""Opcode 0x11: like 0x10 but different addr offset."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x11")
def test_opcode_11_like_0x10_but_different_addr_offset_vanilla():
    """Opcode 0x11: like 0x10 but different addr offset.

    Vanilla ROM examples from script_all:
      - [0x94bb17] 11 01 00 2a 29 35 a4 a5 : WRITE $2835 = RAND & 5
      - [0x94e92d] 11 00 00 b1 09 0b 00 00 : WRITE $2834 = 0x0001
      - [0x94e94b] 11 00 00 0b 00 00 29 31 : WRITE $2834 = (($2834)&0xff) + 1
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x11 (WRITE $2835 = RAND & 5)
        eval("11 01 00 2A 29 35 A4 A5");
    """

    expected = """
        11 01 00 2A 29 35 A4 A5    // (0x11) WRITE $2835 = RAND & 5
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x11")
def test_opcode_11_like_0x10_but_different_addr_offset_variations():
    """Variations for Opcode 0x11:
      Variation 1: [0x94bb17] 11 01 00 2a 29 35 a4 a5 (WRITE $2835 = RAND & 5)
      Variation 2: [0x94e92d] 11 00 00 b1 09 0b 00 00 (WRITE $2834 = 0x0001)
      Variation 3: [0x94e94b] 11 00 00 0b 00 00 29 31 (WRITE $2834 = (($2834)&0xff) + 1)
      Variation 4: [0x94ea92] 11 01 00 b1 09 0b 01 00 (WRITE $2835 = 0x0001)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
