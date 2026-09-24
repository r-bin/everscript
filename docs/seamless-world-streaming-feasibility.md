# Seamless World Streaming: Feasibility Scoping for Secret of Evermore

> [!CAUTION]
> **This is a scoping / research document, not an implementation plan.** No ASM has been written,
> no patch exists, and nothing here should be treated as "ready to build" until its claims are
> individually marked **VERIFIED**. Per `AGENTS.md` §1 ("ROM Hacking is Exact Science"), every claim
> not backed by a citation into this repo's own docs/code is explicitly labeled **UNVERIFIED —
> hypothesis** or **NEEDS INVESTIGATION**. Nothing here should be copied into `in/core/`,
> `patches/`, or any compiler source without independently re-deriving it via disassembly or
> Mesen2.
>
> Sources consulted: `docs/map_rendering_pipeline.md`, `docs/map_decompression_trace_analysis.md`,
> `docs/map_tile_graphics_decompression.md`, `docs/map_encoding.md` (grepped for timing claims),
> `docs/map_editor_architecture_and_limitations.md`, `docs/map_objects.md`,
> `docs/map_collision_mechanics.md`, `docs/npc_movement_and_waypoints.md`,
> `docs/map_palette_extraction.md`, `docs/rom-extension-wishlist.md`, `.github/rom-map.md`,
> `.github/memory-map.md`, `architecture.md`,
> `in/core/[group] 02_functions/[group] 02_everscript_commands/04_map_manipulation.evs`, and the
> skills `rom-map-data`, `secret-of-evermore-engine`, `wram-memory-mapping`,
> `snes-memory-mapping` (index only — see note in §7), `map-tooling`. Pokémon Red/Blue facts are
> **external, general Game Boy engineering knowledge**, sourced from a live web search (see
> "External sources" at the bottom) — not derived from anything in this repository and not
> independently verified against Pokémon's own disassembly by this pass.

---

## Executive Summary

**Verdict: not a patch — a near-total rearchitecture of the room-loading, tile-addressing, and
compression subsystems, with at least one identified blocker (metatile IDs doubling as live WRAM
byte offsets, §3.7) that is structurally incompatible with holding two rooms' tile dictionaries
in memory at once under the engine's existing zero-lookup rendering design.** This is not a vibe
judgment — three independent, separately-verified facts about this repo's own pipeline compound
against each other: (1) the room-transition sequence is an explicit, synchronous
fade-out → `CHANGE MAP` opcode → full re-decompression → fade-in script pattern with no evidence
anywhere in this repo of incremental or background decompression (§3.1, §3.6); (2) WRAM bank `$7F`
— the destination for the decompressed tile grid and metatile dictionary — is already reported as
"close to its comfortable ceiling" for the single largest vanilla room, let alone two rooms held
simultaneously (§3.3, quoting `docs/map_editor_architecture_and_limitations.md` §4.3 directly);
and (3) a metatile's "ID" is not an abstract index but a literal, room-dimension-dependent byte
offset into WRAM bank `$7F` that the PPU-streaming routine dereferences with zero translation
(§3.7) — so two rooms' metatile ID spaces would collide unless the core streaming routine at
`$909460` is rewritten, not merely re-parameterized. None of the wishlist's five items (map count,
enemy sprites, concurrent sprites, palette slots, SA-1) individually rearchitects the engine's
*addressing model*; continuous-world streaming would have to solve all of the WRAM/VRAM budget
constraints those items already describe as tight **and** additionally break and rebuild the
core tile/collision addressing scheme that touches every one of the 127 room blobs.

---

## 1. What SoE's Current Pipeline Actually Does

### 1.1 How a room is currently loaded and displayed (sub-question 1)

**VERIFIED**, from `docs/map_decompression_trace_analysis.md` §6.3 and
`.github/skills/rom-map-data/SKILL.md` §3 — both derived from live Mesen2 trace logs, cross-checked
against **all 127 vanilla rooms with 0 failures**:

1. The room-load hook at `$908F6A` resolves a 24-bit blob pointer from the Master Map Pointer
   Table (`$9FFDE7 + room_id * 4`) — no bounds check on `room_id`
   (`docs/rom-extension-wishlist.md` §1, already established in a prior pass, reused here).
2. `$908F60..$909050` parses the 13-byte header (origin, width/height, four PPU registers, an
   effect variant) and the step-on/B-trigger tables deterministically, with **zero heuristic
   scanning** — every offset is computed from preceding field lengths
   (`docs/map_decompression_trace_analysis.md` §6.3, "100% Deterministic Empirical Verification").
3. Three compressed payload blocks are decompressed in sequence, each dispatched through the same
   `$8C988D` method-tag dispatcher (`docs/map_decompression_trace_analysis.md` Trace 2):
   - **Block 1** (delta tile palette) → LZSS or raw copy → WRAM `$7FC300`, then a 16-bit
     in-place delta accumulator at `$908E85` converts deltas to absolute CHR tile IDs
     (Trace 1, byte-for-byte verified against a live trace for Room `0x33`).
   - **Block 2** (2D Markov-coded metatile layout grid) → `$8C9BD0` → WRAM `$7F0000`, `W×H` words
     (Trace 3).
   - **Block 3** (3-slice planar metatile dictionary: Layer 1 word, Layer 2 word, collision word
     per metatile) → LZSS → WRAM `$7F0280`, divided by 6 via the SNES hardware multiply/divide
     unit (`$4204..$4206`/`$4214`) to recover the metatile count (§6.1 of the same doc).
