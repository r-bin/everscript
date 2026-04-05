# [0x0d] Gothica — Ebon Keep Hall (Behind Verminator)

| Field | Value |
|-------|-------|
| Room ID | 0x0d |
| Name | Gothica - Ebon Keep Hall (Stairs, behind Verm) |
| Act | Act 3 — Gothica |
| Data offset | `0xa9d82a` |
| Enter script | `0x92805c` → `0x98e80f` |
| Step-ons | 8 |
| B-triggers | 0 |
| Music | 0x6e |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 8 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | Naris NPC `$2834` (NPC 0x00b0>>1=0x58) — cutscene only; 4× door OBJs (3,4,5) |
| Forced dog form | — |
| Music | 0x6e |

---

## Overview

The interior hall of Ebon Keep, behind the Verminator staircase. Contains the staircase entrance to the Queen's Room (0x11) and the dungeon entry (0x74). On first visit, a Naris introduction cutscene plays where he confronts the player and then agrees to take them to the Queen. On the second visit (`$22ec&0x20`), he leads boy+dog upstairs to meet Queen Camellia, transitioning to 0x11. The `$23c3` DOGGO CLOSE flag is always set on entry.

---

## Enter Script Logic

1. `$22eb&0x20` guard: teleport both to `[19,5f]`, fade-out
2. If `$22dc&0x08` (WindWalker unlocked): `$2437 = 0x0007`
3. `$23bf = 0x0001`; `$23c3 = 0x0001` (dog follows closely)
4. If CHANGE MUSIC set: PLAY MUSIC 0x6e
5. **Branch: IF `$22f5&0x04`** (post-event / door-open sequence):
   - Load OBJ 5, OBJ 3, OBJ 4
   - Clear `$22f5&0x04`
   - CALL cinematic; unload OBJ 5; PLAY SOUND 0x42; END
6. **Branch: ELSE IF `$22ec&0x20`** (Naris guided walk to throne):
   - Clear `$22ec&0x20`
   - RCALL 0x98e63a: fade-in, load Naris at `[39,2b]` → `$2834`; walk boy+dog+Naris upstairs to throne room area; `$22ec |= 0x10`; fade-out; CHANGE MAP 0x11 @ `[0x00d8|0x02c8]`
7. **Branch: ELSE** (normal / first visit):
   - CALL cinematic script
   - If NOT `$22df&0x40` (first meeting with Naris):
     - RCALL 0x98e45d: Naris first meeting cutscene (see below) → `$22ec |= 0x20`, `$22eb |= 0x20`, CHANGE MAP 0x0d @ `[0x0200|0x00b8]`

---

## Naris First Meeting Cutscene (RCALL 0x98e45d)

Triggered on first entry (NOT `$22df&0x40`). Sets `$22df|=0x40` so it never repeats.

- Boy+dog walk into the hall; Naris (`$2834`) appears from south
- Boy: *"Wow! This place is just like the other castle. Only, not quite as... clean."*
- Naris: *"Halt! Stop! Wait!"* / *"Who are you? What do you want?"*
- Boy: *"Uh, I'm [boy] and this is my dog, [dog]."*
- Boy: *"We've been sent here by the queen of Ivor Tower. She wants us to open the drawbridge!"*
- Naris: *"That imposter sent you here! ... Oh! This won't do! We can't have this!"*
- Naris: *"Please, I implore you, before you do anything rash, come with me!"*
- Naris leads boy+dog north, brightness fades; sets `$22ec|=0x20`, CHANGE MAP 0x0d

On re-entry with `$22ec&0x20`: RCALL 0x98e63a runs — Naris leads boy+dog up the stairs into the throne room and transitions to 0x11.

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[29,43:2a,44]` | MAP 0x74 @ `[0x0170\|0x0088]` | → Dungeon; `$22eb\|=0x40`; DOGGO CLOSE |
| `[2e,3e:30,40]` | MAP 0x0e @ `[0x0110\|0x01d8]` | → Dining Room (global 0x26) |
| `[36,54:39,56]` | MAP 0x5e @ `[0x00b0\|0x0048]` | → Ebon Keep Front Room (global 0x21) |
| `[44,24:46,25]` | MAP 0x11 @ `[0x00d8\|0x02a8]` | → Queen's Room; `$22ec\|=0x10`; OBJ 5 loaded; SOUND 0x46; DOGGO CLOSE |
| `[47,33:48,35]` | (OBJ 4 load) | NPC proximity gate: if NPC `$23c1` within range → walk NPC to `[0x44,0x34]`; SET OBJ 4 STATE = val:1 |
| `[47,30:48,32]` | (OBJ 4 unload) | NPC proximity gate: SET OBJ 4 STATE = val:0 |
| `[47,2b:48,2d]` | (OBJ 3 load) | NPC proximity gate: SET OBJ 3 STATE = val:1 |
| `[47,28:48,2a]` | (OBJ 3 unload) | NPC proximity gate: SET OBJ 3 STATE = val:0 |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22eb` | 0x40 | W | ⚙️ Set on dungeon step-on |
| `$22dc` | 0x08 | R | 📖 WindWalker unlocked |
| `$22ec` | 0x20 | R/W | 📖 Naris intro seen — set at end of first-meeting RCALL; cleared on re-entry to run guided-walk |
| `$22ec` | 0x10 | W | 📖 Guided walk to throne done — set after RCALL 0x98e63a; cleared in 0x11 to play sound |
| `$22df` | 0x40 | R/W | 📖 First meeting with Naris done — set during RCALL 0x98e45d; if set, skips Naris cutscene |
| `$22f5` | 0x04 | R/W | 📖 Post-door-event flag — if set: OBJ load/unload sequence |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |
| `$23c3` | — | W | ⚙️ DOGGO CLOSE = 0x0001 (dog follows closely) |
| `$2437` | — | W | ⚙️ Set to 0x0007 if WindWalker unlocked |
| `$2834` | — | W | ⚙️ Naris NPC pointer (NPC 0x58 at `[36,3f]` — cutscene only) |

## Notes

- The hall is the first Ebon Keep room where Naris appears; a guided-walk RCALL introduces her on first visit (one-shot, guarded by `$22df&0x01`).
- WindWalker unlock (`$22dc&0x08`) changes the room palette and sets `$2437=0x0007`; this pattern repeats across most Ebon Keep interior rooms.
- `$22f5&0x04` tracks the post-door-event cutscene state; the exit to Ebon Keep Sewers is gated by this same byte.
