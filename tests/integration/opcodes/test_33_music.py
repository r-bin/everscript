"""Opcode 0x33: music."""

from tests.helpers import assert_evs_bytes


def test_opcode_33_music():
    """Opcode 0x33: Play music."""
    script = """
        music(0x12);
    """

    expected = """
        33          // (33) PLAY MUSIC
        12          // song/track ID: 0x12
    """

    assert_evs_bytes(script, expected)
