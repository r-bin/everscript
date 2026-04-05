# 0x17 — Prehistoria: Bug Room 2

**ROM address:** `0x9ffe43`  
**Data address:** `0xac9955`  
**Enter script:** `0x92808e` → `0x93c5e0`  
**Act:** 1 — Prehistoria

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on zones | 8 (2 map exits + 6 bug-legs exits to Bugmuck exterior) |
| B-trigger zones | 12 (12 sniff spots, no gourds) |
| Gourds | 0 |
| Sniff spots | 12 (Water×3, Clay×3, Roots×3, Oil×3) |
| Enemy spawners | 11× NPC `0x0e`, 1× NPC `0x0f` (static `3c` load) |
| Music | `0x14` (Bugmuck / swamp theme) |

---

## Connections

| Direction | Zone | Destination | Notes |
|-----------|------|-------------|-------|
| South (step-on) | `[1f,2e:23,30]` | `0x16` BBM @ `0x0058` | Fade-out; script `0x21` |
| North (step-on) | `[1f,04:24,06]` | `0x18` Thraxx' room @ `0x01f8` | Fade-out; script `0x26` |
| West ×3 (step-on) | `[13,11:15,13]`, `[13,1a:15,1c]`, `[13,23:15,25]` | `0x67` Bugmuck exterior @ `0x01a0`/`0x01f0`/`0x0250` | Sets `$22ec\|=0x04` (bug-legs); script `0x19` |
| East ×3 (step-on) | `[2e,11:30,13]`, `[2e,1a:30,1c]`, `[2e,23:30,25]` | `0x67` Bugmuck exterior @ `0x01a0`/`0x01f0`/`0x0250` | Sets `$22ec\|=0x04` (bug-legs); script `0x1d` |

---

## Memory Access

| Address | Bits | Category | R/W | Meaning |
|---------|------|----------|-----|---------|
| `$22eb` | `0x20` | ⚙️ | R/W | In animation — cleared on enter if set |
| `$22ec` | `0x04` | 📖 | W | Set on all exits to Bugmuck exterior — triggers bug-leg platforms in `0x67` |
| `$22a0` | `0x04` | 👃 | R/W | Sniff Water #0 |
| `$22a0` | `0x08` | 👃 | R/W | Sniff Water #1 |
| `$22a0` | `0x10` | 👃 | R/W | Sniff Water #2 |
| `$22a0` | `0x20` | 👃 | R/W | Sniff Clay #3 |
| `$22a0` | `0x40` | 👃 | R/W | Sniff Clay #4 |
| `$22a0` | `0x80` | 👃 | R/W | Sniff Clay #5 |
| `$22a1` | `0x01` | 👃 | R/W | Sniff Roots #6 |
| `$22a1` | `0x02` | 👃 | R/W | Sniff Roots #7 |
| `$22a1` | `0x04` | 👃 | R/W | Sniff Roots #8 |
| `$22a1` | `0x08` | 👃 | R/W | Sniff Oil #9 |
| `$22a1` | `0x10` | 👃 | R/W | Sniff Oil #10 |
| `$22a1` | `0x20` | 👃 | R/W | Sniff Oil #11 |
| `$2391` | — | ⚙️ | W | PRIZE (sniff content) |
| `$2395` | — | ⚙️ | W | MAP REF? |
| `$2433` | — | ⚙️ | W | Written `0x0001` then `0x000a` (spawner group) |
| `$23c1` | — | ⚙️ | W | Written `0x0001` on enter |
| `$23bf` | — | ⚙️ | W | Written `0x0000` after music |
| `$238d` | — | 🎵 | R | CHANGE MUSIC flag |
| `$23a1`–`$23a9` | — | ⚙️ | W | Enemy drops: rate 10/2/1; Petal/(`0x0001`×10)/Nectar |
| `$23e9–$23ef` | — | ⚙️ | W | Map boundaries: X=`0x0000`–`0x01d0`, Y=`0x0000`–`0x02e0` |
| `$0eac+8` | — | ⚙️ | W | Written `0x178e` (BBM wings engine register) |
| `$0eac+0` | — | ⚙️ | W | Written `0x172b` |

