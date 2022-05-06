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
    generated = utils.beautify_output(generated)
    utils.dump(generated, "patch.txt")

    generated_clean = generator.clean(generated)
    utils.dump(generated_clean, "patch.clean.txt")

    generator.file(generated_clean, "out/everscript.ips")
    
    log(f"done!")
    #print(generated)

code = """
#include("in/core.evs")

#memory(
    0x300000..0x3fffff // extension
)

fun upgrade_dog() {
    <0x24a7> = <0x24a7> + 0x02;
    if(<0x24a7> > DOG.TOASTER) {
        <0x24a7> = DOG.TOASTER;
    }
    MEMORY.DOG = <0x24a7>;
}

fun loot_legendary() {
    if(<0x289d> == 0x00) {
        reward(ITEM.HARD_BALL);
        reward(ITEM.FLASH);
    } else if(<0x289d> == 0x01) {
        reward(ITEM.SPEAR_3);
    } else if(<0x289d> == 0x02) {
        reward(ITEM.WINGS);
    } else if(<0x289d> == 0x03) {
        upgrade_dog();
    }
}
fun loot_epic() {
    if(<0x289d> == 0x00) {
        reward(ITEM.HARD_BALL);
    } else if(<0x289d> == 0x01) {
        reward(ITEM.AXE_1);
    } else if(<0x289d> == 0x02) {
        reward(ITEM.PETAL);
        reward(ITEM.NECTAR);
    } else if(<0x289d> == 0x03) {
        upgrade_dog();
    }
}
fun loot_rare() {
    if(<0x289d> == 0x00) {
        reward(ITEM.FLASH);
    } else if(<0x289d> == 0x01) {
        reward(ITEM.AXE_1);
    } else if(<0x289d> == 0x02) {
        reward(ITEM.NECTAR);
    } else if(<0x289d> == 0x03) {
        upgrade_dog();
    }
}
fun loot_common() {
    if(<0x289d> == 0x00) {
        reward(ITEM.ACID_RAIN);
    } else if(<0x289d> == 0x01) {
        reward(ITEM.AXE_1);
    } else if(<0x289d> == 0x02) {
        reward(ITEM.PETAL);
    } else if(<0x289d> == 0x03) {
        upgrade_dog();
    }
}

fun rng_fiesta(difficulty) {
    question(STRING.RANDOM_UNCOMPRESSED_1);

    if(difficulty >= 0x30) {
        dialog(STRING.RANDOM_UNCOMPRESSED_2);
        loot_legendary();
    } else if(difficulty > 0x14) {
        dialog(STRING.RANDOM_UNCOMPRESSED_3);
        loot_epic();
    } else if(difficulty > 0x0a) {
        dialog(STRING.RANDOM_UNCOMPRESSED_4);
        loot_rare();
    } else {
        dialog(STRING.RANDOM_UNCOMPRESSED_5);
        loot_common();
    }
}

@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER)
fun south_forest_enter() {
    <0x24a7> = DOG.TOASTER;
    MEMORY.DOG = <0x24a7>;

    // transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.NORTH, DIRECTION.NORTH);

    init_map(0x00, 0x02, 0x80, 0x96);

    price(0x1, 0xa, 0x0800, 0x1);
    price(0x2, 0x5, 0x0805, 0x1);
    price(0x3, 0x2, 0x0001, 0x1);

    // MEMORY.DOG = DOG.TOASTER;

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
        teleport(CHARACTER.BOTH, 0x50, 0x83);
    }

    music_volume(MUSIC.START, 0x64);
    fade_in();
}
@install(0x94ce7b, False)
fun fe_village_dog() {
    eval("4d 4d 4d 4d");
}
@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER_GOURD_1)
fun first_gourd() {
    set(<0x2262, 0x02>);

    // transition(MAP.RAPTORS, 0x1d, 0x33, DIRECTION.NORTH, DIRECTION.NORTH);
    
    question(STRING.RANDOM_UNCOMPRESSED_1);
    loot_legendary();
}

@install()
@inject(ADDRESS.FE_EXIT_EAST)
fun village_exit_east() {
    MEMORY.DOG = DOG.TOASTER;
    transition(MAP.THRAXX, 0x17, 0x3f, DIRECTION.WEST, DIRECTION.NORTH);
}
@install(0x93d349, False)
fun thraxx_heal() {
    eval("4d 4d 4d 4d 4d");
    eval("4d 4d 4d 4d 4d");
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
    transition(MAP.RAPTORS, 0x1d, 0x33, DIRECTION.SOUTH, DIRECTION.NORTH);
}
@install(0x93912c, False)
fun raptors_dog() {
    eval("4d 4d 4d 4d");
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
@inject(ADDRESS.FE_EXIT_WEST)
fun fe_exit_west() {
    transition(MAP.MAGMAR, 0x18, 0x47, DIRECTION.NORTH, DIRECTION.NORTH);
}

@install()
@inject(ADDRESS.FE_EXIT_NORTH)
fun fe_exit_north() {
    transition(MAP.SALABOG, 0x1c, 0x61, DIRECTION.WEST, DIRECTION.NORTH);
}
@install(0x978e34, False)
fun fe_village_dog() {
    eval("4d 4d 4d 4d");
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

@install(ADDRESS.STRING_RANDOM_UNCOMPRESSED_1)
fun string_test_1() {
    string("[0x96][0x8b]Alchemy[LF]");
    string("[0x8b]Weapon[LF]");
    string("[0x8b]Consumable[LF]");
    string("[0x8b]Dog");
}

fun text_header() {
    string("[0x96].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b].[PAUSE:0b][LF]");
}
fun text_footer() {
    string("[0x86]");
}
@install(ADDRESS.STRING_RANDOM_UNCOMPRESSED_2)
fun string_test_2() {
    text_header();
    string("L[PAUSE:2b]-[PAUSE:2b]E[PAUSE:2b]-[PAUSE:2b]G[PAUSE:2b]-[PAUSE:2b]E[PAUSE:2b]-[PAUSE:2b]N[PAUSE:2b]-[PAUSE:2b]D[PAUSE:2b]-[PAUSE:2b]A[PAUSE:2b]-[PAUSE:2b]R[PAUSE:2b]-[PAUSE:2b]Y loot![PAUSE:2b]![PAUSE:4b]![PAUSE:8b]1");
    text_footer();
}
@install(ADDRESS.STRING_RANDOM_UNCOMPRESSED_3)
fun string_test_2() {
    text_header();
    string("EPIC loot![PAUSE:2b]![PAUSE:4b]![PAUSE:8b]1");
    text_footer();
}
@install(ADDRESS.STRING_RANDOM_UNCOMPRESSED_4)
fun string_test_2() {
    text_header();
    string("Rare loot!");
    text_footer();
}
@install(ADDRESS.STRING_RANDOM_UNCOMPRESSED_5)
fun string_test_2() {
    text_header();
    string("Some loot.");
    text_footer();
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
    
    with open("out/profile.txt", "w+") as f:
        print(result, file=f)
    print(result)
else:
    handle_parse(code, True)

utils.patch('Secret of Evermore (U) [!].smc', "out/everscript.ips")