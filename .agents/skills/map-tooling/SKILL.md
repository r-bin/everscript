---
name: map-tooling
description: How to read, render, edit and write back Secret of Evermore room data using tools/dump_room.py, encode_room.py, render_map.py, collision.py and cuttable_grass.py. Use when inspecting a room, producing map PNGs, or changing map data in the ROM.
---

# Map Tooling Workflow

The practical runbook for `tools/*.py`. For the *format* these tools implement, see the
`rom-map-data` skill and the documents it indexes — this skill is about driving the tools.

> [!IMPORTANT]
> These tools are the authoritative implementation of the map format. They round-trip every one
> of the 127 vanilla rooms byte-exactly (`encode_room.py --verify`). **Do not re-derive map
> decoding by hand, and do not write a second implementation** — if something is wrong, fix it
> here so every consumer gets the fix.

---

## 1. The five modules

| Module | Role | Has a CLI |
|---|---|---|
| `tools/dump_room.py` | Decode a room blob → a Python dict of header, triggers, objects, metatile grid, VRAM words, collision words | Yes |
| `tools/encode_room.py` | The inverse: model → blob bytes, and write it back into a ROM | Yes |
| `tools/render_map.py` | Decoded room → PNG (layers, composite, collision overlay, full composition) | Yes |
| `tools/collision.py` | Decode a collision word (plane, geometry, drift, entity gates) | Library only |
| `tools/cuttable_grass.py` | Decode the metatile swap table | Library only |

`dump_room()` already calls `collision.planes_used()` and `cuttable_grass.find_cuttable_grass_tiles()`,
so the common derived data is on the result dict without extra work.

---

## 2. Reading a room

```bash
python3 tools/dump_room.py 0x38              # summary: size, triggers, objects, planes, grass
python3 tools/dump_room.py 0x38 --header     # metadata only, no big grids
python3 tools/dump_room.py 0x38 --objects    # list every Section 3 object and its states
python3 tools/dump_room.py 0x38 --json       # full model as JSON
python3 tools/dump_room.py --all             # decode all 127 rooms, report failures
```

Programmatically:

```python
from tools.dump_room import dump_room
room = dump_room(0x38)

room["header"]["width_tiles"], room["header"]["height_tiles"]
room["layer1_metatile_ids"][y][x]     # hex strings, e.g. "0x3B02"
room["collision_int_words"][y][x]     # ints
room["objects"][i]["states"][s]["metatiles"]
room["triggers"]["b_trigger"][i]["script_id"]   # matches script_all's "id:" field
room["elevation_planes"], room["elevation_plane_count"]
room["cuttable_grass_tiles"], room["cuttable_grass_table"]
room["cuttable_grass_warnings"]       # should be empty; non-empty means a malformed swap table
```

> [!CAUTION]
> Grid values in `layer1_metatile_ids`, `layer1_vram_words`, `layer2_vram_words` and
> `collision_words` are **hex strings**; the `*_int_words` variants are ints. Mixing them up
> silently produces wrong results rather than an error — prefer the `_int_words` forms in code.

### Collision words

Never interpret a collision word by hand — the bitfield is not obvious and an earlier
hand-reading of it was wrong for years:

```python
from tools.collision import (passability, tile_plane, drift_vector,
                             entity_gate, is_always_walkable, planes_used, SOLID)

cw = room["collision_int_words"][y][x]
tile_plane(cw)                  # elevation plane 0..3 (bits 5..4)
passability(cw, entity_plane=1) # geometry code as $909DE8 would return it
drift_vector(cw)                # (dx, dy, "NE") for drift tiles, else (0, 0, "")
entity_gate(cw)                 # 3/5/7 gate nibble, or -1
```

---

## 3. Rendering

```bash
python3 tools/render_map.py 0x38                       # layer1, layer2, composite, composition
python3 tools/render_map.py 0x38 --layer composition   # the all-in-one annotated view
python3 tools/render_map.py 0x38 --collision --collision-mode verbose
python3 tools/render_map.py --all-rooms -o out/maps    # every room
```

The **composition** layer is the one to reach for when debugging map data: it draws per-plane
collision contours (dominant plane solid, others dashed), drift arrows, plane-transparent and
elevation-change tiles, cuttable grass, object stamps and trigger boxes, with a header banner and
legend. Objects and triggers are labelled with the indices `script_all` uses, so a box in the PNG
can be matched to a script by eye.

---

## 4. Writing a room back

```bash
python3 tools/encode_room.py --verify           # byte-exact round-trip, all 127 rooms
python3 tools/encode_room.py --verify-rebuild   # re-encoded round-trip, all 127 rooms
python3 tools/encode_room.py 0x38 --rebuild --compress --out room38.bin
```

The editing path:

```python
from tools.dump_room import dump_room, DEFAULT_ROM_PATH
from tools.encode_room import rebuild_model, build_blob, write_room_into_rom

rom  = open(DEFAULT_ROM_PATH, "rb").read()
room = dump_room(0x38)

# ... edit room["layer1_metatile_ids"], room["collision_int_words"], room["objects"] ...

blob          = build_blob(rebuild_model(rom, 0x38, room))
new_rom, off  = write_room_into_rom(rom, 0x38, blob)     # in place, or pass at_offset=...
```

Rules worth knowing before editing:

- **A rebuilt blob is never larger than the original** for any vanilla room, so an in-place write
  always fits if you did not add content. `write_room_into_rom` raises rather than overflowing
  into the next room; pass `at_offset=` to relocate and repoint `$9FFDE7`.
- **New metatile IDs must be introduced in ascending order** across the grid — the Markov encoder
  widens its literal field only via the sequential token. Violating this raises `ValueError` from
  `encode_markov_grid` rather than producing a corrupt stream.
- **Run `validate`-equivalent checks before writing**: the same assertions live in
  `tests/integration/maps/test_encode_room.py`; `--verify-rebuild` runs them across the ROM.

---

## 5. Tests

```bash
.venv/bin/pytest tests/integration/maps/ -v
```

Covers VRAM ground truth against Mesen2 PPU dumps, byte-exact and re-encoded round-trips for all
127 rooms, LZSS edge cases (including self-overlapping matches), object-area packing, and an
end-to-end rebuild → write → re-dump. Any change to the five modules above must keep this green.

---

## 6. Where the room lives in ROM

`.github/rom-map.md` §2 lists all 127 blobs with their ROM offsets, byte sizes, compression
flags, elevation planes and cuttable-grass counts — useful when deciding whether an edit fits in
place, or where free space is. It is generated from these tools; §4 of that file shows how to
regenerate it.
