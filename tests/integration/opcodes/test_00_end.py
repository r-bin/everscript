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


# todo: test mode that traverses the bytes and checks if the end of the script is reached correctly (e.g. "end(); end();" should only reach the first end and both do not reach the end)