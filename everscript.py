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
    pprint_color(list(lexer.lex(code)))
    parsed_code = parser.parse(lexer.lex(code))
    
    out = generator.generate()
    utils.dump(out, "patch.txt")

    utils.dump(generator.clean(out), "patch.clean.txt")

    generator.file(generator.clean(generator.generate()), "out/everscript.ips")
    
    print(out)

handle_parse("""
enum DIRECTION {
    NORTH = 0x01,
    EAST = 0x02,
    SOUTH = 0x03,
    WEST = 0x04
}

fun end() {
    code(0x00, "// (00) END (return)");
}

fun fade_out() {
    code(0xa3, 0x00, "// (a3) CALL "Fade-out / stop music" (0x00)");
}
fun load_map(map, x, y) {
    code(0x22, x, y, map, 0x00, "// (22) CHANGE MAP = 0x34 @ [ 0x0090 | 0x0118 ]: ...");
}
fun transition(map, x, y, direction) {
    fade_out();
    
    if(direction == DIRECTION.NORTH) {
        code(0xa3, 0x26, "// (a3) CALL 'Prepare room change? North exit/south entrance outdoor-indoor?' (0x26)");
    } else if(direction == DIRECTION.EAST) {
        code(0xa3, 0x1d, "// (a3) CALL 'Prepare room change? East exit/west entrance outdoor-outdoor?' (0x1d)");
    } else if(direction == DIRECTION.SOUTH) {
        code(0xa3, 0x19, "// (a3) CALL '"Prepare room change? South exit/north entrance indoor-outdoor?'" (0x22)");
    } else if(direction == DIRECTION.WEST) {
        code(0xa3, 0x19, "// (a3) CALL 'Prepare room change? West exit/east entrance outdoor-outdoor?' (0x19)");
    };

    load_map(x, y, map);
}

@install()
@inject(0x9380ad)
fun room_1_exit_north() {
    goto(TEST);
    transition(0x25, 0x05, 0x06, DIRECTION.NORTH);
    end();
    TEST: transition(0x5c, 0x1d, 0x33, DIRECTION.NORTH);
}
@install()
@inject(0x93802b)
fun room_1_exit_north() {
    if([0x225f, 0x40]) {
        transition(0x25, 0x05, 0x06, DIRECTION.NORTH);
    } else {
        transition(0x5c, 0x1d, 0x33, DIRECTION.NORTH);
    };
}
""")

utils.patch('Secret of Evermore (U) [!].smc', "out/everscript.ips")