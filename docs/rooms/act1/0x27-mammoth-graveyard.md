# 0x27 — Mammoth Graveyard

**ROM:** `0x9ffe83` | **Data:** `0xa6d67a` | **Enter:** `0x9280de` → `0x93e017`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x2a` |
| Dog form | Wolf (`$2443 = 0x02`) |
| Objects | 32 (obj 0 = boss guardian; obj 1–30 = sniff spots; obj 31 = intro VFX) |
| NPCs | 7 spawners + boss fight NPCs (loaded by trigger) |
| Step-on zones | 3 (N exit, S exit, boss trigger) |
| B-triggers | 30 (all sniff spots) |
| Sniff spots | 30 |
| Drop table | Petal 10×, `0x0001` qty=15 2×, Nectar 1× |

## Connections

| Direction | Destination | Step-on Zone | Notes |
|-----------|-------------|--------------|-------|
| South | `0x41` North Jungle @ `[0x02b0\|0x0028]` | `[22,3c:29,3e]` | outdoor→outdoor |
| North | `0x69` Volcano Path @ `[0x00d8\|0x04e8]` | `[26,16:28,17]` | outdoor→indoor |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$225f` | `0x04` | 📖 | Mammoth Graveyard fight unlocked (unloads obj 0; gates boss trigger) |
| `$2834` | `0x20` | 📖 | Mammoth boss trigger fired (one-shot) |
| `$22a4` | `0x08` | 👃 | Water sniff #3 |
| `$22a4` | `0x10` | 👃 | Water sniff #1 |
| `$22a4` | `0x20` | 👃 | Water sniff #19 |
| `$22a4` | `0x40` | 👃 | Water sniff #30 |
| `$22a4` | `0x80` | 👃 | Clay sniff #9 |
| `$22a5` | `0x01` | 👃 | Clay sniff #4 |
| `$22a5` | `0x02` | 👃 | Clay sniff #5 |
| `$22a5` | `0x04` | 👃 | Clay sniff #10 |
| `$22a5` | `0x08` | 👃 | Clay sniff #20 |
| `$22a5` | `0x10` | 👃 | Clay sniff #23 |
| `$22a5` | `0x20` | 👃 | Roots sniff #11 |
| `$22a5` | `0x40` | 👃 | Roots sniff #21 |
| `$22a5` | `0x80` | 👃 | Roots sniff #29 |
| `$22a6` | `0x01` | 👃 | Roots sniff #16 |
| `$22a6` | `0x02` | 👃 | Roots sniff #26 |
| `$22a6` | `0x04` | 👃 | Roots sniff #18 |
| `$22a6` | `0x08` | 👃 | Oil sniff #13 |
| `$22a6` | `0x10` | 👃 | Oil sniff #25 |
| `$22a6` | `0x20` | 👃 | Oil sniff #8 |
| `$22a6` | `0x40` | 👃 | Oil sniff #2 |
| `$22a6` | `0x80` | 👃 | Ash sniff #17 |
| `$22a7` | `0x01` | 👃 | Ash sniff #15 |
| `$22a7` | `0x02` | 👃 | Ash sniff #14 |
| `$22a7` | `0x04` | 👃 | Ash sniff #7 |
| `$22a7` | `0x08` | 👃 | Ash sniff #6 |
| `$22a7` | `0x10` | 👃 | Ash sniff #12 |
| `$22a7` | `0x20` | 👃 | Ash sniff #22 |
| `$22a7` | `0x40` | 👃 | Ash sniff #24 |
| `$22a7` | `0x80` | 👃 | Wax sniff #28 |
| `$22a8` | `0x01` | 👃 | Wax sniff #27 |

## Objects

| Obj | Unload Condition | Description |
|-----|-----------------|-------------|
| 0 | `$225f & 0x04` | Mammoth guardian (story-gated, removed when fight unlocked) |
| 1–30 | `$22a4&0x10` … `$22a8&0x01` (see sniff table) | Sniff spot markers |
| 31 | set state=`0x7e` during boss trigger | VFX object used in mammoth spirit intro |

## NPCs / Enemies

| NPC ID | Count | Spawn Type | Notes |
|--------|-------|-----------|-------|
| `0x22` | 7 | `c2` spawner | Mammoth-type enemy; `$2433=0x0001` preset |
| `0x2a` (type 42) | 1 | Loaded by boss trigger | Flying mammoth spirit (intro animation, then destroyed) |
| `0x29` (= `0x52>>1`) | 4 | Loaded by boss trigger | Mammoth Vipers; scripts `0x17d3/0x17d6/0x17d9/0x17dc` |
| `0x2a` (direct) | 1 | Loaded by boss trigger | Mammoth Viper Commander; script `0x17df`; stored to `$24a5` |

