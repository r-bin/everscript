"""Opcode 0x38: <- according to darkmoon. i only traced 3a."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x38")
def test_opcode_38_according_to_darkmoon_i_only_traced_3a_vanilla():
    """Opcode 0x38: <- according to darkmoon. i only traced 3a.

    Vanilla ROM examples from script_all:
      - [0xabc201] 38 07 70 c2 47 6c 99 db : YIELD (break out of script loop, continue later)
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x38 (YIELD (break out of script loop, continue later))
        eval("38 07 70 C2 47 6C 99 DB");
    """

    expected = """
        38 07 70 C2 47 6C 99 DB    // (0x38) YIELD (break out of script loop, continue later)
    """

    assert_evs_bytes(script, expected)
