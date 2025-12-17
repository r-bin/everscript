# Kaizo Evermore

A romhack of the SNES game "Secret of Evermore" built with the everscript compiler.

## Overview

### What does 'Kaizo' mean?

- **Japanese** - In Japanese, "Kaizo" (改造, kaizō) means "reorder". In this context, it refers to rearranging existing game content rather than creating entirely new content.
- **Super Mario World** - "Kaizo Mario" refers to extremely hard, precision-oriented custom levels or hacks. In-depth knowledge about the game and pixel/frame perfect inputs are often mandatory.
- **Action RPGs** - In non-platformers the focus is often shifted to dodging enemy attacks and abusing detail knowledge about the game.

### What does this game want to be?

- Showcase of `everscript` for custom content.
- Challenging (but doable) experience.

### What does this game **NOT** want to be?

- "Secret of Evermore 2"
- I don't enjoy writing dialogues/stories.
- Free of soft-locks. I tried to warn the player about "point of no returns", but this won't be perfect.

### How to play the game

- Hold `START` when starting a new game for settings.
- Loading the game is considered cheating, I'm afraid.
- `Wings glitch` is explicitly allowed.
- Please inform me about any glitches/bugs/typos/weird text boxes.

### Known limitations of the Secret of Evermore engine

- Color palettes are limited. If there are more than a few enemies with different colors are in a map, they will start sharing colors.
- Lag quickly builds up, when there are too many enemies or scripts active at the same time.

## Patches

- `patches/scale_enemies.asm` — Scale enemy stats to a more flat baseline
- `patches/five_status_effects_fix.asm` — Instead of incorrectly making the oldest status effect permanent, it will be removed
- `patches/no_alchemy_xp.asm` — Remove alchemy leveling

## Building

### Requirements

- Python 3.8+
- ROM (`Secret of Evermore (U) [!].smc`) (not included)
- [Asar](https://github.com/RPGHacker/asar) (optional)

### Setup

```bash
python everscript.py --rom "Secret of Evermore (U) [!].smc" --patches ./patches in/kaizo/kaizo.evs && open /Applications/Snes9x.app "./out/Secret of Evermore (U) [!].smc"
```

## Credits

- [SoETilesViewer](https://github.com/black-sliver/SoETilesViewer) - Black Sliver
- `patches/save_file_growth*` - Black Sliver
- `patches/assassin_*` - Assassin17
- `patches/hotkeys.asm` - Skarsnikus
- `patches/debug_menu_*` - XaserLE