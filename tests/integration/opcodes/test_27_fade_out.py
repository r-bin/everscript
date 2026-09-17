"""Opcode 0x27: fade_out."""

from tests.helpers import assert_evs_bytes


def test_opcode_27_fade_out():
    """Opcode 0x27: Fade out screen."""
    script = """
        fade_out();
    """

    expected = """
        27          // (27) FADE OUT SCREEN
    """

    assert_evs_bytes(script, expected)
