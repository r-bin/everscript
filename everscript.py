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

enum ENEMY {
    FLOWER = 0x0b
}
enum ITEM {
    JAGUAR_RING = 0x0100,

    AXE_1 = 0x0200,
    SPEAR_3 = 0x0201,
    
    HARD_BALL = 0x0300,
    ACID_RAIN = 0x0301,
    FLASH = 0x0302,

    WINGS = 0x0400,
    PETAL = 0x0401,
    NECTAR = 0x0402
}

fun add_enemy(enemy, x, y) {
    code(0xba, enemy, x, y, "// (ba) LOAD NPC 0b at 49 79");
}

fun add_enemy_with_flags(enemy, x, y, flags) {
    code(0x3c, enemy, 0x00, flags, x, y, "// (ba) LOAD NPC 0b at 49 79");
}

fun control(character) {
    if(character == CHARACTER.NONE) {
        code(0xc0, "// (c0) BOY+DOG = STOPPED");
    } else if(character == CHARACTER.BOTH) {
        code(0xc1, "// (c1) BOY+DOG = Player controlled");
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

fun subtext(id) {
    code(0x52, id, "// (52) SHOW TEXT 066f FROM 0x91d66f compressed UNWINDOWED c03ad9> 'Received Jaguar Ring'");
}

fun question(id) {
    text_start();

    text(id);
    
    eval("1d 69 00 30 ac // (1d) WRITE $289d = Dialog response (preselect 0)");
    
    text_end();
}

fun dialog(id) {
    text_start();

    text(id);

    text_end();
}

fun sleep(ticks) {
    code(0xa7, ticks, "// (a7) SLEEP 59 TICKS");
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
        set([0x2262, 0x02]);

        sleep(0x20);
        subtext(0x066f);
        
        fanfare_weapon();
    } else if(item == ITEM.AXE_1) {
        [0x2441] = 0x0a;
        
        subtext(0x05b8);
        fanfare_weapon();
    } else if(item == ITEM.SPEAR_3) {
        [0x2441] = 0x18;
        
        subtext(0x2247);
        fanfare_weapon();
    } else if(item == ITEM.HARD_BALL) {
        set([0x225a, 0x02]);
        
        dialog(0x0651);
        fanfare_weapon();
    } else if(item == ITEM.FLASH) {
        set([0x2259, 0x80]);
        
        dialog(0x0963);
        fanfare_weapon();
    } else if(item == ITEM.ACID_RAIN) {
        set([0x2258, 0x01]);
        
        dialog(0x059d);
        fanfare_weapon();
    } else if(item == ITEM.WINGS) {
        eval("18 39 01 84 04 08 // (18) WRITE PRIZE    ($2391) = Wings (0x0804)");
        eval("17 3d 01 14 00 // (17) WRITE MAP REF? ($2395) = 0x0014");
        eval("a3 3a // (a3) CALL "Loot gourd?" (0x3a)");
        
        fanfare_weapon();
    } else if(item == ITEM.PETAL) {
        eval("18 39 01 84 00 08 // (18) WRITE PRIZE    ($2391) = Wings (0x0804)");
        eval("17 3d 01 02 00 // (17) WRITE MAP REF? ($2395) = 0x0014");
        eval("a3 3a // (a3) CALL "Loot gourd?" (0x3a)");
        
        fanfare_weapon();
    } else if(item == ITEM.NECTAR) {
        eval("18 39 01 84 01 08 // (18) WRITE PRIZE    ($2391) = Wings (0x0804)");
        eval("17 3d 01 12 00 // (17) WRITE MAP REF? ($2395) = 0x0014");
        eval("a3 3a // (a3) CALL "Loot gourd?" (0x3a)");
        
        fanfare_weapon();
    }
}

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

fun loot_legendary() {
    if([0x289d] == 0x01) {
        reward(ITEM.HARD_BALL);
        reward(ITEM.FLASH);
    } else if([0x289d] == 0x02) {
        reward(ITEM.SPEAR_3);
    } else if([0x289d] == 0x03) {
        reward(ITEM.WINGS);
    }
}
fun loot_epic() {
    if([0x289d] == 0x01) {
        reward(ITEM.HARD_BALL);
    } else if([0x289d] == 0x02) {
        reward(ITEM.AXE_1);
    } else if([0x289d] == 0x03) {
        reward(ITEM.PETAL);
        reward(ITEM.NECTAR);
    }
}
fun loot_rare() {
    if([0x289d] == 0x01) {
        reward(ITEM.FLASH);
    } else if([0x289d] == 0x02) {
        reward(ITEM.AXE_1);
    } else if([0x289d] == 0x03) {
        reward(ITEM.NECTAR);
    }
}
fun loot_common() {
    if([0x289d] == 0x01) {
        reward(ITEM.ACID_RAIN);
    } else if([0x289d] == 0x02) {
        reward(ITEM.AXE_1);
    } else if([0x289d] == 0x03) {
        reward(ITEM.PETAL);
    }
}

fun rng_fiesta(difficulty) {
    question(0x10bf);

    if(difficulty >= 0x30) {
        loot_legendary();
    } else if(difficulty > 0x14) {
        loot_epic();
    } else if(difficulty > 0x0a) {
        loot_rare();
    } else {
        loot_common();
    }
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
    
    if(!FLAG.IN_ANIMATION) {
        teleport(CHARACTER.BOTH, 0x46, 0x89);
    }

    music_volume(MUSIC.START, 0x64);
    eval("29 75 5e 00 // (29) CALL 0x92de75 Some cinematic script (used multiple times)");
}

@install()
@inject(0x13802b)
fun first_gourd() {
    rng_fiesta(rnd(0x00, 0x20));

    transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.NORTH, DIRECTION.NORTH);
}

