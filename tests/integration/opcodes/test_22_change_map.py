"""Opcode 0x22: change_map."""

from tests.helpers import assert_evs_bytes


def test_opcode_22_change_map():
    """Opcode 0x22: Change map / teleport."""
    script = """
        load_map(MAP.FLOWERS, 0x10, 0x20);
    """

    expected = """
        22          // (22) LOAD MAP / TELEPORT
        10          // target X coordinate: 0x10
        20          // target Y coordinate: 0x20
        38 00       // map ID: MAP.FLOWERS (0x0038)
    """

    assert_evs_bytes(script, expected)
