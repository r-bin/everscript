# ROM Map Overview

A quick-reference map of what lives where in the vanilla Secret of Evermore ROM, in the spirit of
[Data Crystal's SoE ROM map](https://datacrystal.tcrf.net/wiki/Secret_of_Evermore/ROM_map) —
lighter on detail than that wiki page, and lighter than this repo's own deep-dive docs. Ordered by
**ROM file offset, `0x000000` → `0x3FFFFF`**, with every region marked as one of:

| Marker | Meaning |
|---|---|
| ✅ **KNOWN / USED** | Verified content, cited to a specific doc or first-party source |
| 🟡 **NON-ZERO, UNUSED** | Bytes exist and are non-zero, but verified not read as valid data by the engine — reclaimable, but not blank |
| ⬜ **VERIFIED EMPTY** | Actually checked, and it's a real run of padding bytes |
| ❓ **UNKNOWN** | Not characterized this session — could be data, could be free space, nobody's looked |
| 🚫 **DOESN'T PHYSICALLY EXIST** | Beyond the end of the actual ROM file |

Deep-dive sources this page summarizes: [`.github/rom-map.md`](../.github/rom-map.md),
[`architecture.md`](../architecture.md) §3.1, [`docs/rom-extension-wishlist.md`](rom-extension-wishlist.md),
`compiler/linker.py`'s own `#memory()` docstring. **This page is an index — read those for
citations and disassembly-level evidence.**

---

## Answering the question that prompted this page

**"Are there 0s after the map table, so it can just be used?" — No.** This was re-checked directly
against the ROM for this revision, not assumed. Entries `0x7F..0x85` (the 7 "free" map-table slots
[`rom-extension-wishlist.md` §1](rom-extension-wishlist.md) already identified by arithmetic) were
read byte-for-byte and run through this repo's own room-validity check
(`tools/dump_room.py`'s rule: `block2_sub == 0x07 AND decomp_size == width*height*2`):

| Slot | Raw bytes | Room-valid? |
|---|---|---|
| `0x7F` | `89 CF C9 CC` | ❌ fails (already known) |
| `0x80` | `4E 90 98 E8` | ❌ fails |
| `0x81` | `EA F6 01 02` | ❌ fails |
| `0x82` | `01 07 0E 02` | ❌ fails |
| `0x83` | `1F 0A 03 0F` | ❌ fails |
| `0x84` | `02 0A 07 01` | ❌ fails |
| `0x85` | `03 03 C0 06` | ❌ fails |

So the good news survives: **none of the 7 slots are read as valid rooms today**, confirmed the
same rigorous way the existing `0x7F` finding was, not just assumed by extension. But **the bytes
are not zero** — they're non-zero, varied, garbage-looking values (leftover data, not padding).
"Can just be used" is right in the sense that nothing currently depends on them; it's wrong in the
sense that a patch would be *overwriting real bytes*, not filling in blank space. Practically this
changes nothing about feasibility — it's still the easiest item on the wishlist — but "already
empty" was never actually true, and now that's checked rather than assumed.

---

## Ordered ROM walk

Only regions with a **directly cited, verified file offset** get their own row — see the
"Coarse subsystem labels" section below for everything only described at bank-level granularity.

| File offset | SNES address | Region | Status | Notes |
|---|---|---|---|---|
| `0x000000..0x007FFF` | `$C0:0000..$C0:7FFF` | Vanilla string content, bank 1 of 4 | ✅ KNOWN | `compiler/linker.py` docstring |
| `0x008000..0x00FFFF` | `$C0:8000..$C0:FFFF` | — | ❓ UNKNOWN | Gap between the linker's declared string-content chunks; not characterized |
| `0x010000..0x017FFF` | `$C1:0000..$C1:7FFF` | Vanilla string content, bank 2 of 4 | ✅ KNOWN | `compiler/linker.py` docstring |
| `0x018000..0x01FFFF` | `$C1:8000..$C1:FFFF` | — | ❓ UNKNOWN | Same pattern |
| `0x020000..0x027FFF` | `$C2:0000..$C2:7FFF` | Vanilla string content, bank 3 of 4 | ✅ KNOWN | `compiler/linker.py` docstring |
| `0x028000..0x02FFFF` | `$C2:8000..$C2:FFFF` | — | ❓ UNKNOWN | Same pattern |
| `0x030000..0x037FFF` | `$C3:0000..$C3:7FFF` | Vanilla string content, bank 4 of 4 | ✅ KNOWN | `compiler/linker.py` docstring |
| `0x038000..0x11CFFF` | — | Engine core, misc (coarse only) | ❓ UNKNOWN at this precision | `rom-map.md` §1 labels banks `$80..$91` "engine core" in general terms; not independently re-verified at file-offset precision this session |
| `0x11D000..0x11F32D` | `$91:D000..$91:F32D` | **String ID (key) table** — 3002 entries × 3 bytes | ✅ KNOWN | [`rom-extension-wishlist.md` §6](rom-extension-wishlist.md); all 3002 slots verified non-null, non-duplicate |
| `0x11F32E..~0x11FE8C` | `$91:F32E..~$91:FE8C` | Dictionary/decompression tables + vocabulary blob | ✅ KNOWN | Directly read this session — zero gap after the string table, real SoE vocabulary confirmed (Nobilia, Podunk, Madronius, …) |
| `~0x11FE8C..0x127FFF` | — | — | ❓ UNKNOWN | Real, uncharacterized gap between the end of the dictionary/vocab data and the start of the script-bank region. Not scanned this session. |
| `0x128000..0x1BFFFF` | `$92:8000..$9B:FFFF` | Vanilla room script bytecode (Script VM) | ✅ KNOWN (mixed density) | `compiler/linker.py` + `rom-map.md` §1. Not fully packed: a prior pass found a 108-byte run of `0x00` at file `~0x1466BB`, inside this range — one confirmed pocket of free space, not a full map of this region's internal gaps |
| `0x1C0000..0x1C7FFF` | — | — | ❓ UNKNOWN | Gap before the first room blob (room `0x06` starts exactly at `0x1C8000`) |
| `0x1C8000..~0x2DE000` | `$9C:8000..~$AD:E000` | **Room blob region** — 127 blobs, `0x1FFDE7` map table embedded near its end | 🟡 MIXED | 561,259 bytes (49%) are real, individually cited room blobs — full per-room table in [`rom-map.md` §2](../.github/rom-map.md). The other ~51% of this span is ❓ **UNKNOWN** — `rom-map.md` itself notes "blobs are not stored in room order," so this is genuine unmapped gap space, not necessarily free |
| `0x1FFDE7..0x1FFFE2` | `$9F:FDE7..$9F:FFE2` | **Map ID table**, 127 valid entries | ✅ KNOWN | [`rom-extension-wishlist.md` §1](rom-extension-wishlist.md); embedded inside the room-blob region above, at the end of bank `$9F` |
| `0x1FFFE3..0x1FFFFF` | `$9F:FFE3..$9F:FFFF` | 7 unused map-table slots (`0x7F..0x85`) + 1 leftover byte | 🟡 **NON-ZERO, UNUSED** | Re-verified this session — see callout above. All 7 fail the room-validity check; none are zero |
| `~0x2DE000..0x2FFFFF` | — | — | ❓ UNKNOWN | Gap after the last known room blob, to the end of the physical 3 MB ROM |
| `0x300000..0x3FFFFF` | `$B0:0000..$BF:FFFF` | **Extension region** (1 MB) | 🚫 **DOESN'T PHYSICALLY EXIST** | The ROM file in this repo is exactly `0x300000` bytes (3,145,728 — confirmed by reading the file directly). This entire region is virtual until a patch grows the file. Already used in production today for overflow string content (`0x300000+`) and new script code (`0x308000+`), per `compiler/linker.py` |

---

## Coarse subsystem labels (not independently re-verified)

For completeness — `rom-map.md` §1's own bank-level table, reproduced as-is. These are broader,
qualitative labels that were **not** reconciled against file offset in this pass (SNES HiROM bank
mirroring makes that non-trivial to do safely without risking a wrong claim — flagged here rather
than guessed at):

| Banks | Primary content | Verified this session? |
|---|---|---|
| `$80..$91` | Engine core, interrupt handlers, V-Blank DMA, PPU drivers | No |
| `$92..$9C` | Script VM bytecode, dialog handlers, event dispatchers | Partially — see script-bank row above |
| `$8C..$A8` | Room map blobs | Partially — see room-blob row above |
| `$C0..$C4` | Text string tables | Partially — first 4×32KB chunks per `linker.py`; rest unverified |
| `$D0..$DF` | CHR tile graphics (LZSS-compressed) | No |
| `$18:0000` | SPC700 audio engine, SFX, music | No |

---

## Room Blob Binary Anatomy (per-room, not global)

"Everscript location" for room logic means *inside each room blob*, not a global table — every
room has this shape ([`rom-map.md` §3](../.github/rom-map.md)):

```
Room Blob
  ├── 13-byte header (origin X/Y, width, height, PPU regs)
  ├── Step-on Trigger table (length-prefixed, 6 bytes/record)
  ├── B-Trigger table (length-prefixed, 6 bytes/record)
  ├── Tile family list (VRAM CHR layout)
  └── Compressed payload: palette deltas, animated tiles, metatile grid, collision, map objects
```

Each trigger record points straight at script bytecode — there's nothing to relocate separately
from the room blob itself. The closest thing to a *global* script ID mechanism is the
`function_key` table at `$928294` (same 3-byte-stride convention as `string_key`, size unconfirmed
— see [`rom-extension-wishlist.md` §6](rom-extension-wishlist.md) blast-radius notes).

---

## What this means for "move X into the extension"

- **String content**: already done — solved, in production use today (`0x300000+`).
- **New rooms (up to 7)**: table slots exist without relocation, but they hold real non-zero
  leftover bytes, not blank space — a patch overwrites them, it doesn't fill in emptiness. Still
  the easiest item on the wishlist.
- **New rooms (beyond 7) / relocating the map table itself**: needs the extension region; scoped
  as moderate engine surgery in wishlist §1.
- **String IDs beyond 3002 / relocating the string-key table**: blocked on a real finding — static
  analysis found *zero* code references to the table's base address, meaning the engine most
  likely addresses it via bank-register state rather than a patchable literal. Needs a live Mesen2
  trace before this can be scoped further. See wishlist §6.
- **New scripts**: already possible without new engine work — `@install()`-declared functions
  already go into extension space (`$B08000+`) today.
- **Everything marked ❓ UNKNOWN above**: genuinely not looked at this session. The two largest
  unknowns by byte count are the ~51% of the room-blob region not accounted for by the 127 cited
  blobs, and the `0x038000..0x11CFFF` span only described at coarse bank level — either could hold
  real free space, but neither has been checked.
