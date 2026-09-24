# Dog Sniff Spot Mechanics in Secret of Evermore

What the Dog can and can't sniff, and where that's decided in the data.

> **Status:** the authoring-level mechanism below (how a sniff spot is built and how it differs
> from a gourd/chest) is confirmed directly from the compiler source and cross-checked against a
> dumped vanilla room. What is **not** confirmed is the native engine routine that decides, frame
> to frame, when the Dog's nose animation plays — that would need a Mesen2 trace. See
> [§4 What's not verified](#4-whats-not-verified) — do not present that part as fact, per
> `AGENTS.md` §1.

---

## 1. The answer

**Only tagged objects.** The Dog does not react to "any object" or "any B-trigger" — a tile is
sniffable only if it was authored as a distinct **sniff spot**: a 1×1 Section 3 map object paired
with a B-trigger whose script calls the shared `loot()` helper with the *kneel-and-dig* animation
variant, ROM call ID `ADDRESS_ID.LOOT_SNIFF = 0x39` (`in/core/[group] 00_general_enums/01_rom.evs:151`).

Everything else that looks superficially similar — gourds, chests — is a **different**, explicitly
separate authored type. They call `loot_chest()`, which uses `ADDRESS_ID.LOOT_GOURD = 0x3a`
(`01_rom.evs:152`) instead, and never plays the Dog's kneel/dig animation.

So: it's a closed set of specifically-built objects, not a generic property every object has.

---

## 2. Where the tag lives

### 2.1 Authoring surface (`.evs`)

Two high-level Everscript functions wrap the same underlying `loot()` shared routine
(`in/core/[group] 02_functions/[group] 04_complex/09.evs:24`), distinguished by one boolean at the
compiler level — `compiler/ast_everscript.py:1907` (`class Loot`):

```python
def __init__(self, generator, with_kneel_animation: bool, object, reward, amount, next):
    if with_kneel_animation:
        self.animation = Word(0x39, 1)   # ADDRESS_ID.LOOT_SNIFF — dig animation
    else:
        self.animation = Word(0x3a, 1)   # ADDRESS_ID.LOOT_GOURD — chest-open animation
```

Parser wiring (`compiler/parser.py:83-84`):

```python
"_loot":       lambda p: Loot(self.generator, True,  p[2][0], p[2][1], p[2][2], p[2][3]),  # sniff spot
"_loot_chest": lambda p: Loot(self.generator, False, p[2][0], p[2][1], ...),                # gourd/chest
```

`loot(...)` in `.evs` source *is* the sniff-spot authoring call; `loot_chest(...)` is the gourd/chest
one. Also note the `SNIFF_SPOT_MEMORY_TYPE` system switch (`ast_everscript.py:1933`) that decides
whether a sniff spot's persistence flag is allocated in RAM or SRAM — another sign sniff spots are
handled as their own category by the compiler, not a generic object flag.

### 2.2 Map-data surface (ROM)

Per `docs/map_objects.md` §7.3, a sniff spot is a Section 3 map object with `max_state = 1`
(state 0 = hidden, state 1 = dug up), and its coordinates match its own dedicated B-trigger — same
shape as a gourd, but a different object *purpose* driven entirely by which loot animation its
B-trigger script calls.

Confirmed on Room `0x38` (South Jungle) via `docs/rooms/act1/0x38-south-jungle-start.md`:

| Objects | Type | B-trigger dispatch |
|---|---|---|
| `0x02`–`0x05` | gourd 🫙 | "Global 0x3a" — `loot_chest()` |
| `0x07`–`0x1e` (24 objects) | sniff spot 👃 | "Global 0x39" — `loot()` |

Every single sniff-spot B-trigger in that room calls Global `0x39`; every gourd B-trigger calls
Global `0x3a`. No B-trigger in the room calls one animation for an object tagged as the other type.

### 2.3 Persistence surface (SRAM)

Sniff spots get their own contiguous per-room bit ranges in `$2258..$23FF`, disjoint from gourd
flags — `docs/patterns.md` "Sniff Flag Organization": **193 unique sniff bits** catalogued in Act 1
alone, no bit reused across rooms. `docs/rooms/act1/0x38-south-jungle-start.md` lists each of the 24
sniff spots against its own flag byte/bit (e.g. `$2290 bit 0x40` → Ash, `$228f bit 0x20` → Roots).

### 2.4 Documentation convention

The project's own classification taxonomy (`.github/skills/data-classification-emojis/SKILL.md`
§2.3) treats sniff spots as a distinct tagged category with a dedicated emoji (`👃`), separate from
gourds (`🫙`) — reinforcing that this has always been modeled as a closed, explicitly-marked set of
objects, not an emergent property.

---

## 3. What the Dog does *not* sniff

- **Gourds/chests** — different animation (`LOOT_GOURD`/`0x3a`), no kneel/dig.
- **Doors, hatches, bridges, switches, destructible walls, boss segments** — none of these ever
  call the `0x39` animation; they're driven by `set_object_state()`-style calls
  (`docs/map_objects.md` §6, opcode `0x5C`), not `loot()`.
- **Cuttable grass** — a completely unrelated mechanism (a metatile swap table, see
  `docs/cuttable_grass_mechanics.md`); no B-trigger or loot call is involved at all.
- **Arbitrary NPCs/enemies** — those are dynamic actor entities (entity slots `$7E1000..$7E1FFF`),
  not Section 3 map objects, and outside the loot/object system entirely.

---

## 4. What's not verified

- **The Dog AI's actual detection routine.** Nothing here has been traced to confirm *how* the
  engine decides, per-frame, to animate the Dog's nose near a sniff spot — e.g. whether it scans a
  per-room list of sniff-tagged B-trigger coordinates specifically, or whether it's driven by some
  other flag on the Section 3 object record itself. The `.evs`/compiler evidence above proves sniff
  spots are authored as a distinct, tagged type; it does not by itself prove what native code reads
  at runtime to trigger the nose animation. That needs a Mesen2 trace (breakpoint on the animation
  call, or on writes to the Dog's animation-state byte, while walking near a known sniff coordinate
  like Room `0x38` object `0x07`).
- **OBJ `0x0006` in Room `0x38`** is a loose end: it has a persistence flag and an `UNLOAD OBJ`
  call in the enter script, but no B-trigger was found for it, so its type (sniff spot or
  otherwise) is unconfirmed (`docs/rooms/act1/0x38-south-jungle-start.md` line 68/133).
- **Sniff spots `0x0009`/`0x000e`** write an extra `LOOT_AMOUNT` before the loot call, unlike every
  other sniff spot in the room — the bonus item this grants is unconfirmed
  (`vanilla_bugs_and_oddities.md` line 15 also documents a "broken sniff spot" case, B-trigger
  #19/Object #1, elsewhere).
