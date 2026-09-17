"""Tests for compiler/lexer.py — token rules and DOC_COMMENT support."""

import pytest
from compiler.lexer import Lexer


def lex(source: str) -> list[tuple[str, str]]:
    """Return a list of (token_name, token_value) pairs for *source*."""
    lexer = Lexer().get_lexer()
    return [(t.name, t.value) for t in lexer.lex(source)]


def token_names(source: str) -> list[str]:
    return [name for name, _ in lex(source)]


def token_values(source: str) -> list[str]:
    return [value for _, value in lex(source)]


# ---------------------------------------------------------------------------
# Basic literals
# ---------------------------------------------------------------------------

class TestHexLiterals:
    def test_two_byte_hex(self):
        tokens = lex("0x1234")
        assert tokens == [("WORD", "0x1234")]

    def test_one_byte_hex(self):
        tokens = lex("0x12")
        assert tokens == [("WORD", "0x12")]

    def test_six_digit_hex(self):
        tokens = lex("0x928000")
        assert tokens == [("WORD", "0x928000")]

    def test_negative_hex(self):
        tokens = lex("-0x01")
        assert tokens == [("WORD", "-0x01")]

    def test_uppercase_x(self):
        tokens = lex("0X1234")
        assert tokens == [("WORD", "0X1234")]


class TestDecimalLiterals:
    def test_decimal(self):
        tokens = lex("0d255")
        assert tokens == [("WORD_DECIMAL", "0d255")]

    def test_short_decimal(self):
        # Single digit after 0d — the NAME_IDENTIFIER fix lets f() work;
        # separately, 0d3 should still lex as a WORD_DECIMAL token.
        tokens = lex("0d3")
        assert tokens == [("WORD_DECIMAL", "0d3")]

    def test_zero_padded_decimal(self):
        tokens = lex("0d0003")
        assert tokens == [("WORD_DECIMAL", "0d0003")]

    def test_large_decimal(self):
        tokens = lex("0d256")
        assert tokens == [("WORD_DECIMAL", "0d256")]


# ---------------------------------------------------------------------------
# Keywords
# ---------------------------------------------------------------------------

class TestKeywords:
    def test_fun(self):
        assert token_names("fun foo") == ["FUN", "IDENTIFIER"]

    def test_map(self):
        assert token_names("map foo") == ["MAP", "IDENTIFIER"]

    def test_val_var(self):
        assert token_names("val x") == ["VAL", "IDENTIFIER"]
        assert token_names("var x") == ["VAR", "IDENTIFIER"]

    def test_signed(self):
        assert token_names("signed x") == ["SIGNED", "IDENTIFIER"]

    def test_true_false(self):
        assert token_names("True False") == ["TRUE", "FALSE"]

    def test_if_else(self):
        names = token_names("if(")
        assert "IF" in names

    def test_if_bang(self):
        names = token_names("if!(")
        assert "IF!" in names

    def test_while_bang(self):
        names = token_names("while!(")
        assert "WHILE!" in names


# ---------------------------------------------------------------------------
# Operators
# ---------------------------------------------------------------------------

class TestOperators:
    def test_compound_shift_left(self):
        assert token_names("<<=") == ["<<="]

    def test_compound_shift_right(self):
        assert token_names(">>=") == [">>="]

    def test_shift_left(self):
        assert token_names("<<") == ["<<"]

    def test_shift_right(self):
        assert token_names(">>") == [">>"]

    def test_less_than_not_confused_with_shift(self):
        # "<" alone must be LT, not part of "<<"
        assert token_names("< 0x01") == ["<", "WORD"]

    def test_greater_than_not_confused_with_shift(self):
        assert token_names("> 0x01") == [">", "WORD"]

    def test_equals(self):
        assert token_names("==") == ["=="]

    def test_not_equals(self):
        assert token_names("!=") == ["!="]

    def test_b_and(self):
        # & not followed by & or =
        assert token_names("&") == ["B_AND"]

    def test_b_or(self):
        assert token_names("|") == ["B_OR"]

    def test_b_xor(self):
        assert token_names("^") == ["B_XOR"]

    def test_and_or_keywords(self):
        assert token_names("&&") == ["AND"]
        assert token_names("||") == ["OR"]

    def test_increment_decrement(self):
        assert token_names("++") == ["++"]
        assert token_names("--") == ["--"]

    def test_compound_add(self):
        assert token_names("+=") == ["+="]

    def test_compound_or(self):
        assert token_names("|=") == ["OR="]


