"""
Integration tests for tools/encode_room.py -- the inverse of dump_room.

The decisive test is the byte-exact round-trip: extracting a lossless model
from the ROM and serialising it again must reproduce the original blob for
every vanilla room. That proves the container layout is understood rather than
merely parsed, which is what a map editor depends on.
"""

import os
import sys

import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.dump_room import (  # noqa: E402
    DEFAULT_ROM_PATH,
    LZSSDecompressor,
    MAP_LIST_ADDR,
    MAX_ROOMS,
    dump_room,
    parse_blob_layout,
    read24,
    snes2rom,
)
from tools.encode_room import (  # noqa: E402
    Block,
    SUB_MARKOV,
    rebuild_model,
    SUB_RAW,
    build_blob,
    build_object_area,
    encode_block1,
    encode_block2,
    encode_block3,
    lzss_compress,
    model_from_rom,
    verify_lossless,
    verify_rebuild,
    write_room_into_rom,
)
from tools.encode_room import _slices_of, _unpack  # noqa: E402

pytestmark = pytest.mark.skipif(
    not os.path.exists(DEFAULT_ROM_PATH), reason="ROM not available"
)

SAMPLE_ROOMS = [0x00, 0x05, 0x15, 0x1B, 0x33, 0x34, 0x38, 0x3B, 0x3D, 0x48, 0x69, 0x7E]


@pytest.fixture(scope="module")
def rom() -> bytes:
    with open(DEFAULT_ROM_PATH, "rb") as f:
        return f.read()


# --- Read -> decode -> encode -------------------------------------------

def test_decode_encode_is_byte_identical_for_every_room(rom):
    """
    Reading a room and writing it straight back must reproduce the original
    blob exactly, for all 127 rooms. This is the proof that the container
    layout is understood rather than merely parsed.
    """
    assert verify_lossless(rom, range(MAX_ROOMS)) == []


@pytest.mark.parametrize("room_id", SAMPLE_ROOMS)
def test_decode_encode_byte_identical_per_room(rom, room_id):
    """Same property per room, so a failure names the room."""
    blob_offset = snes2rom(read24(rom, MAP_LIST_ADDR + room_id * 4))
    built = build_blob(model_from_rom(rom, room_id))
    assert built == rom[blob_offset:blob_offset + len(built)]


def test_full_rebuild_is_never_larger_than_the_original(rom):
    """
    Re-encoding every block from decoded data must not cost bytes, for any
    room. The encoders keep whichever encoding is smallest -- raw, LZSS, or
    the original payload when its content is unchanged -- so an edit that
    grows a blob can only be an edit that added content.
    """
    grew = []
    total = 0
    for room_id in range(MAX_ROOMS):
        original = len(build_blob(model_from_rom(rom, room_id)))
        rebuilt = len(build_blob(rebuild_model(rom, room_id)))
        total += rebuilt - original
        if rebuilt > original:
            grew.append((f"0x{room_id:02X}", original, rebuilt))
    assert grew == [], f"rebuilt blobs grew: {grew}"
    assert total < 0, "the rebuild should be smaller overall, got {total:+d}"


def test_full_rebuild_decodes_to_the_same_room(rom):
    """Re-encoded blocks and object area decode back to identical content."""
    assert verify_rebuild(rom, range(MAX_ROOMS)) == []


@pytest.mark.parametrize("room_id", SAMPLE_ROOMS)
def test_rebuilt_room_matches_when_dumped_again(rom, room_id, tmp_path):
    """
    The end-to-end property a map editor needs: decode a room, re-encode every
    block, write the blob into a ROM, and dump it again -- the decoded data
    must be unchanged.
    """
    src = dump_room(room_id)
    blob = build_blob(rebuild_model(rom, room_id, src))
    new_rom, _ = write_room_into_rom(rom, room_id, blob)

    path = str(tmp_path / f"room_{room_id:02x}.smc")
    with open(path, "wb") as f:
        f.write(new_rom)

    after = dump_room(room_id, path)
    for key in ("header", "size", "triggers", "object_count", "tile_families",
                "tile_palette", "metatile_count", "base_metatile",
                "layer1_metatile_ids", "layer1_vram_words", "layer2_vram_words",
                "collision_words", "cuttable_grass_tiles", "animated_tiles"):
        assert after[key] == src[key], key
    for before, now in zip(src["objects"], after["objects"]):
        for a, b in zip(before["states"], now["states"]):
            assert (a["width"], a["tile_x"], a["tile_y"], a["target_width"],
                    a["target_height"], a["metatiles"]) == \
                   (b["width"], b["tile_x"], b["tile_y"], b["target_width"],
                    b["target_height"], b["metatiles"])


