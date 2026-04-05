# [0x28] Antiqua — Halls Collapsing Bridge

| Field | Value |
|-------|-------|
| Room ID | 0x28 |
| Name | Antiqua - Halls Collapsing Bridge |
| Act | Act 2 — Antiqua |
| Data offset | `0xa1a38f` |
| Enter script | `0x9280e3` → `0x97aeba` |
| Step-ons | 32 |
| B-triggers | 2 |
| Music | 0x66 |

---

## Overview

Long east-west bridge room connecting the Halls main room (0x29) to the south. The entire central bridge section is a one-way collapse trap: fifteen sequential platform tiles (OBJs 17–31) each require two separate crossings to collapse — first pass sets the instability bit, second pass triggers a fall sequence that slides the player down then teleports them back to the safe platform at [43,4c]. After the fall, all bridge bits clear and the bridge resets. A secret passage (OBJ 13) opens via a one-time south step-on. A Honey×2 gourd (OBJ 0x20) sits in the west alcove.

---

## Memory Access

| Address | Bit | OBJ | Type | Item / Effect |
|---------|-----|-----|------|---------------|
| `$228a` | 0x80 | 13 | 📖 | Secret door activated [0x28] |
| `$2284` | 0x01 | 0x20 | 🧪 | Honey×2 gourd looted [0x28] |
| `$2836` | 0x04 | 17 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 17) — session-local [0x28] |
| `$2836` | 0x08 | 18 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 18) — session-local [0x28] |
| `$2836` | 0x10 | 19 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 19) — session-local [0x28] |
| `$2836` | 0x20 | 20 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 20) — session-local [0x28] |
| `$2836` | 0x40 | 21 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 21) — session-local [0x28] |
| `$2836` | 0x80 | 22 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 22) — session-local [0x28] |
| `$2837` | 0x01 | 23 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 23) — session-local [0x28] |
| `$2837` | 0x02 | 24 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 24) — session-local [0x28] |
| `$2837` | 0x04 | 25 | ⚙️ | Bridge trap 2nd-hit flag (OBJ 25) — session-local [0x28] |
| `$2838` | 0x02 | — | ⚙️ | Fall-sub re-entry guard (prevents double-trigger) [0x28] |
| `$2838` | 0x04 | — | ⚙️ | Dog-close active flag [0x28] |
| `$2838` | 0x10 | — | 🎥 | Camera wide-view activated [0x28] |

---

## Enter Script Summary

1. **Greyhound** animation guard (`$22eb&0x20`); teleport fallback to [0x21, 0x95] if in animation.
2. **OBJ 13** unloaded if `$228a&0x80` (secret door already opened).
3. **OBJ 0x20** unloaded if `$2284&0x01` (Honey gourd already looted).
4. **Drop table**: Nectar 10/50 · Coins 3/50 · Wax 1/50.
5. **NPC spawners**: NPC 0x71 ×5 (gargoyles), NPC 0x7c ×14, NPC 0x76 ×2 (manual at [6f,9d] and [69,9b]).
6. **Music** 0x66; write `$23bf = 0`; CALL `0x92de75`.

---

## Step-on Scripts

| # | Tile | Condition | Effect |
|---|------|-----------|--------|
| 1 | `[38,1b:3b,1c]` | — | North entrance cutscene: face south, OBJ 3 states 2→0 (gate opens), `$22f3\|=0x80`, `$22eb\|=0x40`, CHANGE MAP **0x29** |
| 2 | `[24,3a:28,3b]` | `$2834&0x02` | OBJ 14 states 3→0 (west bridge section collapses) |
| 3 | `[24,2a:28,2b]` | `$2834&0x01` | OBJ 2 states 2→0 (east gate); spawns 2× NPC 0x70 (kill script 0x199b) |
| 4 | `[30,52:32,54]` | — (one-time `$228a&0x80`) | `$228a\|=0x80`; OBJ 13 → state 1 (secret door opens, SFX) |
| 5 | `[44,35:46,37]` | — | OBJ 5 → 0x7e; OBJ 15 states 1→3 (bridge section crumbles, expands) |
| 6 | `[44,42:46,44]` | — | OBJ 9 → 0x7e |
| 7 | `[4e,42:50,44]` | — | OBJ 10 → 0x7e |
| 8 | `[44,38:46,3a]` | — | OBJ 7 → 0x7e |
| 9 | `[4e,38:50,3a]` | — | OBJ 8 → 0x7e |
| 10 | `[48,35:4a,37]` | — | OBJ 6 → 0x7e |
| 11 | `[38,51:3c,53]` | — (one-time `$2834&0x04`) | OBJ 16 states 1→3; OBJs 11/12 → 0x7e (east passage gate + debris) |
| 12 | `[12,44:13,4a]` | dog-close ON | Dog-close OFF: clear `$2838&0x04`, `$23c3 = 0` |
| 13 | `[13,45:14,4a]` | dog-close OFF | Dog-close ON: `$2838\|=0x04`, `$23c3 = 1` |
| 14 | `[36,45:37,4a]` | dog-close OFF | Dog-close ON (2nd entry): `$2838\|=0x04`, `$23c3 = 1` |
| 15 | `[37,44:38,4a]` | dog-close ON | Dog-close OFF (2nd exit): clear `$2838&0x04`, `$23c3 = 0` |
| 16–30 | `[16,45:18,4a]`–`[32,45:34,4a]` | per-OBJ bit | **Bridge trap series** (OBJs 17–31) — see below |
| 31 | `[0d,41:0e,43]` | one-time `$2838&0x10` | Camera wide-view: `$2838\|=0x10`; writes camera scroll params (`$240f=$2411=0x80`, `$2413=0x68`, `$2415=0x78`) |
| 32 | `[0e,41:0f,43]` | `$2838&0x10` | Camera reset: clear `$2838&0x10`; restore scroll params (`$240f=$2411=0x48`, `$2413=0x68`, `$2415=0x38`) |