4. CHR graphics: for every unique tile ID collected in step 3, `$90934B` calls `$8CC88C`, which
   resolves a 24-bit pointer from a **separate** master table at `$EE0000` (3-byte stride) and DMAs
   a 128-byte 4bpp planar tile into a VRAM character slot
   (`docs/map_tile_graphics_decompression.md` §2, §4). This is a second, independent decompression
   pass with its own format (dual-stream nibble/bit compressor, 16 modes) — VERIFIED, full
   reference Python implementation in that doc round-trips against Mesen2 traces.
5. Palettes: `$90D020` resolves each of up to 8 "tile family" IDs from a **third** master table at
   `$9CC322` (32 bytes/family) and DMAs them into CGRAM via `$8085FA`
   (`docs/map_palette_extraction.md` §1–§3).
6. Section 2 (animated tiles) frame-0 IDs are appended to the same tile list consumed in step 4
   (`docs/map_tile_graphics_decompression.md` §7).
7. Object/entity population: Section 3's object pointer table and object record data are resolved
   with two more deterministic pointer computations (`$909120..$909131`,
   `$90925E..$90926C`) and initialized via `$90A320` into WRAM `$7E107E`/`$7E10CE`
   (`docs/map_objects.md` §3, §5) — this is **map-object** (tile-stamp) state, not the
   actor/NPC entity-slot table.
8. Script (enter/step-on/B-trigger) rebinding: **VERIFIED at the script-authoring level, not
   engine-disassembly level** — `in/core/[group] 02_functions/[group] 02_everscript_commands/
   04_map_manipulation.evs`'s `transition()` function shows the actual sequencing a room change
   goes through from the script side: `fade_out()` → (direction-dependent walk/wait) →
   `load_map()` (emits opcode `0x22`, `CHANGE MAP`) — and separately, `fade_in()` is called from
   the *new* room's own enter script after the engine has already re-populated everything above.
   There is **no code path in any doc reviewed, and none surfaced by grepping this repo for
   "background"/"incremental"/"async" decompression, that decompresses anything before the
   `CHANGE MAP` opcode fires or spreads decompression across multiple frames.** The transition is
   an explicit fade-to-black, full synchronous reload, fade-from-black sequence.
   `// TODO_EVIDENCE_NEEDED: disassemble $908F6A..$909460's actual frame-by-frame execution in
   Mesen2 to confirm this is a single-frame stall vs. spread across several frames during the
   black-screen window — the fade itself is several frames long (opcode 0x27), which could hide
   a multi-frame load. Either way, nothing found suggests it survives the screen staying visible.`

### 1.2 Is the camera/scroll system tied to fixed room dimensions? (sub-question 2)

**VERIFIED that camera bounds are recomputed per room-load from that room's own dimensions, via
script, not hardware-fixed.** From `.github/memory-map.md` (camera fields, all flagged `[SRAM]`
in that doc — see the discrepancy noted below) and
`04_map_manipulation.evs`:

- `_init_map(x_start, y_start, x_end, y_end)` writes
  `MEMORY.CAMERA_BOUNDRY_X_START`/`_X_END`/`_Y_START`/`_Y_END` (WRAM `$23E9`/`$23ED`/`$23EB`/
  `$23EF` per `.github/memory-map.md` lines 379–382). `secret-of-evermore-engine`'s SKILL.md
  documents `init_map(...)` as a "standard task" of the room's own **enter script**, run every
  room load.
- `.github/skills/rom-map-data/SKILL.md` §1 documents the header fields that feed this: `width_tiles`
  (offset `$02`) is stored to `$7E23ED` as `W × 16` (max X), `height_tiles` (offset `$03`) to
  `$7E23EF` as `H × 16` (max Y) — i.e. the camera's own hard bound is derived directly from **the
  currently-loading room's** dimensions, recomputed at every transition.
- A **separate** smooth-pan system exists (`CAMERA_PAN_X`/`_Y`/`_SPEED` at `$242B`/`$242D`/`$242F`,
  driven by `set_camera()` in the same file) — this is a scripted camera *motion* control, not a
  scroll-*boundary* control; it moves the camera within whatever boundary is currently set.
- **UNVERIFIED / NEEDS INVESTIGATION**: whether the PPU BG scroll registers (`$210D`/`$210E` for
  BG1, `$2110`/`$2111` for BG2) are clamped purely in software against these WRAM boundary values
  (which would mean the *hardware* has no fixed-room assumption at all, and only the *software*
  boundary variables would need to be relaxed/removed) or whether some other routine assumes the
  boundary equals exactly one room's `W×16`/`H×16` extent elsewhere (e.g. in the VRAM tilemap wrap
  logic touched by `$909460`, per §1.1 above). No doc in this repo traces this. This is the single
  most important open question for sub-question 2 — see §5.