@pytest.mark.parametrize("room_id", SAMPLE_ROOMS)
def test_blob_layout_is_self_consistent(rom, room_id):
    """Every section of a rebuilt blob lands at the same relative offset."""
    original = snes2rom(read24(rom, MAP_LIST_ADDR + room_id * 4))
    source = parse_blob_layout(rom, original)
    rebuilt = parse_blob_layout(build_blob(model_from_rom(rom, room_id)), 0)

    offset_keys = ("b_len_offset", "payload_offset", "extras_offset", "block1",
                   "section2", "section3", "block2", "section4", "block3",
                   "object_area")
    for key in offset_keys:
        assert rebuilt[key] == source[key] - original, key
    for key in ("step_len", "b_len", "tile_count", "extra_count", "object_count",
                "fc4", "section2_count", "section2_len", "section4_len",
                "block1_sub", "block1_decomp", "block2_sub", "block2_decomp",
                "block3_sub", "block3_decomp"):
        assert rebuilt[key] == source[key], key


def test_room_0x15_block3_is_uncompressed(rom):
    """
    Room 0x15's Block 3 uses sub_flag 0x00. It is the one room where the old
    signature scan (which only accepted 0x03) latched onto the wrong block, so
    it is worth pinning down.
    """
    layout = parse_blob_layout(rom, snes2rom(read24(rom, MAP_LIST_ADDR + 0x15 * 4)))
    assert layout["block3_sub"] == SUB_RAW
    assert layout["block3_decomp"] == 12
    assert dump_room(0x15)["metatile_count"] == 2


# --- Compression ----------------------------------------------------------

@pytest.mark.parametrize("payload", [
    bytes(5000),                       # long zero run
    b"\x41" * 100 + bytes(4000),       # run then zero fill
    b"\x01\x02\x03\x04" * 3000,        # periodic, needs overlapping matches
    bytes(range(256)) * 16,            # no repeats within the match window
])
def test_lzss_round_trip(payload):
    packed = lzss_compress(payload)
    back = bytes(LZSSDecompressor(packed, 0).decompress(len(payload)))[:len(payload)]
    assert back == payload


def test_lzss_compresses_real_block3(rom):
    raw = bytes(_unpack(model_from_rom(rom, 0x38).block3))
    packed = lzss_compress(raw)
    assert len(packed) < len(raw)
    assert bytes(LZSSDecompressor(packed, 0).decompress(len(raw)))[:len(raw)] == raw


def test_markov_encoder_is_byte_identical_to_vanilla(rom):
    """
    The greedy token choice reproduces the original bitstream exactly for every
    room, so an edited grid is encoded the same way the game's own data was.
    """
    for room_id in range(MAX_ROOMS):
        src = dump_room(room_id)
        model = model_from_rom(rom, room_id)
        grid = [int(v, 16) for row in src["layer1_metatile_ids"] for v in row]
        encoded = encode_block2(grid, model.width, model.height,
                                model.base_metatile, model.fc4)
        assert encoded.sub == SUB_MARKOV
        assert encoded.decomp == model.block2.decomp
        assert encoded.data == model.block2.data, f"room 0x{room_id:02X}"


def test_encode_block1_inverts_the_delta_accumulator(rom):
    src = dump_room(0x33)
    block = encode_block1([int(w, 16) for w in src["tile_palette"]])
    raw = _unpack(block)
    acc, running = [], 0
    for i in range(0, len(raw) & ~1, 2):
        running = (running + (raw[i] | (raw[i + 1] << 8))) & 0xFFFF
        acc.append(running)
    assert acc == [int(w, 16) for w in src["tile_palette"]]


def test_encode_block3_lays_the_slices_out_planar():
    block = encode_block3([1, 2], [3, 4], [5, 6], compress=False)
    assert block.sub == SUB_RAW
    assert block.decomp == 12
    assert bytes(_unpack(block)) == bytes([1, 0, 2, 0, 3, 0, 4, 0, 5, 0, 6, 0])
    assert _slices_of(block) == [1, 2, 3, 4, 5, 6]


def test_encode_block3_rejects_ragged_slices():
    with pytest.raises(ValueError, match="same length"):
        encode_block3([1, 2], [3], [5, 6])


# --- Objects --------------------------------------------------------------

def test_object_area_packing_is_never_larger_than_vanilla(rom):
    """
    Vanilla overlaps stamping blocks -- room 0x09 has 15 of its 24 blocks
    overlapping their neighbour. The greedy superstring packing has to match
    that or rebuilt rooms bloat.
    """
    grew = []
    for room_id in range(MAX_ROOMS):
        model = model_from_rom(rom, room_id)
        original = len(model.object_area) + 2 * len(model.object_offsets)
        offsets, area = build_object_area(dump_room(room_id)["objects"])
        if len(area) + 2 * len(offsets) > original:
            grew.append(f"0x{room_id:02X}")
    assert grew == []


