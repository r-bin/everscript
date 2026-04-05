# 0x66 — West of Swamp

**ROM:** `0x9fff7f` | **Data:** `0xa8c44e` | **Enter:** `0x928219` → `0x9488a7`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x0c` |
| Map bounds | Default; expanded to X 0x0220 × Y 0x0260 if `$22dc&0x08` (WindWalker unlocked) |
| Objects | 8+ (obj 0–13 sniff spots; obj 5–6 gourds; obj 7 leafpad entity) |
| NPCs | 16 (7× `0x21`, 5× `0x0c`, 4× `0x1e`) |
| Step-on zones | 7 |
| B-triggers | 19 (11 sniff spots with duplicates + 2 gourds) |
| Sniff spots | 11 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| North | `0x36` Both fire pits @ `[0x00b8\|0x0160]` | step-on `[17,04:1b,05]` | indoor transition (Global 0x27) |
| East | `0x65` Swamp (main area) @ `[0x0008\|0x0580]` | step-on `[3a,20:3c,22]` | outdoor → outdoor (Global 0x1d) |
| West | `0x69` Volcano path @ `[0x0358\|0x0418]` | step-on `[0c,14:0e,17]` | outdoor → outdoor (Global 0x1a) |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22dc` | `0x08` | 📖 | WindWalker unlocked (expands map bounds; blocks leafpad/obj 7 load) |
| `$22f2` | `0x02` | 📖 | **Swamp leafpad activated** — SET by step-on `[27,22:28,25]`; gates obj 7 reload on entry |
| `$228f` | `0x04` | 👃 | Sniffed Water in West of swamp (#0) |
| `$22b3` | `0x02` | 👃 | Sniffed Water in West of swamp (#1) |
| `$22b3` | `0x04` | 👃 | Sniffed Roots in West of swamp (#2) |
| `$22b3` | `0x08` | 👃 | Sniffed Roots in West of swamp (#3) |
| `$22b4` | `0x01` | 👃 | Sniffed Wax in West of swamp (#4) |
| `$227c` | `0x08` | 🫙 | Gourd obj 5 looted (Water) |
| `$227c` | `0x10` | 🫙 | Gourd obj 6 looted (Water) |
| `$22b3` | `0x10` | 👃 | Sniffed Roots in West of swamp (#8) |
| `$22b2` | `0x80` | 👃 | Sniffed Water in West of swamp (#9) |
| `$22b3` | `0x20` | 👃 | Sniffed Oil in West of swamp (#10) |
| `$22b3` | `0x40` | 👃 | Sniffed Oil in West of swamp (#11) |
| `$22b3` | `0x80` | 👃 | Sniffed Wax in West of swamp (#12) |
| `$22b3` | `0x01` | 👃 | Sniffed Water in West of swamp (#13) |

## Objects

| Obj | Type | Contents | Flag | Notes |
|-----|------|----------|------|-------|
| 5 | 🫙 Gourd | Water | `$227c&0x08` | MAP REF 0x0005 |
| 6 | 🫙 Gourd | Water | `$227c&0x10` | MAP REF 0x0006 |
| 7 | 🐸 Leafpad entity | — | `$22f2&0x02` | State 0x7e on reload; state 5 on first activation; blocked by `$22dc&0x08` |

## NPCs / Enemies

| NPC ID | Count | Positions | State | Notes |
|--------|-------|-----------|-------|-------|
| `0x21` | 7 | `(27,1b)`,`(37,17)`,`(2d,3d)`,`(3d,2f)`,`(4d,39)`,`(55,2d)`,`(21,27)` | — | Enemy type (same as 0x65 swamp) |
| `0x0c` | 5 | `(0d,1b)`,`(05,2b)`,`(0f,13)`,`(2a,10)`,`(19,3f)` | — | Standard enemy |
| `0x1e` | 4 | `(07,47)`,`(0b,05)`,`(4f,15)`,`(55,49)` | `8400` | `$2433=0x000a`; quest NPC variant |

## Drop Table

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| Prize 1 | Petal (`0x0800`) | 10 | 1 |
| Prize 2 | `0x0001` | 2 | 20 |
| Prize 3 | Nectar (`0x0801`) | 1 | 1 |

## Enter Script Summary

1. Set engine hook `$0eac+0=0x172b`; prize table.
2. If not re-entry: teleport both to `(0x09, 0x25)`.
3. Set `$23c5=0x0280` (parallax/camera register — TODO: identify).
4. Unload sniff spots and gourds per their flags (`$228f&0x04`, `$22b2&0x80`, `$22b3` full byte, `$22b4&0x01`, `$227c&0x08`, `$227c&0x10`).
5. If `$22f2&0x02` AND NOT `$22dc&0x08` → set obj 7 state=0x7e (reload leafpad entity).
6. If `$22dc&0x08` (WindWalker unlocked) → expand map bounds to X 0x0220, Y 0x0260.
7. Load NPCs: 7× `0x21`, 5× `0x0c`, 4× `0x1e` (state 8400, `$2433=0x000a`).
8. Play music `0x0c`. Call cinematic entry (`0x92de75`). End.

## Step-on Zones

| Zone | Action | Notes |
|------|--------|-------|
| `[2d,24:2e,25]` | SFX 0x72; `$2835`+1/-1 (max 5 concurrent) | Mudpuddle splash |
| `[28,24:29,25]` | SFX 0x72; `$2835`+1/-1 | Mudpuddle splash (shared script) |
| `[2a,24:2c,25]` | SFX 0x72; `$2835`+1/-1 | Mudpuddle splash (shared script) |
| `[27,22:28,25]` | First-time: walk to `(0x3a,0x41)`, set `$22f2\|=0x02`, SFX 0x72, obj 7 state=5 | Leafpad first activation; no-op if flag or `$22dc&0x08` already set |
| `[17,04:1b,05]` | CHANGE MAP = `0x36` @ `[0x00b8\|0x0160]` | North exit → Both fire pits |
| `[3a,20:3c,22]` | CHANGE MAP = `0x65` @ `[0x0008\|0x0580]` | East exit → Swamp main |
| `[0c,14:0e,17]` | CHANGE MAP = `0x69` @ `[0x0358\|0x0418]` | West exit → Volcano path |

## Sniff Spots

The dump labels positions #5–7 as gobjects/gourds; positions #0–#4 and #8–#13 are sniff spots. Several spots share flags across multiple B-trigger zones (duplicated coordinates).

| # | Zone(s) | Ingredient | Flag |
|---|---------|------------|------|
| 0 | `[2a,0d:2b,0e]` | 💧 Water | `$228f&0x04` |
| 1 | `[36,18:37,19]` | 💧 Water | `$22b3&0x02` |
| 2 | `[19,0d:1a,0e]` | 🌿 Roots | `$22b3&0x04` |
| 3 | `[1f,0b:20,0c]` | 🌿 Roots | `$22b3&0x08` |
| 4 | `[10,0f:11,10]` | 🕯️ Wax | `$22b4&0x01` |
| 5 | `[13,0b:15,0d]` | 🫙 **Gourd — Water** | `$227c&0x08` |
| 6 | `[1d,0c:1f,0e]` | 🫙 **Gourd — Water** | `$227c&0x10` |
| 8 | `[1e,21:1f,22]`, `[12,1a:13,1b]` | 🌿 Roots | `$22b3&0x10` |
| 9 | `[1f,27:20,28]`, `[22,1a:23,1b]` | 💧 Water | `$22b2&0x80` |
| 10 | `[29,18:2a,1a]`, `[13,27:14,28]` | 🛢️ Oil | `$22b3&0x20` |
| 11 | `[2b,18:2c,1a]`, `[2b,25:2c,26]` | 🛢️ Oil | `$22b3&0x40` |
| 12 | `[31,19:32,1b]`, `[32,23:33,24]` | 🕯️ Wax | `$22b3&0x80` |
| 13 | `[1f,15:21,17]`, `[2a,1d:2b,1e]` | 💧 Water | `$22b3&0x01` |

**Summary:** Water×5, Roots×3, Oil×2, Wax×2 + 2 gourds (Water each) = **11 sniff spots + 2 gourds**. Some spots span two physical zones sharing the same persistence flag.

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x948748` | Mudpuddle splash SFX (`$2835`+1, SFX 0x72, -1 after 12 ticks; max 5 active) |
| `0x948729` | Leafpad first-activation (walk, set flag, obj 7 state=5) |

## Notes

- **`$22f2 bit 0x02`** = "Swamp leafpad activated" — confirmed by dump label. Setter: step-on `[27,22:28,25]` in this room. Obj 7 is the leafpad entity; it is only loaded/reloaded when this flag is set AND `$22dc&0x08` is NOT set.
- **WindWalker map expansion:** When WindWalker is unlocked (`$22dc&0x08`), the map expands northward/eastward (X 0x0220, Y 0x0260) and the leafpad is no longer relevant, presumably opening a direct path through the swamp.
- **Spot #7 gap:** MAP REF 0x0007 is not present in the B-trigger table — obj 7 is the leafpad entity (not a looted ingredient). Its persistence is `$22f2&0x02` but it is managed via step-on and enter script, not as a B-trigger.
- **`$23c5 = 0x0280`** is set in both 0x66 and 0x65 — likely a parallax scrolling or water-effect register for the swamp area. — TODO: identify.
- `$2835` is used here as a "mudpuddle splash counter" (max 5 concurrent splashes). In other rooms it stores NPC position state. This appears to be a scratch/temp field.
- `$0eac+0=0x172b` appears in all outdoor rooms — confirmed as engine behavior hook.
