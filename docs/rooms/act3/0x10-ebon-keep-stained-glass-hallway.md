# [0x10] Gothica — Ebon Keep Stained Glass Hallway

| Field | Value |
|-------|-------|
| Room ID | 0x10 |
| Name | Gothica - Ebon Keep Stained Glass Hallway |
| Act | Act 3 — Gothica |
| Data offset | `0xadc553` |
| Enter script | `0x92806b` → `0x998321` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | 0x6e |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 (locked until battle won) |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | NPC 0x28 and NPC 0x29 and NPC 0x4b (glass knight variants) — 5 total across waves |
| NPCs | OBJs 0–4 = stained glass windows that spawn enemies; OBJ 3 = showcase OBJ |
| Forced dog form | — (showcase: sets Crusader Sword + Poodle) |
| Music | 0x6e (normal) / 0x5a (battle) / 0x36 (victory fanfare) |

---

## Overview

A hallway with magical stained glass windows that come to life as enemies. The battle is triggered automatically on first entry when `$22de&0x01` is not set. Five enemy waves spawn from the windows using a timer loop that advances by stage (`$2835`) every time a wave is cleared. Once all 5 waves are defeated, `$22de|=0x01` is set, the victory fanfare plays, and boy says *"Whew! Those guys were a pane in the glass."* The two exits — to the Queen's Room (0x11, west) and to Tinker's Room (0x14, east) — are **locked until the battle is won**.

In showcase mode (`$22eb&0x04`): sets weapon = Crusader Sword (0x06) + dog = Poodle (0x08), walk-in animation, then transitions to the attraction/demo mode sequence.

---

## Enter Script Logic

1. `$22eb&0x20` guard: teleport both to `[07,19]`, fade-out
2. If `$22eb&0x04` (showcase): RCALL showcase walk-in → CALL "Attraction mode, after Thraxx" (0x59); END
3. Music 0x6e if `$238d == 0x00`
4. `$23bf = $22de&0x01` (0 if battle pending, 1 if battle won)
5. **Branch IF NOT `$22de&0x01`** (battle not yet won):
   - RCALL: walk-in cinematic with boy+dog
   - Boy: *"Wow! What cool windows! The pictures seem almost... alive. It must be a trick of the light."*
   - Dog reacts (sound effect); Boy: *"What is it [dog]? What's wrong?"*
   - OBJ 0 loaded (first window); music → 0x5a (battle); `$2834|=0x01` (battle start)
   - **Timer loop** (`$2835` wave counter 0–5): every ~0x044c game ticks (or when `$2834&0x01` is set):
     - Wave 0: NPC 0x50>>1=0x28 at `[0c,16]` (knight #1)
     - Wave 2: OBJ 1 loaded; NPC 0x29 at `[12,16]` (knight #2)
     - Wave 4: OBJ 2 loaded; 2× NPC 0x4b at `[18,16]` (dual spawn — different speed values)
     - Wave 1: OBJ 3 loaded; NPC 0x29 at `[1e,16]` (knight #3)
     - Wave 3: OBJ 4 loaded; NPC 0x28 at `[24,16]` (knight #4)
     - Wave 5 (`$2835==6`): all waves complete → `$22de|=0x01`; BOY+DOG STOPPED; music → 0x36 (fanfare); hold-up weapon animation; *"Whew! Those guys were a pane in the glass."*; player controlled; END
6. **Else** (battle already won): CALL cinematic; END

---

## Step-On Scripts

Both step-ons require `$22de&0x01` (battle won) to function; otherwise they fall through silently.

| Tile | Destination | Notes |
|------|-------------|-------|
| `[1e,20:20,25]` | MAP 0x14 @ `[0x0028\|0x0198]` | East → Tinker's Room (only if `$22de&0x01`) |
| `[08,20:0a,25]` | MAP 0x11 @ `[0x01b8\|0x01a0]` | West → Queen's Room (only if `$22de&0x01`) |

---

## B-Trigger Scripts

None (battle is triggered from enter script, not B-triggers).

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x04 | R | ⚙️ Showcase mode |
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22de` | 0x01 | R/W | 📖 Stained glass battle won — unlocks step-on exits; set by battle loop when wave 5 cleared |
| `$2835` | — | W | ⚙️ Wave counter (0–6); used as internal loop index during battle |
| `$2834` | 0x01 | W | ⚙️ Battle start flag — set/cleared by timer loop |
| `$23bf` | — | W | ⚙️ Set to `$22de&0x01` on entry (0 or 1) |

## Notes

- The wave battle is scripted entirely from the enter script — no B-triggers; five enemy waves use `$2835` as the wave counter.
- `$22de&0x01` persists the battle-won state; exits to the Queen's Room west corridor open permanently once all waves are cleared.
- Showcase mode (`$22eb&0x04`) bypasses the wave battle entirely — `$23bf` is set to the current value of `$22de&0x01` on entry (0 or 1) rather than a fixed constant.
