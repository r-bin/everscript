enum DIRECTION {
    NORTH = 0x26,
    EAST = 0x02,
    SOUTH = 0x03,
    WEST = 0x04
}

enum DOG {
    WOLF = 0x2,
    WOLF2 = 0x4,
    GREYHOUND = 0x6,
    POODLE = 0x8,
    PUPPER = 0xa,
    TOASTER = 0xc
}

enum CHARACTER {
    BOY = 0xd0,
    DOG = 0xd1,
    ACTIVE = 0xd2,
    INACTIVE = 0xd3,

    BOTH = 0x00,
    NONE = 0x01
}

enum MUSIC {
    START = 0x12,

    FANFARE = 0x78
}

enum MAP {
    START = 0x00,
    RAPTORS = 0x5c,
    FE_VILLAGE = 0x25
}

enum FLAG {
    RAPTORS = [0x225f, 0x40],
    GOURD_1 = [0x2268, 0x40],
    
    IN_ANIMATION = [0x22eb, 0x20]
}

enum MEMORY {
    DOG = [0x2443],
    GAIN_WEAPON = [0x2441]
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

fun teleport(character, x, y) {
    if(character == CHARACTER.BOTH) {
        code(0x20, x, y, "// (20) Teleport both to 43 93");
    }
}

fun init_map(x_start, y_start, x_end, y_end) {
    code(0x1b, 0x23e9 - 0x2258, 0x23eb - 0x2258, x_start, y_start);
    code(0x1b, 0x23ed - 0x2258, 0x23ef - 0x2258, x_end, y_end);
}

fun music(music) {
    code(0x33, music, "// PLAY MUSIC 0x12");
}
fun music_volume(music, volume) {
    music(music);
    code(0x86, 0x82, volume, "// (86) SET AUDIO volume to 0x64");
}

fun price(index, rate, drop, quantity) {
    if(index == 0x1) {
        [0x239b] = rate;
        [0x23a1] = drop;
        [0x23a7] = quantity;
    } else if(index == 0x2) {
        [0x239d] = rate;
        [0x23a3] = drop;
        [0x23a9] = quantity;
    } else if(index == 0x3) {
        [0x239f] = rate;
        [0x23a5] = drop;
        [0x23ab] = quantity;
    }
}