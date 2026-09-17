"""Opcode 0xA3: call_id."""

from tests.helpers import assert_evs_bytes


def test_opcode_a3_call_id():
    """Opcode 0xA3: Call global script by ID."""
    script = """
        call_id(0x3d);
    """

    expected = """
        A3          // (a3) CALL GLOBAL SCRIPT BY ID
        3D          // script index/ID: 0x3D
    """

    assert_evs_bytes(script, expected)
