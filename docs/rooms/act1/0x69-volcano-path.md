# 0x69 — Volcano Path

**ROM:** `0x9fff8b` | **Data:** `0xa18000` | **Enter:** `0x928228` → `0x93ed19`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x0a` (normal); `0x78` (Gauge jingle) |
| Dog form | default (no `$2443` set) |
| Objects | ~39 (8 lava platforms + sniff spots + gourds + Gauge + Levitate platform) |
| NPCs | 25 (8× NPC `0x2b` + 10× NPC `0x0c` + 7× NPC `0x22`) |
| Step-on zones | 31 (lava platforms × 21 + room exits × 6 + geyser × 2 + caves × 3) |
| B-triggers | 33 (1 Gauge + ~26 sniff spots + ~4 gourds + misc) |
| Drop table | Petal 10×, Nectar 1× (first set); Petal 10×, `0x0001` qty=30 2×, Wax 1× (second set) |

## Connections

| Direction | Destination | Zone | Notes |
|-----------|-------------|------|-------|
| South | `0x27` Mammoth Graveyard @ `[0x0190\|0x0078]` | `[1c,56:1f,58]` | outdoor→outdoor |
| East | `0x66` West of Swamp @ `[0x0008\|0x0118]` | `[45,48:46,4c]` | outdoor→outdoor |
| Cave A | `0x35` cave complex @ `[0x0200\|0x0168]` | `[36,3f:37,41]` | `$234d=3, $234e=2` |
| Cave B | `0x35` cave complex @ `[0x04b0\|0x0138]` | `[15,40:16,42]` | `$234d=4, $234e=4` |
| Cave C | `0x35` cave complex @ `[0x0200\|0x0168]` | `[2f,2d:30,2f]` | `$234d=5, $234e=2` |
| Geyser → top | `0x52` Top of Volcano @ `[0x0008\|0x00e8]` | `[27,24:29,25]` | sets `$22ec\|=0x08` |
| Act 2 (outro only) | `0x1b` Desert of Doom @ `[0x0278\|0x04a8]` | — | gated by `$22f1&0x40` |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22f1` | `0x40` | 📖 | Act 1 outro active (triggers volcano eruption → Act 2 warp) |
| `$22ef` | `0x40` | 📖 | "Emerged from dark" entry animation pending (fade-from-black) |
| `$22ec` | `0x10` | 📖 | BBM ride cinematic pending (cleared after playing in this room) |
| `$22dc` | `0x08` | 📖 | Unknown (inverted gate for BBM ride branch) — TODO: identify setter |
| `$22ec` | `0x08` | 📖 | Stepped on geyser (set when player uses geyser to 0x52) |
| `$2264` | `0x04` | 💎 | Gauge collected |
| `$225a` | `0x20` | 📖 | Levitate learned (gates obj 5 Levitate platform at room entry) |
| `$2269` | `0x20` | 🫙 | Gourd 1 collected (obj 9) |
| `$2269` | `0x40` | 🫙 | Gourd 2 collected (obj 8) |
| `$2269` | `0x80` | 🫙 | Gourd 3 collected (obj 10) |
| `$226a` | `0x01` | 🫙 | Gourd 4 collected (obj 11) |
| `$2264` | `0x04` | 💎 | Gauge item unloads obj 0x27 when collected |
| `$22a8` | `0x02`–`0x80` | 👃 | Sniff spots (objs 12–18) |
| `$22a9` | `0x01`–`0x80` | 👃 | Sniff spots (objs 19–26) |
| `$22aa` | `0x01`–`0x80` | 👃 | Sniff spots (objs 27, 0x22, 0x21, 0x20, 31, 30, 29, 28) |
| `$22ab` | `0x01`–`0x08` | 👃 | Sniff spots (objs 0x23–0x26) |

## Objects

| Obj | Description | Condition |
|-----|-------------|-----------|
| 0–7 | Lava platform objects (animated by step-on scripts) | always active |
| 8–11 | Gourds | `$2269&0x40/0x20/0x80`, `$226a&0x01` |
| 12–39 | Sniff spot markers | `$22a8&0x02` through `$22ab&0x08` |
| 5 | Levitate platform | loaded via `SET OBJ 5 STATE=1` if `$225a&0x20` |
| 0x27 | Gauge item | `$2264&0x04` (unloaded = already collected) |

## NPCs / Enemies

| NPC ID | Count | Notes |
|--------|-------|-------|
| `0x2b` | 8 | TODO: identify; also used in outro cutscene (`0x56>>1`) |
| `0x0c` | 10 | Standard enemy (same as other outdoor rooms) |
| `0x22` | 7 | Mammoth-type enemy (same as 0x27) |

## Drop Tables

Two drop table configurations:
- **First (initial):** Petal 10×, Nectar 1×, rate 0 for slot 3
- **Second (active):** Petal 10×, `0x0001` qty=30 2×, Wax 1×

## Enter Script Summary

