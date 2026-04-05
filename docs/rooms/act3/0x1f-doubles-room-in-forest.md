# 0x1f — Gothica: Doubles Room in Forest

| Field | Value |
|-------|-------|
| Room ID | 0x1f |
| Act | Gothica (Act 3) |
| Data | `0xa8d4ca` |
| Enter script ptr | `0x9280b6` |
| Enter script addr | `0x99ccdb` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | MUSIC.BOSS_MINI (0x5a) alive / MUSIC.WIND_AMBIENT_BIRDS (0x68) dead |
| Dog sprite | Poodle (0x08) |

---

## Overview

A forest clearing containing the "Doubles" — six ENEMY::OWL_BLACK (Greeble,
NPC 0x4f) enemies that act as a mini-boss encounter. When all are defeated
(`$22df&0x01` set), OBJs 1–7 are replaced, and NPC VILLAGER_3_2 (0x51 —
"Legendary boy" / dark-hair NPC, likely a save-related character) appears
at [0x5b,0x1d] with talk script 0x1a6a.

Both exits lead into the Dark Forest (0x22) via fade-out transitions, writing
different `$24f7` entry tokens to determine the starting cell of the maze.

No gourds, no sniff spots, no B-triggers.

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$22df` | 0x01 | 📖 Doubles dead [multi-room] — gates encounter, OBJ state, post-battle NPC |
| `$22eb` | 0x20 | ⚙️ Animation-skip guard (standard pattern) |
| `$22ee` | 0x01 | ⚙️ Entry-from-lab flag — if set on enter: clear flag, teleport to `[$24ab-24,$24af]` and `[$24ab-24,$24af+16]` (specific starting pos) // TODO: confirm origin room that sets this flag |
| `$238d` | — | 🎵 CHANGE MUSIC register |
| `$24f7` | — | ⚙️ Dark-forest entry token — written by step-ons before CHANGE MAP 0x22 |
| `$2834` | — | ⚙️ Greeble entity pointer #1 (session-local) |
| `$2836` | — | ⚙️ Greeble entity pointer #2 (session-local) |
| `$2838` | — | ⚙️ Greeble entity pointer #3 (session-local) |
| `$283a` | — | ⚙️ Greeble entity pointer #4 (session-local) |
| `$283c` | — | ⚙️ Greeble entity pointer #5 (session-local) |
| `$283e` | — | ⚙️ Greeble entity pointer #6 (session-local) |

---

## Enter Script Summary (`0x99ccdb`)

1. Set Poodle dog (`$2443=0x08`).
2. **Animation guard**: if NOT `$22eb&0x20` → teleport both to [0x05,0x20]; fade-out music.
3. **Lab entry**: if `$22ee&0x01`: clear flag; write `$24ab=0x02d8, $24af=0x00e8`;
   teleport boy to [$24ab-24, $24af] and dog to [$24ab-24, $24af+16].
4. If NOT `$22df&0x01` (**Doubles alive**):
   - Music BOSS_MINI (0x5a).
   - Load OWL_BLACK (0x4f) × 6 at positions [0x0b,0x1b], [0x11,0x21], [0x19,0x1d],
     [0x17,0x1d], [0x15,0x1b], [0x19,0x1f]; save entity pointers to `$2834–$283e`.
   - Run "Doubles room enter part [1]" intro cutscene (`0x99c3ff`): stops movement,
     hides OBJ 0, calls 6 sub-scripts (0x99ca9e–0x99cbde), camera scroll, fade-in.
5. Else (**Doubles dead**):
   - Music WIND_AMBIENT_BIRDS (0x68).
   - OBJ 1–7 → state 0x7e.
   - Load VILLAGER_3_2 (0x51) at [0x5b,0x1d] with talk script 0x1a6a.
6. CALL `0x92de75`; END.

---

## Step-on Scripts (2 entries)

| # | Tile | Description |
|---|------|-------------|
| 1 | [32,0c:34,17] | **Exit → 0x22** Dark Forest; writes `$24f7=0x00a9`; fade-out |
| 2 | [02,0f:04,16] | **Exit → 0x22** Dark Forest; writes `$24f7=0x0077`; fade-out |

---

## NPCs

| NPC ID | Spawn condition | Notes |
|--------|-----------------|-------|
| ENEMY::OWL_BLACK (0x4f) | NOT `$22df&0x01` | "Greeble" × 6; kill script presumably sets `$22df\|=0x01` |
| VILLAGER_3_2 (0x51) | `$22df&0x01` | Appears after defeat; talk script 0x1a6a // TODO: verify what 0x51 says/does |

---

## Notes

- The "Doubles room enter part [1]" intro cutscene (`0x99c3ff`) calls `0x99c53e`
  ("Doubles room enter part [2]") mid-way; full intro contents not read in this
  session. `// TODO: read 0x99c53e`.
- The two step-ons set different `$24f7` values (0xa9 vs 0x77), placing the player
  in different starting cells of the Dark Forest (0x22) depending on which exit is used.
- `$22ee&0x01` is labeled "unknown intro/outro? flag in prof. lab" in the dump;
  it may be set in room 0x46 (Professor's lab) when transitioning to Act 3.
