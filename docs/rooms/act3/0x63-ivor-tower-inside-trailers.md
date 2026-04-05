# [0x63] Gothica — Ivor Tower, Inside Trailers

| Field | Value |
|-------|-------|
| Room ID | 0x63 |
| Name | Gothica - Ivor Tower, inside trailers |
| Act | Act 3 — Gothica |
| Data offset | `0xad8000` |
| Enter script | `0x92820a` → `0x9ab34a` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | 0x76 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | none |
| NPCs | 1 barker (NPC 0x48) + 2 audience NPCs (spawned mid-cutscene) |
| Forced dog form | Poodle (0x08) |
| Music | 0x76 |

---

## Overview

The interior of Perceval Plank's three travelling trailers. `$234b` (set by 0x62 step-ons) determines which trailer was entered: 0 = left, 1 = middle (the one with the full cutscene), 2 = right.

If `$234b == 1` AND `$22dc&0x01` is NOT set (pig race not yet done): runs the full Exhibition cutscene. Barker (NPC `0x90>>1 = 0x48`) leads boy through three exhibits:
1. **Mr. Head** — "The man with no body." (OBJ 0)
2. **The Unigoat** — "The one-horned beauty." (OBJ 1)
3. **Mungola** — "It has escaped! I would be very careful..." (OBJ 2)
4. **Pigpoodle** — the dog, revealed as the final exhibit (OBJ 3 = dog transformed)

At the end of Pigpoodle reveal: sets `$22ee |= 0x08` and `$22f5 |= 0x20` (triggers pig race in 0x4e), then CHANGE MAP → 0x62 @ `[0x02a0|0x0218]` with `$22eb|=0x20`.

If `$22f2&0x01` (credits): runs a special credits cutscene in this room instead.

---

## Enter Script Logic

1. If `$22eb&0x20` (in animation): teleport both to `[1c,17]`, fade-out, clear flag
2. RCALL: sets up camera bounds
3. If `$22f2&0x01` (credits): run credits NPC-spawn sequence (NPC 0x48, 0x4b, 0x16, 0x62, 0x55, 0x56 spawned)
4. Play music 0x76; set `$23bf = 0x0001`
5. If `$234b == 1` AND NOT `$22dc&0x01`:
   - Set camera bounds `[0x0000|0x0000]`→`[0x01c0|0x0100]`
   - RCALL: full Exhibition cutscene (see below)
6. If `$234b == 2`: CHANGE MAP path exits not triggered; load NPC 0x56 at `[4b,1d]` talk `0x1acd`
7. If `$234b == 0` AND NOT `$22dc&0x01`: load NPC 0x55 at `[4b,1d]` talk `0x1aca`
8. Cinematic script + SOUND 0x42

---

## Exhibition Cutscene (`$234b == 1`, pre-race)

Barker (`$2836` = NPC 0x48 at `[11,14]`) leads boy through three exhibits in sequence:

| Exhibit | OBJ | Dialog |
|---------|-----|--------|
| Mr. Head: The man with no body | OBJ 0 | "The first stop… will make you ponder the principles of our existence. … How, you will ask, can such a creature live and breathe? …Mr. Head: The man with no body." — Boy: "I have an itch on my nose. It's very uncomfortable." — "Weird!" |
| The Unigoat | OBJ 1 | "This next exhibit comes to us from the far east… It is fantastic, freakish and full of cheese-producing goodness — The Unigoat!" — "Isn't she amazing?" — "Please! Do not touch the horn!" |
| Mungola | OBJ 2 | "This disgusting, vile and gruesome beast… I give you the terror that is — Mungola!" — "Mungola has escaped! It could appear around any corner!" |
| Pigpoodle (dog) | OBJ 3 | "I present to you… the fabulous, unbelievable — **Pigpoodle**!" — Boy: "[dog], is that you?" — "I know that you've been going through some changes, but this is ridiculous!" — "I guess if I were a poodle with the head of a pig, I'd run, too!" — "Maybe it would work better if we started with a pig and dressed it up like a poodle." |

After Pigpoodle:
- Sets `$22ee |= 0x08`
- Sets `$22f5 |= 0x20` (pig race pending)
- Fade-out → CHANGE MAP → 0x62 @ `[0x02a0|0x0218]` with `$22eb |= 0x20`

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[2c,13:2e,15]` | MAP 0x62 @ `[0x00a0|0x00d8]` / `[0x0190|0x00a8]` / `[0x0270|0x00d8]` | North exit; sets `$22eb|=0x40`; destination based on `$234b` (0→left, 1→middle, 2→right) |
| `[14,0f:16,11]` | same routing | Second exit tile; same logic |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22f5` | 0x20 | W | 📖 Pig race pending — SET here after Pigpoodle exhibit |
| `$22ee` | 0x08 | W | 📖 Unknown — also SET alongside `$22f5&0x20` after Pigpoodle exhibit |
| `$22dc` | 0x01 | R | 📖 Pigrace finished — gates whether the Exhibition cutscene runs |
| `$234b` | — | R | ⚙️ Which trailer entered (0=left, 1=middle, 2=right) |
| `$22f2` | 0x01 | R | ⚙️ Credits mode — triggers credits NPC spawn instead of normal enter |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard (standard `IN_ANIMATION` pattern) |
| `$22eb` | 0x40 | W | ⚙️ Set before step-on exit to 0x62 (signals "returning from trailer") |
| `$2443` | — | W | ⚙️ Dog form set to Poodle (0x08) |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |
| `$2836` | — | W | ⚙️ Barker NPC pointer (NPC 0x48 at `[11,14]`) |

## Notes

- All three trailers share a single room (0x63); which interior is shown depends on `$234b` passed from 0x62 (0=left, 1=middle, 2=right).
- The Pigpoodle exhibition cutscene sets both `$22f5&0x20` (pig race pending) and `$22ee&0x08`; it only runs if `$22dc&0x01` (pigrace finished) is NOT set.
- Credits mode (`$22f2&0x01`) is checked here and triggers a completely different NPC load path — an unusual use of the credits flag in a gameplay room.
