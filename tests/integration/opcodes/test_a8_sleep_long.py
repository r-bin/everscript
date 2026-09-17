"""Opcode 0xA8: sleep_long."""

from tests.helpers import assert_evs_bytes


def test_opcode_a8_sleep_long():
    """Opcode 0xA8: Sleep long duration (> 0xff ticks)."""
    script = """
        _sleep(0x0200);
    """

    expected = """
        A8          // (a8) SLEEP LONG DURATION
        00 02       // sleep ticks: 0x0200 (512 ticks, 16-bit little endian)
    """

    assert_evs_bytes(script, expected)
