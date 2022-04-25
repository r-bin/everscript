# everscript
Compiler for assembler based scripts, used in the SNES game "Secret of Evermore".

Almost completely based on the results of [SoETilesViewer](https://github.com/black-sliver/SoETilesViewer) and the work of [Black Sliver](https://github.com/black-sliver).

# Idea
The game already uses a script language (instead of pure ASM) for the game logic/story, which can be made available to developers:

- Painless changes on a script level
  - Macros to reuse code
- Dynamic memory management
  - `label`s for jumps
  - `if`'s as jump replacement
- IPS format for outputs

# Example
Making a gourd teleport the player to the next room: (before and after)

```
[0x38] Prehistoria - South jungle / Start at 0x9ffec7
  data at 0x9e8000
  enter script at 0x928133 => 0x9384d9
  ...
  B trigger scripts at 0x9e801d, len=0x00ba (31 entries)
    [40,30:42,32] = (id:7e6 => (80ad@928a7a) => addr:0x9380ad)
      [0x9380ad] (08) IF !($2269&0x08) SKIP 21 (to 0x9380c8)
      [0x9380b3] (18) WRITE PRIZE    ($2391) = Money (0x0001)
      [0x9380b7] (18) WRITE AMOUNT   ($2393) = 0x000f
      [0x9380bb] (17) WRITE MAP REF? ($2395) = 0x0005
      [0x9380c0] (a3) CALL "Loot gourd?" (0x3a)
      [0x9380c2] (0c) $2269 |= 0x08 if ($22ea & 0x01) else $2269 &= ~0x08
      [0x9380c8] (00) END (return)
```
```
[0x38] Prehistoria - South jungle / Start at 0x9ffec7
  data at 0x9e8000
  enter script at 0x928133 => 0x9384d9
  ...
  B trigger scripts at 0x9e801d, len=0x00ba (31 entries)
    [40,30:42,32] = (id:7e6 => (80ad@928a7a) => addr:0x9380ad)
      [0x9380ad] (29) CALL 0xb08000 Unnamed ABS script 0xb08000
      [0x9380b1] (00) END (return)
```

## IN

```
@install()
@inject(0x9380ad)
fun room_1_exit_north() {
    transition(0x5c, 0x1d, 0x33, DIRECTION.NORTH);
}
```
## OUT
```
PATCH
1380AD 0005 // address=1278125 count=5
// call(11567104)
29 00 00 0F      // (29) CALL 0x92de75 Some cinematic script (used multiple times)"
00      // (00) END (return)"
308000 000A // address=3178496 count=10
a3 00 // (a3) CALL Fade-out / stop music (0x00)
a3 26 // (a3) CALL 'Prepare room change? North exit/south entrance outdoor-indoor?' (0x26)
22 1d 33 5c 00 // (22) CHANGE MAP = 0x34 @ [ 0x0090 | 0x0118 ]: ...
00      // (00) END (return)"
EOF
```

# Credits
- [SoETilesViewer](https://github.com/black-sliver/SoETilesViewer) - Black Sliver
- [rply](https://github.com/alex/rply)
- `/patches/skip_intro.txt` - Black Sliver
