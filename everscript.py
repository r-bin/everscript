from utils import Utils

from lexer import Lexer
from codegen import CodeGen
from parser import Parser
from linker import Linker

utils = Utils()
utils.clean_out()

lexer = Lexer().get_lexer()


def handle_lex(code):
    print("To lex: '"+code+"'")
    print(list(lexer.lex(code)))
    print("\n")

#handle_lex("0x5 0xffff 0x0 transition()")
#handle_lex("transition(0xffff, DIRECTION.NORTH)")

#handle_lex("""
#goto(TEST);
#TEST: 0x99;
#""")

#handle_lex("""
#fun room_1_exit_north(0xffff) {
#    transition(0x33, 0x03, 0x04, DIRECTION.NORTH);
#    goto(TEST);
#    goto(TEST);
#    transition(0x11, 0x05, 0x06, DIRECTION.NORTH);
#    TEST: transition(0x22, 0x07, 0x08, DIRECTION.NORTH);
#}
#""")

linker = Linker()
generator = CodeGen(linker)

pg = Parser(generator)
pg.parse()
parser = pg.get_parser()

def handle_parse(code):
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import Terminal256Formatter
    from pprint import pformat

    def pprint_color(obj):
        print(highlight(pformat(obj), PythonLexer(), Terminal256Formatter()))

    print("To parse: '"+code+"'")
    print(list(lexer.lex(code)))
    parser.parse(lexer.lex(code))
    
    out = generator.generate()
    utils.dump(out, "patch.txt")

    utils.dump(generator.clean(out), "patch.clean.txt")

    generator.file(generator.clean(generator.generate()), "out/everscript.ips")
    
    print(out)

handle_parse("""
enum DIRECTION {
    NORTH = 0x26,
    EAST = 0x02,
    SOUTH = 0x03,
    WEST = 0x04
}

enum FLAG {
    RAPTORS = [0x225f, 0x40],
    GOURD_1 = [0x2268, 0x40]
}

enum DOG {
    WOLF = 0x02,
    WOLF2 = 0x04,
    GREYHOUND = 0x06,
    POODLE = 0x08,
    PUPPER = 0x0a,
    TOASTER = 0x0c
}

fun end() {
    code(0x00, "// (00) END (return)");
}

fun fade_out() {
    code(0x27, "// (27) Fade-out screen (WRITE $0b83=0x8000)");
}
fun load_map(map, x, y) {
    code(0x22, x, y, map, 0x00, "// (22) CHANGE MAP = 0x34 @ [ 0x0090 | 0x0118 ]: ...");
}
fun prepare_transition(direction) {
    code(0xa3, direction, "// (a3) CALL "Prepare room change? North exit/south entrance outdoor-indoor?" (0x26)");
}

fun transition(map, x, y, direction) {
    fade_out();
    prepare_transition(direction);
    load_map(x, y, map);
}

fun init_map(x_start, y_start, x_end, y_end) {
    code(0x1b, 0x23e9 - 0x2258, 0x23eb - 0x2258, x_start, y_start);
    code(0x1b, 0x23ed - 0x2258, 0x23ef - 0x2258, x_end, y_end);
}

fun init_map_1() {
    init_map(0x00, 0x02, 0x80, 0x96);
}

@install()
@inject(0x138044)
fun room_1_exit_north_goto() {
    goto(TEST);
    transition(0x25, 0x05, 0x06, DIRECTION.NORTH);
    end();
    TEST: eval("a3 26");
    transition(0x5c, 0x1d, 0x33, DIRECTION.NORTH);
}

@install()
@inject(0x13802b)
fun room_1_exit_north_if() {
    if(!FLAG.RAPTORS) {
        transition(0x5c, 0x1d, 0x33, DIRECTION.NORTH);
    } else {
        transition(0x25, 0x59, 0x73, DIRECTION.NORTH);
    };
}

@install()
fun test() {
    eval("11");
    init_map_1();
}
""")

utils.patch('Secret of Evermore (U) [!].smc', "out/everscript.ips")