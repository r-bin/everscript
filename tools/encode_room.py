#!/usr/bin/env python3
"""
Secret of Evermore Room Blob Encoder
------------------------------------
The inverse of `tools/dump_room.py`: turns a room model back into the byte
blob the engine loads, so a map editor can write a working map into the ROM.

Two levels of use:

*   `model_from_rom(rom, room_id)` -> `RoomModel` is lossless. Feeding it
    straight back into `build_blob()` reproduces the original bytes exactly
    for all 127 vanilla rooms, which is how the container layout below is
    verified (`--verify`).
*   The `encode_block*` helpers rebuild a block's compressed payload from
    decoded content, for when an editor has actually changed something.
    Those are verified by re-dumping the result and comparing the decoded
    data (`--verify-rebuild`).

Container layout
----------------
Every section carries its own length, so the chain is walkable with no
searching; `dump_room.parse_blob_layout()` is the single source of truth and
this module writes the same layout back.

    +$00            header[13]
    +$0D            step_len:2, step-on records (6 bytes each)
                    b_len:2,    B-trigger records (6 bytes each)
    payload         tile_family_count:1, families (2 bytes each)
    extras          extra_count:1, CHR descriptors (3 bytes each)
    block1          payload_len:2, sub_flag:1, decomp_size:2, data
    section2        count:1, len:2, animated-tile descriptors
    section3        object_count:1, object offsets (2 bytes each)
    block2          payload_len:2, sub_flag:1, decomp_size:2, data
    section4        len:2, $0FC4:1, metatile swap records
    block3          payload_len:2, sub_flag:1, decomp_size:2, data
    object_area     object records and their stamping blocks

`payload_len` counts the sub_flag byte, the decomp_size word and the data,
i.e. `3 + len(data)`.

Compression sub_flags, per the dispatcher at `$8C98A1`:

    0x00  uncompressed copy   ($8C98B1)
    0x03  LZSS sliding window ($8C98C9)
    0x07  2D Markov bitstream ($8C9B65)

Blocks 1 and 3 occur with both `0x00` and `0x03` in vanilla rooms, so an
editor may legally emit either; `0x00` is the safe default when rewriting.
Block 2 is `0x07` in all 127 rooms, so the grid is always Markov-encoded.

Sizing
------
A rebuilt blob is usually larger than the original (uncompressed blocks, and
a greedy Markov encoder). Blobs are reached through the 4-byte map pointer
table at `$9FFDE7`, so a larger blob can simply be relocated to free space and
the pointer repointed -- see `write_room_into_rom()`.
"""

import os
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from tools.dump_room import (  # noqa: E402
    DEFAULT_ROM_PATH,
    MAP_LIST_ADDR,
    MAX_ROOMS,
    LZSSDecompressor,
    decompress_markov_grid,
    parse_blob_layout,
    read16,
    read24,
    snes2rom,
)

SUB_RAW = 0x00
SUB_LZSS = 0x03
SUB_MARKOV = 0x07


# ---------------------------------------------------------------------------
# Bit I/O
# ---------------------------------------------------------------------------

class BitWriter:
    """MSB-first bit stream, matching the decoders' `read_bits`."""

    def __init__(self) -> None:
        self.out = bytearray()
        self._acc = 0
        self._n = 0

    def write(self, value: int, bits: int) -> None:
        for i in range(bits - 1, -1, -1):
            self._acc = (self._acc << 1) | ((value >> i) & 1)
            self._n += 1
            if self._n == 8:
                self.out.append(self._acc & 0xFF)
                self._acc = 0
                self._n = 0

    def flush(self) -> bytes:
        if self._n:
            self.out.append((self._acc << (8 - self._n)) & 0xFF)
            self._acc = 0
            self._n = 0
        return bytes(self.out)


# ---------------------------------------------------------------------------
# LZSS compressor (inverse of dump_room.LZSSDecompressor, $8C98C9)
# ---------------------------------------------------------------------------

MIN_MATCH = 2
MAX_MATCH = 17          # length nibble + 2
WINDOW_SIZE = 0x1000


