# 0x59 — Prehistoria: Quick Sand Desert

**ROM address:** `0x9fff4b`  
**Data address:** `0xa08000`  
**Enter script:** `0x9281d8` → `0x93acb7`  
**Act:** 1 — Prehistoria

---

## Statistics

| Metric | Count |
|--------|-------|
| Step-on zones | 65 total (7 exits + ~58 sand whirl zones) |
| B-trigger zones | 28 (21 unique sniff spots incl. 1 dual-zone, + 8 gourds) |
| Gourds | 8 |
| Sniff spots | 20 unique |
| Static Enemies | 8× SKELESNAIL |
| Enemy spawners | 6 (NPC `0x0f` unknown species) + 1 PLACEHOLDER |
| Music | `0x6c` (desert/quicksand theme) |

---

## Connections

| Direction | Zone | Destination | Notes |
|-----------|------|-------------|-------|
| West (step-on) | `[10,19:12,1b]` | `0x5b` East jungle @ `0x01a8` | Global script `0x19` |
| West (step-on) | `[10,14:12,18]` | `0x5b` East jungle @ `0x0118` | Global script `0x1a` |
| West (step-on) | `[10,0e:12,10]` | `0x5b` East jungle @ `0x0088` | Clears `$22eb` bit `0x10`; global script `0x19` |
| North (step-on) | `[30,12:32,13]` | `0x35` Quicksand/Bugmuck caves @ `0x0148` | Writes `$234d=1`, `$234e=1`; global script `0x26` |
| South (step-on) | `[27,52:2c,54]` | `0x67` Bugmuck exterior @ `0x0058` | Global script `0x21` |
| South (step-on) | `[2c,53:36,54]` | `0x67` Bugmuck exterior @ `0x00d8` | Clears `$22eb` bit `0x10`; global script `0x21` |
| East (step-on) | `[48,14:4a,18]` | `0x5a` Acid rain guy @ `0x00b0` | Global script `0x1d` |
| Scripted outro | (enter guard) | `0x69` Volcano path @ `0x04c8` | Triggered if `$22f1&0x40` already set; sand whirl cutscene |

---

## Sand Whirl System

The desert contains ~15 sand whirls scattered across the map. Each whirl uses a two-step-on system:

1. **Outer trigger zone** — player steps in; sets a state flag (`$2834`/`$2835`/`$2836`/`$2837`/`$2838` bit), writes whirl ID to destination register pair (`$285f`/`$2861`/etc.), opens the whirl object, closes it if the "suck" flag is clear.
2. **Center zone** — polls player position + timer every frame; if player stays >25 ticks, scripts the player facing south, animates the whirl object (state 2→1→0→`0x8000`), writes `$242f=0x0030`, loads `$287b = <whirl destination register>`, then calls:
   - `0x93a59a` **Sand whirl script part [1]** — executes the warp
   - `0x93a524` **Sand whirl script part [2]** — follow-up

The whirl destinations are dispatched inside the subroutines via the value in `$287b`, which contains the whirl's destination ID (a small integer written to a `$285X`/`$286X` register pair). Full destination mapping requires analysis of `0x93a59a`.

### Sand Whirl Destination Registers

| Register | Typical value set | Object var | Named in dump |
|----------|------------------|------------|---------------|
| `$285f` | `0x0000` | `$247b` | whirl 1 / cave / 11th / last-center |
| `$2861` | — | `$247d` | whirl 2 |
| `$2863` | — | `$247f` | whirl 3 |
| `$2865` | — | `$2481` | whirl 4 / 14th |
| `$2867` | — | `$2483` | whirl 5 / 15th |
| `$2869` | — | `$2485` | whirl 6 |
| `$286b` | — | `$2487` | (unnamed) |
| `$286d` | — | `$2489` | whirl related |
| `$286f` | `0x0003` | `$248b` | 3rd / 13th |
| `$2871` | `0x000a` | `$248d` | below-far-right |
| `$2873` | — | `$248f` | whirl related |

**`// TODO: fully map sand whirl destination IDs → destination rooms/coords`**

### Sand Whirl Activation Flags

| Register | Bit | Whirl role |
|----------|-----|-----------|
| `$2834` | `0x10` | Whirl 13 open/active |
| `$2834` | `0x40` | Whirl 3 open/active |
| `$2835` | `0x04` | Whirl 11 / cave / last-center open/active |
| `$2835` | `0x10` | Whirl 13 alt trigger |
| `$2835` | `0x20` | Whirl 14 open/active |
| `$2836` | `0x08` | Whirl 5 / 15 open/active |
| `$2836` | `0x20` | below-far-right whirl open/active |
| `$2836` | `0x80` | Whirl 1 / cave / 11 open/active |
| `$2837` | `0x01` | Suck flag for whirl 2 / 11 |
| `$2837` | `0x02` | Suck flag for whirl 2 alt |
| `$2837` | `0x04` | Suck flag for whirl 4/14 |
| `$2837` | `0x08` | Suck flag for whirl 5/15 |
| `$2837` | `0x10` | Suck flag for whirl 6 |
| `$2837` | `0x40` | Suck flag for whirl 7 |
| `$2837` | `0x80` | Suck flag for whirl 1/11 |
| `$2838` | `0x01` | Close flag for below-far-right |
| `$2838` | `0x02` | Suck flag for whirl near (26,25) |

