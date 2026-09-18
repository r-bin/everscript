"""Opcode 0x81: unknown, at 8ce209."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x81")
def test_opcode_81_unknown_at_8ce209_vanilla():
    """Opcode 0x81: unknown, at 8ce209.

    Vanilla ROM examples from script_all:
      - [0x938369] 81 c0 18 67 01 b1 6f d1 : HIDE UNWINDOWED TEXT
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x81 (HIDE UNWINDOWED TEXT)
        eval("81 C0 18 67 01 B1 6F D1");
    """

    expected = """
        81 C0 18 67 01 B1 6F D1    // (0x81) HIDE UNWINDOWED TEXT
    """

    assert_evs_bytes(script, expected)
