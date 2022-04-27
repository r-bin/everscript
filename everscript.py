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

enum ENEMY {
    FLOWER = 0x0b
}
enum ITEM {
    JAGUAR_RING = 0x00,
    AXE_1 = 0x01
}

fun add_enemy(enemy, x, y) {
    code(0xba, enemy, x, y, "// (ba) LOAD NPC 0b at 49 79");
}

fun add_enemy_with_flags(enemy, x, y, flags) {
    code(0x3c, enemy, 0x00, flags, x, y, "// (ba) LOAD NPC 0b at 49 79");
}

fun subtext(id) {
    code(0x52, id, "// (52) SHOW TEXT 066f FROM 0x91d66f compressed UNWINDOWED c03ad9> 'Received Jaguar Ring'");
}

fun sleep(ticks) {
    code(0xa7, ticks, "// (a7) SLEEP 59 TICKS");
}

fun control(character) {
    if(character == CHARACTER.NONE) {
        code(0xc0, "// (c0) BOY+DOG = STOPPED");
    } else if(character == CHARACTER.BOTH) {
        code(0xc1, "// (c1) BOY+DOG = Player controlled");
    }
}

fun fanfare() {
    code(0xa3, 0x00, "// (a3) CALL "Fade-out / stop music" (0x00)");
    music(MUSIC.FANFARE);
    code(0xa3, 0x01, "// (a3) CALL "Fade-in / start music" (0x01)");
}
fun fanfare_item() {
    fanfare();
}
fun fanfare_weapon() {
    control(CHARACTER.NONE);
    eval("29 33 3f 00 // (29) CALL 0x92bf33 Hold up weapon");

    sleep(0x08);
    fanfare();
        
    sleep(0xc8);
    control(CHARACTER.BOTH);
}

fun reward(item) {
    if(item == ITEM.JAGUAR_RING) {
        fanfare_item();

        [0x2262] = 0x02;

        sleep(0x20);
        subtext(0x066f);
    } else if(item == ITEM.AXE_1) {
        [0x2441] = 0x0a;
        
        subtext(0x05b8);
        fanfare_weapon();
    }
}

fun text_start() {
    control(CHARACTER.NONE);
    code(0xa3, 0x02, "// (a3) CALL "Open message box?" (0x02)");
}
fun text(id) {
    code(0x51, id, "// (51) SHOW TEXT 10bf FROM 0x91e0bf compressed WINDOWED c14dd8> '[0x97][0x8b]Goat[LF]' '[0x8b]Chicken[LF]' '[0x8b]Basket'");
}
fun text_end() {
    code(0x55, "// (55) CLEAR TEXT");
    
    control(CHARACTER.BOTH);
}

fun question(id) {
    text_start();

    text(id);
    
    eval("1d 69 00 30 ac // (1d) WRITE $289d = Dialog response (preselect 0)");
    
    text_end();
}

fun test_dialog() {
    question(0x10bf);

    eval("09 0e 69 00 29 31 a2 16 00 // (09) IF ($289d == 1) == FALSE THEN SKIP 32 (to 0x96aeeb)");
    reward(ITEM.AXE_1);
}

@install()
@inject(0x1384d9)
fun room_1() {
    init_map(0x00, 0x02, 0x80, 0x96);

    price(0x1, 0xa, 0x0800, 0x1);
    price(0x2, 0x5, 0x0805, 0x1);
    price(0x3, 0x2, 0x0001, 0x1);

    MEMORY.DOG = DOG.TOASTER;

    add_enemy(ENEMY.FLOWER, 0x49, 0x79);
    add_enemy(ENEMY.FLOWER, 0x6b, 0x81);
    add_enemy(ENEMY.FLOWER, 0x51, 0x65);
    add_enemy(ENEMY.FLOWER, 0x45, 0x4d);
    add_enemy(ENEMY.FLOWER, 0x19, 0x53);
    add_enemy(ENEMY.FLOWER, 0x25, 0x3d);
    add_enemy(ENEMY.FLOWER, 0x2d, 0x63);
    add_enemy(ENEMY.FLOWER, 0x19, 0x7d);
    add_enemy(ENEMY.FLOWER, 0x1d, 0x23);
    add_enemy(ENEMY.FLOWER, 0x59, 0x21);
    add_enemy(ENEMY.FLOWER, 0x45, 0x3b);
    add_enemy(ENEMY.FLOWER, 0x63, 0x3b);
    add_enemy(ENEMY.FLOWER, 0x69, 0x51);
    add_enemy(ENEMY.FLOWER, 0x63, 0x23);
    
    if(!MEMORY.IN_ANIMATION) {
        teleport(CHARACTER.BOTH, 0x46, 0x89);
    }

    music_volume(MUSIC.START, 0x64);
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
fun room_1_exit_north_if() {
    if(!FLAG.RAPTORS) {
        transition(MAP.RAPTORS, 0x1d, 0x33, DIRECTION.NORTH);
        end();
    } else {
        transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.NORTH);
    }
}
@install()
@inject(0x13802b)
fun test() {
    test_dialog();
}
""")

utils.patch('Secret of Evermore (U) [!].smc', "out/everscript.ips")