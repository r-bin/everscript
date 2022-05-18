from utils.utils import *

from compiler.lexer import Lexer
from compiler.codegen import CodeGen
from compiler.parser import Parser
from compiler.linker import Linker

import time
import re
import sys, getopt

version = "1.0.0"

outUtils.clean_out()

lexer = Lexer().get_lexer()
linker = Linker()
generator = CodeGen(linker)
pg = Parser(generator)
pg.parse()
parser = pg.get_parser()

def handle_parse(code, profile):
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

    generated_clean = generator.clean(generated)
    outUtils.dump(generated_clean, "patch.clean.txt")

    generator.file(generated_clean, "out/everscript.ips")
    
    log(f"done!")

def parse_args(argv):
    name = argv[0]
    argv = argv[1:]

    example_rom_file = '"Secret of Evermore (U) [!].smc"'
    example_input_file = "<input_file.evs>"
    example_patches_dir = "</additional_patches>"

    rom_file = None
    input_file = None
    patches_dir = None
    profile = False

    def help():
        print(f"""
Compiles '.evs' code into everscript assembler and patches it into Secret of Evermore ROMs.
Based on the code and results of https://github.com/black-sliver/SoETilesViewer from Black Sliver.

-r, --rom
    Secret of Evermore ROM: English, good dump '[!]', no header ({example_rom_file})
-s, --script, #1
    Contains the code to be compiled into an IPS file and patched into the ROM.
-p, --patches
    Additional patches to be applied.
--profile
    Measures the performance of the compiler. Useful for finding problems.
-v, --version
    Current version ({name} - {version})

examples:
    {name} --rom {example_rom_file} {example_input_file}                                                rom + script
    {name} --rom {example_rom_file} --script {example_input_file}                                       rom + script
    {name} --rom {example_rom_file} --script {example_input_file} --patches {example_patches_dir}       rom + script + patches
    {name} --rom {example_rom_file} --script {example_input_file} --profile                             profile(rom + script)
        """.strip())
        sys.exit()

    try:
        opts, args = getopt.getopt(argv,"hpr:s:",["profile", "rom=", "script=", "patches="])
    except getopt.GetoptError:
        help()

    if len(args) == 1:
        input_file = args[0]
    else:
        help()

    for opt, arg in opts:
        if opt == "-h":
            help()
        elif opt in ("-v", "--version"):
            print(version)
            sys.exit()
        elif opt in ("-p", "--profile"):
            profile = True
        elif opt in ("-r", "--rom"):
            rom_file = arg
        elif opt in ("-s", "--script"):
            input_file = arg
        elif opt in ("-p", "--patches"):
            patches_dir = arg

    if not input_file:
        help()

    code = fileUtils.file2string(input_file)

    if not profile:
        handle_parse(code, True)
    else:
        import cProfile, pstats
        import io

        profiler = cProfile.Profile()
        profiler.enable()
        handle_parse(code, profile)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('tottime')
        
        result = io.StringIO()
        pstats.Stats(profiler, stream=result).sort_stats('tottime').print_stats()
        result = result.getvalue()
        
        with open("out/profile.txt", "w+") as f:
            print(result, file=f)
        print(result)

    outUtils.patch(rom_file, "out/everscript.ips", patches_dir)

parse_args(sys.argv)