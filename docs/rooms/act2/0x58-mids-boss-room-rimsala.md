# 0x58 — Antiqua: 'mids Boss Room (Rimsala)

| Field | Value |
|-------|-------|
| Room ID | 0x58 |
| Act | Antiqua (Act 2) |
| Data | `0xad8cbb` |
| Enter script ptr | `0x9281d3` |
| Enter script addr | `0x95aff3` |
| Step-ons | 5 |
| B-triggers | 0 |
| Music | 0x24 (boss) / fade-in if beaten |
| Dog sprite | — (not set in enter script) |

---

## Overview

The Rimsala boss chamber. Rimsala (NPC 0x3b) is accompanied by 6 statues
(NPC 0x5b) that can optionally be destroyed; destroying them is NOT required to
defeat Rimsala permanently.
The enter script contains a persistent battle loop: crystals periodically heal and
Rimsala resets position on hit. The Diamond Eye `$22d8&0x40` is the permanent
boss-beaten flag; on re-entry this flag skips the fight setup entirely.

---

## Memory Access

| Address | Bit | Description |
|---------|-----|-------------|
| `$22d8` | 0x40 | 💎 Diamond Eye obtained / Rimsala beaten [0x58] — gates fight setup on enter; gates altar step-on trigger |
| `$22eb` | 0x20 | ⚙️ Animation entry flag — if set: clear flag; else teleport both to [0x21,0x38] |
| `$2834` | 0x01 | ⚙️ Crystal OBJ 0 alive (entity in `$283d`) [WRAM, session-local] |
| `$2834` | 0x02 | ⚙️ Crystal OBJ 4 alive (entity in `$283f`) [WRAM, session-local] |
| `$2834` | 0x04 | ⚙️ Crystal OBJ 5 alive (entity in `$2841`) [WRAM, session-local] |
| `$2834` | 0x08 | ⚙️ Crystal OBJ 1 alive (entity in `$2843`) [WRAM, session-local] |
| `$2834` | 0x10 | ⚙️ Crystal OBJ 2 alive (entity in `$2845`) [WRAM, session-local] |
| `$2834` | 0x20 | ⚙️ Crystal OBJ 3 alive (entity in `$2847`) [WRAM, session-local] |
| `$2834` | 0x40 | ⚙️ Rimsala NPC loaded / battle active [WRAM] — set on enter; cleared by step-on |
| `$2834` | 0x80 | ⚙️ Rimsala altar triggered [WRAM] — set by step-on #2; gates battle loop hit-counter |
| `$2835` | — | ⚙️ Hit counter reset (WRAM) — counts Rimsala hits since last crystal heal |
| `$2837` | — | ⚙️ Total attack timer (WRAM) — increments per hit; resets after 18 to trigger crystal heal |
| `$2849` | — | ⚙️ WindWalker NPC link (used in `$284b = 3 + 3*$2849` to scale reset threshold) |
| `$284b` | — | ⚙️ Crystal heal reset threshold (computed from `$2849`) |
| `$23bf` | — | ⚙️ Cleared to 0 on enter |

---

## Enter Script Summary (`0x95aff3`)

1. Clear `$2835=0`, `$2837=0`.
2. **Entry guard**: if NOT `$22eb&0x20` → teleport both to [0x21,0x38] + fade-out;
   else → clear `$22eb&0x20`.
3. **If beaten** (`$22d8&0x40`): fade-in music; skip to step 9 (SKIP 184).
4. **If not beaten**: BOY+DOG stopped; play music 0x24.
5. `$2834|=0x40` (Rimsala NPC flag).
6. Load Rimsala (NPC 0x3b) at [0x22,0x0f]; set kill script 0x18a5; store in `$283b`.
7. Load summoner NPC (0x3c) at [0x22,0x05]; store in `$2839`.
8. Load 6 crystals (NPC 0x5b): scripts 0x18a8/0x18ab/0x18ae/0x18b1/0x18b4/0x18b7;
   set `$2834` bits 0x01/0x02/0x04/0x08/0x10/0x20; store in `$283d`/`$283f`/`$2841`/`$2843`/`$2845`/`$2847`.
9. BOY+DOG player controlled; `$23bf=0`; CALL 0x92de75 (cinematic).
10. Clear `$2835=0`, `$2837=0`.
11. **If beaten** → skip to END.
12. **Battle loop** (loops back to itself while not beaten):
    - Sleep 59 ticks.
    - If `$2834&0x80`: increment `$2835` + `$2837`; compute `$284b = 3 + 3*$2849`.
    - If `$2835 > $284b` AND NOT beaten: RCALL crystal reposition sub (`0x95af49`);
      reset `$2835=0`.
    - If `$2837 > 18` AND NOT beaten: RCALL crystal heal sub (`0x95ad23`); reset `$2837=0`
      (heals all dead crystals 999 HP each; restores `$2834` bits 0x01-0x20).
    - Loop (SKIP -91).
13. BOY+DOG player controlled; END.

---

## Step-on Scripts (5 entries)

| # | Tile | Script addr | Description |
|---|------|-------------|-------------|
| 1 | [1d,26:20,27] × 2 | `0x95aaeb` | **Exit → 0x06** `[0x0290\|0x01c0]`: fade-out; MAP 0x06 |
| 2 | [14,18:2a,19] | `0x95ae36` | **Rimsala altar**: if beaten OR `$2834&0x80` → skip; BOY+DOG stopped; CALL subs 0xbb–0xc0; walk both to [0x22,0x25]; face north; Rimsala casts spell 24 (power 0x4b); RCALL crystal heal sub; CALL `0x95ac57`; set `$2834\|=0x80` |
| 3 | [1c,22:21,23] | `0x95ae1d` | **Rimsala OBJ 6 toggle**: if `$2834&0x40` AND NOT beaten → OBJ 6 → state 0x7e, SFX 0x76, clear `$2834&0x40` |
| 4 | [1c,21:21,22] | `0x95ae1d` | Same script as step-on #3 |

---

## Exits

| Destination | Trigger | Coords |
|-------------|---------|--------|
| 0x06 Outside of 'mids | Step-on #1 | `[0x0290\|0x01c0]` |

---

## B-triggers

None.

---

## NPCs

| NPC ID | Role | Entity ptr |
|--------|------|-----------|
| 0x3b | Rimsala (boss) | `$283b` |
| 0x3c | Summoner NPC | `$2839` |
| 0x5b × 6 | Statues (optional targets) | `$283d`/`$283f`/`$2841`/`$2843`/`$2845`/`$2847` |

---

## Notes

- **Crystal heal mechanic**: if Rimsala is hit more than `3 + 3×$2849` times since
  last heal, all crystals teleport to new positions. If 18+ total hits, all dead crystals
  are healed for 999 HP each and their `$2834` bits are restored.
- **`$2834`** is WRAM (session-local) — shared address with 0x55's switch flags, but
  distinct per-room session; both rooms clear relevant bits on entry.
- **`$22d8&0x40`** is the permanent Diamond Eye flag. When set: skips all NPC loading,
  plays music fade-in only, loops are bypassed.
- Step-on #2 (altar trigger) can only fire once per session (`$2834&0x80` prevents replay).
