"""Parser smoke tests — minimal self-contained snippets parsed through the
full lex → parse pipeline.

These tests do NOT require core.evs or a ROM.  They test language constructs
that can be expressed without referencing external enums or identifiers.

The pipeline (Lexer + Linker + CodeGen + Parser) is shared across all tests
in this module via a module-level fixture to keep test setup cheap.
"""

import pytest

from compiler.lexer import Lexer
from compiler.linker import Linker
from compiler.codegen import CodeGen
from compiler.parser import Parser
from compiler.ast_everscript import (
    Function, Annotation_Install, Annotation_Weak, Annotation_Inject,
    Annotation_Doc,
)
from compiler.ast_core import Word


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _build_pipeline():
    """Return a fresh (lexer, parser, generator) triple."""
    linker = Linker()
    generator = CodeGen(linker)
    pg = Parser(generator)
    pg.parse()
    parser = pg.get_parser()
    lexer = Lexer().get_lexer()
    return lexer, parser, generator


def parse_snippet(source: str):
    """Parse *source* and return the generator for inspection."""
    lexer, parser, generator = _build_pipeline()
    parser.parse(lexer.lex(source))
    return generator


# ---------------------------------------------------------------------------
# Basic function declarations
# ---------------------------------------------------------------------------

class TestFunctionDeclaration:
    def test_empty_function_added(self):
        # Grammar requires at least one expression in the body.
        gen = parse_snippet("fun foo() { 0x01; }")
        funcs = [f for f in gen.code if isinstance(f, Function) and f.name == "foo"]
        assert len(funcs) == 1

    def test_single_char_function_name(self):
        # f() must be a valid function name after the NAME_IDENTIFIER fix.
        gen = parse_snippet("fun f() { 0x01; }")
        funcs = [f for f in gen.code if isinstance(f, Function) and f.name == "f"]
        assert len(funcs) == 1

    def test_function_with_args(self):
        gen = parse_snippet("fun move(x, y) { 0x01; }")
        funcs = [f for f in gen.code if isinstance(f, Function) and f.name == "move"]
        assert len(funcs) == 1
        assert len(funcs[0].args) == 2

    def test_function_arg_names(self):
        gen = parse_snippet("fun pos(x, y) { 0x01; }")
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "pos")
        arg_names = [a.name.value if hasattr(a.name, 'value') else a.name for a in func.args]
        assert "x" in arg_names
        assert "y" in arg_names

    def test_multiple_functions(self):
        gen = parse_snippet("fun a() { 0x01; } fun b() { 0x02; }")
        names = [f.name for f in gen.code if isinstance(f, Function)]
        assert "a" in names
        assert "b" in names


# ---------------------------------------------------------------------------
# Annotations
# ---------------------------------------------------------------------------

class TestAnnotations:
    def test_install_annotation(self):
        gen = parse_snippet("@install()\nfun entry() { 0x01; }")
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "entry")
        assert func.install is True

    def test_weak_annotation(self):
        gen = parse_snippet("@weak()\nfun optional() { 0x01; }")
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "optional")
        assert func.weak is True

    def test_async_annotation(self):
        gen = parse_snippet("@async()\nfun bg() { 0x01; }")
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "bg")
        assert func.async_call is True

    def test_stacked_annotations(self):
        gen = parse_snippet("@install()\n@weak()\nfun maybe() { 0x01; }")
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "maybe")
        assert func.install is True
        assert func.weak is True


# ---------------------------------------------------------------------------
# Doc comments attached to functions
# ---------------------------------------------------------------------------

