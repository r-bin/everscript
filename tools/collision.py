#!/usr/bin/env python3
"""
Collision Word Decoder
----------------------
A faithful Python port of the engine's collision-word evaluator at `$909DE8`,
plus the plane bookkeeping at `$8FA914`.  Every rule here is read off the ROM
disassembly and confirmed against a Mesen2 CPU trace; nothing is inferred from
room ids, tile graphics or hand-built word lists.

Anatomy of the 16-bit collision word
------------------------------------
```
 15 14 13 12 11 10  9  8  7  6  5  4  3  2  1  0
  ?  ? AW  ? [ entity gate ]  0 PT [pln] [ geometry ]
```

| Field | Bits | Meaning |
|---|---|---|
| geometry | 3..0 | Sub-tile passability / slope, as before |
| plane | 5..4 | **Elevation plane, 0..3** |
| PT | 6 | Plane-transparent: walkable from any *other* plane |
| (unused) | 7 | Never set in any of the 390 584 vanilla tiles |
| entity gate | 11..8 | Active when bit 8 is set; see `entity_gate()` |
| AW | 13 | Always-walkable override: geometry is forced to 0 |
| unknown | 12, 15..14 | Read by the sprite-priority routine `$8FC780`; **UNVERIFIED** |

Evidence
--------
Mesen2 trace `drift.txt` (player carried along a sewer pipe in room `0x3D`,
frames 114092+), plus the ROM bytes at `$909DE8..$909E72` and `$8FA914`.

- **Plane is bits 5..4.** `$8FA914` is the only writer of the entity's plane
  field: `BIT #$2040 / BNE / AND #$0030 / STA $44`, and `$44` is copied to the
  entity record at `+$18` (`$8FC2E8`).  The evaluator then does
  `SEC / SBC $44 / AND #$0030 / BNE <mismatch>` — the tile's bits 5..4 must
  equal the entity's.  Trace: tile `$101F` with `$44 = $0010` → match.
- **Bit 13 forces walkability.** `BIT #$2000 / BNE $909E3A`, and `$909E3A`
  reads the 16-word table at `$909E73`, which is 32 bytes of `00` in the ROM
  (`$909E73..$909E92`, code resumes at `$909E93`).  So the returned geometry
  code is 0 for every low nibble.  This is what makes the sewer pipes, the
  volcano slides and the desert drift walkable despite geometry `0xF`, with no
  room-specific knowledge needed.
- **Bit 13 and bit 6 also suppress the plane update** (`BIT #$2040` above), so
  standing on one of those tiles leaves the entity on its previous plane.
- **Bit 6 is plane-transparency.** `$909E44`: `EOR $44 / AND #$0030 / BNE ->
  TDC / RTL` — a *different* plane returns geometry 0 (you pass straight
  through), the *same* plane returns the tile's own geometry.  That is the
  bridge/overpass rule.
- **Bits 11..8 gate by entity** when bit 8 is set.  `$909DEF..$909E1F` folds
  the nibble with `EOR #$0300`, `EOR #$0600`, `EOR #$0200` and compares the
  current entity pointer `$4C` against the two hardcoded slots `$4E89` and
  `$4F37`.  The trace identifies those: `$4E89` is the boy (`$8FC364
  CPY #$4E89`) and `$4F37` the dog (its `+$5E` "follow target" holds `$4E89`).

ROM-wide consistency check (all 127 vanilla rooms, 390 584 tiles)
-----------------------------------------------------------------
- Bit 7 is never set — consistent with bits 6..4 being the whole plane field.
- 104 of 127 rooms use exactly one plane.  The multi-plane rooms are the ones
  with bridges, overpasses and tunnels: `0x06` (all four planes), `0x69`,
  `0x3B` (volcano), `0x3D` (sewers), `0x1B` (desert), `0x22`, `0x4E`, and the
  `{0,1}` / `{1,2}` groups.  An elevation field behaves exactly like this; the
  previously assumed `(cw >> 12) >= 1` did not.
- The entity-gate nibble only ever takes the values 1, 3, 5, 7, 9 — and the
  disassembly only acts on 3, 5 and 7.

Not verified
------------
- **UNVERIFIED:** bits 12 and 15..14.  `$8FC780` reads bits 8..12 to pick a
  sprite attribute word (`$FC20` / `$CC20` / `$CC30`), i.e. draw order against
  the background, but the mapping was not pinned down.
- **UNVERIFIED:** what applies the sliding motion on bit-13 tiles.  `$9086AB`
  branches on bit 13 and calls the velocity helper `$8FAD51` with the entity's
  *own* facing (`+$22`) rather than anything from the tile — so the drift
  direction does not appear to be stored in the map data at all.  No direction
  arrows are drawn for that reason.
"""

from typing import Dict, Iterable, List, Set, Tuple

# --- Field accessors --------------------------------------------------------

GEOMETRY_MASK = 0x000F
PLANE_MASK = 0x0030
PLANE_TRANSPARENT = 0x0040
ENTITY_GATE_ACTIVE = 0x0100
ENTITY_GATE_MASK = 0x0F00
ALWAYS_WALKABLE = 0x2000

SOLID = 0x0F
OPEN = 0x00

# Entity slots the evaluator compares against, hardcoded in the ROM at
# $909E09 / $909E12 / $909E1B.
SLOT_BOY = 0x4E89
SLOT_DOG = 0x4F37


def tile_plane(cw: int) -> int:
    """Elevation plane 0..3 (bits 5..4)."""
    return (cw & PLANE_MASK) >> 4


def is_plane_transparent(cw: int) -> bool:
    """Bit 6: walkable from any plane other than the tile's own."""
    return bool(cw & PLANE_TRANSPARENT)


