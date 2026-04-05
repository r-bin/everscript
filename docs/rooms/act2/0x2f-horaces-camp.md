---
room: 0x2f
name: Antiqua – Horace's Camp
act: act2
data: 0xa0cd23
---

# 0x2f — Antiqua – Horace's Camp

| Field | Value |
|-------|-------|
| Room ID | 0x2f |
| Full Name | Antiqua – Horace's Camp |
| Act | 2 (Antiqua) |
| Data block | 0xa0cd23 |
| Enter script | 0x928106 → 0x96df65 |
| Step-on table | 0xa0cd32 (6 entries, 0x0024 bytes) |
| B-trigger table | 0xa0cd58 (20 entries, 0x0078 bytes) |

## Overview

Horace Highwater's outdoor camp east of Crustacia, connecting to the Waterfall (0x6b, north), Between 'Mids and Halls (0x05, east), and Outside of 'Mids (0x06, south). 

This is where **Horace is first met** — a lengthy introduction cutscene (`$22d9&0x01` gate) plays on the step-on tiles south of his campfire. Horace provides the Diamond Eye quest briefing and introduces Madronius (who gives Revealer if not yet obtained). If the player falls into a pit in 0x4f and arrives here via `$22ed&0x80`, a shorter pit-fall dialog plays instead. The room also has **20 dog-sniff B-triggers** covering ingredients #2–21 across `$22ba`, `$22bb`, `$22bc`.