class TestDocComments:
    def test_single_doc_comment(self):
        gen = parse_snippet("/// Does something useful\nfun documented() { 0x01; }")
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "documented")
        assert func.doc is not None
        assert len(func.doc) == 1
        assert "Does something useful" in func.doc[0]

    def test_doc_comment_stripped_of_slashes(self):
        gen = parse_snippet("/// @param x  the x coord\nfun move(x) { 0x01; }")
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "move")
        assert func.doc[0].startswith("@param")

    def test_multiple_doc_lines(self):
        src = "/// Line 1\n/// Line 2\n/// Line 3\nfun multi() { 0x01; }"
        gen = parse_snippet(src)
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "multi")
        assert len(func.doc) == 3

    def test_function_without_doc_has_none(self):
        gen = parse_snippet("fun plain() { 0x01; }")
        func = next(f for f in gen.code if isinstance(f, Function) and f.name == "plain")
        assert func.doc is None

    def test_doc_comment_with_annotation(self):
        src = "/// Doc\n@install()\nfun annotated() { 0x01; }"
        gen = parse_snippet(src)
        func = next(
            f for f in gen.code if isinstance(f, Function) and f.name == "annotated"
        )
        assert func.install is True
        assert func.doc is not None
        assert "Doc" in func.doc[0]

    def test_line_comment_does_not_attach_as_doc(self):
        # Plain // comments are ignored — must NOT appear on Function.doc
        gen = parse_snippet("// not a doc comment\nfun undocumented() { 0x01; }")
        func = next(
            f for f in gen.code if isinstance(f, Function) and f.name == "undocumented"
        )
        assert func.doc is None


# ---------------------------------------------------------------------------
# Literals and expressions
# ---------------------------------------------------------------------------

class TestLiterals:
    def test_word_literal_parsed(self):
        parse_snippet("fun f() { val x = 0x01; }")

    def test_decimal_literal_parsed(self):
        parse_snippet("fun f() { val x = 0d10; }")

    def test_true_false_literals(self):
        parse_snippet("fun f() { val t = True; val ff = False; }")

    def test_string_literal(self):
        parse_snippet('fun f() { val s = "hello"; }')


# ---------------------------------------------------------------------------
# Control flow
# ---------------------------------------------------------------------------

class TestControlFlow:
    def test_if_statement(self):
        parse_snippet("fun f() { if(True) { 0x01; } }")

    def test_if_else(self):
        parse_snippet("fun f() { if(True) { 0x01; } else { 0x02; } }")

    def test_if_bang(self):
        parse_snippet("fun f() { if!(True) { 0x01; } }")

    def test_while(self):
        parse_snippet("fun f() { while(True) { 0x01; } }")

    def test_while_bang(self):
        parse_snippet("fun f() { while!(True) { 0x01; } }")


# ---------------------------------------------------------------------------
# Enum declarations
# ---------------------------------------------------------------------------

class TestEnums:
    def test_simple_enum(self):
        gen = parse_snippet("enum COLOR { RED = 0x00, GREEN = 0x01, BLUE = 0x02 }")
        enum = gen.get_identifier("COLOR")
        assert enum is not None

    def test_enum_entry_count(self):
        gen = parse_snippet("enum SIZE { SMALL = 0x00, LARGE = 0x01 }")
        enum = gen.get_identifier("SIZE")
        assert len(enum.values) == 2

    def test_enum_entry_values(self):
        gen = parse_snippet("enum SIZE { SMALL = 0x00, LARGE = 0x01 }")
        enum = gen.get_identifier("SIZE")
        assert enum.values[0].name == "SMALL"
        assert enum.values[1].name == "LARGE"


# ---------------------------------------------------------------------------
# Group blocks
# ---------------------------------------------------------------------------

class TestGroups:
    def test_group_contents_registered(self):
        gen = parse_snippet("group utils() { fun helper() { 0x01; } };")
        names = [f.name for f in gen.code if isinstance(f, Function)]
        assert "helper" in names


# ---------------------------------------------------------------------------
# Parser error recovery
# ---------------------------------------------------------------------------

class TestParserErrors:
    def test_syntax_error_raises(self):
        with pytest.raises(Exception):
            parse_snippet("fun { }")  # missing name and args

    def test_invalid_annotation_raises(self):
        with pytest.raises(Exception):
            parse_snippet("@unknown_annotation()\nfun f() { }")
