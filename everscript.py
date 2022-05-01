from utils import Utils

from lexer import Lexer
from codegen import CodeGen
from parser import Parser
from linker import Linker

import time
import re

profile = False

utils = Utils()
utils.clean_out()

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
    log(f"handle string input:")

    log(f"reading code...")
    #print("To parse: '"+code+"'")
    
    utils.dump(re.sub("\),", "\),\n", f"{list(lexer.lex(code))}"), "lexer.txt")

    log(f"lexing code...")
    lexed = lexer.lex(code)
    log(f"generating objects...")
    parsed = parser.parse(lexed)

    log(f"creating artifacts...")
    generated = generator.generate()
    utils.dump(generated, "patch.txt")

    generated_clean = generator.clean(generated)
    utils.dump(generated_clean, "patch.clean.txt")

    generator.file(generated_clean, "out/everscript.ips")
    
    log(f"done!")
    #print(generated)

code = """
#include("in/core.evs")

fun test_dialog() {
    question(0x10bf);

    if(<0x289d> == 0x01) {
        reward(ITEM.HARD_BALL);
        reward(ITEM.FLASH);
    } else if(<0x289d> == 0x02) {
        reward(ITEM.SPEAR_3);
    } else if(<0x289d> == 0x03) {
        reward(ITEM.WINGS);
    }
}

fun spawn_jade_guy(id, x, y) {
    code(0xba, id, x, y);
    <0x2835> = MEMORY.LAST_ENTITY;
    eval("3d 8d 01 00 0c 18 // (3d) WRITE $2835+x66=0x180c, $2835+x68=0x0040 (talk script): Jaguar ring dude");
}

fun rain() {
    eval("07 2a 59 00 // (07) CALL 0x92d92a Outro rain and sky color");
}

fun rain_dark() {
    rain();
    
    eval("91 b5 // (91) Sets brightness to 0");
}

fun yield() {
    code(0x3a, "// (3a) YIELD (break out of script loop, continue later)");
}

fun shaking(on) {
    if(on > 0x00) {
        code(0x8d, 0x01, "// (8d) 01 Start screen shaking");
        code(0x18, 0xb1, 0x01, 0xb1, "// (18) WRITE SCREEN SHAKING MAGNITUDE X ($2409) = 0x0001");
        code(0x18, 0xb3, 0x01, 0xb1, "// (18) WRITE SCREEN SHAKING MAGNITUDE Y ($240b) = 0x0001");
    } else {
        code(0x8d, 0x00, "// (8d) 01 Start screen shaking");
    }

}

@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER)
fun room_1() {
    init_map(0x00, 0x02, 0x80, 0x96);

    price(0x1, 0xa, 0x0800, 0x1);
    price(0x2, 0x5, 0x0805, 0x1);
    price(0x3, 0x2, 0x0001, 0x1);

    MEMORY.DOG = DOG.TOASTER;

    add_enemy(ENEMY.FLOWER, 0x49, 0x79);
    <0x2835> = MEMORY.LAST_ENTITY;
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
    
    if(!FLAG.IN_ANIMATION) {
        teleport(CHARACTER.BOTH, 0x46, 0x89);
    }

    music_volume(MUSIC.START, 0x64);
    eval("29 75 5e 00 // (29) CALL 0x92de75 Some cinematic script (used multiple times)");
}

fun sepia() {
    eval("b4 05 b0 b0 b0 82 84 82 90 3e 59 00 // (b4) CALL Absolute (24bit) script 0x92d93e ("Unnamed ABS script 0x92d93e")  WITH 5 ARGS 0, 0, 0, 0x84, 0x90");
}

fun hide_status_bar() {
    eval("29 e7 23 00 // (29) CALL 0x92a3e7 Hide status bar layer");
}

fun clear_status_effects() {
    code(0xaa, "// (aa) Clear boy and dog statuses");
}
fun heal(character, animation) {
    if(animation == False) {
        if(character == CHARACTER.BOTH) {
            code(0x95, CHARACTER.BOY, 0x84, 0x03e7, "// (95) HEAL dog FOR 0x03e7 = 999");
            code(0x95, CHARACTER.DOG, 0x84, 0x03e7, "// (95) HEAL dog FOR 0x03e7 = 999");
        } else {
            code(0x95, character, 0x84, 0x03e7, "// (95) HEAL dog FOR 0x03e7 = 999");
        }
    } else {
        if(character == CHARACTER.BOY) {
            code(0x94, character, 0x08, 0x8d, 0x01, 0x29, 0x3f, 0x1a, 0xd5, "// (94) HEAL boy FOR *($23e5 + 15) WITH ANIMATION = health");
        } else if(character == CHARACTER.DOG) {
            code(0x94, character, 0x08, 0x8f, 0x01, 0x29, 0x3f, 0x1a, 0xd5, "// (94) HEAL dog FOR *($23e7 + 15) WITH ANIMATION = health");
        } else if(character == CHARACTER.BOTH) {
            code(0x94, CHARACTER.BOY, 0x08, 0x8d, 0x01, 0x29, 0x3f, 0x1a, 0xd5, "// (94) HEAL boy FOR *($23e5 + 15) WITH ANIMATION = health");
            code(0x94, CHARACTER.DOG, 0x08, 0x8f, 0x01, 0x29, 0x3f, 0x1a, 0xd5, "// (94) HEAL dog FOR *($23e7 + 15) WITH ANIMATION = health");
        }
    }
}

@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER_GOURD_1)
fun first_gourd() {
    set(<0x2262, 0x02>);
    // transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.NORTH, DIRECTION.NORTH);
    
    heal(CHARACTER.BOTH, True);
}
"""

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
    
    with open("out/profil.txt", "w+") as f:
        print(result, file=f)
    print(result)
else:
    handle_parse(code, True)

utils.patch('Secret of Evermore (U) [!].smc', "out/everscript.ips")

