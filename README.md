# everscript
Compiler for assembler based scripts, used in the SNES game "Secret of Evermore".

Almost completely based on the results of [SoETilesViewer](https://github.com/black-sliver/SoETilesViewer) and the work of [Black Sliver](https://github.com/black-sliver).

# Idea
The game already uses a script language (instead of pure ASM) for the game logic/story, which can be made available to developers:

- Painless changes on a script level
  - Functions/Macros to reuse code
- Dynamic memory management
  - Scripts and Strings will be allocated automatically
  - `if`, `while`, etc. as jump replacement
- IPS format for outputs

# Example
Making a gourd teleport the player to the next room: (before and after)

```
[0x38] Prehistoria - South jungle / Start at 0x9ffec7
  data at 0x9e8000
  enter script at 0x928133 => 0x9384d9
  ...
  B trigger scripts at 0x9e801d, len=0x00ba (31 entries)
    ...
    [38,4a:3a,4c] = (id:7e9 => (802b@928a7d) => addr:0x93802b)
      [0x93802b] (08) IF !($2268&0x40) NOT(Gourd in south Jungle) SKIP 19 (to 0x938044)
      [0x938031] (18) WRITE PRIZE    ($2391) = Petal (0x0800)
      [0x938037] (17) WRITE MAP REF? ($2395) = 0x0000
      [0x93803c] (a3) CALL "Loot gourd?" (0x3a)
      [0x93803e] (0c) $2268 |= 0x40 if ($22ea & 0x01) else $2268 &= ~0x40 (Gourd in south Jungle)
      [0x938044] (00) END (return)
```
```
[0x38] Prehistoria - South jungle / Start at 0x9ffec7
  data at 0x9e8000
  enter script at 0x928133 => 0x9384d9
  ...
  B trigger scripts at 0x9e801d, len=0x00ba (31 entries)
    ...
    [38,4a:3a,4c] = (id:7e9 => (802b@928a7d) => addr:0x93802b)
      [0x93802b] (29) CALL 0xb08000 Unnamed ABS script 0xb08000
      [0x93802f] (00) END (return)
    ...
Known abs scripts
    ...
    "Unnamed ABS script 0xb08000" = (addr:0xb08000)
      [0xb08000] (a3) CALL "Fade-out / stop music" (0x00)
      [0xb08002] (0c) $22eb |= 0x20 (in animation)
      [0xb08006] (18) WRITE $238f = 0x0003
      [0xb0800a] (27) Fade-out screen (WRITE $0b83=0x8000)
      [0xb0800b] (a3) CALL "Prepare room change? North exit/south entrance outdoor-indoor?" (0x26)
      [0xb0800d] (a7) SLEEP 15 TICKS
      [0xb0800f] (22) CHANGE MAP = 0x5c @ [ 0x00e8 | 0x0198 ]: "Prehistoria - Raptors"
      [0xb08014] (00) END (return)
```
## IN
```
everscript --rom "Secret of Evermore (U) [!].smc" --patches "/patches" "in/hello_world.evs"
```
```
#memory(
    string_key(0x0000)..string_key(0x232b), // all string keys

    0x300000..0x3fffff // extension
)
#include("in/core.evs")

@install()
@inject(ADDRESS.SOUTH_JUNGLE_ENTER_GOURD_1)
fun enter_map_raptors() {
    transition(MAP.RAPTORS, 0x1d, 0x33, DIRECTION.NORTH, DIRECTION.NORTH);
}
```
## OUT
```
/out/Secret of Evermore (U) [!].patched.smc
```
```
PATCH

13802B 0005      // address=1277995 count=5 name=Token('FUN_IDENTIFIER', 'enter_map_raptors')
29 00 00 0F      // call(11567104)
00               // (00) END (return)"

308000 0015      // address=3178496 count=21 name=Token('FUN_IDENTIFIER', 'enter_map_raptors')
A3 00            // (a3) CALL Fade-out / stop music (0x00)
0c 9d 04 b1      // (0c) $22eb |= 0x20 (in animation)
18 37 01 b3      // (18) WRITE $238f = 0x0003
27               // (27) Fade-out screen (WRITE $0b83=0x8000)
A3 26            // (a3) CALL Prepare room change? North exit/south entrance outdoor-indoor? (0x26)
a7 10            // (a7) SLEEP 15 TICKS
22 1D 33 5C 00   // (22) CHANGE MAP = 0x34 @ [ 0x0090 | 0x0118 ]: ...
00               // (00) END (return)"
EOF
```

# Credits
- [SoETilesViewer](https://github.com/black-sliver/SoETilesViewer) - Black Sliver
- [rply](https://github.com/alex/rply)
- `/patches/skip_intro.txt` - Black Sliver
- `/research/maps/*` - Grizzly