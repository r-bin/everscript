# ROM Extension Wishlist: Hard Engine Limits for a Future Romhack

> [!CAUTION]
> **This is a scoping / research document, not an implementation plan.** No ASM has been
> written, no patch exists, and nothing here should be treated as "ready to build" until its
> claims are individually marked **VERIFIED**. Per `AGENTS.md` §1 ("ROM Hacking is Exact
> Science"), everything below that is not backed by a citation into this repo's own docs is
> explicitly labeled **UNVERIFIED — hypothesis** or **NEEDS INVESTIGATION**. Nothing here should
> be copied into `in/core/`, `patches/`, or any compiler source without independently re-deriving
> it via disassembly or Mesen2.
>
> Sources consulted: `.github/rom-map.md`, `.github/memory-map.md`, `architecture.md`,
> `docs/map_editor_architecture_and_limitations.md`, `docs/map_palette_extraction.md`,
> `docs/map_tile_graphics_decompression.md`, `docs/map_rendering_pipeline.md`,
> `docs/rom-map-overview.md`, `docs/seamless-world-streaming-feasibility.md`,
> `docs/map_objects.md`, `docs/npc_movement_and_waypoints.md`, `.github/skills/*`,
> `in/core/[group] 00_general_enums/**`, and (as an explicitly third-party, unverified reference
> per `AGENTS.md` §3) the sibling `SoETilesViewer` repository's headers and `mainwindow.cpp`.

---

## How to read the per-item sections

Each item has:
- **Current known limit and why** — cited mechanism, or an explicit "not documented" statement.
- **What would need to change** — structural description, verified vs. hypothesis.
- **Blast radius** — what else depends on the same constant/structure, where known.
- **Open questions** — concrete, breakpoint-able questions for Mesen2/disassembly follow-up.
- **Feasibility tier (judgment, not fact)** — my own estimate of engineering difficulty.

---

## 1. Maps beyond 127

### Current known limit and why it exists
**Largely already answered by this repo's own research** — see
[`docs/map_editor_architecture_and_limitations.md`](map_editor_architecture_and_limitations.md)
§7 and [`.github/rom-map.md`](../.github/rom-map.md) §2, both **VERIFIED**:

- The vanilla ROM defines **127 rooms**, `0x00..0x7E`. The Master Map Pointer Table lives at
  `$9FFDE7` (ROM file offset `0x1FFDE7`), 4-byte stride per room (24-bit pointer + 1 padding
  byte). `.github/rom-map.md` §2 documents the specific evidence that entry `0x7F` is not a
  room (padding byte `0xCC` instead of the `0x00` every real entry uses; the bytes it points at
  fail Block 2's `sub_flag` check).
- The table sits near the end of bank `$9F` (`$9F8000..$9FFFFF` → ROM `0x1F8000..0x1FFFFF`).
  Remaining space from `$9FFDE7` to the bank boundary is 536 bytes = 134 possible 4-byte
  entries, so **7 more rooms (`0x7F..0x85`) fit in the existing table without relocating
  anything** — `0x7F` itself being free today.
- The room-loading hook at `$908F6A` (cited in `map_editor_architecture_and_limitations.md` §7.2
  with a disassembly excerpt) does **not bounds-check `room_id`**: it multiplies by 4 and indexes
  `$9FFDE7` directly. `room_id` in WRAM and in the `CHANGE MAP` bytecode instruction is a single
  byte, so the ceiling imposed by *those* fields is **256 rooms (`0x00..0xFF`)**, not 127 — 127
  is a data-table-size limit, not an instruction-width limit.

### What would need to change
- **VERIFIED** (already reasoned through in the cited doc): relocate the table to free ROM
  space (e.g. bank `$40` or `$50`, both cited elsewhere in this repo as HiROM expansion space —
  see `architecture.md` §3.1's `0x300000..0x3fffff` free range) and patch the `LDA
  $9FFDE7,X`-style read at `$908F6E` to `LDA !NEW_MAP_TABLE,X`.
- Up to 7 rooms (`0x7F..0x85`) need **no relocation at all** — just populate the existing free
  slots via `tools/encode_room.py` / `write_room_into_rom()`, which the map-editor doc already
  describes as functional for injecting new blobs and repointing 4-byte table entries.

### Blast radius
- **VERIFIED**: `MAX_ROOMS = 127` in `tools/dump_room.py` is a tooling constant that would need
  updating in lockstep with any table expansion, or every regeneration of
  `.github/rom-map.md` §2 (via the documented regeneration script) would silently omit new rooms.
- **UNVERIFIED — needs investigation**: whether `room_id` is persisted to SRAM anywhere with an
  implicit range assumption (e.g. a save-state room-id field narrower than a byte, or a
  randomizer/seed table that enumerates rooms `0..126`). Nothing in `.github/memory-map.md` was
  found describing a room-id SRAM field during this pass; a full-text search should be repeated
  against any save-format doc if one exists.
- **UNVERIFIED**: whether any other ROM table is sized or indexed off "127" independently (e.g.
  a minimap/world-map icon table, a music-per-room table). None surfaced in the docs reviewed for
  this pass — flagged as an open question below rather than assumed absent.

### Open questions
1. Confirm via Mesen2 (breakpoint on read of `$9FFDE7,X`) that `$908F6A` truly performs no
   range check on `room_id`, across at least one attempted out-of-range transition (e.g. force
   `room_id = 0x7F` via the `CHANGE MAP` opcode/debug tooling and observe behavior) — the doc's
   claim is disassembly-based but not stated as emulator-confirmed live.
2. Is there a second, independent table (minimap icon, room name string index, music cue table)
   that is also indexed by `room_id` and sized at exactly 127/128 entries? Search ROM banks
   `$C0..$C4` (text tables) and any UI/HUD code for a parallel per-room array.
3. Does the `everscript` compiler's linker (`compiler/linker.py`) or any `#memory(...)` directive
   in `in/core/` hard-code an assumption about the room count or the `$9F` bank boundary that
   would need updating alongside a relocated table?
4. If relocating the table, what free-space budget actually exists in banks `$40`/`$50` today,
   after all other patches currently declared in `patches/`? (Not derived in this pass — needs a
   `memory_map.txt` free-space audit before committing to a target bank.)

### Feasibility tier (judgment)
- **7 extra rooms (`0x7F..0x85`), no relocation:** straightforward — the encode/inject pipeline
  already exists and is described as functional in `docs/map_editor_architecture_and_limitations.md`.
- **Beyond that (table relocation to support up to 256 rooms):** moderate engine surgery — one
  well-understood hook to repoint, but requires care around bank-boundary DMA/addressing
  assumptions elsewhere in the loader that were not audited in this pass.

---

## 2. More enemy sprites, especially palette-shifted variants

### Current known limit and why it exists
Two distinct sub-systems are involved, and they are **not equally well understood** in this
repo's docs:

1. **Enemy/character *stat* table** — **VERIFIED structure, UNVERIFIED size.**
   `.github/skills/soetilesviewer/SKILL.md` §4 documents a 74-byte-per-entity stat record
   starting at ROM `$8EB678` (`characterdata.h` in the sibling `SoETilesViewer` repo), with
   fields for HP, attack, defense, animation pointers, and (offset `+$09`) a "default sprite
   palette index." The base address and 74-byte stride are on `AGENTS.md`'s explicit trusted-
   pointer list (`$8EB678` is named directly).
   However: the "142 entries" figure quoted in that skill file is **not actually verified even
   by its source**. I read `SoETilesViewer/mainwindow.cpp` directly (not just the skill's
   summary) and found the loop that populates the character list:
   ```cpp
   for (int i=0; i<142; i++) { // TODO: any indication on how many there are in rom?
   ```
   That comment is the tool author's own admission that 142 is a guess, not a discovered table
   boundary or terminator. **This repo's skill file states 142 as fact; it should not be trusted
   as such.** Flagging this as a documentation risk, not fixing it (out of scope — only
   `docs/rom-extension-wishlist.md` is an authorized edit target for this task).
2. **Enemy sprite *graphics* (CHR blocks, frames, palette-shift variants)** — largely
   **undocumented in this repo**. `soetilesviewer/SKILL.md` §2 lists three more ROM tables as
   "critical resource tables discovered": 16×16 sprite blocks (`$EC0000`), 8×8 sprite blocks
   (`$D80000`), and multi-chunk sprite frame descriptors (`$CA0003`, format decoded in
   `spriteinfo.h`/`spriteblock.h`). Of these, only `$EC0000` is on `AGENTS.md`'s explicit
   trusted-pointer list; `$D80000` and `$CA0003` are documented by extension but their **table
   sizes, indexing bounds, and free-space-after-table are not established anywhere in this
   repo's docs.**
3. **Enemy ID encoding itself is inconsistent across opcodes — VERIFIED as an open question, not
   resolved.** Reading `in/core/[group] 02_functions/[group] 02_everscript_commands/03_sprite.evs`
   directly:
   - `_add_enemy()` emits opcode `0xa2`/`0x3c` with the enemy ID **multiplied by 2**
     (`0x0000 + enemy * 0x02`), annotated `// SPAWN NPC 0x00ca>>1` — i.e. a word-stride index,
     plausibly into the `$CA0003` sprite-frame-chunk table referenced above.
   - `add_enemy()`'s other branch emits opcode `0xba` with the enemy ID passed through
     **unmultiplied** (`code(0xba, enemy, x, y, ...)`).
   These two code paths imply *different* enemy-ID interpretations for different opcodes, and
   neither this file nor any doc reviewed states the maximum legal value for either. This needs
   disassembly of both opcode handlers before any claim about "how many enemy types can exist"
   can be made.

### What would need to change
- **UNVERIFIED — needs investigation** for all three sub-systems above. Any real answer requires:
  finding the actual end/size of the `$8EB678` stat array (terminator? hard-coded loop bound in
  the room-load or battle-init routine reading it? adjacent table that would collide if grown?);
  and finding the actual size/terminator of the `$EC0000`, `$D80000`, and `$CA0003` tables.
- Palette-shifted variants specifically: `03_sprites.evs`'s `add_colored_enemy()` /
  `_add_colored_enemy()` functions (same file, lines ~117-130) already let a script spawn one
  enemy's *behavior* (`CHARACTER_TYPE`) with another enemy's *palette* (`ENEMY` used as a palette
  source) — i.e. **vanilla already supports palette-swapped enemy variants at the script level**,
  reusing the 6 general-purpose sprite palette slots documented in item 4 below. This suggests
  "new palette-shifted enemy variants" may be substantially a **palette-slot problem (item 4)**
  plus **stat-table-slot problem (this item)**, not a new graphics-table problem, if the intent
  is recoloring existing sprite graphics rather than adding wholly new CHR art. That distinction
  matters for scoping and was not confirmed against any evidence — flagged as a hypothesis.

### Blast radius
- **UNVERIFIED**: whether other ROM structures assume a character-stat-table size (e.g. a
  drop-table, a boss-flag bitfield, or a bestiary/compendium feature if one exists) sized off the
  same count. `in/kaizo/faq.md` documents empirically that palette-shifting existing sprites "can
  corrupt and crash the game" and is only done "in controlled scenarios" by the Kaizo hack's own
  author — direct, first-party evidence that the palette-assignment mechanism is fragile in ways
  not fully understood even by an experienced user of this codebase.

### Open questions
1. What terminates or bounds the `$8EB678` character-stat array? Is there a count byte
   elsewhere, or is `142` (or any other number) simply "wherever the next ROM table happens to
   start"? Breakpoint on reads at `$8EB678 + 142*74` and see what's there / whether anything
   reads past it.
2. What is the actual max index for `$EC0000` (16×16 sprite blocks), `$D80000` (8×8 sprite
   blocks), and `$CA0003` (sprite frame chunks)? Is each table pointer-terminated, fixed-count,
   or bounded by the start of the next known ROM resource?
3. Disassemble both the `0xa2`/`0x3c` and `0xba` opcode handlers to determine: is the enemy field
   8-bit or 16-bit in ROM? Does `0xba`'s unmultiplied byte alias into the same ID space as
   `0xa2`/`0x3c`'s `enemy*2`, or a different, disjoint one?
4. Confirm whether `+$09` in the 74-byte stat record ("default sprite palette index") is an index
   into the 8 hardware palette slots described in item 4, or into something larger/different.
5. How much free ROM space exists immediately after each of the `$EC0000`/`$D80000`/`$CA0003`
   tables today, in case new entries could be appended in place rather than relocated?

### Feasibility tier (judgment)
- **Cannot responsibly assign a tier yet.** The stat-table and graphics-table boundaries are
  unknown, and even the ID-encoding scheme across opcodes is not settled. This item needs a
  dedicated Mesen2/disassembly investigation pass before any feasibility estimate would be more
  than a guess — which `AGENTS.md` explicitly forbids presenting as fact.

---

## 3. More sprites active at the same time (concurrent entities)

### Current known limit and why it exists
**VERIFIED, and gives a concrete number** — but note a `// MISMATCH` already flagged elsewhere in
this repo's own docs that I am carrying forward rather than silently resolving:

- `docs/npc_movement_and_waypoints.md` §5 records:
  > `secret-of-evermore-engine` skill §3 says entity slots live in `$7E1000..$7E1FFF`, while
  > `03_sprites.evs:815` says `$7E3DE5..$7E4E88`, stride `0x8E` (142 decimal) bytes per entity,
  > with concrete slot addresses (`ENTITY_1 = 0x3de5`, `ENTITY_2 = 0x3e73`, …). The doc concludes
  > the `in/core/` addresses are authoritative because they're what the compiler actually emits.
- I independently verified the arithmetic implied by that range: reading
  `in/core/[group] 00_general_enums/[group] 05_everscript/03_sprites.evs` directly (its
  `ATTRIBUTE` enum comment, line ~761: *"See data crystals: 7E3DE5 to 7E4E88 = Monster/NPC data
  for the current room. Each Monster/NPC gets x8E bytes of data."*):
  $$(0x4E88 - 0x3DE5) = 0x10A3 = 4259 \text{ bytes}, \qquad 4259 / 0x8E\,(142) = 30 \text{ exactly}$$
  This is a clean, exact division — strong internal-consistency evidence (not proof) that the
  active-entity table holds **30 concurrent Monster/NPC slots** per room, each `0x8E` (142)
  bytes wide, at `$7E3DE5..$7E4E88`. This is the number that gates "more sprites active at the
  same time," if the `03_sprites.evs` range is the correct one (per the doc's own reasoning,
  it's the range the compiler actually uses, so it is the practically load-bearing one).
- The competing `$7E1000..$7E1FFF` range from the `secret-of-evermore-engine` skill is explicitly
  called out there as *unexplained* and *should be re-checked* — I am not resolving that
  discrepancy here, only reporting it, per `AGENTS.md` §2.1's "never silently pick a side" rule.

### What would need to change
- **UNVERIFIED — needs investigation.** Growing the table beyond 30 slots means finding: (a) what
  code computes the table's fixed size (a hard-coded loop bound, most likely, since `0x8E * 30`
  is an exact, suspiciously round-looking budget); (b) what memory immediately follows
  `$7E4E88` today, since WRAM is a flat 128 KB space and anything placed there natively would be
  clobbered by growing the table in place; (c) whether the entity-slot index itself (used to
  compute `$7E3DE5 + index * 0x8E`) is 8-bit and thus not itself a hard ceiling below 30 — i.e.
  whether the real ceiling is *WRAM space*, not an index-width limit.

### Blast radius
- **VERIFIED, first-party evidence of fragility**: `in/kaizo/faq.md` states plainly, as a known
  limitation of the existing Kaizo hack (which already pushes vanilla content further than
  stock): *"Lag free (Sadly it is impossible to write good content without producing lag, and in
  some cases I removed the dog to reduce lag)"*. This is direct evidence that entity count
  already interacts with real-time performance budgets (likely V-Blank/DMA/OAM-write time, not
  just WRAM table size) — raising the concurrent-sprite ceiling is not purely a WRAM-table-size
  problem; it may also run into SNES **hardware** OAM/DMA budgets that no doc in this repo
  currently quantifies for Evermore specifically.
- `docs/map_objects.md` explicitly distinguishes **Map Objects** (tilemap-stamp descriptors,
  unrelated to hardware OAM sprites or entity slots) from **entity slots** — so growing the
  entity table does *not* interact with the Section 3 object-count limits documented in
  `docs/map_editor_architecture_and_limitations.md` §3. Those are separate systems; conflating
  them would be a scoping error.

### Open questions
1. Resolve the `$7E1000..$7E1FFF` vs. `$7E3DE5..$7E4E88` mismatch definitively: breakpoint on
   writes to both ranges during normal gameplay with multiple enemies on-screen, and see which
   one the entity-spawn/AI routines actually touch.
2. Find the code that iterates the entity table (likely a fixed loop bound of 30, or a
   loop-until-sentinel) — confirm whether 30 is a hard-coded constant or a WRAM-budget
   consequence.
3. What occupies WRAM immediately after `$7E4E88`? Is it free, or does another system
   (script VM stack, per `architecture.md`'s WRAM references) start there?
4. Is there a **separate**, harder SNES hardware ceiling in play — the SNES OAM table holds a
   hardware maximum of 128 sprites total and 32 per scanline (well-known SNES PPU hardware fact,
   **external to this repo, not SoE-specific, and not yet cross-checked against how Evermore's
   engine partitions OAM entries per entity** — e.g. multi-chunk sprites per `spriteinfo.h`'s
   `SpriteChunk` format could consume several OAM slots per entity). This needs its own
   Mesen2 OAM-viewer investigation before assuming 30 WRAM slots is the binding constraint.
5. Does the Kaizo hack's documented lag (`in/kaizo/faq.md`) come from entity-table size, OAM/DMA
   bandwidth, or script VM overhead? Without knowing this, "raise the concurrent sprite limit"
   could produce a hack that is WRAM-legal but unplayably slow.

### Feasibility tier (judgment)
- **Moderate-to-major engine surgery, contingent on unresolved hardware-vs-software bottleneck
  question above.** If the ceiling is purely the 30-slot WRAM table, this could be a table-size
  and hard-coded-loop-bound change (moderate). If SNES OAM/DMA bandwidth is the real ceiling
  (open question 4), this becomes a much harder performance-engineering problem, potentially not
  solvable without also touching rendering priority/culling logic. **Judgment only — not
  verified either way in this pass.**

---

## 4. More palette slots for sprites

### Current known limit and why it exists
**VERIFIED, with an important general-SNES-hardware caveat.**

- `in/core/[group] 00_general_enums/02_ram.evs` (lines ~409-417, part of "Authoritative
  Constants" per `AGENTS.md` §3) defines exactly **8 sprite palette slots**:
  ```
  PALETTE_SLOT_1 = <0x1278>   // some sprites hard-coded to slots 1+2, e.g. ENEMY.VIGOR
  PALETTE_SLOT_2 = <0x127a>
  PALETTE_SLOT_3 = <0x127c>   // prioritized by consumables/alchemy
  PALETTE_SLOT_4 = <0x127e>   // TODO: seems unused, always 0x0000
  PALETTE_SLOT_5 = <0x1280>   // preferred starting index for some enemies (offset 0x08)
  PALETTE_SLOT_6 = <0x1282>
  PALETTE_SLOT_BOY = <0x1284> // slot 7
  PALETTE_SLOT_DOG = <0x1286> // slot 8
  ```
  `.github/memory-map.md` line 88 independently lists the same `0x1278…0x1286` range as
  `PALETTE_SLOT_1…8`, corroborating the address range (though its `Word×4` type annotation
  appears to be a stale/inconsistent label vs. the 8 distinct word-sized slots actually named in
  `02_ram.evs` — noted as a documentation inconsistency, not resolved here, per the "never
  silently pick a side" rule).
- `03_sprites.evs`'s `enum PALETTE` (lines ~374-418) lists specific ROM source addresses (e.g.
  `VIGOR_1 = 0xb5ab`, `THRAXX = 0xb18b`) each presumably a 16-color, 32-byte CGRAM-ready block,
  DMA'd into one of these 8 WRAM staging slots before being pushed to hardware CGRAM. Comments in
  that enum note real allocation constraints observed empirically: `VIGOR` only gets slots 1+2,
  `MOSQUITO`/`FOOTKNIGHT` get slots 1-3, slot 4 is empty/unused, `THRAXX`/`CARLTRON`/`STERLING`/
  `MAGMAR` start at slots 5-6.
- **Why 8, and not more, at the hardware level**: SNES Mode 1 PPU has a fixed CGRAM budget of
  256 total colors, hard-partitioned by hardware into 8 background palettes (used for BG1/BG2,
  documented for Evermore specifically in `docs/map_palette_extraction.md` as CGRAM palettes
  0-7) and 8 **separate** object/sprite palettes (this second half of CGRAM is **standard SNES
  PPU hardware architecture — external, well-established fact, not itself derived from this
  repo's docs, and not yet cross-referenced against Evermore-specific CGRAM-address DMA code
  the way the BG palette path was in `map_palette_extraction.md`**). If Evermore's 8 named
  sprite slots already map 1:1 onto the SNES PPU's 8 hardware OBJ palette registers, then
  **"more sprite palette slots" is not a software-table limit at all — it is the SNES PPU's
  fixed CGRAM budget**, and cannot be worked around without changing what data occupies the
  other CGRAM half (a much larger, cross-cutting change) or without SA-1/coprocessor tricks
  that do not exist on stock hardware. This mapping was **not directly confirmed** in this pass
  — see open questions.

### What would need to change
- **If** the 8 slots are already the SNES's 8 physical OBJ palette registers (unconfirmed): there
  is no room to add slots without giving up BG palette budget or accepting fewer simultaneous
  distinct BG colors — a hardware ceiling, not an engine one.
- **If** the 8 slots are instead a *software* staging/rotation scheme sitting on top of a larger
  usable hardware budget (e.g. Evermore reserves fewer than 8 OBJ palettes for BG-adjacent
  purposes and could reassign more): this would be a WRAM staging-buffer and DMA-destination
  (`CGADD`) change, in the same family as the already-documented BG palette loader in
  `docs/map_palette_extraction.md` (`$90D020`, `$8085FA`) but targeting the OBJ half of CGRAM
  instead — structurally plausible by analogy to that verified BG mechanism, but **not itself
  documented or traced for the OBJ path anywhere in this repo.**

### Blast radius
- **VERIFIED, first-party evidence this is already a live pain point**: `in/kaizo/faq.md` lists,
  as a known and accepted defect of the existing hack: *"Visual glitch free (Some sprites will
  have the wrong palette, because the map uses too many palettes at once)"* and separately
  *"Changing the palette of a sprite looks fancy, but can corrupt and crash the game (I try to
  change them only in controlled scenarios)."* Both are direct, empirical confirmation that the
  8-slot budget is already exhausted or over-committed by ambitious vanilla-plus-Kaizo content,
  and that the palette-assignment code path is fragile enough to crash when pushed. Any patch
  raising this limit inherits that fragility as a starting point, not a clean slate.
- `03_sprites.evs`'s own comments (`VIGOR` hard-coded to slots 1+2, boss-specific slot 5 offset
  preferences) show that **specific enemies have hard-coded slot assumptions** baked into
  vanilla behavior — a naive slot-renumbering or expansion would need to audit every such
  hard-coded reference, not just the 8 named constants.

### Open questions
1. Does Evermore's DMA loader write sprite palettes to `CGADD` in the `0x80..0xFF` (OBJ) CGRAM
   half, and if so, at what specific `CGADD` values per slot? (Direct analogy to the verified BG
   loader `$90D020`/`$8085FA` in `map_palette_extraction.md`, but for sprites — not yet traced.)
2. Are all 8 SNES hardware OBJ palette registers actually in use by these 8 named slots, or does
   Evermore only use e.g. 6 of the 8 hardware registers for gameplay sprites, reserving others
   for HUD/UI sprites (health bars, menu cursors, ring-menu icons)? If some hardware slots are
   reserved for UI, is there recoverable budget there in rooms where that UI isn't shown?
3. What determines the run-time mapping from a `PALETTE` enum's ROM source address (e.g.
   `THRAXX = 0xb18b`) to one of the 8 WRAM slot addresses — is it hard-coded per-enemy (as the
   `enum PALETTE` comments suggest) or computed/allocated dynamically at spawn time? This
   determines whether "add more slots" requires editing every enemy's spawn logic or just
   widening a shared allocator.