The inn NPC (0x1b) is always present; Madronius (NPC 0x32) only spawns after Horace is met.

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$22ba` | R/W | (full byte) | Nature sniff spot persistence — OBJ unload on entry + sniff dog-loot flags |
| `$22bb` | R/W | (full byte) | Nature sniff spot persistence — OBJ unload on entry + sniff dog-loot flags |
| `$22bc` | R/W | &0x01–0x10 | Nature sniff spot persistence — OBJ unload on entry + sniff dog-loot flags |
| `$22d9` | R/W | &0x01 | Horace met / Madronius spawned — set on first Horace meeting step-on; gates Madronius NPC load on all subsequent entries |
| `$22d9` | R | &0x08 | Aegis dead — if set: SET OBJ 0/1 STATE = 1 (post-Aegis camp layout); also gates parts of Horace dialog |
| `$22eb` | R/W | &0x20 | IN_ANIMATION — teleport both to [0x79,0x2d] + fade; cleared otherwise |
| `$22ed` | R/W | &0x80 | Falling into a pit — if set on entry: trigger pit-fall arrival sequence (Horace dialog, fade in); cleared after cutscene |
| `$22ee` | R/W | &0x01 | Arena return / special teleport — if set: clear it, `$238f=0x000f`, teleport boy to [0x2a,0x1e], dog to [0x26,0x21] |
| `$22d8` | R | &0x40 | Diamond Eye #1 (pyramids) obtained — gates Horace's Diamond Eye direction hint |
| `$22d8` | R | &0x80 | Diamond Eye #2 (halls) obtained — gates Horace's Diamond Eye direction hint |
| `$225b` | R | &0x10 | Revealer obtained — if set, Horace skips the "talk to Madronius for Revealer" line in his intro |
| `$2348` | write | =0x0003 | CURRENCY_CURRENT — set to 3 (Jewels) on entry |
| `$23bf` | write | =0x0001 | PACIFIED — written 1 on entry |

## Enter Script Summary (`0x96df65`)

1. If `$22eb&0x20`: teleport both to [0x79,0x2d] + fade music; else clear flag.
2. `$2348 = 3` (Jewels currency).
3. **Unload persistence**:
   - `$22ba` bits 0x02–0x80 → unload OBJs 21/20/17/16/2/19/18
   - `$22bb` bits 0x01–0x80 → unload OBJs 3/5/6/4/15/7/8/9
   - `$22bc` bits 0x01–0x10 → unload OBJs 10/11/12/13/14
4. If `$22d9&0x08` (Aegis dead): SET OBJ 0/1 STATE = 1.
5. If `$22d9&0x01` (Horace met): LOAD NPC 0x32 at [0x3f,0x27]→`$2455`, talk 0x196b (Madronius).
6. LOAD NPC 0x1b at [0x19,0x29]→`$2835`, talk 0x196e (Inn keeper — always present).
7. If `$22ee&0x01`: clear it; `$238f = 0x000f`; teleport boy to [0x2a,0x1e], dog to [0x26,0x21].
8. If `$238d != 0`: PLAY MUSIC 0x22; fade in.
9. `$23bf = 1`.
10. If `$22ed&0x80` (pit-fall arrival):
    - If NOT (both Diamond Eyes): LOAD NPC 0x8a>>1 flags 0x0020 at [0x35,0x25]→`$2837` (Horace).
    - Teleport boy to [0x28,0x33] west-facing, dog to [0x2a,0x3c] west-facing.
    - Fade in (brightness loop 0→15).
    - Call pit-fall cutscene (`0x96d6cf`): if `$22d9&0x01` (met before): "You should avoid falling into those pits!"; else: Horace walkup + brief "Are you OK?" intro; then clears `$22ed&0x80`.
11. Else:
    - If NOT (both Diamond Eyes): LOAD NPC 0x45 at [0x35,0x25]→`$2837` (Horace).
    - Call cinematic setup (0x92de75).

## Step-on Scripts (6 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [2d,20:2e,22] | `0x96d7b6` | **Horace first-meet trigger** (shared — see below) |
| [28,1f:29,22] | `0x96d7b6` | Horace first-meet trigger (duplicate tile) |
| [28,22:2e,23] | `0x96d7b6` | Horace first-meet trigger (duplicate tile) |
| [3b,0e:3e,0f] | `0x96d6bb` | **EXIT north** → 0x6b (Antiqua Waterfall) at [0x0088, 0x01f8] |
| [4f,25:51,28] | `0x96d6b1` | **EXIT east** → 0x05 (Between 'Mids and Halls) at [0x0020, 0x0178] |
| [37,45:3f,47] | `0x96d6c5` | **EXIT south** → 0x06 (Outside of 'Mids) at [0x0330, 0x0020] |

**Horace first-meet trigger (`0x96d7b6`)** — fires only if `$22d9&0x01` NOT set AND NOT both Diamond Eyes:
1. SET `$22d9 |= 0x01` (Horace met).
2. If pit-fall (`$22ed&0x80`): short pit greeting, skip full intro.
3. Else: Horace walks up; full introduction:
   - "By Golly! What have we here? A visitor?"
   - "You're definitely not from Crustacia — no facial hair, tattoos or visible scars."
   - "And you're not from Nobilia either — no toga or sandals."
   - Boy: "Actually, we're from_"
   - Horace: "Wait! Let me guess! You're from… Podunk!"
   - Boy: "Wow! You're right! I'm [BOY_NAME] and this is my dog, [DOG_NAME]."
   - Horace: "It's a pleasure to meet you. I'm Horace Highwater. I, too, am from Podunk."
   - "I was the curator of the Natural History Museum in Podunk."
   - "I was part of an experiment in the big mansion on the hill, and something went wrong!"
   - "Fire Eyes — er, Elizabeth told us about it. She's Professor Ruffleberg's granddaughter."
   - "There was another guest at that party too. Miss Bluegarden, the librarian."
   - "The new leader is after the Diamond Eyes — he appeared only weeks ago."
   - "I suggest you find the diamonds and bring them to me — I'll make sure they don't fall into the wrong hands!"
   - Direction hint (branches on which Diamond Eye(s) already obtained): Pyramid (south) / Hall of Collosia (north) / both locations
   - "We've dug pits that protect these sites from harmful intruders. You can see hidden paths over these pits using the Revealer Formula."
   - If `$225b&0x10` not set: "My friend Madronius will give you this formula if you talk to him."
4. Loads Madronius at [0x3f,0x27]→`$2455`, walks to [0x3f,0x27].
5. Boy: "OK! We'll do it!"
6. Release player control.

## Exits

| Tiles | Destination | Coordinates | Notes |
|-------|-------------|-------------|-------|
| [3b,0e:3e,0f] | 0x6b — Antiqua Waterfall | [0x0088, 0x01f8] | step-on |
| [4f,25:51,28] | 0x05 — Between 'Mids and Halls | [0x0020, 0x0178] | step-on |
| [37,45:3f,47] | 0x06 — Outside of 'Mids | [0x0330, 0x0020] | step-on |

## B-Triggers (20 entries — all dog sniff spots)

| # | Tile | Flag | Item | MAP REF |
|---|------|------|------|---------|
| 2 | [50,3c:51,3d] | `$22ba&0x20` | 👃 Ethanol | 0x0002 |
| 3 | [1b,3d:1c,3e] | `$22bb&0x01` | 👃 Roots | 0x0003 |
| 4 | [3f,45:40,46] | `$22bb&0x08` | 👃 Wax | 0x0004 |
| 5 | [25,16:26,17] | `$22bb&0x02` | 👃 Limestone | 0x0005 |
| 6 | [43,19:44,1a] | `$22bb&0x04` | 👃 Limestone | 0x0006 |
| 7 | [22,35:23,36] | `$22bb&0x20` | 👃 Water | 0x0007 |
| 8 | [14,3b:15,3c] | `$22bb&0x40` | 👃 Vinegar | 0x0008 |
| 9 | [11,22:12,23] | `$22bb&0x80` | 👃 Ash | 0x0009 |
| 10 | [46,26:47,27] | `$22bc&0x01` | 👃 Bone | 0x000a |
| 11 | [46,27:47,28] | `$22bc&0x02` | 👃 Bone | 0x000b |
| 12 | [33,15:34,16] | `$22bc&0x04` | 👃 Bone | 0x000c |
| 13 | [2d,32:2e,33] | `$22bc&0x08` | 👃 Brimstone | 0x000d |
| 14 | [24,22:25,23] | `$22bc&0x10` | 👃 Brimstone | 0x000e |
| 15 | [2e,40:2f,41] | `$22bb&0x10` | 👃 Water | 0x000f |
| 16 | [4d,44:4e,45] | `$22ba&0x10` | 👃 Crystal | 0x0010 |
| 17 | [4a,3d:4b,3e] | `$22ba&0x08` | 👃 Clay | 0x0011 |
| 18 | [44,44:45,45] | `$22ba&0x80` | 👃 Roots | 0x0012 |
| 19 | [4e,3c:4f,3d] | `$22ba&0x40` | 👃 Roots | 0x0013 |
| 20 | [50,2e:51,2f] | `$22ba&0x04` | 👃 Clay | 0x0014 |
| 21 | [4f,2a:50,2b] | `$22ba&0x02` | 👃 Oil | 0x0015 |

All sniff B-triggers follow the pattern: if flag already set → skip; else loot ingredient (call 0x39), then set flag if LOOT_SUCCESSFUL, else clear. The same flag bits gate OBJ unload on room entry (preventing re-spawned ingredient objects for looted spots).

## NPCs

| NPC | Spawn | Persistent? | Notes |
|-----|-------|-------------|-------|
| NPC 0x1b (Inn keeper) | [0x19, 0x29] | Always | Talk 0x196e; stored in `$2835` |
| NPC 0x32 (Madronius) | [0x3f, 0x27] | After Horace met | Talk 0x196b; stored in `$2455`; spawns only if `$22d9&0x01` |
| NPC 0x45 / 0x8a>>1 (Horace) | [0x35, 0x25] | Conditional | Loaded only if NOT both Diamond Eyes obtained; pit-fall entry uses flags 0x0020 variant; stored in `$2837` |

## Notes

- **`$22ba&0x01` not a sniff spot in this room**: The B-trigger table starts at sniff #2 (`$22ba&0x20`) and covers #2–21. `$22ba&0x01` has no corresponding B-trigger tile in this room \u2014 it likely controls an object (such as the river lift/ferry in [0x07]) rather than a sniff spot here. // TODO: confirm `$22ba&0x01` owner across nearby rooms.
- **Double-use of persistence flags**: Each of `$22ba`/`$22bb`/`$22bc`'s bits serves two roles: (1) gates OBJ unload in the enter script (removes the nature object when previously looted), and (2) is set/cleared by the sniff B-trigger (marks the loot as taken). This is a standard SoE nature-spot pattern.
- **Both Diamond Eyes gate**: Horace first-meet cutscene is suppressed when both Diamond Eyes (`$22d8&0x40` AND `$22d8&0x80`) are already held — Horace presumably has a different post-quest role.
- **Revealer branch**: Horace mentions Madronius only if the dog doesn't already have Revealer (`$225b&0x10`).
- **Music 0x22**: Horace's Camp theme.
- // TODO: Identify NPC 0x1b (Inn keeper) and NPC 0x45/0x32 (Horace vs. Madronius NPC IDs).
- // TODO: Confirm what OBJ 0/1 becoming state 1 means post-Aegis in camp layout.
