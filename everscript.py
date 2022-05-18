from utils.utils import *

from lexer import Lexer
from codegen import CodeGen
from parser import Parser
from linker import Linker

import time
import re
import sys

profile = False

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

if False:
    code = """
    #memory(
        // <0x2266>,

        string_key(0x0000)..string_key(0x232b), // all string keys

        0x300000..0x3fffff // extension
    )
    #include("in/core.evs")

    @install()
    @inject(ADDRESS.SOUTH_JUNGLE_ENTER_GOURD_1)
    fun first_gourd() {
        dialog(string("[0x96]test, test![0x86]"));
    }

    """
else:
    if len(sys.argv) < 2:
        print("input file required")
        sys.exit(2)

    code = sys.argv[1]
    code = fileUtils.file2string(code)

if profile:
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
else:
    handle_parse(code, True)

outUtils.patch('Secret of Evermore (U) [!].smc', "out/everscript.ips")