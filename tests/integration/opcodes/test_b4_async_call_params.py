"""Opcode 0xB4: async_call_params."""

from tests.helpers import assert_evs_bytes


def test_opcode_b4_async_call_params():
    """Opcode 0xB4: Async call installed function with parameters."""
    script = """
        @install()
        @async()
        fun target_async(a) {
            yield();
        }

        fun test_b4() {
            target_async(0x12);
        }
    """

    expected = """
        B4          // (b4) ASYNC CALL SCRIPT WITH PARAMETERS
        01          // parameter count: 1
        E2          // compact arg: 0x12 (0xD0 + 0x12 = 0xE2)
        xx xx xx    // 24-bit target subroutine address
    """

    assert_evs_bytes(script, expected, name="test_b4")
