from utils import Utils

from lexer import Lexer
from codegen import CodeGen
from parser import Parser
from linker import Linker

utils = Utils()
utils.clean_out()

lexer = Lexer().get_lexer()

linker = Linker()
generator = CodeGen(linker)

pg = Parser(generator)
pg.parse()
parser = pg.get_parser()

def handle_parse(code):
    print("To parse: '"+code+"'")
    utils.dump(f"{list(lexer.lex(code))}", "lexer.txt")

    lexed = lexer.lex(code)
    parsed = parser.parse(lexed)

    generated = generator.generate()
    utils.dump(generated, "patch.txt")

    utils.dump(generator.clean(generated), "patch.clean.txt")

    generator.file(generator.clean(generator.generate()), "out/everscript.ips")
    
    print(generated)

handle_parse("""
#include("in/core.es")

@install()
@inject(0x1384d9)
fun room_1() {
    init_map(0x00, 0x02, 0x80, 0x96);

    price(0x1, 0xa, 0x0800, 0x1);
    price(0x2, 0x5, 0x0805, 0x1);
    price(0x3, 0x2, 0x0001, 0x1);

    MEMORY.DOG = DOG.TOASTER;
    
    eval("08 85 9d 04 03 00 // (08) IF !($22eb&0x20) NOT(in animation) SKIP 8 (to 0x94e60d)");
    teleport(CHARACTER.BOTH, 0x46, 0x89);

    music(MUSIC.START, 0x64);
    eval("29 75 5e 00 // (29) CALL 0x92de75 Some cinematic script (used multiple times)");
}

@install()
@inject(0x138044)
fun room_1_exit_north_goto() {
    goto(TEST);
    transition(0x25, 0x05, 0x06, DIRECTION.NORTH);
    end();
    TEST: transition(0x5c, 0x1d, 0x33, DIRECTION.NORTH);
}

@install()
@inject(0x13802b)
fun room_1_exit_north_if() {

    [0x2262] = 0x02;

    if(!FLAG.RAPTORS) {
        transition(MAP.RAPTORS, 0x1d, 0x33, DIRECTION.NORTH);
        end();
    } else {
        transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.NORTH);
    }
}
""")

utils.patch('Secret of Evermore (U) [!].smc', "out/everscript.ips")