# Practice ROM

A romhack of the SNES game "Secret of Evermore" built with the everscript compiler.

## Overview

Extends the ROM and patches in “Brian’s Test Chamber” as hub and the debug ring menu to manipulate the game.

### Hub features:
- Teleports to various locations from the speedruns

### Ring Menu Features:
- Built in cheats for atlas glitch, no-clip and items (consumables, weapons, armor, etc.)
- Spawning various enemies
- Access to the wind walker (Mode7 flying)
- etc.

### Optional Patches: (Pre-integrated in the main patch)
- Unlocks the camera
- Room Timer

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
- `patches/room_timer*` - Skarsnikus
- `patches/debug_menu_*` - XaserLE