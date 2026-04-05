# 0x2b — Antiqua: Outside of Halls

| Field | Value |
|-------|-------|
| Room ID | 0x2b |
| Act | Antiqua (Act 2) |
| Data | `0xa7ce91` |
| Enter script ptr | `0x9280f2` |
| Enter script addr | `0x95e506` |
| Step-ons | 2 |
| B-triggers | 17 |
| Music | 0x68 |
| Dog sprite | Greyhound (0x06) |

---

## Overview

The outdoor area in front of the Halls of Collosia. Two exits — one north to the
Halls main room (0x29) and one south-west to the area between 'mids and halls
(0x05). Sixteen sniff spots (ingredients) scattered across the map; no gourds.
Two enemy types spawn.

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$22b8` | 0x02 | 👃 Sniffed Brimstone (#0) [0x2b] (OBJ 0, MAP REF 0x00) |
| `$22b8` | 0x04 | 👃 Sniffed Brimstone (#1) [0x2b] (OBJ 1, MAP REF 0x01) |
| `$22b8` | 0x08 | 👃 Sniffed Brimstone×3 (#2) [0x2b] (OBJ 2, MAP REF 0x02) |
| `$22b8` | 0x10 | 👃 Sniffed Brimstone×2 (#3) [0x2b] (OBJ 3, MAP REF 0x03) |
| `$22b8` | 0x20 | 👃 Sniffed Limestone (#4) [0x2b] (OBJ 4, MAP REF 0x04) |
| `$22b8` | 0x40 | 👃 Sniffed Limestone×2 (#5) [0x2b] (OBJ 5, MAP REF 0x05) |
| `$22b8` | 0x80 | 👃 Sniffed Limestone×3 (#6) [0x2b] (OBJ 6, MAP REF 0x06) |
| `$22b9` | 0x01 | 👃 Sniffed Bone×2 (#7) [0x2b] (OBJ 7, MAP REF 0x07) |
| `$22b9` | 0x02 | 👃 Sniffed Bone×2 (#8) [0x2b] (OBJ 8, MAP REF 0x08) |
| `$22b9` | 0x04 | 👃 Sniffed Bone×2 (#9) [0x2b] (OBJ 9, MAP REF 0x09) |
| `$22b9` | 0x08 | 👃 Sniffed Ethanol×2 (#10) [0x2b] (OBJ 10, MAP REF 0x0a) |
| `$22b9` | 0x10 | 👃 Sniffed Ethanol (#11) [0x2b] (OBJ 11, MAP REF 0x0b) |
| `$22b9` | 0x20 | 👃 Sniffed Ethanol×4 (#12) [0x2b] (OBJ 12, MAP REF 0x0c) |
| `$22b9` | 0x40 | 👃 Sniffed Ash (#13) [0x2b] (OBJ 13, MAP REF 0x0d) |
| `$22b9` | 0x80 | 👃 Sniffed Ash×3 (#14) [0x2b] (OBJ 14, MAP REF 0x0e) |
| `$22ba` | 0x01 | 👃 Sniffed Ash (#15) [0x2b] (OBJ 15, MAP REF 0x0f) |
| `$22eb` | 0x20 | ⚙️ Animation entry flag — cleared on enter |
| `$23bf` | — | ⚙️ Cleared to 0 on enter |
| `$238d` | — | 🎵 CHANGE MUSIC register — if 0x00, play music 0x68 |
| `$2443` | — | 🐶 Dog sprite — set to Greyhound (0x06) |

---

## Enter Script Summary (`0x95e506`)

1. Set Greyhound.
2. **Entry guard**: if NOT `$22eb&0x20` → teleport both to [0x43,0x39] + fade-out;
   else → clear `$22eb&0x20`.
3. **Sniff spot OBJ unloads**: `$22b8&0x02`→OBJ 0 through `$22b9&0x80`→OBJ 14,
   and `$22ba&0x01`→OBJ 15.
4. `$0ea2+0=0x40`, `$0eac+0=0x172b`.
5. **Enemy drops**: PRIZE1=0x0801 (rate 10); PRIZE2=0x0001 qty 65 (rate 3);
   PRIZE3=0x020f (rate 1). // TODO: identify item 0x020f
6. NPC 0x28 × 6 positions (enemy, `$2433=1`).
7. NPC 0x23 × 4 positions (enemy, `$2433=5/7/7/3`).
8. Music 0x68 + fade-in; `$23bf=0`; CALL 0x92de75; END.

---

## Step-on Scripts (2 entries)

| # | Tile | Script addr | Description |
|---|------|-------------|-------------|
| 1 | [1e,1f:27,21] | `0x95e330` | **Exit → 0x05** `[0x0168\|0x0008]`: fade-out; MAP 0x05 "Between 'mids and halls" |
| 2 | [1f,01:23,03] | `0x95e326` | **Enter → 0x29** `[0x0148\|0x0458]`: fade-out; MAP 0x29 "Halls main room" |

---

## Exits

| Destination | Trigger | Coords |
|-------------|---------|--------|
| 0x05 Between 'mids and halls | Step-on #1 | `[0x0168\|0x0008]` |
| 0x29 Halls main room | Step-on #2 | `[0x0148\|0x0458]` |

---

## B-triggers (17 entries): Sniff Spots

| # | Tile | Flag | Item | MAP REF |
|---|------|------|------|---------|
| 1 | [07,0c:08,0d] | `$22b8&0x02` | Brimstone×2 | 0x00 |
| 2 | [2d,06:2e,07] × 2 | `$22b8&0x04` | Brimstone | 0x01 |
| 3 | [09,1e:0a,1f] | `$22b8&0x08` | Brimstone×3 | 0x02 |
| 4 | [33,0b:34,0c] | `$22b8&0x10` | Brimstone×2 | 0x03 |
| 5 | [0e,04:0f,05] | `$22b8&0x20` | Limestone | 0x04 |
| 6 | [3e,01:3f,02] | `$22b8&0x40` | Limestone×2 | 0x05 |
| 7 | [02,06:03,07] | `$22b8&0x80` | Limestone×3 | 0x06 |
| 8 | [1c,1f:1d,20] | `$22b9&0x01` | Bone×2 | 0x07 |
| 9 | [38,20:39,21] | `$22b9&0x02` | Bone×2 | 0x08 |
| 10 | [24,0d:25,0e] | `$22b9&0x04` | Bone×2 | 0x09 |
| 11 | [1d,12:1e,13] | `$22b9&0x08` | Ethanol×2 | 0x0a |
| 12 | [29,1d:2a,1e] | `$22b9&0x10` | Ethanol | 0x0b |
| 13 | [43,18:44,19] | `$22b9&0x20` | Ethanol×4 | 0x0c |
| 14 | [19,0b:1a,0c] | `$22b9&0x40` | Ash | 0x0d |
| 15 | [28,13:29,14] | `$22b9&0x80` | Ash×3 | 0x0e |
| 16 | [37,0c:38,0d] | `$22ba&0x01` | Ash | 0x0f |

---

## NPCs

| NPC ID | Count | Notes |
|--------|-------|-------|
| 0x28 | 6 positions | Enemy spawner (`$2433=1`) |
| 0x23 | 4 positions | Enemy spawner (`$2433=5/7/7/3`) |

---

## Notes

- **No gourds**: all B-triggers use `Loot nature?` (sub 0x39), not `Loot gourd?` (0x3a).
- **`$22b8&0x01`** is not used by this room's sniff spots; purpose unknown.
- **Sniff address range**: `$22b8&0x02` to `$22ba&0x01` = 16 spots (#0–#15). The OBJ
  unload table in the enter script matches bit order exactly.
- **`$22b8`** is also used as Halls area gourd byte: `$22b8&0x01` may be mapped to another
  room — check [0x29] and other halls rooms. // TODO: identify $22b8&0x01
