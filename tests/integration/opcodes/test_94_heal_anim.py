"""Opcode 0x94: ."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x94")
def test_opcode_94_opcode_94_vanilla():
    """Opcode 0x94: .

    Vanilla ROM examples from script_all:
      - [0x94bd22] 94 8d 12 00 02 32 29 12 : HEAL $2846 FOR 0x32 + signed arg0 WITH ANIMATION
      - [0x9683ec] 94 d0 ee aa 09 05 48 00 : HEAL boy FOR 30 WITH ANIMATION
      - [0x9683f7] 94 d1 ee 5b a1 52 e9 0d : HEAL dog FOR 30 WITH ANIMATION
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x94 (HEAL $2846 FOR 0x32 + signed arg0 WITH ANIMATION)
        eval("94 8D 12 00 02 32 29 12");
    """

    expected = """
        94 8D 12 00 02 32 29 12    // (0x94) HEAL $2846 FOR 0x32 + signed arg0 WITH ANIMATION
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x94")
def test_opcode_94_opcode_94_variations():
    """Variations for Opcode 0x94:
      Variation 1: [0x94bd22] 94 8d 12 00 02 32 29 12 (HEAL $2846 FOR 0x32 + signed arg0 WITH ANIMATION)
      Variation 2: [0x9683ec] 94 d0 ee aa 09 05 48 00 (HEAL boy FOR 30 WITH ANIMATION)
      Variation 3: [0x9683f7] 94 d1 ee 5b a1 52 e9 0d (HEAL dog FOR 30 WITH ANIMATION)
      Variation 4: [0x9a8f44] 94 8d 0b 00 64 29 2a 29 (HEAL $283f FOR 20 + (RAND & 0x3f) WITH ANIMATION)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
