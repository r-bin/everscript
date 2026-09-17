"""Opcode 0x04: jump."""

from tests.helpers import assert_evs_bytes


def test_opcode_04_unconditional_jump():
    """Opcode 0x04: Verify unconditional jump emitted by if-else construct."""
    script = """
        if(<ACTIVE> == <BOY>) {
            yield();
        } else {
            end();
        }
    """

    expected = """
        09                  // (09) BRANCH_IF_NOT
            52              // read <ACTIVE>
            29 50           // push <BOY>
            A2              // ==
            04 00           // skip 4 bytes (skips then-body + unconditional jump)
        3A                  // (3A) YIELD (then-body)
        04                  // (04) UNCONDITIONAL JUMP
            01 00           // skip 1 byte (skips else-body)
        00                  // (00) END (else-body)
    """

    assert_evs_bytes(script, expected)
