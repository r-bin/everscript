# [0x61] Misc — Opening: Scrolling over Machine

| Field | Value |
|-------|-------|
| Room ID | 0x61 |
| Name | Opening - Scrolling over Machine |
| Act | Misc (intro sequence) |
| Data offset | `0xa8b3a9` |
| Enter script | `0x928200` → `0x92e0ca` |
| Step-ons | 0 |
| B-triggers | 0 |
| Music | 0x06 |

---

## Statistics

| Metric | Value |
|--------|-------|
| Step-on triggers | 0 |
| B-triggers | 0 |
| Gourds | 0 |
| Sniff spots | 0 |
| Enemies | — |
| NPCs | 3 anonymous NPC 20 entities (particle/reveal effect, script-local only) |
| Forced dog form | — |
| Music | 0x06 |

---

## Overview

The very first room the game enters — an unskippable (unless Start is held) cinematic panning over the Omnitopia Machine. A camera scrolls toward the Machine while a large particle-burst reveal effect assembles it on screen. This is a pure scripted animation room with no player interaction: no step-ons, no B-triggers, no persistent state beyond flags in `$22ea`/`$22eb`.

The room auto-chains to 0x31 (Intro - Podunk 1965) after END — the transition is handled at the engine level, not by a CHANGE MAP in the script.

---

## Enter Logic

1. `$22eb &= 0xfb` (clear showcase bit 0x04)
2. `$22ea |= 0x08`; `$22ea &= 0xdf`
3. If `$22eb&0x02` (Start pressed in intro): SKIP to `0x92e3a4` (fast-path to end)
4. CALL `0x92a3e7` (Hide status bar); BOY+DOG = STOPPED
5. `$242b = 0x0000`, `$242d = 0x0210`; PLAY MUSIC 0x06; VOLUME 0xff
6. Teleport both to `[$242b - 0x32, $242d]`
7. Begin scroll loop: camera moves toward target (`$2401`/`$2405`); YIELD each frame
8. At midpoint (`$22ea&0x20`): fade, set OBJ 0 state, shift `$242b = 0x0200`; wait; UNTRACED (VRAM)
9. Once scroll reaches target: load 3 anonymous NPC 20 entities for particle burst
10. Particle reveal loop: `REVEAL ENTITY??` × 3 per frame; decrement counter; YIELD
11. `$2834 = 0x0000` (during scroll) → `$2834 = 0x0001` (machine revealed)
12. OBJ 1 unload/reload; sleep; position NPC 12 above Machine; UNTRACED sprite
13. Zoom sequence: `$92e2d3`–`$92e36e` — NPC 12 scales toward camera and away × 2
14. `$22ea |= 0x10`; SLEEP 479 TICKS; `$22eb |= 0x04` (set showcase flag)
15. Fade-out, FADE OUT VOLUME, SLEEP; Show status bar (`0x92a3ed`)
16. `$22ea |= 0x20`; `$22ea |= 0x10`; END

**Fast path** (skip target `0x92e3a4`, reached if `$22eb&0x02` or `$22ea&0x20`):
- `$22ea |= 0x20`; `$22ea |= 0x10`; END

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
| `$22eb` | 0x02 | R | ⚙️ Start pressed in intro — skip animation if set |
| `$22eb` | 0x04 | R/W | ⚙️ Showcase mode — cleared on entry (`&= 0xfb`), re-set at end of animation |
| `$22ea` | 0x08 | W | ⚙️ Set on entry |
| `$22ea` | 0x20 | R/W | ⚙️ Scroll completed flag — set at end; also checked at fast-path entry |
| `$22ea` | 0x10 | W | ⚙️ Set at animation end |
| `$2834` | — | W | ⚙️ Animation phase: 0x0000 = scrolling, 0x0001 = machine revealed |
| `$242b` | — | W | ⚙️ Camera scroll X target |
| `$242d` | — | W | ⚙️ Camera scroll Y target |
| `$242f` | — | W | ⚙️ Camera scroll speed |

---

## Notes

- A pure scripted cinematic — no player interaction. The only in-script "branching" is the Start-pressed skip (`$22eb&0x02`) which jumps directly to the END sequence.
- `$22eb&0x04` (showcase mode) is cleared at the top of the script and re-set after the full animation completes, enabling the showcase cycle for subsequent intro rooms.
- `$2834` is used as a purely session-local animation phase counter here — not persistent.
- The room auto-chains to 0x31 (Podunk 1965) at the engine level; there is no CHANGE MAP in this room's script.
