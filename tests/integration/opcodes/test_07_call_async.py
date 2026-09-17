"""Opcode 0x07: call_async."""

from tests.helpers import assert_evs_bytes


def test_opcode_07_call_async():
    """Opcode 0x07: Async call to absolute script address."""
    script = """
        call_async(0x92a3e7);
    """

    expected = """
        07          // (07) ASYNC CALL
        E7 23 00    // 24-bit ROM address offset ($92a3e7 - $928000 = 0x0023e7, little-endian)
    """

    assert_evs_bytes(script, expected)
