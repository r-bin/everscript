"""Opcode 0x19: write_temp_word."""

from tests.helpers import assert_evs_bytes


def test_opcode_19_write_temp_word():
    """Opcode 0x19: Write word to temp WRAM (debug marker)."""
    script = """
        <0x2834> = 0xffff;
    """

    expected = """
        19          // (19) WRITE TEMP WORD
        00 00       // temp RAM offset from $2834
        84          // calculator operand: word literal follows
        FF FF       // 16-bit value: 0xFFFF
    """

    assert_evs_bytes(script, expected)
