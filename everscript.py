from utils.utils import *

from compiler.lexer import Lexer
from compiler.codegen import CodeGen
from compiler.parser import Parser
from compiler.linker import Linker

import time
import re
import sys, getopt
import os

lexer = Lexer().get_lexer()
linker = Linker()
generator = CodeGen(linker)
pg = Parser(generator)
pg.parse()
parser = pg.get_parser()

def handle_parse(outUtils, rom_file, patches_dir, code, profile):
    def log(text):
        if profile:
            print(f"{text} ({'{:.1f}'.format(time.time() - start)}s)")
        else:
            print(text)

    start = time.time()
    
    log(f"lexing code...")
    outUtils.dump(re.sub("\),", "\),\n", f"{list(lexer.lex(code))}"), "lexer.txt")

    lexed = lexer.lex(code)
    log(f"generating objects...")
    parsed = parser.parse(lexed)

    log(f"creating artifacts...")
    generated = generator.generate()
    generated = stringUtils.beautify_output(generated)
    outUtils.dump(generated, "patch.txt")
    outUtils.dump(generator.get_memory_allocation(), "memory_map.txt")

    generated_clean = outUtils.clean(generated)
    outUtils.dump(generated_clean, "patch.clean.txt")

    outUtils.file(generated_clean, "everscript.ips")
    outUtils.prepare_rom(rom_file)
    outUtils.prepare_patches(rom_file, patches_dir, generator.patches)
    
    log(f"done!")

def parse_args(argv):
    outUtils = OutUtils()
    outUtils.init_out()

    args = outUtils.parse_args()

    code = fileUtils.file2string(args.input_file)

    if not args.profile:
        handle_parse(outUtils, args.rom_file, args.patches_dir, code, True)
    else:
        import cProfile, pstats
        import io

        profiler = cProfile.Profile()
        profiler.enable()
        handle_parse(outUtils, args.rom_file, args.patches_dir, code, args.profile)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('tottime')
        
        result = io.StringIO()
        pstats.Stats(profiler, stream=result).sort_stats('tottime').print_stats()
        result = result.getvalue()
        
        with open(f"{args.output_dir}/profile.txt", "w+") as f:
            print(result, file=f)
        print(result)

    if(args.rom_file != None):
        outUtils.patch(args.rom_file, "everscript.ips")

parse_args(sys.argv)