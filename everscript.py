"""EverScript compiler entry point.

Orchestrates the full compilation pipeline::

    preprocess → lex → parse → codegen → IPS patch

Usage (see ``--help`` for full options)::

    python everscript.py [--rom <rom_file>] [--profile] <input.evs>

The ``--profile`` flag wraps the pipeline with :mod:`cProfile` and writes a
``profile.txt`` report to the output directory alongside the normal artefacts.
"""

import os
import re
import time
import cProfile
import pstats
import io

from utils.out_utils import *
from compiler.lexer import Lexer
from compiler.codegen import CodeGen
from compiler.parser import Parser
from compiler.linker import Linker
from compiler.preprocessor import preprocess

# Shared pipeline objects, initialised once inside main() before any compilation.
lexer = None
linker = None
generator = None
parser = None

def handle_parse(code: str, verbose: bool):
    """Run the lex → parse → codegen pipeline on preprocessed EverScript source.

    Args:
        code:    Fully preprocessed EverScript source text.
        verbose: When ``True`` each progress line includes elapsed wall-clock
                 time in seconds.

    Returns:
        A ``ParserOut`` instance with:

        - ``.everscript`` – path to the generated ``.ips`` file in ``out/``.
        - ``.patches``    – list of additional patch descriptors from the
          generator (forwarded to :func:`out_utils.prepare_patches`).
    """
    class ParserOut:
        everscript = None
        patches = None

    parser_out = ParserOut()
    start = time.time()

    def log(text: str) -> None:
        """Print *text*, appending elapsed time when *verbose* is ``True``."""
        if verbose:
            print(f"{text} ({time.time() - start:.1f}s)")
        else:
            print(text)

    log("lexing code…")
    out_utils.dump(re.sub(r"\),", r"\),\n", f"{list(lexer.lex(code))}"), "lexer.txt")

    lexed = lexer.lex(code)
    log("generating objects…")
    parser.parse(lexed)

    log("creating patch artifact…")
    generated = generator.generate()
    parser_out.patches = generator.patches
    generated = string_utils.beautify_output(generated)
    out_utils.dump(generated, "patch.txt")
    out_utils.dump(generator.get_memory_allocation(), "memory_map.txt")

    generated_clean = file_utils.clean(generated)
    out_utils.dump(generated_clean, "patch.clean.txt")

    parser_out.everscript = out_utils.dump(generated_clean, "everscript.ips")

    log("done!")
    return parser_out

def main() -> None:
    """CLI entry point.

    1. Initialises the shared compilation pipeline (lexer, linker, codegen,
       parser).
    2. Preprocesses the input ``.evs`` file (resolves ``#import`` directives).
    3. Runs the lex → parse → codegen pass, optionally under :mod:`cProfile`.
    4. If ``--rom`` is supplied, applies the resulting ``.ips`` patch and any
       extra assembler patches to the ROM.
    """
    global lexer, linker, generator, parser

    # Build the pipeline once before parsing arguments so any construction
    # errors surface immediately.
    linker = Linker()
    generator = CodeGen(linker)
    pg = Parser(generator)
    pg.parse()
    parser = pg.get_parser()
    lexer = Lexer().get_lexer()

    args = arg_utils.parse()

    # If input is a directory, resolve to main.evs inside it.
    if os.path.isdir(args.input_file):
        args.input_file = os.path.join(args.input_file, "main.evs")

    code = file_utils.file2string(args.input_file)

    # Preprocess: resolve #import directives (static text substitution).
    code = preprocess(code, args.input_file)

    out_utils.init_out()

    # Dump fully expanded source for debugging.
    out_utils.dump(code, "preprocessed.evs")

    if args.profile:
        profiler = cProfile.Profile()
        profiler.enable()
        parser_out = handle_parse(code, verbose=True)
        profiler.disable()

        result = io.StringIO()
        pstats.Stats(profiler, stream=result).sort_stats("tottime").print_stats()
        result = result.getvalue()

        with open(f"{args.output_dir}/profile.txt", "w") as f:
            print(result, file=f)
        print(result)
    else:
        parser_out = handle_parse(code, verbose=True)

    if args.rom_file is not None:
        print("preparing rom:")
        out_utils.prepare_rom(args.rom_file)
        print("preparing patches:")
        out_utils.prepare_patches(args.rom_file, args.patches_dir, parser_out.patches)

        print("evermizer patch:")
        out_utils.patch(args.rom_file, parser_out.everscript)

    print("done!")


if __name__ == "__main__":
    main()