### Bridge Trap Series (tiles 16–30)

Each tile in the 15-tile bridge trap corridor (`[16,45:18,4a]` through `[32,45:34,4a]`) follows this pattern:

- **1st entry** (gate bit NOT set): Set the OBJ's `$2834`/`$2835` instability bit; wait 9 ticks; OBJ → state 1 (shake), SFX 0x54; OBJ → state 0x7e (crumble); set `$2836`/`$2837` 2nd-hit flag.
- **2nd entry** (2nd-hit flag set, re-entry guard `$2838&0x02` clear): Execute **big fall sub** — slide controlled char down (y += 4 each frame until y > 0x470); teleport boy+dog to [43,4c]; player-controlled; SFX 0x76 ×3, OBJ 2 states 1→2→3; `$2834\|=0x01`; then **full reset**: `$23c3=0`, OBJs 17–31 → state 0, clear ALL bits in `$2834`, `$2835`, `$2836`, `$2837`, `$2838&0xfd`.

| Tile | OBJ | Instability bit | 2nd-hit flag |
|------|-----|-----------------|--------------|
| `[16,45:18,4a]` | 17 | `$2834&0x08` | `$2836\|=0x04` |
| `[18,45:1a,4a]` | 18 | `$2834&0x10` | `$2836\|=0x08` |
| `[1a,45:1c,4a]` | 19 | `$2834&0x20` | `$2836\|=0x10` |
| `[1c,45:1e,4a]` | 20 | `$2834&0x40` | `$2836\|=0x20` |
| `[1e,45:20,4a]` | 21 | `$2834&0x80` | `$2836\|=0x40` |
| `[20,45:22,4a]` | 22 | `$2835&0x01` | `$2836\|=0x80` |
| `[22,45:24,4a]` | 23 | `$2835&0x02` | `$2837\|=0x01` |
| `[24,45:26,4a]` | 24 | `$2835&0x04` | `$2837\|=0x02` |
| `[26,45:28,4a]` | 25 | `$2835&0x08` | `$2837\|=0x04` |
| `[28,45:2a,4a]` | 26 | `$2835&0x10` | `$2837\|=0x08` |
| `[2a,45:2c,4a]` | 27 | `$2835&0x20` | `$2837\|=0x10` |
| `[2c,45:2e,4a]` | 28 | `$2835&0x40` | `$2837\|=0x20` |
| `[2e,45:30,4a]` | 29 | `$2835&0x80` | `$2837\|=0x40` |
| `[30,45:32,4a]` | 30 | (unknown) | `$2837\|=0x80` |
| `[32,45:34,4a]` | 31 | (unknown) | (unknown) |

> **TODO:** Instability bits for OBJs 30–31 not directly confirmed; pattern extrapolation from OBJs 17–29 gives `$2836&0x01` / `$2836&0x02` as candidates.

---

## Exits

| Tile | Destination | Conditions |
|------|-------------|------------|
| `[38,1b:3b,1c]` | **0x29** Halls main room | Sets `$22f3\|=0x80`, `$22eb\|=0x40` |

---

## B-Triggers

| # | Tile | Flag | Item / Effect |
|---|------|------|---------------|
| 1 | `[3b,1e:3c,20]` | — (no flag) | SFX 0x00; OBJ 4 → 0x7e; OBJ 3 states 1→2→3 (north gate closes permanently) |
| 2 | `[02,3f:04,41]` | `$2284&0x01` | 🧪 **Honey×2** (MAP REF 0x0020 = OBJ 0x20) |

---

## NPCs

| Spawner | Count | Notes |
|---------|-------|-------|
| NPC 0x71 | 5 | Gargoyles (random spawn) |
| NPC 0x7c | 14 | Basic enemy spawner |
| NPC 0x76 | 2 | Manual placement at [6f,9d] and [69,9b] |
| NPC 0x70 | 2 | Spawned when `$2834&0x01` gate tile triggers; kill script 0x199b |

---

## Notes

- The **bridge trap** is purely session-local: the full reset sub clears all `$2834`–`$2838` bits after a fall, so the bridge is always intact on re-entry.
- The **dog-close tiles** at [12,44:13,4a] / [0d,41:0e,43] area prevent the dog from running ahead over the collapsing bridge sections.
- **B-trigger #1** (`[3b,1e:3c,20]`) has no persistence flag — it fires every visit. It animates OBJ 3 (north gate) into states 1→2→3, which closes it. This is the gate-shut sequence that plays after leaving via the north exit (the gate-open is step-on #1 at `[38,1b:3b,1c]`).
- `$2836`/`$2837` bits 0x04–0x80/0x01–0x?? are the **"hot" bridge bits**: set on first crossing, trigger fall on second. They all clear in the full reset sub at `0x97ab84`.
