# 0x36 — Both Fire Pits (One Room)

**ROM:** `0x9ffebf` | **Data:** `0xa3f774` | **Enter:** `0x928129` → `0x97cb63`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x40` (normal); `0x84` (outro/WindWalker sequence) |
| Map bounds | `(0,0)` to `(0x190, 0x190)` |
| Objects | 0–6 (fire pit state objects + sniff-spot objects) |
| Step-on zones | 2 |
| B-triggers | 4 (all sniff spots, no gourds) |
| Sniff spots | 4 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| North | `0x25` Fire Eyes' Village @ `[0x03e8\|0x0328]` | enter script (outro path) | Only during `$22f1&0x40` outro |
| Fire pit | `0x3a` Antiqua - Nobilia, Fire pit @ `[0x00e8\|0x00c8]` | step-on `[21,23:28,2a]` | Via WINDWALK; requires `$2355==2`; player confirms Omnitopia |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22f1` | `0x40` | 📖 | **Inside outro** (Act 1 outro sequence active; WindWalker landing) |
| `$22dc` | `0x08` | 📖 | WindWalker unlocked (required for outro fire pit sequence) |
| `$22e5` | `0x08` | ⚙️ | WW Landing (set before loading fire pit from overworld) |
| `$22eb` | `0x08` | ⚙️ | Debug flag (forces `$22f1\|=0x40` and `$22dc\|=0x08` on entry) |
| `$22d9` | `0x08` | 📖 | Unknown (gates OBJ 2 state=1 if also `$237d==1`) |
| `$2261` | `0x01` | 📖 | Dog unavailable (teleports dog to `(0x33,0x01)`, calls global 0x36) |
| `$237d` | full byte | ⚙️ | State counter; 0/1 = fire pit landing; 2 = second landing; 4 = Omnitopia selected |
| `$237b` | full byte | ⚙️ | Previous `$237d` value; set to `$237d` during WW landing |
| `$2355` | low byte | ⚙️ | WindWalker landing phase: 1 = first fire pit (OBJ 0 state 1), 2 = second fire pit (OBJ 0 state 2) |
| `$22fe` | low byte | ⚙️ | WW landing attempt counter (0 = first entry; incremented on first outro entry) |
| `$2545` | low byte | 📖 | Dialog response: "Is your destination Omnitopia?" (0=Yes → `$237d=4`) |
| `$22d3` | `0x04` | 👃 | Sniffed Ash (#5) |
| `$22d3` | `0x08` | 👃 | Sniffed Clay (#6) |
| `$22d3` | `0x10` | 👃 | Sniffed Oil (#3) |
| `$22d3` | `0x20` | 👃 | Sniffed Oil (#4) |

## NPCs

| NPC ID | Position | Notes |
|--------|----------|-------|
| `0x2a` | `(0x01, 0x33)` | WindWalker NPC; only loaded during outro (`$22f1&0x40`) and `$22fe>0`; ref `$2836` |
| `0x20` | `(0x17, 0x1f)` | Fire pit visual NPC; loaded during WW landing with `$2355==1` (sprite 0x014e) or `$2355==2` (sprite 0x0144); ref `$2834` |

## Enter Script Summary

1. `$22eb&0x20` guard; default teleport to `(0x1d, 0x29)`; stop music.
2. Debug flag (`$22eb&0x08`): if set, force `$22f1|=0x40` (outro) + `$22dc|=0x08` (WindWalker).
3. **Music selection:** if `$22f1&0x40` → music `0x84` (outro); else → music `0x40` (normal).
4. Set map bounds; unload looted sniff objects (`$22d3&0x04/08/10/20`).
5. If `$22d9&0x08` AND `$237d==1`: SET OBJ 2 STATE=1. SET OBJ 0/1 STATE=0.
6. **Outro branch** (`$22f1&0x40`):
   - Call "Outro rain and sky color" (`0x92d92a`); hide status bar; `$23bf=1`; `$2355=2`; `$237d=0`.
   - First pass (`$22fe==0`): set `$22e5|=0x08`, increment `$22fe`, skip rest.
   - Subsequent passes: load NPC `0x2a` at `(0x01,0x33)`; teleport boy+dog+NPC to `(0x0118,0x00f8)`; face west; NPC goes script-controlled; clear `$22e5&=~0x08`.
   - WW landing check (if `$22e5&0x08` OR `$237b==0/1` AND `$22dc&0x08` AND `$237d==0/1`):
     - `$2355==1`: OBJ 0+1 state=1; load fire NPC `0x20` at `(0x17,0x1f)`, sprite 0x014e.
     - `$2355==2`: OBJ 1 state=1, OBJ 0 state=2; load fire NPC `0x20` at `(0x17,0x1f)`, sprite 0x0144.
     - If `$22e5&0x08`: set `$237b=$237d`; stop boy+dog; teleport `$2834` to off-screen start; play WW landing animation.
   - Dog check (`$2261&0x01`): if dog unavailable, hide dog.
   - If NOT WindWalker: CHANGE MAP 0x25 @ `[0x03e8|0x0328]` directly (early outro fast path).
7. **Normal branch** (NOT outro): call cinematic `0x92de75`. WindWalker mode still checked via `$22dc&0x08`.

## Step-ons

| Zone | Effect |
|------|--------|
| `[23,2e:26,30]` | Internal: if `$237d==1` → call `0x97c760`; if `$237d==0` → call `0x97c756` (handles WW flight sequence bookkeeping) |
| `[21,23:28,2a]` | **Fire pit zone**: fade-out; if `$2355==1` → WW animation, transition (silent); if `$2355==2` → WW animation, ask **"Is your destination Omnitopia?"** (Y/N); Yes: `$237d=4` → WINDWALK to `0x3a` Antiqua; No: different handler (`0x92dc1b`) |

## Sniff Spots

| # | Zone | Ingredient | Flag | `$2461` |
|---|------|------------|------|---------|
| 3 | `[2e,28:2f,29]` | 🛢️ Oil | `$22d3&0x10` | 3 |
| 4 | `[23,20:24,21]` | 🛢️ Oil | `$22d3&0x20` | 1 |
| 5 | `[1e,29:1f,2a]` | 💨 Ash | `$22d3&0x04` | 1 |
| 6 | `[1c,24:1d,25]` | 🏺 Clay | `$22d3&0x08` | 2 |

No gourds.

## Notes

- **This room serves dual purposes:** Normal gameplay (fire pit area players can visit freely) AND the Act 1 → Act 2 transition (WindWalker sequence ending Prehistoria).
- **`$22f1&0x40` = "Inside outro"** is the clearest Act boundary flag seen so far. It is set before loading this room during the ending sequence.
- **The fire pit dialog** (`"Is your destination Omnitopia?"`) appears when `$2355==2` — meaning the player has gone through the first fire pit (Prehistoria) once already, and is now entering the second one to travel to Antiqua. The WindWalker then calls the WINDWALK instruction which transitions to room 0x3a in Antiqua.
- **`$237d=4`** is written when the player confirms Omnitopia. This likely signals the WindWalker that the landing destination is set.
- **`$2355`** tracks which fire pit the player has used: 1 = first fire pit entry (just the WindWalker tests the path), 2 = second fire pit entry (player actually travels).
- **`$22e5&0x08` = "WW Landing"** — this is set by the overworld script before loading 0x36 for the WindWalker landing sequence. Clears after landing.
- **Music `0x84`** = Act 1 outro theme. Music `0x40` = standard fire pits theme.
- The NPC `0x2a` is loaded in 0x3b as the Mammoth Viper Commander, but here it appears to be the WindWalker NPC. // TODO: Verify NPC type — same ID `0x2a` used for two different NPCs in this act?
