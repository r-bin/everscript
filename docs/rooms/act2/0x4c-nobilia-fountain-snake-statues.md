# 0x4c — Nobilia, Fountain and Snake Statues

| Field | Value |
|-------|-------|
| **ROM addr** | `0x9fff17` |
| **Data addr** | `0xab958d` |
| **Enter script** | `0x928197` → `0x95d6fc` |
| **Step-on table** | `0xab959c` len=`0x000c` (2 entries) |
| **B-trigger table** | `0xab95aa` len=`0x003c` (10 entries) |
| **Music** | `0x56` |
| **Act** | Act 2 — Antiqua |

## Overview

The plaza between Nobilia Square and the Palace grounds, dominated by a central
fountain flanked by two snake statues. Contains five dog sniff spots (Vinegar,
Water ×2, Limestone ×2) and a pair of palace-gate guards. A hidden WindWalker
platform awards one free Call Bead once the WindWalker is unlocked.

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22d0` | `0x80` | 👃 | Sniffed Vinegar (#7) [0x4c] (0xBIT) |
| `$22d1` | `0x01` | 👃 | Sniffed Water (#3) [0x4c] (0xBIT) |
| `$22d1` | `0x02` | 👃 | Sniffed Water (#4) [0x4c] (0xBIT) |
| `$22d1` | `0x04` | 👃 | Sniffed Limestone (#5) [0x4c] (0xBIT) |
| `$22d1` | `0x08` | 👃 | Sniffed Limestone (#6) [0x4c] (0xBIT) |
| `$22dc` | `0x08` | 📖 | WindWalker unlocked (gates palace entry + Call Bead easter egg) |
| `$22f2` | `0x80` | 📖 | Palace guard easter egg dialog seen [0x4c] |
| `$22c6` | `0x01` | 📖 | Free Call Bead already given [0x4c] |
| `$2834` | — | ⚙️ | Guard visit counter (session-local; incremented on each denied entry attempt) |
| `$231c` | — | ⚙️ | Current Call Bead count |
| `$234a` | — | ⚙️ | Max Call Bead count (Easter egg condition: `$231c < $234a`) |

## Enter Script Summary

1. `CHANGE_DOGGO = Greyhound (0x06)`
2. If `!IN_ANIMATION`: teleport both to `(0x16, 0x3f)`, fade-out/stop music; else clear in-animation flag.
3. Unload already-sniffed objects: `$22d0&0x80`→obj7, `$22d1&0x01`→obj3, `&0x02`→obj4, `&0x04`→obj5, `&0x08`→obj6.
4. Play music `0x56` if change-music flag set; fade in.
5. Write `$23bf = 0x0001` (pacified).
6. If `$2261&0x01` (dog unavailable): hide dog at `(1,1)`, global `0x36`, disable dog → END.
7. Else if `$22dc&0x08` (WindWalker unlocked): SET OBJ 2 STATE = `0x7e` (load WindWalker vehicle).
8. Write `$234b = 0x0000`; call cinematic script `0x92de75`; END.

## Exits

| Dest | Coords | Trigger |
|------|--------|---------|
| [0x08] Nobilia Square | `[0x0160\|0x0018]` | Step-on `[0d,26:13,28]`; global `0x21` |
| [0x0b] Palace Grounds | `[0x02b0\|0x0228]` | Step-on `[0d,09:13,0b]`; global `0x26`; sets `$234b=0x4f` |

## B-Triggers

| Tile | Flag | Description |
|------|------|-------------|
| `[0c,1c:0d,1e]` + `[0d,1c:0e,1e]` | — | Fountain NPC (boy only): *"Why are you talking to me? Yeesh! Kids these days!"* |
| `[12,0f:14,10]` | — | Palace gate right guard: if WindWalker → *"It's OK to go through"* (boy) / *"What a nice Sacred Dog!"* (dog); else dog→*"No one admitted"*; boy→`$2834>1` *"Don't you have something better to do?"* else *"No one goes through"*; `$2834+=1` |
| `[0c,0f:0e,10]` | — | Palace gate left guard: if WindWalker → easter egg `$22f2&0x80` *"Uh, kid, sorry about that vowel crack"* else *"You may enter"*; else dog→*"No one admitted—not even Sacred Dogs"*; boy→`$2834>1` sets `$22f2\|=0x80` + *"Buy a vowel"* else *"You may not enter"*; `$2834+=1` |
| `[14,18:15,23]` | `$22d1&0x01` | 👃 Sniffed Water (#3) [0x4c] (0x01) |
| `[0b,18:0c,23]` | `$22d1&0x02` | 👃 Sniffed Water (#4) [0x4c] (0x02) |
| `[08,0c:09,0d]` | `$22d1&0x04` | 👃 Sniffed Limestone (#5) [0x4c] (0x04) |
| `[17,0c:18,0d]` | `$22d1&0x08` | 👃 Sniffed Limestone (#6) [0x4c] (0x08) |
| `[0c,15:0d,16]` | `$22d0&0x80` | 👃 Sniffed Vinegar (#7) [0x4c] (0x80) |
| `[18,14:19,15]` | `$22dc&0x08` + `$22c6&0x01` | 💎 Call Bead easter egg: if WindWalker unlocked AND `!$22c6&0x01` AND `$231c < $234a` → give Call Beads (0x0807) + `$22c6\|=0x01` |

## NPCs

None loaded by script (guards are room objects, not dynamically loaded).

## Notes

- The WindWalker vehicle (obj 2) appears on the platform at top-right once
  `$22dc&0x08` is set; prior to that the platform is empty.
- `$2834` is reused across multiple rooms as a session-local counter; here it
  tracks how many times the player has been denied palace entry, enabling the
  guard's "Don't you have something better to do?" variant.
- The Call Bead easter egg only triggers once (`$22c6&0x01`); the condition
  `$231c < $234a` ensures it is not awarded if the player is already at max
  Call Beads.