def lzss_compress(data: bytes, max_candidates: int = 64) -> bytes:
    """
    Produce a stream the engine's LZSS decompressor turns back into `data`.

    Token format, mirroring the decoder:
        bit 1            -> 8-bit literal follows
        bit 0            -> 16-bit token: offset = token >> 4 (0 ends the
                            stream), length = (token & 0x0F) + 2, source read
                            from window index (offset - 1) & 0xFFF

    The 4 KB window starts zeroed and advances one slot per emitted byte, so a
    match source is just a distance back through the output with the leading
    zero fill available at the start.
    """
    bw = BitWriter()
    window = bytearray(WINDOW_SIZE)
    win_ptr = 0
    # 3-byte key -> recent absolute output positions, newest last.
    index: Dict[bytes, List[int]] = {}
    pos = 0
    n = len(data)

    def emit_byte(b: int) -> None:
        nonlocal win_ptr
        window[win_ptr] = b
        win_ptr = (win_ptr + 1) & 0xFFF

    def match_length(src: int, at: int) -> int:
        """
        How many bytes the decoder would copy from window index `src`.

        The decoder writes each copied byte back into the window as it goes, so
        a self-overlapping match reads bytes it has just produced. This mirrors
        that exactly -- getting it wrong silently corrupts long runs.
        """
        probe = src
        wp = win_ptr
        written: Dict[int, int] = {}
        length = 0
        while length < MAX_MATCH and at + length < n:
            b = written.get(probe, window[probe])
            if b != data[at + length]:
                break
            written[wp] = b
            probe = (probe + 1) & 0xFFF
            wp = (wp + 1) & 0xFFF
            length += 1
        return length

    while pos < n:
        best_len = 0
        best_src = 0
        if pos + 3 <= n:
            key = bytes(data[pos:pos + 3])
            for cand in reversed(index.get(key, ())[-max_candidates:]):
                dist = pos - cand
                if dist <= 0 or dist > WINDOW_SIZE:
                    continue
                src = (win_ptr - dist) & 0xFFF
                if src == 0xFFF:
                    continue  # offset would encode as 0, the end-of-stream marker
                length = match_length(src, pos)
                if length > best_len:
                    best_len = length
                    best_src = src
                    if length == MAX_MATCH:
                        break

        if best_len >= 3:
            bw.write(0, 1)
            bw.write((((best_src + 1) & 0xFFF) << 4) | (best_len - 2), 16)
            for k in range(best_len):
                if pos + k + 3 <= n:
                    index.setdefault(bytes(data[pos + k:pos + k + 3]), []).append(pos + k)
                emit_byte(data[pos + k])
            pos += best_len
        else:
            bw.write(1, 1)
            bw.write(data[pos], 8)
            if pos + 3 <= n:
                index.setdefault(bytes(data[pos:pos + 3]), []).append(pos)
            emit_byte(data[pos])
            pos += 1

    # End-of-stream: a reference token with offset 0.
    bw.write(0, 1)
    bw.write(0, 16)
    return bw.flush()


# ---------------------------------------------------------------------------
# Markov grid encoder (inverse of dump_room.decompress_markov_grid, $8C9BD0)
# ---------------------------------------------------------------------------