### Branch 1 — Act 1 Outro (`$22f1&0x40`)
If the outro flag is set, immediately run the Act 1 finale:
1. Call `0x92de75` (cinematic init).
2. Call subroutine `0x93ec4c`:
   - Load NPC `0x2b` (× `0x56>>1`) at `(0x15, 0x85)` and `(0x41, 0x7b)` → store as `arg0`, `arg2`.
   - Load NPC `0x0c` (× `0x18>>1`) at `(0x23, 0x63)` → store as `arg6`.
   - Call `0x92d915` (explosion setup).
   - Call `0x92de75`.
   - Stop boy+dog; face north; walk both toward `(0x41, 0x7b)`.
   - Call `0x92d5bd` × 3 (explosion effect on each NPC with coords), destroying each with sleep intervals.
   - Call `0x92d607` between each explosion.
   - Final walk to `(0x1b, 0x67)`.
   - Fade out screen; set `$238f=0x0000`.
   - **CHANGE MAP = `0x1b` Antiqua - Desert of Doom** @ `[0x0278|0x04a8]`.

### Branch 2 — "Emerged from dark" animation (`$22ef&0x40`)
If `$22ef&0x40`: fade in from black with screen brightness loop (0→15 over 3-tick intervals); teleport characters to Y=0x0030 then scroll them northward to Y=0x00d8 (emerge-from-cave animation); screen shake; SFX `0x3c`; repeat for second character.

### Normal Entry
1. Engine `$0eac+0=0x172b`. Drop table (first config). Set `$2834|=0x04`, `$234e=0x0002`.
2. Play music `0x0a`, fade in.
3. Drop table (second config).
4. If `$225a&0x20` (Levitate learned): set obj 5 state=1.
5. Load 8× NPC `0x2b`, 10× NPC `0x0c`, 7× NPC `0x22` at positions across the map.
6. Unload sniff spot objs (`$22a8&0x02` through `$22ab&0x08`).
7. Unload gourd objs (`$2269&0x20/0x40/0x80`, `$226a&0x01`).
8. Unload obj 0x27 (Gauge) if `$2264&0x04`.

### Branch 3 — BBM Ride Cinematic (`$22ec&0x10` AND NOT `$22dc&0x08`)
After normal entry, if this condition: stop boy+dog; clear `$22ec&0x10`; face south; YIELD; face south; sleep 59 ticks; call `0x93e192`; teleport controlled char along Y path from 0x01c0→0x01fa (move up); set character animations; sleep; walk forward 2; call `0x93e1a7`; same motion for non-controlled char. BOY+DOG = player controlled.

## Step-on Zones

### Room Exits

| Zone | Destination | Notes |
|------|-------------|-------|
| `[1c,56:1f,58]` | `0x27` Mammoth Graveyard | south |
| `[45,48:46,4c]` | `0x66` West of Swamp | east |
| `[36,3f:37,41]` | `0x35` cave @ `[0x0200\|0x0168]` | `$234d=3,$234e=2` |
| `[15,40:16,42]` | `0x35` cave @ `[0x04b0\|0x0138]` | `$234d=4,$234e=4` |
| `[2f,2d:30,2f]` | `0x35` cave @ `[0x0200\|0x0168]` | `$234d=5,$234e=2` |
| `[27,24:29,25]` | `0x52` Top of Volcano | geyser; sets `$22ec\|=0x08`; sets `$22eb\|=0x20` |

### Lava Platform Step-ons (21 entries)

All lava platform step-ons follow the same pattern using shared subroutines. When triggered:
1. Make both characters script-controlled.
2. Call `0x93e74d` (platform animation setup; uses `$245d` as timing param).
3. Set view bounds (`$242b/$242d/$242f`).
4. Set platform params: `$24b3` (X?), `$24b5` (Y start), `$24b7` (platform variant 0–4).
5. Set target obj STATE = 1 (animate/raise platform).
6. Walk controlled char to destination X/Y.
7. Walk non-controlled char to secondary Y.
8. Call `0x93e758` (coordinate non-controlled char walk).
9. Walk non-controlled char to same destination as controlled char.
10. Call `0x93e795` (landing animation/reset).
11. Set target obj STATE = 0 (lower/hide platform).

Some "main path" platforms additionally call `0x93e3c6` + `0x93e432` (non-controlled char drop sequence with camera scroll). One platform (`[29,1b:2b,1c]`) also sets `$2834|=0x01`.

Selected platform step-ons:

