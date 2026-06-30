"""Root conftest.py — runs before any test module is imported.

The EverScript compiler reads sys.argv at module-import time (via
arg_utils.parse() called from OutUtils.__init__).  When pytest runs, sys.argv
contains pytest's own flags, which causes arg_utils to print help and exit.

Patching sys.argv here (before any compiler module is imported) prevents that
exit and lets tests import compiler modules freely.
"""

import sys

# Provide the one required positional argument so arg_utils.parse() succeeds.
# The value is a dummy path; tests that need real files create their own.
_DUMMY_SCRIPT = "tests/_dummy.evs"
sys.argv = [sys.argv[0], _DUMMY_SCRIPT]