def test_pack_overlapping_shares_a_common_suffix_prefix():
    """A block whose prefix is another block's suffix must share those bytes."""
    from tools.encode_room import _pack_overlapping

    a = bytes([0x01, 0x02, 0x11, 0x11, 0x22, 0x22])
    b = bytes([0x22, 0x22, 0x33, 0x33])            # a's last 2 bytes == b's first 2
    buf, placed = _pack_overlapping({a, b})
    assert len(buf) < len(a) + len(b), "the shared bytes should not be duplicated"
    assert bytes(buf[placed[a]: placed[a] + len(a)]) == a
    assert bytes(buf[placed[b]: placed[b] + len(b)]) == b


def test_pack_overlapping_drops_fully_contained_blocks():
    from tools.encode_room import _pack_overlapping

    big = bytes(range(10))
    small = bytes(range(3, 7))              # entirely inside `big`
    buf, placed = _pack_overlapping({big, small})
    assert len(buf) == len(big)
    assert bytes(buf[placed[big]: placed[big] + len(big)]) == big
    assert bytes(buf[placed[small]: placed[small] + len(small)]) == small


def test_build_object_area_shares_identical_stamping_blocks():
    obj = {"states": [{"width": 5, "tile_x": 1, "tile_y": 2,
                       "target_width": 1, "target_height": 1, "metatiles": [0x1234]}]}
    twin = {"states": [{"width": 5, "tile_x": 9, "tile_y": 9,
                        "target_width": 1, "target_height": 1, "metatiles": [0x1234]}]}
    offsets, area = build_object_area([obj, twin])
    assert len(offsets) == 2
    a = area[offsets[0] + 1 + 3] | (area[offsets[0] + 1 + 4] << 8)
    b = area[offsets[1] + 1 + 3] | (area[offsets[1] + 1 + 4] << 8)
    assert a == b, "identical stamping blocks should be emitted once"


@pytest.mark.parametrize("room_id", SAMPLE_ROOMS)
def test_rebuilt_objects_preserve_content(rom, room_id):
    """Rebuilding the object area keeps every field except the internal offset."""
    src = dump_room(room_id)
    model = model_from_rom(rom, room_id)
    model.object_offsets, model.object_area = build_object_area(src["objects"])
    blob = build_blob(model)
    layout = parse_blob_layout(blob, 0)
    assert layout["object_count"] == len(src["objects"])

    area = layout["object_area"]
    for i, obj in enumerate(src["objects"]):
        rec = area + (blob[layout["section3"] + 1 + i * 2]
                      | blob[layout["section3"] + 2 + i * 2] << 8)
        assert blob[rec] == len(obj["states"])
        for s, state in enumerate(obj["states"]):
            sp = rec + 1 + s * 5
            assert blob[sp] == state["width"]
            assert blob[sp + 1] == state["tile_x"]
            assert blob[sp + 2] == state["tile_y"]
            tp = area + (blob[sp + 3] | blob[sp + 4] << 8)
            assert blob[tp] == state["target_width"]
            assert blob[tp + 1] == state["target_height"]
            tiles = [blob[tp + 2 + k * 2] | blob[tp + 3 + k * 2] << 8
                     for k in range(blob[tp] * blob[tp + 1])]
            assert tiles == state["metatiles"]


# --- Writing back into a ROM ---------------------------------------------

def test_write_room_in_place_leaves_neighbours_untouched(rom, tmp_path):
    """
    A rebuilt blob is never larger than the original (see
    test_full_rebuild_is_never_larger_than_the_original), so it always fits
    written in place -- and doing so must not disturb any other room's data.
    """
    room_id = 0x48
    blob = build_blob(rebuild_model(rom, room_id))
    new_rom, offset = write_room_into_rom(rom, room_id, blob)
    assert offset == snes2rom(read24(rom, MAP_LIST_ADDR + room_id * 4))

    path = str(tmp_path / "rebuilt.smc")
    with open(path, "wb") as f:
        f.write(new_rom)

    for other in (0x47, 0x49, 0x38):
        assert dump_room(other, path)["layer1_metatile_ids"] == \
               dump_room(other)["layer1_metatile_ids"]


def test_write_room_refuses_to_overflow_in_place(rom):
    room_id = 0x34
    model = model_from_rom(rom, room_id)
    model.block3 = Block(sub=SUB_RAW, decomp=0x4000, data=bytes(0x4000))
    with pytest.raises(ValueError, match="only occupies"):
        write_room_into_rom(rom, room_id, build_blob(model))


def test_write_room_refuses_to_cross_a_bank_boundary(rom):
    blob = build_blob(model_from_rom(rom, 0x34))
    with pytest.raises(ValueError, match="bank boundary"):
        write_room_into_rom(rom, 0x34, blob, at_offset=0x0FFFF0)


def test_write_room_repoints_the_map_table(rom):
    blob = build_blob(model_from_rom(rom, 0x34))
    target = 0x0F0000
    new_rom, offset = write_room_into_rom(rom, 0x34, blob, at_offset=target)
    assert offset == target
    assert snes2rom(read24(new_rom, MAP_LIST_ADDR + 0x34 * 4)) == target
    assert bytes(new_rom[target:target + len(blob)]) == blob