---

## NPCs / Enemies

| Sprite ID | Count | Spawn type | Notes |
|-----------|-------|-----------|-------|
| `0x0e` (unknown) | 11 | `c2` roaming spawner, group 1 | `// TODO: identify` |
| `0x0f` (unknown) | 1 | `3c` static load, group 10 | At `(0x31, 0x0b)`; `// TODO: identify` |

---

## Enemy Drop Table

| Slot | Rate | Item | Qty |
|------|------|------|-----|
| 1 | `0x0a` | `0x0800` (PETAL) | 1 |
| 2 | `0x02` | `0x0001` qty=10 | 10 |
| 3 | `0x01` | `0x0801` (NECTAR) | 1 |

---

## Sniff Spots

| # | Persistence | Zone | Content |
|---|-------------|------|---------|
| 0 | `$22a0` bit `0x04` | `[25,1c:26,1d]` | Water |
| 1 | `$22a0` bit `0x08` | `[1d,10:1e,11]` | Water |
| 2 | `$22a0` bit `0x10` | `[1c,08:1d,09]` | Water |
| 3 | `$22a0` bit `0x20` | `[1f,2a:20,2b]` | Clay |
| 4 | `$22a0` bit `0x40` | `[1a,25:1b,26]` | Clay |
| 5 | `$22a0` bit `0x80` | `[1d,19:1e,1a]` | Clay |
| 6 | `$22a1` bit `0x01` | `[16,1c:17,1d]` | Roots |
| 7 | `$22a1` bit `0x02` | `[24,13:25,14]` | Roots |
| 8 | `$22a1` bit `0x04` | `[25,07:26,08]` | Roots |
| 9 | `$22a1` bit `0x08` | `[22,20:23,21]` | Oil |
| 10 | `$22a1` bit `0x10` | `[18,16:19,17]` | Oil |
| 11 | `$22a1` bit `0x20` | `[24,10:25,11]` | Oil |

---

## External Scripts

| Opcode / Callee | Purpose |
|----------------|---------|
| `0x00` | Fade-out / stop music |
| `0x01` | Fade-in / start music |
| `0x19` | Prepare room change: west exit (outdoor→outdoor) |
| `0x1d` | Prepare room change: east exit (outdoor→outdoor) |
| `0x21` | Prepare room change: south exit |
| `0x26` | Prepare room change: north exit |
| `0x39` | Loot nature (sniff spot) |
| `0x92de75` | Cinematic script |

---

## Enter Script Summary

1. In-animation branch (standard); teleport both to `(0x1c, 0x55)`.
2. Write engine registers `$0eac+8=0x178e`, `$0eac+0=0x172b`.
3. Set enemy drop table: Petal/`0x0001`×10/Nectar; rates 10/2/1.
4. Unload 12 already-collected sniff spots (objs 0–11 via `$22a0`/`$22a1`).
5. Write `$23c1=0x0001`.
6. Add 11 NPC `0x0e` roaming spawners (group 1) + 1 NPC `0x0f` static at `(0x31,0x0b)` (group 10).
7. Set map boundaries.
8. If music not set: play music `0x14`, fade in.
9. Call cinematic script `0x92de75`.

---

## Notes

- **Bug-legs flag (`$22ec bit 0x04`)** is explicitly set on ALL six exits to Bugmuck exterior (0x67). This is the room that activates the giant bug platform in 0x67 — exiting through any side of this room (east or west) to the exterior puts the player on bug legs.
- **No gourds** — only sniff spots.
- **Map boundaries** written on enter constrain the camera/scroll area for this room.
- **NPC `0x0f`** appears here alone (group 10) — different group from the spawner use in 0x16 BBM. This is likely the BBM-related large creature that occupies the north part of the room.
  - `// TODO: identify NPC sprite IDs 0x0e and 0x0f`