- **Documentation inconsistency, not resolved here (per `AGENTS.md` §2.1):** `.github/memory-map.md`
  tags `CAMERA_BOUNDRY_X_START` et al. as `[SRAM]` (i.e. persisted to the cartridge save), which
  is surprising for a value that is rewritten by every room's enter script and would not need to
  survive a power cycle. This may be a stale/incorrect tag inherited from that document's
  address-range-based labeling convention rather than a per-field verification. Flagged, not
  silently corrected.

### 1.3 WRAM budget for holding more than one room's data simultaneously (sub-question 3)

**VERIFIED, and this is the most concrete quantitative constraint found.**

- `.github/skills/wram-memory-mapping/SKILL.md` §1 documents SNES WRAM as a flat 128 KB across
  banks `$7E`/`$7F`, with **bank `$7F` (`$7F0000..$7FFFFF`, 64 KB) described as "High WRAM:
  graphical buffers, sound queue buffers, background layers"** — i.e. already described, in this
  repo's own documentation, as dedicated to the currently-loaded room's rendering data, not as a
  general-purpose heap with spare capacity.
- `docs/map_decompression_trace_analysis.md` §3.4 gives the concrete WRAM layout inside bank `$7F`
  for a loaded room: the Layer-1 metatile grid at `$7F0000`, the metatile-dictionary-plus-Markov-
  cache immediately after it at `$7F0280`, a 4096-byte LZSS sliding window at `$7FA000..$7FAFFF`,
  and a 194-byte delta CHR palette buffer at `$7FC300`. These are **fixed, room-independent base
  addresses** — the *next* room's equivalent data would either need a second, disjoint region of
  bank `$7F` (which is a 64 KB bank — there may or may not be room, see below) or reuse of the
  same addresses (which is exactly what makes it non-simultaneous today).
- `docs/map_editor_architecture_and_limitations.md` §4.2–§4.3 directly quantifies the ceiling using
  the game's own **largest vanilla room** (`0x4B`, Antiqua – Oglin Cave, per `.github/rom-map.md`
  row 75: `106×125` tiles, `575` unique metatiles):
  - Metatile dictionary (Block 3): `575 × 6 bytes ≈ 3.45 KB`.
  - Layout grid (Block 2): `106 × 125 × 2 bytes = 26.5 KB`.
  - That doc's own conclusion, quoted directly: *"Room `0x4B` (`106×125 = 13,250` metatiles)
    already pushes the vanilla engine close to its comfortable ceiling"* against an estimated
    ~32–40 KB budget it derives for the grid alone (bank total 64 KB minus dictionary and engine
    scratch).
- **Conclusion for streaming feasibility, stated as reasoning from the above verified numbers, not
  as an independently-measured fact:** holding a *second* room's grid + dictionary simultaneously
  (a hard requirement for any streaming approach, since the area ahead of the player must be ready
  before they cross into it) would, for anything beyond SoE's smallest rooms, **not fit** in the
  remaining bank-`$7F` headroom this repo's own docs describe as already close to exhausted for a
  *single* large room. Small rooms (`0x15` Brian's Test Ground: `24×24`, 2 metatiles;
  `0x33` Strong Heart's Exterior: `20×16`, 197 metatiles) would fit two-at-once comfortably; the
  game's actual largest rooms (`0x4B`, `0x37` Gomi's Tower `56×125`/2131 metatiles per
  `.github/rom-map.md` row 55, `0x59` Quicksand Desert `58×79`/1252 metatiles row 89) would not,
  without either a WRAM reallocation this repo has not scoped or a redesign of what "loaded" means
  (e.g. streaming only a *visible strip* rather than a whole room, which is closer to what
  Pokémon Gen 1 actually does — see §2).
