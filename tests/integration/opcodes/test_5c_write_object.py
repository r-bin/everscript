"""Opcode 0x5C: write_object."""

from tests.helpers import assert_evs_bytes


def test_opcode_5c_write_object():
    """Opcode 0x5C: Write map object state."""
    script = """
        object[0x05] = 0x7e;
    """

    expected = """
        5C          // (5c) WRITE MAP OBJECT STATE
        B5          // object index: 0x05 (compact 1-byte integer: 0xB0 + 0x05)
        82 7E       // state value: 0x7E (1-byte parameter 0x82 + 0x7E)
    """

    assert_evs_bytes(script, expected)