## Enemy Drop Table

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| 1 | Petal (`0x0800`) | 10 | default |
| 2 | `0x0001` | 2 | 15 |
| 3 | Nectar (`0x0801`) | 1 | default |

## Enter Script Summary

1. Dog = Wolf (`$2443=0x02`).
2. **Animation branch:** If `$22eb&0x20`: teleport both to `(0x2f, 0x59)`, fade out. Else clear `$22eb&0x20`.
3. `$2433=0x0001`; add 7× NPC `0x22` spawners at positions across the graveyard.
4. Unload objs 1–30 per sniff persistence bits (`$22a4&0x08` through `$22a8&0x01`).
5. Unload obj 0 if `$225f&0x04`.
6. Engine `$0eac+0=0x172b`.
7. Drop table: Petal 10×, `0x0001` qty=15 2×, Nectar 1×.
8. If `$238d ≠ 0`: play music `0x2a`, fade in.
9. `$23bf=0x0000`. Call `0x92de75`.

## Step-on Zones

| Zone | Destination | Notes |
|------|-------------|-------|
| `[22,3c:29,3e]` | `0x41` North Jungle @ `[0x02b0\|0x0028]` | south, outdoor→outdoor |
| `[26,16:28,17]` | `0x69` Volcano Path @ `[0x00d8\|0x04e8]` | north, outdoor→indoor |
| `[1e,24:25,25]` | Mammoth boss trigger | one-shot; see below |

### Boss Trigger (`0x93d913`)

1. **One-shot gate:** If `$2834&0x20` already set → return immediately. Else set `$2834|=0x20`.
2. **Story gate:** If NOT `$225f&0x04` → return (fight not yet unlocked).
3. Stop boy+dog; boy walks to `(0x2d, 0x25)`, dog walks to `(0x36, 0x25)`, both face north. YIELD.
4. Set camera/view registers: `$242f=0x0018`, `$242b=0x0108`, `$242d=0x00a0`.
5. Set obj 31 state = `0x7e` (VFX).
6. Load flying mammoth spirit (NPC `0x2a` state 0020) at `(0x32, 0x0f)` → store to `$283f`.
7. **Spirit fly-in:** sweep from `(0x0c80, 0x000f)` → moves Y downward → then X leftward via per-tick teleport loop.
8. **TEXT 05be:** *"You trespass in our bone land! Prepare to join the mammoths!"*
9. **Spirit fly-out:** reverse sweep upward-right.
10. Destroy `$283f`. Fade out; play music `0x5a`.
11. BOY+DOG = Player controlled; reset view (`$242b=0xffff`, `$242f=0x0080`).
12. Narrow map bounds: `$23df=0x0178`, `$23e1=0x0118` (left arena), then `0x01a8`/`0x0138` (right arena).
13. Load 4× Mammoth Viper (NPC `0x29`, state 0010) — 2 pairs at `(0x1d,0x1b)/(0x1d,0x1f)` and `(0x43,0x1d)/(0x43,0x1f)` with scripts `0x17d3/0x17d6/0x17d9/0x17dc`.
14. Load Mammoth Viper Commander (NPC `0x2a`, direct) at `(0x32, 0x09)`, face south; script `0x17df`; store to `$24a5`; make script-controlled.
15. Call `0x93d8dd` (Mammoth Viper Commander fight manager).

## B-triggers (Sniff Spots)

Ingredient counts: 4× Water · 6× Clay · 6× Roots · 4× Oil · 8× Ash · 2× Wax = 30 total