@install()
@inject(ADDRESS.FE_EXIT_EAST)
fun village_exit_east() {
    MEMORY.DOG = DOG.TOASTER;
    transition(MAP.THRAXX, 0x17, 0x3f, DIRECTION.WEST, DIRECTION.NORTH);
}
@install()
@inject(ADDRESS.THRAXX_EXIT_NORTH)
@inject(ADDRESS.THRAXX_EXIT_SOUTH)
fun thraxx_exit() {
    if(!FLAG.RANDOM_1) {
        set(FLAG.RANDOM_1);
        rng_fiesta(rnd(0x10, 0x20));
    }
    transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.UNKNOWN, DIRECTION.NORTH);
}

@install()
@inject(ADDRESS.FE_EXIT_SOUTH)
fun fe_exit_south() {
    MEMORY.DOG = DOG.TOASTER;
    transition(MAP.RAPTORS, 0x1d, 0x33, DIRECTION.SOUTH, DIRECTION.NORTH);
}
fun raptor_flags() {
    if(!FLAG.RANDOM_2) {
        set(FLAG.RANDOM_2);
        rng_fiesta(rnd(0x00, 0x10));
    }
    transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.UNKNOWN, DIRECTION.NORTH);
}
@install()
@inject(ADDRESS.RAPTORS_EXIT_SOUTH)
fun raptors_exit() {
    if(!FLAG.RAPTORS) {
        transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.UNKNOWN, DIRECTION.NORTH);
    }

    raptor_flags();
}
@install()
@inject(ADDRESS.RAPTORS_EXIT_NORTH)
fun raptors_exit() {
    set(FLAG.RAPTORS);

    raptor_flags();
}

@install()
@inject(ADDRESS.FE_EXIT_NORTH)
fun fe_exit_north() {
    MEMORY.DOG = DOG.TOASTER;
    transition(MAP.MAGMAR, 0x18, 0x47, DIRECTION.NORTH, DIRECTION.NORTH);
}

@install()
@inject(ADDRESS.FE_EXIT_WEST)
fun fe_exit_west() {
    MEMORY.DOG = DOG.TOASTER;
    transition(MAP.SALABOG, 0x1c, 0x61, DIRECTION.WEST, DIRECTION.NORTH);
}
@install()
@inject(ADDRESS.SALABOG_EXIT_SOUTH)
@inject(ADDRESS.SALABOG_EXIT_NORTH)
fun salabog_exit() {
    if(!FLAG.SALABOG) {
        transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.UNKNOWN, DIRECTION.NORTH);
    }

    if(!FLAG.RANDOM_4) {
        set(FLAG.RANDOM_4);
        rng_fiesta(rnd(0x15, 0x20));
    }
    transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.UNKNOWN, DIRECTION.NORTH);
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

