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
    
    log(f"lexing code...")
    utils.dump(re.sub("\),", "\),\n", f"{list(lexer.lex(code))}"), "lexer.txt")

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
    dialog(STRING.RANDOM_UNCOMPRESSED_2);
    question(STRING.RANDOM_UNCOMPRESSED_1);

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

fun shaking(on) {
    if(on > 0x00) {
        code(0x8d, 0x01, "// (8d) 01 Start screen shaking");
        code(0x18, 0xb1, 0x01, 0xb1, "// (18) WRITE SCREEN SHAKING MAGNITUDE X ($2409) = 0x0001");
        code(0x18, 0xb3, 0x01, 0xb1, "// (18) WRITE SCREEN SHAKING MAGNITUDE Y ($240b) = 0x0001");
    } else {
        code(0x8d, 0x00, "// (8d) 01 Start screen shaking");
    }

}

fun fade_in() {
    eval("29 75 5e 00 // (29) CALL 0x92de75 Some cinematic script (used multiple times)");
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

    add_enemy_with_flags(ENEMY.MOSQUITO, 0x11, 0x1f, FLAG_ENEMY.MOSQUITO);
    add_enemy_with_flags(ENEMY.MOSQUITO, 0x11, 0x39, FLAG_ENEMY.MOSQUITO);
    add_enemy_with_flags(ENEMY.MOSQUITO, 0x2d, 0x7d, FLAG_ENEMY.MOSQUITO);
    add_enemy_with_flags(ENEMY.MOSQUITO, 0x73, 0x73, FLAG_ENEMY.MOSQUITO);
    add_enemy_with_flags(ENEMY.MOSQUITO, 0x75, 0x1d, FLAG_ENEMY.MOSQUITO);
    add_enemy_with_flags(ENEMY.MOSQUITO, 0x45, 0x14, FLAG_ENEMY.MOSQUITO);
    add_enemy_with_flags(ENEMY.MOSQUITO, 0x3b, 0x4d, FLAG_ENEMY.MOSQUITO);
    
    if(!FLAG.IN_ANIMATION) {
        teleport(CHARACTER.BOTH, 0x46, 0x89);
    }

    music_volume(MUSIC.START, 0x64);
    fade_in();
}

@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER_GOURD_1)
fun first_gourd() {
    set(<0x2262, 0x02>);

    // transition(MAP.RAPTORS, 0x1d, 0x33, DIRECTION.NORTH, DIRECTION.NORTH);
    
    test_dialog();
}

fun object(index, value) {
    code(0x5c, 0xb0 + index, 0xb0 + value, "// (5c) SET OBJ 5 STATE = val:1 (load/unload)");
}

@install()
@inject(ADDRESS.RAPTORS_EXIT_ENTER)
fun raptors() {
    if(!FLAG.IN_ANIMATION) {
        teleport(CHARACTER.BOTH, 0x1d, 0x27);
    }

    if(!FLAG.RAPTORS) {
        object(0x05, 0x03); // northern bushes
        object(0x04, 0x00); // southern bush
        object(0x00, 0x00); // top left
        object(0x01, 0x00); // top right
        object(0x02, 0x00); // bottom left
        object(0x03, 0x00); // bottom right
        
        music(MUSIC.RAPTORS);

        // add_enemy_with_flags(0x0040, 0x13, 0x19, 0x0022);

        add_enemy_with_flags(ENEMY.RAPTOR_RED, 0x15, 0x13, FLAG_ENEMY.INACTIVE_IMORTAL);
        MEMORY.ENTITY_1 = MEMORY.LAST_ENTITY;
        add_enemy_with_flags(ENEMY.RAPTOR_RED, 0x17, 0x29, FLAG_ENEMY.INACTIVE_IMORTAL);
        MEMORY.ENTITY_2 = MEMORY.LAST_ENTITY;
        add_enemy_with_flags(ENEMY.RAPTOR_RED, 0x25, 0x13, FLAG_ENEMY.INACTIVE_IMORTAL);
        MEMORY.ENTITY_3 = MEMORY.LAST_ENTITY;
        add_enemy_with_flags(ENEMY.RAPTOR_RED, 0x27, 0x29, FLAG_ENEMY.INACTIVE_IMORTAL);
        MEMORY.ENTITY_4 = MEMORY.LAST_ENTITY;

        // call(0x9391b9); // leaf cutscene
    }

    fade_in();
}

@install()
@inject(ADDRESS.RAPTORS_STEP_ON_FIGHT)
fun raptors_trigger() {
    // <0x2847> = 0x0001;
    // call(0x9389d1);
    
    object(0x02, 0x01);
    yield();
    yield();
    yield();
    yield();
    yield();
    yield();
    object(0x02, 0x00);
    yield();
    yield();
    yield();
    yield();
    yield();
    yield();
    object(0x02, 0x01);
    yield();
    yield();
    yield();
    yield();
    yield();
    yield();
    object(0x02, 0x00);
}

@install(ADDRESS.STRING_RANDOM_UNCOMPRESSED_1)
fun string_test() {
    string("[0x96][0x8b]Alchemy[LF]");
    string("[0x8b]Weapon[LF]");
    string("[0x8b]Consumable");
}

@install(ADDRESS.STRING_RANDOM_UNCOMPRESSED_2)
fun string_test() {
    string("[0x96].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b][LF]");
    string("EPIC loot![PAUSE:1b]![PAUSE:2b]![PAUSE:3b]1[0x86]");
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

