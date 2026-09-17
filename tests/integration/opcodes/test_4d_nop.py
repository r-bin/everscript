"""Opcode 0x4D: nop."""

from tests.helpers import assert_evs_bytes


def test_opcode_4d_nop():
    """Opcode 0x4D: NOP instruction."""
    script = """
        nop();
    """

    expected = """
        4D          // (4d) NOP INSTRUCTION
    """

    assert_evs_bytes(script, expected)
