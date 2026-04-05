# 0x57 — Antiqua: 'mids Basement Level (Tiny)

| Field | Value |
|-------|-------|
| Room ID | 0x57 |
| Act | Antiqua (Act 2) |
| Data | `0xa7a7a2` |
| Enter script ptr | `0x9281ce` |
| Enter script addr | `0x95a8c3` |
| Step-ons | 21 |
| B-triggers | 11 |
| Music | 0x20 (normal) / 0x5a (Tiny encounter) |
| Dog sprite | Greyhound (0x06) |

---

## Overview

The lowest level of the Mammoth Mausoleum. Tiny (ENEMY::TINY, 0x46) patrols this room along a scripted path and confronts the player with a dialogue warning. Four rock walls block sections of the room; each is destroyed by pressing B while wielding a sufficiently strong Axe (WEAPON_INDEX 0x0c–0x10; three walls require ≥ AXE_2 / Bronze Axe, one requires ≥ AXE_3 / Knight Basher). Separately, Tiny's inner gate is opened via a two-character positional puzzle requiring the WindWalker machine (`$22dc&0x08`; see `docs/patterns.md` — WindWalker). Seven gourds occupy the room.

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$22dc` | 0x08 | 💎 WindWalker spell unlocked [multi-room] — gates NPC 0x3c spawn on enter |
| `$22e2` | 0x80 | ⚙️ WindWalker obstacles removed / gate levitation active [0x57] — if set: OBJ 1/2/3 hidden on enter; gates switch logic |
| `$22e3` | 0x01 | 📖 WindWalker gate opened (levitation complete) [0x57] — if set: NPC 0x3c starts at alt position; OBJ 3 not restored |
| `$22e3` | 0x02 | 📖 Rock wall 1 (OBJ 4) destroyed [0x57] — set by B-trigger #9 (WEAPON_INDEX 0x0c–0x10 / AXE_2–AXE_4) |
| `$22e3` | 0x04 | 📖 Rock wall 2 (OBJ 5) destroyed [0x57] — set by B-trigger #10 (WEAPON_INDEX 0x0c–0x10 / AXE_2–AXE_4) |
| `$22e3` | 0x08 | 📖 Rock wall 3 (OBJ 6) destroyed [0x57] — set by B-trigger #11 (WEAPON_INDEX 0x0c–0x10 / AXE_2–AXE_4) |
| `$22e3` | 0x10 | 📖 Rock wall 4 (OBJ 14) destroyed [0x57] — set by B-trigger #1 (WEAPON_INDEX 0x0e–0x10 / AXE_3–AXE_4) |
| `$22e3` | 0x20 | 📖 Tiny defeated [0x57] — gates encounter step-on and Tiny NPC spawn |
| `$22eb` | 0x20 | ⚙️ Teleporter-entry animation guard — if set: clear flag (fall-landing animation already in progress via `$238f=5`); if NOT set: teleport both to [0xc9,0x65] |
| `$22f2` | 0x10 | 📖 "Tiny and his shame must have left" message shown [0x57] |
| `$22f2` | 0x20 | 📖 "Tiny must be around…" hint message shown [0x57] |
| `$23bf` | — | ⚙️ Cleared to 0 on enter |
| `$23c5` | — | ⚙️ Written 0x0280 on enter |
| `$238d` | — | 🎵 CHANGE MUSIC register — if 0x00 on enter, play music 0x20 |
| `$238f` | — | ⚙️ Animation handshake: if 5 on enter → run fall-landing cutscene |
| `$2281` | 0x40 | 🫙 Gourd OBJ 7: Honey [0x57] (MAP REF 0x07) |
| `$2281` | 0x80 | 🫙 Gourd OBJ 8: Herbal Essence [0x57] (MAP REF 0x08) |
| `$2282` | 0x01 | 🫙 Gourd OBJ 9: Pixie Dust [0x57] (MAP REF 0x09) |
| `$2282` | 0x02 | 🫙 Gourd OBJ 10: Ethanol×3 [0x57] (MAP REF 0x0a) |
| `$2282` | 0x04 | 🫙 Gourd OBJ 11: Wings [0x57] (MAP REF 0x0b) |
| `$2282` | 0x08 | 🫙 Gourd OBJ 12: Call Beads [0x57] (MAP REF 0x0c) |
| `$2282` | 0x10 | 🫙 Gourd OBJ 13: Biscuit [0x57] (MAP REF 0x0d) |
| `$2443` | — | 🐶 Dog sprite — set to Greyhound (0x06) |
| `$2849` | — | ⚙️ WindWalker NPC entity pointer (session-local) |
| `$2851` | — | ⚙️ Tiny patrol step counter — incremented/reset by patrol tiles; session-local |
| `$2853` | — | ⚙️ Tiny NPC entity pointer — written on encounter |
| `$2839` | — | ⚙️ Gate switch 1 activated (one-time per session; resets on room exit) |
| `$283b` | — | ⚙️ Gate switch 2 activated (one-time per session; resets on room exit) |

---

## Enter Script Summary (`0x95a8c3`)

1. Set Greyhound; `$0ea2+8=0x01`, `$0eac+8=0x1797`.
2. **Fall-entry guard**: if NOT `$22eb&0x20` → teleport both to [0xc9,0x65] (default spawn);
   else → clear `$22eb&0x20`.
3. `$23c5=0x0280`.
4. **WindWalker NPC** (if `$22dc&0x08`):
   - If `$22e3&0x01` (gate opened): NPC 0x3c at [0x91,0x51].
   - Else: NPC 0x3c at [0x96,0x51] + OBJ 3 → state 0x7e; `$2849=last entity`.
5. **Rock wall OBJ restore**: OBJ 4 → 0x7e if `$22e3&0x02`; OBJ 5 → 0x7e if `$22e3&0x04`;
   OBJ 6 → 0x7e if `$22e3&0x08`; OBJ 14 → 0x7e if `$22e3&0x10`.
6. If `$22e2&0x80`: OBJ 1/2/3 → state 0x7e (WindWalker obstacles removed).
7. **Gourd unloads**: `$2281&0x40` → OBJ 7; `$2281&0x80` → OBJ 8;
   `$2282&0x01` → OBJ 9; `$2282&0x02` → OBJ 10; `$2282&0x04` → OBJ 11;
   `$2282&0x08` → OBJ 12; `$2282&0x10` → OBJ 13.
8. `$0ea2+0=0x40`, `$0eac+0=0x172b`.
9. **Enemy drops**: PRIZE1=0x0801 (rate 10); PRIZE2=0x0001 qty 65 (rate 3);
   PRIZE3=0x0802 (rate 1).
10. `$23dd=0x0064`; NPC 0x6e at 10 positions (Bellbones).
11. `$23dd=0xffff`; NPC 0x3a at 16 positions.
12. Music 0x20 + fade-in; `$23bf=0`.
13. **Landing cutscene** (if `$238f==5`): load NPC 0x20 (prop), teleport boy+dog+NPC
    to [0x5d,0x81]; animate landing (SFX 0x36 × 2, walk forward, face south,
    destroy NPC); set `$22eb|=0x20`.
14. BOY+DOG = player controlled; `$0ea2+6=0x01`, `$0eac+6=0x1887`;
    `$0ea2+4=0x01`, `$0eac+4=0x188a`; END.

---

## Step-on Scripts (21 entries)

### Exit

| # | Tile | Description |
|---|------|-------------|
| 1 | [47,46:4a,48] | **Exit → 0x64** `[0x00b8\|0x0090]`: set `$22eb\|=0x20`, `$238f=5`; fade; MAP 0x64 |

### Tiny Encounter

| # | Tile | Description |
|---|------|-------------|
| 2 | [48,35:4a,36] | **Tiny encounter**: if `$22e3&0x20` skip; stop movement, fade music, play music 0x5a, load Tiny (NPC 0x8c>>1 at [0x84,0x22]), cutscene, text: *"Tiny has found a home here. Leave Tiny and Tiny's friends alone! …Leave now, before Tiny must crush you!"*; CALL 0x959efc |

### Tiny Patrol (scripted movement)

Tiny's patrol path is driven by `$2851` (counter), `$2853` (entity pointer), and calls to
sub `0x95a8a4` (Tiny teleport). The counter increments on some tiles and resets on others.

| # | Tile | `$2851` change | Description |
|---|------|---------------|-------------|
| 3 | [3a,2a:3d,2c] | +1 | Patrol step A; CALL Tiny teleport |
| 4 | [3a,1f:3d,21] | none | Patrol step B; teleport destination depends on `$2851 < 3` |
| 5 | [45,20:48,22] | = 0 | Patrol step C; CALL Tiny teleport |
| 6 | [4c,20:4f,22] | +1 | Patrol step D; CALL Tiny teleport |
| 7 | [49,23:4c,25] | = 0 | Patrol step E; CALL Tiny teleport |
| 8 | [53,24:56,26] | = 0 | Patrol step F; CALL Tiny teleport |
| 9 | [53,2a:56,2c] | = 0 | Patrol step G; CALL Tiny teleport |
| 10 | [4e,31:51,33] | +1 | Patrol step H; CALL Tiny teleport |
| 11 | [6b,1f:6e,21] | — | Tiny teleport (no counter change) |
| 12 | [5a,1f:5d,21] | — | Tiny teleport (no counter change) |
| 13 | [61,37:64,39] | — | Tiny teleport (no counter change) |
| 14 | [22,3c:25,3e] | — | Tiny teleport (no counter change) |
| 15 | [28,24:2b,26] | — | Tiny teleport (no counter change) |
| 16 | [16,2a:19,2c] | — | Tiny teleport (no counter change) |

### WindWalker Gate Switches

| # | Tile | Description |
|---|------|-------------|
| 17 | [3d,40:3f,42] | **Gate switch 1**: if `$22e2&0x80` skip; if `$2839` not yet set → set `$2839=1`, OBJ 1 → state 0x7e; if `$22e3&0x01` AND non-player-char in hitbox → CALL "Open Tiny's gate" (`0x959de0`); write `$284d=controlled char` |
| 18 | [48,40:4a,42] | **Gate switch 2**: if `$22e2&0x80` skip; if `$283b` not yet set → set `$283b=1`, OBJ 2 → state 0x7e; if `$22e3&0x01` AND non-player-char in hitbox → CALL "Open Tiny's gate" (`0x959de0`); write `$284f=controlled char` |
| 19 | [52,40:54,42] | **Gate switch 3**: if `$22e2&0x80` OR `$22e3&0x01` → skip; else OBJ 3 → state 0x7e |

### NPC Dialogue (post-Tiny)

| # | Tile | Description |
|---|------|-------------|
| 20 | [48,25:4d,27] | **Post-defeat message**: if `$22e3&0x20` AND NOT `$22f2&0x10`: set `$22f2\|=0x10`; text: *"Tiny and his shame must have left."* |
| 21 | [4e,42:52,44] | **WindWalker hint**: if `$22dc&0x08` AND NOT `$22e3&0x20` AND NOT `$22f2&0x20`: set `$22f2\|=0x20`; text: *"Tiny must be around. This looks like one of his rocks."* |

---

## Exits

| Destination | Trigger | Coords |
|-------------|---------|--------|
| 0x64 Cave entrance | Step-on #1 | `[0x00b8\|0x0090]` |

---

## B-triggers (11 entries)

### Weapon-Gated Wall Breaks (Axe)

| # | Tile | Condition | Effect |
|---|------|-----------|--------|
| 1 | [6b,26:6e,2a] | WEAPON_INDEX 0x0e–0x10 (AXE_3–AXE_4) + NOT `$22e3&0x10` | `$22e3\|=0x10`, OBJ 14 → state 0x7e, SFX 0x58 |
| 9 | [23,37:25,3a] | WEAPON_INDEX 0x0c–0x10 (AXE_2–AXE_4) + NOT `$22e3&0x02` | `$22e3\|=0x02`, OBJ 4 → state 0x7e, SFX 0x58 |
| 10 | [64,40:66,43] | WEAPON_INDEX 0x0c–0x10 (AXE_2–AXE_4) + NOT `$22e3&0x04` | `$22e3\|=0x04`, OBJ 5 → state 0x7e, SFX 0x58 |
| 11 | [5b,2c:5d,2f] | WEAPON_INDEX 0x0c–0x10 (AXE_2–AXE_4) + NOT `$22e3&0x08` | `$22e3\|=0x08`, OBJ 6 → state 0x7e, SFX 0x58 |

### Gourds

| # | Tile | Flag | OBJ | Item | MAP REF |
|---|------|------|-----|------|---------|
| 2 | [67,36:69,38] | `$2282&0x10` | 13 | Biscuit | 0x0d |
| 3 | [2e,49:30,4b] | `$2282&0x08` | 12 | Call Beads | 0x0c |
| 4 | [2e,36:30,38] | `$2282&0x04` | 11 | Wings | 0x0b |
| 5 | [2e,2f:30,31] | `$2282&0x02` | 10 | Ethanol×3 | 0x0a |
| 6 | [2e,23:30,25] | `$2282&0x01` | 9 | Pixie Dust | 0x09 |
| 7 | [12,28:14,2a] | `$2281&0x80` | 8 | Herbal Essence | 0x08 |
| 8 | [0d,26:0f,28] | `$2281&0x40` | 7 | Honey | 0x07 |

---

## NPCs

| NPC ID | Spawn condition | Notes |
|--------|-----------------|-------|
| 0x3c | `$22dc&0x08` (WindWalker unlocked) | WindWalker entity; position depends on `$22e3&0x01` |
| 0x6e | Always | Bellbones × 10 positions |
| 0x3a | Always | Enemy × 16 positions |
| 0x20 | Enter if `$238f==5` | Teleporter prop (plays fall-landing animation on arrival from 0x64 teleporter) |
| 0x8c>>1 (0x46) | Encounter trigger step-on #2 | Tiny; script-controlled; sets `$22e3&0x20` on defeat |

---

## Notes

- **Tiny encounter**: tile [48,35:4a,36] triggers Tiny's warning cutscene. Tiny NPC is
  loaded dynamically during the encounter (entity stored in `$2853`). Tiny's kill script
  presumably sets `$22e3|=0x20`.
- **Rock wall weapon gates**: three walls (OBJs 4/5/6) require WEAPON_INDEX 0x0c–0x10 (AXE_2 / Bronze Axe or better); one wall (OBJ 14) requires 0x0e–0x10 (AXE_3 / Knight Basher or better). B-trigger comparisons are in decimal (`>= 12 && <= 16` / `>= 14 && <= 16`); these fall exclusively within the Axe tier indices — no Spear or Sword indices are in range.
- **WindWalker gate puzzle**: gate step-ons [3d,40] and [48,40] only activate when `$22e3&0x01` is set (prerequisite; what sets this flag is not visible within 0x57's own scripts — likely set by NPC 0x3c interaction or a preceding room). When active: controlled char steps on switch while non-controlled char is within a specific position bounding box → CALL `0x959de0` ("Open Tiny's gate") → `$22e2|=0x80` (levitation permanent). WindWalker NPC (0x3c) position: [0x96,0x51] before puzzle, [0x91,0x51] after (`$22e3&0x01` set).
- **`$2839`/`$283b`** are WRAM registers (not SRAM), so they reset each visit. The
  gate switch logic relies on `$22e3&0x01` for the permanent state.
- **Teleporter entry from 0x64**: the connection from [0x64] to 0x57 is a teleporter (NOT a pit or hole in the floor). Arrival via teleporter sets `$238f==5`, which triggers the fall-landing cutscene on entry. The prop NPC 0x20 is destroyed after the animation.
- **Gourd continuity**: `$2281&0x40/0x80` are the last two bits of the 0x56 gourd byte 3;
  `$2282&0x01–0x10` are 0x57's gourd byte (OBJs 9–13).
- **`$22e3&0x20`** was previously labeled "[0x4d]" in memory-map — this should be `[0x57]`.
  // MISMATCH: check [0x4d] doc to see if 0x20 is read there as Horace trigger or Tiny flag.
