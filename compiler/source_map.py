"""Source map: which .evs file:line each script instruction in the ROM came from.

Written to ``out/source_map.json`` for the VS Code debugger, which pauses the
emulator on the script interpreter and needs ROM address <-> source line.

How positions travel through the pipeline:

1. The preprocessor flattens ``#import`` into one text. It wraps every imported
   piece in zero-width origin markers; ``split_origins`` strips them and returns
   a table: line of the flattened text -> (file, line) it came from.
2. ``annotate_tokens`` gives every token ``stmt_src``: the origin of the first
   token of its statement (the token after the last ``;``, ``{`` or ``}``).
   Parser productions copy it onto statement nodes as ``source_id``.
3. ``Function_Code`` writes a ``//@src:<id>`` comment line before each tagged
   statement, and a ``Call`` in statement position starts an inlined function
   body with ``//@in:<byte count>:<name>``. A marker is always followed by a
   newline, never by bytes on its own line, and comments never reach the IPS
   (``//.*`` is stripped before counting and writing): the bytes are unchanged.
4. ``SourceMap.add_function`` walks a function's final code text, counting
   bytes, and records the ROM offset each marker lands on. ``strip_markers``
   then removes them so ``patch.txt`` stays as it was.
"""

import json
import os
import re

ORIGIN_OPEN = ""
ORIGIN_CLOSE = ""
_RE_ORIGIN = re.compile(ORIGIN_OPEN + r"(\d+)\|([^" + ORIGIN_CLOSE + r"]*)" + ORIGIN_CLOSE)

SRC_MARKER = "//@src:"
INLINE_MARKER = "//@in:"
_RE_MARKER_LINE = re.compile(r"^[ \t]*//@(?:src:\d+|in:\d+:[^\n]*)[ \t]*(?:\n|$)", re.M)
_RE_COMMENT = re.compile(r"//.*")

STATEMENT_BOUNDARIES = (";", "{", "}")


def origin(file: str | None, line: int) -> str:
    """Zero-width marker: the text after it is `file` from `line` on (None = generated text)."""
    return f"{ORIGIN_OPEN}{line}|{os.path.abspath(file) if file else ''}{ORIGIN_CLOSE}"


def split_origins(text: str) -> tuple[str, list[tuple[str | None, int]]]:
    """Strip origin markers. Returns the clean text and, per line of it, (file, line).

    A line that switches file part-way is attributed to whatever its first
    non-blank character belongs to.
    """
    out_lines = []
    table = []
    cur_file, cur_line = None, 0
    for raw in text.split("\n"):
        attributed = None
        parts = []
        pos = 0
        for m in _RE_ORIGIN.finditer(raw):
            segment = raw[pos:m.start()]
            if attributed is None and segment.strip():
                attributed = (cur_file, cur_line)
            parts.append(segment)
            cur_line = int(m.group(1))
            cur_file = m.group(2) or None
            pos = m.end()
        segment = raw[pos:]
        if attributed is None and segment.strip():
            attributed = (cur_file, cur_line)
        parts.append(segment)
        table.append(attributed or (cur_file, cur_line))
        out_lines.append("".join(parts))
        cur_line += 1
    return "\n".join(out_lines), table


def annotate_tokens(tokens, table):
    """Yield `tokens` with `src` (own origin) and `stmt_src` (its statement's first token)."""
    def lookup(token):
        pos = getattr(token, "source_pos", None)
        if pos is None or not table or not (1 <= pos.lineno <= len(table)):
            return None
        file, line = table[pos.lineno - 1]
        return (file, line) if file else None

    start = None
    for token in tokens:
        token.src = lookup(token)
        if start is None:
            start = token.src
        token.stmt_src = start
        yield token
        if token.gettokentype() in STATEMENT_BOUNDARIES:
            start = None


def strip_markers(code: str) -> str:
    return _RE_MARKER_LINE.sub("", code)


