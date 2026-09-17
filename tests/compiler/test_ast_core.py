"""Tests for the Word class in compiler/ast_core.py.

Covers hex literal parsing, decimal literal parsing (including the 0d3 bug),
value_count sizing, and code() output.
"""

import pytest
from rply import Token
from compiler.ast_core import Word


def make_hex_token(s: str) -> Token:
    return Token("WORD", s)


def make_dec_token(s: str) -> Token:
    return Token("WORD_DECIMAL", s)


# ---------------------------------------------------------------------------
# Hex literals
# ---------------------------------------------------------------------------

class TestWordHex:
    def test_one_byte_hex_value(self):
        w = Word(make_hex_token("0x12"))
        assert w.value == 0x12

    def test_one_byte_hex_size(self):
        w = Word(make_hex_token("0x12"))
        assert w.value_count() == 1

    def test_two_byte_hex_value(self):
        w = Word(make_hex_token("0x1234"))
        assert w.value == 0x1234

    def test_two_byte_hex_size(self):
        w = Word(make_hex_token("0x1234"))
        assert w.value_count() == 2

    def test_three_byte_hex_size(self):
        w = Word(make_hex_token("0x928000"))
        assert w.value_count() == 3
        assert w.value == 0x928000

    def test_uppercase_hex(self):
        w = Word(make_hex_token("0xFF"))
        assert w.value == 0xFF

    def test_negative_hex(self):
        w = Word(make_hex_token("-0x01"))
        assert w.value == -1

    def test_explicit_two_byte(self):
        # When a Token is passed, _value_count is derived from the hex string
        # length — the value_count constructor arg only applies when an int or
        # Word is passed.  0x12 is a 1-byte literal regardless of the param.
        # Use force_value_count() to override after construction.
        w = Word(make_hex_token("0x12"))
        w.force_value_count(2)
        assert w.value_count() == 2

    def test_hex_code_one_byte(self):
        w = Word(make_hex_token("0xAB"))
        assert w.code([]) == "AB"

    def test_hex_code_two_byte_little_endian(self):
        # 0x1234 stored little-endian → "34 12"
        w = Word(make_hex_token("0x1234"))
        assert w.code([]) == "34 12"


# ---------------------------------------------------------------------------
# Decimal literals
# ---------------------------------------------------------------------------

class TestWordDecimal:
    def test_decimal_255_value(self):
        w = Word(make_dec_token("0d255"), is_decimal=True)
        assert w.value == 255

    def test_decimal_255_size(self):
        # 255 ≤ 0xff and digit string "255" has len < 4 → 1 byte
        w = Word(make_dec_token("0d255"), is_decimal=True)
        assert w.value_count() == 1

    def test_decimal_256_size(self):
        # 256 > 0xff → 2 bytes
        w = Word(make_dec_token("0d256"), is_decimal=True)
        assert w.value_count() == 2

    def test_decimal_zero_padded_4chars_size(self):
        # "0003" has len >= 4 → forced to 2 bytes regardless of value
        w = Word(make_dec_token("0d0003"), is_decimal=True)
        assert w.value_count() == 2
        assert w.value == 3

    def test_decimal_single_digit(self):
        # "3" has len 1 < 4 and value 3 ≤ 0xff → 1 byte
        # NOTE: this is the root of the <<= 0d3 bug (short decimal in compound
        # assignments should respect the LHS width, not the literal's width).
        # This test documents the CURRENT behaviour, not the desired fix.
        w = Word(make_dec_token("0d3"), is_decimal=True)
        assert w.value == 3
        assert w.value_count() == 1  # known limitation — see W1 in docs/review.md

    def test_decimal_zero(self):
        w = Word(make_dec_token("0d0"), is_decimal=True)
        assert w.value == 0
        assert w.value_count() == 1

    def test_decimal_uppercase_d(self):
        w = Word(make_dec_token("0D10"), is_decimal=True)
        assert w.value == 10


# ---------------------------------------------------------------------------
# Integer construction
# ---------------------------------------------------------------------------

class TestWordInt:
    def test_from_int_value(self):
        w = Word(42)
        assert w.value == 42

    def test_from_int_default_size(self):
        w = Word(42)
        assert w.value_count() == 2

    def test_from_int_explicit_size(self):
        w = Word(42, value_count=1)
        assert w.value_count() == 1

    def test_from_word(self):
        inner = Word(make_hex_token("0x10"))
        outer = Word(inner)
        assert outer.value == 0x10

    def test_repr(self):
        t = make_hex_token("0x1234")
        w = Word(t)
        assert "Word" in repr(w)


# ---------------------------------------------------------------------------
# eval() and code()
# ---------------------------------------------------------------------------

class TestWordEval:
    def test_eval_returns_int(self):
        w = Word(make_hex_token("0x05"))
        assert w.eval([]) == 5

    def test_code_one_byte(self):
        w = Word(make_hex_token("0x0A"))
        assert w.code([]) == "0A"

    def test_code_two_byte_little_endian(self):
        w = Word(make_hex_token("0x0100"))
        assert w.code([]) == "00 01"

    def test_code_negative_wraps(self):
        # Negative 1-byte value → two's complement
        w = Word(-1, value_count=1)
        assert w.code([]) == "FF"

    def test_force_value_count(self):
        w = Word(make_hex_token("0x01"))
        w.force_value_count(2)
        assert w.value_count() == 2
        # code() should now produce a 2-byte LE output
        assert w.code([]) == "01 00"
