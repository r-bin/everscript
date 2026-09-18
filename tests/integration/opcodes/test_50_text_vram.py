"""Opcode 0x50: like 0x51, but 1 byte "destination in vram"."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x50")
def test_opcode_50_like_0x51_but_1_byte_destination_in_vram_vanilla():
    """Opcode 0x50: like 0x51, but 1 byte "destination in vram".

    Vanilla ROM examples from script_all:
      - [0x9bbd65] 50 01 ff 21 54 01 a7 08 : SHOW TEXT 21ff FROM 0x91f1ff uncompressed (UNWINDOWED) IN #1
      - [0x9bbd73] 50 01 02 22 54 01 6f d0 : SHOW TEXT 2202 FROM 0x91f202 compressed (UNWINDOWED) IN #1
      - [0x9bbd98] 50 01 05 22 54 01 a7 20 : SHOW TEXT 2205 FROM 0x91f205 compressed (UNWINDOWED) IN #1
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x50 (SHOW TEXT 21ff FROM 0x91f1ff uncompressed (UNWINDOWED) IN #1)
        eval("50 01 FF 21 54 01 A7 08");
    """

    expected = """
        50 01 FF 21 54 01 A7 08    // (0x50) SHOW TEXT 21ff FROM 0x91f1ff uncompressed (UNWINDOWED) IN #1
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x50")
def test_opcode_50_like_0x51_but_1_byte_destination_in_vram_variations():
    """Variations for Opcode 0x50:
      Variation 1: [0x9bbd65] 50 01 ff 21 54 01 a7 08 (SHOW TEXT 21ff FROM 0x91f1ff uncompressed (UNWINDOWED) IN #1)
      Variation 2: [0x9bbd73] 50 01 02 22 54 01 6f d0 (SHOW TEXT 2202 FROM 0x91f202 compressed (UNWINDOWED) IN #1)
      Variation 3: [0x9bbd98] 50 01 05 22 54 01 a7 20 (SHOW TEXT 2205 FROM 0x91f205 compressed (UNWINDOWED) IN #1)
      Variation 4: [0x9bbde6] 50 01 08 22 a7 78 50 01 (SHOW TEXT 2208 FROM 0x91f208 uncompressed (UNWINDOWED) IN #1)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