---

## Memory Access

| Address | Bits | Category | R/W | Meaning |
|---------|------|----------|-----|---------|
| `$22f1` | `0x40` | 📖 | R | Inside outro? — triggers volcano path cutscene on enter |
| `$22eb` | `0x20` | ⚙️ | R/W | In animation — cleared on enter if set |
| `$22eb` | `0x10` | ⚙️ | W | Cleared on specific west/south exits |
| `$226c` | `0x01` | 🫙 | R/W | Gourd obj0 (Petal) looted |
| `$226c` | `0x02` | 🫙 | R/W | Gourd obj1 (Wax) looted |
| `$226c` | `0x04` | 🫙 | R/W | Gourd obj2 (Crystal) looted |
| `$226c` | `0x08` | 🫙 | R/W | Gourd obj0x27 (Clay) looted |
| `$226c` | `0x10` | 🫙 | R/W | Gourd obj0x28 (Biscuit) looted |
| `$226c` | `0x20` | 🫙 | R/W | Gourd obj0x29 (Clay) looted |
| `$226c` | `0x40` | 🫙 | R/W | Gourd obj0x2a (Water) looted |
| `$2296` | `0x08` | 👃 | R/W | Sniff Ash #23 collected |
| `$2296` | `0x10` | 👃 | R/W | Sniff Ash #24 collected |
| `$2296` | `0x20` | 👃 | R/W | Sniff Ash #25 collected |
| `$2296` | `0x40` | 👃 | R/W | Sniff Ash #26 collected |
| `$2296` | `0x80` | 👃 | R/W | Sniff Ash #27 collected |
| `$2297` | `0x01` | 👃 | R/W | Sniff Ash #28 collected |
| `$2297` | `0x02` | 👃 | R/W | Sniff Ash #29 collected |
| `$2297` | `0x04` | 👃 | R/W | Sniff Wax #22 collected |
| `$2297` | `0x08` | 👃 | R/W | Sniff Wax #45 collected |
| `$2297` | `0x10` | 👃 | R/W | Sniff Wax #46 collected |
| `$2297` | `0x20` | 👃 | R/W | Sniff Wax #44 collected |
| `$2297` | `0x40` | 👃 | R/W | Sniff Roots #30 collected |
| `$2297` | `0x80` | 👃 | R/W | Sniff Roots #31 collected |
| `$2298` | `0x01` | 👃 | R/W | Sniff Roots #32 collected |
| `$2298` | `0x02` | 👃 | R/W | Sniff Roots #33 collected |
| `$2298` | `0x04` | 👃 | R/W | Sniff Roots #34 collected |
| `$2298` | `0x08` | 👃 | R/W | Sniff Clay #35 collected |
| `$2298` | `0x10` | 👃 | R/W | Sniff Clay #36 collected |
| `$2298` | `0x20` | 👃 | R/W | Sniff Clay #37 collected |
| `$2298` | `0x40` | ⚙️ | R/W | Unloads obj 0x2b — purpose unclear `// TODO` |
| `$2298` | `0x80` | 👃 | R/W | Sniff Clay #38 collected |
| `$2834`–`$2838` | various | ⚙️ | R/W | Sand whirl open/active/suck flags (see table above) |
| `$2391` | — | ⚙️ | W | PRIZE (sniff/gourd content) |
| `$2395` | — | ⚙️ | W | MAP REF? (object index) |
| `$2461` | — | ⚙️ | W | NEXT ADD (gourd respawn delta) |
| `$238d` | — | 🎵 | R | CHANGE MUSIC flag |
| `$234d` | — | ⚙️ | W | Written `0x0001` before cave entrance |
| `$234e` | — | ⚙️ | W | Written `0x0001` before cave entrance |
| `$22ea` | `0x01` | ⚙️ | R | Collected flag (engine result) |
| `$2429` | — | ⚙️ | R | Controlled char position (used by sand whirl poll) |
| `$242f` | — | 🎥 | W | Written `0x0030` during sand whirl suck-in |
| `$2433` | — | ⚙️ | W | Spawner group ID |
| `$287b` | — | ⚙️ | W | Active sand whirl destination register pointer |
| `$287d` | — | ⚙️ | W | PLACEHOLDER entity reference |
| `$23a1`–`$23a9` | — | ⚙️ | W | Enemy drop table (same as 0x5b: rates 10/2/1, drops `0x0800`/`0x0001`×7/`0x0200`) |
| `$23c1` | — | ⚙️ | W | Written `0x0001` on enter |
| `$23c5` | — | ⚙️ | W | Written `0x0280` on enter |
| `$23bf` | — | ⚙️ | W | Written `0x0000` on enter |
| `$0ea2` | — | ⚙️ | W | Unknown engine register |
| `$0eac` | — | ⚙️ | W | Unknown engine register = `0x172b` |

