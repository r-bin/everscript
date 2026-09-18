"""Opcode 0x7F: show text input (dog's name)."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x7F")
def test_opcode_7f_show_text_input_dog_s_name_vanilla():
    """Opcode 0x7F: show text input (dog's name).

    Vanilla ROM examples from script_all:
      - [0x94d8f9] 7f 03 00 a7 10 75 d0 a7 : SHOW TEXT/NAME INPUT 0x0003
      - [0xaa8119] 7f a7 fe f1 08 9b 42 f9 : SHOW TEXT/NAME INPUT 0xfea7
      - [0xa480d6] 7f c0 1a 1b 90 10 2e 62 : SHOW TEXT/NAME INPUT 0x1ac0
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x7F (SHOW TEXT/NAME INPUT 0x0003)
        eval("7F 03 00 A7 10 75 D0 A7");
    """

    expected = """
        7F 03 00 A7 10 75 D0 A7    // (0x7F) SHOW TEXT/NAME INPUT 0x0003
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x7F")
def test_opcode_7f_show_text_input_dog_s_name_variations():
    """Variations for Opcode 0x7F:
      Variation 1: [0x94d8f9] 7f 03 00 a7 10 75 d0 a7 (SHOW TEXT/NAME INPUT 0x0003)
      Variation 2: [0xaa8119] 7f a7 fe f1 08 9b 42 f9 (SHOW TEXT/NAME INPUT 0xfea7)
      Variation 3: [0xa480d6] 7f c0 1a 1b 90 10 2e 62 (SHOW TEXT/NAME INPUT 0x1ac0)
      Variation 4: [0x9e8209] 7f 7d 03 7f 7d 03 7f 7d (SHOW TEXT/NAME INPUT 0x037d)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
