# [0x15] Misc — Brian's Test Ground

| Field | Value |
|-------|-------|
| Room ID | 0x15 |
| Name | Brian's Test Ground |
| Act | Misc (developer room) |
| Data offset | `0xa0ff33` |
| Enter script | `0x928084` → `0x928000` |
| Step-ons | 0 |
| B-triggers | 0 |
| Music | — (unset) |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 0 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | 0 |
| NPCs | 0 |
| Forced dog form | — |
| Music | — |

---

## Overview

A leftover developer test room, named after one of the game's programmers ("Brian"). Contains a single opcode: a healing instruction. No layout content, no enemies, no NPCs, no gourds. Never accessible during normal gameplay.

---

## Enter Logic

1. `(94) HEAL 0x31 FOR ? WITH ANIMATION`
2. (end of script)

That is the complete enter script.

---

## Step-On Scripts

None.

---

## B-Trigger Scripts

None.

---

## Memory Access

None.

---

## Notes

- The entire room's script consists of one instruction: `HEAL 0x31 FOR ? WITH ANIMATION`. Nothing else exists in the room.
- "Brian" is a reference to a developer in the game's credits — this was almost certainly a quick throwaway room used during development for testing the heal mechanic or map-load flow.
- The enter script pointer (`0x928084`) points to `0x928000`, which is the very beginning of the map script table — `0x928000` is where the first script in the table begins.
- No persistent flags, no story progression, no items. Safe to ignore for randomizers or logic graphs.
