# 0x3c — Volcano Room 1

**ROM:** `0x9ffed7` | **Data:** `0xa2a161` | **Enter:** `0x928147` → `0x949fa1`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x08` (normal) or `0x5c` (section 10 only) |
| Map bounds | 11 viewport sections, indexed by `$234b` (see below) |
| Objects | 0–23 (gourds + sniff spots across all sections) |
| NPCs | 1 "Speed dude" always + 1 special (section 10) + 13× NPC `0x29` spawners |
| Step-on zones | 21 (16 internal section transitions + 5 external exits) |
| B-triggers | 25 (10 gourds with 1 duplicate + 14 sniff spots + 1 duplicate) |

## Viewport Sections

0x3c is a single large cave map spanning the inside of the volcano. The `$234b` register acts as an entrance index, selecting a viewport sub-area on entry.

| `$234b` | X range | Y range | Notes |
|---------|---------|---------|-------|
| 1 | 0x0000–0x0150 | 0x0020–0x01e0 | |
| 2 | 0x01d0–0x0340 | 0x0040–0x01c0 | |
| 3 | 0x03c0–0x0580 | 0x0030–0x01c0 | |
| 4 | 0x05f0–0x07e0 | 0x0020–0x01b0 | |
| 5 | 0x0050–0x0180 | 0x01e0–0x03e0 | |
| 6 | 0x0200–0x0400 | 0x01c0–0x0360 | |
| 7 | 0x0460–0x0590 | 0x0230–0x03e0 | |
| 8 | 0x05a0–0x07c0 | 0x01e0–0x04b0 | |
| 9 | 0x0008–0x0158 | 0x0418–0x0588 | |
| 10 | 0x01f8–0x0360 | 0x0448–0x0590 | Different music; special NPC |
| 11 | 0x05d0–0x07c0 | 0x01e0–0x04b0 | |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| Exit south A | `0x41` North Jungle @ `[0x0040\|0x0078]` | step-on `[29,5a:2b,5c]` | music fade |
| Exit south B | `0x41` North Jungle @ `[0x0240\|0x0098]` | step-on `[68,4c:6d,4e]` | music fade |
| Exit to Rm 2 A | `0x3b` Volcano Room 2 @ `[0x03e8\|0x0588]` | step-on `[0f,45:11,47]` | sets `$225e\|=0x40` |
| Exit to Rm 2 B | `0x3b` Volcano Room 2 @ `[0x0170\|0x0028]` | step-on `[0d,1f:0f,21]` | |
| Exit to Rm 2 C | `0x3b` Volcano Room 2 @ `[0x0288\|0x0588]` | step-on `[68,21:6b,23]` | |
| Internal × 16 | `0x3c` self (various sections) | see step-on table | sets `$234b` before re-entering |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$225e` | `0x40` | 📖 | Viper Commander spawn trigger — **SET** by exit step-on `[0f,45:11,47]` → 0x3b |
| `$22ee` | `0x01` | 📖 | Volcano Room 1 intro flag (gates initial section 11 entry teleport) |
| `$226e` | `0x80` | 🫙 | Gourd MAP REF 0x00 looted (Ash) |
| `$226f` | `0x01` | 🫙 | Gourd MAP REF 0x01 looted (Wax) |
| `$226f` | `0x02` | 🫙 | Gourd MAP REF 0x02 looted (Water) |
| `$226f` | `0x04` | 🫙 | Gourd MAP REF 0x03 looted (Call Beads) |
| `$226f` | `0x08` | 🫙 | Gourd MAP REF 0x05 looted (Ash) |
| `$226f` | `0x10` | 🫙 | Gourd MAP REF 0x04 looted (Ash) |
| `$226f` | `0x20` | 🫙 | Gourd MAP REF 0x06 looted (Wax) |
| `$226f` | `0x40` | 🫙 | Gourd MAP REF 0x07 looted (Water) |
| `$22b1` | `0x80` | 🫙 | Gourd MAP REF 0x15 looted (Wax) |
| `$22b2` | `0x01` | 🫙 | Gourd MAP REF 0x16 looted (Wax) |
| `$22af` | `0x01` | 👃 | Sniffed Water (#8) |
| `$22af` | `0x02` | 👃 | Sniffed Water (#9) |
| `$22af` | `0x04` | 👃 | Sniffed Clay (#10) |
| `$22af` | `0x08` | 👃 | Sniffed Roots (#11) |
| `$22af` | `0x10` | 👃 | Sniffed Roots (#12) |
| `$22af` | `0x20` | 👃 | Sniffed Roots (#13) |
| `$22af` | `0x40` | 👃 | Sniffed Roots (#14) |
| `$22af` | `0x80` | 👃 | Sniffed Oil (#15) |
| `$22b0` | `0x01` | 👃 | Sniffed Oil (#16) |
| `$22b0` | `0x02` | 👃 | Sniffed Oil (#17) |
| `$22b0` | `0x04` | 👃 | Sniffed Ash (#23) |
| `$22b0` | `0x08` | 👃 | Sniffed Wax (#18) |
| `$22b0` | `0x10` | 👃 | Sniffed Wax (#19) |
| `$22b0` | `0x20` | 👃 | Sniffed Wax (#20) |

## NPCs / Enemies

| NPC ID | Count | Position(s) | State | Notes |
|--------|-------|-------------|-------|-------|
| `0x24` | 1 | `(0xef, 0x29)` | `0002` | "Speed dude" — talk script `0x1803`; always loaded (except section 10) |
| `0x07` | 1 | `(0x55, 0x9f)` | — | "Volcano Room1 NPC 1" — talk script `0x1806`; **only in section 10** (`$234b==10`) |
| `0x29` | 13 spawners | scattered | `0x0001` | Mammoth Viper enemy; positions: `(0d,25)`,`(4b,29)`,`(83,27)`,`(9f,1b)`,`(d1,1d)`,`(e3,5d)`,`(c9,61)`,`(99,61)`,`(65,59)`,`(4d,63)`,`(19,55)`,`(25,6b)`,`(1f,9f)` |

## Drop Table

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| Prize 1 | Petal (`0x0800`) | 10 | 1 |
| Prize 2 | `0x0001` | 2 | 15 |
| Prize 3 | Nectar (`0x0801`) | 1 | 1 |

## Enter Script Summary

1. Set engine hooks `$0eac+8=0x178b`, `$0eac+0=0x172b`; prize table.
2. If `$22ee&0x01`: clear flag, set `$234b=0x0004`, teleport both to `(0xeb, 0x29)`.
3. Select viewport based on `$234b` value (1–11).
4. If `$234b==10`: load NPC `0x07` at `(0x55, 0x9f)` (talk script `0x1806`), set `$23bf=0x0001`; play music `0x5c`.
5. Otherwise: load 13× NPC `0x29` spawners + NPC `0x24` "Speed dude"; play music `0x08`.
6. Unload looted gourds/sniff spots (`$226e&0x80`, `$226f`, `$22af`, `$22b0`, `$22b1&0x80`, `$22b2&0x01`).
7. Call cinematic entry. End.

## Step-on Zones

### External Exits

| Zone | Destination | Notes |
|------|-------------|-------|
| `[29,5a:2b,5c]` | `0x41` North Jungle | Fade music; Global 0x21 |
| `[68,4c:6d,4e]` | `0x41` North Jungle | Fade music; Global 0x21 |
| `[0f,45:11,47]` | `0x3b` Volcano Room 2 @ `[0x03e8\|0x0588]` | **Sets `$225e\|=0x40`** (Viper Commander spawn); Global 0x26 |
| `[0d,1f:0f,21]` | `0x3b` Volcano Room 2 @ `[0x0170\|0x0028]` | Global 0x21 |
| `[68,21:6b,23]` | `0x3b` Volcano Room 2 @ `[0x0288\|0x0588]` | Global 0x26 |

### Internal Section Transitions (16 tunnels)

| Zone | `$234b` set | Destination in 0x3c | Direction |
|------|-------------|---------------------|-----------|
| `[32,10:34,13]` | 1 | `[0x0008\|0x0120]` | East→West |
| `[00,14:02,17]` | 2 | `[0x0338\|0x00e0]` | West→East |
| `[4e,05:50,07]` | 2 | `[0x0260\|0x01b0]` | North |
| `[0d,21:0f,23]` | 3 | `[0x0420\|0x01b8]` | North |
| `[67,05:69,07]` | 3 | `[0x04f0\|0x01b8]` | North |
| `[25,1d:27,1f]` | 3 | `[0x04f0\|0x0028]` | South |
| `[4e,1d:50,1f]` | 4 | `[0x0680\|0x0028]` | South |
| `[25,1f:27,21]` | 5 | `[0x0110\|0x03d8]` | North |
| `[41,1d:43,1f]` | 5 | `[0x00e0\|0x01e8]` | South |
| `[10,3f:12,41]` | 6 | `[0x0260\|0x01c8]` | North |
| `[4e,3f:50,41]` | 6 | `[0x0300\|0x01c8]` | North |
| `[5d,30:5f,33]` | 6 | `[0x03f8\|0x0300]` | West |
| `[2f,1f:31,21]` | 7 | `[0x04f0\|0x03d8]` | North |
| `[7a,30:7c,32]` | 9 | `[0x0008\|0x0518]` | East |
| `[3e,32:40,35]` | 11 | `[0x05d8\|0x02e8]` | East |
| `[00,53:02,56]` | 11 | `[0x07b8\|0x02d8]` | West |

## Gourds

| MAP REF | Zone | Contents | Flag | `$2461` |
|---------|------|----------|------|---------|
| 0x0000 | `[4d,31:4f,33]` | 💨 Ash | `$226e&0x80` | 0x0002 |
| 0x0001 | `[4e,33:50,35]` | 🕯️ Wax | `$226f&0x01` | 0x0001 |
| 0x0002 | `[65,13:67,15]` | 💧 Water | `$226f&0x02` | 0x0002 |
| 0x0003 | `[5d,40:5f,42]` | 📿 Call Beads | `$226f&0x04` | 0x0000 |
| 0x0004 | `[0a,33:0c,35]` | 💨 Ash | `$226f&0x10` | 0x0003 |
| 0x0005 | `[0d,15:0f,17]` | 💨 Ash | `$226f&0x08` | 0x0003 |
| 0x0006 | `[75,14:77,16]` | 🕯️ Wax | `$226f&0x20` | 0x0004 |
| 0x0007 | `[73,15:75,17]` | 💧 Water | `$226f&0x40` | 0x0005 |
| 0x0015 | `[28,50:2a,52]` | 🕯️ Wax | `$22b1&0x80` | — |
| 0x0016 | `[2a,4f:2c,51]` | 🕯️ Wax | `$22b2&0x01` | 0x0002 |

## Sniff Spots

| # | Zone | Ingredient | Flag |
|---|------|------------|------|
| 8 | `[0c,0f:0d,10]` | 💧 Water | `$22af&0x01` |
| 9 | `[20,32:21,33]` | 💧 Water | `$22af&0x02` |
| 10 | `[08,2b:09,2c]` | 🏺 Clay | `$22af&0x04` |
| 11 | `[3e,0f:3f,10]` | 🌿 Roots | `$22af&0x08` |
| 12 | `[2a,2b:2b,2c]` | 🌿 Roots | `$22af&0x10` |
| 13 | `[74,34:75,35]` | 🌿 Roots | `$22af&0x20` |
| 14 | `[26,4f:27,50]` | 🌿 Roots | `$22af&0x40` |
| 15 | `[29,12:2a,13]` | 🛢️ Oil | `$22af&0x80` |
| 16 | `[4e,2f:4f,30]` | 🛢️ Oil | `$22b0&0x01` |
| 17 | `[0b,54:0c,55]` | 🛢️ Oil | `$22b0&0x02` |
| 18 | `[54,13:55,14]` | 🕯️ Wax | `$22b0&0x08` |
| 19 | `[17,34:18,35]` | 🕯️ Wax | `$22b0&0x10` |
| 20 | `[67,2d:68,2e]` | 🕯️ Wax | `$22b0&0x20` |
| 23 | `[68,15:69,16]` | 💨 Ash | `$22b0&0x04` |

**Summary:** Water×2, Clay×1, Roots×4, Oil×3, Wax×3, Ash×1 = 14 sniff spots.

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x1803` | "Speed dude" NPC talk script |
| `0x1806` | "Volcano Room1 NPC 1" talk script (section 10 only) |

## Notes

- This room is actually one continuous cave map; the `$234b` entrance index just scrolls the viewport to the correct sub-area. The same enter script handles all sections.
- **`$225e&0x40`** is set by the upper-left exit to 0x3b (`[0f,45:11,47]`). Based on naming ("Viper Commander spawn?"), this flag likely gates a special NPC or boss encounter in 0x3b. — MISMATCH: flag name in dump says "Viper Commander spawn?" — unconfirmed.
- **Section 10** (`$234b=10`) has different music (`0x5c`) and a different NPC (`0x07`). This may be a special cutscene area or sub-boss area. Setting `$23bf=0x0001` suggests a water/parallax visual effect.
- The "Speed dude" (NPC `0x24`, talk script `0x1803`) is loaded at `(0xef, 0x29)` in the large northeast section of the map. He appears when `$234b != 10`.
- **`$2461`** is written alongside most gourd pickups with values 0–5. This appears to be a "which compartment opens next" tracker or NPC reward slot. — TODO: identify `$2461` fully.
- Gourd MAP REF 0x0005 entry is duplicated in the B-trigger table (same zone, same flag) — this is an error/redundancy in the original script.
- Sniff spots #21 and #22 are not present in this room (MAP REFs 0x0015 and 0x0016 are gourds, not sniff spots). The sniff spot gap (#21–#22) may belong to an adjacent room or be unused.
