"""Opcode 0x7A: write_deref."""

from tests.helpers import assert_evs_bytes


def test_opcode_7a_write_deref():
    """Opcode 0x7A: Write to dereferenced entity attribute."""
    script = """
        <LAST_ENTITY>[HP] = 0x05;
    """

    expected = """
        7A          // (7a) WRITE DEREFERENCED ATTRIBUTE
        2D 29       // base entity address: $292D (<LAST_ENTITY>)
        04          // attribute offset: HP (0x04)
        2A 00       // size / type indicator (word attribute)
        9A          // dereference assignment operator
        B5          // value: 0x05 (compact 1-byte integer: 0xB0 + 0x05)
    """

    assert_evs_bytes(script, expected)
