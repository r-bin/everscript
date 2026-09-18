"""Opcode 0x80: unknown, clears msbit in unframed message timer."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x80")
def test_opcode_80_unknown_clears_msbit_in_unframed_message_timer_vanilla():
    """Opcode 0x80: unknown, clears msbit in unframed message timer.

    Vanilla ROM examples from script_all:
      - [0x9384a5] 80 00 c0 6c d0 49 79 6c : UNHIDE? UNWINDOWED TEXT
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x80 (UNHIDE? UNWINDOWED TEXT)
        eval("80 00 C0 6C D0 49 79 6C");
    """

    expected = """
        80 00 C0 6C D0 49 79 6C    // (0x80) UNHIDE? UNWINDOWED TEXT
    """

    assert_evs_bytes(script, expected)
