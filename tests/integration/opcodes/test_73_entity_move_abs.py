"""Opcode 0x73: identical format but absolute position, not relative."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x73")
def test_opcode_73_identical_format_but_absolute_position_not_relative_vanilla():
    """Opcode 0x73: identical format but absolute position, not relative.

    Vanilla ROM examples from script_all:
      - [0x978ddb] 73 d3 12 04 29 68 9a 12 : Make non-controlled char walk to signed arg4 + 24,signed arg6 + 16 directly
      - [0x97c979] 73 d0 92 00 92 02 73 d1 : Make boy walk to signed arg0,signed arg2 directly
      - [0x97c97f] 73 d1 92 00 92 02 a9 d0 : Make dog walk to signed arg0,signed arg2 directly
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x73 (Make non-controlled char walk to signed arg4 + 24,signed arg6 + 16 directly)
        eval("73 D3 12 04 29 68 9A 12");
    """

    expected = """
        73 D3 12 04 29 68 9A 12    // (0x73) Make non-controlled char walk to signed arg4 + 24,signed arg6 + 16 directly
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x73")
def test_opcode_73_identical_format_but_absolute_position_not_relative_variations():
    """Variations for Opcode 0x73:
      Variation 1: [0x978ddb] 73 d3 12 04 29 68 9a 12 (Make non-controlled char walk to signed arg4 + 24,signed arg6 + 16 directly)
      Variation 2: [0x97c979] 73 d0 92 00 92 02 73 d1 (Make boy walk to signed arg0,signed arg2 directly)
      Variation 3: [0x97c97f] 73 d1 92 00 92 02 a9 d0 (Make dog walk to signed arg0,signed arg2 directly)
      Variation 4: [0x97cb2d] 73 d0 92 00 12 02 29 32 (Make boy walk to signed arg0,signed arg2 - 2 directly)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
