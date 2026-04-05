# [0x03] Misc — Intro: Mansion Exterior 1995

| Field | Value |
|-------|-------|
| Room ID | 0x03 |
| Name | Intro - Mansion Exterior 1995 |
| Act | Misc (intro sequence / outro sequence) |
| Data offset | `0xaaeaba` |
| Enter script | `0x92802a` → `0x92ef08` |
| Step-ons | 0 |
| B-triggers | 0 |
| Music | 0x00 (normal path, silence initially) / 0x4a (outro path) |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 0 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | 1 animated dog on normal path; 4 friends NPCs on outro path |
| Forced dog form | — |
| Music | 0x00 initially (normal); 0x4a (outro) |

---

## Overview

The exterior of the Highwater mansion in 1995 — serves double duty as both an **intro room** (boy approaches the mansion and follows the dog inside, leading to the start of the adventure in 0x46) and the **outro room** (friends reunion scene after defeating the final boss).

Two major paths based on `$22f1&0x40`:

1. **Outro path** (`$22f1&0x40` set): Four friends (Horace, Camellia, and two others from the adventure) reunite outside the mansion, deliver farewell dialog, and the screen fades to the credits via `0x92d0d6`. This is the true game ending.
2. **Normal intro path** (`$22f1&0x40` clear): Boy follows the dog along the mansion wall to the secret entrance. Several NPCs appear from side doors. Sets `$22ec|=0x20` (intro/lab flag), then CHANGE MAP → 0x46 (Omnitopia / Prof's lab).

---

## Enter Logic

**Outro path** (if `$22f1&0x40`, RCALL `0x92edd8`):
1. BOY+DOG = STOPPED; CALL `0x92a3e7` (Hide status bar)
2. Load 4 friend NPCs at positions `[09,17]`, `[0e,17]`, `[1c,17]`, `[17,17]` with sprites `0x00ae>>1`, `0x002a>>1`, `0x0098>>1`, `0x008a>>1` → script-local args 0/2/6/4
3. Check music lock; if not: PLAY MUSIC `0x4a`; FADE IN
4. Camera `$242b = 0x0010`, `$242d = 0x0000`; CALL `0x92de75` (cinematic)
5. Teleport boy+dog, set brightness 0; CALL `0x92e6a8` (BG animation); VRAM write; SLEEP 31
6. SFX `0x70`; SLEEP 31; camera `$242b = 0x0020`, `$242d = 0x02a0`; SLEEP 15
7. Walk dog to `[14,6b]` → `[14,48]`; face dog north; SFX `0x24`; SLEEP 59
8. Teleport boy from `[6b,01]`; walk to `[14,6b]`; dog teleported to `[1,1]` (despawn)
9. Wait for boy; SFX; boy faces south/north; NPC brightness ramp-up (`$2836` 0→15)
10. Dialog sequence (Horace/friends):
    - **"Well, we're safe and we're home, friends. That was a close call!"**
    - **"It certainly was."** (Horace)
    - **"Now, a new adventure begins in this real world."** (Camellia)
    - **"It's not 1965 anymore, you know!"** (Horace)
    - **"I know that it was time to go, but I'm going to miss my village."** (Camellia)
    - **"And I will miss my kingdom."** (Horace)
    - **"I wonder what will become of Evermore?"**
11. Fade-out; stop music; `0x92d0d6` (credits/ending); END

**Normal intro path** (`$22f1&0x40` clear):
1. If `$22eb&0x20` (in animation): clear `$22eb&0x20` and skip teleport; else teleport both to `[01, 6b]`
2. `$23bf = 0x0001`; check music lock; if not: PLAY MUSIC `0x00`; FADE IN
3. Camera `$242b = 0x0000`, `$242d = 0x02a0`; boy teleported to `[ff,ff]`; dog teleported to `[6b,01]`
4. SET BRIGHTNESS 0; CALL `0x92ed63` (animated OBJ setup); VRAM write; SLEEP 31
5. SFX `0x70`; SLEEP 31; scroll `$242b = 0x0020`, `$242d = 0x02a0`
6. Walk dog to `[14,6b]`, SFX `0x24`; wait; walk dog to `[14,48]`; dog faces north; SLEEP 15
7. SFX `0x24`; SLEEP 59; teleport boy from `[6b,01]`; walk boy to `[14,6b]`; wait
8. Dog teleported to `[1,1]`; wait for boy; boy faces south; SLEEP 7
9. Open box; **"Now, where did he go?"**; CLEAR TEXT
10. Boy faces north; camera `$242b = 0x0020`, `$242d = 0x01a0`; walk boy to `[14,48]`; SLEEP 73
11. OBJ 0 → state 6; SLEEP 29; OBJ 1 → state 6; SLEEP 27; OBJ 2 → state 6
12. Wait for boy; **"Hmmm... the door is open..."** (boy faces north/east); SLEEP 15
13. **"I'd better take a look inside."**; walk boy to `[14,37]`; camera `$242b = 0x0020`, `$242d = 0x0150`
14. Wait for NPC; **"There you are! You know, I think that cat is long gone!"**
15. Camera `$242b = 0x0000`, `$242d = 0x0150`; wait; **"Hey! Where are you going?"**; SLEEP 59
16. Camera to `[0x0000,0x00a0]`; wait; **"Yikes! Watch out for that..."**; SFX `0x3c`/`0x3e`/`0x3c`
17. **"...oops."**; **"Hey! Look! A mummy... a chainsaw... and a balloon animal!"**
18. Camera `$242b = 0x0040`, `$242d = 0x00a0`; wait; **"Hmmm... this wall panel is kind of loose..."**
19. SFX `0x42`; SLEEP 29; **"Wow! I think we've found some sort of secret entrance!"**; SLEEP 29
20. Camera `$242b = 0x0020`, `$242d = 0x0030`; wait for NPC; SLEEP 59
21. `$22ec |= 0x20`; SLEEP 59; `$22eb |= 0x20`
22. Brightness ramp-down (`$2836` 14→0); stop music; Fade-out
23. CHANGE MAP `0x46` @ `[0x00d0|0x02d8]` (Omnitopia / Prof's lab)

---

## Step-On Scripts

None.

---

## B-Trigger Scripts

None.

---

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22f1` | 0x40 | R | 📖 Inside outro — triggers ending cutscene |
| `$22eb` | 0x20 | R/W | ⚙️ In-animation flag — cleared on entry if set; set before CHANGE MAP |
| `$22ec` | 0x20 | W | 📖 Intro/outro flag for Prof. lab (0x46) — set just before CHANGE MAP |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on normal-path entry |
| `$238d` | — | R | ⚙️ Music lock |
| `$2836` | — | W | ⚙️ Brightness counter (normal path: 14→0 ramp); NPC arg on outro path |

---

## Notes

- Like 0x32, this room appears in both the intro and the outro. In the outro path, it hosts the true ending scene — all four companions (Horace, Camellia, and two others from the adventure) appear and deliver farewell dialog before the credits.
- `$22ec|=0x20` is set just before the CHANGE MAP to 0x46. The lab room (0x46) reads this flag to determine the intro variant to play (first-entry intro path, not the lab's normal enter logic).
- The dog "running off screen" is implemented by walking to `[14,6b]`, then `[14,48]`, then teleporting to `[1,1]` — the teleport-off-screen technique used across multiple intro/outro rooms.
- The normal intro path has no music for most of its duration (PLAY MUSIC 0x00 = silence); only ambient SFX are heard until the player enters 0x46.
- The outro path triggers `0x92d0d6` which is the credits/ending global script — not a CHANGE MAP.