def is_always_walkable(cw: int) -> bool:
    """Bit 13: geometry forced to 0 via the all-zero table at $909E73."""
    return bool(cw & ALWAYS_WALKABLE)


def holds_plane(cw: int) -> bool:
    """True if standing here leaves the entity's plane unchanged ($8FA914)."""
    return bool(cw & (ALWAYS_WALKABLE | PLANE_TRANSPARENT))


def entity_gate(cw: int) -> int:
    """
    Entity-gate nibble (bits 11..8) when bit 8 is set, else -1.
    Values the evaluator acts on:
        3 -> solid for every entity except the boy and the dog
        5 -> solid for the dog
        7 -> solid for the boy and the dog
    Any other value falls through to the normal plane logic.
    """
    return ((cw & ENTITY_GATE_MASK) >> 8) if (cw & ENTITY_GATE_ACTIVE) else -1


GATE_BLOCKS: Dict[int, Set[str]] = {
    3: {"other"},
    5: {"dog"},
    7: {"boy", "dog"},
}


def passability(cw: int, entity_plane: int, entity: str = "boy") -> int:
    """
    Port of `$909DE8`.  Returns the 4-bit geometry code the engine would use:
    0x00 fully open, 0x0F fully solid, anything else a sub-tile slope/barrier.

    Args:
        cw:           the 16-bit collision word.
        entity_plane: the plane the entity is currently on, 0..3.
        entity:       "boy", "dog" or "other" (NPCs, enemies), for bit 8 gates.
    """
    plane_bits = (entity_plane & 0x03) << 4

    gate = entity_gate(cw)
    if gate in GATE_BLOCKS and entity in GATE_BLOCKS[gate]:
        return SOLID  # $909E64: LDA #$000F / RTL

    if cw & PLANE_TRANSPARENT:                      # $909E44
        if ((cw ^ plane_bits) & PLANE_MASK) != 0:
            return OPEN                             # $909E51: TDC / RTL
        return cw & GEOMETRY_MASK

    diff = (cw - plane_bits) & 0xFFFF               # $909E27: SEC / SBC $44
    if (diff & PLANE_MASK) == 0:                    # same plane
        return OPEN if (cw & ALWAYS_WALKABLE) else (cw & GEOMETRY_MASK)

    # $909E53: plane mismatch
    if (diff & 0x0020) == 0:                        # $909E68
        return OPEN if (cw & ALWAYS_WALKABLE) else SOLID
    if (diff & 0x0010) == 0:                        # $909E64
        return SOLID
    return SOLID                                    # $909E5D falls through here
                                                    # (its BIT #$0040 on $44 can
                                                    # never be true: $8FA914
                                                    # masks $44 with #$0030)


# --- Sub-tile geometry ------------------------------------------------------
# Which of a metatile's 16x16 pixels the geometry code blocks.  Unchanged from
# the previously verified mapping in docs/map_collision_mechanics.md §3.

def geometry_mask(code: int) -> bytes:
    """256-byte 16x16 mask, 1 = solid pixel, for a 4-bit geometry code."""
    out = bytearray(256)
    for py in range(16):
        for px in range(16):
            if code == 0x0F:
                s = True
            elif code == 0x00:
                s = False
            elif code in (0x02, 0x06):
                s = py >= px
            elif code in (0x01, 0x05):
                s = px + py >= 15
            elif code in (0x0A, 0x0E):
                s = px + py <= 15
            elif code in (0x09, 0x0D):
                s = py <= px
            elif code in (0x03, 0x04):
                s = py >= 8
            elif code in (0x0C, 0x0B):
                s = py < 8
            elif code == 0x08:
                s = px >= 8
            elif code == 0x07:
                s = px < 8
            else:
                s = False
            out[py * 16 + px] = 1 if s else 0
    return bytes(out)


GEOMETRY_MASKS: List[bytes] = [geometry_mask(c) for c in range(16)]

# Same data sliced into 16 rows of 16 bytes, so a renderer can stamp a tile
# with slice assignments instead of a per-pixel loop.
GEOMETRY_ROWS: List[List[bytes]] = [
    [m[py * 16:(py + 1) * 16] for py in range(16)] for m in GEOMETRY_MASKS
]


# --- Room-level helpers -----------------------------------------------------

def planes_used(collision_words: Iterable[Iterable[int]]) -> List[int]:
    """Sorted list of the elevation planes that occur in a room."""
    seen: Set[int] = set()
    for row in collision_words:
        for cw in row:
            seen.add(tile_plane(cw))
    return sorted(seen)


def plane_transition_tiles(collision_words: List[List[int]]) -> Set[Tuple[int, int]]:
    """
    Tiles that change the entity's elevation plane: a tile that sets a plane
    (i.e. neither bit 13 nor bit 6) and is orthogonally adjacent to another
    plane-setting tile with a *different* plane, where both are enterable on
    their own plane.  Ramps and stair runs show up as the join between the two
    plane regions.
    """
    h = len(collision_words)
    w = len(collision_words[0]) if h else 0
    out: Set[Tuple[int, int]] = set()

    def enterable(cw: int) -> bool:
        return passability(cw, tile_plane(cw)) != SOLID

    for y in range(h):
        for x in range(w):
            cw = collision_words[y][x]
            if holds_plane(cw) or not enterable(cw):
                continue
            p = tile_plane(cw)
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if not (0 <= nx < w and 0 <= ny < h):
                    continue
                ncw = collision_words[ny][nx]
                if holds_plane(ncw) or not enterable(ncw):
                    continue
                if tile_plane(ncw) != p:
                    out.add((x, y))
                    break
    return out