- **NEEDS INVESTIGATION**: exact byte occupancy of the rest of bank `$7F` (the `wram-memory-
  mapping` skill's table gives only a coarse "graphical buffers, sound queue buffers, background
  layers" label for the whole bank, not a byte-by-byte map) — a real feasibility number would need
  a live WRAM heap map of bank `$7F` during gameplay in Mesen2, which this pass did not do (no
  such trace exists in this repo).
- The prior wishlist doc's entity-table finding (`docs/rom-extension-wishlist.md` §3) is relevant
  context but is a **different** memory region (`$7E3DE5..$7E4E88`, bank `$7E`, 30 actor/NPC
  slots) from the tile/collision data discussed here (bank `$7F`) — reused as corroborating
  evidence that this engine's WRAM working set is *already* tight in more than one subsystem, not
  reused as direct evidence about bank `$7F` itself.

### 1.4 How room transitions are triggered and gated (sub-question 4)

**VERIFIED: loading and triggering are two separable layers, but the *scripting model* is built
on the assumption that "room" is the unit of both.**

- Step-on and B-triggers are rectangular bounding boxes (`y_min, x_min, y_max, x_max, script_id`,
  6 bytes) stored **inside each room's own blob** and evaluated only against the coordinates of
  the currently-loaded room, with an `origin_x`/`origin_y` offset from that same room's header
  (`.github/skills/rom-map-data/SKILL.md` §1–§2, `$8FACCE..$8FAD08`). A trigger that fires a room
  change does so by calling `transition()` → `load_map()` → opcode `0x22` `CHANGE MAP`
  (`04_map_manipulation.evs`, confirmed above).
- This means **triggering** (deciding *when* to change rooms) is architecturally separate from
  **loading** (the `$908F6A..$909460` pipeline in §1.1) — a script can call `load_map()` from
  anywhere, and the loading pipeline doesn't know or care why it was invoked. In principle a
  boundary-crossing trigger *could* be replaced by "start streaming" logic without touching the
  trigger-evaluation code itself.
- However: **the same trigger table format is also used for pure gameplay logic that has nothing
  to do with room boundaries** — pits, cutscene starts, dialogue, obstacle checks
  (`.github/skills/secret-of-evermore-engine/SKILL.md` §2.2–§2.3) — and Everscript's own
  `object()`/map-object system (`docs/map_objects.md`) stamps tile-level state changes addressed
  in the **same room-local metatile coordinate space** discussed in §1.3/§3.7. Removing "room" as
  a first-class unit would require re-deriving what a trigger's bounding box, an object's stamp
  position, and a metatile ID *mean* once two rooms' coordinate spaces are merged — this is a data
  format question (§1.7), not merely a control-flow one. **The scripting *control flow* (when to
  transition) is separable from the *loading mechanism*; the *coordinate/addressing model*
  underneath both is not**, per the evidence in §1.7.
- **NEEDS INVESTIGATION**: whether `map_transition`/`CHANGE MAP`-adjacent code performs any
  entity-state teardown (e.g. clearing the 30-slot actor table at `$7E3DE5..$7E4E88`, per
  `docs/rom-extension-wishlist.md` §3) that a streaming design would need to *not* do for entities
  near the shared boundary — not traced in this repo.

### 1.5 VRAM/CGRAM constraints (sub-question 5)

**General SNES hardware fact (external, not SoE-specific): the SNES PPU has 64 KB of VRAM and 512
bytes of CGRAM (256 15-bit colors), fixed in hardware regardless of game or mode.** This is
standard, widely-documented SNES architecture, cited here as hardware fact, not repo research.

Applied to SoE's own documented usage (**this half is SoE-specific and cited**):

- `docs/map_editor_architecture_and_limitations.md` §2.1: Mode 1 gives **8 background palettes ×
  16 colors** (120 usable colors after transparency), and VRAM CHR storage is the "remaining
  ~56 KB (~1,792 unique 8×8 tiles)" after BG1/BG2 tilemap allocation (2–4 KB each).
- Each room is limited to **"up to 7–8 Tile Family IDs"** (§2.2, same doc) — i.e. a room's visible
  graphics are already scoped tightly to what fits that budget; the doc's own worked example
  (§2.3, "mixing water and lava") shows the *animated*-tile DMA budget, not the static CHR budget,
  as the tighter constraint: **"the engine allocates safe bandwidth for 4 to 8 animated tiles per
  room"** out of an SNES V-Blank transfer ceiling of "~6 KB per frame" (both figures asserted
  directly in that doc, not independently re-derived in this pass — see §5 for the open question
  on their own provenance).
- **Reasoning from the above, not independently measured:** any seamless scroll across a room
  boundary requires **both rooms' visible tile graphics resident in VRAM at once** (unlike a
  discrete transition, where the outgoing room's CHR tiles can simply be overwritten once the
  black-screen fade completes). Two rooms' tile families are not obviously going to overlap enough
  to share the existing ~56 KB CHR budget without either (a) restricting streaming to only
  room-pairs that already share tile families vanilla groups this way in places (**UNVERIFIED —
  no doc in this repo establishes whether adjacent vanilla rooms share tile families; this is
  answerable by comparing the Tile Family ID lists two vanilla rooms currently use, via
  `tools/dump_room.py`, but was not done in this pass**), or (b) a genuine VRAM-budget expansion,
  which the wishlist doc's item 4 already treats as potentially "hardware-impossible... without a
  coprocessor" for the *sprite*-palette half of CGRAM (`docs/rom-extension-wishlist.md` §4) — the
  *background* half of the same fixed 512-byte CGRAM budget is under identical hardware pressure
  by the same general fact, even though this repo's docs have not separately quantified BG-palette
  headroom the way they did for sprite palettes.

### 1.6 Compression/decompression cost (sub-question 6)

**NEEDS INVESTIGATION — no cycle-count, frame-count, or wall-clock timing data for the map
decompression pipeline exists anywhere in this repo.** A targeted search (`grep -rn "cycles\|
timing\|frame budget\|V-Blank\|performance"` across `docs/map_encoding.md`,
`docs/map_decompression_trace_analysis.md`, `docs/map_tile_graphics_decompression.md`) found:

