"""
Preprocessor for EverScript.

Resolves #import("path") directives BEFORE lexing (static text substitution).
Paths are resolved relative to the importing file's directory, just like
#include in C.

- File path:      paste file content as-is
- Directory path: scan entries with this sort order:
                    1. _ prefix entries first (shared/group files)
                    2. everything else alphabetically
                  Entry types:
                    - "[type] name" subdirectory → wrap contents in  type name() { ... };
                    - plain subdirectory         → wrap contents in  area name() { ... };
                    - .evs file                  → paste content as-is
                  Recurse into subdirectories.

This is fundamentally different from #include(), which re-lexes and re-parses
at the parser level (used for core.evs).
"""

import os
import re
from pathlib import Path


def preprocess(source: str, source_path: str = "") -> str:
    """
    Resolve all #import directives in source code.

    Paths inside #import() are resolved relative to source_path's directory,
    matching C #include semantics.

    Args:
        source:      The raw source text.
        source_path: Path to the source file (used to resolve relative imports).

    Returns:
        Fully expanded source with all #import directives resolved.

    Raises:
        FileNotFoundError: If a referenced path does not exist.
        ImportError:       If a circular #import is detected.
    """
    base_dir = os.path.dirname(os.path.normpath(source_path)) if source_path else "."
    # Seed the visited set with the entry-point file so that any #import of it
    # from within itself (or transitively) is caught immediately.
    initial_visited: frozenset[str] = (
        frozenset({os.path.abspath(source_path)}) if source_path else frozenset()
    )
    return _resolve_imports(source, base_dir, _visited=initial_visited)


def _resolve_imports(
    source: str,
    base_dir: str,
    _depth: int = 0,
    _visited: frozenset = frozenset(),
) -> str:
    """Recursively resolve #import directives, resolving paths relative to base_dir.

    Args:
        source:   Source text to scan for #import directives.
        base_dir: Directory used to resolve relative import paths.
        _depth:   Nesting depth (for directory wrapping decisions).
        _visited: Absolute paths of files currently on the import stack.  Used
                  for circular-import detection.  Immutable (frozenset) so that
                  sibling imports don't share state.
    """
    pattern = r'#import\(\s*"([^"]+)"\s*\)'

    def replacer(match):
        raw_path = match.group(1)
        path = os.path.normpath(os.path.join(base_dir, raw_path))

        if os.path.isdir(path):
            return _import_directory(path, _depth=_depth, _visited=_visited)
        elif os.path.isfile(path):
            return _import_file(path, _depth=_depth, _visited=_visited)
        else:
            raise FileNotFoundError(
                f"#import path not found: '{raw_path}' (resolved to '{path}')"
            )

    return re.sub(pattern, replacer, source)


def _import_file(file_path: str, _depth: int = 0, _visited: frozenset = frozenset()) -> str:
    """Import a single .evs file, recursively resolving nested #import directives.

    Raises:
        ImportError: If *file_path* is already in *_visited* (circular import).
    """
    abs_path = os.path.abspath(file_path)
    if abs_path in _visited:
        chain = " \u2192 ".join(
            os.path.relpath(p) for p in sorted(_visited)
        )
        raise ImportError(
            f"Circular #import detected: '{os.path.relpath(abs_path)}' is already "
            f"being imported.\nImport chain: {chain} \u2192 {os.path.relpath(abs_path)}"
        )
    content = Path(file_path).read_text()
    base_dir = os.path.dirname(abs_path)
    return _resolve_imports(content, base_dir, _depth=_depth, _visited=_visited | {abs_path})