| Zone | Target Obj | Destination Walk | Variant (`$24b7`) |
|------|-----------|-----------------|-------------------|
| `[3e,15:41,16]` | — | `(0x5f,0x13)` | uses `0x93e3c6/e432` |
| `[37,21:38,22]` | obj 3 | `(0x4e,0x31)` | 0 |
| `[36,21:37,22]` | obj 3 | `(0x4e,0x31)` | 2 |
| `[32,21:34,22]` | — | `(0x46,0x31)` | uses `0x93e3c6/e432` |
| `[2a,17:2b,18]` | obj 7 | `(0x36,0x1d)` | 3 |
| `[24,23:26,24]` | — | `(0x2a,0x35)` | uses `0x93e3c6/e432` |
| `[29,1b:2b,1c]` | — | `(0x34,0x25)` | uses `0x93e3c6/e432`; sets `$2834\|=0x01` |
| `[2e,12:30,13]` | — | `(via 0x93e432)` | uses `0x93e3c6/e432` |
| `[34,0d:36,0e]` | — | `(0x4a,0x09)` | uses `0x93e3c6/e432` |
| `[35,14:37,15]` | — | (teleport) | uses `0x93e3c6/e432` |
| `[31,1a:33,1b]` | — | `(0x44,0x23)` | uses `0x93e3c6/e432` |
| `[39,1b:3b,1c]` | obj 2 | `(0x52,0x25)` | 0 |
| `[38,15:3a,16]` | obj 0 | `(0x52,0x19)` | 1 |
| `[27,24:29,25]` | obj 4 | `(0x30,0x37)` → **0x52** | geyser; sets `$22ec\|=0x08` |
| `[26,1c:28,1d]` | obj 1 | `(0x3c,0x27)` | 3 |
| `[2e,28:30,29]` | obj 5 | `(0x3c,0x3f)` | 2 |
| `[32,29:33,2a]` | obj 6 | `(0x44,0x41)` | 2 |
| `[31,29:32,2a]` | obj 6 | `(0x44,0x41)` | 4 |
| `[2b,17:2c,18]` | obj 7 | `(0x36,0x1d)` | 2 |
| `[38,1b:3a,1c]` | obj 2 | `(0x52,0x25)` | 0 |
| `[2d,28:2f,29]` | obj 5 | `(0x3c,0x3f)` | 2 |
| `[2d,1c:2f,1d]` | obj 1 | `(0x3c,0x27)` | 3 |

## B-triggers

### Gauge Item

| Zone | Flag | Description |
|------|------|-------------|
| `[3d,17:3f,19]` | `$2264 bit 0x04` | 💎 Gauge — show "Received a Gauge"; play jingle `0x78`→`0x0a`; set obj 0x27 state=`0x7e` |

### Sniff Spots

26 sniff spots spanning `$22a8&0x02` through `$22ab&0x08` (objs 12–39):

| Address Range | Ingredient | Count |
|---------------|------------|-------|
| `$22a8 bits 0x02–0x80` | TODO: identify (read full B-trigger list) | 7 |
| `$22a9 bits 0x01–0x80` | TODO: identify | 8 |
| `$22aa bits 0x01–0x80` | TODO: identify | 8 |
| `$22ab bits 0x01–0x08` | TODO: identify | 4 (partial read) |

First confirmed sniff: `[21,1e:23,1f]` → Clay (`$226a&0x01`, MAP REF `0x000b`).

### Gourds (4)

| Zone | Contents | Flag | Obj |
|------|----------|------|-----|
| TBD | ? | `$2269 bit 0x20` | obj 9 |
| TBD | ? | `$2269 bit 0x40` | obj 8 |
| TBD | ? | `$2269 bit 0x80` | obj 10 |
| TBD | ? | `$226a bit 0x01` | obj 11 |

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x93ec4c` | Act 1 finale/outro subroutine — loads 3 NPCs, explosion sequence, warps to Antiqua |
| `0x92d5bd` | Explosion/destruction visual effect (called 3 times in outro) |
| `0x92d607` | Post-explosion pause script |
| `0x92d915` | Outro setup script |
| `0x93e192` | BBM ride cinematic part 1 (controlled char) |
| `0x93e1a7` | BBM ride cinematic part 2 (non-controlled char) |
| `0x93e3c6` | Platform setup — main path variant |
| `0x93e432` | Non-controlled char drop + `$2834\|=0x04` |
| `0x93e74d` | Lava platform animation setup (takes `$245d` timing arg) |
| `0x93e758` | Mid-platform coordination walk |
| `0x93e795` | Landing/reset animation |

## Notes

- This is the **Act 1 transition room** — the only exit to Act 2 (Antiqua) is via `$22f1&0x40` (outro flag).
- 3 separate cave entrances to `0x35` (the cave complex), distinguished by `$234d` values 3, 4, 5.
- The lava platform system uses 8 platform objects (objs 0–7) shared across 21 step-on zones — multiple step-ons can reference the same platform obj.
- Platform variant `$24b7` (0–4) likely selects the platform visual/timing; `$245d` seems to be a per-platform timing constant (0x0040 for most, 0x0044 for outer ones, 0x0062 for the deepest).
- `$22ec bit 0x10` (BBM ride done) is **consumed** in this room — cleared after the entry cinematic plays.
- `$2264 bit 0x04` (Gauge) is the 3rd key item in `$2264` (wheel=`0x08`, TODO first bits).
- `$2834 bits 0x01/0x02/0x04` are set by various step-ons — their semantics unclear without further context.
- Sniff spot B-trigger list was partially read; ingredient assignments for most spots are TODO.
