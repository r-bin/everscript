# NPC & Enemy Movement: Are There Waypoints in the Map Data?

> [!IMPORTANT]
> **Short answer: no.** The room blob contains **no waypoint table, no path nodes, and no
> per-NPC route data of any kind**. Every byte of all 127 room blobs is accounted for by known
> structures, and none of them describe movement.
>
> NPC and enemy movement comes from three places *outside* the map blob:
> 1. **Script walk orders** — bytecode opcodes that hand one entity one destination at a time.
> 2. **Engine AI** — per-entity behaviour driven by the 74-byte character-stat table at `$8EB678`.
> 3. **Spawners** — opcode `0xc2`, which places spawn points, not routes.
>
> There is no node graph, so there is nothing for an enemy to "choose a node" from. What actually
> happens is documented in §3, including the parts that are still unknown.

---

## 1. Proof that the room blob carries no movement data

### 1.1 The blob is fully accounted for

`tools/encode_room.py` models a blob as a complete list of fields and serialises it back:

```
$ python3 tools/encode_room.py --verify
byte-exact round-trip: 127/127 rooms
```

`build_blob(model_from_rom(rom, rid))` reproduces the original bytes for every room. The fields it
needs to do that are the complete contents of a blob:

| Order | Field | Positional data? |
|---|---|---|
| 1 | 13-byte header (origin, dimensions, PPU registers, effect variant) | no |
| 2 | Step-on trigger table (`y1,x1,y2,x2,script_id`, 6 bytes each) | rectangles, 16-px units |
| 3 | B-trigger table (same record format) | rectangles, 16-px units |
| 4 | Tile families (`count:1`, then `count * 2`) | no |
| 5 | CHR descriptors (`count:1`, then `count * 3`) | no |
| 6 | Block 1 — delta tile palette | no |
| 7 | Section 2 — animated tiles | no |
| 8 | Section 3 — object pointer table (`count:1`, then `count * 2`) | no |
| 9 | Block 2 — 2D Markov metatile grid | the map itself |
| 10 | Section 4 — metatile offset initialiser | no |
| 11 | Block 3 — 3-slice planar metatile table (layer 1, layer 2, collision) | the map itself |
| 12 | Object area — object records + metatile stamping blocks | stamp positions, 16-px units |

See [rom-map.md §1](../.github/rom-map.md) for the header and trigger layout and
[map_objects.md](map_objects.md) for the object area. The only coordinates anywhere in a blob are
**trigger rectangles** and **object stamp positions** — both static, both addressed to the metatile
grid, neither attached to an entity.

### 1.2 There is no hidden slack to hide a table in

`--verify` compares a prefix, so "the model round-trips" alone would not rule out extra bytes
*after* the object area. Measuring the real extents rules it out:

- Room blobs live only in the **upper half of each of banks `$9C..$AD`** (verified: every blob
  offset satisfies `offset & 0xFFFF >= 0x8000`).
- Sorted by ROM offset, consecutive blobs inside one bank half are packed with **at most 6 bytes**
  of slack, and usually 0 or 1. Several "gaps" are *negative* — blobs overlap, because vanilla
  shares metatile stamping blocks between object states.
- The apparent ~32 KB gaps are the lower halves of banks, which hold unrelated data and are simply
  skipped by the packer.
- The single largest gap adjacent to a blob is 11 681 bytes after room `0x06` (`0x1CC321`). Its
  content reads as 15-bit BGR colour words, not as coordinate records. It is not identified here
  and is **not** referenced by any room blob field. `// TODO: identify the 0x1CC321..0x1CF0C2 region`

### 1.3 There is no per-room side table either

Two places where a parallel "paths for room N" pointer could hide, both checked against the ROM:

| Candidate | Finding |
|---|---|
| 4th byte of each master map pointer entry (`$9FFDE7 + id*4 + 3`) | `0x00` in all 127 entries. (The non-room entry `0x7F` has `0xCC` — see [rom-map.md §2](../.github/rom-map.md).) |
| Header `word_0f84` (`$09..$0A`) and `padding_0b` (`$0B..$0C`) | `0x0000` in all 127 rooms, both fields. |

