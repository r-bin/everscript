"""Opcode 0x0C: write_flag."""

from tests.helpers import assert_evs_bytes


def test_opcode_0c_write_flag():
    """Opcode 0x0C: Write bit flag to persistent WRAM ($2258..)."""
    script = """
        <0x2258, 0x01> = 0x01;
    """

    expected = """
        0C          // (0C) WRITE FLAG
        00 00       // RAM address offset from $2258 (bit index 0)
        B1          // bit flag descriptor: mask & value (bit 0 = 1)
    """

    assert_evs_bytes(script, expected)
