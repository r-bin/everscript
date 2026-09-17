"""Opcode 0x29: call."""

from tests.helpers import assert_evs_bytes


def test_opcode_29_call():
    """Opcode 0x29: Call script subroutine at 24-bit address."""
    script = """
        call(0x92a3e7);
    """

    expected = """
        29          // (29) CALL SCRIPT SUBROUTINE
        E7 23 00    // 24-bit address / offset ($0023E7)
    """

    assert_evs_bytes(script, expected)