Nothing in the per-room data addresses anything outside the blob.

---

## 2. Where movement orders actually come from

### 2.1 Script walk orders (the closest thing to a "waypoint")

The script VM has a family of walk opcodes. Each one gives **one entity one destination**; the
script is the route, and it lives in the bytecode stream in banks `$92..$9C`, not in the map.

| Opcode | Everscript `WALK_TYPE` | Target | Obstacles |
|---|---|---|---|
| `0x6c` | `TILE_ABSOLUTE` | absolute tile x,y (2 bytes) | honoured |
| `0x6e` | `TILE_ABSOLUTE_DIRECT` | absolute tile x,y (2 bytes) | ignored |
| `0x6d` | `TILE_RELATIVE` | relative, via sub-instructions | honoured |
| `0x6f` | `TILE_RELATIVE_DIRECT` | relative, via sub-instructions | ignored |
| `0x9d` | `COORDINATE_ABSOLUTE` | absolute coordinates | honoured |
| `0x73` | `COORDINATE_ABSOLUTE_DIRECT` | absolute coordinates | ignored |
| `0x2e` | `wait(character)` | — | blocks the script until the entity reaches its destination |

Sources: `WALK_TYPE` in
[`in/core/[group] 00_general_enums/[group] 05_everscript/03_sprites.evs:326`](<../in/core/[group] 00_general_enums/[group] 05_everscript/03_sprites.evs#L326>),
the `walk()` / `wait()` wrappers in
[`_shared.evs:60-98`](<../in/core/[group] 02_functions/[group] 02_everscript_commands/[group] 02_character_manipulation/_shared.evs#L60-L98>),
and the opcode handlers in `SoEScriptDumper/list-rooms.cpp:1901-1953`. The two sources agree on
which opcodes ignore barriers; `list-rooms.cpp` states it as *"6d honours barriers, 6f and 73
ignores barriers"*.

> [!NOTE]
> **"Direct" means "ignores barriers", which implies the non-direct variants do *something* to get
> around obstacles.** That routing behaviour is the only place in the engine where anything like
> pathfinding could live. Its algorithm has not been traced.
> `// TODO: trace the non-direct walk handler and document how it routes around collision`

**Coordinate units.** Walk and spawn coordinates in scripts are in **8-pixel units**, not the
16-pixel metatile units the trigger tables use:

- `walk()` converts its `TILE_*` arguments to `COORDINATE_*` with `x << 3` (×8) —
  [`_shared.evs:76`](<../in/core/[group] 02_functions/[group] 02_everscript_commands/[group] 02_character_manipulation/_shared.evs#L76>).
- Cross-check in room `0x38` (South Jungle, 83×91 metatiles = 1328×1456 px): the enter script
  teleports to `(0x46, 0x89)`. At ×8 that is (560, 1096) px — inside the room. At ×16 it would be
  (1120, 2192) px — 736 px past the bottom edge. So ×8 is the only consistent reading.
- The same room's trigger rectangles max out at x=80, y=83 against 83×91 metatiles, confirming
  triggers use 16-px units (`LSR A` ×4 at `$8FACCE..$8FACE4`).

**Runtime destination storage.** `list-rooms.cpp:1917` comments that `0x6e` *"create[s] some object
in `3bc9+*3bc7`, attach[es] to pointer+0x6c"* — i.e. a pool of walk-order structures indexed by a
counter, with the active order linked from entity field `+0x6C`. That field sits in the documented
gap between `ATTACHED_SCRIPT_TRIGGER` (`+0x68`) and `POINTER_STATUS_ICON_SPRITE` (`+0x6e`) in the
`ATTRIBUTE` enum, so it is plausible — but `$3BC7` / `$3BC9` are **not** in
[memory-map.md](../.github/memory-map.md) and this has not been verified here.
`// TODO: verify $3BC7/$3BC9 walk-order pool and entity+0x6C in Mesen2`

### 2.2 Engine AI, per entity

Autonomous movement is a property of the **entity**, configured from its character record — never
from the room. The relevant runtime state, from
[`03_sprites.evs`](<../in/core/[group] 00_general_enums/[group] 05_everscript/03_sprites.evs>):

| Field | Meaning (as labelled in `in/core/`) |
|---|---|
| `ATTRIBUTE.POINTER_BEHAVIOR_CURRENT = 0x00` | 3-byte pointer, purpose marked `?` |
| `ATTRIBUTE.POINTER_BEHAVIOR_BASE = 0x03` | 3-byte pointer, purpose marked `?` |
| `ATTRIBUTE_FLAGS.FLAGS_3 & 0x04` | `AI_FOLLOWING` — "walking to waypoint?" |
| `ATTRIBUTE_FLAGS.FLAGS_3 & 0x01` | `AI_FOLLOWING_REACHED` — "reached waypoint?" |
| `ATTRIBUTE_FLAGS.FLAGS_6 & 0x08` | `AI_RUN` |
| `ATTRIBUTE_BITS.AI_RUN = 0x34` / `AI_WALK = 0x36` | `attribute()` selectors that toggle run/walk |

> [!CAUTION]
> The word "waypoint" in those two comments is a **guess by a previous author**, marked with a
> question mark. The flags track *"an AI destination is active / has been reached"*. They are set
> for the dog following the boy as well. They are **not** evidence of a stored waypoint list, and
> nothing in the ROM has been shown to feed them a list of nodes.

**Character stat table (`$8EB678`, 74 bytes × 142 entries).** This is where per-enemy-type
behaviour parameters live. `SoETilesViewer/characterdata.h` labels two fields that bear directly on
"how an enemy decides to move":

| Offset | `characterdata.h` label | Status |
|---|---|---|
| `+$13` | `aggro_range` — "detection distance in pixels" | third-party label, **unverified in this repo** |
| `+$15` | `aggro_chance` — "probability to engage, out of 256" | third-party label, **unverified in this repo** |
| `+$11`, `+$17` | unknown | unknown |

The record layout itself is solid: `in/core/`'s `ATTRIBUTE_GENERAL` and `characterdata.h` were
derived independently and agree on `+0x19` attack, `+0x1b` defense, `+0x1d` magic defense,
`+0x1f` evasion, `+0x21` hit, `+0x23` XP, `+0x2c` charge max, `+0x32`/`+0x34`/`+0x36` sprite
pointers. `in/core/` simply has no entry for `+0x13`/`+0x15`.

An empirical observation consistent with the aggro labels. Reading all 142 records and resolving
each one's name pointer splits them cleanly in two — **51 records have both fields zero, 91 have at
least one non-zero**, and the split falls exactly along "can this thing fight?":

| Character # | Name | `+$13` | `+$15` | HP |
|---:|---|---|---|---:|
| 0 | `<Boy Name>` | `0x0020` | `0x0064` | 30 |
| 1 | `<Dog Name>` | `0x0020` | `0x00FF` | 36 |
| 2–36 | Boy, Girl, Man, Woman, Old man, Child's Pet, Alchemist, Harry, Fire Eyes, … | `0x0000` | `0x0000` | 1 |
| 45 | Tiny | `0x0037` | `0x0032` | 150 |
| 51 | Bad Dawg | `0x0020` | `0x00FF` | 120 |
| 52 | Skullclaw | `0x0050` | `0x0032` | 200 |
| 53 | Will o' the Wisp | `0x0037` | `0x0032` | 40 |

Every all-zero record is a 1 HP talk-only town NPC. Every combat-capable record — including the
Boy and the Dog, whose companion AI does seek out and attack nearby enemies — has non-zero values.
Non-zero values are round decimals (0x20, 0x32, 0x37, 0x50, 0x64, 0xFF …), which reads like
hand-tuned designer parameters. Strongly suggestive, **not proof**: nothing here shows the engine
reading these fields.
`// TODO: confirm +$13/+$15 by breakpointing the AI chase decision`

### 2.3 Spawners

`add_enemy_spawner(enemy, x, y, quantity)` emits opcode `0xc2` with `(npc_id, x, y)` and optionally
presets `$2433` (`MEMORY.ENEMY_SPAWNER_QUANTITY`) first —
[`03_sprite.evs:174`](<../in/core/[group] 02_functions/[group] 02_everscript_commands/03_sprite.evs#L174>).
`list-rooms.cpp:2700` describes `0xc2` as *"adds npc to conditional spawn list"*.

A spawner is a **spawn point**, not a route: one position, no destination. Across the whole script
dump, `WRITE $2433 = N` is followed by `0xc2` 553 times and by the plain NPC load `0x3c` 129 times;
the values are small (`0x0001`–`0x000a`, with `0x0001` alone accounting for 429 of 687 writes).
What `$2433` means for the 129 `0x3c` cases is unresolved — room docs variously guess "spawner
group ID" ([0x5b-east-jungle.md](rooms/act1/0x5b-east-jungle.md)) and "patrol/behavior variant"
([0x41-north-jungle.md](rooms/act1/0x41-north-jungle.md)). `// MISMATCH: docs disagree on $2433`
`// TODO: trace the 0x3c handler to see whether it reads $2433 at all`

### 2.4 What a "patrol" looks like in practice

The Minitaur in Halls SE (`0x2c`) is the clearest vanilla example of a boss that walks around, and
it is a **plain script loop with a random delay** — dump at `script_all:32178-32202`:

```
[0x979d30] (3c) Load NPC 0070>>1 flags/state 0010 at pos 16 20
[0x979d3b] (3f) WRITE $2835+x68=0x300, $2835+x66=0x198c (set script)
[0x979d43] (a6) RCALL -396 (to 0x979bb7)
  [0x979bb7] (09) IF $2835 == FALSE THEN SKIP 106      ; dead -> stop
  [0x979bbd] (09) IF (signed arg0 >= 0x03ff) == FALSE THEN SKIP 80
  [0x979bc7] (75) MAKE $2835 FACE SOUTH
  [0x979bcb] (78) <untraced> for $2835, 0x8000 4         ; stomp
  ...
  [0x979c14] (1a) WRITE SCRIPT arg0 = 0
  [0x979c17] (1a) WRITE SCRIPT arg0 = (signed arg0 + 1) + (RAND & 1)
  [0x979c24] (3a) YIELD
  [0x979c25] (05) SKIP -110 (to 0x979bb7)
```

The script owns a counter, advances it by `1 + (RAND & 1)` each frame, and fires the stomp when it
crosses `0x03FF`. Movement between stomps is left to the engine AI (§2.2), which homes on the
player. No node list, no route, no destination table — an RNG-driven timer plus chase behaviour.
[`docs/rooms/act2/0x2c-halls-se.md`](rooms/act2/0x2c-halls-se.md) describes the same loop as
"wanders toward player with random delay".

Town NPCs are set up the same way: loaded with `0x3c`/`0xba`, given a talk script with `0x3d`
(`entity+0x66` = script id, `entity+0x68` = trigger mask), and otherwise left to the engine. See the
Fire Eyes village block at `script_all:1189-1220`.

---

## 3. So how *does* an enemy choose where to walk?

Stated as precisely as the current evidence allows:

**Established:**
- Not from map data. Nothing in the room blob describes entity movement (§1).
- A script can push one absolute or relative destination onto an entity at a time, with a flag for
  whether barriers are honoured, and can block until arrival (§2.1).
- Behaviour parameters are per **character type**, read from `$8EB678 + id * 74`, and are identical
  in every room that spawns that type (§2.2).
- Two fields of that record, `+$13` and `+$15`, are zero for exactly the 51 talk-only 1 HP town
  NPCs and non-zero for all 91 combat-capable characters, the Boy and Dog included.

**Hypothesis, consistent with the evidence but unverified:** an enemy with no active script walk
order runs its engine behaviour routine, which decides whether to home on the player using the
`+$13` / `+$15` fields (distance test, then a probability roll), and otherwise idles or drifts. The
`AI_FOLLOWING` / `AI_FOLLOWING_REACHED` flags then track the single active destination.

**Not established, and not to be written down as fact until traced in Mesen2:**
- What the idle/non-aggro movement actually is (random walk? fixed drift? standing still?).
- How the non-direct walk opcodes route around collision.
- What `POINTER_BEHAVIOR_CURRENT` / `POINTER_BEHAVIOR_BASE` point at, and whether those targets
  are per-type AI routines or something else.
- Whether `$2433` influences NPCs loaded with `0x3c`.
- The meaning of the `0x3c` flags/state word beyond the documented `FLAG_ENEMY` bits. Observed
  distribution: `0x0020` (423×), `0x0002` (276×), `0x8400` (113×), `0x0400` (24×), `0x0010` (21×).
  `FLAG_ENEMY` documents `0x0020 = INACTIVE`, `0x0002 = INVINCIBLE`, `0x0400 = PHASING`; bits
  `0x8000` and `0x1000` (in `0x9000`) are undocumented.
  [`0x44-greenhouse.md`](rooms/act4/0x44-greenhouse.md) guesses that `0x8400` "may give them their
  wandering behaviour pattern" — a guess, not a finding.

---

## 4. Verifying any of this in Mesen2

The open questions above are all reachable with breakpoints. Suggested order:

1. **Does anything read the blob after the object area?** Set a read breakpoint on the bytes right
   past `_object_area_end(rom, L)` for a room with roaming enemies (e.g. `0x5b` East Jungle) and
   walk around. Expect no hits — that is the direct confirmation of §1.
2. **Entity AI destination.** Break on writes to `entity + 0x12` (`FLAGS_3`) for a spawned enemy and
   look at what set `AI_FOLLOWING`; the caller is the AI routine.
3. **Aggro fields.** Break on reads of `$8EB678 + id*74 + 0x13` and `+ 0x15` while an enemy notices
   the player. A hit at the moment of aggro confirms the `characterdata.h` labels.
4. **Walk-order pool.** Break on writes to `$7E3BC7` and the region at `$7E3BC9` while a cutscene
   issues a `0x6e`, then on reads of `entity + 0x6C`.
5. **`$2433`.** Break on reads of `$7E2433` and see whether the `0x3c` handler touches it.

See [mesen2-debugging-re](../.github/skills/mesen2-debugging-re/SKILL.md) for the workflow.

---

## 5. Cross-document notes

> [!WARNING]
> `// MISMATCH: entity table location.`
> [secret-of-evermore-engine](../.github/skills/secret-of-evermore-engine/SKILL.md) §3 says the
> engine keeps entity slots in `$7E1000..$7E1FFF`, while
> [`03_sprites.evs:815`](<../in/core/[group] 00_general_enums/[group] 05_everscript/03_sprites.evs#L815>)
> says `$7E3DE5..$7E4E88`, 0x8E bytes per entity, and lists concrete slot addresses
> (`ENTITY_1 = 0x3de5`, `ENTITY_2 = 0x3e73`, … stride `0x8E`). The `in/core/` addresses are the ones
> the compiler actually emits and are consistent with the `0x8E` stride, so they are the ones used
> throughout this document. The skill's range is unexplained and should be re-checked before anyone
> relies on it.

**Related documents**

| Question | Document |
|---|---|
| What *is* in a room blob, byte by byte? | [rom-map.md](../.github/rom-map.md), [map_encoding.md](map_encoding.md) |
| How do map objects (gourds, doors, bridges) work? | [map_objects.md](map_objects.md) |
| What does a collision word mean? | [map_collision_mechanics.md](map_collision_mechanics.md) |
| Which bits gate entity movement through terrain? | [map_collision_mechanics.md](map_collision_mechanics.md) |
| How are enemies spawned from scripts? | [`03_sprite.evs`](<../in/core/[group] 02_functions/[group] 02_everscript_commands/03_sprite.evs>) |
