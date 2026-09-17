"""Opcode 0x8E: if_currency_ge."""

from tests.helpers import assert_evs_bytes


def test_opcode_8e_if_currency_ge():
    """Opcode 0x8E: Currency >= conditional jump."""
    script = """
        if_currency(<0x2348> < 0d10) {
            end();
        }
    """

    expected = """
        8E          // (8e) IF CURRENCY >= JUMP
        89 F0 00    // currency address/type: <0x2348>
        BA          // comparison amount: 10 (compact 1-byte integer: 0xB0 + 0x0A)
        01 00       // jump offset (+1 byte)
        00          // (00) END
    """

    assert_evs_bytes(script, expected)
