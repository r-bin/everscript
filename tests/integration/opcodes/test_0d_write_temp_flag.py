"""Opcode 0x0D: write_temp_flag."""

from tests.helpers import assert_evs_bytes


def test_opcode_0d_write_temp_flag():
    """Opcode 0x0D: Write bit flag to temp WRAM ($2834..)."""
    script = """
        <0x2834, 0x01> = 0x01;
    """

    expected = """
        0D          // (0D) WRITE TEMP FLAG
        00 00       // temp RAM offset from $2834 (bit index 0)
        B1          // bit flag descriptor: mask & value (bit 0 = 1)
    """

    assert_evs_bytes(script, expected)

# todo: "<0x2834, 0x01> = True;"