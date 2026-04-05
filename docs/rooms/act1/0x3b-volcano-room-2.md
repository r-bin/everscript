# 0x3b — Volcano Room 2

**ROM:** `0x9ffed3` | **Data:** `0xa2c0a8` | **Enter:** `0x928142` → `0x949996`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x08` |
| Map bounds | Large single-section cave map |
| Objects | 0–0x25 (gourds + NPC placeholder states + WindWalker alternate obj) |
| NPCs | 3× `0x3c`, 3× `0x3e`, optional `0x2a` boss, optional 14× `0x29` spawners |
| Step-on zones | 4 |
| B-triggers | 34 (8 gourds with 1 dual-zone + 25 sniff spots) |
| Sniff spots | 25 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| North A | `0x3c` Volcano Room 1 @ `[0x00e0\|0x01d8]` | step-on `[26,04:28,06]` | `$234b=0x0001`; Global 0x26 |
| North B | `0x3e` Side rooms of pipe maze @ `[0x00d0\|0x0178]` | step-on `[4a,04:4c,05]` | music fade; Global 0x26 |
| South A | `0x3c` Volcano Room 1 @ `[0x0100\|0x0428]` | step-on `[4d,58:50,5a]` | `$234b=0x0009`; Global 0x21 |
| South B | `0x3c` Volcano Room 1 @ `[0x0698\|0x01e8]` | step-on `[37,58:3a,5a]` | `$234b=0x0008`; Global 0x21 |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$225d` | `0x80` | 📖 | NPC `0x3e` #1 position-shifted (obj 1 state=4 if set) |
| `$225e` | `0x01` | 📖 | NPC `0x3e` #2 position-shifted (obj 2 state=4 if set) |
| `$225e` | `0x02` | 📖 | NPC `0x3e` #3 position-shifted (obj 0 state=5 if set) |
| `$225e` | `0x04` | 📖 | NPC `0x3c` #1 position-shifted |
| `$225e` | `0x08` | 📖 | NPC `0x3c` #2 position-shifted |
| `$225e` | `0x10` | 📖 | NPC `0x3c` #3 position-shifted |
| `$225e` | `0x40` | 📖 | **Viper Commander spawn** (set by 0x3c exit step-on; cleared here after spawning; gates NPC `0x2a` load) |
| `$22dc` | `0x08` | 📖 | WindWalker unlocked (if set: skip enemy spawners; load obj 0x25 state=1) |
| `$226d` | `0x80` | 🫙 | Gourd MAP REF 0x03 looted (Mud Pepper, DOG ONLY) |
| `$226e` | `0x01` | 🫙 | Gourd MAP REF 0x04 looted (Mud Pepper) |
| `$226e` | `0x02` | 🫙 | Gourd MAP REF 0x05 looted (Petal) |
| `$226e` | `0x04` | 🫙 | Gourd MAP REF 0x06 looted (Clay) |
| `$226e` | `0x08` | 🫙 | Gourd MAP REF 0x07 looted (Roots) |
| `$226e` | `0x10` | 🫙 | Gourd MAP REF 0x08 looted (Roots) |
| `$226e` | `0x20` | 🫙 | Gourd MAP REF 0x0a looted (Water) |
| `$226e` | `0x40` | 🫙 | Gourd MAP REF 0x0b looted (Money 100, DOG ONLY) |
| `$22ab` | `0x80` | 👃 | Sniffed Water (#12) |
| `$22ac` | `0x01` | 👃 | Sniffed Water (#13) |
| `$22ac` | `0x02` | 👃 | Sniffed Water (#14) |
| `$22ac` | `0x04` | 👃 | Sniffed Water (#15) |
| `$22ac` | `0x08` | 👃 | Sniffed Water (#16) |
| `$22ac` | `0x10` | 👃 | Sniffed Clay (#17) |
| `$22ac` | `0x20` | 👃 | Sniffed Clay (#18) |
| `$22ac` | `0x40` | 👃 | Sniffed Clay (#19) |
| `$22ac` | `0x80` | 👃 | Sniffed Clay (#20) |
| `$22ad` | `0x01` | 👃 | Sniffed Clay (#21) |
| `$22ad` | `0x02` | 👃 | Sniffed Clay (#22) |
| `$22ad` | `0x04` | 👃 | Sniffed Clay (#23) |
| `$22ad` | `0x08` | 👃 | Sniffed Roots (#24) |
| `$22ad` | `0x10` | 👃 | Sniffed Oil (#25) |
| `$22ad` | `0x20` | 👃 | Sniffed Oil (#26) |
| `$22ad` | `0x40` | 👃 | Sniffed Ash (#27) |
| `$22ad` | `0x80` | 👃 | Sniffed Ash (#28) |
| `$22ae` | `0x01` | 👃 | Sniffed Ash (#29) |
| `$22ae` | `0x02` | 👃 | Sniffed Ash (#30) |
| `$22ae` | `0x04` | 👃 | Sniffed Ash (#31) |
| `$22ae` | `0x08` | 👃 | Sniffed Ash (#32) |
| `$22ae` | `0x10` | 👃 | Sniffed Ash (#33) |
| `$22ae` | `0x20` | 👃 | Sniffed Wax (#34) |
| `$22ae` | `0x40` | 👃 | Sniffed Wax (#35) |
| `$22ae` | `0x80` | 👃 | Sniffed Wax (#36) |

## NPCs / Enemies

| NPC ID | Count | Position(s) | State | Notes |
|--------|-------|-------------|-------|-------|
| `0x3c` | 3 | varies per `$225e&0x04/0x08/0x10` | `0002` | Unknown NPC type; position shifts when flag is set; refs: `$283f/$2841/$2843` |
| `0x3e` | 3 | varies per `$225d&0x80/$225e&0x01/0x02` | `0002` | Unknown NPC type; teleported to specific map coords; talk scripts `0x17fa/0x17fd/0x1800`; replaced by obj state when defeated |
| `0x2a` | 1 | `(0x49, 0x67)` | — | **Mammoth Viper Commander** — only if `$225e&0x40`; kill script `0x17f4` ("Viper commander kill"); `$225e&0x40` cleared immediately after load |
| `0x29` | 14 spawners | scattered | `0x0001` | Mammoth Viper; NOT spawned if `$22dc&0x08` (WindWalker unlocked) |

## Enter Script Summary

1. Set engine hooks (`$0eac+8=0x178b`, `$0eac+0=0x172b`, **`$0eac+4=0x17f7`**).
2. Prize table (Petal/`0x0001`/Nectar).
3. Load 3× NPC `0x3c` — position A or B based on `$225e&0x04/0x08/0x10`; store refs in `$283f/$2841/$2843`.
4. Load 3× NPC `0x3e` gated by `$225d&0x80`, `$225e&0x01`, `$225e&0x02`. If flag NOT set: load NPC, teleport to canonical position. If flag IS set: set corresponding obj to state 4 or 5 (NPC defeated/removed).
5. If NOT `$22dc&0x08`: load 14× NPC `0x29` spawners + check `$225e&0x40`.
6. If `$22dc&0x08`: set obj 0x25 state=1 (WindWalker alternate path object).
7. Unload looted gourds (`$226d&0x80`, `$226e` full byte, `$22ab&0x80`, `$22ac/ad/ae`).
8. If `$225e&0x40`: load NPC `0x2a` at `(0x49,0x67)` with kill script `0x17f4`; clear `$225e&0x40`.
9. Teleport both to `(0x51, 0xa7)` on normal entry. Play music `0x08`.

## Gourds

| MAP REF | Zone | Contents | Flag | Dog-only? |
|---------|------|----------|------|-----------|
| 0x0003 | `[39,1e:3b,1f]`, `[39,1f:3b,20]` | 🌶️ Mud Pepper | `$226d&0x80` | ✅ `$2425==0x02` |
| 0x0004 | `[36,45:38,47]` | 🌶️ Mud Pepper | `$226e&0x01` | ❌ |
| 0x0005 | `[4e,32:50,34]` | 🧪 Petal | `$226e&0x02` | ❌ |
| 0x0006 | `[1d,33:1f,35]` | 🏺 Clay | `$226e&0x04` | ❌ |
| 0x0007 | `[23,1c:25,1e]` | 🌿 Roots | `$226e&0x08` | ❌ |
| 0x0008 | `[2c,12:2e,14]` | 🌿 Roots | `$226e&0x10` | ❌ |
| 0x000a | `[32,38:34,3a]` | 💧 Water | `$226e&0x20` | ❌ |
| 0x000b | `[35,39:37,3b]` | 💰 Money (100) | `$226e&0x40` | ✅ `$2425==0x02` |

## Sniff Spots

| # | Zone | Ingredient | Flag |
|---|------|------------|------|
| 12 | `[3d,46:3e,47]` | 💧 Water | `$22ab&0x80` |
| 13 | `[3b,2c:3c,2d]` | 💧 Water | `$22ac&0x01` |
| 14 | `[2c,2a:2d,2b]` | 💧 Water | `$22ac&0x02` |
| 15 | `[2c,1e:2d,1f]` | 💧 Water | `$22ac&0x04` |
| 16 | `[3d,19:3e,1a]` | 💧 Water | `$22ac&0x08` |
| 17 | `[33,42:34,43]` | 🏺 Clay | `$22ac&0x10` |
| 18 | `[44,3c:45,3d]` | 🏺 Clay | `$22ac&0x20` |
| 19 | `[2d,3a:2e,3b]` | 🏺 Clay | `$22ac&0x40` |
| 20 | `[44,2f:45,30]` | 🏺 Clay | `$22ac&0x80` |
| 21 | `[30,2b:31,2c]` | 🏺 Clay | `$22ad&0x01` |
| 22 | `[25,1b:26,1c]` | 🏺 Clay | `$22ad&0x02` |
| 23 | `[44,1e:45,1f]` | 🏺 Clay | `$22ad&0x04` |
| 24 | `[4f,38:50,39]` | 🌿 Roots | `$22ad&0x08` |
| 25 | `[39,49:3a,4a]` | 🛢️ Oil | `$22ad&0x10` |
| 26 | `[19,28:1a,29]` | 🛢️ Oil | `$22ad&0x20` |
| 27 | `[36,50:37,51]` | 💨 Ash | `$22ad&0x40` |
| 28 | `[20,3b:21,3c]` | 💨 Ash | `$22ad&0x80` |
| 29 | `[3a,39:3b,3a]` | 💨 Ash | `$22ae&0x01` |
| 30 | `[26,2d:27,2e]` | 💨 Ash | `$22ae&0x02` |
| 31 | `[39,2b:3a,2c]` | 💨 Ash | `$22ae&0x04` |
| 32 | `[50,1f:51,20]` | 💨 Ash | `$22ae&0x08` |
| 33 | `[34,0e:35,0f]` | 💨 Ash | `$22ae&0x10` |
| 34 | `[3c,46:3d,47]` | 🕯️ Wax | `$22ae&0x20` |
| 35 | `[15,30:16,31]` | 🕯️ Wax | `$22ae&0x40` |
| 36 | `[1b,26:1c,27]` | 🕯️ Wax | `$22ae&0x80` |

**Summary:** Water×5, Clay×7, Roots×1, Oil×2, Ash×7, Wax×3 = 25 sniff spots.

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x17f4` | Mammoth Viper Commander kill handler |
| `0x17fa` | NPC `0x3e` #1 talk script |
| `0x17fd` | NPC `0x3e` #2 talk script |
| `0x1800` | NPC `0x3e` #3 talk script |
| `0x17f7` | Engine hook slot 4 (`$0eac+4`) — unknown |

## Notes

- **`$225e&0x40` = "Viper Commander spawn"** — CONFIRMED. Set by 0x3c exit step-on `[0f,45:11,47]`; on re-entering 0x3b, NPC `0x2a` (Mammoth Viper Commander) spawns at `(0x49, 0x67)` and the flag is immediately cleared. This is a **one-time spawn trigger** — once the Commander appears, the flag is gone.
- **Dog-only gourds**: MAP REF 0x0003 (Mud Pepper) and 0x000b (Money 100) check `$2425==0x02`. `$2425` appears to be the "active/controlled character" register with `0x02` = dog. This is the only confirmed dog-exclusive mechanic seen so far in Act 1.
- **NPC `0x3e`** talk scripts `0x17fa/0x17fd/0x1800` and the teleport to specific coordinates suggest these are interactive NPCs that move to a position and can be talked to (possibly activating puzzles or doors). When defeated/used (`$225d&0x80/$225e&0x01/0x02`), their slot is replaced by an object state.
- **`$0eac+4=0x17f7`** is a NEW engine hook slot (slot 4), only seen in 0x3b. Combined with `$0eac+8=0x178b` (also in 0x3c), this suggests 0x3b/0x3c use special per-frame scripts.
- **WindWalker path (`$22dc&0x08`)**: When set, enemy spawners are skipped and obj 0x25 state=1 is loaded. This object likely opens an alternate route through the room.
- MAP REF 0x0009 is absent from B-triggers. Either it's unused or belongs to another context.
- The Mammoth Viper Commander (NPC `0x2a`) here in 0x3b is distinct from the Mammoth Graveyard's commander (0x27). They share the same NPC type but this is a different encounter.