| Zone | Ingredient | Flag | Obj | Map Ref | Extra |
|------|------------|------|-----|---------|-------|
| `[1f,39:20,3a]` | 💧 Water | `$22a4 bit 0x10` | 1 | `0x0001` | — |
| `[2d,39:2e,3a]` | 💧 Water | `$22a4 bit 0x08` | 3 | `0x0003` | NEXT ADD=1 |
| `[3d,21:3e,22]` | 💧 Water | `$22a4 bit 0x20` | 19 | `0x0013` | NEXT ADD=2 |
| `[15,15:16,16]` | 💧 Water | `$22a4 bit 0x40` | 30 | `0x001e` | — |
| `[28,2c:29,2d]` | 🪨 Clay | `$22a4 bit 0x80` | 9 | `0x0009` | — |
| `[37,38:38,39]` | 🪨 Clay | `$22a5 bit 0x01` | 4 | `0x0004` | NEXT ADD=1 |
| `[1e,31:1f,32]` | 🪨 Clay | `$22a5 bit 0x02` | 5 | `0x0005` | NEXT ADD=2 |
| `[1d,2d:1e,2e]` | 🪨 Clay | `$22a5 bit 0x04` | 10 | `0x000a` | — |
| `[1d,1f:1e,20]` | 🪨 Clay | `$22a5 bit 0x08` | 20 | `0x0014` | — |
| `[1e,19:1f,1a]` | 🪨 Clay | `$22a5 bit 0x10` | 23 | `0x0017` | NEXT ADD=1 |
| `[12,2e:13,2f]` | 🌿 Roots | `$22a5 bit 0x20` | 11 | `0x000b` | NEXT ADD=2 |
| `[13,1e:14,1f]` | 🌿 Roots | `$22a5 bit 0x40` | 21 | `0x0015` | — |
| `[2a,15:2b,16]` | 🌿 Roots | `$22a5 bit 0x80` | 29 | `0x001d` | NEXT ADD=1 |
| `[25,24:26,25]` | 🌿 Roots | `$22a6 bit 0x01` | 16 | `0x0010` | — |
| `[39,19:3a,1a]` | 🌿 Roots | `$22a6 bit 0x02` | 26 | `0x001a` | NEXT ADD=3 |
| `[38,28:39,29]` | 🌿 Roots | `$22a6 bit 0x04` | 18 | `0x0012` | — |
| `[15,28:16,29]` | 🛢 Oil | `$22a6 bit 0x08` | 13 | `0x000d` | — |
| `[31,1d:32,1e]` | 🛢 Oil | `$22a6 bit 0x10` | 25 | `0x0019` | NEXT ADD=2 |
| `[2e,2c:2f,2d]` | 🛢 Oil | `$22a6 bit 0x20` | 8 | `0x0008` | — |
| `[19,37:1a,38]` | 🛢 Oil | `$22a6 bit 0x40` | 2 | `0x0002` | — |
| `[2c,25:2d,26]` | 🌿 Ash | `$22a6 bit 0x80` | 17 | `0x0011` | NEXT ADD=1 |
| `[29,28:2a,29]` | 🌿 Ash | `$22a7 bit 0x01` | 15 | `0x000f` | — |
| `[28,29:29,2a]` | 🌿 Ash | `$22a7 bit 0x02` | 14 | `0x000e` | — |
| `[36,2b:37,2c]` | 🌿 Ash | `$22a7 bit 0x04` | 7 | `0x0007` | — |
| `[29,30:2a,31]` | 🌿 Ash | `$22a7 bit 0x08` | 6 | `0x0006` | NEXT ADD=1 |
| `[14,2b:15,2c]` | 🌿 Ash | `$22a7 bit 0x10` | 12 | `0x000c` | — |
| `[1a,18:1b,19]` | 🌿 Ash | `$22a7 bit 0x20` | 22 | `0x0016` | — |
| `[24,19:25,1a]` | 🌿 Ash | `$22a7 bit 0x40` | 24 | `0x0018` | NEXT ADD=2 |
| `[2f,14:30,15]` | 🕯 Wax | `$22a7 bit 0x80` | 28 | `0x001c` | NEXT ADD=2 |
| `[36,14:37,15]` | 🕯 Wax | `$22a8 bit 0x01` | 27 | `0x001b` | NEXT ADD=1 |

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x93d8dd` | Mammoth Viper Commander fight manager (called at end of boss trigger) |
| `0x17d3` | Mammoth Viper 1 AI |
| `0x17d6` | Mammoth Viper 2 AI |
| `0x17d9` | Mammoth Viper 3 AI |
| `0x17dc` | Mammoth Viper 4 AI |
| `0x17df` | Mammoth Viper Commander AI |

## Notes

- Largest sniff spot count in Act 1 (30 spots; compare to 34 in 0x67).
- The "NEXT ADD" value written to `$2461` before some loot calls likely sets an additional ingredient quantity or secondary bonus — consistent with higher-value spots being more generous.
- `$225f bit 0x04` is the fight unlock flag; its setter has not been found yet. TODO: identify where this flag is set.
- The flying mammoth spirit intro NPC (`0x2a`) uses positional teleport loops (`$2841/$2845`) for a custom fly-in animation — unusual engine use.
- Mammoth Viper Commander is loaded directly (`ba` opcode, NPC type `0x2a`) while vipers use the packed `3c` opcode (NPC type `0x29` = `0x52>>1`).
- `$2834 bit 0x20` ensures the boss intro cutscene fires only once per save.
