from utils import Utils

from lexer import Lexer
from codegen import CodeGen
from parser import Parser
from linker import Linker

import time

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
    utils.dump(f"{list(lexer.lex(code))}", "lexer.txt")

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

    if([0x289d] == 0x01) {
        reward(ITEM.HARD_BALL);
        reward(ITEM.FLASH);
    } else if([0x289d] == 0x02) {
        reward(ITEM.SPEAR_3);
    } else if([0x289d] == 0x03) {
        reward(ITEM.WINGS);
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

@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER_GOURD_1)
fun first_gourd() {
    transition(MAP.STRONGHEART, 0x12, 0x23, DIRECTION.NORTH, DIRECTION.NORTH);
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

