"""Opcode 0x30: sound."""

from tests.helpers import assert_evs_bytes


def test_opcode_30_sound():
    """Opcode 0x30: Play sound effect."""
    script = """
        sound(0x0a);
    """

    expected = """
        30          // (30) PLAY SOUND EFFECT
        0A          // SFX index: 0x0A
    """

    assert_evs_bytes(script, expected)