def encode_markov_grid(grid: Sequence[int], width: int, height: int,
                       base_metatile: int, fc4: int = 0) -> bytes:
    """
    Encode a metatile grid into the 2D context-predictive bitstream.

    The decoder keeps, per metatile id, a 4-slot context `[above0, left1,
    above2, left3]`, and at each cell picks one of six prefix-free tokens:

        1        (1 bit)              -> table[above][0]
        000      (3 bits)             -> table[left][1]
        0011     (4 bits)             -> the next sequential metatile
        00100    (5 bits)             -> table[above][2]
        00101    (5 bits)             -> table[left][3]
        01       (2 bits + tile_bits) -> literal metatile index

    This encoder runs the identical model and picks the cheapest token that
    reproduces the wanted value, with one rule: when the value *is* the next
    sequential metatile it always uses `0011`, because that token is the only
    thing that widens `tile_bits`, and the literal token needs that width.

    The result need not be byte-identical to the original stream -- only to
    decode back to the same grid, which `--verify-rebuild` checks for every
    vanilla room.
    """
    stride = width * 2
    table: Dict[int, List[int]] = {
        tid: [tid, tid, tid, tid]
        for tid in range(base_metatile, base_metatile + 0x0800, 8)
    }

    tile_counter = fc4
    next_seq_tile = base_metatile + fc4 * 8
    tile_mask = 1
    tile_bits = 0
    tmp = fc4
    while tmp > 0:
        tile_mask <<= 1
        tile_bits += 1
        tmp >>= 1

    above_tile = base_metatile
    left_tile = base_metatile
    bw = BitWriter()

    for idx in range(width * height):
        byte_y = idx * 2
        val = grid[idx]

        if val == next_seq_tile:
            bw.write(0b0011, 4)
            next_seq_tile += 8
            if val not in table:
                table[val] = [val, val, val, val]
            tile_counter += 1
            if (tile_counter & tile_mask) != 0:
                tile_mask <<= 1
                tile_bits += 1
        elif table.get(above_tile, [None])[0] == val:
            bw.write(0b1, 1)
        elif table.get(left_tile, [None, None])[1] == val:
            bw.write(0b000, 3)
        elif table.get(above_tile, [None, None, None])[2] == val:
            bw.write(0b00100, 5)
        elif table.get(left_tile, [None, None, None, None])[3] == val:
            bw.write(0b00101, 5)
        else:
            t_idx = (val - base_metatile) // 8
            if t_idx < 0 or t_idx >= (1 << tile_bits):
                raise ValueError(
                    f"metatile {val:#06x} (index {t_idx}) does not fit the "
                    f"{tile_bits}-bit literal field at cell {idx}; the grid "
                    f"must introduce metatiles in ascending order so the "
                    f"sequential token can widen it")
            bw.write(0b01, 2)
            bw.write(t_idx, tile_bits)

        if val not in table:
            table[val] = [val, val, val, val]

        if byte_y >= stride:
            if val != table[above_tile][2]:
                table[above_tile][2] = table[above_tile][0]
            table[above_tile][0] = val

        if val != table[left_tile][3]:
            table[left_tile][3] = table[left_tile][1]
        table[left_tile][1] = val
        left_tile = val

        next_byte_y = byte_y + 2
        if next_byte_y >= stride:
            above_tile = grid[(next_byte_y - stride) // 2]

    return bw.flush()


# ---------------------------------------------------------------------------
# Room model
# ---------------------------------------------------------------------------

@dataclass
class Block:
    """One dispatcher sub-block: `payload_len:2, sub_flag:1, decomp:2, data`."""
    sub: int
    decomp: int
    data: bytes

    def to_bytes(self) -> bytes:
        payload_len = 3 + len(self.data)
        if payload_len > 0xFFFF:
            raise ValueError(f"block payload {payload_len} exceeds the 16-bit length field")
        return (payload_len.to_bytes(2, "little")
                + bytes([self.sub])
                + self.decomp.to_bytes(2, "little")
                + self.data)


@dataclass
class RoomModel:
    """Everything a room blob contains, in writable form."""
    header: bytes                       # 13 bytes
    step_on: List[dict] = field(default_factory=list)
    b_trigger: List[dict] = field(default_factory=list)
    tile_families: List[int] = field(default_factory=list)
    extras: bytes = b""                 # extra_count * 3 CHR descriptors
    block1: Optional[Block] = None
    section2_count: int = 0
    section2_data: bytes = b""
    object_offsets: List[int] = field(default_factory=list)
    block2: Optional[Block] = None
    section4: bytes = b""               # $0FC4 byte + metatile swap records
    block3: Optional[Block] = None
    object_area: bytes = b""

    @property
    def width(self) -> int:
        return self.header[2]

    @property
    def height(self) -> int:
        return self.header[3]

    @property
    def base_metatile(self) -> int:
        return self.width * self.height * 2

    @property
    def fc4(self) -> int:
        return self.section4[0] if self.section4 else 0


def _triggers_to_bytes(records: Sequence[dict]) -> bytes:
    out = bytearray()
    for r in records:
        out += bytes([r["y1"] & 0xFF, r["x1"] & 0xFF, r["y2"] & 0xFF, r["x2"] & 0xFF])
        out += int(r["script_id"]).to_bytes(2, "little")
    return bytes(out)


def build_blob(model: RoomModel) -> bytes:
    """Serialise a RoomModel into the byte blob the engine loads."""
    if len(model.header) != 13:
        raise ValueError(f"header must be 13 bytes, got {len(model.header)}")
    for name in ("block1", "block2", "block3"):
        if getattr(model, name) is None:
            raise ValueError(f"{name} is required")
    if len(model.extras) % 3:
        raise ValueError(f"extras must be a whole number of 3-byte descriptors, got {len(model.extras)}")

    out = bytearray(model.header)

    step = _triggers_to_bytes(model.step_on)
    out += len(step).to_bytes(2, "little") + step

    btrig = _triggers_to_bytes(model.b_trigger)
    out += len(btrig).to_bytes(2, "little") + btrig

    out += bytes([len(model.tile_families)])
    for tid in model.tile_families:
        out += int(tid).to_bytes(2, "little")

    out += bytes([len(model.extras) // 3]) + model.extras
    out += model.block1.to_bytes()

    out += bytes([model.section2_count])
    out += len(model.section2_data).to_bytes(2, "little") + model.section2_data

    out += bytes([len(model.object_offsets)])
    for off in model.object_offsets:
        out += int(off).to_bytes(2, "little")

    out += model.block2.to_bytes()
    out += len(model.section4).to_bytes(2, "little") + model.section4
    out += model.block3.to_bytes()
    out += model.object_area
    return bytes(out)


def model_from_rom(rom: bytes, room_id: int) -> RoomModel:
    """
    Lossless extraction: `build_blob(model_from_rom(rom, rid))` reproduces the
    original bytes exactly. Compressed payloads are kept verbatim; use the
    `encode_block*` helpers to replace one after editing its content.
    """
    blob = snes2rom(read24(rom, MAP_LIST_ADDR + room_id * 4))
    L = parse_blob_layout(rom, blob)

    def records(start: int, length: int) -> List[dict]:
        out = []
        for i in range(length // 6):
            r = rom[start + i * 6: start + (i + 1) * 6]
            out.append({"y1": r[0], "x1": r[1], "y2": r[2], "x2": r[3],
                        "script_id": r[4] | (r[5] << 8)})
        return out

    def block(off: int) -> Block:
        payload_len = read16(rom, off)
        return Block(sub=rom[off + 2], decomp=read16(rom, off + 3),
                     data=bytes(rom[off + 5: off + 2 + payload_len]))

    n_obj = L["object_count"]
    return RoomModel(
        header=bytes(rom[blob:blob + 13]),
        step_on=records(blob + 0x0F, L["step_len"]),
        b_trigger=records(L["b_len_offset"] + 2, L["b_len"]),
        tile_families=[read16(rom, L["payload_offset"] + 1 + i * 2)
                       for i in range(L["tile_count"])],
        extras=bytes(rom[L["extras_offset"] + 1: L["block1"]]),
        block1=block(L["block1"]),
        section2_count=L["section2_count"],
        section2_data=bytes(rom[L["section2"] + 3: L["section3"]]),
        object_offsets=[read16(rom, L["section3"] + 1 + i * 2) for i in range(n_obj)],
        block2=block(L["block2"]),
        section4=bytes(rom[L["section4"] + 2: L["block3"]]),
        block3=block(L["block3"]),
        object_area=bytes(rom[L["object_area"]: _object_area_end(rom, L)]),
    )


def _object_area_end(rom: bytes, L: dict) -> int:
    """
    Extent of the object area: the furthest byte any object record or stamping
    block reaches. Objects and their stamping blocks are both addressed as
    offsets from the area start, and vanilla rooms share stamping blocks
    between states, so the end has to be measured rather than summed.
    """
    aa = L["object_area"]
    end = aa
    for i in range(L["object_count"]):
        rec = aa + read16(rom, L["section3"] + 1 + i * 2)
        max_state = rom[rec]
        end = max(end, rec + 1 + max_state * 5)
        for s in range(max_state):
            sp = rec + 1 + s * 5
            tp = aa + read16(rom, sp + 3)
            end = max(end, tp + 2 + rom[tp] * rom[tp + 1] * 2)
    return end


# ---------------------------------------------------------------------------
# Block re-encoders, for content an editor has actually changed
# ---------------------------------------------------------------------------

def encode_block1(accum_words: Sequence[int], compress: bool = False,
                  original: Optional[Block] = None) -> Block:
    """
    Block 1 is a CHR tile palette stored as 16-bit deltas which the engine
    accumulates at `$908E85`; `dump_room` reports the accumulated values, so
    this differentiates them back.
    """
    raw = bytearray()
    prev = 0
    for w in accum_words:
        raw += ((w - prev) & 0xFFFF).to_bytes(2, "little")
        prev = w & 0xFFFF
    return _wrap(bytes(raw), compress, original)


def encode_block2(grid: Sequence[int], width: int, height: int,
                  base_metatile: int, fc4: int = 0) -> Block:
    """Block 2 is always Markov-encoded (sub_flag 0x07) in vanilla rooms."""
    data = encode_markov_grid(grid, width, height, base_metatile, fc4)
    return Block(sub=SUB_MARKOV, decomp=width * height * 2, data=data)


def encode_block3(slice0: Sequence[int], slice1: Sequence[int],
                  slice2: Sequence[int], compress: bool = False,
                  original: Optional[Block] = None) -> Block:
    """
    Block 3 is the three planar slices -- Layer 1 words, Layer 2 words and
    collision words -- concatenated, one after the other.
    """
    if not (len(slice0) == len(slice1) == len(slice2)):
        raise ValueError("the three metatile slices must be the same length")
    raw = bytearray()
    for sl in (slice0, slice1, slice2):
        for w in sl:
            raw += int(w).to_bytes(2, "little")
    return _wrap(bytes(raw), compress, original)


def _wrap(raw: bytes, compress: bool, original: Optional[Block] = None) -> Block:
    """
    Pick the smallest legal encoding of `raw`.

    Passing the block this content came from lets an editor keep a payload it
    has not actually changed, so re-encoding an untouched room never costs
    bytes just because this LZSS packer made a different choice than whatever
    produced the original data.
    """
    best = Block(sub=SUB_RAW, decomp=len(raw), data=raw)
    if compress:
        packed = lzss_compress(raw)
        if len(packed) < len(best.data):
            best = Block(sub=SUB_LZSS, decomp=len(raw), data=packed)
    if original is not None and len(original.data) < len(best.data):
        try:
            unchanged = bytes(_unpack(original)) == raw
        except ValueError:
            unchanged = False
        if unchanged:
            best = original
    return best


def _overlap(a: bytes, b: bytes) -> int:
    """Length of the longest suffix of `a` that is also a prefix of `b`."""
    limit = min(len(a), len(b)) - 1
    while limit > 0 and a[-limit:] != b[:limit]:
        limit -= 1
    return max(limit, 0)


def _pack_overlapping(blocks: "set[bytes]") -> Tuple[bytearray, Dict[bytes, int]]:
    """
    Lay stamping blocks out so they share bytes, the way the vanilla object
    area does -- room 0x09 has 15 of its 24 blocks overlapping their
    neighbour, and room 0x06 has 434- and 1298-byte blocks overlapping by
    dozens of bytes each.

    Blocks fully contained in another are dropped first, then the rest are
    merged greedily by largest pairwise overlap (the standard shortest common
    superstring heuristic). Every input block is then located in the result.
    """
    items = sorted(blocks, key=lambda b: (-len(b), b))
    # Drop anything already contained in a longer block.
    kept: List[bytes] = []
    for blk in items:
        if not any(blk in bigger for bigger in kept):
            kept.append(blk)

    while len(kept) > 1:
        best = (0, -1, -1)
        for i, a in enumerate(kept):
            for j, b in enumerate(kept):
                if i == j:
                    continue
                ov = _overlap(a, b)
                if ov > best[0]:
                    best = (ov, i, j)
        if best[0] == 0:
            break
        ov, i, j = best
        merged = kept[i] + kept[j][ov:]
        for k in sorted((i, j), reverse=True):
            kept.pop(k)
        kept.append(merged)

    buf = bytearray()
    for chunk in kept:
        buf.extend(chunk)

    placed: Dict[bytes, int] = {}
    for blk in blocks:
        at = buf.find(blk)
        if at < 0:  # pragma: no cover - the merge always keeps every block
            at = len(buf)
            buf.extend(blk)
        placed[blk] = at
    return buf, placed


def build_object_area(objects: Sequence[dict]) -> Tuple[List[int], bytes]:
    """
    Rebuild the object records and stamping blocks from decoded objects, as
    `dump_room` reports them.

    Returns `(object_offsets, object_area)` for `RoomModel`.

    Each object is `max_state:1` followed by 5-byte states
    `[width, tile_x, tile_y, target_off:2]`; each stamping block is
    `[target_width, target_height, metatiles...]`. Both are addressed as
    offsets from the start of the area.

    Stamping blocks are packed the way the vanilla data is: a block that
    already appears anywhere in the buffer reuses that offset, and otherwise
    only the part that does not overlap the buffer's tail is appended. Room
    0x09, for instance, has 15 of its 24 blocks overlapping their neighbour.
    Blocks are placed longest-first, the usual greedy heuristic for this kind
    of packing.
    """
    records: List[bytearray] = []
    targets_per_object: List[List[Tuple[int, int, Sequence[int]]]] = []

    for obj in objects:
        states = obj.get("states", [])
        rec = bytearray([len(states)])
        targets: List[Tuple[int, int, Sequence[int]]] = []
        for st in states:
            rec += bytes([st.get("width", 0) & 0xFF,
                          st["tile_x"] & 0xFF,
                          st["tile_y"] & 0xFF])
            rec += b"\x00\x00"  # target offset, patched once blocks are placed
            targets.append((st.get("target_width", 1),
                            st.get("target_height", 1),
                            st.get("metatiles", [])))
        records.append(rec)
        targets_per_object.append(targets)

    def payload(tw: int, th: int, metatiles: Sequence[int]) -> bytes:
        out = bytearray([tw & 0xFF, th & 0xFF])
        for m in metatiles:
            out += int(m).to_bytes(2, "little")
        return bytes(out)

    wanted = {payload(*t) for targets in targets_per_object for t in targets}
    block_bytes, placed = _pack_overlapping(wanted)

    rec_size = sum(len(r) for r in records)
    for rec, targets in zip(records, targets_per_object):
        for s, t in enumerate(targets):
            off = rec_size + placed[payload(*t)]
            rec[1 + s * 5 + 3: 1 + s * 5 + 5] = off.to_bytes(2, "little")

    offsets: List[int] = []
    cursor = 0
    for rec in records:
        offsets.append(cursor)
        cursor += len(rec)
    return offsets, bytes(b"".join(records) + block_bytes)


def rebuild_model(rom: bytes, room_id: int, room_data: Optional[dict] = None,
                  compress: bool = True) -> RoomModel:
    """
    Re-encode a room entirely from decoded data -- the path a map editor takes
    after changing something.

    Blocks 1 and 3 are re-encoded from their decoded content, Block 2 from the
    metatile grid, and the object area is rebuilt from the object list.
    `room_data` defaults to `dump_room(room_id)`; pass an edited copy to write
    changes. Each block keeps whichever encoding is smallest, including the
    original payload when its content is unchanged, so a rebuilt blob is never
    larger than the one it came from.
    """
    from tools.dump_room import dump_room

    src = room_data if room_data is not None else dump_room(room_id)
    model = model_from_rom(rom, room_id)

    model.header = bytes.fromhex(src["header"]["raw_hex"])
    model.step_on = list(src["triggers"]["step_on"])
    model.b_trigger = list(src["triggers"]["b_trigger"])
    model.tile_families = [int(t, 16) for t in src["tile_families"]]

    model.block1 = encode_block1([int(w, 16) for w in src["tile_palette"]],
                                 compress=compress, original=model.block1)

    grid = [int(v, 16) for row in src["layer1_metatile_ids"] for v in row]
    model.block2 = encode_block2(grid, model.width, model.height,
                                 model.base_metatile, model.fc4)

    n = src["metatile_count"]
    slices = _slices_of(model.block3)
    model.block3 = encode_block3(slices[:n], slices[n:2 * n], slices[2 * n:3 * n],
                                 compress=compress, original=model.block3)

    model.object_offsets, model.object_area = build_object_area(src["objects"])
    return model


# ---------------------------------------------------------------------------
# Writing a blob back into a ROM image
# ---------------------------------------------------------------------------

def write_room_into_rom(rom: bytes, room_id: int, blob: bytes,
                        at_offset: Optional[int] = None) -> Tuple[bytearray, int]:
    """
    Place `blob` in a ROM image and repoint room `room_id` at it.

    With `at_offset` omitted the blob is written over the room's current
    location, which is only safe when it is no larger than the original --
    this raises otherwise rather than clobbering the neighbouring room.
    Otherwise the blob goes at `at_offset` (a ROM file offset) and the 4-byte
    map pointer table entry at `$9FFDE7 + room_id * 4` is updated.

    Returns `(new_rom, blob_offset)`.
    """
    if not (0 <= room_id < MAX_ROOMS):
        raise ValueError(f"room id {room_id:#04x} out of range")
    out = bytearray(rom)
    original = snes2rom(read24(rom, MAP_LIST_ADDR + room_id * 4))

    if at_offset is None:
        L = parse_blob_layout(rom, original)
        available = _object_area_end(rom, L) - original
        if len(blob) > available:
            raise ValueError(
                f"rebuilt blob is {len(blob)} bytes but room 0x{room_id:02X} "
                f"only occupies {available}; pass at_offset to relocate it")
        at_offset = original
    else:
        if at_offset + len(blob) > len(out):
            raise ValueError("blob does not fit in the ROM image at that offset")
        # HiROM: a blob must not straddle a bank boundary, since the loader
        # walks it with 16-bit offsets from the blob's own bank base.
        if (at_offset >> 16) != ((at_offset + len(blob) - 1) >> 16):
            raise ValueError(
                f"blob at 0x{at_offset:06X} would cross a bank boundary")

    out[at_offset:at_offset + len(blob)] = blob

    snes = 0x800000 | at_offset
    entry = MAP_LIST_ADDR + room_id * 4
    out[entry] = snes & 0xFF
    out[entry + 1] = (snes >> 8) & 0xFF
    out[entry + 2] = (snes >> 16) & 0xFF
    return out, at_offset


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------

def verify_lossless(rom: bytes, room_ids: Sequence[int]) -> List[str]:
    """`build_blob(model_from_rom(...))` must equal the original bytes."""
    problems = []
    for rid in room_ids:
        blob_off = snes2rom(read24(rom, MAP_LIST_ADDR + rid * 4))
        model = model_from_rom(rom, rid)
        built = build_blob(model)
        original = rom[blob_off:blob_off + len(built)]
        if built != original:
            first = next((i for i in range(len(built)) if built[i] != original[i]), len(built))
            problems.append(
                f"room 0x{rid:02X}: {len(built)} bytes, first difference at +0x{first:04X}")
    return problems


def verify_rebuild(rom: bytes, room_ids: Sequence[int]) -> List[str]:
    """
    Re-encode blocks 1, 2 and 3 from decoded content and the object area from
    the decoded objects, then decode the result and compare.
    """
    from tools.dump_room import dump_room

    problems = []
    for rid in room_ids:
        src = dump_room(rid)
        original = build_blob(model_from_rom(rom, rid))
        model = rebuild_model(rom, rid, src)
        blob = build_blob(model)

        if len(blob) > len(original):
            problems.append(
                f"room 0x{rid:02X}: rebuilt blob is {len(blob)} bytes, "
                f"{len(blob) - len(original)} larger than the original")

        try:
            check = _decode_blob(blob)
        except Exception as exc:                       # noqa: BLE001
            problems.append(f"room 0x{rid:02X}: rebuilt blob failed to parse: {exc}")
            continue

        grid = [int(v, 16) for row in src["layer1_metatile_ids"] for v in row]
        want_slices = _slices_of(model_from_rom(rom, rid).block3)
        if check["grid"] != grid:
            bad = next(i for i in range(len(grid)) if check["grid"][i] != grid[i])
            problems.append(f"room 0x{rid:02X}: grid differs at cell {bad}")
        if check["slices"] != want_slices:
            problems.append(f"room 0x{rid:02X}: metatile table differs")
        if check["objects"] != _objects_key(src["objects"]):
            problems.append(f"room 0x{rid:02X}: objects differ")
    return problems


def _unpack(b: Block) -> bytearray:
    """A block's decompressed payload, whichever sub_flag it uses."""
    if b.sub == SUB_LZSS:
        return LZSSDecompressor(b.data, 0).decompress(b.decomp)[:b.decomp]
    if b.sub == SUB_RAW:
        return bytearray(b.data[:b.decomp])
    raise ValueError(f"cannot unpack sub_flag 0x{b.sub:02X}")


def _slices_of(block3: Block) -> List[int]:
    raw = _unpack(block3)
    return [raw[i] | (raw[i + 1] << 8) for i in range(0, len(raw) & ~1, 2)]


def _recompress(b: Block, compress: bool) -> Block:
    """Re-encode a block from its own decoded content."""
    return _wrap(bytes(_unpack(b)), compress, original=b)


def _objects_key(objects: Sequence[dict]) -> list:
    return [[(st.get("width"), st["tile_x"], st["tile_y"],
              st.get("target_width"), st.get("target_height"),
              list(st.get("metatiles", [])))
             for st in o.get("states", [])] for o in objects]


def _decode_blob(blob: bytes) -> dict:
    """Parse a standalone blob the way the engine would, for verification."""
    L = parse_blob_layout(blob, 0)
    w, h = blob[2], blob[3]
    base = w * h * 2

    b2 = L["block2"]
    grid = decompress_markov_grid(blob, b2 + 5, w, h, base, fc4=L["fc4"])

    b3 = L["block3"]
    raw = (LZSSDecompressor(blob, b3 + 5).decompress(L["block3_decomp"])[:L["block3_decomp"]]
           if L["block3_sub"] == SUB_LZSS
           else bytearray(blob[b3 + 5: b3 + 5 + L["block3_decomp"]]))
    slices = [raw[i] | (raw[i + 1] << 8) for i in range(0, len(raw) & ~1, 2)]

    aa = L["object_area"]
    objects = []
    for i in range(L["object_count"]):
        rec = aa + read16(blob, L["section3"] + 1 + i * 2)
        states = []
        for s in range(blob[rec]):
            sp = rec + 1 + s * 5
            tp = aa + read16(blob, sp + 3)
            tw, th = blob[tp], blob[tp + 1]
            states.append((blob[sp], blob[sp + 1], blob[sp + 2], tw, th,
                           [read16(blob, tp + 2 + k * 2) for k in range(tw * th)]))
        objects.append(states)
    return {"grid": grid, "slices": slices, "objects": objects}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    ap = argparse.ArgumentParser(description="Encode a room model back into a ROM blob")
    ap.add_argument("room", nargs="?", help="Room id (hex e.g. 0x38, or decimal)")
    ap.add_argument("--rom", default=DEFAULT_ROM_PATH)
    ap.add_argument("--out", help="Write the blob to this file")
    ap.add_argument("--rebuild", action="store_true",
                    help="Re-encode blocks 1-3 and the object area instead of "
                         "keeping the original payloads")
    ap.add_argument("--compress", action="store_true",
                    help="With --rebuild, LZSS-compress blocks 1 and 3")
    ap.add_argument("--verify", action="store_true",
                    help="Check byte-exact round-trip for every room")
    ap.add_argument("--verify-rebuild", action="store_true",
                    help="Check that re-encoded blocks decode back identically")
    args = ap.parse_args()

    with open(args.rom, "rb") as f:
        rom = f.read()

    if args.verify or args.verify_rebuild:
        ids = list(range(MAX_ROOMS))
        failed = False
        if args.verify:
            problems = verify_lossless(rom, ids)
            print(f"byte-exact round-trip: {len(ids) - len(problems)}/{len(ids)} rooms")
            for p in problems:
                print("  " + p)
            failed |= bool(problems)
        if args.verify_rebuild:
            problems = verify_rebuild(rom, ids)
            print(f"re-encoded round-trip:  {len(ids) - len(problems)}/{len(ids)} rooms")
            for p in problems:
                print("  " + p)
            failed |= bool(problems)
        sys.exit(1 if failed else 0)

    if not args.room:
        ap.error("a room id is required unless --verify / --verify-rebuild is given")
    rid = int(args.room, 16) if args.room.lower().startswith("0x") else int(args.room, 0)

    model = (rebuild_model(rom, rid, compress=args.compress)
             if args.rebuild else model_from_rom(rom, rid))

    blob = build_blob(model)
    original_len = len(build_blob(model_from_rom(rom, rid)))
    print(f"Room 0x{rid:02X}: {len(blob)} bytes "
          f"({len(blob) - original_len:+d} vs original {original_len})")
    print(f"  block1 sub=0x{model.block1.sub:02X} decomp={model.block1.decomp:6d} data={len(model.block1.data):6d}")
    print(f"  block2 sub=0x{model.block2.sub:02X} decomp={model.block2.decomp:6d} data={len(model.block2.data):6d}")
    print(f"  block3 sub=0x{model.block3.sub:02X} decomp={model.block3.decomp:6d} data={len(model.block3.data):6d}")
    if args.out:
        with open(args.out, "wb") as f:
            f.write(blob)
        print(f"  wrote {args.out}")


if __name__ == "__main__":
    main()