def _dir_sort_key(entry: str):
    """
    Sort key for directory entries:
      1. _ prefix entries first  (shared/group code, e.g. _00_non_maps.evs)
      2. everything else: extract leading numeric prefix for stable source-order
         e.g. "[area] 04_intro_screens" → numeric 4
              "14_town_bridge.evs"      → numeric 14
              "some_file.evs"           → numeric inf (no prefix)
    """
    if entry.startswith('_'):
        return (0, entry.lower())
    # Strip "[type] " prefix from directory names, then extract leading digits
    stripped = re.sub(r'^\[\w+\]\s*', '', entry)
    m = re.match(r'^(\d+)', stripped)
    numeric = int(m.group(1)) if m else float('inf')
    return (1, numeric, entry.lower())



def _indent_text(text: str, spaces: int) -> str:
    """Add spaces to the start of each non-empty line."""
    if spaces == 0:
        return text
    indent = ' ' * spaces
    lines = text.split('\n')
    indented = [indent + line if line.strip() else '' for line in lines]
    return '\n'.join(indented)


def _import_directory(dir_path: str, _depth: int = 0, _visited: frozenset = frozenset()) -> str:
    """
    Import a directory.

    Entry sort order: _ prefix first, then everything else alphabetically.

    Entry handling:
      - "[type] name" subdirectory → ALWAYS wrap in type name() { ... };
                                      (preserves scope structure)
      - plain subdirectory         → if _depth > 0: wrap in area name() { ... };
                                     if _depth == 0: flatten (don't wrap)
      - .evs file                  → paste content as-is
      - hidden entries (leading .) → skipped
    
    _shared.evs is always imported first (if present) to ensure proper initialization.
    
    If dir_path itself has a [type] name pattern, wrap all contents in that type.
    """
    # Check if THIS directory itself is marked with [type] name
    dir_name = os.path.basename(dir_path)
    self_marked_m = re.match(r'^\[(\w+)\]\s+(.+)$', dir_name)
    
    if self_marked_m and _depth == 0:
        # This is a marked directory being directly imported
        # We need to wrap its contents
        self_type = self_marked_m.group(1)
        self_name = self_marked_m.group(2)
        self_name = re.sub(r'^\d+_', '', self_name)
        inner = _import_directory_inner(dir_path, _depth, _visited)
        return f'{self_type} {self_name}() {{\n{inner}\n}};'
    else:
        return _import_directory_inner(dir_path, _depth, _visited)


def _import_directory_inner(dir_path: str, _depth: int = 0, _visited: frozenset = frozenset()) -> str:
    """Process the actual contents of a directory."""
    parts = []
    entries = sorted(os.listdir(dir_path), key=_dir_sort_key)

    # Import _shared.evs first if it exists
    shared_path = os.path.join(dir_path, '_shared.evs')
    if os.path.isfile(shared_path):
        content = _import_file(shared_path, _depth=_depth, _visited=_visited)
        parts.append(content)

    for entry in entries:
        if entry.startswith('.') or entry == '_shared.evs':
            continue
        full_path = os.path.join(dir_path, entry)

        if os.path.isdir(full_path):
            # Parse "[type] name" pattern
            m = re.match(r'^\[(\w+)\]\s+(.+)$', entry)
            if m:
                block_type = m.group(1)   # e.g. 'area' or 'group'
                block_name = m.group(2)   # e.g. '04_shrine_area' or 'shrine_area'
                # Strip leading numeric prefix from name (e.g. '04_shrine_area' → 'shrine_area')
                block_name = re.sub(r'^\d+_', '', block_name)
                is_marked = True
            else:
                block_type = 'area'
                block_name = entry
                # Strip leading numeric prefix from name
                block_name = re.sub(r'^\d+_', '', block_name)
                is_marked = False

            inner = _import_directory(full_path, _depth=_depth + 1, _visited=_visited)

            if is_marked or _depth > 0:
                # Type-marked directories ALWAYS wrap, or nested directories wrap
                parts.append(f'{block_type} {block_name}() {{\n{inner}\n}};')
            else:
                # Plain directories at global level: just flatten
                parts.append(inner)

        elif entry.endswith('.evs'):
            content = _import_file(full_path, _depth=_depth, _visited=_visited)
            parts.append(content)

    return '\n\n'.join(parts)

