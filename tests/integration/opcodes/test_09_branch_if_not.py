"""Opcode 0x09: branch_if_not."""

import pytest
from tests.helpers import assert_evs_bytes


def test_opcode_09_branch_if_not_active_equals_boy():
    """Opcode 0x09: Verify if(<ACTIVE> == <BOY>) emits opcode 09 with operand A2 (==) and skip 1."""
    script = """
        if(<ACTIVE> == <BOY>) {
            end();
        }
    """

    expected = """
        09          // (09) BRANCH_IF_NOT (skip if false)
            52      // <ACTIVE>
            29 50   // push <BOY> (0x50)
            A2      // == (0x22 | 0x80)
            01 00   // forward jump distance: 1 byte
        00          // (00) END
    """

    assert_evs_bytes(script, expected)


def test_opcode_09_branch_if_not_active_not_boy():
    """Opcode 0x09: Verify if(<ACTIVE> != <BOY>) emits opcode 09 with operand A3 (!=) and skip 1 (guard_boy pattern)."""
    script = """
        if(<ACTIVE> != <BOY>) {
            end();
        }
    """

    expected = """
        09          // (09) BRANCH_IF_NOT (skip if false)
            52      // read <ACTIVE> entity type
            29 50   // push <BOY> (0x50)
            A3      // != comparison operator (0x23 | 0x80)
            01 00   // 16-bit forward jump distance (skip 1 byte)
        00          // (00) END
    """

    assert_evs_bytes(script, expected)


def test_opcode_09_branch_if_not_nested_distance():
    """Opcode 0x09: Verify nested if statements calculate jump distances correctly."""
    script = """
        if(<ACTIVE> == <BOY>) {
            if(<ACTIVE> == <BOY>) {
                end();
            }
        }
    """

    expected = """
        09                  // (09) Outer BRANCH_IF_NOT
            52              // read <ACTIVE>
            29 50           // push <BOY>
            A2              // ==
            08 00           // skip 8 bytes (skips entire inner if block)
        09                  // (09) Inner BRANCH_IF_NOT
            52              // read <ACTIVE>
            29 50           // push <BOY>
            A2              // ==
            01 00           // skip 1 byte (skips end())
        00                  // (00) END
    """

    assert_evs_bytes(script, expected)


def test_opcode_09_branch_if_not_multi_statement_distance():
    """Opcode 0x09: Verify if with multiple statements accurately counts all byte lengths."""
    script = """
        if(<ACTIVE> != <BOY>) {
            end();
            end();
            <0x2834> = 0xffff;
        }
    """

    expected = """
        09                  // (09) BRANCH_IF_NOT
            52              // read <ACTIVE>
            29 50           // push <BOY>
            A3              // !=
            08 00           // skip 8 bytes (1 + 1 + 6 bytes)
        00                  // (00) END (1 byte)
        00                  // (00) END (1 byte)
        19 00 00 84 FF FF   // (19) WRITE TEMP WORD (6 bytes)
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="MISMATCH: user specified == with expected byte A3 (!=). == emits A2, != emits A3.")
def test_opcode_09_branch_if_not_user_failing_case():
    """Exact test case from user prompt:
    Input: if(<ACTIVE> == <BOY>) { end(); }
    Expected: 09 52 29 50 a3 01 00  00
    Fails because == compiles to A2, while prompt expected A3 (!=).
    """
    script = """
        if(<ACTIVE> == <BOY>) {
            end();
        }
    """

    expected = """
        09          // (09) BRANCH_IF_NOT
            52      // <ACTIVE>
            29 50   // push <BOY> (0x50)
            A3      // != (mismatch: prompt expected A3 (!=) for == comparison)
            01 00   // skip 1 byte
        00          // (00) END
    """

    assert_evs_bytes(script, expected)
