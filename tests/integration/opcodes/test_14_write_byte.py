"""Opcode 0x14: write_byte."""

from tests.helpers import assert_evs_bytes


def test_opcode_14_write_byte():
    """Opcode 0x14: Write byte to WRAM."""
    script = """
        MEMORY.CURRENT_WEAPON_TYPE = 0x01;
    """

    expected = """
        14          // (14) WRITE BYTE
        08 01       // RAM address offset from $2258 ($2360 - $2258 = 0x0108, little-endian)
        B1          // byte literal: 0x01 (encoded as 0xB0 + value)
    """

    assert_evs_bytes(script, expected)
