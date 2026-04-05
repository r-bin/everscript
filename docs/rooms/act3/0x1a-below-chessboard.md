# [0x1a] Gothica — Below Chessboard

| Field | Value |
|-------|-------|
| Room ID | 0x1a |
| Name | Gothica - Below Chessboard |
| Act | Act 3 — Gothica |
| Data offset | `0xa8e53c` |
| Enter script | `0x92809d` → `0x99db84` |
| Step-ons | 4 |
| B-triggers | 1 |
| Music | 0x6c |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 4 |
| B-triggers | 1 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | NPC 0x74 (chess-level enemy) × 7 spawners |
| NPCs | NPC 0x14 (Energy Core OBJ) at `[4b,57]` → `$2834`; NPC 0x20 (showcase NPC) at `[71,65]` → `$2455` |
| Forced dog form | Poodle (0x08) — showcase path only |
| Music | 0x6c |

**Drop table**:

| Slot | Item | Rate | Qty |
|------|------|------|-----|
| 1 | 🧪 Honey (0x0802) | 100/132 | 1 |
| 2 | 💰 Currency (0x0001) | 30/132 | 0x64 (100) |
| 3 | 🧪 Revive Pellets (0x0807) | 2/132 | 1 |

---

## Overview

The underground cavern below the chessboard, reached by falling through one of the two holes on the chessboard (0x19). Contains the **Energy Core** — a key story item gated behind a B-trigger at `[2b,2b:2c,2c]`. A south step-on at `[34,4f:37,50]` leads to the Queen's cutscene room (0x78) on first visit, or exits to the Dark Forest Entrance (0x21) once `$22de&0x04` is set.

In showcase mode (`$22ef&0x20` set on entry), a special NPC 0x20 spawns at `[71,65]`. In combat mode, 7 NPC 0x74 spawners are loaded instead.

---

## Enter Script Logic

1. If `$22eb&0x20` (in-animation guard): teleport both to `[15,15]`, fade-out
2. Set enemy config (`$0ea2+0`, `$0eac+0`)
3. Drop table: Prize1=Honey(0x0802)/100, Prize2=Currency(0x0001)/30/100, Prize3=RevivePellets(0x0807)/2
4. If `$22eb&0x04` (showcase mode): clear `$22ef&0x20` and `$22e7&0x40`
5. If `$22ef&0x20` (entered via showcase fall):
   - Load NPC 0x20 at `[71,65]` → `$2455`, talk script `0x1a73`
   - Clear `$22ef&0x20`
6. Else (combat mode):
   - `$2433 = 0x0002`; load 7× NPC 0x74 spawners
7. If NOT `$22e7&0x40` (Energy Core not yet picked up):
   - Load NPC 0x14 at `[4b,57]` → `$2834`, sprite 0x00c0
8. Else: unload OBJ 0 (Energy Core object)
9. Music 0x6c if `$238d == 0x00`
10. `$23bf = 0x0000`

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[29,32:2a,36]` | (dialog only) | One-shot (`$22e7&0x20` guard): camera pan, boy: *"Hey! What's that? It looks like the energy core we saw when the statue blew up."*; sets `$22e7\|=0x20` |
| `[34,4f:37,50]` | MAP 0x78 @ `[0x00f8\|0x00b8]` | If NOT `$22de&0x04`: first visit → Queen's lair intro; `$234b=0x8d` |
|  | MAP 0x21 @ `[0x0058\|0x0058]` | Else: Queen cutscene done → exit south to Dark Forest Entrance |
| `[0f,03:12,04]` | MAP 0x19 @ `[0x0218\|0x0200]` | North exit (west hole) — global script 0x28 |
| `[26,02:29,03]` | MAP 0x19 @ `[0x0298\|0x0260]` | North exit (east hole) — global script 0x29 |

---

## B-Trigger Scripts

| Tile | Guard Flag | Action |
|------|------------|--------|
| `[2b,2b:2c,2c]` | `$22e7&0x40` (one-shot) | 💎 Receive Energy Core: show item message, `$2264\|=0x20`, `$22e7\|=0x40`, destroy `$2834` |

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x04 | R | ⚙️ Showcase mode active |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22ef` | 0x20 | R/W | 📖 Entered via showcase hole-fall — loads showcase NPC at `[71,65]`; cleared on entry |
| `$22e7` | 0x20 | R/W | 📖 Energy Core dialog seen (one-shot step-on at `[29,32:2a,36]`) |
| `$22e7` | 0x40 | R/W | 📖 Energy Core picked up — OBJ 0 unloaded; NPC not spawned on entry |
| `$2264` | 0x20 | W | 💎 Energy Core (story item carry flag) — set by B-trigger |
| `$22de` | 0x04 | R | 📖 Queen cutscene below chessboard watched — gates step-on exit to 0x78 vs 0x21 |
| `$234b` | — | W | ⚙️ Set to 0x8d on transition to 0x78 (Queen's lair) |
| `$23bf` | — | W | ⚙️ Set to 0x0000 on entry |
| `$2433` | — | W | ⚙️ Set to 0x0002 in combat mode (enemy spawn config) |
| `$2834` | — | W | ⚙️ Energy Core NPC pointer (NPC 0x14 at `[4b,57]`) |
| `$2455` | — | W | ⚙️ Showcase NPC pointer (NPC 0x20 at `[71,65]`) |

## Notes

- The Energy Core (`$2264|=0x20`) is the final key item required for Tinker's rocket, obtained via a one-shot B-trigger guarded by `$22e7&0x40`.
- `$22de&0x04` gates the north step-on exit: if the Queen cutscene below the chessboard has been watched, exit leads to 0x78 (Ivor Tower Queen's Room); otherwise to 0x21 (Dark Forest Entrance).
- Showcase mode entry (`$22ef&0x20` set) spawns a bonus NPC at `[71,65]` and forces Poodle dog form — the only path in this room where dog form is overridden.
