"""Opcode 0xAF: call_params."""

from tests.helpers import assert_evs_bytes


def test_opcode_af_call_params():
    """Opcode 0xAF: Call installed function with parameters."""
    script = """
        @install()
        fun target(a) {
            yield();
        }

        fun test_af() {
            target(0x12);
        }
    """

    expected = """
        AF          // (af) CALL SCRIPT WITH PARAMETERS
        01          // parameter count: 1
        E2          // compact arg: 0x12 (0xD0 + 0x12 = 0xE2)
        xx xx xx    // 24-bit target subroutine address
    """

    assert_evs_bytes(script, expected, name="test_af")
