"""Opcode 0x43: Teleport entity from sub-instr to sub-instr,sub-instr."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x43")
def test_opcode_43_teleport_entity_from_sub_instr_to_sub_instr_sub_instr_vanilla():
    """Opcode 0x43: Teleport entity from sub-instr to sub-instr,sub-instr.

    Vanilla ROM examples from script_all:
      - [0x9390d4] 43 8d 29 00 08 3b 02 29 : Teleport $285d to x:$2493 + signed arg4, y:$2495 + signed arg2
      - [0x94ce5f] 43 d0 88 61 01 88 63 01 : Teleport boy to x:$23b9, y:$23bb
      - [0x94ce67] 43 d1 88 61 01 88 63 01 : Teleport dog to x:$23b9, y:$23bb
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x43 (Teleport $285d to x:$2493 + signed arg4, y:$2495 + signed arg2)
        eval("43 8D 29 00 08 3B 02 29");
    """

    expected = """
        43 8D 29 00 08 3B 02 29    // (0x43) Teleport $285d to x:$2493 + signed arg4, y:$2495 + signed arg2
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x43")
def test_opcode_43_teleport_entity_from_sub_instr_to_sub_instr_sub_instr_variations():
    """Variations for Opcode 0x43:
      Variation 1: [0x9390d4] 43 8d 29 00 08 3b 02 29 (Teleport $285d to x:$2493 + signed arg4, y:$2495 + signed arg2)
      Variation 2: [0x94ce5f] 43 d0 88 61 01 88 63 01 (Teleport boy to x:$23b9, y:$23bb)
      Variation 3: [0x94ce67] 43 d1 88 61 01 88 63 01 (Teleport dog to x:$23b9, y:$23bb)
      Variation 4: [0x94ca39] 43 ad 8d 33 00 8d 35 00 (Teleport last entity ($0341) to x:$2867, y:$2869)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
