from injector import Injector, inject
_injector = Injector()

from utils.out_utils import *
from compiler.lexer import Lexer
from compiler.codegen import CodeGen
from compiler.parser import Parser
from compiler.linker import Linker

import time
import re


lexer = Lexer().get_lexer()
linker = Linker()
generator = CodeGen(linker)
pg = Parser(generator)
pg.parse()
parser = pg.get_parser()

def handle_parse(rom_file, patches_dir, code, profile):
    class ParserOut:
        everscript = None
        patches = None
    parser_out = ParserOut()

    def log(text):
        if profile:
            print(f"{text} ({'{:.1f}'.format(time.time() - start)}s)")
        else:
            print(text)

    start = time.time()
    
    log(f"lexing code…")
    out_utils.dump(re.sub("\),", "\),\n", f"{list(lexer.lex(code))}"), "lexer.txt")

    lexed = lexer.lex(code)
    log(f"generating objects…")
    parsed = parser.parse(lexed)

    log(f"creating patch artifact…")
    generated = generator.generate()
    parser_out.patches = generator.patches
    generated = string_utils.beautify_output(generated)
    out_utils.dump(generated, "patch.txt")
    out_utils.dump(generator.get_memory_allocation(), "memory_map.txt")

    generated_clean = file_utils.clean(generated)
    out_utils.dump(generated_clean, "patch.clean.txt")

    parser_out.everscript = out_utils.dump(generated_clean, "everscript.ips")
    
    log(f"done!")

    return parser_out

def main():
    args = arg_utils.parse()
    code = file_utils.file2string(args.input_file)

    parser_out = None
    out_utils.init_out()

    if not args.profile:
        parser_out = handle_parse(args.rom_file, args.patches_dir, code, True)
    else:
        import cProfile, pstats
        import io

        profiler = cProfile.Profile()
        profiler.enable()
        parser_out = handle_parse(args.rom_file, args.patches_dir, code, args.profile)
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('tottime')
        
        result = io.StringIO()
        pstats.Stats(profiler, stream=result).sort_stats('tottime').print_stats()
        result = result.getvalue()
        
        with open(f"{args.output_dir}/profile.txt", "w+") as f:
            print(result, file=f)
        print(result)

    if(args.rom_file != None):
        print("preparing rom:")
        out_utils.prepare_rom(args.rom_file)
        print("preparing patches:")
        out_utils.prepare_patches(args.rom_file, args.patches_dir, parser_out.patches)
    
        print("evermizer patch:")
        out_utils.patch(args.rom_file,parser_out.everscript)

    print(f"done!")

main()