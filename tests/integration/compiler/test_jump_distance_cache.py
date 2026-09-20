"""Relative jump distances must not leak between call sites of a shared function.

`Function_Base.code()` caches its result on the AST node, keyed only on whether
any params were passed. But a jump node's emitted bytes embed `self.distance`,
which the enclosing `If_list` recomputes for *every* call site. Core functions
are shared AST node graphs inlined at many call sites, so without invalidating
the cache when `distance` changes, one call site's distance is served to
another.

The failure is not subtle in game: the `if` jumps to an address that is not an
instruction boundary, the VM decodes garbage, and the SNES locks up. It was
found as a freeze when hitting a mud stone, traced to
`guard_boy()` inside `guard_bone()` emitting `SKIP 8` where the body it should
skip is 1 byte.

Regression guard for the fix in `Function_Base.distance` (compiler/ast_core.py).
"""

from tests.helpers import clean_byte_string, compile_functions

# `guard_boy(callback)` in in/core/.../01_guards.evs is:
#
#     if(<ACTIVE> != <BOY>) {
#         if(callback is Function) { callback(); }
#         end();
#     }
#
# Called bare, the inner if folds away at compile time, so the outer if's body
# is just `end()` -- one byte, so the jump distance must be 1.
GUARD_BOY_IF = "09 52 29 50 A3"          # if(<ACTIVE> != <BOY>) ...
END = "00"
DEBUG_MARKER = "19 00 00 84 FF FF"
FAKE_B = "78 D2 06 80 B0"


def test_bare_guard_boy_skips_only_its_own_body():
    """Baseline: on its own, the bare call site emits distance 1."""
    out = compile_functions(
        """#include("in/core")
fun only_bare() { guard_boy(); debug_marker(); end(); }
""",
        ["only_bare"],
    )["only_bare"]

    assert clean_byte_string(out) == clean_byte_string(
        f"{GUARD_BOY_IF} 01 00 {END} {DEBUG_MARKER} {END}"
    )


def test_callback_call_site_does_not_leak_its_distance_to_a_bare_one():
    """A call site *with* a callback must not change what a bare one emits.

    Before the fix this returned `06 00` for the bare site -- the distance
    belonging to the callback site -- which lands in the middle of the
    `debug_marker()` instruction that follows.
    """
    out = compile_functions(
        """#include("in/core")
fun a_with_callback() { guard_boy({ fake_b(); }); }
fun b_bare()          { guard_boy(); debug_marker(); end(); }
""",
        ["a_with_callback", "b_bare"],
    )

    # The callback site's body is fake_b() + end() = 6 bytes.
    assert clean_byte_string(out["a_with_callback"]) == clean_byte_string(
        f"{GUARD_BOY_IF} 06 00 {FAKE_B} {END}"
    )
    # The bare site's body is still just end() = 1 byte.
    assert clean_byte_string(out["b_bare"]) == clean_byte_string(
        f"{GUARD_BOY_IF} 01 00 {END} {DEBUG_MARKER} {END}"
    ), "the bare call site inherited the callback call site's jump distance"


def test_leak_is_independent_of_declaration_order():
    """The bare site must be correct whether it is compiled first or second."""
    bare_first = compile_functions(
        """#include("in/core")
fun b_bare()          { guard_boy(); debug_marker(); end(); }
fun a_with_callback() { guard_boy({ fake_b(); }); }
""",
        ["b_bare", "a_with_callback"],
    )
    bare_second = compile_functions(
        """#include("in/core")
fun a_with_callback() { guard_boy({ fake_b(); }); }
fun b_bare()          { guard_boy(); debug_marker(); end(); }
""",
        ["b_bare", "a_with_callback"],
    )

    for label, out in (("bare first", bare_first), ("bare second", bare_second)):
        assert clean_byte_string(out["b_bare"]) == clean_byte_string(
            f"{GUARD_BOY_IF} 01 00 {END} {DEBUG_MARKER} {END}"
        ), f"bare call site wrong when compiled {label}"


def test_guard_bone_jump_lands_on_an_instruction_boundary():
    """The exact shape that froze the game.

    `guard_bone()` is `guard_boy(); debug_marker(); if(weapon != sword) end();`.
    The first if must skip only its own `end()`, landing on the
    `debug_marker()` that follows -- not past it into the next instruction.
    """
    out = compile_functions(
        """#include("in/core")
fun other_user() { guard_boy({ fake_b(); }); }
fun bone()       { guard_bone(); }
""",
        ["other_user", "bone"],
    )["bone"]

    tokens = clean_byte_string(out).split()
    # The first instruction is the guard_boy if; its distance is bytes 5..6.
    assert tokens[:5] == GUARD_BOY_IF.split(), tokens[:8]
    distance = int(tokens[5], 16) | (int(tokens[6], 16) << 8)

    # Walk forward from the end of the if and collect valid instruction starts.
    body = tokens[7:]
    assert body[0] == END, "expected the if body to be a single end()"
    assert distance == 1, (
        f"guard_boy() should skip its 1-byte body, got {distance}; "
        f"target would land inside the following instruction"
    )


def test_distance_setter_clears_the_code_cache():
    """Unit-level guard on the mechanism itself."""
    from compiler.ast_everscript import Jump

    jump = Jump(4)
    jump.cache_code = "stale"

    jump.distance = 4          # unchanged -- cache may stand
    assert jump.cache_code == "stale"

    jump.distance = 9          # changed -- cache must be dropped
    assert jump.cache_code is None
    assert jump.distance == 9