4. Root-cause the `in/kaizo/faq.md`-documented palette-corruption crash: is it a WRAM staging
   buffer overrun (writing to slot 4 or beyond when the buffer assumes fewer), a CGRAM DMA timed
   wrong relative to V-Blank, or something else? This determines whether raising the slot count
   fixes or worsens that existing crash risk.
5. Confirm whether slot 4 (`PALETTE_SLOT_4`, marked `// TODO: seems to be unused, always
   0x0000` in `02_ram.evs`) is truly dead/reserved and could be safely repurposed as an
   incremental step short of a full hardware-budget expansion.

### Feasibility tier (judgment)
- **If slot 4 is genuinely unused and safely reclaimable**: straightforward, single-slot gain.
- **If the goal is going beyond the SNES's 8 physical OBJ CGRAM palettes**: not feasible on
  stock hardware without giving up BG color budget or other CGRAM-resident data — this would be
  major rearchitecture at best, and may simply be **hardware-impossible** without a
  coprocessor/expansion chip (see item 5). This determination hinges entirely on open question 2
  above, which was not resolved in this pass.

---

## 5. SA-1 port

### Current known limit and why it exists
**Not documented anywhere in this repo.** I searched `.github/`, `docs/`, `architecture.md`,
`dev_notes.md`, `vanilla_bugs_and_oddities.md`, all `.github/skills/*`, and the sibling
`SoETilesViewer`/`script_all` dump for any mention of "SA-1", "SA1", or coprocessor-related
terms — **zero hits**. This repo's compiler and patch pipeline (`architecture.md` §1) targets
straight HiROM (`.github/rom-map.md` §1: "3 MB (24 Mbit) HiROM cartridge") with no coprocessor
references anywhere in `compiler/linker.py`'s described memory model or `patches/`'s described
Asar-based hook system.

