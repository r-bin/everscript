# Secret of Evermore Map Collision Mechanics

How the engine decides whether an entity can enter a metatile, decoded from the
ROM routine that does it.

> **Status.** §2–§5 are a line-by-line reading of `$909DE8` and `$8FA914`,
> cross-checked against a Mesen2 CPU trace and against all 390 584 collision
> words in the 127 vanilla rooms. Anything not established that way is marked
> **UNVERIFIED**. See `AGENTS.md` §1.
>
> **This document replaces an earlier version that was wrong** about the upper
> bits. If you remember "bits 15..12 = elevation plane", "bit 4 = active flag",
> or per-room drift/pipe/slide word lists, discard them — [§8](#8-what-the-previous-version-got-wrong)
> explains why.

---

## 1. Storage

Payload Block 3 decompresses into three planar slices of `W × H` words:

- **Slice 0** — Layer 1 (canopy) tilemap words
- **Slice 1** — Layer 2 (terrain) tilemap words
- **Slice 2** — **collision words**

In WRAM the three are interleaved into 8-byte metatile records, so a metatile
ID doubles as its own byte offset: `$7F0000 + id` is the Layer 1 word, `+2`
Layer 2, and **`+4` the collision word**. Every read in §3 is a `LDA $7F0004,X`
with `X` = the metatile ID.

The same structure is used by all 127 rooms.

---

## 2. Anatomy of the 16-bit collision word

```
 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
  ?  ? AW  ? [ entity gate ]  0 PT [pln] [geometry]
```

| Field | Bits | Meaning |
|---|---|---|
| **geometry** | 3..0 | Sub-tile passability and slope, see §5 |
| **plane** | 5..4 | **Elevation plane, 0..3** |
| **PT** | 6 | Plane-transparent — walkable from any *other* plane |
| — | 7 | Never set in any vanilla tile |
| **entity gate** | 11..8 | Active when bit 8 is set, see §4 |
| **AW** | 13 | Always-walkable override — geometry forced to 0 |
| unknown | 12, 15..14 | Read by the sprite-priority routine `$8FC780`. **UNVERIFIED** |

---

## 3. The evaluator, `$909DE8`

Input: the collision word in `$50`, the entity's current plane in `$44`
(as bits 5..4, i.e. `$00`/`$10`/`$20`/`$30`). Output: a 4-bit geometry code,
`$00` fully open through `$0F` fully solid.

```asm
909DE8  LDA $50
909DEA  BIT #$0100        ; entity gate active?
909DED  BEQ $909E22
        ...               ; §4
909E22  BIT #$0040        ; plane-transparent?
909E25  BNE $909E44
909E27  SEC
909E28  SBC $44           ; compare the tile's plane against the entity's
909E2A  AND #$0030
909E2D  BNE $909E53       ; plane mismatch
909E2F  LDA $50
909E31  BIT #$2000        ; always-walkable?
909E34  BNE $909E3A
909E36  AND #$000F        ; normal: the tile's own geometry
909E39  RTL
909E3A  AND #$000F
909E3D  ASL
909E3E  TAX
909E3F  LDA $909E73,X     ; table is 32 bytes of 00 -> always returns 0
909E43  RTL
909E44  EOR $44           ; plane-transparent path
909E46  AND #$0030
909E49  BNE $909E51
909E4B  LDA $50
909E4D  AND #$000F        ; same plane -> normal geometry
909E50  RTL
909E51  TDC               ; other plane -> A = 0, fully open
909E52  RTL
909E53  BIT #$0020        ; plane mismatch
909E56  BEQ $909E68
909E58  BIT #$0010
909E5B  BEQ $909E64
909E5D  LDA $44
909E5F  BIT #$0040
909E62  BNE $909E2F
909E64  LDA #$000F        ; solid
909E67  RTL
909E68  LDA $50
909E6A  BIT #$2000
909E6D  BNE $909E3A
909E6F  LDA #$000F        ; solid
909E72  RTL
```

Three rules fall out:

1. **Plane must match.** Bits 5..4 of the tile must equal the entity's plane,
   or the tile is solid. This is what lets a bridge and the tunnel beneath it
   occupy the same coordinates.
2. **Bit 13 forces the tile open.** `$909E73` is 32 bytes of `00` in the ROM
   (`$909E73..$909E92`; code resumes at `$909E93`), so the lookup returns 0 for
   every low nibble. Sewer pipes, volcano slides and desert quicksand are
   geometry `0xF` tiles made walkable this way — no room-specific knowledge is
   needed to find them.
3. **Bit 6 makes a tile transparent to other planes.** Same plane → the tile's
   own geometry; different plane → fully open, you walk straight through.

### 3.1 Who sets the entity's plane

`$8FA914` is the only writer:

```asm
8FA914  BIT #$2040        ; bit 13 or bit 6 set?
8FA917  BNE $8FA91F       ; -> leave the plane alone
8FA919  AND #$0030
8FA91C  STA $44
```

`$44` is then stored into the entity record at `+$18` (`$8FC2E8`). So standing
on an always-walkable or plane-transparent tile **keeps** your current plane;
only ordinary tiles change it. An elevation transition therefore happens where
two ordinary walkable tiles of different planes meet — that is what
`tools/collision.py::plane_transition_tiles` marks.

---

## 4. Entity gates (bits 11..8)

When bit 8 is set, `$909DEF..$909E1F` folds the nibble with `EOR #$0300`,
`EOR #$0600`, `EOR #$0200` and compares the current entity pointer `$4C`
against two hardcoded slots — `$4E89` (the boy) and `$4F37` (the dog):

| Nibble | Effect |
|---|---|
| `3` | Solid for everything **except** the boy and the dog |
| `5` | Solid for **the dog** |
| `7` | Solid for **the boy and the dog** (enemies and NPCs pass) |
| `1`, `9` | No gate; falls through to the plane logic |

Across all vanilla rooms the nibble only ever takes the values 1, 3, 5, 7, 9.

---

## 5. Sub-tile geometry (bits 3..0)

Unchanged and still correct. `0x0` is fully open, `0xF` fully solid; the rest
are 45° slopes and half-tile barriers:

| Code | Solid where |
|---|---|
| `0x02`, `0x06` | `py >= px` (SW) |
| `0x01`, `0x05` | `px + py >= 15` (SE) |
| `0x0A`, `0x0E` | `px + py <= 15` (NW) |
| `0x09`, `0x0D` | `py <= px` (NE) |
| `0x03`, `0x04` | `py >= 8` (top barrier) |
| `0x0C`, `0x0B` | `py < 8` (bottom barrier) |
| `0x08` | `px >= 8` (west barrier) |
| `0x07` | `px < 8` (east barrier) |

---

## 6. Drift and sliding

Bit 13 marks the tiles, but **the direction is not in the map data.**
`$9086AB` branches on bit 13 and calls the velocity helper `$8FAD51` with the
entity's own facing (`entity + $22`), not with anything read from the tile:

```asm
9086AB  LDA $003C,Y       ; the entity's cached collision word
9086AE  BIT #$2000
9086B1  BEQ $9086C0
9086B3  STZ $02
9086B5  LDA $0022,Y       ; the entity's own facing
9086B8  STA $04
9086BA  JSL $8FAD51
```

So a static map tool cannot draw drift arrows. `tools/render_map.py`
deliberately draws none; it shades bit-13 tiles and leaves direction out.

**UNVERIFIED:** the remaining details of how momentum is maintained and how
corners redirect the entity.

---

## 7. ROM-wide consistency

Checked over all 127 rooms / 390 584 tiles:

- Bit 7 is never set, consistent with bits 6..4 being the whole plane field.
- **104 of 127 rooms use exactly one plane** (plane 1). The multi-plane rooms
  are precisely the ones with bridges, overpasses and tunnels: `0x06` uses all
  four; `0x69` uses 1/2/3; `0x3B` (volcano), `0x17`, `0x19`, `0x2F`, `0x3C`,
  `0x4F`, `0x59`, `0x65` use 1/2; `0x1B` (desert), `0x28`, `0x2D`, `0x31`,
  `0x3D` (sewers), `0x46`, `0x54`, `0x77` use 0/1.
- Every tile the old per-room "pipe" hardcode listed for room `0x3D` — all 676
  of them — is exactly the bit-13 set. Eight of the nine hand-listed
  drift/slide words are bit-13 tiles; the ninth, `0x5010`, is plain open floor
  and was a mistake in that list.

---

## 8. What the previous version got wrong

| Old claim | Reality |
|---|---|
| Bits 15..12 are the elevation plane, `(cw >> 12) >= 1` means "elevated" | The plane is bits 5..4. The old test put 84% of all tiles on "plane 1"; a single-floor room like `0x34` had 13% of its walkable neighbour pairs "changing elevation", which is impossible |
| Bit 4 is an "active/interactive terrain" flag | Bit 4 is the low bit of the plane field |
| `(cw >> 4) & 0x0F in (5, 6)` identifies stairs | That tests plane + bit 6, i.e. it selects *plane-transparent* tiles. This is why the old renderer drew "stair rungs" across corridor intersections |
| Drift/pipe/slide tiles need per-room word lists | Bit 13 identifies all of them, everywhere |
| `0x4010` is not a doorway opcode | Still true — warps come from step-on trigger records, not the collision word |

---

## 9. Tooling

`tools/collision.py` is a faithful port of §3–§5 with no room-specific
knowledge:

| Symbol | Purpose |
|---|---|
| `passability(cw, entity_plane, entity="boy")` | Port of `$909DE8` |
| `tile_plane(cw)` | Bits 5..4 |
| `is_always_walkable(cw)` / `is_plane_transparent(cw)` | Bits 13 / 6 |
| `holds_plane(cw)` | Port of the `BIT #$2040` test in `$8FA914` |
| `entity_gate(cw)`, `GATE_BLOCKS` | §4 |
| `GEOMETRY_MASKS`, `GEOMETRY_ROWS` | §5, as 16×16 pixel masks |
| `planes_used(grid)`, `plane_transition_tiles(grid)` | Room-level helpers |

`tools/render_map.py --layer composition` draws every plane's contour in its
own colour — the dominant plane solid, the others dashed — so a tunnel and the
bridge above it appear as two crossing outlines rather than one merged blob.
Plane-transparent tiles, always-walkable tiles, elevation changes and entity
gates each get their own shading, and the header banner lists the counts.
