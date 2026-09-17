"""Opcode 0x3A: yield."""

from tests.helpers import assert_evs_bytes


def test_opcode_3a_yield():
    """Opcode 0x3A: Yield script execution loop."""
    script = """
        yield();
    """

    expected = """
        3A          // (3a) YIELD EXECUTION LOOP
    """

    assert_evs_bytes(script, expected)
