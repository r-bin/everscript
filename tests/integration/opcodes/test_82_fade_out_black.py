"""Opcode 0x82: fade_out_black."""

from tests.helpers import assert_evs_bytes


def test_opcode_82_fade_out_black():
    """Opcode 0x82: Fade out black."""
    script = """
        fade_out_black();
    """

    expected = """
        82          // (82) FADE OUT TO BLACK
    """

    assert_evs_bytes(script, expected)
