# 0x16 — Prehistoria: BBM

**ROM address:** `0x9ffe3f`  
**Data address:** `0xa38000`  
**Enter script:** `0x928089` → `0x93c2c2`  
**Act:** 1 — Prehistoria

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on zones | 42 (2 map exits + 16 BBM segment triggers + ~24 tube-navigation zones) |
| B-trigger zones | 24 (24 sniff spots, no gourds) |
| Gourds | 0 |
| Sniff spots | 24 (Water×2, Clay×6, Roots×4, Oil×8, Ash×4) |
| Enemy spawners | 6× NPC `0x0a`, 13× NPC `0x0e` |
| BBM segments | 16 (objs 0–15; obj 8 is special — can be in state 4 vs 0) |
| Music | `0x14` (Bugmuck / swamp theme) |

---

## Connections

| Direction | Zone | Destination | Notes |
|-----------|------|-------------|-------|
| South (step-on) | `[25,5b:29,5d]` | `0x67` Bugmuck exterior @ `0x03a8` | Script `0x21` (outdoor→outdoor) |
| North (step-on) | `[26,0d:2a,0f]` | `0x17` Bug room 2 @ `0x02d8` | Script `0x26` |

---

## Memory Access

| Address | Bits | Category | R/W | Meaning |
|---------|------|----------|-----|---------|
| `$22eb` | `0x20` | ⚙️ | R/W | In animation — cleared on enter if set |
| `$22eb` | `0x04` | ⚙️ | R | Attraction/showcase mode — triggers BBM intro walk |
| `$22dc` | `0x08` | ⚙️ | R | Unknown condition — gates BBM segment state reset on enter |
| `$22e9` | `0x04` | 📖 | R/W | BBM room visited — set on enter; used to gate segment-state initialization |
| `$2288` | `0x10` | 📖 | R/W | BBM seg 0 eaten; unloads obj 0 on enter |
| `$2288` | `0x20` | 📖 | R/W | BBM seg 1 eaten; unloads obj 1 |
| `$2288` | `0x40` | 📖 | R/W | BBM seg 2 eaten; unloads obj 2 |
| `$2288` | `0x80` | 📖 | R/W | BBM seg 3 eaten; unloads obj 3 |
| `$2289` | `0x01` | 📖 | R/W | BBM seg 4 eaten; unloads obj 4 |
| `$2289` | `0x02` | 📖 | R/W | BBM seg 5 eaten; unloads obj 5 |
| `$2289` | `0x04` | 📖 | R/W | BBM seg 6 eaten; unloads obj 6 |
| `$2289` | `0x08` | 📖 | R/W | BBM seg 7 eaten; unloads obj 7 |
| `$2289` | `0x10` | 📖 | R/W | BBM seg 8 "digested" — obj 8 set to state 4 if set, else 0 |
| `$2289` | `0x20` | 📖 | R/W | BBM seg 9 eaten; unloads obj 9 |
| `$2289` | `0x40` | 📖 | R/W | BBM seg 10 eaten; unloads obj 10 |
| `$2289` | `0x80` | 📖 | R/W | BBM seg 11 eaten; unloads obj 11 |
| `$228a` | `0x01` | 📖 | R/W | BBM seg 12 eaten; unloads obj 12 |
| `$228a` | `0x02` | 📖 | R/W | BBM seg 13 eaten; unloads obj 13; requires seg 11 eaten first |
| `$228a` | `0x04` | 📖 | R/W | BBM seg 14 eaten; unloads obj 14 |
| `$228a` | `0x08` | 📖 | R/W | BBM seg 15 eaten; unloads obj 15 |
| `$2834` | `0x01` | 📖 | R/W | BBM approach gate A (seg 2 requires this) |
| `$2834` | `0x02` | 📖 | R/W | BBM approach gate B (seg 3 requires this) |
| `$2834` | `0x04` | 📖 | R/W | BBM approach gate C (seg 7 requires this) |
| `$2835` | — | 📖 | R/W | BBM approach counter for seg 5 (requires >1 before seg moves) |
| `$229d` | `0x04` | 👃 | R/W | Sniff Water #16 |
| `$229d` | `0x08` | 👃 | R/W | Sniff Water #17 |
| `$229d` | `0x10` | 👃 | R/W | Sniff Clay #18 |
| `$229d` | `0x20` | 👃 | R/W | Sniff Clay #19 |
| `$229d` | `0x40` | 👃 | R/W | Sniff Clay #20 |
| `$229d` | `0x80` | 👃 | R/W | Sniff Clay #21 |
| `$229e` | `0x01` | 👃 | R/W | Sniff Clay #22 |
| `$229e` | `0x02` | 👃 | R/W | Sniff Clay #23 |
| `$229e` | `0x04` | 👃 | R/W | Sniff Roots #24 |
| `$229e` | `0x08` | 👃 | R/W | Sniff Roots #25 |
| `$229e` | `0x10` | 👃 | R/W | Sniff Roots #26 |
| `$229e` | `0x20` | 👃 | R/W | Sniff Roots #27 |
| `$229e` | `0x40` | 👃 | R/W | Sniff Oil #28 |
| `$229e` | `0x80` | 👃 | R/W | Sniff Oil #29 |
| `$229f` | `0x01` | 👃 | R/W | Sniff Oil #30 |
| `$229f` | `0x02` | 👃 | R/W | Sniff Oil #31 |
| `$229f` | `0x04` | 👃 | R/W | Sniff Oil #32 |
| `$229f` | `0x08` | 👃 | R/W | Sniff Oil #33 |
| `$229f` | `0x10` | 👃 | R/W | Sniff Oil #34 |
| `$229f` | `0x20` | 👃 | R/W | Sniff Oil #35 |
| `$229f` | `0x40` | 👃 | R/W | Sniff Ash #36 |
| `$229f` | `0x80` | 👃 | R/W | Sniff Ash #37 |
| `$22a0` | `0x01` | 👃 | R/W | Sniff Ash #38 |
| `$22a0` | `0x02` | 👃 | R/W | Sniff Ash #39 |
| `$2391` | — | ⚙️ | W | PRIZE (sniff content) |
| `$2395` | — | ⚙️ | W | MAP REF? |
| `$2497` | — | ⚙️ | R/W | Target X coord for tube-navigation warp |
| `$2499` | — | ⚙️ | R/W | Target Y coord for tube-navigation warp |
| `$2421` | — | ⚙️ | R | Source X (for south-exit step-ons) |
| `$2423` | — | ⚙️ | R | Source Y (for south-exit step-ons) |
| `$2433` | — | ⚙️ | W | Written `0x0001` (spawner group) |
| `$2837` | — | ⚙️ | R/W | Tube exit direction flag (`0xffff`=left, `0x0001`=right) |
| `$238d` | — | 🎵 | R | CHANGE MUSIC flag |
| `$23bf` | — | ⚙️ | W | Written `0x0000` after music |
| `$23a1`–`$23a9` | — | ⚙️ | W | Enemy drops: rate 10/2/1; Petal/(`0x0001`×10)/Nectar |
| `$0ea2+8` | — | ⚙️ | W | Written `0x0001` (BBM wings? unique to this room) |
| `$0eac+8` | — | ⚙️ | W | Written `0x178e` (BBM wings engine register) |
| `$0ea2+0` | — | ⚙️ | W | Written `0x0040` |
| `$0eac+0` | — | ⚙️ | W | Written `0x172b` |