# ---------------------------------------------------------------------------
# Identifiers
# ---------------------------------------------------------------------------

class TestIdentifiers:
    def test_plain_identifier(self):
        tokens = lex("SOME_CONST")
        assert tokens == [("IDENTIFIER", "SOME_CONST")]

    def test_enum_call(self):
        tokens = lex("ITEM.SWORD")
        assert tokens == [("ENUM_CALL", "ITEM.SWORD")]

    def test_name_identifier_multi_char(self):
        # multi-char lowercase name followed by ( → NAME_IDENTIFIER
        # Lookahead (?=\() does not consume the (, so it appears as a separate token.
        names = token_names("foo(")
        assert names == ["NAME_IDENTIFIER", "("]

    def test_name_identifier_single_char(self):
        # single-char function name — the NAME_IDENTIFIER regex fix allows this
        names = token_names("f(")
        assert names == ["NAME_IDENTIFIER", "("]

    def test_name_identifier_underscore_prefix(self):
        names = token_names("_foo(")
        assert names == ["NAME_IDENTIFIER", "("]


# ---------------------------------------------------------------------------
# Strings
# ---------------------------------------------------------------------------

class TestStrings:
    def test_double_quoted_string(self):
        tokens = lex('"hello world"')
        assert tokens == [("STRING", '"hello world"')]

    def test_single_quoted_string(self):
        tokens = lex("'raw string'")
        assert tokens == [("STRING_RAW", "'raw string'")]


# ---------------------------------------------------------------------------
# Comments
# ---------------------------------------------------------------------------

class TestComments:
    def test_line_comment_ignored(self):
        # // comments should produce no tokens
        assert lex("// this is a comment\n") == []

    def test_line_comment_does_not_eat_next_line(self):
        tokens = lex("// comment\n0x01")
        assert tokens == [("WORD", "0x01")]

    def test_doc_comment_is_a_token(self):
        # /// doc comments must produce DOC_COMMENT tokens, not be ignored
        tokens = lex("/// hello world")
        assert len(tokens) == 1
        assert tokens[0][0] == "DOC_COMMENT"
        assert "hello world" in tokens[0][1]

    def test_doc_comment_value(self):
        tokens = lex("/// @param x  the x position")
        assert tokens[0][0] == "DOC_COMMENT"
        assert "@param x" in tokens[0][1]

    def test_doc_comment_followed_by_code(self):
        tokens = lex("/// doc\n0x01")
        assert tokens[0][0] == "DOC_COMMENT"
        assert tokens[1] == ("WORD", "0x01")

    def test_doc_comment_not_confused_with_line_comment(self):
        tokens = lex("// not doc\n/// yes doc")
        names = [t[0] for t in tokens]
        assert names == ["DOC_COMMENT"]

    def test_multiple_doc_comments(self):
        tokens = lex("/// line 1\n/// line 2\n")
        assert [t[0] for t in tokens] == ["DOC_COMMENT", "DOC_COMMENT"]


# ---------------------------------------------------------------------------
# Special constructs
# ---------------------------------------------------------------------------

class TestSpecialConstructs:
    def test_label_destination(self):
        tokens = lex("MY_LABEL:")
        # LABEL_DESTINATION matches [A-Z][A-Z_]*:
        assert tokens[0][0] == "LABEL_DESTINATION"

    def test_fun_include(self):
        # Lookahead (?=\() does not consume ( — it appears as a separate token.
        names = token_names('#include(')
        assert names == ["FUN_INCLUDE", "("]

    def test_fun_memory(self):
        names = token_names('#memory(')
        assert names == ["FUN_MEMORY", "("]

    def test_fun_patch(self):
        # Only one FUN_PATCH rule (duplicate was removed)
        names = token_names('#patch(')
        assert names == ["FUN_PATCH", "("]

    def test_memory_open(self):
        names = token_names('memory(')
        assert names == ["MEMORY", "("]

    def test_object_bracket(self):
        names = token_names('object[')
        assert names == ["OBJECT", "["]

    def test_range_operator(self):
        names = token_names('0x00..0xff')
        assert names == ["WORD", "..", "WORD"]

    def test_annotation_at(self):
        names = token_names('@install(')
        assert names[0] == "@"

    def test_enum_keyword(self):
        # enum not followed by ( is ENUM keyword
        tokens = lex("enum FOO")
        assert tokens[0][0] == "ENUM"
