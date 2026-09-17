"""Opcode 0x86: volume."""

from tests.helpers import assert_evs_bytes


def test_opcode_86_volume():
    """Opcode 0x86: Set audio volume."""
    script = """
        volume(0x64);
    """

    expected = """
        86          // (86) SET AUDIO VOLUME
        82 64       // 1-byte parameter value: 0x64 (0x82 + 0x64)
    """

    assert_evs_bytes(script, expected)
