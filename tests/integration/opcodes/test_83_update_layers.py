"""Opcode 0x83: (updates what layers are rendered, called after variables are modified)."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_83_updates_what_layers_are_rendered_called_after_variables_are_modified():
    """Opcode 0x83: (updates what layers are rendered, called after variables are modified)."""
    script = """
        update_ui();
    """

    expected = """
        83
    """

    assert_evs_bytes(script, expected)
