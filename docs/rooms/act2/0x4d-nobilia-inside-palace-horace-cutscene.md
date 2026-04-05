# 0x4d — Nobilia, Inside Palace (Horace Cutscene)

| Field | Value |
|-------|-------|
| **ROM addr** | `0x9fff1b` |
| **Data addr** | `0xad8669` |
| **Enter script** | `0x92819c` → `0x95d422` |
| **Step-on table** | `0xad8678` len=`0x0000` (0 entries) |
| **B-trigger table** | `0xad867a` len=`0x0000` (0 entries) |
| **Music** | `0x4a` |
| **Act** | Act 2 — Antiqua |

## Overview

The Emperor's palace interior. Pure cutscene room — no step-ons, no B-triggers.
Three distinct story beats play depending on story flags, all gated by
`$22dc&0x08` (WindWalker unlocked) and `$225f&0x20` (Vigor defeated).

The WindWalker flag is set unconditionally on the very first (non-animation) entry,
so all subsequent visits go to the Horace encounter path (Path C below).

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22dc` | `0x08` | 📖 | WindWalker unlocked (SET on first entry; gates cutscene vs. Horace path) |
| `$225f` | `0x20` | 📖 | Vigor defeated (sub-branches cutscene) |
| `$22e3` | `0x20` | 📖 | Tiny defeated (Horace dialogue variant) [0x4d] R |
| `$22f2` | `0x40` | 📖 | Horace met post-WindWalker [0x4d] R/W (set here on first WW meeting) |
| `$22f3` | `0x01` | 📖 | Crush dialog to be shown (set after dog enters palace) [0x4d] W |
| `$2258` | `0x04` | ⚗️ | Barrier spell [0x4d] R/W (set here when Horace teaches Barrier) |
| `$2261` | `0x01` | 📖 | Dog unavailable (set when dog stays in palace — Path A2) |
| `$22eb` | `0x20` | ⚙️ | IN_ANIMATION flag (standard; suppresses WindWalker flag set) |
| `$2445` | — | ⚙️ | PRESELECT_ALCHEMY = Barrier `0x04` (set before alchemy screen) |
| `$2836` | — | ⚙️ | Brightness counter (session-local) |
| `$283a` | — | ⚙️ | Horace entity ref (Path C; session-local) |
| `$244d` | — | ⚙️ | Pompolonius entity ref (Path A1; session-local) |
| `$2834` | — | ⚙️ | Emperor / Horace entity ref (paths A1+A2; session-local) |

## Enter Script Summary

**Common preamble:**
1. If `!IN_ANIMATION`: SET `$22dc |= 0x08` (WindWalker unlocked).
2. `CHANGE_DOGGO = Greyhound (0x06)`.
3. Teleport both to `(0x43, 0x01)`, fade-out/stop music; clear in-animation flag.
4. Play music `0x4a`; write `$23bf = 0x0001` (pacified); stop boy and dog.

**Branch on `$22dc&0x08`:**
- **`IF $22dc&0x08` (always true after step 1)**: skip 151 instructions → **Path C**.
- **`IF !$22dc&0x08`** (only possible if `IN_ANIMATION` was set on entry AND flag was never set before): fall through to **Path A/B**.

---

**Path A — Pre-WindWalker cutscene (first palace visit, entry via 0x0b step-on):**

- *Sub-path A1 — `!$225f&0x20` (Vigor not yet defeated):*
  - Load Pompolonius (NPC `0x31`) at `(0x21, 0x14)` → `$244d`; Emperor (NPC `0x20`) at `(0x35, 0x11)` → `$2834`.
  - Palace doors open (OBJ 0 cycles states 0→6); brightness fade-in.
  - Spy dialogue: Emperor asks Pompolonius about Diamond Eyes; Pompolonius says adventurers are searching and "that boy" is also looking, implies a surprise awaits; Emperor warns not to let it happen like "the kid on the plateau."
  - Doors close; brightness fade-out; SET `$22eb |= 0x20`; CHANGE MAP → [0x1c] North of Market @ `[0x0200|0x0020]`.

- *Sub-path A2 — `$225f&0x20` (Vigor defeated):*
  - Load Emperor (NPC `0x20`) at `(0x3d, 0x10)` → `$2834`; palace door animation.
  - Dog walks into the throne room from south; Pompolonius: *"Uh, Sir. We have a visitor."*
  - SET `$22f3 |= 0x01` (Crush dialog); SET `$2261 |= 0x01` (dog unavailable); CLEAR `$2261 bit1`.
  - CHANGE MAP → [0x4f] East of Crustacia @ `[0x0138|0x00b8]`.

---

**Path C — WindWalker unlocked (all normal re-entries):**

- Load Horace (NPC `0x45`) at `(0x37, 0x17)` → `$283a`; script-controlled, face north.
- Boy and dog walk in from south; call palace cutscene part 3 (`0x95d31b`).
- **Branch on Tiny defeated (`$22e3&0x20`):** if set → Horace: *"The news spread that you defeated Tiny. Too bad things had to end up that way."* / Boy: *"Yes, it's very sad. Tiny seemed troubled and in need of therapy."*
- **Else branch on Horace met (`$22f2&0x40`):** if set → Horace: *"Be careful around those Oglins!"* → exit.
- **Else (first WindWalker meeting):** Horace: *"By Gum! It's my young friends! I'm afraid I have unpleasant news... Tiny has set himself up as leader of the Oglins in the depths of the pyramid. I fear the power has gone to his head."*; SET `$22f2 |= 0x40`.
- If `!$2258&0x04` (Barrier not yet taught): Horace: *"I discovered a spell — 1 Limestone and 2 Bone."* + show Barrier alchemy screen (`$2445 = 0x04`) + SET `$2258 |= 0x04`.
- Boy/dog walk south; SET `$22eb |= 0x20`; CHANGE MAP → [0x0b] Palace Grounds @ `[0x02b0|0x00f8]`; write `$234b = 0x4f`.

## Exits

| Dest | Coords | Notes |
|------|--------|-------|
| [0x1c] North of Market | `[0x0200\|0x0020]` | Path A1 (pre-Vigor spy scene) |
| [0x4f] East of Crustacia | `[0x0138\|0x00b8]` | Path A2 (post-Vigor, dog enters palace) |
| [0x0b] Palace Grounds | `[0x02b0\|0x00f8]` | Path C (WindWalker; sets `$234b=0x4f`) |

## B-Triggers

None.

## NPCs

| Ref | NPC# | Pos | Path |
|-----|------|-----|------|
| `$244d` | `0x31` (Pompolonius) | `(0x21, 0x14)` | Path A1 only |
| `$2834` | `0x20` (Emperor) | `(0x35, 0x11)` (A1) / `(0x3d, 0x10)` (A2) | Paths A1 + A2 |
| `$283a` | `0x45` (Horace) | `(0x37, 0x17)` | Path C only |

## Notes

- **WindWalker unlock sequence:** `$22dc|=0x08` fires at the very first instruction
  of the enter script, but only if `!IN_ANIMATION`. Since entry from 0x0b (step-on)
  always sets `IN_ANIMATION`, the flag is suppressed on the first two story visits
  (Paths A1 and A2). The flag is set the moment the player walks in directly — which
  normally happens automatically after the story returns control. Subsequent entries
  (Path C) always have `$22dc&0x08` set and skip the cutscene entirely.
- Path A2 is the "Sacred Dog ceremony" scene: the dog physically enters the palace
  and is presented to the Emperor, setting up the entire pyramid / Crustacia arc.
  `$22f3|=0x01` (Crush dialog) is also set here, indicating the boy will be sent
  east via 0x4f to deal with the Crustacia situation.
- Barrier (⚗️ `$2258&0x04`) is taught in Path C on first WW meeting; recipe is
  1× Limestone + 2× Bone.
