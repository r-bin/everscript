"""Opcode 0x9D: like 73 but does not ignore barriers."""

import pytest
from tests.helpers import assert_evs_bytes


@pytest.mark.xfail(reason="TODO: Everscript syntax pendant for opcode 0x9D")
def test_opcode_9d_like_73_but_does_not_ignore_barriers_vanilla():
    """Opcode 0x9D: like 73 but does not ignore barriers.

    Vanilla ROM examples from script_all:
      - [0x9b886c] 9d d0 08 61 01 29 38 9a : Make boy walk to $23b9 + 8,$23bb
      - [0x9b8877] 9d d1 08 61 01 29 38 9b : Make dog walk to $23b9 - 8,$23bb
      - [0x9b9ded] 9d d3 88 45 02 88 47 02 : Make non-controlled char walk to $249d,$249f
    """
    # TODO: Implement Everscript high-level syntax for this opcode
    script = """
        // TODO: opcode 0x9D (Make boy walk to $23b9 + 8,$23bb)
        eval("9D D0 08 61 01 29 38 9A");
    """

    expected = """
        9D D0 08 61 01 29 38 9A    // (0x9D) Make boy walk to $23b9 + 8,$23bb
    """

    assert_evs_bytes(script, expected)


@pytest.mark.xfail(reason="TODO: Additional variations for opcode 0x9D")
def test_opcode_9d_like_73_but_does_not_ignore_barriers_variations():
    """Variations for Opcode 0x9D:
      Variation 1: [0x9b886c] 9d d0 08 61 01 29 38 9a (Make boy walk to $23b9 + 8,$23bb)
      Variation 2: [0x9b8877] 9d d1 08 61 01 29 38 9b (Make dog walk to $23b9 - 8,$23bb)
      Variation 3: [0x9b9ded] 9d d3 88 45 02 88 47 02 (Make non-controlled char walk to $249d,$249f)
      Variation 4: [0x9b9983] 9d d3 08 45 02 29 38 9b (Make non-controlled char walk to $249d - 8,$249f)
    """
    pytest.skip("TODO: Additional variations pending syntax implementation")
