# 0x5a — Acid Rain Guy

**ROM:** `0x9fff4f` | **Data:** `0xad9309` | **Enter:** `0x9281dd` → `0x93af06`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x46` |
| Objects | 2 (gourds) |
| NPCs | 1 (Acid Rain Guy) |
| Step-on zones | 1 |
| B-triggers | 2 |
| Drop table | none |

## Connections

| Direction | Destination | Step-on Zone |
|-----------|-------------|--------------|
| West | `0x59` Quick Sand Desert @ `[0x0398\|0x0110]` | `[05,0a:07,0d]` |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$2258` | `0x01` | 📖 | Acid Rain dialog seen / spell learned |
| `$226c` | `0x80` | 🫙 | Water gourd collected (obj 0) |
| `$226d` | `0x01` | 🫙 | Ash gourd collected (obj 1) |

## Objects

| Obj | Unload Condition | Contents |
|-----|-----------------|----------|
| 0 | `$226c & 0x80` | Water gourd |
| 1 | `$226d & 0x01` | Ash gourd |

## NPCs

| NPC ID | Position | Talk Script | Notes |
|--------|----------|-------------|-------|
| `0x12` | `(0x13, 0x18)` | `0x17b8` | Acid Rain Guy |

## Enter Script Summary

1. **Animation branch:** If `$22eb&0x20` (entered via indoor-to-outdoor transition): teleport both to `(0x09, 0x18)`, fade out. Else clear `$22eb&0x20`.
2. Clear `$22ee&0x01` (unknown intro/outro flag).
3. Load NPC `0x12` at `(0x13, 0x18)`, store to `$2455`; assign talk script `0x17b8` (Acid Rain Guy).
4. If `$2258&0x01` already set: make NPC script-controlled, face west (skip intro).
5. Unload obj 0 if `$226c&0x80`; unload obj 1 if `$226d&0x01`.
6. If `$238d ≠ 0`: play music `0x46`, fade in.
7. `$23bf = 0x0001`.
8. Call `0x92de75` (cinematic init script).
9. If NOT `$2258&0x01`: call Acid Rain dialog subroutine `0x93ae82`.

### Acid Rain Dialog (`0x93ae82`)

1. Set `$2258|=0x01` (mark dialog seen).
2. Stop boy+dog movement; boy walks to `(0x09, 0x18)`, dog walks toward NPC at `(0x13, 0x1c)`.
3. NPC walks left; dog performs look-around animation (`0x78` instruction, 0x003a).
4. **TEXT 0597:** *"Well, you look like you've been through a lot! There are a lot of bugs and baddies out there. They are probably giving you a hard time."*
5. Clear text; boy steps right, faces south.
6. **TEXT 059a** (dog voice): *"You're telling me!"*
7. Clear text; NPC walks left again; boy faces east.
8. YIELD (cooperative multitasking break).
9. **TEXT 059d:** *"Here's something that should help you out in the sand, tar and lava. It's the formula of Acid Rain. Just mix three parts Water with one part Ash and you'll have a potent concoction."*
10. Show Alchemy selection screen (pre-selected: Acid Rain `0x00`).
11. Set ingredient shop `$2459=0x0004`; call "Buy ingredients dialog" (`0x54`).
12. Set save spot `$2449=0x0009`; call "Save dialog" (`0x4d`).
13. Restore NPC to player/AI-controlled.

## Step-on Zones

| Zone | Destination | Condition |
|------|-------------|-----------|
| `[05,0a:07,0d]` | `0x59` Quick Sand Desert @ `[0x0398\|0x0110]` | always |

## B-triggers (Gourds)

| Zone | Contents | Flag | Obj |
|------|----------|------|-----|
| `[0d,09:0f,0b]` | 💧 Water (`0x0201`) × 3 | `$226c bit 0x80` | obj 0 |
| `[0f,0a:11,0c]` | 🌿 Ash (`0x0214`) × 3 | `$226d bit 0x01` | obj 1 |

## Notes

- Simplest room in Act 1: single NPC, no enemy spawns, one exit.
- Uniquely bundles **alchemy teaching** + **ingredient shop** + **save point** in one cutscene.
- `$2258 bit 0x01` is permanent once set, preventing repeated cutscene playback.
- The two gourds are conveniently stocked with Water and Ash — the ingredients for Acid Rain itself.
