"""Opcode 0x88: clear ring menu item list according to darkmoon."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_88_clear_ring_menu_item_list_according_to_darkmoon():
    """Opcode 0x88: clear ring menu item list according to darkmoon."""
    script = """
        clear_shop();
    """

    expected = """
        88
    """

    assert_evs_bytes(script, expected)