---

## Objects

### Gourds

| Obj | Persistence | Zone | Content | Notes |
|-----|-------------|------|---------|-------|
| 0 | `$226c` bit `0x01` | `[11,1b:13,1d]` | Petal | MapRef `0x0000` |
| 1 | `$226c` bit `0x02` | `[36,0f:38,11]` | Wax | MapRef `0x0001`; NEXT_ADD=3 |
| 2 | `$226c` bit `0x04` | `[25,49:27,4b]` | Crystal | MapRef `0x0002`; NEXT_ADD=3 |
| 0x27 (39) | `$226c` bit `0x08` | `[41,10:43,11]` | Clay | MapRef `0x0027` |
| 0x28 (40) | `$226c` bit `0x10` | `[43,11:45,12]` | Biscuit | MapRef `0x0028` |
| 0x29 (41) | `$226c` bit `0x20` | `[3f,13:41,15]` | Clay | MapRef `0x0029` |
| 0x2a (42) | `$226c` bit `0x40` | `[44,13:46,14]` | Water | MapRef `0x002a` |

### Sniff Spots

| Obj | Persistence | Zone(s) | Content | MapRef |
|-----|-------------|---------|---------|--------|
| 22 | `$2297` bit `0x04` | `[1d,42:1e,43]` + `[3e,0f:3f,10]` | Wax | `0x0016` (dual-zone) |
| 23 | `$2296` bit `0x08` | `[38,0d:39,0e]` | Ash | `0x0017` |
| 24 | `$2296` bit `0x10` | `[31,20:32,21]` | Ash | `0x0018` |
| 25 | `$2296` bit `0x20` | `[21,2f:22,30]` | Ash | `0x0019` |
| 26 | `$2296` bit `0x40` | `[33,2e:34,2f]` | Ash | `0x001a` |
| 27 | `$2296` bit `0x80` | `[14,38:15,39]` | Ash | `0x001b` |
| 28 | `$2297` bit `0x01` | `[2b,38:2c,39]` | Ash | `0x001c` |
| 29 | `$2297` bit `0x02` | `[33,4f:34,50]` | Ash | `0x001d` |
| 30 | `$2297` bit `0x40` | `[1f,1c:20,1d]` | Roots | `0x001e` |
| 31 | `$2297` bit `0x80` | `[2a,2c:2b,2d]` | Roots | `0x001f` |
| 32 | `$2298` bit `0x01` | `[28,34:29,35]` | Roots | `0x0020` |
| 33 | `$2298` bit `0x02` | `[1d,3c:1e,3d]` | Roots | `0x0021` |
| 34 | `$2298` bit `0x04` | `[2e,36:2f,37]` | Roots | `0x0022` |
| 35 | `$2298` bit `0x08` | `[20,0d:21,0e]` | Clay | `0x0023` |
| 36 | `$2298` bit `0x10` | `[18,30:19,31]` | Clay | `0x0024` |
| 37 | `$2298` bit `0x20` | `[36,30:37,31]` | Clay | `0x0025` |
| 38 | `$2298` bit `0x80` | `[30,43:31,44]` | Clay | `0x0026` |
| 44 | `$2297` bit `0x20` | `[22,38:23,39]` | Wax | `0x002c` |
| 45 | `$2297` bit `0x08` | `[33,3e:34,3f]` | Wax | `0x002d` |
| 46 | `$2297` bit `0x10` | `[35,1c:36,1d]` | Wax | `0x002e` |

---

## NPCs / Enemies

| Sprite ID | Name | Count | Type | Notes |
|-----------|------|-------|------|-------|
| `0x26` (SKELESNAIL) | Skelesnail | 8 | Static | At: `(19,2d)`, `(29,55)`, `(0d,63)`, `(1b,71)`, `(3f,8b)`, `(37,15)`, `(3f,67)`, `(3f,35)` |
| `0x0f` (unknown) | Unknown | 6 | Spawner | Groups 3/4/5/6 at `(0f,13)`, `(07,43)`, `(0f,99)`, `(51,97)`, `(53,4f)`, `(51,11)`; flags `0x0400` |
| `0x20` (PLACEHOLDER) | Placeholder | 1 | Static | At `(41,28)`; flags `0x0020`; ref saved to `$287d` |

