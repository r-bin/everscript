"""Tests for compiler/preprocessor.py.

Covers #import resolution, nested imports, directory wrapping, and
circular-import detection.
"""

import os
import textwrap
import pytest
from pathlib import Path

from compiler.preprocessor import preprocess, _resolve_imports, _dir_sort_key


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def write(tmp_path: Path, rel: str, content: str) -> Path:
    """Write *content* to *tmp_path / rel*, creating parent dirs as needed."""
    p = tmp_path / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content))
    return p


# ---------------------------------------------------------------------------
# Basic #import resolution
# ---------------------------------------------------------------------------

class TestBasicImport:
    def test_import_file(self, tmp_path):
        write(tmp_path, "b.evs", "val x = 0x01;")
        main = write(tmp_path, "main.evs", '#import("b.evs")')
        result = preprocess(main.read_text(), str(main))
        assert "val x = 0x01;" in result

    def test_import_replaces_directive(self, tmp_path):
        write(tmp_path, "b.evs", "CONTENT")
        main = write(tmp_path, "main.evs", 'before\n#import("b.evs")\nafter')
        result = preprocess(main.read_text(), str(main))
        assert result.index("CONTENT") > result.index("before")
        assert result.index("after") > result.index("CONTENT")

    def test_import_missing_file_raises(self, tmp_path):
        main = write(tmp_path, "main.evs", '#import("does_not_exist.evs")')
        with pytest.raises(FileNotFoundError, match="does_not_exist"):
            preprocess(main.read_text(), str(main))

    def test_no_directives_unchanged(self, tmp_path):
        src = "fun foo() { }"
        main = write(tmp_path, "main.evs", src)
        result = preprocess(main.read_text(), str(main))
        assert result == src


# ---------------------------------------------------------------------------
# Nested #import (A imports B imports C)
# ---------------------------------------------------------------------------

class TestNestedImport:
    def test_nested_import(self, tmp_path):
        write(tmp_path, "c.evs", "val c = 0x03;")
        write(tmp_path, "b.evs", '#import("c.evs")\nval b = 0x02;')
        main = write(tmp_path, "main.evs", '#import("b.evs")')
        result = preprocess(main.read_text(), str(main))
        assert "val c = 0x03;" in result
        assert "val b = 0x02;" in result

    def test_nested_import_relative_paths(self, tmp_path):
        (tmp_path / "sub").mkdir()
        write(tmp_path, "sub/leaf.evs", "val leaf = 0x01;")
        write(tmp_path, "sub/mid.evs", '#import("leaf.evs")')
        main = write(tmp_path, "main.evs", '#import("sub/mid.evs")')
        result = preprocess(main.read_text(), str(main))
        assert "val leaf = 0x01;" in result


# ---------------------------------------------------------------------------
# Directory import
# ---------------------------------------------------------------------------

class TestDirectoryImport:
    def test_import_directory_pastes_evs_files(self, tmp_path):
        (tmp_path / "lib").mkdir()
        write(tmp_path, "lib/a.evs", "val a = 0x01;")
        main = write(tmp_path, "main.evs", '#import("lib")')
        result = preprocess(main.read_text(), str(main))
        assert "val a = 0x01;" in result

    def test_import_directory_multiple_files_in_order(self, tmp_path):
        (tmp_path / "lib").mkdir()
        write(tmp_path, "lib/01_first.evs", "// first")
        write(tmp_path, "lib/02_second.evs", "// second")
        main = write(tmp_path, "main.evs", '#import("lib")')
        result = preprocess(main.read_text(), str(main))
        assert result.index("first") < result.index("second")

    def test_import_directory_underscore_first(self, tmp_path):
        (tmp_path / "lib").mkdir()
        write(tmp_path, "lib/_shared.evs", "// shared_first")
        write(tmp_path, "lib/01_a.evs", "// regular")
        main = write(tmp_path, "main.evs", '#import("lib")')
        result = preprocess(main.read_text(), str(main))
        assert result.index("shared_first") < result.index("regular")

    def test_import_typed_subdirectory_wraps(self, tmp_path):
        sub = tmp_path / "[group] mygroup"
        sub.mkdir()
        write(tmp_path, "[group] mygroup/thing.evs", "fun thing() { }")
        main = write(tmp_path, "main.evs", '#import("[group] mygroup")')
        result = preprocess(main.read_text(), str(main))
        assert "group mygroup()" in result


# ---------------------------------------------------------------------------
# Circular import detection
# ---------------------------------------------------------------------------

class TestCircularImport:
    def test_self_import_raises(self, tmp_path):
        main = write(tmp_path, "main.evs", '#import("main.evs")')
        with pytest.raises(ImportError, match="[Cc]ircular"):
            preprocess(main.read_text(), str(main))

    def test_two_file_cycle_raises(self, tmp_path):
        write(tmp_path, "b.evs", '#import("a.evs")')
        main = write(tmp_path, "a.evs", '#import("b.evs")')
        with pytest.raises(ImportError, match="[Cc]ircular"):
            preprocess(main.read_text(), str(main))

    def test_three_file_cycle_raises(self, tmp_path):
        write(tmp_path, "c.evs", '#import("a.evs")')
        write(tmp_path, "b.evs", '#import("c.evs")')
        main = write(tmp_path, "a.evs", '#import("b.evs")')
        with pytest.raises(ImportError, match="[Cc]ircular"):
            preprocess(main.read_text(), str(main))

    def test_diamond_import_no_cycle(self, tmp_path):
        """A→B, A→C, B→D, C→D is NOT a cycle — D is imported twice."""
        write(tmp_path, "d.evs", "val d = 0x04;")
        write(tmp_path, "b.evs", '#import("d.evs")')
        write(tmp_path, "c.evs", '#import("d.evs")')
        main = write(tmp_path, "a.evs", '#import("b.evs")\n#import("c.evs")')
        # Diamond imports are allowed (d.evs pasted twice) — no ImportError
        result = preprocess(main.read_text(), str(main))
        assert result.count("val d = 0x04;") == 2


# ---------------------------------------------------------------------------
# _dir_sort_key
# ---------------------------------------------------------------------------

class TestDirSortKey:
    def test_underscore_prefix_sorts_first(self):
        entries = ["01_a.evs", "_shared.evs", "02_b.evs"]
        assert sorted(entries, key=_dir_sort_key)[0] == "_shared.evs"

    def test_numeric_prefix_ordering(self):
        entries = ["10_z.evs", "02_a.evs", "01_b.evs"]
        sorted_entries = sorted(entries, key=_dir_sort_key)
        assert sorted_entries == ["01_b.evs", "02_a.evs", "10_z.evs"]

    def test_no_prefix_sorts_last(self):
        entries = ["01_a.evs", "no_prefix.evs"]
        sorted_entries = sorted(entries, key=_dir_sort_key)
        assert sorted_entries == ["01_a.evs", "no_prefix.evs"]

    def test_typed_dir_strips_bracket_prefix(self):
        # "[area] 04_shrine" should sort at numeric position 4
        entries = ["[area] 04_shrine", "03_other.evs"]
        sorted_entries = sorted(entries, key=_dir_sort_key)
        assert sorted_entries[0] == "03_other.evs"