### What would need to change
**Entirely unscoped.** An SA-1 port is a categorically different undertaking from the other four
items: it is not "extend an existing table" but "change the fundamental CPU/memory
architecture the entire ROM executes on." At minimum, unresolved even at a conceptual level for
this repo:
- Whether Evermore's HiROM layout and all its bank-relative addressing (which this repo's own
  `compiler/linker.py` bank-aware allocator depends on, per `architecture.md` §3.1) would need a
  wholesale remap for SA-1's different memory map (SA-1 ROM is typically mapped and banked
  differently, and the SA-1 core runs at a much higher effective clock with its own internal
  RAM) — this is **general SA-1 hardware knowledge, external to this repo, not independently
  verified against Evermore's actual bank layout in this pass.**
- Whether any of Evermore's DMA-timing-dependent code (e.g. the V-Blank palette/animation DMA
  budget explicitly called out as tight in `docs/map_editor_architecture_and_limitations.md` §2.3
  — "the SNES V-Blank interval can only transfer ~6 KB per frame") would behave identically under
  SA-1's different bus/DMA characteristics, or would need retiming.
- Whether the 65c816 assembly this repo already ships in `patches/*.asm` (assembled via Asar per
  `architecture.md` §2 and the `snes-asm-asar-patching` skill) is SA-1-core-compatible as-is, or
  requires SA-1-specific opcode/addressing adjustments — **not determined in this pass.**

### Blast radius
Everything. A CPU/coprocessor-level port would touch every ROM read, every DMA, every bank
boundary the compiler's linker currently reasons about, and every existing patch in `patches/`.
No existing doc in this repo attempts to scope this, and this pass did not attempt to originate
that scope either — doing so responsibly would require dedicated SA-1 hardware research
independent of anything in this repository.

### Open questions
1. Does any prior SA-1 romhack of a similarly-sized (~3MB) SNES HiROM game exist as a reference
   point for feasibility/tooling (external research, not derivable from this repo)?
2. Would porting be "run the existing ROM under an SA-1 mapper with minimal changes" (if that is
   even meaningful) or "rewrite the addressing/bank model from scratch" — these are wildly
   different scopes and this repo's docs give no basis for picking between them.
3. What would the *benefit* actually be for items 1-4 above? (SA-1 offers faster CPU and extra
   RAM, which could independently relax the WRAM-table and DMA-bandwidth constraints identified
   in items 2-4 above — but this is speculation stated explicitly as speculation, not a finding.)