**`// TODO: identify NPC sprite 0x0f (loaded in quicksand desert as enemy spawner)`**

---

## Enemy Drop Table

Same as room `0x5b`:

| Slot | Rate | Item | Qty |
|------|------|------|-----|
| 1 | `0x0a` | `0x0800` (PETAL) | 1 |
| 2 | `0x02` | `0x0001` qty=7 | 7 |
| 3 | `0x01` | `0x0200` | 1 |

---

## External Scripts

| Opcode | Callee | Purpose |
|--------|--------|---------|
| `0x00` | `"Fade-out / stop music"` | Standard enter fade-out |
| `0x01` | `"Fade-in / start music"` | Standard enter fade-in |
| `0x19` | `"Prepare room change? West exit/east entrance outdoor-outdoor?"` | West exits |
| `0x1a` | `"Unnamed Global script 0x1a"` | Middle west exit |
| `0x1d` | `"Prepare room change? East exit/west entrance outdoor-outdoor?"` | East exit |
| `0x21` | `"Prepare room change? South exit/north entrance outdoor-outdoor?"` | South exits |
| `0x26` | `"Prepare room change? North exit/south entrance outdoor-indoor?"` | Cave entrance |
| `0x39` | `"Loot nature?"` | All sniff spot B-triggers |
| `0x3a` | `"Loot gourd?"` | All gourd B-triggers |
| `0x92de75` | `"Some cinematic script (used multiple times)"` | End of enter sequence |
| `0x93a524` | `"Sand whirl script part [2]"` | Sand whirl post-warp follow-up |
| `0x93a59a` | `"Sand whirl script part [1]"` | Sand whirl warp dispatch (reads `$287b` for destination) |
| `0x92d5bd` | `"Unnamed ABS script 0x92d5bd"` | Used in outro NPC spawn animation |
| `0x92d607` | `"Unnamed ABS script 0x92d607"` | Outro cutscene between NPC despawns |
| `0x92d915` | `"Unnamed ABS script 0x92d915"` | Outro: hides status bar layer |

---

## Enter Script Summary

1. **In-animation branch:** if `$22eb&0x20` — clear flag; else teleport both to `(09,25)` and fade out.
2. **Outro guard:** if `$22f1&0x40` (already in outro sequence) — set the flag again, call cinematic script, spawn 3× NPC `0x4c>>1` (NPC 0x26 = SKELESNAIL) at `(19,2d)`, `(1d,38)`, `(29,55)` for cutscene, walk them east one by one with dust effects, fade screen, CHANGE MAP → `0x69` Volcano path.
3. Set engine registers, enemy drops.
4. Unload previously-collected sniff spots (20 bits: `$2296`/`$2297`/`$2298`) and gourds (`$226c`).
5. Write `$23c1=0x0001`, `$23c5=0x0280` (unknown purpose).
6. Load 8 static SKELESNAIL enemies.
7. Load 6 NPC `0x0f` spawners across the map (groups 3/4/5/6).
8. Load PLACEHOLDER entity at `(41,28)`, save to `$287d`.
9. Unload gourds already collected (`$226c` bits).
10. If music not set: play music `0x6c`, fade in.
11. Clear `$23bf`, call cinematic script.

---

## Notes

- **The outro sequence** (triggered by `$22f1&0x40`) is the moment Fire Eyes and the player travel toward the volcano after completing Prehistoria. Three SKELESNAIL-sprite NPCs (used as windwalker companions?) spawn and walk east before the screen fades to room `0x69`.  
  - `// MISMATCH: The outro NPC uses `NPC 0x4c>>1` = NPC 0x26 = SKELESNAIL sprite. This seems unusual — expected a windwalker/Fire Eyes sprite. Verify in-game.`
- **Sand whirl numbering is non-contiguous:** whirls are labeled 1st, 3rd, 4th, 5th, 11th, 13th, 14th, 15th, "cave", "below-far-right", etc. — suggesting some were removed or renumbered during development.
- **Sniff spot numbering is sparse:** spots are #22–#38 and #44–#46, implying a global namespace shared with rooms `0x25`, `0x5b`, and others. The gaps (0–21, 39–43, 47+) are used by other rooms.
- **`$23c1` and `$23c5`** are written on every enter; their purpose is unknown.
  - `// TODO: identify purpose of $23c1=0x0001 and $23c5=0x0280`
- **`$2298 bit 0x40`** triggers an unload of obj 0x2b on enter, but no corresponding B-trigger was found. May be a removed sniff spot or sand whirl persistence flag.
  - `// TODO: clarify $2298 bit 0x40 / obj 0x2b usage`
- **Music `0x6c`** = Quicksand desert theme (unique to this room).
