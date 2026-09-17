"""Opcode 0x18: write_word."""

from tests.helpers import assert_evs_bytes


def test_opcode_18_write_word():
    """Opcode 0x18: Write word to persistent WRAM."""
    script = """
        <0x2258> = 0x1234;
    """

    expected = """
        18          // (18) WRITE WORD
        00 00       // RAM offset from $2258 ($2258 - $2258 = 0)
        84          // calculator operand: word literal follows
        34 12       // 16-bit value: 0x1234 (little-endian)
    """

    assert_evs_bytes(script, expected)
