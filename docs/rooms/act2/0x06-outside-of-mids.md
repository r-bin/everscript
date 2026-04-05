# [0x06] Antiqua — Outside of 'mids

## Header

| Field | Value |
|-------|-------|
| Room ID | 0x06 |
| Act | Antiqua (Act 2) |
| Data | `0x9c8000` |
| Enter script ptr | `0x928039` → `0x96cee8` |
| Step-on table | `0x9c800f`, len=0x00a2 (27 entries) |
| B-trigger table | `0x9c80b3`, len=0x0078 (20 entries) |
| Music | 0x40 |
| Dog | Greyhound |
| `$23bf` | 0 (cleared on entry) |

## Overview

The exterior hub surrounding 'mids. Boy and dog can split: each independently enters 'mids via the bottom entry (→ 0x55) or one of three top entries (→ 0x56), tracked by `$2357` (boy) and `$2358` (dog). A two-character gear puzzle to the northwest raises platform OBJ 12 required for upper access. If the dog is freed (`$22e3&0x40`) and one Diamond Eye has been found (`$22d8&0x40`), a boy/dog reunite cutscene fires on entry.

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22c3` | 0x10–0x80 | R/W | 👃 Sniff persistence: sniff #16–#19 (OBJs 16–19) [0x06] |
| `$22c4` | 0x01–0x80 | R/W | 👃 Sniff persistence: sniff #20–#27 (OBJs 20–27) [0x06] |
| `$22c5` | 0x01–0x80 | R/W | 👃 Sniff persistence: sniff #28–#35 (OBJs 28–35) [0x06] |
| `$22d8` | 0x40 | R | 💎 Diamond Eye #1 obtained — gates reunite cutscene |
| `$22d9` | 0x08 | R | 📖 Aegis dead — SET OBJ 4–10 state=1 on entry |
| `$22e0` | 0x02 | R/W | ⚙️ Gear puzzle active |
| `$22e0` | 0x04 | R/W | ⚙️ Left gear turned |
| `$22e0` | 0x08 | R/W | ⚙️ Right gear turned |
| `$22e3` | 0x40 | R/W | 📖 Dog freed from 'mids |
| `$22e3` | 0x80 | R/W | 📖 "Dog can't go up this way" message shown |
| `$22e4` | 0x02 | R | 📖 Reunite cutscene already played (prevents replay) |
| `$22e4` | 0x04 | R/W | ⚙️ Boy blocked at north exit while dog is inside 'mids |
| `$22e4` | 0x08 | R/W | ⚙️ Dog assigned to bottom gear entry |
| `$22e4` | 0x10 | R/W | ⚙️ Boy assigned to bottom gear entry |
| `$22e4` | 0x20 | R/W | ⚙️ Dog on L gear |
| `$22e4` | 0x40 | R/W | ⚙️ Dog on R gear |
| `$22e4` | 0x80 | R/W | ⚙️ Boy on L gear |
| `$22e5` | 0x01 | R/W | ⚙️ Boy on R gear |
| `$22e5` | 0x02 | R/W | ⚙️ 'mids split state flag A |
| `$22e5` | 0x04 | R/W | ⚙️ 'mids split state flag B |
| `$22eb` | 0x20 | R/W | ⚙️ IN_ANIMATION — entry teleport guard |
| `$22ed` | 0x80 | W | ⚙️ Falling into a pit (set on pit-fall step-ons) [0x06] |
| `$2261` | 0x01 | R/W | ⚙️ Dog unavailable |
| `$2261` | 0x02 | R/W | ⚙️ Boy unavailable |
| `$2350` | — | W | ⚙️ Reset to 0 on entry |
| `$2357` | — | R/W | ⚙️ Boy's 'mids room destination (0=outside, 1=bottom 0x55, 2=top 0x56) |
| `$2358` | — | R/W | ⚙️ Dog's 'mids room destination (0=outside, 1=bottom 0x55, 2=top 0x56) |
| `$238d` | — | R | 🎵 CHANGE_MUSIC flag |
| `$23bf` | — | W | ⚙️ Cleared to 0 on entry |

## Enter Script Summary (`0x96cee8`)

1. **Entry guard**: if `$22eb&0x20`: teleport both to [0x3d,0x71] + fade; else clear flag.
2. **Dog-freed state** (`$22e3&0x40`): clear `$2357`/`$2358`; clear `$22e4&0x04`, `$22e5&0x04/0x02`; clear `$2261&0x02/0x01` (boy/dog unavailable); `$2350=0`.
3. **Enemy drops**: PRIZE1=Jewels×10 (rate 10); PRIZE2=Roots qty 70 (rate 3); PRIZE3=Money(100) (rate 1).
4. **OBJ unload persistence**: `$22c3&0x10–0x80` → unload OBJs 16–19; `$22c4&0x01–0x80` → unload OBJs 20–27; `$22c5&0x01–0x80` → unload OBJs 28–35.
5. **Post-Aegis OBJs**: if `$22d9&0x08` (Aegis dead): SET OBJ 4–10 state=1.
6. **Monster spawner** (sub `0x96cd69`):
   - Pre-Aegis: NPC 0x39 (sandworm) at 9 locations; NPC 0x23 (enemy) at 22 locations
   - Post-Aegis (additional): NPC 0x39 at 4 more locations; NPC 0x23 at 8 more
7. **Music**: if `$238d != 0`: PLAY MUSIC 0x40; fade in.
8. **Gear state sync**: if `$22e0&0x04` AND `$22e0&0x08`: SET OBJ 13 state=2 (platform raised).
9. **NPC**: LOAD NPC 0x5e at [0x94,0x76] → `$2835`; talk scripts 0x195f/0x195c.
10. **Init**: `$23bf=0`; CHANGE DOGGO = Greyhound (0x06).
11. **Boy/dog split** (if NOT `$22e3&0x40`):
    - If `$2357==1` (boy in 'mids bottom): mark boy unavailable (`$2261|=0x02`), switch to dog, teleport boy to holding pos [0x0448,0x04ea].
    - If `$2358==1` (dog in 'mids bottom): mark dog unavailable (`$2261|=0x01`), switch to boy, teleport dog to holding pos [0x0448,0x04ea].
12. **`$2350=0`**; release controlled char.
13. **Reunite cutscene** (sub `0x96cc1e`): fires if `$22e3&0x40` AND `$22d8&0x40` AND NOT `$22e4&0x02`: boy/dog walk to gate, reunite, teleport away.

## Step-on Scripts (27 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [4f,55:51,59] | `0x96c7fd` | **"Can't leave my dog!"** — if `$22e4&0x04` AND NOT `$22e3&0x40`: message; walk boy to [0x68,0x80] |
| [5a,58:5d,5a] | `0x96c755` | **EXIT → 0x64** (Cave entrance) at [0x00a8,0x0118]; clears `$22e4&0x10/0x08`, `$22e0&0x02` |
| [5f,53:61,55] | `0x96c83b` | **PIT-FALL → 0x2f** (Horace's Camp) at [0x0198,0x0140]; sets `$22ed\|=0x80` |
| [61,4d:62,4e] | `0x96c83b` | PIT-FALL → 0x2f (dup) |
| [61,4f:64,4e] | `0x96c83b` | PIT-FALL → 0x2f (dup) |
| [34,4b:38,4c] | `0x96cea6` | **"Dog can't go up"** — if player=boy AND NOT `$22e3&0x80`: set `$22e3\|=0x80`; show message "It's much too steep for you Buddy." |
| [43,32:44,33] | `0x96cb7f` | **R gear step-on** — if NOT `$22e0&0x08` AND `$22e3&0x40`: `$22e0\|=0x08`; assign R gear roles; OBJ 15 state=1; if `$22e0&0x04`: both gears ready |
| [3e,32:3f,33] | `0x96cb14` | **L gear step-on** — if NOT `$22e0&0x04` AND `$22e3&0x40`: `$22e0\|=0x04`; assign L gear roles; OBJ 14 state=1; if `$22e0&0x08`: both gears ready |
| [3b,4d:3c,4e] | `0x96cabd` | **Gear release (bottom)** — toggle OBJ 12 based on `$22e4&0x08/0x10` and `$22e0&0x02`; adjust `$2358` |
| [3a,4c:3b,4e] | `0x96cabd` | Gear release (bottom, dup) |
| [5f,4e:65,4f] | `0x96c83b` | PIT-FALL → 0x2f (dup) |
| [63,51:65,53] | `0x96c83b` | PIT-FALL → 0x2f (dup) |
| [5f,4f:61,51] | `0x96c83b` | PIT-FALL → 0x2f (dup) |
| [61,53:63,55] | `0x96c83b` | PIT-FALL → 0x2f (dup) |
| [63,53:64,54] | `0x96c83b` | PIT-FALL → 0x2f (dup) |
| [67,4b:68,54] | `0x96c73f` | **EXIT east → 0x05** (Between 'Mids & Halls) at [0x0020,0x0388]; clears `$22e4&0x10/0x08`, `$22e0&0x02` |
| [3d,4c:3f,4d] | `0x96c781` | **ENTER 'mids bottom → 0x55** — dog: `$2358=1`; boy: `$2357=1` → CHANGE MAP 0x55 [0x0450,0x0480] |
| [3a,3d:3c,3e] | `0x96c7cb` | **ENTER 'mids top-L → 0x56** — dog: `$2358=2`; boy: `$2357=2` → CHANGE MAP 0x56 [0x02a0,0x0380] |
| [46,3d:48,3e] | `0x96c7b2` | **ENTER 'mids top-R → 0x56** — dog/boy → CHANGE MAP 0x56 [0x03a0,0x0380] |
| [46,2e:47,30] | `0x96c7e4` | **ENTER 'mids top-alt → 0x56** — call global 0x1c → CHANGE MAP 0x56 [0x0460,0x0240] |
| [3b,4c:3c,4d] | `0x96ca81` | **Gear puzzle start** — if NOT `$22e0&0x02` AND NOT (`$22e3&0x40` AND `$22d8&0x40`): `$22e0\|=0x02`; assign gear entry roles; OBJ 12 state=2 |
| [63,4d:64,4e] | `0x96c83b` | PIT-FALL → 0x2f (dup) |
| [3d,32:3e,34] | `0x96cb43` | **R gear exit** — if released from R gear: clear `$22e4&0x20/0x40/0x80`; OBJ 14 state=0 |
| [3e,33:40,34] | `0x96cb43` | R gear exit (dup) |
| [44,32:45,34] | `0x96cbae` | **L gear exit** — if released from L gear: clear `$22e4&0x40`, `$22e5&0x01`; OBJ 15 state=0 |
| [42,33:44,34] | `0x96cbae` | L gear exit (dup) |
| [48,17:4e,18] | `0x96c76b` | **EXIT north → 0x2f** (Horace's Camp) at [0x02a8,0x0370]; clears `$22e4&0x10/0x08`, `$22e0&0x02` |

## Exits

| Destination | Trigger | Player Spawn |
|-------------|---------|--------------|
| 0x64 Cave entrance under 'mids | Step-on [5a,58:5d,5a] | [0x00a8, 0x0118] |
| 0x05 Between 'Mids and Halls | Step-on [67,4b:68,54] | [0x0020, 0x0388] |
| 0x2f Horace's Camp (north) | Step-on [48,17:4e,18] | [0x02a8, 0x0370] |
| 0x2f Horace's Camp (pit-fall) | Step-on [5f,53:61,55] + 8 dup tiles | [0x0198, 0x0140] |
| 0x55 'mids bottom | Step-on [3d,4c:3f,4d] | [0x0450, 0x0480] |
| 0x56 'mids top | Step-on [3a,3d:3c,3e] | [0x02a0, 0x0380] |
| 0x56 'mids top | Step-on [46,3d:48,3e] | [0x03a0, 0x0380] |
| 0x56 'mids top | Step-on [46,2e:47,30] | [0x0460, 0x0240] |

## B-Triggers (20 entries)

| B# | Tile | Flag | Item | MAP REF |
|----|------|------|------|---------|
| 1 | [65,37:66,38] | `$22c3&0x10` | 👃 Sniffed Wax (#16) [0x06] (0x10) | 0x0010 |
| 2 | [4e,1b:4f,1c] | `$22c3&0x20` | 👃 Sniffed Wax (#17) [0x06] (0x20) | 0x0011 |
| 3 | [47,19:48,1a] | `$22c3&0x40` | 👃 Sniffed Wax (#18) [0x06] (0x40) | 0x0012 |
| 4 | [1e,4b:1f,4c] | `$22c3&0x80` | 👃 Sniffed Wax (#19) [0x06] (0x80) | 0x0013 |
| 5 | [39,64:3a,65] | `$22c4&0x01` | 👃 Sniffed Ash (#20) [0x06] (0x01) | 0x0014 |
| 6 | [3f,4f:40,50] | `$22c4&0x02` | 👃 Sniffed Ash (#21) [0x06] (0x02) | 0x0015 |
| 7 | [45,2c:46,2d] | `$22c4&0x04` | 👃 Sniffed Bone (#22) [0x06] (0x04) | 0x0016 |
| 8 | [48,3d:49,3e] | `$22c4&0x08` | 👃 Sniffed Bone (#23) [0x06] (0x08) | 0x0017 |
| 9 | [5f,63:60,64] | `$22c4&0x10` | 👃 Sniffed Bone (#24) [0x06] (0x10) | 0x0018 |
| 10 | [46,64:47,65] | `$22c4&0x20` | 👃 Sniffed Brimstone (#25) [0x06] (0x20) | 0x0019 |
| 11 | [21,5e:22,5f] | `$22c4&0x40` | 👃 Sniffed Brimstone (#26) [0x06] (0x40) | 0x001a |
| 12 | [1d,2b:1e,2c] | `$22c4&0x80` | 👃 Sniffed Brimstone (#27) [0x06] (0x80) | 0x001b |
| 13 | [55,1c:56,1d] | `$22c5&0x01` | 👃 Sniffed Brimstone (#28) [0x06] (0x01) | 0x001c |
| 14 | [52,65:53,66] | `$22c5&0x02` | 👃 Sniffed Water (#29) [0x06] (0x02) | 0x001d |
| 15 | [57,43:58,44] | `$22c5&0x04` | 👃 Sniffed Limestone (#30) [0x06] (0x04) | 0x001e |
| 16 | [35,34:36,35] | `$22c5&0x08` | 👃 Sniffed Limestone (#31) [0x06] (0x08) | 0x001f |
| 17 | [1c,39:1d,3a] | `$22c5&0x10` | 👃 Sniffed Roots (#32) [0x06] (0x10) | 0x0020 |
| 18 | [1f,21:20,22] | `$22c5&0x20` | 👃 Sniffed Roots (#33) [0x06] (0x20) | 0x0021 |
| 19 | [37,1a:38,1b] | `$22c5&0x40` | 👃 Sniffed Roots (#34) [0x06] (0x40) | 0x0022 |
| 20 | [63,2c:64,2d] | `$22c5&0x80` | 👃 Sniffed Vinegar (#35) [0x06] (0x80) | 0x0023 |

## NPCs

| NPC | Type | Load Condition | Pos | Notes |
|-----|------|----------------|-----|-------|
| NPC 0x5e | Unknown | Always (enter script) | [0x94, 0x76] | Stored at `$2835`; talk scripts 0x195f/0x195c |
| NPC 0x39 | Sandworm | Enter script spawner | Multiple | 9 pre-Aegis + 4 post-Aegis locations |
| NPC 0x23 | Enemy | Enter script spawner | Multiple | 22 pre-Aegis + 8 post-Aegis locations |

## Notes

- **Boy/dog split mechanic**: `$2357`=boy's 'mids room (0=outside, 1=bottom, 2=top); `$2358`=dog's. On entry, if either ≠0, that character is teleported to a holding position [0x0448,0x04ea] and marked unavailable, preventing control until they exit 'mids.
- **Gear puzzle**: `$22e0&0x02`=puzzle active (gated — won't start if dog is freed and Diamond Eye obtained). OBJ 12=moving platform, OBJ 14=L gear, OBJ 15=R gear. Both characters must step on separate gear tiles simultaneously. Once both gears turned (`$22e0&0x04` AND `$22e0&0x08`), platform rises.
- **Post-Aegis** (`$22d9&0x08`): OBJ 4–10 set state=1 (likely removes obstacles or opens shortcuts).
- **Reunite cutscene** (`0x96cc1e`): fires once when dog freed + Diamond Eye found + NOT already played (`$22e4&0x02`). Characters walk through the north gate together and teleport.
- **`$23bf=0`** on entry (unlike most rooms which set 1).
- **`$22c3` bits 0x01–0x08** (sniffs #12–#15): used by another room — not [0x06].
