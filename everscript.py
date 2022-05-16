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
    
    log(f"lexing code...")
    utils.dump(re.sub("\),", "\),\n", f"{list(lexer.lex(code))}"), "lexer.txt")

    lexed = lexer.lex(code)
    log(f"generating objects...")
    parsed = parser.parse(lexed)

    log(f"creating artifacts...")
    generated = generator.generate()
    generated = utils.beautify_output(generated)
    utils.dump(generated, "patch.txt")
    utils.dump(generator.get_memory_allocation(), "memory_map.txt")

    generated_clean = generator.clean(generated)
    utils.dump(generated_clean, "patch.clean.txt")

    generator.file(generated_clean, "out/everscript.ips")
    
    log(f"done!")
    #print(generated)

code = """
#memory(
    // <0x2266>,

    // string_key(0x0000)..string_key(0x232b), // all string keys
    string_key(0x0933),
    string_key(0x111c),
    string_key(0x111f),
    string_key(0x1122),
    string_key(0x1125),

    0x300000..0x3fffff // extension
)
#include("in/core.evs")

enum STRING {
    PORTAL_ACT_1_1 = string("[0x96][0x8b]Oil[LF][0x8b]Intro skip[LF][0x8b]Thraxx[LF][0x8b]Next[END]"),
    PORTAL_ACT_1_2 = string("[0x96][0x8b]Solar[LF][0x8b]Magmar[END]"),

    PORTAL_ACT_1_1_THRAXX = string("[0x96][0x8b]Normal[LF][0x8b]Intro skip[LF][0x8b]Zombie boy[END]")
}
fun store_last_entity(tmp) {
    code(0x19, tmp - 0x2834, 0xad, "// (19) WRITE $283b = last entity ($0341)");
}

fun entity_script_controlled(tmp) {
    code(0x2a, 0x8d, tmp - 0x2834, "// (2a) Make $283b script controlled");
}

fun fake_level(level) {
    level(level);
    // heal(CHARACTER.BOTH, True);
    // MEMORY.BOY_CURRENT_HP = 0x03e7;

    MEMORY.BOY_XP_REQUIRED = 0x00;
    add_enemy_with_flags(ENEMY.MOSQUITO, 0x00, 0x00, FLAG_ENEMY.MOSQUITO);
    store_last_entity(0x2835);

    // eval("ac 8d 01 00 b4 82 96 8d 01 00 b0 // (ac) $2835 CASTS SPELL 28 POWER 0x96 ON $2837 if alive");
    eval("93 8d 01 00 84 e8 03 // (93) DAMAGE $2843 FOR 0x03e8");
}
fun fake_atlas() {
    <0x4F29> = 0xefff;

    // <0x4ECF> = 0x0090;
    // eval("17 77 2c 98 00                      // write status effect 1 = 0x0090");
    // eval("10 5a ed 07 5a ed 29 31 9a          // write status effect count += 1");
    
    <0x4ECF> = 0x0098;
    yield();
    <0x4ECF> = 0xFFFF;
}

@install()
@inject(0x94d5c7)
fun portal_act_1() {
    question(STRING.PORTAL_ACT_1_1);

    if(MEMORY.QUESTION_ANSWER == 0x00) { // Oil
        transition(0x25, 0x6f, 0x49, DIRECTION.NORTH, DIRECTION.SOUTH);
    } else if(MEMORY.QUESTION_ANSWER == 0x01) { // Intro skip
        transition(0x17, 0x39, 0x44, DIRECTION.NORTH, DIRECTION.WEST);
    } else if(MEMORY.QUESTION_ANSWER == 0x02) { // Thraxx
        question(STRING.PORTAL_ACT_1_1_THRAXX);
    
        if(MEMORY.QUESTION_ANSWER == 0x00) { // Normal
            transition(MAP.THRAXX, 0x17, 0x3f, DIRECTION.NORTH, DIRECTION.NORTH);
        } else if(MEMORY.QUESTION_ANSWER == 0x01) { // Intro skip
            transition(MAP.THRAXX, 0x17, 0x3f, DIRECTION.NORTH, DIRECTION.WEST);
        } else if(MEMORY.QUESTION_ANSWER == 0x02) { // Zombie boy
            MEMORY.BOY_CURRENT_HP = 0x0000;
            transition(MAP.THRAXX, 0x17, 0x3f, DIRECTION.NORTH, DIRECTION.NORTH);
        }
    } else if(MEMORY.QUESTION_ANSWER == 0x03) { // Next
        question(STRING.PORTAL_ACT_1_2);

        if(MEMORY.QUESTION_ANSWER == 0x00) { // Solar
            fake_level(0x0007);
            transition(0x3b, 0x51, 0xb1, DIRECTION.NORTH, DIRECTION.NORTH);
        } else if(MEMORY.QUESTION_ANSWER == 0x01) { // Magmar
            fake_level(0x0007);
            transition(MAP.MAGMAR, 0x18, 0x47, DIRECTION.NORTH, DIRECTION.NORTH);
        } else if(MEMORY.QUESTION_ANSWER == 0x01) {
            nop();
        } else if(MEMORY.QUESTION_ANSWER == 0x02) {
            nop();
        }
    }
}

@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER)
fun south_forest_enter() {
    MEMORY.DOG = DOG.WOLF;

    // transition(MAP.FE_VILLAGE, 0x59, 0x73, DIRECTION.NORTH, DIRECTION.NORTH);

    init_map(0x00, 0x02, 0x80, 0x96);

    price(0x1, 0xa, 0x0800, 0x1);
    price(0x2, 0x5, 0x0805, 0x1);
    price(0x3, 0x2, 0x0001, 0x1);

    // MEMORY.DOG = DOG.TOASTER;

    if(!FLAG.IN_ANIMATION) {
        teleport(CHARACTER.BOTH, 0x50, 0x83);
    }

    music_volume(MUSIC.START, 0x64);
    fade_in();

    add_enemy_with_flags(0x2a, 0x45, 0x81, 0x0020);
    store_last_entity(0x2835);
    eval("3d 8d 01 00 57 18");
    
    // 0x94d5c7 = 0x14d5c7 = 0x14BD70 + 0x001857
    // (3d) WRITE $2835+x66=0x1857, $2835+x68=0x0040 (talk script): Fire Eyes
    // 3d 8d 01 00 57 18

    add_enemy_with_flags(0x8a, 0x47, 0x81, 0x0020);
    store_last_entity(0x2835);
    eval("3d 8d 01 00 57 18");

    add_enemy_with_flags(0x96, 0x4a, 0x81, 0x0022);
    store_last_entity(0x2835);
    eval("3d 8d 01 00 57 18");

    add_enemy(0x57, 0x4d, 0x81);
    store_last_entity(0x2835);
    entity_script_controlled(0x2835);
    eval("3d 8d 01 00 57 18");
}
@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER_GOURD_1)
fun first_gourd() {
    set(<0x2262, 0x02>);
    
    // transition(MAP.RAPTORS, 0x1d, 0x33, DIRECTION.NORTH, DIRECTION.NORTH);
    
    // dialog(string("[0x96]test, test![0x86]"));

    unlock(ITEM.ALL);
    
    // fake_level(0x0030);
    fake_atlas();

    // select_alchemy();
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