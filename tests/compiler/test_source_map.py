"""Source map (out/source_map.json): ROM address -> .evs file:line, for the VS Code debugger."""

import os

from compiler.codegen import CodeGen
from compiler.lexer import Lexer
from compiler.linker import Linker
from compiler.parser import Parser
from compiler.preprocessor import preprocess, preprocess_mapped
from compiler.source_map import annotate_tokens, split_origins, origin, strip_markers
from utils.file_utils import file_utils


def test_origins_follow_imports(tmp_path):
    (tmp_path / "part.evs").write_text("fun a() {\n    b();\n}\n")
    main = tmp_path / "main.evs"
    main.write_text('// head\n#import("part.evs")\nfun c() {\n}\n')

    text, table = preprocess_mapped(main.read_text(), str(main))

    assert text == preprocess(main.read_text(), str(main))
    lines = text.split("\n")
    by_text = {line.strip(): table[i] for i, line in enumerate(lines) if line.strip()}
    assert by_text["// head"] == (str(main), 1)
    assert by_text["fun a() {"] == (str(tmp_path / "part.evs"), 1)
    assert by_text["b();"] == (str(tmp_path / "part.evs"), 2)
    assert by_text["fun c() {"] == (str(main), 3)


def test_split_origins_strips_markers():
    text, table = split_origins(origin("/x.evs", 5) + "a\nb")
    assert text == "a\nb"
    assert table == [("/x.evs", 5), ("/x.evs", 6)]


def _compile(source, path):
    linker = Linker()
    generator = CodeGen(linker)
    pg = Parser(generator)
    pg.parse()
    parser = pg.get_parser()
    text, table = preprocess_mapped(source, path)
    parser.parse(annotate_tokens(Lexer().get_lexer().lex(text), table))
    return generator


def test_statements_map_to_lines_without_changing_bytes(tmp_path):
    path = str(tmp_path / "main.evs")
    source = (
        '#include("in/core")\n'          # 1
        "fun helper() {\n"              # 2
        "    <0x2258> = 0x01;\n"        # 3
        "}\n"                           # 4
        "@install()\n"                  # 5
        "fun main_fn() {\n"             # 6
        "    <0x2258> = 0x02;\n"        # 7
        "    if(<0x2258> == 0x02) {\n"  # 8
        "        helper();\n"           # 9
        "    }\n"                       # 10
        "}\n"                           # 11
    )
    generator = _compile(source, path)
    function = generator.current_scope().functions["main_fn"]
    code = function.code([])

    assert file_utils.clean(strip_markers(code)) == file_utils.clean(code)

    generator.source_map.add_function("main_fn", 0x300000, function.count([]), code,
                                      function.source_id, function.end_source_id)
    statements = generator.source_map.statements
    files = generator.source_map.files
    lines = [(s["line"], s["function"], [c["line"] for c in s.get("callers", [])]) for s in statements]

    assert all(files[s["file"]] == os.path.abspath(path) for s in statements)
    assert lines == [(7, "main_fn", []), (8, "main_fn", []), (3, "helper", [9]), (11, "main_fn", [])]
    assert statements[0]["address"] == 0x300000
    assert generator.source_map.functions[0]["line"] == 6


def test_memory_symbols(tmp_path):
    path = str(tmp_path / "main.evs")
    source = (
        '#include("in/core")\n'
        "enum DEBUG_MEM {\n"
        "    BYTE_VALUE = (Byte) <0x0ADA>,\n"
        "    WORD_VALUE = <0x289D>,\n"
        "    FLAG_VALUE = <0x28FA, 0x20>\n"
        "}\n"
    )
    generator = _compile(source, path)
    generator.collect_memory_symbols()
    symbols = {s["name"]: s for s in generator.source_map.symbols}

    assert symbols["DEBUG_MEM.BYTE_VALUE"] == {"name": "DEBUG_MEM.BYTE_VALUE", "address": 0x0ADA, "size": 1}
    assert symbols["DEBUG_MEM.WORD_VALUE"]["size"] == 2
    assert symbols["DEBUG_MEM.FLAG_VALUE"]["flag"] == 0x20
    assert "MEMORY.QUESTION_ANSWER" in symbols
