# 0x6a — Act 2 Start Cutscene - Waterfall

**ROM:** `0x9fff8f` | **Data:** `0xac88e1` | **Enter:** `0x92822d` → `0x94e8a6`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x64` (WindWalker flight theme, continued from 0x53) |
| Map bounds | Small vertical map |
| NPCs | 0 |
| Step-on zones | 0 |
| B-triggers | 0 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| End of cutscene | `0x68` Crustacia exterior @ `[0x0170\|0x0320]` | scripted | Sets `$22ed\|=0x08` before warping |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22eb` | `0x20` | ⚙️ | Animation-skip flag (standard entry guard) |
| `$22ed` | `0x08` | 📖 | Crustacia intro to be shown (set here before entering Crustacia) |
| `$2288` | `0x04` | 📖 | Received Petal or Honey in Fire Eyes' Village huts (cleared here) |
| `$225f` | `0x80` | 📖 | Village post-Thraxx message shown (cleared here) |
| `$22fa` | full byte | ⚙️ | Set to `0x10` on entry (screen effect parameter?) |
| `$22fb` | full byte | ⚙️ | Set to `0x14` on entry (screen effect parameter?) |

## Enter Script Summary

1. `$22eb&0x20` guard; default teleport to `(0x0b, 0x0b)`; stop music.
2. Teleport both to `(0x00, 0x11)`.
3. `$23bf=1`; play music `0x64`; `$22fa=0x10`; `$22fb=0x14`.
4. Call cinematic script `0x92de75`.
5. BOY+DOG STOPPED.
6. **Waterfall fall animation** (RCALL `0x94e7e1`):
   - Start positions: boy at `($24cf-10, $24d1)`, dog at `($24cf+20, $24d1+2)` where `$24cf=0x0088`, `$24d1=0x0440`.
   - Both face south; sprite walk animations applied.
   - **Fall loop**: while boy/dog Y < `$24d1` (0x0440): teleport both incrementing Y by 3 each YIELD.
   - At iteration 0x012c: `Fade-out screen`.
   - After loop: `$238f=0`; idle sprites.
7. Set `$22ed|=0x08` (crustacia intro to be shown).
8. Clear `$2288&=~0x04` (forget FE Village hut gift flag).
9. Clear `$225f&=~0x80` (forget post-Thraxx message flag).
10. CHANGE MAP = 0x68 @ `[0x0170|0x0320]`.

## Notes

- **Pure cutscene — no player interaction.** Boy and dog fall off the WindWalker into a waterfall, plunging downward until fade-out.
- **`$22ed&0x08` = "crustacia intro to be shown"** — this flag is consumed in 0x68 to trigger the first-time Crustacia intro event.
- **`$2288&0x04` and `$225f&0x80`** are cleared here as "clean slate" flags when transitioning from Act 1. They control content shown in Prehistoria that doesn't apply in Antiqua.
- The fall animation starts at Y=0x0440 (far below the screen bottom) and goes even further — the camera does not follow; the screen fades out at frame 0x012c.
- **Music `0x64`** continues from 0x53 with no break, making rooms 0x53 + 0x6a a seamless cinematic sequence.
