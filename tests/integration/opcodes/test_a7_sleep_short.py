"""Opcode 0xA7: sleep_short."""

from tests.helpers import assert_evs_bytes


def test_opcode_a7_sleep_short():
    """Opcode 0xA7: Sleep short duration (<= 0xff ticks)."""
    script = """
        _sleep(0x10);
    """

    expected = """
        A7          // (a7) SLEEP SHORT DURATION
        10          // sleep ticks: 0x10 (16 ticks)
    """

    assert_evs_bytes(script, expected)