---

## Objects

### BBM Segments

| Obj | Persistence | Trigger Zone | Walk Target (non-ctrl) | Notes |
|-----|-------------|-------------|----------------------|-------|
| 0 | `$2288` bit `0x10` | `[3a,46:3b,49]` | `(0x5a, 0x7e)` | No gate |
| 1 | `$2288` bit `0x20` | `[38,3d:39,40]` | `(0x58, 0x6d)` | No gate |
| 2 | `$2288` bit `0x40` | `[31,39:35,3a]` | `(0x4a, 0x60)` | Requires `$2834&0x01`; else sets it |
| 3 | `$2288` bit `0x80` | `[1b,45:21,46]` | `(0x1f, 0x7d)` | Requires `$2834&0x02`; else sets it |
| 4 | `$2289` bit `0x01` | `[1f,3e:20,41]` | `(0x20, 0x6f)` | No gate |
| 5 | `$2289` bit `0x02` | `[17,36:18,3a]` | `(0x11, 0x60)` | Requires `$2835 > 1`; else `$2835++` |
| 6 | `$2289` bit `0x04` | `[13,35:18,36]` | `(0x0e, 0x5d)` | No gate |
| 7 | `$2289` bit `0x08` | `[22,31:26,32]` | `(0x2c, 0x51)` | Requires `$2834&0x04`; else sets it |
| 8 | `$2289` bit `0x10` | `[31,35:35,36]` | `(0x4a, 0x5e)` | Special: state=4 (not unloaded) |
| 9 | `$2289` bit `0x20` | `[29,36:2a,3a]` | `(0x39, 0x60)` | No gate |
| 10 | `$2289` bit `0x40` | `[32,2c:35,2d]` | `(0x4a, 0x4c)` | No gate |
| 11 | `$2289` bit `0x80` | `[25,1f:2b,20]` | `(0x34, 0x2d)` | No gate |
| 12 | `$228a` bit `0x01` | `[1a,1e:1e,1f]` | `(0x1b, 0x2a)` | No gate |
| 13 | `$228a` bit `0x02` | `[1d,1a:1e,1d]` | `(0x1c, 0x27)` | Requires seg 11 eaten (`$2289&0x80`) |
| 14 | `$228a` bit `0x04` | `[26,14:2a,15]` + `[26,19:2a,1a]` | `(0x34, 0x17)` + `(0x34, 0x25)` | Two entry points |
| 15 | `$228a` bit `0x08` | `[32,16:36,17]` | `(0x4c, 0x1b)` | No gate |

