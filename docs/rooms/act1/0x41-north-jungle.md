# 0x41 — North Jungle

**ROM:** `0x9ffeeb` | **Data:** `0xa5e6be` | **Enter:** `0x928160` → `0x93953f`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x7a` |
| Dog form | Wolf (`$2443 = 0x02`) |
| Map bounds | X: `0x0318`, Y: `0x0278` |
| Objects | 23 (2 gourds + 21 sniff spot markers) |
| NPCs | 16 (10 × NPC `0x0c` + 5 × NPC `0x0f` + 1 × NPC `0x1e` quest) |
| Step-on zones | 4 |
| B-triggers | 23 (21 sniff spots + 2 gourds) |
| Sniff spots | 21 |
| Drop table | Petal 10×, `0x0805` 5×, `0x0001` qty=12 2× |

## Connections

| Direction | Destination | Step-on Zone | Notes |
|-----------|-------------|--------------|-------|
| South | `0x25` Fire Eyes' Village @ `[0x02c8\|0x0068]` | `[09,36:0c,37]` | outdoor→outdoor |
| North | `0x27` Mammoth Graveyard @ `[0x0178\|0x02f8]` | `[30,12:34,14]` | outdoor→indoor |
| Northeast | `0x3c` Volcano Room 1 @ `[0x06a8\|0x04a8]` | `[2a,19:2c,1b]` | hut `$234b=0x0008` |
| Northwest | `0x3c` Volcano Room 1 @ `[0x02a0\|0x0588]` | `[0a,17:0c,19]` | hut `$234b=0x000a`, `$234d=0x0000` |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$225e` | `0x20` | 📖 | Checked in North Jungle (gates quest NPC position) |
| `$2268` | `0x10` | 🫙 | Nectar gourd collected (obj 1) — // MISMATCH: dumper labels as "Gourd in south Jungle" |
| `$2268` | `0x20` | 🫙 | Clay gourd collected (obj 0) — // MISMATCH: dumper labels as "Gourd in south Jungle" |
| `$22a1` | `0x40` | 👃 | Sniff #2 — Water |
| `$22a1` | `0x80` | 👃 | Sniff #3 — Water |
| `$22a2` | `0x01` | 👃 | Sniff #4 — Water |
| `$22a2` | `0x02` | 👃 | Sniff #5 — Water |
| `$22a2` | `0x04` | 👃 | Sniff #6 — Water |
| `$22a2` | `0x08` | 👃 | Sniff #7 — Water |
| `$22a2` | `0x10` | 👃 | Sniff #8 — Oil |
| `$22a2` | `0x20` | 👃 | Sniff #9 — Oil |
| `$22a2` | `0x40` | 👃 | Sniff #10 — Roots |
| `$22a2` | `0x80` | 👃 | Sniff #11 — Roots |
| `$22a3` | `0x01` | 👃 | Sniff #12 — Roots |
| `$22a3` | `0x02` | 👃 | Sniff #13 — Roots |
| `$22a3` | `0x04` | 👃 | Sniff #14 — Roots |
| `$22a3` | `0x08` | 👃 | Sniff #15 — Clay |
| `$22a3` | `0x10` | 👃 | Sniff #16 — Clay |
| `$22a3` | `0x20` | 👃 | Sniff #17 — Clay |
| `$22a3` | `0x40` | 👃 | Sniff #18 — Ash |
| `$22a3` | `0x80` | 👃 | Sniff #19 — Ash |
| `$22a4` | `0x01` | 👃 | Sniff #20 — Ash |
| `$22a4` | `0x02` | 👃 | Sniff #21 — Wax |
| `$22a4` | `0x04` | 👃 | Sniff #22 — Wax |

## Objects

| Obj | Unload Condition | Contents |
|-----|-----------------|----------|
| 0 | `$2268 & 0x20` | Clay gourd |
| 1 | `$2268 & 0x10` | Nectar gourd |
| 2–22 | `$22a1&0x40` … `$22a4&0x04` (in order) | Sniff spot markers |

## NPCs / Enemies

| NPC ID | Count | Positions | Notes |
|--------|-------|-----------|-------|
| `0x0c` | 10 | `(0f,35)` `(21,45)` `(27,35)` `(29,29)` `(39,2f)` `(49,33)` `(1d,2d)` `(33,15)` `(0b,21)` `(55,13)` | TODO: identify |
| `0x0f` | 5 | `(03,45)` `(39,4b)` `(5b,33)` `(1d,15)` `(5b,1f)` | TODO: identify; state 0400; `$2433` set to 2/3/3/7/2 before each load |
| `0x1e` | 1 | `(0x48,0x15)` or `(0x43,0x15)` | Quest NPC; position set by `$225e&0x20`; stored to `$2835` |

## Enemy Drop Table

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| 1 | Petal (`0x0800`) | 10 | default |
| 2 | `0x0805` | 5 | default |
| 3 | `0x0001` | 2 | 12 |

## Enter Script Summary

