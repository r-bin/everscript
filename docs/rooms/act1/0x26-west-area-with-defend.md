# 0x26 — Prehistoria: West area with Defend

**ROM address:** `0x9ffe7f`  
**Data address:** `0xadcee5`  
**Enter script:** `0x9280d9` → `0x94e57d`  
**Act:** 1 — Prehistoria

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on zones | 1 |
| B-trigger zones | 3 |
| Gourds | 3 |
| NPCs | 0–1 (conditional) |
| Enemies | 0 |
| Music | `0x12` (Prehistoria overworld) |

---

## Connections

| Direction | Zone | Destination |
|-----------|------|-------------|
| East (step-on) | `[1c,10:1e,13]` | `0x25` Fire Eyes' Village |

---

## Memory Access

| Address | Bits | Category | R/W | Meaning |
|---------|------|----------|-----|---------|
| `$2260` | `0x10` | 📖 | R | Thraxx dead |
| `$2268` | `0x02` | 🫙 | R/W | Gourd obj0 looted (changing content) |
| `$2268` | `0x04` | 🫙 | R/W | Gourd obj1 looted (Clay) |
| `$2268` | `0x08` | 🫙 | R/W | Gourd obj2 looted (Ash) |
| `$2288` | `0x08` | 📖 | R | Unknown — gates Defend Guy spawn (not set = show NPC) |
| `$225c` | `0x40` | 📖 | R | Call Beads given by Fire Eyes (upgrades gourd obj0 content) |
| `$2391` | —     | ⚙️ | W | PRIZE (gourd loot content) |
| `$2395` | —     | ⚙️ | W | MAP REF? (gourd object index) |
| `$2443` | —     | 🐶 | W | CHANGE DOGGO — written to Wolf (`0x02`) on enter |
| `$2461` | —     | ⚙️ | W | NEXT ADD (gourd respawn count delta) |
| `$22ea` | `0x01` | ⚙️ | R | Gourd collected flag (engine result; written to $2268 bit) |
| `$22eb` | `0x20` | ⚙️ | R/W | In animation — cleared on enter if set |
| `$22eb` | `0x40` | ⚙️ | W | Set on east exit to `0x25` |
| `$238d` | —     | 🎵 | R | CHANGE MUSIC flag (skip play if already set) |
| `$23bf` | —     | ⚙️ | W | Written `0x0001` on enter (display/cinematic flag) |
| `$242b` | —     | 🎥 | W | Scroll/camera register |
| `$242d` | —     | 🎥 | W | Scroll/camera register |
| `$242f` | —     | 🎥 | W | Scroll/camera register |

---

## Objects

| Obj | Coords | Content | Persistence flag | Notes |
|-----|--------|---------|-----------------|-------|
| 0 | `[10,0d:12,0f]` | Biscuit → Call Beads | `$2268` bit `0x02` | Upgrades to Call Beads if `$225c&0x40` (FE gave call beads); MapRef `0x0000` |
| 1 | `[13,0c:15,0e]` | Clay | `$2268` bit `0x04` | NEXT_ADD=3; MapRef `0x0001` |
| 2 | `[11,14:13,16]` | Ash | `$2268` bit `0x08` | NEXT_ADD=4; MapRef `0x0002` |

---

## NPCs / Enemies

| Sprite ID | Name | Spawn Coords | Condition | Talk Script |
|-----------|------|-------------|-----------|-------------|
| `0x09` (VILLAGER_1_6) | Defend Guy | `(0b, 13)` | `$2260&0x10` (Thraxx dead) AND NOT `$2288&0x08` | "Defend Guy" (addr `$0341+x66=0x1860, x68=0x0040`) |

---

## External Scripts

| Opcode | Callee | Purpose |
|--------|--------|---------|
| `0x00` | `"Fade-out / stop music"` | Called on fresh enter (no in-animation flag) |
| `0x01` | `"Fade-in / start music"` | Called after music set on enter |
| `0x1d` | `"Prepare room change? East exit/west entrance outdoor-outdoor?"` | Called on east exit step-on |
| `0x3a` | `"Loot gourd?"` | Called by each B-trigger |
| `0x92de75` | `"Some cinematic script (used multiple times)"` | Called during enter sequence |

---

## Enter Script Summary

1. Set dog sprite to Wolf (`$2443 = 0x02`).
2. **Branch on in-animation flag (`$22eb&0x20`):**
   - Not set → teleport both to `(13, 15)`, call Fade-out.
   - Set → clear the flag (`$22eb &= 0xdf`).
3. If Thraxx dead AND NOT `$2288&0x08`: load Defend Guy NPC (`0x09`) at `(0b, 13)`.
4. Unload gourds already collected (`$2268` bits 0x02/0x04/0x08 → objs 0/1/2).
5. If music not already set: play music `0x12`, fade in.
6. Set `$23bf = 0x0001`, call cinematic script, sleep 14 ticks, set volume 100.
7. Walk entity by `(-4, 0)`; adjust scroll registers; wait for character to arrive; release player control.

---

## Notes

- **Defend Guy** is a post-Thraxx NPC; he appears only after the boss is defeated and `$2288&0x08` is clear. His role (presumably teaching/offering the Defend alchemy move) is not captured in the enter script — his dialogue is in his talk script.
- **Gourd obj0** is the only changing-content gourd in Act 1 outside of 0x51: it holds a Biscuit until `$225c&0x40` (set in `0x51` FE Cutscene 3), after which it holds Call Beads.
- **`$2288 bit 0x08`** — purpose unknown; gates the Defend Guy spawn. Likely set after the player receives the Defend move.
  - `// TODO: identify what sets $2288 bit 0x08`
- Music `0x12` = Prehistoria overworld (shared with `0x25`, `0x5b`, etc.).
