# [0x0e] Gothica — Ebon Keep Dining Room

| Field | Value |
|-------|-------|
| Room ID | 0x0e |
| Name | Gothica - Ebon Keep Dining Room |
| Act | Act 3 — Gothica |
| Data offset | `0xacc8b8` |
| Enter script | `0x928061` → `0x98e8a4` |
| Step-ons | 2 |
| B-triggers | 1 |
| Music | 0x6e |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 1 |
| Gourds | 1 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | None (OBJ 0 is the gourd) |
| Forced dog form | None |
| Music | 0x6e |

---

## Overview

A small dining room on the west wing of Ebon Keep, connecting the main castle hall to Naris's room. Contains a single gourd holding Call Beads. The room has no enemies and no story events; it is a transitional area with one collectable.

---

## Enter Script Logic

1. Guard `$22eb&0x20`; teleport both to `[21,2d]`; fade-out music
2. If `$22dc&0x08` (WindWalker unlocked): `$2437=0x0007`
3. If `$2288&0x02` (gourd already looted): unload OBJ 0
4. Play music 0x6e (if not already playing)
5. `$23bf = 0x0001`; cinematic; **END**

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[46,3b:48,3e]` | MAP 0x0d @ `[0x00a0\|0x0258]` | South → Ebon Keep Hall |
| `[37,2e:3a,31]` | MAP 0x0f @ `[0x03b8\|0x0148]` | West → Ebon Keep West Room (Naris) |

---

## B-Trigger Scripts

| Tile | Contents | Guard | Notes |
|------|----------|-------|-------|
| `[51,26:53,27]` | 🔑 Call Beads (0x0807) — MAP REF 0x0000 | `$2288&0x02` | No NEXT ADD specified |

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22dc` | 0x08 | R | 📖 WindWalker unlocked — set `$2437=0x0007` |
| `$2288` | 0x02 | R/W | 💎 Call Beads (0x0807) looted from gourd MAP REF 0x0000 |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |

## Notes

- Minimal scripting — a single gourd (Call Beads at `[51,26]`) gated by `$2288&0x02` is the only interactive element.
- WindWalker unlock (`$22dc&0x08`) alters the room palette on entry, consistent with all other Ebon Keep interior rooms.
- Acts as a passive transit room; the only scripted path beyond loot is the WindWalker palette branch.
