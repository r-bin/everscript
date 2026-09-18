"""Opcode 0x5B: unknown, checks timer of unframed messages."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x5B")
def test_opcode_5b_unknown_checks_timer_of_unframed_messages_vanilla():
    """Opcode 0x5B: unknown, checks timer of unframed messages.

    Vanilla ROM examples from script_all:
      - [0x94ccc9] 5b 80 a7 3c b4 05 b0 b0 : UNTRACED INSTR, checking message timer
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x5B (UNTRACED INSTR, checking message timer)
        eval("5B 80 A7 3C B4 05 B0 B0");
    """

    expected = """
        5B 80 A7 3C B4 05 B0 B0    // (0x5B) UNTRACED INSTR, checking message timer
    """

    assert_evs_bytes(script, expected)