When a segment trigger fires (and gate is satisfied): sets the corresponding `$2288/9/a` bit, moves the non-controlled character NPC to the walk target, plays sound `0x58`, sets obj state to 3 (loaded/digested), waits for NPC to arrive, then returns control.

Obj 8 (`$2289&0x10`) is loaded to state 4 instead of being unloaded — this represents a special "eaten but visible" state.

---

## Tube Navigation Step-ons

These step-ons warp the player between positions within the map (passing through BBM's body). They write target coords to `$2497`/`$2499` and call absolute scripts.

| Zone(s) | $2497 (X) | $2499 (Y) | $2837 | Script |
|---------|-----------|-----------|-------|--------|
| `[16,19:17,1a]`–`[15,1c:16,1d]` (×4) | `0x0078` | `0x0148` | `0xffff` | `0x93bb91` |
| `[38,19:39,1a]`–`[3a,1c:3b,1d]` (×3) + `[3a,48:3b,49]` | `0x02d0` | `0x0148` | `0x0001` | `0x93bb91` |
| `[11,24:12,25]`, `[11,25:12,27]` | `0x0030` | `0x01e8` | `0xffff` | `0x93bc03` |
| `[11,36:12,38]` | `0x0030` | `0x02f8` | `0xffff` | `0x93bc03` |
| `[11,3e:12,40]` | `0x0030` | `0x0378` | `0xffff` | `0x93bc03` |
| `[3e,3c:3f,40]` | `0x0310` | `0x0368` | `0x0001` | `0x93bc03` |
| `[3e,25:3f,29]` | `0x0310` | `0x01f8` | `0x0001` | `0x93bc03` |
| `[3b,46:3c,48]`, `[3a,48:3b,49]` | `0x02d8` | `0x0408` | `0x0001` | `0x93bc03` |
| `[14,46:15,48]`, `[15,48:16,49]` | `0x0070` | `0x0408` | `0xffff` | `0x93bc6a` |
| `[36,50:37,51]`–`[37,4e:38,4f]` (×3) | `0x0298` | `0x0488` | `0x0001` | `0x93bc6a` |
| `[35,53:36,54]` | from `$2421` | from `$2423` | `0x0001` | inline |
| `[1a,53:1b,54]` | from `$2421` | from `$2423` | `0xffff` | inline |

---

## NPCs / Enemies

| Sprite ID | Count | Notes |
|-----------|-------|-------|
| `0x0a` (unknown) | 6 | Roaming spawner group 1; `// TODO: identify` |
| `0x0e` (unknown) | 13 | Roaming spawner group 1; `// TODO: identify` |

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
| 16 | `$229d` bit `0x04` | `[31,5b:32,5c]` | Water |
| 17 | `$229d` bit `0x08` | `[1d,5b:1e,5c]` | Water |
| 18 | `$229d` bit `0x10` | `[1b,51:1c,52]` | Clay |
| 19 | `$229d` bit `0x20` | `[27,49:28,4a]` | Clay |
| 20 | `$229d` bit `0x40` | `[21,38:22,39]` | Clay |
| 21 | `$229d` bit `0x80` | `[2a,28:2b,29]` | Clay |
| 22 | `$229e` bit `0x01` | `[36,25:37,26]` | Clay |
| 23 | `$229e` bit `0x02` | `[1d,12:1e,13]` | Clay |
| 24 | `$229e` bit `0x04` | `[17,45:18,46]` | Roots |
| 25 | `$229e` bit `0x08` | `[3c,3f:3d,40]` | Roots |
| 26 | `$229e` bit `0x20` | `[3c,25:3d,26]` | Roots |
| 27 | `$229e` bit `0x10` | `[16,23:17,24]` | Roots |
| 28 | `$229e` bit `0x40` | `[20,53:21,54]` | Oil |
| 29 | `$229e` bit `0x80` | `[23,4b:24,4c]` | Oil |
| 30 | `$229f` bit `0x01` | `[31,42:32,43]` | Oil |
| 31 | `$229f` bit `0x02` | `[23,3b:24,3c]` | Oil |
| 32 | `$229f` bit `0x04` | `[2a,31:2b,32]` | Oil |
| 33 | `$229f` bit `0x08` | `[21,2e:22,2f]` | Oil |
| 34 | `$229f` bit `0x10` | `[1a,18:1b,19]` | Oil |
| 35 | `$229f` bit `0x20` | `[37,14:38,15]` | Oil |
| 36 | `$229f` bit `0x40` | `[36,4d:37,4e]` | Ash |
| 37 | `$229f` bit `0x80` | `[13,38:14,39]` | Ash |
| 38 | `$22a0` bit `0x01` | `[3c,37:3d,38]` | Ash |
| 39 | `$22a0` bit `0x02` | `[23,1f:24,20]` | Ash |

---

## External Scripts

| Opcode / Callee | Purpose |
|----------------|---------|
| `0x00` | Fade-out / stop music |
| `0x01` | Fade-in / start music |
| `0x21` | Prepare room change: south outdoor-outdoor |
| `0x26` | Prepare room change: north outdoor-indoor |
| `0x39` | Loot nature (sniff spot) |
| `0x59` | Attraction mode, after Thraxx |
| `0x93bb91` | Tube warp: east-west transition (BBM body passages) |
| `0x93bc03` | Tube warp: left/multi-corridor transitions |
| `0x93bc6a` | Tube warp: lower/south passage transitions |
| `0x93c281` | BBM segment state reset subroutine (clears $2288–$228a bits) |
| `0x92de75` | Cinematic script (called at end of enter) |

---

## Enter Script Summary

1. In-animation branch (standard); teleport both to `(0x31, 0xa1)`.
2. Write engine register `$0eac+8 = 0x178e` (BBM wings?); `$0eac+0 = 0x172b`.
3. Set enemy drop table: Petal/`0x0001`×10/Nectar; rates 10/2/1.
4. Unload 24 already-collected sniff spots (objs 16–39 via `$229d–$22a0`).
5. **BBM segment initialization:**
   - If `$22dc&0x08` AND NOT `$22e9&0x04`: call segment-reset subroutine (clears all `$2288–$228a` eaten bits).
   - Set `$22e9 |= 0x04`.
   - For each eaten bit in `$2288&0x10–0x80`, `$2289&0x01–0x08`, `$2289&0x20–0x80`, `$228a&0x01–0x04`: unload corresponding obj.
   - Obj 8: set state 4 if `$2289&0x10`, else state 0.
6. Add 6 NPC `0x0a` + 13 NPC `0x0e` spawners at various coords.
7. If music not set: play music `0x14`, fade in.
8. If `$22eb&0x04` (attraction mode): run BBM intro walk sequence, call `"Attraction mode, after Thraxx"` (0x59).
9. Call cinematic script `0x92de75`.

---

## Notes

- **BBM (Big Bug Monster)** occupies the majority of this room. Its 16 body segments are separate objects (0–15), each with its own stepped-on trigger zone and persistence bit.  
- **Segment ordering is not strictly sequential** — some segments require others to be activated first (seg 13 requires seg 11; segs 2, 3, 7 require their respective gate bits). This imposes a partial order on exploration.  
- **Obj 8 uses state 4** rather than being unloaded — this likely represents a visually distinct "inside" state for the middle segment.
- **$2835 counter (seg 5 gate):** The player must step on seg 5's zone twice before it activates. First step sets `$2835 += 1`; on the second visit with `$2835 > 1`, the segment fires.
- **Tube navigation scripts** (`0x93bb91`/`0x93bc03`/`0x93bc6a`) teleport both boy and dog to $2497/$2499 coords within the map, simulating travel through BBM's body. `$2837` encodes the exit direction.
- **No gourds** in this room — sniff spots (24) are the only collectibles.
- **NPC IDs 0x0a and 0x0e** remain unidentified. Both appear in 0x67 (Bugmuck exterior) with the same spawner group.
- **`$22dc&0x08`** purpose unknown — gates whether BBM segments are reset on room entry. Likely set by some prior progression event.
  - `// TODO: identify $22dc bit 0x08`