- The only quantified timing figure anywhere in the reviewed docs is the general "SNES V-Blank
  interval can only transfer ~6 KB per frame" claim in
  `docs/map_editor_architecture_and_limitations.md` §2.2, which is about the **animated-tile DMA
  queue**, not the Block 1/2/3 decompression routines themselves.
- Nothing in the trace-analysis docs states whether `$8C988D` (LZSS dispatcher), `$8C9BD0`
  (2D Markov decoder), or `$8CC88C`/`$8CC9C0` (CHR tile decompressor) execute within a single
  frame, across several, or how many CPU cycles per byte they cost. The traces in
  `docs/map_decompression_trace_analysis.md` are **correctness** traces (verifying output bytes
  match a reference decoder), not **performance** traces.
- The room-transition sequencing evidence in §1.1/§1.8 (fade-out → `CHANGE MAP` → fade-in, with no
  incremental-decompression code path found) is consistent with — but does not prove — a
  single-shot, non-frame-spread decompression during the black-screen window. Whether that window
  is long enough to hide a multi-frame decompression, or whether the decompression completes
  within one or two frames and the fade duration is purely aesthetic, is unknown from this repo's
  documentation. **`// TODO_EVIDENCE_NEEDED: Mesen2 CPU-cycle-count trace across a full
  `$908F6A`→`$909460` room load, correlated against frame boundaries (NMI/V-Blank markers), for at
  least one small room and one large room (e.g. `0x33` vs. `0x4B`).`**
- Even if decompression turned out to be fast enough to run within a frame budget, that alone does
  not establish it *can* run incrementally/in the background — the algorithms as documented
  (LZSS with a 4096-byte sliding window carried across the whole stream, and the 2D Markov decoder
  whose prediction cache depends on the tile immediately above/left) are **inherently sequential,
  whole-block decoders**: resuming mid-stream across frame boundaries would require checkpointing
  the sliding window and Markov prediction-cache state, which is architecturally possible in
  principle but is not how the pipeline is described anywhere in this repo, and represents
  meaningful new engineering on top of "just call the existing routine a few more times."

### 1.7 The world coordinate system (sub-question 7)

**This is the strongest, most specific structural blocker found in this pass, and it is fully
cited from this repo's own trace analysis.**

