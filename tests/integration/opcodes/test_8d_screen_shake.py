"""Opcode 0x8D: start/stop screen shaking."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x8D")
def test_opcode_8d_start_stop_screen_shaking_vanilla():
    """Opcode 0x8D: start/stop screen shaking.

    Vanilla ROM examples from script_all:
      - [0x94ce24] 8d 01 18 b1 01 b1 18 b3 : 01 Start screen shaking
      - [0x94ce6f] 8d 00 a6 b0 fe a3 1f 22 : 00 Stop screen shaking
      - [0xaec404] 8d ff fd ff f2 ff 36 df : ff Start screen shaking
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x8D (01 Start screen shaking)
        eval("8D 01 18 B1 01 B1 18 B3");
    """

    expected = """
        8D 01 18 B1 01 B1 18 B3    // (0x8D) 01 Start screen shaking
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x8D")
def test_opcode_8d_start_stop_screen_shaking_variations():
    """Variations for Opcode 0x8D:
      Variation 1: [0x94ce24] 8d 01 18 b1 01 b1 18 b3 (01 Start screen shaking)
      Variation 2: [0x94ce6f] 8d 00 a6 b0 fe a3 1f 22 (00 Stop screen shaking)
      Variation 3: [0xaec404] 8d ff fd ff f2 ff 36 df (ff Start screen shaking)
      Variation 4: [0xa2ac00] 8d e9 22 4f f9 af 42 0d (e9 Start screen shaking)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
