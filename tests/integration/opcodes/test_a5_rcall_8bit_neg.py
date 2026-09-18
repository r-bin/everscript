"""Opcode 0xA5: 0xa5, looks like a call with a negative 8bit offset."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0xA5")
def test_opcode_a5_0xa5_looks_like_a_call_with_a_negative_8bit_offset_vanilla():
    """Opcode 0xA5: 0xa5, looks like a call with a negative 8bit offset.

    Vanilla ROM examples from script_all:
      - [0x9384fa] a5 ad 18 eb 01 b2 29 ed : RCALL -83 (to 0x9384a7): Unknown
      - [0x94ca55] a5 d1 3c 2a 00 20 00 55 : RCALL -47 (to 0x94ca26): Unknown
      - [0x94ca69] a5 bd 3c 10 00 20 00 4f : RCALL -67 (to 0x94ca26): Unknown
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0xA5 (RCALL -83 (to 0x9384a7): Unknown)
        eval("A5 AD 18 EB 01 B2 29 ED");
    """

    expected = """
        A5 AD 18 EB 01 B2 29 ED    // (0xA5) RCALL -83 (to 0x9384a7): Unknown
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0xA5")
def test_opcode_a5_0xa5_looks_like_a_call_with_a_negative_8bit_offset_variations():
    """Variations for Opcode 0xA5:
      Variation 1: [0x9384fa] a5 ad 18 eb 01 b2 29 ed (RCALL -83 (to 0x9384a7): Unknown)
      Variation 2: [0x94ca55] a5 d1 3c 2a 00 20 00 55 (RCALL -47 (to 0x94ca26): Unknown)
      Variation 3: [0x94ca69] a5 bd 3c 10 00 20 00 4f (RCALL -67 (to 0x94ca26): Unknown)
      Variation 4: [0x94ca7d] a5 a9 3c 0c 00 20 00 4f (RCALL -87 (to 0x94ca26): Unknown)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
