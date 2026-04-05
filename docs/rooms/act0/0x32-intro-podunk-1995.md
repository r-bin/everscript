# [0x32] Misc — Intro: Podunk 1995

| Field | Value |
|-------|-------|
| Room ID | 0x32 |
| Name | Intro - Podunk 1995 |
| Act | Misc (intro sequence / outro sequence) |
| Data offset | `0xada585` |
| Enter script | `0x928115` → `0x92ed4c` |
| Step-ons | 0 |
| B-triggers | 0 |
| Music | 0x4a (normal path) / 0x90 (outro path) |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 0 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | 3 NPCs on normal path (`$2837`, `$2839`, `$283b`); additional NPCs on outro path |
| Forced dog form | Alternates Regular (0x0A) / Toaster (0x0c) during outro dog-transform animation |
| Music | 0x4a (normal), 0x90 (outro) |

---

## Overview

Podunk in 1995 — serves double duty as both an **intro room** (first time the player sees the game's home town, just before 0x03) and the **outro room** (the act 4 outro scene where boy and dog return home after the adventure).

Two major paths based on `$22f1&0x40`:

1. **Outro path** (`$22f1&0x40` set): The full Act 4 ending cutscene — boy returns home and the dog rapidly alternates between Regular and Toaster forms as a comedic "back to normal" sequence. Long dialog exchange between boy and dog. Ends with CHANGE MAP → 0x03.
2. **Normal intro path** (`$22f1&0x40` clear): Podunk street scene with 3 NPCs, camera scroll, and eventually CHANGE MAP → 0x03 (Mansion Exterior 1995) after dialog.

---

## Enter Logic

**Common preamble:**
1. Teleport both to `[02, 00]`; stop music; `$23bf = 0x0001`

**Outro path** (if `$22f1&0x40`, RCALL `0x92e942`):
1. CALL `0x92a3e7` (Hide status bar); BOY+DOG = STOPPED; face south/west
2. Teleport boy to `[03, 33]`; SET BRIGHTNESS 0; stop music; PLAY MUSIC 0x90; FADE IN
3. OBJ 1 load; boy sprite `0x0188`; brightness ramp up (`$2835` 0→15)
4. CALL `0x92e763` (background animation)
5. `$284d = 0x0cc0`, `$284f = 0x0003`; advance `$284f` by 0x24; teleport boy (parachute drop loop)
6. SFX `0x34`; CALL `0x92ec33` (impact); SLEEP 29; CALL `0x92e8f4`; SLEEP 119
7. Dog transform loop (40 iterations, `$23b9` 0→39):
   - Speed `$23bb`: 1 if `$23b9<20`, 2 if `<30`, else 4
   - Toggle `$2434&0x01`: if set → CHANGE DOGGO Regular (0x0A), clear bit; else → Toaster (0x0c), set bit
   - SLEEP `$23bb`; toggle again; SLEEP `$23bb`
8. CHANGE DOGGO → Regular (0x0A); SLEEP 29
9. Dialog: **"Hi, [dog]! It's good to see that you're back to normal!"** (boy); **"Everything is normal!"** (dog)
10. Camera scroll, walk boy+dog to positions, more dialog:
    - "Good old Podunk. Nothing strange here."
    - "I wonder if that whole adventure was just a product of our overly active imaginations."
    - "Wow!"; brightness ramp; more walk/dialog
    - "I think we've got our answer!"
    - Sparkle-reveal effect (`REVEAL ENTITY??` × 20 iterations), brightness ramp-down
11. CHANGE MAP `0x03` @ `[0x0008|0x0358]` (Mansion Exterior 1995)

**Normal intro path** (if `$22f1&0x40` clear, RCALL `0x92e7c7`):
1. Load NPCs: `$2837` (NPC 20, sprite `0x012c`), `$2839` (NPC 20, sprite `0x0134`), `$283b` (NPC 20, sprite `0x012a`)
2. Check music lock; if not locked: PLAY MUSIC `0x4a`; FADE IN
3. Camera `$242b = 0x0010`, `$242d = 0x0000`; CALL `0x92de75` (cinematic); BOY+DOG = STOPPED
4. CALL `0x92e6a8` (background ABS); SLEEP 119; OBJ 0 load/unload sequence; walk boy+dog in
5. Dialog exchange between boy and dog about the adventure:
   - "What a classic! My favorite part was the battle with the slime beast in the toxic swamp."
   - "You could hardly tell that it was really a bunch of old tires and a garden hose."
   - Dog walks east; more ambient walk and turn animations
   - "Where are you going, buddy? That's not the way home!"
   - Walk/scroll sequences; "Wait for me!"
6. CHANGE MAP `0x03` @ `[0x0008|0x0358]` (Mansion Exterior 1995)

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
| `$22f1` | 0x40 | R | 📖 Inside outro — selects outro path (RCALL `0x92e942`) |
| `$23bf` | — | W | ⚙️ Set to 0x0001 on entry |
| `$238d` | — | R | ⚙️ Music lock |
| `$2443` | — | W | ⚙️ Dog form (Regular `0x0A` / Toaster `0x0c`) during outro loop |
| `$2834` | 0x01 | R/W | ⚙️ Dog-form toggle bit during outro animation loop |
| `$2835` | — | W | ⚙️ Brightness ramp counter (outro path, 0→15) |
| `$23b9` | — | W | ⚙️ Dog transform loop counter (0→39) |
| `$23bb` | — | W | ⚙️ Dog transform animation speed (1/2/4 based on `$23b9`) |
| `$284d` | — | W | ⚙️ Parachute drop X position (outro) |
| `$284f` | — | W | ⚙️ Parachute drop Y position (outro) |
| `$2845`/`$2847` | — | W | ⚙️ Sparkle reveal coords (outro) |
| `$2836` | — | W | ⚙️ NPC pointer (brightness counter reuse — outro path) |
| `$2837` | — | W | ⚙️ NPC pointer (NPC 20, normal path) |
| `$2839` | — | W | ⚙️ NPC pointer (NPC 20, normal path) |
| `$283b` | — | W | ⚙️ NPC pointer (NPC 20, normal path) |
| `$283a` | — | W | ⚙️ NPC pointer (script-local, outro path) |

---

## Notes

- This room appears twice in the game's narrative: once as an intro room (first playthrough) and once as the Act 4 outro (after defeating the final boss). The same map, same room ID, different content based on `$22f1&0x40`.
- The dog-transform animation (alternating Regular ↔ Toaster form at increasing speed) is unique to this room's outro path — 40 iterations with a speed increasing from 1 tick/frame to 4 ticks/frame.
- The parachute drop for boy in the outro uses a direct teleport loop (`$284f += 4` each frame, boy teleported to new position) — same technique used in other Act 3/4 animation rooms.
- The sparkle-reveal effect (`REVEAL ENTITY??` × 2 per frame for 20 frames) at the end of the outro path is the same effect used in 0x77 (Mungola death) and other climactic scenes.
