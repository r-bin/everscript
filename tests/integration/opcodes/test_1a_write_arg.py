"""Opcode 0x1A: write_arg."""

from tests.helpers import assert_evs_bytes


def test_opcode_1a_write_arg():
    """Opcode 0x1A: Write script argument."""
    script = """
        arg[0x10] = 0x01;
    """

    expected = """
        1A          // (1a) WRITE SCRIPT ARGUMENT
        10          // argument index 0x10
        B1          // calculator operand: 0x01 (compact 1-byte integer: 0xB0 + 0x01)
    """

    assert_evs_bytes(script, expected)
