# [0x62] Gothica — Ivor Tower, West Square (Trailers)

| Field | Value |
|-------|-------|
| Room ID | 0x62 |
| Name | Gothica - Ivor Tower, west square (trailers) |
| Act | Act 3 — Gothica |
| Data offset | `0xa0f130` (shared page) |
| Enter script | `0x928205` → `0x9aaae8` (shared) → `0x9aaae8`→ enters at `0x9aaae8` |
| Step-ons | 9 |
| B-triggers | 0 |
| Music | 0x76 |

> **Note**: The enter script address `0x9aaae8` is in the same code region as 0x4e's scripts. Enter script resolves to `0x9aaabf` per `enter script at 0x928205 => 0x9aaae8`.

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 9 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | none |
| NPCs | 1 barker (NPC `0x90>>1 = 0x48`) |
| Forced dog form | Poodle (0x08) |
| Music | 0x76 |

---

## Overview

The outdoor square in front of Perceval Plank's Exhibition trailers. Contains a barker NPC (`$2835`, NPC type 0x48) who pitches the sideshow. Walking into the trailer entrance zones triggers a one-shot barker speech. Two trailers are enterable (left → 0x63 with `$234b=0`, right → 0x63 with `$234b=2`); middle trailer door is locked. The `$22f5&0x20` pig-race flag skips loading the barker NPC entirely (used when the player re-enters this room while the pig race is in progress in 0x4e).

When returning from a trailer (`$22eb&0x40`), one of OBJ 0/1/2 is cycled based on `$234b` as an exit animation, then SOUND 0x42 plays.

---

## Enter Script Logic

1. If `$22eb&0x20` (in animation): teleport both to `[54,43]`, fade-out, clear flag
2. Set dog = Poodle (`$2443 = 0x08`)
3. If NOT `$22f5&0x20` (pig race NOT pending): load NPC `0x90>>1 = 0x48` at `[2f,23]` → `$2835`, script-controlled, facing south, talk `0x1ac7`
4. Play music 0x76 if `$238d == 0x00`; set `$23bf = 0x0001`
5. If `$22eb&0x40` (returning from trailer): based on `$234b`:
   - 0 → cycle OBJ 0, SOUND 0x42
   - 1 → cycle OBJ 1, SOUND 0x42
   - 2 → cycle OBJ 2, SOUND 0x42
   - other → cinematic only

---

## Barker Speech (Step-On, One-Shot)

Step-ons at `[22,27:23,2b]`, `[2b,27:2c,2b]`, `[23,2a:2b,2b]`, `[23,27:25,28]`, `[29,27:2b,28]` all call `0x9aa4a9`.

If NOT `$2834&0x01` (speech not yet triggered):
- Sets `$2834 |= 0x01`
- Walks boy+dog to `[31,27]`/`[35,23]`
- Loads `$283b` = NPC 0x55 at `[0f,2f]` (talk `0x1ac1`)
- Loads `$283d` = NPC 0x51 at `[37,3b]` (talk `0x1ac4`)
- Barker (`$2835`) speaks:
  - "Come one, come all to Perceval Plank's Exhibition of Cultural Oddities."
  - "Witness inconceivable deviations from the natural laws."
  - "Experience true horror, true terror, true spine-tingling absurdity!"
  - "Believe the unbelievable!"
  - "Right this way! Come one! Come all!"

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[22,27:23,2b]` | barker speech `0x9aa4a9` | One-shot, `$2834&0x01` guard |
| `[2b,27:2c,2b]` | barker speech `0x9aa4a9` | same |
| `[23,2a:2b,2b]` | barker speech `0x9aa4a9` | same |
| `[23,27:25,28]` | barker speech `0x9aa4a9` | same |
| `[29,27:2b,28]` | barker speech `0x9aa4a9` | same |
| `[34,3b:3c,3d]` | MAP 0x4e @ `[0x0150|0x0008]` | South → west alley (market) |
| `[26,23:28,24]` | "Locked" | Middle trailer door |
| `[17,26:19,27]` | MAP 0x63 @ `[0x0260|0x0138]` | Left trailer entrance; `$234b = 0x00` |
| `[34,26:36,27]` | MAP 0x63 @ `[0x0260|0x0138]` | Right trailer entrance; `$234b = 0x02` |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22f5` | 0x20 | R | 📖 Pig race pending — if set, barker NPC is NOT loaded |
| `$2834` | 0x01 | R/W | 📖 Barker speech triggered (one-shot step-on guard) [0x62] |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard (standard `IN_ANIMATION` pattern) |
| `$22eb` | 0x40 | R/W | ⚙️ Returning-from-trailer flag; cleared implicitly by enter re-entry |
| `$234b` | — | R | ⚙️ Which trailer was entered (0=left, 1=middle, 2=right) — controls exit animation OBJ |
| `$2443` | — | W | ⚙️ Dog form set to Poodle (0x08) on entry |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |
| `$238d` | — | R | ⚙️ CHANGE_MUSIC flag |
| `$2835` | — | W | ⚙️ Barker NPC pointer (NPC 0x48 at `[2f,23]`) |
| `$283b` | — | W | ⚙️ Crowd NPC pointer (NPC 0x55 at `[0f,2f]`) — loaded during barker speech |
| `$283d` | — | W | ⚙️ Crowd NPC pointer (NPC 0x51 at `[37,3b]`) — loaded during barker speech |

## Notes

- `$234b` encodes which of the three trailers was entered (0=left, 1=middle, 2=right); the value persists into 0x63 and back to 0x62 to determine the correct exit position on return.
- The barker NPC and crowd NPCs (`$283b`/`$283d`) are suppressed while the pig race is pending (`$22f5&0x20` set).
- `$22eb&0x40` signals "returning from trailer" to the enter script; it is set just before the step-on exit to 0x63 and implicitly cleared on re-entry to 0x62.
