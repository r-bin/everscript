"""Opcode 0x08: branch_if."""

from tests.helpers import assert_evs_bytes


def test_opcode_08_branch_if():
    """Opcode 0x08: BRANCH_IF (emitted by if!)."""
    script = """
        if!(<ACTIVE> == <BOY>) {
            end();
        }
    """

    expected = """
        08          // (08) BRANCH_IF (skip if true)
            52      // <ACTIVE>
            29 50   // push <BOY> (0x50)
            A2      // == (0x22 | 0x80)
            01 00   // forward jump distance: 1 byte
        00          // (00) END
    """

    assert_evs_bytes(script, expected)
