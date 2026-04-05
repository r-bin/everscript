# [0x4e] Gothica — Ivor Tower, West Alley (Market / Pig Race)

| Field | Value |
|-------|-------|
| Room ID | 0x4e |
| Name | Gothica - Ivor Tower, west alley (market) |
| Act | Act 3 — Gothica |
| Data offset | `0xa0f130` |
| Enter script | `0x928205` → `0x9aaae8` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | `MUSIC.DRAGON_ROAR` (0x6a) — plays if `$238d == 0x00` |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | none |
| NPCs | Up to 9 always + 5 pre-race + 1 egg-winner conditional + 3 shops + 9 pig-race crowd |
| Forced dog form | Poodle (0x08) |
| Music | 0x6a |

**Drop table**: none set.

---

## Overview

The market alley west of Ivor Tower. Also the site of the pig race event. Entry branches on two story flags: `$22f5&0x20` triggers the full pig-race cutscene (3 OGLIN pigs racing across screen, dog wins, crowd reacts, awards queen's banquet invitation); `$22dc&0x01` gates which NPC set loads (pre-race vs post-race). After the cutscene `$22dc|=0x01` is set, `$234b=0x89` and the room transitions to 0x7c.

---

## Enter Script Logic

1. If `$22eb&0x20` (in animation): teleport both to `[27,c1]`, fade-out, clear flag
2. Set dog = Poodle (`$2443 = 0x08`)
3. If NOT `$22dc&0x01` (pig race not yet done): load **pre-race NPC set**:
   - NPC 0x33 (type 0x51, VILLAGER_3_2) at `[29,3b]` → talk `0x1a8b`
   - NPC 0x33 at `[29,93]` → talk `0x1a91`
   - NPC 0x38 (type 0x56, VILLAGER_3_6) at `[0f,9b]` → talk `0x1a9d`
   - NPC 0x37 (type 0x55, VILLAGER_3_5) at `[29,1b]` → talk `0x1aa3`
   - NPC 0x37 at `[2b,9b]` → talk `0x1aac`
4. **Always-loaded NPCs**:
   - NPC 0x51 at `[21,71]` → talk `0x1a8e`
   - NPC 0x52 (VILLAGER_3_3) at `[2b,29]` → talk `0x1a94`
   - NPC 0x52 at `[0f,b9]` → talk `0x1a97`
   - NPC 0x56 at `[29,69]` → talk `0x1a9a`
   - NPC 0x56 at `[2b,ab]` → talk `0x1aa0`
   - NPC 0x55 at `[2b,53]` → talk `0x1aa6`
   - NPC 0x55 at `[0f,8b]` → talk `0x1aa9`
   - NPC 0x53 (VILLAGER_3_4) at `[13,45]` → talk `0x1aaf`
   - NPC 0x53 at `[2b,83]` → talk `0x1ab2`
5. If NOT `$2261&0x40` (Chocobo Egg not yet won): load NPC 0x56 at `[09,1f]` facing east → `$2834`, talk `0x1ab5` (egg-winner NPC)
6. RCALL loads shop vendors:
   - NPC 0x55 at `[09,3a]` → `$2836` facing east, talk `0x1ab8`
   - NPC 0x56 at `[09,4a]` → `$2838` facing east, talk `0x1abb`
   - NPC 0x55 at `[09,74]` → `$283a` facing east, talk `0x1abe`
7. Play music 0x6a if `$238d == 0x00`
8. Set `$23bf = 0x0001`
9. If NOT `$22f5&0x20`: set scroll `[0x01d0|0x0660]`, call cinematic script `0x92de75`

---

## Pig Race Cutscene (`$22f5&0x20`)

Triggered if `$22f5&0x20` is set on entry (set externally in 0x63 after the Pigpoodle exhibit).

1. Teleport boy+dog to `[0x8c0, 0x0b]`; scroll set to `[0x01c8|0x0618]`
2. Load 3× OGLIN (NPC `0x00dc>>1 = 0x6e`) as pig entities: `$2860`, `$2862`, `$2864`
3. Load 9 crowd NPCs: `$2848–$2856` (types 0x55/0x56/0x51/0x53)
4. Pig race animation loop (position updates, speed variations)
5. Announcer dialog:
   - "Truffle Trouble is leading the pack!"
   - "We have a winner!"
6. Post-race dialog:
   - NPC: "Who owns this pig?"
   - Boy: "Uh, I guess that would be me."
   - NPC: "You, sir, will be the guest of honor at the queen's banquet tonight!"
   - Boy: "It looks like you've done something right for a change. We can ask the queen if she knows how to get back to Podunk!"
7. Sets `$22f5 &= ~0x20` (clear pig race pending), `$22dc |= 0x01` (Pigrace finished)
8. Clears `$22eb&0x40`; sets scroll `[0x01d0|0x0660]`, `$234b = 0x89`
9. CHANGE MAP → 0x7c @ `[0x0208|0x00d8]`

---

## Step-On Scripts

| Tile | Destination | Scroll | Notes |
|------|-------------|--------|-------|
| `[16,0c:1a,0e]` | MAP 0x62 @ `[0x02a0|0x0258]` | — | North → Ivor Tower west square (trailers) |
| `[1e,6b:20,70]` | MAP 0x7b @ `[0x0008|0x01f0]` | — | South → Ebon Keep/Ivor Tower Exterior Bottom Half |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22f5` | 0x20 | R/W | 📖 Pig race pending — triggers full pig-race cutscene on 0x4e entry; cleared after cutscene // MISMATCH: memory-map previously labelled this bit "FE visited or post-WW?" — needs resolution |
| `$22dc` | 0x01 | R/W | 📖 Pigrace finished — gates pre-race NPC set; set at end of cutscene |
| `$2261` | 0x40 | R | 💎 Chocobo Egg won — if set, egg-winner NPC at `[09,1f]` is NOT loaded |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard (standard `IN_ANIMATION` pattern) |
| `$22eb` | 0x40 | W | ⚙️ Cleared after pig race cutscene |
| `$2443` | — | W | ⚙️ Dog form set to Poodle (0x08) on entry |
| `$234b` | — | W | ⚙️ Set to 0x89 before CHANGE MAP → 0x7c (pig-race winner castle entry) |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on every entry (purpose unknown) |
| `$238d` | — | R | ⚙️ CHANGE_MUSIC flag — music 0x6a plays only if this is 0x00 |
| `$2834` | — | W | ⚙️ Egg-winner NPC pointer (NPC 0x56 at `[09,1f]`) — loaded if `$2261&0x40` NOT set |
| `$2836` | — | W | ⚙️ Shop vendor NPC pointer (NPC 0x55 at `[09,3a]`) |
| `$2838` | — | W | ⚙️ Shop vendor NPC pointer (NPC 0x56 at `[09,4a]`) |
| `$283a` | — | W | ⚙️ Shop vendor NPC pointer (NPC 0x55 at `[09,74]`) |
| `$2848`–`$2856` | — | W | ⚙️ Pig-race crowd NPC pointers (loaded during cutscene) |
| `$2860`–`$2864` | — | W | ⚙️ Pig-race pig entity pointers (OGLIN 0x6e × 3) |

## Notes

- The pig race cutscene runs automatically on entry when `$22f5&0x20` is set; it clears this flag and sets `$22dc&0x01` (pigrace finished) at the end.
- `$22f5&0x20` has a documented label mismatch: this room uses it as "pig race pending" but another memory-map entry labels it "FE visited / post-WW?" — needs resolution. // MISMATCH
- Three permanent shops and up to 9 crowd NPCs loaded during the cutscene make this the most NPC-dense room in Act 3. The Chocobo Egg winner NPC at `[09,1f]` is suppressed if `$2261&0x40` is set.
