# Practice ROM

A romhack of the SNES game "Secret of Evermore" built with the everscript compiler.

## Overview

## Patches

- `patches/camera_hack.evs` — Unrestricted camera (optional)

## Building

### Requirements

- Python 3.8+
- ROM (`Secret of Evermore (U) [!].smc`) (not included)
- [Asar](https://github.com/RPGHacker/asar) (optional)

### Setup

```bash
python everscript.py --rom "Secret of Evermore (U) [!].smc" --patches ./patches in/practice/practice.evs && open /Applications/Snes9x.app "./out/Secret of Evermore (U) [!].smc"
```

## Credits

- [SoETilesViewer](https://github.com/black-sliver/SoETilesViewer) - Black Sliver
- `patches/hotkeys.asm` - Skarsnikus
- `patches/debug_menu_*` - XaserLE