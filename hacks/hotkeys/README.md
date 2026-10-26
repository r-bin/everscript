# Hotkey hack

Start an everscript function with a button press while playing. It replaces
`patches/hotkeys.asm`, which crashed because it started scripts inside the NMI.

| File | What |
|---|---|
| `hotkey_hack.asm` | The Asar patch: one file, features switched with `!WITH_*` / `!HOTKEY_*` defines at the top |
| `main.evs` | Demo: applies the patch and shows the pressed hotkey as a subtitle |

Build (from the repo root):

```
python everscript.py --rom "Secret of Evermore (U) [!].smc" --patches hacks/hotkeys hacks/hotkeys/main.evs
```

## Behaviour

- **Start** → `ADDRESS.HOTKEY_START`, **hold L + Start** → `HOTKEY_START_L`, **hold R + Start** →
  `HOTKEY_START_R` (L+R+Start optional, `!WITH_HOTKEY_START_LR`, script `$FD8380`).
- Once per press: holding Start fires once; adding L while Start is held fires nothing more;
  L and Start pressed in the same frame count as Start+L. Other held buttons (walking, B) are
  ignored.
- Only while the boy is free to act (`!HOTKEY_GATE`): never on the title screen, in the intro,
  cutscenes or text boxes, where the game uses Start itself.

## Vanilla-identical

The hook sits in the game's own joypad matcher (the one that makes Select switch boy and dog)
and spends exactly as many CPU cycles as the code it replaces, so a game without hotkey presses
runs like the original. Tested on three vanilla recordings (105,542 frames, Start pressed ~50
times on the title and in cutscenes): all stay in sync with the original, WRAM identical every
frame except 2 frames of one recording, where the frame ended inside the hook on a lag frame and
DP scratch `$26-$29` was caught half-written (identical again the next frame). A hotkey press
writes WRAM: the script it starts, and the demo's text pointer at `$0690`.

The demo shows text without replacing any vanilla string: the names live in the patch
(`$F8:4000`), and string key `$3690` makes the game read their pointer from WRAM `$0690`
(see TEXT in the patch).

Uses `$F8:0000-$F8:40FF` and the script slots `$FD82C0`, `$FD8300`, `$FD8340` (`$FD8380`);
keep `#memory` away from them.