1. Set dog form to Wolf (`$2443=0x02`), map bounds X=`0x0318` Y=`0x0278`.
2. Engine registers: `$0ea2+0=0x40`, `$0eac+0=0x172b`; secondary NPC script `$0eac+4=0x17b5` (`$0ea2+4=0x01`).
3. Drop table: Petal 10×, `0x0805` 5×, `0x0001` qty=12 2×.
4. Unload sniff spot objs 2–22 if corresponding persistence bits are set (`$22a1&0x40` through `$22a4&0x04`).
5. Load 10× NPC `0x0c` at scattered positions.
6. Load 5× NPC `0x0f` (state 0400) at various positions, with `$2433` preset to 2, 3, 3, 7, 2 before each load respectively.
7. If NOT `$225e&0x20` (not yet "Checked"): load NPC `0x1e` (state 0002) at `(0x48, 0x15)`. Else: load at `(0x43, 0x15)`. Store entity to `$2835`.
8. **Animation branch:** If `$22eb&0x20` (indoor entry): teleport both to `(0x0f, 0x3f)`, fade out. Else clear `$22eb&0x20`.
9. Unload obj 1 if `$2268&0x10`; unload obj 0 if `$2268&0x20`.
10. If `$238d ≠ 0`: play music `0x7a`, fade in.
11. `$23bf = 0x0000`. Call `0x92de75`.

## Step-on Zones

| Zone | Destination | Condition | Notes |
|------|-------------|-----------|-------|
| `[09,36:0c,37]` | `0x25` Fire Eyes' Village @ `[0x02c8\|0x0068]` | always | south, outdoor→outdoor |
| `[30,12:34,14]` | `0x27` Mammoth Graveyard @ `[0x0178\|0x02f8]` | always | north, outdoor→indoor |
| `[2a,19:2c,1b]` | `0x3c` Volcano Room 1 @ `[0x06a8\|0x04a8]` | always | hut `$234b=0x0008` |
| `[0a,17:0c,19]` | `0x3c` Volcano Room 1 @ `[0x02a0\|0x0588]` | always | `$234b=0x000a`, `$234d=0x0000` |

## B-triggers (Sniff Spots)

| Zone | Ingredient | Flag | Map Ref |
|------|------------|------|---------|
| `[0a,2e:0b,2f]` | 💧 Water | `$22a1 bit 0x40` | `0x0002` |
| `[16,33:17,34]` | 💧 Water | `$22a1 bit 0x80` | `0x0003` |
| `[2a,2e:2b,2f]` | 💧 Water | `$22a2 bit 0x01` | `0x0004` |
| `[32,26:33,27]` | 💧 Water | `$22a2 bit 0x02` | `0x0005` |
| `[35,1f:36,20]` | 💧 Water | `$22a2 bit 0x04` | `0x0006` |
| `[15,19:16,1a]` | 💧 Water | `$22a2 bit 0x08` | `0x0007` |
| `[26,29:27,2a]` | 🛢 Oil | `$22a2 bit 0x10` | `0x0008` |
| `[1c,27:1d,28]` | 🛢 Oil | `$22a2 bit 0x20` | `0x0009` |
| `[0a,1e:0b,1f]` | 🌿 Roots | `$22a2 bit 0x40` | `0x000a` |
| `[1f,20:20,21]` | 🌿 Roots | `$22a2 bit 0x80` | `0x000b` |
| `[10,27:11,28]` | 🌿 Roots | `$22a3 bit 0x01` | `0x000c` |
| `[08,31:09,32]` | 🌿 Roots | `$22a3 bit 0x02` | `0x000d` |
| `[33,32:34,33]` | 🌿 Roots | `$22a3 bit 0x04` | `0x000e` |
| `[25,1c:26,1d]` | 🪨 Clay | `$22a3 bit 0x08` | `0x000f` |
| `[13,23:14,24]` | 🪨 Clay | `$22a3 bit 0x10` | `0x0010` |
| `[2f,18:30,19]` | 🪨 Clay | `$22a3 bit 0x20` | `0x0011` |
| `[22,27:23,28]` | 🌿 Ash | `$22a3 bit 0x40` | `0x0012` |
| `[29,31:2a,32]` | 🌿 Ash | `$22a3 bit 0x80` | `0x0013` |
| `[1b,34:1c,35]` | 🌿 Ash | `$22a4 bit 0x01` | `0x0014` |
| `[1b,30:1c,31]` | 🕯 Wax | `$22a4 bit 0x02` | `0x0015` |
| `[2f,23:30,24]` | 🕯 Wax | `$22a4 bit 0x04` | `0x0016` |

## B-triggers (Gourds)

| Zone | Contents | Flag | Obj |
|------|----------|------|-----|
| `[14,1c:16,1e]` | 🧪 Nectar (`0x0801`) × 3 | `$2268 bit 0x10` | obj 1 |
| `[25,2f:27,31]` | 🪨 Clay (`0x0210`) × 3 | `$2268 bit 0x20` | obj 0 |

## External Scripts

| Address | Trigger | Purpose |
|---------|---------|---------|
| `0x17b5` | Engine `$0eac+4` | Unnamed short NPC script (background NPC behavior) |

## Notes

- Two separate entrances into Volcano Room 1 (0x3c): NE via hut `0x0008`, NW via hut `0x000a`.
- NPC `0x1e` changes spawn position based on `$225e&0x20` ("Checked in North Jungle") — likely a quest NPC that moves after interaction.
- `$2433` is written to 2, 3, 3, 7, or 2 before each NPC `0x0f` load — this value likely controls the NPC's patrol/behavior variant.
- Sniff spot numbering starts at `#2` (`$22a1&0x40`), implying sniff spot `#1` (`$22a1&0x20`) belongs to an adjacent room's address space.
- // MISMATCH: Gourd persistence bits `$2268&0x10` and `$2268&0x20` are labeled "Gourd in south Jungle" by the dumper, but they appear in 0x41 (North Jungle). Same `$2268` byte is used by south jungle room 0x38 — possible label bleed-through or shared byte convention.
- 21 sniff spots across `$22a1`–`$22a4`: 6 Water, 2 Oil, 5 Roots, 3 Clay, 3 Ash, 2 Wax.