class SourceMap:
    """Collects source positions while parsing and ROM addresses while generating."""

    def __init__(self):
        self.files: list[str] = []
        self._file_index: dict[str, int] = {}
        self.entries: list[tuple[int, int]] = []   # source_id -> (file index, line)
        self._entry_index: dict[tuple[int, int], int] = {}
        self.functions: list[dict] = []
        self.statements: list[dict] = []
        self.symbols: list[dict] = []

    def register(self, src) -> int | None:
        """source_id for a (file, line) origin, or None for generated code."""
        if not src or not src[0]:
            return None
        file, line = src
        file_index = self._file_index.get(file)
        if file_index is None:
            file_index = self._file_index[file] = len(self.files)
            self.files.append(file)
        key = (file_index, line)
        source_id = self._entry_index.get(key)
        if source_id is None:
            source_id = self._entry_index[key] = len(self.entries)
            self.entries.append(key)
        return source_id

    def add_function(self, name: str, rom_offset: int, size: int, code: str, source_id=None, end_source_id=None) -> None:
        """Record where each statement of a generated function landed in the ROM."""
        function = {"name": name, "address": rom_offset, "size": size}
        if source_id is not None:
            function["file"], function["line"] = self.entries[source_id]
        if end_source_id is not None:
            function["endLine"] = self.entries[end_source_id][1]
        self.functions.append(function)

        # frames[0] is the function itself; each inlined body pushes one.
        # A frame is [function name, source_id of its current statement, end offset].
        frames = [[name, None, None]]
        offset = 0
        pending = False
        for line in code.split("\n"):
            while len(frames) > 1 and offset >= frames[-1][2]:
                frames.pop()
                pending = True  # bytes after an inlined body belong to the caller's statement
            text = line.strip()
            if text.startswith(SRC_MARKER):
                frames[-1][1] = int(text[len(SRC_MARKER):])
                pending = True
                continue
            if text.startswith(INLINE_MARKER):
                size, _, inline_name = text[len(INLINE_MARKER):].partition(":")
                frames.append([inline_name, None, offset + int(size)])
                continue
            count = len(_RE_COMMENT.sub("", line).split())
            if not count:
                continue
            if pending and frames[-1][1] is not None:
                self._add_statement(rom_offset + offset, frames)
            pending = False
            offset += count

    def _add_statement(self, address: int, frames) -> None:
        file, line = self.entries[frames[-1][1]]
        statement = {"address": address, "file": file, "line": line, "function": frames[-1][0]}
        # Inlined bodies: the call sites that expanded them, innermost first.
        callers = []
        for caller_index in range(len(frames) - 2, -1, -1):
            caller_name, caller_source = frames[caller_index][:2]
            if caller_source is None:
                continue
            caller_file, caller_line = self.entries[caller_source]
            callers.append({"function": caller_name, "file": caller_file, "line": caller_line})
        if callers:
            statement["callers"] = callers
        # Two markers on one address (a statement whose first child is a statement): keep the innermost.
        if self.statements and self.statements[-1]["address"] == address:
            self.statements[-1] = statement
        else:
            self.statements.append(statement)

    def add_symbol(self, name: str, address: int, size: int, flag=None, offset=None) -> None:
        """A named memory location (ENUM.ENTRY = <0x...>): WRAM offset in bank $7E, 1 or 2 bytes, flag bit mask."""
        symbol = {"name": name, "address": address, "size": size}
        if flag is not None:
            symbol["flag"] = flag
        if offset is not None:
            symbol["offset"] = offset
        self.symbols.append(symbol)

    def to_json(self) -> str:
        return json.dumps({
            "version": 1,
            "addressing": "rom offset (SNES address & 0x3FFFFF)",
            "files": self.files,
            "functions": sorted(self.functions, key=lambda f: f["address"]),
            "statements": sorted(self.statements, key=lambda s: s["address"]),
            "symbols": sorted(self.symbols, key=lambda s: s["name"]),
        }, indent=1)
