"""Opcode 0x62: reads byte, reads two words, copies some data from unknown region to unknown region."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x62")
def test_opcode_62_reads_byte_reads_two_words_copies_some_data_from_unknown_region_to_unknown_region_vanilla():
    """Opcode 0x62: reads byte, reads two words, copies some data from unknown region to unknown region.

    Vanilla ROM examples from script_all:
      - [0x93ca7e] 62 01 ff 00 01 00 5c b0 : UNTRACED INSTR vals 0x01 0x00ff 0x0001
      - [0x93d2b9] 62 02 ff 00 00 00 09 88 : UNTRACED INSTR vals 0x02 0x00ff 0x0000
      - [0x93ca69] 62 01 ff 00 00 00 5c b0 : UNTRACED INSTR vals 0x01 0x00ff 0x0000
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x62 (UNTRACED INSTR vals 0x01 0x00ff 0x0001)
        eval("62 01 FF 00 01 00 5C B0");
    """

    expected = """
        62 01 FF 00 01 00 5C B0    // (0x62) UNTRACED INSTR vals 0x01 0x00ff 0x0001
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x62")
def test_opcode_62_reads_byte_reads_two_words_copies_some_data_from_unknown_region_to_unknown_region_variations():
    """Variations for Opcode 0x62:
      Variation 1: [0x93ca7e] 62 01 ff 00 01 00 5c b0 (UNTRACED INSTR vals 0x01 0x00ff 0x0001)
      Variation 2: [0x93d2b9] 62 02 ff 00 00 00 09 88 (UNTRACED INSTR vals 0x02 0x00ff 0x0000)
      Variation 3: [0x93ca69] 62 01 ff 00 00 00 5c b0 (UNTRACED INSTR vals 0x01 0x00ff 0x0000)
      Variation 4: [0x93d3df] 62 03 ff 00 05 00 62 03 (UNTRACED INSTR vals 0x03 0x00ff 0x0005)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