4. Does Asar (this repo's assembler, per `architecture.md` §2) even support SA-1 target
   assembly, and would `compiler/linker.py`'s memory model need to be rewritten to understand a
   second address space?

### Feasibility tier (judgment)
- **SA-1-tier extremely hard, acknowledged out of scope for real planning in this document.**
  This item is included only to record that it was searched for and found completely
  unaddressed elsewhere in the repo — not to sketch a plan. Any future work here should start
  from external SA-1 documentation and a dedicated feasibility spike, not from this document.

---

## 6. More string IDs

### Current known limit and why it exists
**VERIFIED — a fixed-size ROM pointer table, hard-coded base address, corroborated by this
repo's own first-party compiler source and by an empirical compile run performed in this pass.**

- Vanilla dialogue/text is addressed through a 3-byte-stride pointer table at ROM `$91D000`
  (file offset `0x11D000`). `compiler/ast_everscript.py`'s `StringKey` class (lines 1556-1565)
  hard-codes `self.address = 0x91d000 + self.index` and enforces `index % 3 == 0` — this is
  **first-party, executable compiler source**, not a third-party claim. The same base address
  and 3-byte/"MSB=compressed" structure are independently corroborated by
  `.github/skills/snes-memory-mapping/SKILL.md` §2.3 ("String Key Table `$91D000..$91F32D`") and
  by `compiler/linker.py`'s own `#memory()` docstring (line 15: `string keys = 0x91d000..0x91F32D
  (index 0x0000-0x232b, 3 bytes, MSB&80=compressed)`). The specific dictionary/decompression
  sub-table addresses cited alongside this in `.github/skills/soetilesviewer/SKILL.md` §5
  (`$91F32E`, `$91F3AE`, `$91F3EC`/`$91F66C`, `$91F46C`/`$91F7D5`) are sourced from the
  third-party `SoETilesViewer`/`text.h` and are **not independently confirmed in this repo** —
  flagged below as an open question, not treated as fact.
- The table holds exactly **3002 slots**: indices `0x0000..0x232B` in steps of 3
  (`(0x232B - 0x0000) / 3 + 1 = 3002`), spanning `$91D000..$91F32D` — this is the exact range the
  README's own top-level example declares (`string_key(0x0000)..string_key(0x232b)`), and
  `architecture.md` §3.1 labels the identical declaration "ROM text pointers."
- Each 3-byte entry is a 24-bit pointer to the actual string bytes, which vanilla stores in slow
  ROM banks `$C0..$C3` (per `compiler/linker.py`'s own docstring, lines 6-21); the pointer's MSB
  (`&0x80`) flags Evermore's proprietary dictionary/byte-pair text compression.
- This fixed table is the **only** source the compiler ever draws string keys from:
  `MemoryManager.allocate_text()` (`compiler/linker.py` lines 113-130) pops one `StringKey` off a
  list populated exclusively from whatever `string_key(...)` ranges a `.evs` file declares in its
  `#memory()` block. A repo-wide search of every `.evs` file's `string_key(...)` declaration
  (40+ hits) found **no file anywhere in this repo that ever declares a `string_key` range
  outside `0x0000..0x232b`** — every project either claims the full vanilla range ("all string
  keys") or a subset of it, most commonly the vanilla-preserving half
  `string_key(0x0546)..string_key(0x232b)` ("last half of string keys," e.g.
  `in/kaizo/main.evs` line 2, `patches/connect_acts.evs` line 8).
- The engine-facing operand is a genuine 16-bit field, so field width is **not** the practical
  ceiling. `text(id)` compiles to opcode `0x51` and `subtext(id)` to opcode `0x52`
  (`in/core/[group] 02_functions/[group] 02_everscript_commands/06_strings.evs` lines 36-38,
  91-93), each taking a 2-byte little-endian word — verified directly by
  `tests/integration/opcodes/test_51_text.py` / `test_52_subtext.py`
  (`text(0x0123)` compiles to bytes `51 23 01`). That word is the `StringKey`'s raw byte-offset
  index, added to base `$91D000` at run time — per the tests' own docstrings ("set text from word
  list in next two bytes + 91d000") and disassembly-derived comments already embedded in the
  compiler source (`06_strings.evs` line 37: `"SHOW TEXT 10bf FROM 0x91e0bf compressed..."`,
  i.e. `0x91d000 + 0x10bf = 0x91e0bf`). A full 16-bit offset would run past bank `$91`'s 64 KB
  boundary long before exhausting the field, so the real ceiling is the ROM space actually
  reserved for the table, not the operand width.
- **Direct first-party evidence the budget is already treated as scarce in practice**:
  `README.md`'s own "Known Bugs" section states, of `in/practice.evs`: *"NPCs are trashing some
  dialoges to make space for the new strings and B-triggers"* — i.e. declaring "all string keys"
  lets the compiler repoint **any** existing vanilla dialogue's key slot to new custom content,
  permanently discarding the original text. Every project that instead declares only
  `string_key(0x0546)..string_key(0x232b)` is a direct, first-party mitigation for this exact
  problem — reserving half the table so at least those NPCs keep their original lines.
- **Empirical confirmation performed in this pass**: I compiled `in/kaizo/main.evs` (the Kaizo
  overhaul, `architecture.md`'s own description of a full-game high-difficulty romhack) against
  the real ROM present in this repo's working tree (`Secret of Evermore (U) [!].smc`) using the
  actual `everscript.py` pipeline (`.venv/bin/python everscript.py --rom "Secret of Evermore (U)
  [!].smc" --patches patches "in/kaizo/main.evs"`, exit code 0), then read the resulting
  `out/memory_map.txt`. Of its declared `string_key(0x0546)..string_key(0x232b)` budget (2552
  total slots), **1336 slots remained unallocated and 1216 were consumed** — roughly 48% of its
  reserved half-budget used by one large, but not the largest conceivable, romhack project. The
  same run's `out/memory_map.txt` shows the string **byte-storage** pool (as opposed to the
  key/pointer pool) is nowhere near exhausted: several entire free 32 KB banks (`$F10000`,
  `$F20000`, `$F30000`, `$F40000`, plus a partial `$F07AF3` range) remained unallocated after the
  same compile. **String content length is not the bottleneck; the number of distinct string IDs
  is.**

### What would need to change
- **String CONTENT (longer/more distinct string byte data) — already effectively solved.** The
  `0x300000..0x3fffff` extension region (documented identically in `compiler/linker.py`'s
  `#memory()` docstring and `.github/skills/snes-memory-mapping/SKILL.md` §2.1) already
  contributes additional string-byte storage alongside the four vanilla slow-ROM text banks
  (`$C0..$C3`), and the `MemoryManager`'s "text" bucket (distinct from the "text_key" bucket)
  draws from it automatically. This pass's empirical Kaizo compile shows large amounts of that
  pool remain genuinely unused — this half of "more strings" is a solved problem within the
  existing dynamic-allocation architecture the README describes, not something this wishlist item
  needs to scope further.
- **The number of distinct string IDs — structurally the same kind of problem as item 1
  (maps).** `StringKey.__init__` hard-codes `self.address = 0x91d000 + self.index` — no code path
  in the compiler lets a `.evs` file declare a *second* string-key table at a different base; the
  formula itself, not just the currently-declared index range, is fixed to `$91D000`. Growing
  past 3002 distinct string IDs needs one of:
  1. **Relocating/extending the pointer table** to unused ROM space, by direct analogy to item
     1's room-table relocation — this requires the engine's `0x51`/`0x52` opcode handlers (and
     possibly `0x8c`, see Blast radius) to be patched to read a different base or stride.
     **Not located or disassembled in this repo**, so whether this is a single-hook patch (like
     item 1's one `LDA` instruction) or scattered across multiple vanilla routines is unknown.
  2. **Reclaiming existing slots more deliberately.** Structurally what
     `in/practice.evs` already does today (per the README's own admission), just done ad hoc
     rather than by design. Needs no ROM-table change, but stays capped at 3002 total and
     permanently discards the original vanilla dialogue it reclaims.
  3. **A hybrid opcode-level change**: patch `0x51`/`0x52` (and any other opcode confirmed to
     reference `$91D000`) to read their operand as pointing into a *new*, additional table placed
     in the extension region, leaving the vanilla table and its neighboring ROM data untouched.
     Structurally the cleanest option, but requires disassembling the opcode handlers first
     (not done in this pass) to confirm the base address is a simple patchable immediate.

### Blast radius
- **UNVERIFIED**: the `function_key` table (`compiler/ast_everscript.py` lines 366-388) is a
  structurally identical 3-byte-stride pointer table at a different hard-coded base
  (`0x928294 + index`), used for indirect/symbolic script calls (`call_id(...)`). Every `.evs`
  file that declares a `function_key(...)` range in this repo stays within the same
  `0x0000..0x232b` index span used for `string_key` (e.g. `architecture.md` §3.1's own example
  declares both ranges identically) — it is **not confirmed** whether this means the
  `function_key` table is also genuinely sized at 3002 entries, or whether that figure is simply
  copy-pasted convention from the `string_key` example. `in/kaizo/main.evs`'s own comments
  (`// 0x1719 seems to be used by the engine`, `// 0x1B7b is the first known global script`) show
  this project has already discovered vanilla-engine boundaries inside the `function_key` range
  empirically, by trial, rather than from a documented table-size citation — suggesting nobody in
  this repo has yet fully mapped the true edges of either pointer table independently of the
  `string_key` figure.
- **UNVERIFIED**: whether any other vanilla system that displays text by ID (item/ingredient
  names, menu labels) reads pointers from this same `$91D000` table or from a separate,
  undiscovered one. `in/core/[group] 02_functions/[group] 02_everscript_commands/
  04_map_manipulation.evs` line 308 shows opcode `0x8c` ("Actual save dialog") also takes an
  `install_string(id)` operand, i.e. a second, confirmed consumer of the same string-key pool
  beyond `0x51`/`0x52` — any relocation patch needs to find and repoint every such consumer, not
  just the two opcodes exercised by the dialogue-specific tests in this repo.
- `docs/review.md` §4.5 independently flags **"Hardcoded ROM addresses in `_wipe_strings`"**
  (`compiler/codegen.py`, cited again at `docs/review.md` line 588 as `0x11d000`, `0x232D`) as
  existing, already-known technical debt: the `$91D000` base and `0x232b`/`0x232D` upper bound are
  duplicated in at least two places in the compiler source (`ast_everscript.py`'s `StringKey`
  class and `codegen.py`'s `_wipe_strings`) — both would need to move in lockstep with any future
  table-relocation patch, and `docs/review.md` already flags this duplication as unaddressed,
  independently of this wishlist item.

### Open questions
1. Disassemble the `0x51`, `0x52`, and `0x8c` opcode handlers in Mesen2 to determine whether
   `$91D000` is a literal 3-byte immediate baked into each handler (patchable the way item 1's
   `LDA $9FFDE7,X` was), or computed some other way. This determines whether relocating the table
   is a small, well-scoped patch or something harder.
2. Confirm or refute, via Mesen2 memory-viewer inspection of `$91F32E` onward, whether the
   soetilesviewer-derived dictionary-table addresses are real and genuinely immediately adjacent
   to the string_key table's last entry. This is currently sourced only from the third-party
   `soetilesviewer` skill (`text.h`), not independently confirmed in this repo, and is the
   load-bearing claim behind "no free space to grow the table in place."
3. Is there free ROM space after the end of the dictionary tables (wherever they actually end)
   where a *relocated and enlarged* string_key table could live without disturbing anything else?
4. Does any vanilla system other than opcodes `0x51`/`0x52`/`0x8c` read pointers from the
   `$91D000` table, or from an as-yet-undiscovered separate one? `.github/rom-map.md` line 26
   generically describes banks `$C0..$C4` as "text string tables" without distinguishing whether
   they're all addressed through this one key table.
5. Is `function_key`'s real table size (base `$928294`) actually 3002 entries like `string_key`,
   or is `0x232b` for it simply inherited from the `string_key` example without independent
   verification? Relevant to whether a combined key-table relocation patch would be more
   efficient than two separate ones — out of scope for fixing this item alone.
6. This pass only empirically measured consumption for Kaizo's reserved *half* of the table.
   Compile a project that declares the full `string_key(0x0000)..string_key(0x232b)` range (e.g.
   one of the `in/custom_bosses/*.evs` or `in/test/*.evs` files that already claim "all string
   keys") and read its `out/memory_map.txt` to see how close a maximal single project gets to the
   full 3002-slot ceiling.

### Feasibility tier (judgment)
- **Growing string CONTENT** (longer/more distinct string byte data): already effectively
  solved — the existing `0x300000..0x3fffff` extension region and the `MemoryManager`'s
  text/text_key split already provide this, and this pass's empirical Kaizo compile shows large
  amounts of that byte-storage pool remain genuinely unused.
- **Growing the number of distinct string IDs beyond 3002**: structurally the same tier as item 1
  (maps) — a fixed-size ROM pointer table with a hard-coded base address baked into the compiler,
  gated by engine-side opcode handlers not yet disassembled in this repo. If those handlers read
  `$91D000` as a single patchable immediate (open question 1) and the adjacent dictionary tables
  can be relocated cleanly (open questions 2-3), this is **moderate engine surgery**, comparable
  to item 1's "relocate table + repoint one load instruction" case. If the adjacent dictionary
  tables cannot be cleanly separated from the pointer table — i.e. text *decompression itself*
  would need touching — this becomes **substantially harder** than item 1, since it risks breaking
  every existing string's rendering, not just growing a table. **Not assignable more precisely
  than that without the Mesen2 disassembly work in the open questions above.**
- **Reclaiming existing slots more deliberately** (no ROM-structure change): straightforward, and
  already happening informally per the README's own admission — formalizing it (e.g. a compiler
  warning when a declared `string_key` range would silently discard vanilla dialogue still
  reachable by unmodified rooms) would be a compiler quality-of-life improvement, not a
  hard-limit fix.

### Empirical check: unused string-key slots in vanilla
**VERIFIED — read directly from the real ROM's raw bytes in this pass; answers "are there
freely-reclaimable (null-pointer) slots in vanilla?" with a concrete no.**

- **Method.** `scratch/string_key_null_scan.py` (throwaway analysis script, not a tracked tool —
  left in `scratch/` per this repo's own convention for one-off work) opens
  `Secret of Evermore (U) [!].smc` read-only and reads all 3002 `string_key` entries (indices
  `0x0000..0x232b` stepping by 3, per `StringKey.__init__`'s own `index % 3 == 0` rule), 3 raw
  bytes each, at file offset `0x11D000 + index`. That file offset comes from this repo's own
  HiROM formula (`.github/rom-map.md` §1: `file_offset = (bank & 0x3F) << 16 | address`), applied
  to SNES address `$91D000` — `(0x91 & 0x3F) << 16 | 0xD000 = 0x11D000`, matching the file offset
  already established in this item's earlier sections, so the formula is cross-checked against
  existing citations rather than assumed. The ROM file is exactly 3,145,728 bytes (3 MB, no
  copier header), matching `.github/rom-map.md`'s own "3 MB (24 Mbit) HiROM cartridge"
  description, so no header-offset correction was needed.
- **What was measured, per entry**: (a) whether the raw 3-byte value is exactly `0x000000` (null
  pointer — the strong "genuinely unused" signal the task asked for), and (b) whether its value,
  with the compression-flag bit (bit 23, i.e. `value & 0x800000`) masked off, is identical to
  another entry's masked value (duplicate target — the softer, more ambiguous signal).
- **Result, run against the real ROM in this repo's working tree**:
  - **0 of 3002 entries are null** (`0x000000`).
  - **0 of 3002 entries are non-null duplicates** of another entry's (compression-flag-masked)
    target.
  - **All 3002 entries are unique, non-null pointers.**
  - Split by the two ranges this repo's projects already treat differently: the vanilla-critical
    range `0x0000..0x0545` (450 slots) is **0 null / 0 duplicate / 450 unique (100%)**; the
    Kaizo-reclaimed range `0x0546..0x232b` (2552 slots) is **0 null / 0 duplicate / 2552 unique
    (100%)**. The two ranges do not differ — neither has any null or duplicate-target slot.
  - As a secondary, purely observational data point (not itself part of the null/duplicate
    question): the raw high byte of every entry's 3-byte value takes only 4 distinct values across
    the whole table (`0x00`, `0x01`, `0x80`, `0x81`), and the earliest entries' (compression-flag
    masked) values increase in small monotonic steps (e.g. index `0x0000` -> masked `0x000000`,
    `0x0003` -> `0x000017`, `0x0006` -> `0x00002a`) — consistent with strings packed back-to-back
    with no gaps, but decoding what the high byte's low 7 bits actually select (a bank index? an
    offset into `$C0`/`$C1` specifically vs. the full `$C0..$C3` range `compiler/linker.py`'s
    docstring describes?) is a pointer-format question this script did not attempt to answer, since
    it is outside the null/duplicate scope this check was asked to perform.
- **Sanity check against other repo sources**: searched `docs/`, `dev_notes.md`, and
  `vanilla_bugs_and_oddities.md` for any prior mention of a specific known-dead `string_key` index
  — found none. No existing document in this repo names a specific "unused" string ID to compare
  against, so this pass's `0` count could not be cross-validated against a second independent
  source; it stands only on the direct ROM read described above.
- **What this does and does not prove.** A null (`0x000000`) entry would mean no string is
  currently assigned to that slot's target — evidence it's freely reclaimable without discarding
  real vanilla content. Finding **zero** such entries means, at the raw-pointer level, **every one
  of the 3002 slots — in both ranges — currently points at real, distinct compressed string data**;
  there is no low-risk "free" subset to reclaim by this signal. This does **not** rule out a
  *different* kind of unused slot this check cannot detect: a slot could hold a valid, non-null,
  non-duplicate pointer to real string bytes that are nonetheless **dead** — never actually read at
  runtime because no live script anywhere calls `text()`/`subtext()`/`install_string()` (opcodes
  `0x51`/`0x52`/`0x8c`) with that index. Detecting *that* requires scanning all script bytecode for
  every operand reference to each of the 3002 indices, which this pass did not attempt — it remains
  open question 4 above (does any vanilla system read this table by a path other than those three
  opcodes) plus an unasked-but-related one: which of the referenced indices are ever actually
  invoked by reachable code. Also, per open questions 1-2 above, whether opcodes `0x51`/`0x52`/`0x8c`
  would crash or misbehave on a genuinely null entry is still undetermined and moot in vanilla,
  since this pass found none — but would matter immediately if a future relocation/extension patch
  (tier-2/3 options above) ever introduces one.
- **Effect on feasibility.** This finding does not change the feasibility tier in the Summary Table
  below: it **reinforces**, rather than contradicts, the tier's existing statement that reclaiming
  slots "permanently discards the original vanilla dialogue it reclaims" — there is no null-pointer
  loophole that would make any slot reclaim non-destructive. The Summary Table cell is left
  unchanged.

### Patch complexity assessment: relocating string_key to the extension region

**Method and honest scope caveat.** No 65816 disassembler is available in this environment
(checked: not in `requirements.txt`, not offline-pip-installable) and no live emulator/Mesen2
session is available either. Everything in this subsection is a **static byte-pattern scan of the
raw ROM file** (`scratch/string_key_code_ref_scan.py`, throwaway, not a tracked tool, same
convention as `scratch/string_key_null_scan.py`), not a disassembly and not a confirmed
instruction trace. A byte sequence matching "plausible opcode + literal `$91D000`" is a
**candidate**, never proof the CPU executes it as that instruction — it could be data (another
table, string content, graphics bytes) that coincidentally matches. Per `AGENTS.md`'s golden rule,
every claim below is labeled by exactly how it was obtained.

#### Step 1 — code-reference scan (open question 1)

**Methodology sanity check, performed first.** Before trusting a zero-hit result, the same
opcode+long-operand scan was run against the **already-known-and-cited** Master Map Pointer Table
base `$9FFDE7` (item 1's own subject). It found exactly **one** hit: file offset `0x108F6A`, opcode
`0xBF` (`LDA long,X`), operand `E7 FD 9F` — i.e. SNES `$908F6A: LDA $9FFDE7,X`. This is the exact
address and instruction shape item 1's section already cites (*"the room-loading hook at
`$908F6A`... `LDA $9FFDE7,X`-style read"*), found independently by this pass's scan with no prior
knowledge fed into the search pattern beyond the target address. **This confirms the scan
methodology correctly finds real, already-documented long-addressing code references when they
exist** — the results below are not a broken or vacuous search.

**Result against `$91D000` (strong form — opcode + 3-byte absolute-long operand `00 D0 91`,
covering all 17 plausible long/long-indexed/JSL/JML opcodes listed in the script, not just the
task's short list):** **0 hits, anywhere in the 3,145,728-byte ROM.** In fact the raw 3-byte byte
sequence `00 D0 91` (with *any* preceding byte, not just a plausible opcode) occurs **0 times** in
the whole ROM — it is not present as an instruction operand, not as embedded data, and not as a
literal 3-byte initializer sequence anywhere.

**Result against `$91D000` (weak form — split 16-bit immediate `LDA #$D000` within 16 bytes of a
`$91` bank-byte reference):** **0 hits.** The exact byte sequence `A9 00 D0` (`LDA #$D000`,
16-bit-accumulator form) occurs exactly **once** in the entire ROM, at file offset `0xCB391`
(SNES `$8CB391`, inside the Room Map Blob bank range `$8C..$A8` per `.github/rom-map.md` §1's bank
table). Reading its actual context (`... C2 20 A9 00 D0 8F 01 D7 7F A9 E0 D0 8F 04 D7 7F ...`)
decodes as `REP #$20; LDA #$D000; STA $7FD701; LDA #$D0E0; STA $7FD704` — a sequence of *different*
16-bit immediate constants (`$D000`, then `$D0E0`) being written to WRAM staging addresses in bank
`$7F`. `$D000` here is one of several unrelated literal constants, not a `$91`-bank-adjacent
reference — checked and ruled out as a false positive, not counted as a weak hit.

**Cross-check with the sibling `function_key` table.** The same raw-3-byte scan was run against
`function_key`'s independently hard-coded base, `$928294` (`compiler/ast_everscript.py` lines
366-388, byte pattern `94 82 92`): also **0 raw occurrences anywhere in the ROM**. Two
structurally-identical, independently hard-coded compiler-source base addresses both produce a
clean zero — this is useful corroborating signal that the *absence* isn't an artifact of this
specific target address, and narrows the plausible explanations (see below).

**An exploratory, beyond-task-spec supplementary scan** (plain 16-bit absolute addressing, bank
implied by the CPU's Data Bank Register rather than encoded in the instruction — e.g. `LDA
$D000,X` = `0xBD 00 D0`, `STA $D000,Y` = `0x99 00 D0`) turned up 12 raw hits for the low word
`$D000` under a plausible absolute-mode opcode, two of which are physically located **inside bank
`$91` itself**: file offsets `0x11C28B` and `0x11C2A1` (SNES `$91C28B`/`$91C2A1`), both `STA
$D000,Y` (`0x99 00 D0`). Decoding the surrounding bytes by hand: `CLC; ADC $02; AND #$03FF; STA
$D000,Y; INY; INY; CPY #$01C0; BCC <loop>` — a loop computing a **monotonically increasing,
10-bit-masked running sum** and storing it as a sequence of 224 words starting at absolute address
`$D000,Y`. This is the *same shape* (monotonic 16-bit offset sequence) as the dictionary
offset-table data found in Step 2 below. **This is a genuinely interesting lead, not a confirmed
hit**: whether this loop's target bank (set by the CPU's Data Bank Register at the time it runs,
which this static scan cannot determine) is actually `$91` — and thus whether this is code that
builds or refreshes one of the dictionary offset tables at `$91D000`+something — is undetermined
without a live Data Bank Register read via Mesen2. Flagged as a concrete, addressable target for
future live tracing, not counted among the "0 hits" figure above.

**What the clean zero (even as raw data) plausibly means.** Since `00 D0 91` does not appear
*anywhere* in the ROM — not even as three separately-written bytes — the base address is not
stored as a single 24-bit literal constant anywhere the CPU could read it, nor built via any of
the instruction/addressing-mode shapes this scan searched. Combined with the bank-`$91`-resident
`STA $D000,Y` candidate above, the most plausible **hypothesis** (explicitly labeled as such, not
established) is that the real opcode handlers for `0x51`/`0x52`/`0x8c` live *inside* bank `$91`
itself and use cheap 2-byte absolute addressing (bank implied by Data Bank Register = Program Bank
Register, a standard 65816 idiom for same-bank data access) rather than a literal 3-byte
long-address operand — which would make them invisible to this scan's literal-operand search by
construction, not because no code references the table. **Open question 1 is not resolved by this
pass.** A live Mesen2 read-breakpoint on `$91D000` (any read, any addressing mode) during a
dialogue-triggering playthrough is the only way to find the real reference(s), confirm the Data
Bank Register value at the point of access, and determine whether the base is a patchable literal
at all.

#### Step 2 — table adjacency and free-space scan (open questions 2 and 3)

**File-offset translation, per this repo's own documented formula** (`.github/rom-map.md` §1's
HiROM mapping, and cross-checked against `scratch/string_key_null_scan.py`'s prior derivation):
`file_offset = (bank & 0x3F) << 16 | address_low16`. For SNES `$91F32D`: `(0x91 & 0x3F) << 16 |
0xF32D = 0x11F32D`.

**Exact adjacency check.** `StringKey`'s last table entry (index `0x232B`) occupies file bytes
`0x11F32B..0x11F32D` (raw bytes `8C AD 81`, read directly from the ROM in this pass) — i.e. the
table's true final byte is at `0x11F32D`. The byte immediately following, at `0x11F32E`, is `0x65`
(`'e'`) — the first byte of readable dictionary-token-shaped data (see below). **There is a
zero-byte gap: the claimed dictionary region begins on the very next byte after the string_key
table's last entry, with no padding between them.** This directly confirms, via direct ROM read in
this pass (not merely repeating the third-party claim), that whatever sits at `$91F32E` is
tightly packed against the table — reinforcing rather than contradicting the "no free space to
grow the table in place" branch of open question 2/3.

**Shape-match against the `soetilesviewer`/`text.h`-claimed dictionary structure**
(`.github/skills/soetilesviewer/SKILL.md` §5 — third-party claim, not previously confirmed in this
repo). Reading 4 KB of raw bytes from `$91F32D` forward (well over the task's 2 KB minimum):
- `$91F32E` onward: short (1-3 byte) printable-ASCII fragments separated by `0x00` and interleaved
  with high-bit-flagged bytes (`0x81`, `0x86`, `0x96`, ...) — e.g. `"th"`, `"ou"`, `"as"`, `"d"`,
  `"re"`. **Shape-consistent** with the claimed "2-character lookup" table at `$91F32E`.
- `~$91F3AE` onward: single printable ASCII letters (`e`, `o`, `t`, `a`, `n`, `r`, `i`, `s`, `h`,
  `l`, `u`, ...). **Shape-consistent** with the claimed "single character lookup" table at
  `$91F3AE`.
- `~$91F3EC` onward: a run of little-endian 16-bit values that increase monotonically in small
  steps (`0x0000, 0x0008, 0x000C, 0x0010, 0x0015, 0x0019, 0x001F, 0x0024, ...`) — the classic shape
  of an offset table into a separate string pool. **Shape-consistent** with the claimed dictionary
  offset table at `$91F3EC`.
- `~$91F46C` onward: a second, independent monotonically-increasing 16-bit sequence (`0x0000,
  0x0006, 0x000D, 0x0018, 0x0023, 0x002D, 0x0039, ...`). **Shape-consistent** with the claimed
  second offset table at `$91F46C`.
- `~$91F66C` onward: a long run of genuine, readable, null-terminated English words directly
  relevant to Secret of Evermore's actual dialogue vocabulary — common words (`and`, `are`,
  `formula`, `ingredients`, `trade`, `village`, `volcano`, ...) followed further on by capitalized
  words including in-game proper nouns (`Nobilia`, `Podunk`, `Bugmuck`, `Ebon`, `Elizabeth`,
  `Horace`, `Ivor`, `Madronius`, `Carltron`, `Centurian`, `Omnitopia`, item names `Amulet`,
  `Beads`, `Bronze`, `Coins`, `Formula`, `Helmet`, `Sheath`, `Silver`). This word blob runs from
  `~$91F66D` to `~$91FE8C` (ends with `"You've\0"` followed by non-ASCII bytes). The claimed
  `$91F7D5` address falls **inside this same contiguous word blob** (at the start of the word
  `"about"`), consistent with a hypothesis — not confirmed, since the actual decode algorithm was
  not run — that the two offset tables (`$91F3EC` and `$91F46C`) index into two different starting
  points (`$91F66C` and `$91F7D5`) within one shared pool of null-terminated word strings, rather
  than two disjoint blobs.
- **What this does and does not prove.** The byte *shapes* found (2-char tokens, 1-char tokens, two
  monotonic offset tables, a large blob of real SoE-vocabulary words) match the third-party claim's
  general structure closely enough to be genuine corroboration, not coincidence — a random 4 KB
  region of ROM would not plausibly contain a naturally-ordered, monotonically-increasing offset
  sequence immediately followed by hundreds of real English words matching this specific game's
  character and place names. This is **static shape-matching, not a runtime algorithm
  confirmation** — the actual decompression logic (`text.h`'s claimed `d & 0xC0` branch dispatch)
  was not executed or traced against any real compressed string in this pass.

**Free-space scan (open question 3).** A programmatic scan for the first run of 64+ identical
bytes, starting at `$91F32D` (file `0x11F32D`) and extending through the entire remainder of the
ROM, found: **zero such runs anywhere in the ~150 KB immediately following the string_key/
dictionary region** (scanned through file offset `0x140000`, i.e. all of banks `$92`/`$93` and the
start of `$94` — matching `.github/rom-map.md`'s own description of banks `$92..$9C` as "Script
Virtual Machine bytecode streams, dialog handlers, event dispatchers," which this scan's density
is consistent with). The **first** 64+-byte identical-byte run anywhere after the table is at file
offset `0x1466BB` (SNES `~$9466BB`), **108 bytes of `0x00`**, roughly **157 KB past** the
string_key table's end. Even this is not obviously "free ROM space budgeted for future use": it is
one of a series of similarly-sized (~104-108 byte) `0x00` runs spaced roughly 129 bytes apart
(`$9466BB`, `$94673C`, `$9467C1`, `$946840`, `$9468C1`, ...), which looks like *periodic
per-entry padding inside a different, unidentified fixed-stride table* rather than a genuinely
reclaimable free block — this pass did not identify what table that padding belongs to, so it is
**not** being recommended as a relocation target.

**Bottom line for open questions 2 and 3:** the dictionary tables are confirmed, via direct ROM
read in this pass, to sit with **zero gap** immediately after the string_key table, and their
general byte shape corroborates the third-party claim closely (though the decode algorithm itself
remains unverified). There is **no usable free space anywhere near the table** — not adjacent, and
not within the next ~150 KB of the same bank region — so growing the table in place is not
supported by this pass's evidence.

#### Structural patch sketch (descriptive only — not compilable code, per this document's own
"scoping, not implementation" rule)

Given Step 1 found **zero confirmed** (only one unresolved candidate, and one ruled-out false
positive) patch sites, and Step 2 found **no adjacent or nearby free space**, a real relocation
patch cannot yet be scoped to "N confirmed sites, here is exactly what to change." What can be
said structurally, contingent on live-tracing resolving open question 1:

1. **Locate the real reference(s).** Live Mesen2 read-breakpoints on `$91D000..$91F32D` during a
   playthrough that triggers dialogue via all three known consumers (`text()`/opcode `0x51`,
   `subtext()`/opcode `0x52`, `install_string()`/opcode `0x8c`) would need to catch every actual
   CPU access, record the Program Counter and Data Bank Register at each hit, and disassemble the
   surrounding routine. This is the step this pass's static analysis could not substitute for — the
   `$91C28B`/`$91C2A1` lead above is the most concrete starting point a live session should check
   first.
2. **If the reference(s) turn out to be literal long-address operands** (this pass found none, but
   a live trace could still surface one via an addressing-mode/register-state combination this
   static scan didn't search, e.g. indirect-long or a computed jump table): patch each confirmed
   site's 3-byte operand from `00 D0 91` to the new base, by direct analogy to item 1's single `LDA
   $9FFDE7,X` -> `LDA !NEW_TABLE,X` repoint.
3. **If the reference(s) turn out to be same-bank absolute addressing relying on an implied Data
   Bank Register** (this pass's leading hypothesis, unconfirmed): relocating the table would require
   either (a) relocating the *handler code itself* into the new target bank so the implied-DBR
   idiom keeps working, or (b) inserting an explicit bank-byte change (`PHB`/`PLB` or an added `LDA
   #$new_bank : PHA : PLB`) before the access and switching the addressing mode to long — a strictly
   larger, more invasive edit than item 1's one-instruction repoint, since it changes code size and
   potentially bank-boundary timing assumptions the loader wasn't written expecting.
4. **Define the new table.** A relocated/enlarged `string_key` table would live in this repo's own
   already-declared extension region `0x300000..0x3fffff` (`compiler/linker.py`'s `#memory()`
   docstring, cited identically elsewhere in this item), sized to whatever new entry count is
   wanted, and populated by copying (or regenerating from) the existing 3002 entries' pointer data —
   itself unaffected by this relocation, since Step 2 showed the dictionary tables and the pointer
   *targets* (`$C0..$C3` and the extension string-content pool) do not need to move, only the
   index-to-pointer lookup table's base does.
5. **Every consumer must be repointed, not just one.** Item 6's existing Blast Radius section
   already lists `0x51`, `0x52`, and `0x8c` as the three known opcode consumers, plus flags that
   this list itself might be incomplete (open question 4, unresolved by this pass) — a real patch
   would need to re-run the live-trace step above with enough scripted content to exercise all
   three opcodes plus any other dialogue-adjacent system, since a static scan (per Step 1) cannot
   distinguish "this opcode never appears in this ROM's code" from "this opcode's reference uses an
   addressing mode this scan didn't search."

**What is still unverified even after this pass:** whether `$91D000` is a patchable literal at all
(open question 1, not resolved — the strongest lead is an unconfirmed same-bank candidate, not a
literal operand); whether any additional, currently-unknown consumer exists beyond `0x51`/`0x52`/
`0x8c`; the exact runtime decode algorithm for the dictionary tables (only their static byte shape
was corroborated, not their behavior); and whether the `$9466BB`-region padding run (or any other
ROM location) is genuinely reclaimable free space versus reserved padding inside an unidentified
table. All four require either live Mesen2 tracing or further disassembly this pass's tooling
constraints made impossible.

#### Revised feasibility tier (judgment, explicitly labeled — supersedes nothing in the tier
above, since that tier already correctly predicted this outcome)

This pass's static evidence **does not** let "moderate engine surgery, item-1-like" be upgraded to
a confirmed, scoped estimate — if anything, it narrows the *optimistic* branch of the existing
tier (*"if those handlers read `$91D000` as a single patchable immediate... this is moderate
engine surgery, comparable to item 1"*) without being able to confirm it holds. Two honest,
evidence-based observations change the picture slightly from where item 6's existing tier left it:

- **The zero-hit result itself is evidence, not just an unresolved gap.** Item 1's `$9FFDE7`
  table *is* found by exactly this scan methodology, in the exact form the doc already describes.
  `$91D000` (and, as a cross-check, `function_key`'s `$928294`) is **not** found in any of the same
  forms, anywhere in the ROM, even as raw data. That is a meaningfully different starting position
  than item 1 had — item 1's relocation patch could point to a *found* literal instruction to
  repoint; this item cannot yet point to one at all. **This makes a firm "item-1-tier" claim
  premature** — the true tier could still turn out to be item-1-simple (a single same-bank absolute
  reference, patchable by moving the handler alongside the table) or could turn out to be
  materially harder (multiple same-bank references scattered through the dialogue-handling code in
  bank `$91`, each needing a bank-switch insertion rather than a one-word repoint).
- **Table adjacency and free-space findings are now confirmed, not merely third-party-sourced.**
  This closes the empirical half of open questions 2-3 for good: no adjacent or nearby (~150 KB)
  free space exists, so **in-place growth is ruled out** and any expansion must relocate to the
  extension region — item 6's existing tier already anticipated this as the likely outcome, and
  this pass's direct ROM read now supports it as a confirmed fact rather than an assumption.

**Bottom line:** static byte-pattern analysis alone could not close open question 1, and this
pass's own honest reading of its results is that it *narrows toward*, without confirming, a
same-bank-implied-addressing hypothesis that would make relocation *more* invasive than item 1's
single-instruction repoint (code movement or an inserted bank switch, not just an operand edit).
**A live Mesen2 tracing session remains a hard prerequisite before this item's complexity can be
assigned a number** — this pass narrows the search (a concrete `$91C28B`/`$91C2A1` lead to check
first) but does not substitute for it.

---

## 7. More tiles / tile families

### Terminology correction (found this pass, stated up front because it changes the scope)

**VERIFIED, disassembly-based — supersedes the plain-prose description used elsewhere in this
repo's docs.** [`docs/map_palette_extraction.md`](map_palette_extraction.md) §1-3 (`Zero-Trust
Trace Methodology`, real 65c816 disassembly of `$90D020..$90D0A3` and `$8085FA`, both cited by
address with instruction-level listings) establishes that a **"Tile Family" is a 32-byte CGRAM
palette block (16 colors × 2 bytes), not a CHR graphics resource.** The routine at `$90D05C`
computes `ROM address = family_id * 32 + $C322` (five `ASL A` instructions = `×32`, then `ADC
#$C322`), DMAs exactly 32 bytes per family into a WRAM staging buffer (`$7E61A7`), then
`$8085FA` DMAs that buffer into **CGRAM** at `CGADD = $0010` (Color 16 = Palette 1). This is a
**palette-loading pipeline**, structurally unrelated to the CHR *tile graphics* pipeline
documented separately in
[`docs/map_tile_graphics_decompression.md`](map_tile_graphics_decompression.md) (master pointer
table at `$EE0000`, resolved via a completely different routine, `$8CC88C`).

This directly contradicts the plain-prose description used in two other places in this repo,
flagged here as `// MISMATCH` per `AGENTS.md` §2.1 rather than silently corrected in those files
(only this wishlist doc is an authorized edit target for this task):
- `docs/map_editor_architecture_and_limitations.md` §2.2 calls a "Tile Family" *"a compressed
  graphics bank containing specific 8×8 character patterns and 16×16 metatile building blocks"* —
  no disassembly citation backs this claim, and it is contradicted by the disassembly-sourced
  description above.
- `.github/rom-map.md` §3's room-blob-anatomy diagram (line 203) labels the same room-header field
  `"Array of 16-bit Tile Family IDs (**VRAM CHR layout**)"` — the parenthetical is wrong by the
  same disassembly evidence: the DMA target is **CGRAM** (palette color data, `$2121`/`$2122`),
  not VRAM (character/tile pixel data, `$2116`/`$2118`). `tools/dump_room.py`'s own field name
  (`tile_families`, `parse_blob_layout` docstring line 263) is neutral and not itself wrong, only
  the doc's descriptive parenthetical is.

The disassembly-based doc (concrete addresses, byte counts, register writes, DMA channel setup —
independently legible as real 65c816 code) is treated here as the load-bearing source over the two
plain-prose descriptions, per `AGENTS.md`'s preference for disassembly/empirical evidence over
unsourced prose — but this is a live cross-doc inconsistency in this repo that should be corrected
in those two files in a future pass, not silently by this one.

**Practical consequence for this item's scope**: "more tiles / tile families" is actually **two
independent sub-systems** with two independent bottlenecks, and conflating them (as the room-blob
diagram's field name already invites) would misdiagnose the real limit. They are scoped
separately below.

### 7A. More Tile Families (CGRAM background palettes)

#### Current known limit and why it exists
**VERIFIED, disassembly-based, with one caveated open lead.**

- SNES Mode 1 provides exactly **8 background CGRAM sub-palettes of 16 colors each** (general SNES
  PPU hardware fact, already cited and cross-checked against Evermore's own engine code in
  `docs/map_palette_extraction.md` §1 and `docs/map_editor_architecture_and_limitations.md` §2.1).
  Palette 0 (`CGRAM` colors `0..15`) is reserved for HUD/dialogue/system use and is **not** loaded
  from a room's tile family list (`docs/map_palette_extraction.md` §4's mapping table, "Not loaded
  by room family"). This leaves **7 usable BG palette slots** (Palettes 1..7) for a room's own
  content.
- The room-blob header field itself (`.github/rom-map.md` §3: `tile_family_count:1, families (2
  bytes each)`) is an **8-bit count**, so the field's own width would allow up to 255 — the field
  width is not the practical ceiling.
- **The engine-side loader disassembly caps the number of families loaded into CGRAM in a single
  invocation to 7**, independent of the room-blob's declared count
  (`docs/map_palette_extraction.md` §3.1, `$90D020..$90D03F`, cited with a full instruction
  listing):
  ```
  90D030: ED 8A 0F  SBC $0F8A      ; N - start_offset
  90D037: C9 08 00  CMP #$0008     ; Cap at maximum 8 palettes
  90D03A: 30 03     BMI $90D03F
  90D03C: A9 07 00  LDA #$0007     ; Capped to 7
  ```
  This is a **hardware-budget-driven cap baked directly into the loader routine**, not a data-table
  size limit — it exists because there are only 7 usable CGRAM BG palette slots to DMA into, not
  because the room-blob's count field or any other table is undersized.
- **Empirical check performed this pass** (`scratch/tile_family_table_size_scan.py`, using this
  repo's own `tools/dump_room.py::dump_room()` across all 127 vanilla rooms): **74 of 127 rooms
  declare exactly 7 families** (the max that fits the 7-slot CGRAM budget in one load), but **22
  rooms declare more than 7** — up to **14** in the most extreme case; the remaining rooms declare
  fewer than 7. This is a genuinely new, disassembly-consistent finding: the `SBC $0F8A` subtracts
  a **runtime WRAM offset** (`$7E2437`, "initial family offset... 0 at room load" per the doc's own
  comment) from the declared count before capping — meaning the *same* room-blob family list can
  plausibly be re-walked by this loader at a **nonzero start offset** later (e.g. a scripted
  event triggering a second batch load of families `7..13` into the same 7 CGRAM slots),
  overwriting the first batch. **This is a hypothesis consistent with the disassembly and the
  empirical >7-family room counts, not independently confirmed in this pass** — no doc reviewed,
  and no live trace performed, confirms `$7E2437` is ever set nonzero at runtime, or by what
  scripted mechanism. Flagged as the single most valuable open question for this sub-item (see
  below), since if true, it means **vanilla already has a working "more than 7 palette banks per
  room" mechanism** — just not more than 7 *simultaneously* resident in CGRAM.
- **Master catalog size** (the total number of *distinct* family entries defined anywhere in the
  ROM, as opposed to how many one room can use at once): the same empirical scan found vanilla
  content references **365 distinct family ids, contiguously dense from `0x0000` to `0x016C`
  (365/365 = 100% occupancy, no gaps)** across all 127 rooms. This is a different number from — and
  not gated by — the 7-slot CGRAM cap above; the catalog can hold (and vanilla already uses) far
  more than 7 distinct palette banks in total, they're simply never all resident in CGRAM at the
  same instant.

#### What would need to change
- **If the goal is "more than 7 background palettes visible in a room at the same instant"**: this
  is the **same SNES Mode 1 hardware ceiling** `docs/rom-extension-wishlist.md` §4 already
  identified for *sprite* CGRAM palettes — the BG half of the same fixed 512-byte CGRAM budget.
  Not feasible on stock hardware without giving up something else in CGRAM (in this case,
  Palette 0's reserved HUD/text colors, which is a much more visible, riskier tradeoff than the
  sprite-palette-4 case in item 4). **This is very likely a hardware-impossible ask on stock
  hardware**, same tier as the sprite-palette-budget half of item 4 — not independently re-derived
  here beyond noting it's the same physical CGRAM resource.
- **If the goal is "more than 365 distinct palette banks defined in the ROM" (growing the
  catalog, not the per-room simultaneous budget)**: this is a table-size/free-space question,
  structurally similar to item 6's `string_key` table. This pass's scan
  (`scratch/tile_family_table_size_scan.py`) read 256 bytes immediately after the highest
  currently-referenced family's 32-byte block (file `0x1CF0C2`) and found **no run of 64+ identical
  bytes anywhere in the following 64 KB** — the same "no adjacent free space" signal item 6 found
  for `string_key`. The master table's base (`0x1CC322`) also falls **inside** the already-cited,
  only-partially-mapped "Room blob region" span (`docs/rom-map-overview.md`: `0x1C8000..~0x2DE000`,
  itself flagged "~51% UNKNOWN — blobs are not stored in room order"), so growing this table in
  place risks colliding with an as-yet-uncharacterized room blob, not obviously-free space.
  Relocating the table (same shape as item 6's relocation sketch: repoint the `ADC #$C322`
  immediate at `$90D065`, a **found, disassembly-cited literal operand** — unlike item 6's `$91D000`
  case, this one *is* already known to be a patchable immediate in the loader disassembly quoted
  above) is the structurally cleanest path, contingent on confirming no other code also embeds
  `#$C322` or `$9CC322` as a literal (not scanned in this pass — see open questions).
- **If the goal is "more than 255 families per room's own declared list"**: would need widening the
  room-blob header's 1-byte `tile_family_count` field — but per the 7A findings above, this is
  almost certainly moot in practice, since only ~14 has ever been observed in vanilla and the
  7-slot CGRAM cap makes anything beyond what the `$7E2437`-offset re-load mechanism can exploit
  functionally invisible anyway.

#### Blast radius
- **VERIFIED**: `$90D065`'s `#$C322` literal is the one confirmed patchable site for a table
  relocation — narrower and more concrete than item 6's `$91D000` search, which found zero literal
  operand hits anywhere in the ROM. This sub-item is **easier to scope** than item 6's for exactly
  this reason.
- **UNVERIFIED**: whether any other routine (e.g. a palette-cycling/day-night/weather effect system,
  if one exists) also reads `$9CC322` or embeds `#$C322`/`#$9C` as a literal — not scanned this
  pass. A relocation patch would need to repeat item 6's byte-pattern scan methodology
  (`scratch/string_key_code_ref_scan.py`'s approach) against `9C C3 22` / `#$C322` before being
  confident only one site needs patching.
- **UNVERIFIED**: whether `$7E2437` (the "initial family offset" WRAM variable) is ever written
  to a nonzero value by any vanilla script or event routine. This is the load-bearing unknown for
  understanding what the >7-family rooms' extra entries are actually *for* — without it, this
  wishlist item cannot state whether "families 7..13" in a 14-family room are dead data, a designed
  swap-in-later mechanism, or evidence of some other consumer entirely.

#### Open questions
1. Confirm via Mesen2 (write-breakpoint on `$7E2437`) whether and when the engine ever sets a
   nonzero "initial family offset," and whether it re-invokes `$90D020` with it during normal
   gameplay in one of the 22 vanilla rooms with >7 declared families. This is the single most
   valuable unresolved question in this sub-item — it would confirm or refute the "vanilla already
   has a 2-batch palette-swap mechanism" hypothesis above.
2. Scan the full ROM for any other literal reference to `$9CC322`/`#$C322` besides `$90D065`,
   using the same byte-pattern methodology item 6's code-ref scan already validated (confirmed
   against the known-good `$9FFDE7` case).
3. What determines which of the (up to) 14 declared family ids gets dropped versus loaded, if
   `$7E2437` is never touched and the 7-slot cap simply discards ids `7..N-1` silently? Does the
   room ever visibly look "wrong" for those 22 rooms, or is the >7 count itself dead data left over
   from map-editor tooling (e.g. an unused staging list)? Not determinable without a live trace or
   without visually comparing a rendered room (via `tools/render_map.py`) against actual game
   footage for one of the 22 rooms.
4. Is there truly no usable free space anywhere in the `0x1CC322` neighborhood, or does the 64 KB
   window this pass scanned simply not reach far enough? (Item 6's equivalent scan needed ~150 KB
   before finding *any* free-space signal, and even that wasn't confirmed reclaimable.)

#### Feasibility tier (judgment)
- **More than 7 simultaneously-visible BG palettes**: very likely hardware-impossible on stock
  SNES CGRAM without sacrificing Palette 0's reserved HUD/text budget — same tier as item 4's
  hardware-ceiling branch.
- **More than 365 distinct catalog entries (not simultaneous)**: moderate engine surgery,
  *more concretely scoped than item 6* — one confirmed patchable literal operand (`$90D065`),
  contingent on the not-yet-performed full-ROM reference scan (open question 2) turning up no
  other consumers.
- **Exploiting the possible existing `$7E2437` multi-batch mechanism** (if open question 1
  confirms it's real and controllable): potentially **no ROM-structure change needed at all** for
  modest growth beyond 7 effective palettes per room — this would be the cheapest possible win in
  this entire document if confirmed, but is currently only a disassembly-consistent hypothesis, not
  a fact.

### 7B. More Tile Graphics (CHR 16×16 metatile patterns)

#### Current known limit and why it exists
**VERIFIED, disassembly-based** — this is the system `docs/map_tile_graphics_decompression.md`
actually documents (§1-2, routines `$8CC88C`/`$8CC9C0`/`$90934B`, master pointer table at `$EE0000`
/ ROM file offset `0x2E0000`), and is a **structurally distinct** system from 7A's palette table:

- **Table structure**: 3-byte-stride, 24-bit little-endian SNES pointer per `tile_id`, i.e. a
  16-bit `tile_id` operand (not an 8-bit field like 7A's room-header count) indexes directly into
  the table: `table_addr = 0x2E0000 + tile_id * 3` (`docs/map_tile_graphics_decompression.md` §2,
  cited with the exact disassembly of the lookup at `$8CC88C..$8CC8AB`). A full 16-bit `tile_id`
  gives a theoretical index space of 65,536 entries (196,608 bytes) — **operand width is not the
  practical ceiling here**, unlike nothing in this table's own indexing scheme forces a small
  catalog size.
- **Compression scheme is NOT the same LZSS used elsewhere in room blobs** — this directly answers
  one of this item's assigned open questions. `.github/rom-map.md` §3's room-blob anatomy shows
  Blocks 1-3 (tile-palette deltas, the 2D Markov metatile grid, and the planar metatile layout) are
  dispatched via `$8C988D` with `sub_flag` values documented in `.github/rom-map.md` §2's table as
  `lzss`/`raw` per room. The **CHR tile graphics** decompressor is a completely different routine
  (`$8CC9C0`), with its own **16-mode dual-stream nibble/bit dispatch table at `$8CCC40`**
  (`docs/map_tile_graphics_decompression.md` §5.2 — 16 distinct modes for zero-fill, byte-fill,
  repeat-last-word, NOT-byte, etc.), operating on a fixed 128-byte-per-tile output rather than a
  variable-length room-layout stream. These are **different algorithms in different ROM banks**,
  not two invocations of the same LZSS scheme — confirmed by direct comparison of the two docs'
  cited disassembly, not by name alone.
- **Per-room simultaneous budget is a hardware VRAM ceiling, not a table-size one**:
  `docs/map_editor_architecture_and_limitations.md` §2.1 (SNES Mode 1 general hardware fact,
  cross-checked against Evermore's own engine in the same doc) states total VRAM is a fixed 64 KB,
  of which ~56 KB remains for CHR tiles after BG1/BG2 tilemap allocation — **~1,792 unique 8×8
  tiles, i.e. ~448 of the 16×16 four-sub-tile metatiles this table actually stores.** A single
  room's Block 1 tile-ID delta list (decompressed into WRAM `$7FC300`, per
  `docs/map_tile_graphics_decompression.md` §1) is empirically far smaller than that ceiling in the
  one cited example (**97 unique tile IDs for room `0x33`**, same doc §1) — consistent with rooms
  already being scoped comfortably inside the VRAM budget rather than pushing against it, though
  this pass did not survey all 127 rooms' Block 1 sizes to confirm none come close to the ~448-tile
  ceiling (see open questions).

#### `$D0..$DF` CHR-bank claim — resolved this pass (was flagged "not verified" in `docs/rom-map-overview.md`)

**VERIFIED, static byte-pattern evidence from `scratch/tile_family_chr_bank_scan.py`, run this
pass.** The coarse subsystem table in `docs/rom-map-overview.md` ("Coarse subsystem labels (not
independently re-verified)") lists `$D0..$DF` = "CHR tile graphics (LZSS-compressed)," explicitly
marked `Verified this session? No`. This pass's script run refutes both halves of that claim:

1. **The verified `$EE0000` master pointer table itself is nowhere near `$D0..$DF`.** `$D0:0000` to
   `$DF:FFFF` masks (per this repo's own HiROM formula) to file offset `0x100000..0x1FFFFF`.
   `$EE0000` masks to file offset `0x2E0000` — outside that span entirely (script output:
   `Inside $D0..$DF span (100000-1FFFFF)? False`).
2. **Scanning the actual resolved target banks of 3,000 `tile_id` table entries** (the script's
   histogram output, reproduced verbatim): resolved CHR tile data physically lands in banks `$80`,
   `$8B..$9B`, `$9D..$9F`, `$A0..$AF`, and `$C3..$C9` — **never once in a bank whose own identity is
   `$D0..$DF`.** Some of those target banks (`$90..$9B`, `$9D..$9F`) do mask to the *same*
   `bank & 0x3F` file-offset range that `$D0..$DF` would also mask to — because HiROM mirrors
   banks `$C0..$FF` onto the same physical ROM bytes as `$80..$BF`/`$00..$3F` via that identical
   masking formula. **This is the most likely explanation for how the "$D0..$DF = CHR graphics"
   label originated**: whoever wrote it was very plausibly looking at the *file-offset range*
   (which genuinely does contain CHR-pointer targets, because it's shared with banks `$90..$9F`)
   and mislabeled it with the `$D0..$DF` bank alias rather than the `$90..$9F` bank that's already
   independently documented (as "Script VM bytecode... dialog handlers" and part of the "Room blob
   region" elsewhere in the same `rom-map-overview.md` document). **`$D0..$DF` does not appear to
   be a real, independently-populated CHR graphics region — it is very likely a stale/mislabeled
   alias of already-documented banks.** Correcting `docs/rom-map-overview.md`'s own table is out of
   scope for this task (only this file is an authorized edit target), but is recommended as a
   direct, low-risk follow-up.
3. As a sanity cross-check within the same script run, the already-VERIFIED `string_key` table
   (`$91D000..$91F32D`, item 6) *does* fall inside the nominal `$D0..$DF` file-offset span — further
   confirming the span is not uniquely "CHR graphics," since it demonstrably also contains a
   completely different, already-well-documented subsystem.

#### What would need to change
- **Growing the per-room simultaneous CHR budget (more than ~448 unique 16×16 tiles resident at
  once)**: a genuine SNES VRAM hardware ceiling (64 KB fixed), same category as item 4's
  hardware-ceiling branch and `docs/seamless-world-streaming-feasibility.md` §1.5's identical
  observation for the same fixed resource. Not feasible on stock hardware.
- **Growing the master catalog** (total distinct 16×16 tiles definable across the whole ROM, not
  simultaneously resident): the pointer table's 16-bit `tile_id` operand already supports up to
  65,536 entries structurally — **UNVERIFIED how many entries actually exist today** (this pass did
  not determine the table's real current size or where it ends / what sits after it; the earlier
  `tile_family_chr_bank_scan.py` scan only sampled `tile_id` 0-2999 densities by *target bank*, not
  the table's own upper bound). This is a concrete, addressable open question, not answered by
  either script run this pass.

#### Blast radius
- Shares the same VRAM-budget ceiling `docs/seamless-world-streaming-feasibility.md` §1.5 already
  cites as a blocker for a completely different feature (seamless room streaming) — any change to
  how many CHR tiles can be resident at once has implications for that document's own analysis too,
  not just this wishlist item.
- **UNVERIFIED**: whether the table's target-bank distribution found by this pass (concentrated in
  `$8B..$9B`, `$AD..$AF`, `$C3..$C9`) means CHR tile *data* is deliberately co-located with the
  room-blob region and text-bank region rather than living in a single dedicated bank range — if
  so, "growing the catalog" may mean finding scattered free space across several already-crowded
  regions rather than one contiguous block, a harder scoping problem than item 6's single-table
  relocation.

#### Open questions
1. What is the master `$EE0000` table's actual current entry count / upper bound? Neither script
   run this pass determined this — it would need either a terminator scan (first entry whose
   pointer decodes to implausible/garbage data) or finding what ROM structure begins immediately
   after the table's last real entry.
2. Confirm `docs/rom-map-overview.md`'s `$D0..$DF` row should be corrected to remove the "CHR tile
   graphics" claim, given this pass's evidence it's very likely a mislabeled alias of `$90..$9F` —
   a documentation fix, not a code investigation, but out of scope for this task's single
   authorized edit target.
3. Across all 127 rooms (not just the one cited example, room `0x33`, with 97 tiles), what is the
   largest Block 1 tile-ID list, and how close does it come to the ~448-tile VRAM ceiling? This
   would confirm or refute whether vanilla content already presses against the VRAM budget anywhere
   (relevant context copied from `docs/seamless-world-streaming-feasibility.md` §1.5's identical
   unresolved question, asked there for a different feature).

#### Feasibility tier (judgment)
- **More simultaneous CHR tiles per room**: very likely hardware-impossible on stock SNES VRAM,
  same tier as the hardware-ceiling branches of items 4 and 7A.
- **Larger total CHR catalog (not simultaneous)**: **cannot responsibly assign a tier** — the
  table's real current size/terminator was not determined this pass (open question 1), so whether
  there's already ample headroom in the unused part of the 65,536-entry index space or whether the
  table is already large and tightly packed against neighboring data (as 7A's palette table turned
  out to be) is genuinely unknown.

---

## Summary Table

| # | Item | Core mechanism found? | Concrete number found? | Feasibility (judgment) |
|---|---|---|---|---|
| 1 | Maps beyond 127 | Yes — VERIFIED (`$9FFDE7`, 4-byte stride, no bounds check at `$908F6A`) | Yes — 7 free slots now, 256 max via byte `room_id` | Straightforward (7 rooms) → Moderate (relocated table) |
| 2 | More enemy sprites / palette variants | Partially — stat table stride verified, size is an admitted guess in the source tool itself; graphics tables located but unsized | No — "142" explicitly debunked as a TODO guess, not a real count | Not assignable yet — needs investigation |
| 3 | More concurrent sprites | Yes, with an open first-party doc mismatch — VERIFIED math for one candidate range (30 slots × 0x8E bytes) | Yes, conditionally — 30 slots (pending mismatch resolution) | Moderate-to-major, contingent on WRAM-vs-hardware-OAM question |
| 4 | More sprite palette slots | Yes — VERIFIED 8 named WRAM slots, unverified mapping to SNES hardware OBJ CGRAM | Yes — 8 slots, 1 possibly reclaimable (slot 4) | 1 slot maybe easy; beyond 8 total may be hardware-impossible |
| 5 | SA-1 port | No — zero references anywhere in this repo | No | SA-1-tier extremely hard / unscoped |
| 6 | More string IDs | Yes — VERIFIED (`$91D000`, 3-byte stride, hard-coded base in compiler source, 3002 slots) | Yes — 3002 total slots; empirically 1336/2552 free in Kaizo's reserved half after a full-project compile in this pass | String content: solved already (extension ROM) → String ID count: Moderate (item-1-like) → possibly harder if decompression dictionary tables can't be cleanly separated |
| 7 | More tiles / tile families | Yes — VERIFIED two distinct systems: 7A palettes (`$9CC322`, 32-byte stride, disassembly of `$90D020..$90D065` incl. a patchable `#$C322` literal); 7B CHR graphics (`$EE0000`, 3-byte stride, distinct 16-mode dual-stream decompressor at `$8CC9C0`, confirmed NOT the room-blob LZSS scheme) | Yes for 7A — 7 usable CGRAM slots (hardware cap, disassembly-confirmed at `$90D037`), 365 distinct catalog ids referenced (100% dense, 0..364); yes for 7B's per-room VRAM ceiling (~448 16×16 tiles), no for 7B's total catalog size (table upper bound not determined this pass) | 7A: simultaneous-slot growth likely hardware-impossible (same CGRAM budget as item 4); catalog growth moderate, more concretely scoped than item 6 (found literal operand); possible free "2nd batch" mechanism via `$7E2437` unconfirmed. 7B: simultaneous-tile growth likely hardware-impossible (VRAM); catalog growth not assignable (table bound unknown). `$D0..$DF` CHR-bank claim in `docs/rom-map-overview.md` refuted this pass — very likely a stale alias of already-documented `$90..$9F` |

Every "Yes" above is traceable to a specific file and line cited in its section; every "No" or
"partially" is stated as such rather than filled in with a plausible-sounding guess, per
`AGENTS.md`'s golden rule.
