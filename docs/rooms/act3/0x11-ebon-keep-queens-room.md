# [0x11] Gothica — Ebon Keep Queen's Room (Camellia)

| Field | Value |
|-------|-------|
| Room ID | 0x11 |
| Name | Gothica - Ebon Keep Queen's Room |
| Act | Act 3 — Gothica |
| Data offset | `0xabbd82` |
| Enter script | `0x928070` → `0x98ef88` |
| Step-ons | 2 |
| B-triggers | 0 |
| Music | 0x18 (normal) / 0x8e (outro) |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 2 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | Camellia `$2836` (NPC 0x0098>>1=0x4c) at `[18,16]`; talk `0x1a49`; sprite 0x0040 |
| Forced dog form | — |
| Music | 0x18 |

---

## Overview

The throne room of Ebon Keep, where Queen Camellia (Bluegarden) resides. On first meeting (`NOT $22df&0x40`), a long cutscene plays: Naris leads boy+dog in, and Camellia tells her story (imprisoned by her evil twin, the imposter who now rules Ivor Tower). She gives the boy **Call Beads** (tops up to 6 if needed) and directs them to talk to **Tinker** to the east. Player regains control after the scene.

If `$22f1&0x40` (the "inside outro" earthquake flag): an earthquake cutscene plays — Camellia panics, everyone escapes to the fire pit (0x39). This is the Act 3 finale scene before the WindWalker launch.

If `$22f2&0x01` (credits mode): the credits animation sequence plays (NPCs line up facing camera, fade to credits).

---

## Enter Script Logic

1. `$22eb&0x20` guard: teleport both to `[1b,1f]`, fade-out
2. `$23bf = 0x0001`
3. If `$22dc&0x08` (WindWalker unlocked): `$2437 = 0x0007`
4. **Branch IF `$22f1&0x40`** (outro/earthquake):
   - Fade-out; PLAY MUSIC 0x8e; fade-in
   - RCALL 0x98e963 (throne room outro): earthquake shaking; Camellia: *"Oh, dear!! I'm so scared!!"*; boy: *"Camellia!!"*; *"We have to go!!"*; Camellia: *"Evermore is shaking apart! No time to explain!"*; dramatic escape walk; CHANGE MAP 0x39 @ `[0x0068|0x01d8]` (Fire Pit)
   - SKIP to END
5. **Else**: if CHANGE MUSIC: PLAY MUSIC 0x18; fade-in
6. **Branch IF `$22f2&0x01`** (credits):
   - RCALL 0x98eb25: credits character lineup + fade → credits
7. Load Camellia NPC at `[18,16]` → `$2836`; talk `0x1a49`; sprite 0x0040
8. **Branch IF NOT `$22df&0x40`** (first meeting):
   - Script-control `$2836` (Camellia); teleport to `[13,1b]`; BOY+DOG = STOPPED
   - Set `$22df|=0x40`
   - RCALL 0x98ebe0 (throne room first meeting cutscene — see below)
9. **Else** (repeat visits): cinematic script; if `$22ec&0x10`: PLAY SOUND 0x42; clear `$22ec&0x10`

---

## First-Meeting Cutscene (RCALL 0x98ebe0)

Long first-meeting scene with Naris and Camellia:

1. Naris leads boy+dog into the room; Naris: *"Please follow these stairs and speak to her highness."*
2. Boy+dog approach Camellia
3. Boy: *"Queen Bluegarden? What are you doing here?"*
4. Camellia: *"Have we met?"* / Boy: *"Yeah! In Ivor Tower! Don't you remember?"*
5. Camellia: *"Oh! You met the imposter — my evil twin!"*
6. Boy: *"Wow! This is like what happens in The Two Doctor Ids! We've found evil twins everywhere! First, there was Fire Eyes, er, Elizabeth and her evil twin, then Horace, and now... you!"*
7. Camellia: *"Elizabeth? Horace? You've met the others!"*
8. Long story: Camellia explains she was locked in dungeon by her twin, the king was hypnotized, the kingdom moved across the ravine
9. Camellia: *"Listen kid, I think that Tinker can help you get back to Podunk. But first, you're going to have to get rid of that imposter."*
10. Boy: *"She sent us here to open the drawbridge so that her troops could clear out the castle."*
11. Camellia: *"That's not good at all!"*
12. If Call Beads count < 6: give Call Beads (set `$231c = 0x0006`; "Received N Call Beads")
13. Camellia: *"If you need my help out in the field, you can call me by using one of your Call Beads."*
14. Camellia: *"Before you leave, make sure that you talk to Tinker in the chamber to the East."*
15. Boy: *"Thanks, Queen Bluegarden."* / Camellia: *"Please. Call me Camellia."*
16. `$225d|=0x01` (Camellia Call Beads set); player regains control

---

## Step-On Scripts

| Tile | Destination | Notes |
|------|-------------|-------|
| `[2c,39:2f,3c]` | MAP 0x10 @ `[0x0018\|0x00c8]` | East → Stained Glass Hallway (global 0x1d) |
| `[1e,49:21,4c]` | MAP 0x0d @ `[0x0200\|0x0088]` | South → Ebon Keep Hall; sets `$22f5\|=0x04` (post-door event) |

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ Animation-skip guard |
| `$22f1` | 0x40 | R | 📖 Inside outro flag — triggers earthquake/escape cutscene to 0x39 |
| `$22f2` | 0x01 | R | ⚙️ Credits mode |
| `$22df` | 0x40 | R/W | 📖 First meeting with Camellia done — set inside RCALL; prevents repeat |
| `$22dc` | 0x08 | R | 📖 WindWalker unlocked |
| `$22ec` | 0x10 | R/W | 📖 Guided-walk-to-throne complete — cleared in enter, plays sound 0x42 |
| `$225d` | 0x01 | W | 📖 Camellia Call Beads received — set during first-meeting cutscene |
| `$231c` | — | W | ⚙️ Call Beads count — set to 0x0006 if < 6 |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |
| `$2437` | — | W | ⚙️ Set to 0x0007 if WindWalker unlocked |
| `$2836` | — | W | ⚙️ Camellia NPC pointer (NPC 0x4c at `[18,16]`) |

## Notes

- Camellia's (Queen Naris's) first-meeting cutscene is guarded by `$22df&0x01`; subsequent entries show a shorter ambient interaction.
- The outro earthquake check (`$22f1&0x40`) routes the player directly to the fire pit (0x39) — this is the Act 3 finale trigger.
- Call Beads count is forced to a minimum of 6 on first meeting; the game sets the carry count to 6 regardless of current quantity (`$225d&0x01` flag, count written to inventory).