- `docs/map_decompression_trace_analysis.md` §6.2 ("Metatile ID as Direct WRAM Bank `$7F` Memory
  Offset") states, and demonstrates with two different rooms' actual numbers, that **a metatile ID
  is not a sequential index — it is a literal byte offset into WRAM bank `$7F`, computed from that
  specific room's own `width_tiles × height_tiles`:**
  $$\text{base\_metatile} = \text{width\_tiles} \times \text{height\_tiles} \times 2$$
  $$\text{Metatile ID}_i = \text{base\_metatile} + (i \times 8)$$
  - Room `0x33` (`20×16`): `base_metatile = 20×16×2 = 0x0280`; metatile IDs run `0x0280, 0x0288,
    0x0290, ...`.
  - Room `0x38` (`83×91`): `base_metatile = 83×91×2 = 0x3B02`; metatile IDs run `0x3B02, 0x3B0A,
    ...`.
  - The PPU tilemap-streaming routine `$909460` dereferences this ID with **zero translation**:
    `LDY $0000,X [$7F0000 + cell_offset]` then `LDA ($26),Y` directly against `$7F0000` — the doc's
    own words: *"This zero-overhead design eliminates table lookup translations entirely during
    active gameplay rendering."*
- **Consequence for streaming, reasoned directly from the above VERIFIED mechanism:** because a
  metatile ID *is* a WRAM address (not an abstract key resolved through a lookup table), **two
  rooms loaded side-by-side would produce colliding, ambiguous metatile ID ranges** unless one of
  them is renumbered into a disjoint offset range — which is exactly the "table lookup translation"
  the engine's own zero-overhead design was built specifically to avoid. Supporting either (a) two
  independent per-room ID spaces stitched together at scroll time, or (b) a single shared global ID
  space across the whole (would-be continuous) world, both require **changing this addressing
  scheme**, not just relocating data. This is a change to the core rendering loop at `$909460`
  itself, not a data-only or WRAM-budget-only problem.
- Separately, and compounding this: `.github/skills/rom-map-data/SKILL.md` §1 documents that
  **trigger and object coordinates are room-local** (`origin_x`/`origin_y` header offset, added to
  player tile position only during that room's own trigger evaluation;
  `docs/npc_movement_and_waypoints.md` §1.1 independently confirms trigger rectangles and object
  stamp positions are "the only coordinates anywhere in a blob," both "addressed to the metatile
  grid"). A continuous world needs one shared coordinate frame; today every room's trigger table,
  object table, and metatile dictionary are self-contained and address only their own local grid.
  Merging rooms means re-deriving **every one of the 127 room blobs'** trigger tables, object
  tables, and metatile dictionaries into a common frame — this is a data-format migration across
  the entire ROM's map content, not an engine patch that leaves existing room data untouched (contrast
  with wishlist item 1, "maps beyond 127," which needs zero changes to any existing room's bytes).

### 1.8 Cross-reference: is this consistent with the transition-sequencing evidence in §1.1?

Yes — `04_map_manipulation.evs`'s `transition()` function (walked through in §1.1) sequences
`fade_out()` then `load_map()` (`CHANGE MAP`) then relies on the *new* room's enter script to call
`fade_in()` once everything above (§1.1 steps 1–7) has completed. There is no script-level or
engine-level evidence anywhere reviewed of two rooms' state coexisting even momentarily during a
normal transition — consistent with, though not proof of, a hard cutover at the WRAM/VRAM level
that matches the addressing-collision problem in §1.7.

---

## 2. What Pokémon Red/Blue Actually Does

> [!NOTE]
> Everything in this section is **general, external, community-documented Game Boy engineering
> knowledge**, gathered via a live web search for this task (see "External sources" below) — it is
> explicitly **not** derived from this repo, not independently verified against Pokémon
> Red/Blue's own disassembly by this pass, and is included only as the comparison point the task
> requested, not as a claim about Secret of Evermore.

- Pokémon Red/Blue's overworld maps declare explicit **connections** to adjacent maps (e.g. Pallet
  Town connects north/south to Route 1/Route 21); the engine can walk this connection graph.
- Map tile data uses **blocksets** — the source described these as sometimes called "metatiles,"
  grouping a game-visible tile out of a 4×4 grid of smaller tiles, reusing a shared library of
  common tile combinations across many maps to fit the Game Boy's tight resource budget (a
  metatile/blockset concept broadly analogous in *purpose*, though not necessarily in binary
  layout, to SoE's own Block 3 metatile dictionary described in §1.7).
- Maps that share the same **tileset** (e.g. the general "overworld" tileset, of which there are
  ~19 named tilesets covering categories like "house," "gym," "forest") are the ones the engine
  can scroll across seamlessly, because the graphics needed for both sides of the boundary are
  already the same shared resource — this is consistent with (though the search results did not
  spell out the precise mechanism for) the well-known Game Boy romhacking community understanding
  that Pokémon's seamless connections work by having the camera scroll continuously while the
  engine streams in new rows/columns of *already-resident-tileset* block data just ahead of the
  viewport, and falls back to a discrete black-screen "warp" transition (not a seamless scroll)
  whenever the destination map uses a **different** tileset. **This specific streaming-vs-warp
  distinction is stated here from general community knowledge of the games, not confirmed by the
  search results returned for this task, and should be treated as slightly less certain than the
  connection/blockset facts directly returned above.**

The core enabling factor, stated as the comparison point: **Pokémon's per-map graphics budget is
scoped at the *tileset* level (shared across many maps) rather than the *individual map* level**,
so two connected maps sharing a tileset already have compatible, already-resident graphics with
no extra VRAM cost to hold both. Whether SoE's own "tile family" system (§1.5) has anything
resembling this shared-scoping property between adjacent rooms is **UNVERIFIED** in this repo (see
§1.5's open question) and is the single most decision-relevant unanswered question for judging how
close SoE's data model is to Pokémon's in spirit.

---

## 3. Gap Analysis

| # | Dimension | SoE today (cited) | Pokémon R/B (general knowledge, external) | Why the gap is hard to close |
|---|---|---|---|---|
| 1 | Transition mechanism | Explicit script-driven fade-out → synchronous `CHANGE MAP` full reload → fade-in (§1.1, §1.8); no incremental/background decompression path found anywhere in this repo | Continuous scroll across same-tileset map connections; discrete warp otherwise (external, §2) | SoE's own loading pipeline was never designed to be interruptible or partial — its three compression algorithms are documented as whole-block decoders (§1.6), and no doc in this repo describes any frame-spread execution |
| 2 | Tile/metatile addressing | Metatile ID **is** a room-dimension-derived WRAM byte offset, dereferenced with zero lookup translation by the PPU streaming routine (§1.7, `docs/map_decompression_trace_analysis.md` §6.2) | Blocksets are a shared library referenced by maps, not stated to double as live addresses (external, less certain) | Two SoE rooms' metatile ID ranges collide unless renumbered — closing this gap means changing the core `$909460` rendering loop's addressing model, not just adding memory |
| 3 | WRAM working-set for tile/collision data | Bank `$7F` (64 KB) already described in this repo as dedicated to *one* room's grid+dictionary+scratch, and already "close to its comfortable ceiling" for the largest vanilla room (§1.3, quoting `docs/map_editor_architecture_and_limitations.md` §4.3 directly) | Not investigated in this pass — Game Boy has its own separate, much smaller (8 KB) WRAM budget and a different graphics model entirely, so no direct byte-for-byte comparison is offered here | Holding two rooms' worth of grid+dictionary simultaneously (a hard requirement for streaming) does not fit in the documented headroom for anything beyond SoE's smallest rooms |
| 4 | VRAM/CGRAM graphics budget | Fixed 64 KB VRAM / 512-byte CGRAM (general SNES hardware fact); SoE rooms already scoped to 7–8 tile families and an animated-tile DMA budget the wishlist doc calls "the real bottleneck" (§1.5, `docs/map_editor_architecture_and_limitations.md` §2.2–§2.3) | Blocksets shared at the tileset level mean many connected maps already share the same resident graphics (external, §2) | UNVERIFIED whether adjacent SoE rooms already share tile families the way Pokémon maps share tilesets — this is the single most decision-relevant open question (§1.5, §5) |
| 5 | Coordinate system | Room-local: trigger/object coordinates relative to a per-room `origin_x/origin_y`; metatile grid is `0..W-1 × 0..H-1` for that room only (§1.7, `.github/skills/rom-map-data/SKILL.md` §1, `docs/npc_movement_and_waypoints.md` §1.1) | Explicit map-to-map connection graph with per-map local coordinates, stitched by the connection data (external) | SoE has no equivalent connection/adjacency data structure documented anywhere in this repo (`docs/npc_movement_and_waypoints.md` §1.3 explicitly rules out any per-room side-table pointing outside a room's own blob) — this would be new data, not a reinterpretation of existing bytes |
| 6 | Camera boundary | Explicitly recomputed per room-load from that room's own `W×16`/`H×16` extent via the enter script's `init_map()` call (§1.2) — software-driven, not obviously hardware-fixed | Camera presumably scrolls freely across connected maps' combined coordinate space (external, not independently confirmed) | The *mechanism* (a WRAM boundary variable) looks relaxable in principle; whether anything else in the engine silently assumes "camera bound == one room" was not traced (§1.2's open question) |

---

## 4. Open Questions

Concrete, Mesen2/disassembly-answerable questions that would need resolving before any real
feasibility number could be given, ordered roughly by how much they'd change the verdict:

1. **Do any two vanilla rooms sharing a border also share tile families?** Compare the Tile Family
   ID lists of adjacent rooms (e.g. via `tools/dump_room.py`) for a few pairs the game treats as
   geographically adjacent. If yes even occasionally, that is the strongest evidence this engine
   has *any* Pokémon-style shared-graphics-budget property to exploit; if no, item 4 in §3 is a
   much harder blocker than stated.
2. **What is the actual cycle/frame cost of `$908F6A`→`$909460`?** A Mesen2 CPU trace with
   frame-boundary markers, for a small room (`0x33`) and the largest room (`0x4B`), would resolve
   §1.6 and establish whether "decompress ahead of time in the background" is even
   computationally plausible before addressing the harder addressing-model problem in §1.7.
3. **Is the SNES BG scroll register write path clamped purely against the WRAM
   `CAMERA_BOUNDRY_*` variables (§1.2), or does anything else (e.g. the VRAM tilemap wraparound
   logic near `$909460`) assume a single-room extent?** Breakpoint on writes to `$210D`/`$210E`/
   `$2110`/`$2111` during normal camera movement near a room's edge and trace what feeds them.
4. **Does the LZSS/Markov decoder state (sliding window position, prediction cache) get reset per
   block-call in a way that would allow a *second, concurrent* decode into a different WRAM region
   without corrupting the first?** This determines whether "decode room A, then room B, into two
   separate buffers" is even mechanically possible with the existing routines, independent of the
   addressing-collision problem in §1.7.
5. **What occupies the rest of WRAM bank `$7F` beyond the documented `$7F0000..$7FC3C1` region
   (§1.3)?** A live Mesen2 WRAM map during gameplay, not just the coarse "graphical buffers, sound
   queue buffers" label this repo currently carries, is needed for a real byte-budget number.
6. **Does anything in the entity/actor system (bank `$7E`, `$7E3DE5..$7E4E88` per
   `docs/rom-extension-wishlist.md` §3) get torn down and rebuilt on every `CHANGE MAP`, and would
   that teardown need to be suppressed for entities near a streamed boundary?** Not traced in this
   repo; relevant to §1.4's "separable but scripting-model-coupled" finding.

---

## 5. Feasibility Tier (Judgment — Not Fact)

**Not assignable as a single number in good conscience, per `AGENTS.md`'s golden rule — but the
qualitative tier is not close to ambiguous either:**

- **This is not a patch in the sense the five `docs/rom-extension-wishlist.md` items are patches.**
  Every wishlist item, even the hardest ones (SA-1 port), is scoped as "extend/relocate an existing
  table" or "change a coprocessor while keeping the same data formats." Seamless streaming, by
  contrast, requires **changing what a metatile ID, a trigger coordinate, and an object stamp
  position *mean*** (§1.7) — a data-format migration touching all 127 room blobs — **in addition
  to** solving WRAM/VRAM budget problems this repo's own docs already describe as tight for a
  single room (§1.3, §1.5).
- **The single hardest, most specifically-cited blocker is §1.7**: the metatile-ID-as-WRAM-offset
  addressing scheme is a *design choice* (explicitly called out in this repo's own trace docs as
  a deliberate "zero-overhead" optimization), not an incidental implementation detail — undoing it
  to support two simultaneous rooms means rewriting the core PPU tilemap-streaming routine
  (`$909460`) that every one of the 127 rooms currently depends on unchanged.
- **If** open question 1 (§4) turned up that adjacent vanilla rooms already share tile families
  the way Pokémon maps share tilesets, that would meaningfully soften the VRAM-budget half of the
  problem (§1.5) — but it would not touch §1.7 at all, since tile-family sharing and metatile-ID
  addressing are independent subsystems (§1.5 is about CHR/palette graphics; §1.7 is about the
  layout grid's own addressing scheme).
- **Judgment**: this sits in the same tier `docs/rom-extension-wishlist.md` §5 reserved for the
  SA-1 port — "categorically different from extend-an-existing-table work" — but for a different
  reason: SA-1 is hard because it's *unscoped* (nothing in this repo addresses it at all).
  Continuous-world streaming is hard because it *is* scoped, by this pass, specifically enough to
  show that it requires rewriting a core rendering-loop optimization the engine's authors clearly
  considered a deliberate, load-bearing design decision, not an oversight. **A phrase that fits the
  evidence, not a vibe: "this is not a patch, this is rewriting the engine's tile-addressing model
  and its core loop's relationship to it."**

---

## 6. Would a RAM-Expansion Coprocessor Chip Change This?

**Question**: could adding a cartridge coprocessor chip with enough RAM to hold every room's
decompressed data solve the problems in §1, the way `docs/rom-extension-wishlist.md` item 5
(SA-1 port) speculated a coprocessor "could independently relax the WRAM-table and DMA-bandwidth
constraints"?

**General SNES hardware fact (external, well-established, not SoE-specific)**: cartridges are not
limited to the console's own memory. Coprocessor chips carry their own cartridge-side RAM, mapped
into extra banks — SA-1's BW-RAM (used by Super Mario RPG, Kirby's Dream Land 3) and Super FX's
private RAM (Star Fox, Yoshi's Island) are real, shipped precedents. A chip carrying a large SRAM
pool could hold every one of the 127 rooms' decompressed data simultaneously as a cartridge-side
cache — that part is unremarkable; cartridges routinely carry more storage than the console itself.

**What that RAM cannot do**: WRAM (128 KB, banks `$7E`/`$7F` — the exact bank §1.3 already
documents as tight for a *single* room) and VRAM (64 KB) and CGRAM (512 B) are not cartridge
resources. They are fixed hardware inside the console's CPU (5A22) and PPU packages, on the
motherboard side of the cartridge slot. No coprocessor chip, regardless of how much RAM it
carries, can enlarge them — this is the same console/cartridge boundary implicit in
`docs/rom-extension-wishlist.md` item 4's finding that the SNES's 8 hardware OBJ CGRAM palettes
may be a hardware ceiling, not a software one.

**Consequence for the §1.7 blocker specifically**: a coprocessor cache would convert the current
"decompress from ROM on every `CHANGE MAP`" cost (§1.6's open question about background/
incremental decompression) into "copy from cartridge cache," which is faster and could plausibly
remove load-screen stutter or let the engine prefetch a few rooms ahead. **It does not touch
§1.7.** The metatile-ID-as-literal-WRAM-offset scheme dereferenced by `$909460` is a property of
the console-side WRAM bank `$7F`, not of wherever the source data came from. Two rooms cannot be
simultaneously "live" in that fixed, deliberately-zero-lookup addressing scheme regardless of
how the source bytes arrived (slow ROM decompression or fast cartridge-RAM copy) — that still
requires the same rewrite of the core streaming routine's addressing model that §5 already
concludes is mandatory.

**Judgment (not fact)**: a RAM-expansion chip meaningfully de-risks §1.6 (decompression latency)
and, separately, is the only avenue `docs/rom-extension-wishlist.md` item 4 identifies for
exceeding the SNES's fixed 8-palette OBJ CGRAM budget. It does not de-risk §1.7, §1.3, or §1.5 —
those are bounded by fixed console-side WRAM/VRAM/CGRAM sizes that no cartridge-side chip can
change, and by the addressing-scheme rewrite required to let more than one room's tile data occupy
that fixed space at once. **A big cartridge RAM chip turns this from "impossible" to "the storage
half is easy, the engine's core addressing model still has to be rewritten regardless."**

---

## External sources

Pokémon Red/Blue facts in §2 are general, external, community-documented Game Boy engineering
knowledge, gathered via a live web search performed for this task:

- [Vjeux — Pokemon Red/Blue Map](https://blog.vjeux.com/2023/project/pokemon-red-blue-map.html)
- [Peter Hajas — Parsing Pokémon Red and Blue Maps](https://www.peterhajas.com/blog/pokemon_rb_map_parsing/)
- [Pokémon Red and Blue/Notes — Data Crystal (TCRF.net)](https://datacrystal.tcrf.net/wiki/Pok%C3%A9mon_Red_and_Blue/Notes)
- [Tileset — Pokémon Red / Blue — The Spriters Resource](https://www.spriters-resource.com/game_boy_gbc/pokemonredblue/asset/63033/)

None of these sources were independently verified against Pokémon Red/Blue's own disassembly by
this pass, and none of them are Secret of Evermore-specific — they are cited here only as the
external comparison point the task requested.
