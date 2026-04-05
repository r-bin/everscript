# 0x3a — Nobilia, Fire Pit (WindWalker Launch Pad)

| Field | Value |
|-------|-------|
| **ROM addr** | `0x9ffecf` |
| **Data addr** | `0xadab68` |
| **Enter script** | `0x92813d` → `0x97c543` |
| **Step-on table** | `0xadab77` len=`0x000c` (2 entries) |
| **B-trigger table** | `0xadab85` len=`0x0000` (0 entries) |
| **Music** | `0x40` (normal) / `0x84` (outro cinematic) |
| **Act** | Act 2 — Antiqua |

## Overview

The Nobilia fire pit that serves as the WindWalker launch pad to Gothica and,
later, Omnitopia. Acts as the cross-act gateway from Antiqua to Gothica. Has two
entry modes: normal (music `0x40`, no cutscene) and "outro" (`$22f1&0x40`, which
plays the inter-act cinematic with special rain/sky effects). The latter sends
the player to either [0x08] Nobilia Square or [0x39] Gothica — Ebon Keep Fire Pit
depending on WW landing state.

No B-triggers. The only interactive elements are the two step-ons.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22f1` | `0x40` | 📖 | Inside outro mode (set before loading this room for the WW launch cinematic) |
| `$22dc` | `0x08` | 📖 | WindWalker unlocked (gates WW departure) |
| `$22e5` | `0x08` | 📖 | WW Landing (set before loading fire pit from overworld) |
| `$22fe` | — | ⚙️ | Outro landing counter (first WW landing = 1; second = 2) |
| `$2355` | — | ⚙️ | WindWalker destination state: 1=Gothica, 2=Omnitopia selector |
| `$237d` | — | ⚙️ | WindWalker travel state (3=Gothica route, 4=Omnitopia route) |
| `$237b` | — | ⚙️ | WindWalker landing state |
| `$246b` | — | ⚙️ | WW animation trigger flag |
| `$2834` | — | ⚙️ | NPC entity ref (Emperor/Horace on WW pad; session-local) |
| `$2838` | — | ⚙️ | NPC `0x8a` (Horace?) entity ref for outro; session-local |
| `$23b9`/`$23bb` | — | ⚙️ | WW target X/Y position |
| `$249d`/`$249f` | — | ⚙️ | WW destination X/Y position |

## Enter Script Summary

1. If `!IN_ANIMATION`: teleport both to `(0x0b, 0x1b)`, fade-out; else clear in-animation.
2. **Debug shortcut** (if `$22eb&0x08` debug): SET `$22f1|=0x40` (outro mode) + SET `$22dc|=0x08` (WW unlocked).
3. **Outro mode** (`$22f1&0x40`): play music `0x84`, fade-in; skip normal music.
   - Else: play music `0x40` if change-music flag set.
4. Write `$23bf = 0x0000`; unload OBJ 1 and OBJ 0.
5. **If `$22f1&0x40`** (outro cinematic):
   - `$23bf=0x0001`; hide status bar; write `$2355=0x0002`, `$237d=0x0003`.
   - Call sky/rain color setup scripts (`0x92d93e`, `0x92d92a`).
   - **If `$22fe == 1`** (first WW landing): SET `$22e5|=0x08`; increment `$22fe`; skip to main continue.
   - **Else** (`$22fe != 1`): load NPC `0x8a` at `(0x1d, 0x00)` → `$2838`; teleport NPC+boy to `(0x0088, 0x00b8)`, dog to `(0x00e8, 0x00c8)`; clear `$22e5&0xf7`.
   - **If WW landing conditions** (`($22e5&0x08 || $237b==3)` AND `$22dc&0x08` AND `$237d==3`):
     - `$2355==1`: load objs 0+1, load NPC `0x20` → `$2834`, animate.
     - `$2355==2`: load obj 0 only, load NPC `0x20` → `$2834`, animate.
     - If `$22e5&0x08`: write `$237b=3`, stop both, teleport all to `(0x00e8, 0)`.
6. Dog unavailable: hide dog at `(0x2e, 0x01)`, global `0x36`, disable; else → cinematic `0x92de75`.
7. **Outro mode post-cinematic**: run WW departure or arrival logic based on `$22e5&0x08` / `$22dc&0x08` / `$237d`:
   - If WW landing (`$22e5&0x08`): run arrival walk-in sub (`0x97c344`), then CHANGE MAP → [0x08] Nobilia Square @ `[0x02d8|0x01b8]`.
   - Else: run walk-up sub (`0x97c4f8`); if `$2355==2`: walk NPC off + destroy; sleep 29 ticks.
   - If launching: write `$22e5|=0x08`, `$246b=0x0001`; **WINDWALK** args 22 0 0 0 0 0; clear `$238f`; CHANGE MAP → [0x39] Gothica — Ebon Keep Fire Pit @ `[0x0138|0x01d8]`.

## Exits

| Dest | Coords | Trigger |
|------|--------|---------|
| [0x08] Nobilia Square | `[0x02d8\|0x01b8]` | Step-on `[11,17:12,1a]` (or outro arrival) |
| [0x39] Ebon Keep Fire Pit | `[0x0138\|0x01d8]` | WW launch (outro mode); **cross-act to Gothica** |

## Step-ons

| Tile | Action |
|------|--------|
| `[1a,14:21,1b]` | Main WW launch pad: if `$2355==1` → Gothica launch (`$237d=3`, call `0x92dc02`); if `$2355==2` → Omnitopia prompt *"Is your destination Omnitopia?"* YES→`$237d=4` call `0x92dc51`; NO→`$237d=3` call `0x92dc1b` |
| `[11,17:12,1a]` | → [0x08] Nobilia Square; global `0x19` |

## B-Triggers

None.

## NPCs

| Ref | NPC# | Pos | Notes |
|-----|------|-----|-------|
| `$2838` | `0x8a` (Horace?) | `(0x1d, 0x00)` | Outro cinematic only; destroyed after landing sequence |
| `$2834` | `0x20` (Emperor?) | `(0x1d, 0x19)` | WW state 1 or 2 sub-paths during outro |

## Notes

- `$22f1&0x40` ("Inside outro?") is set by an external room before loading 0x3a,
  not by 0x3a itself; this flag tells the room to run the inter-act WW launch cinematic.
- `$2355` determines WW destination: value `1` = Gothica only; value `2` = can also
  choose Omnitopia. The step-on triggers the choice prompt only when `$2355==2`.
- The **WINDWALK** instruction at `0x97c6e7` (args `22 0 0 0 0 0`) is the actual
  WindWalker flight animation; it fades to `[0x39]` Ebon Keep, completing the
  Act 2 → Act 3 transition.
- `$22e5&0x08` (WW Landing) is set before entering this room from the overworld
  when the WindWalker is landing; the enter script uses it to play the landing
  arrival sub instead of the launch departure.
