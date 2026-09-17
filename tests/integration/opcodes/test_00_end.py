"""Opcode 0x00: end."""

from tests.helpers import assert_evs_bytes


def test_opcode_00_end():
    """Opcode 0x00: END / return."""
    script = """
        end();
    """

    expected = """
        00      // (00) END (return from script)
    """

    assert_evs_bytes(script, expected)
