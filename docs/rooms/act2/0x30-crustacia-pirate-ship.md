---
room: 0x30
name: Antiqua – Crustacia Inside Pirate Ship
act: act2
data: 0xaaa4f5
---

# 0x30 — Antiqua – Crustacia Inside Pirate Ship

| Field | Value |
|-------|-------|
| Room ID | 0x30 |
| Full Name | Antiqua – Crustacia Inside Pirate Ship |
| Act | 2 (Antiqua) |
| Data block | 0xaaa4f5 |
| Enter script | 0x92810b → 0x95c174 |
| Step-on table | 0xaaa504 (8 entries, 0x30 bytes) |
| B-trigger table | 0xaaa536 (7 entries, 0x2a bytes) |

## Overview

The interior of the pirate ship docked in Crustacia. One large map with 5 distinct sections (determined by `$234c` 1–5), each with its own camera bounds and NPC population:

| `$234c` | Section | Entry from 0x68 |
|---------|---------|-----------------|
| 1 | North cabin — NPC 0x1c (one named character) | [28,2b:2b,2c] |
| 2 | Mid-south area — 1 guard NPC | [4b,3b:4e,3c] |
| 3 | Mid area — 1 guard NPC | [37,37:39,38] |
| 4 | Captain's quarters — many NPCs (captain + crew) | [38,45:3a,46] |
| 5 | Upper north cabin — 1 guard NPC | [44,2b:47,2c] |

Section 4 uses music 0x5c (dramatic theme); all others use 0x2c (town). A Monk at section 1 sells an **Amulet of Annihilation** for 10,000 Jewels (via step-on tiles). 6 gourds are distributed across sections; the 7th B-trigger is a dialog NPC.

Dog is set to Greyhound. Dog is hidden/disabled if unavailable or `$2350 != 0`.

## Memory Access

| Address | Access | Value | Notes |
|---------|--------|-------|-------|
| `$226b` | R/W | &0x04–0x80 | Gourd persistence flags (6 gourds, see B-triggers); enter script unloads objs 1–6 based on these bits |
| `$22eb` | R/W | &0x20 | IN_ANIMATION routing — teleport to [0x0f, 0x1d] if set; cleared otherwise |
| `$22ee` | R/W | &0x01 | Arena return flag — if set in section 1 (`$234c==1`): clear flag; teleport boy to [0x24,0x19] facing east, dog to [0x24,0x1d] facing west |
| `$234c` | R | &0x00–0x05 | Entry section identifier — set by 0x68 step-ons; determines camera bounds + NPC population |
| `$2350` | R | (byte) | Dog staircase state — if != 0, dog is hidden/disabled on entry |
| `$2443` | write | =0x06 | CHANGE DOGGO to Greyhound on room entry |
| `$2848` | R/W | — | Monk proximity counter — incremented each time player walks near Monk whisper tile |
| `$2260` | R/W | &0x80 | Crustacia indoors shop flag — toggled by Monk interaction; gates Monk greeting vs. sales dialog |

## Enter Script Summary (`0x95c174`)

1. `CHANGE DOGGO = Greyhound (0x06)`.
2. If `$22eb&0x20`: teleport to [0x0f, 0x1d] + fade music; else clear flag.
3. Unload persistence: `$226b&0x04`→OBJ 3, `$226b&0x08`→OBJ 1, `$226b&0x10`→OBJ 6, `$226b&0x20`→OBJ 5, `$226b&0x40`→OBJ 4, `$226b&0x80`→OBJ 2.
4. **Section branching** by `$234c`:
   - **1**: bounds [0,0–0x170,0x150]; NPC 0x1c at [0x19,0x19]→`$284e`, talk 0x18db; if `$22ee&0x01`: clear it + position boy/dog at [0x24,0x19/0x1d].
   - **2**: bounds [0,0x1c0–0x130,0x2e0]; NPC 0x4e (guard) at [0x0f,0x51]→`$284a`, talk 0x18de.
   - **3**: bounds [0x190,0x1b0–0x2b0,0x290]; NPC 0x4e at [0x41,0x47]→`$284c`, talk 0x18e1.
   - **4**: bounds [0x2c0,0x180–0x430,0x270]; loads NPC 0x5a>>1 (→`$2834`, talk 0x18c0), NPC 0x5c>>1 (→`$2836`, talk 0x18c3), NPC 0x5e>>1 (→`$283a`, talk 0x18c6), NPC 0x60>>1 (→`$283c`, talk 0x18c9), NPC 0x40>>1 (→`$2842`, talk 0x18cc), NPC 0x5e>>1 (→`$2844`, talk 0x18cf), 2× NPC 0x4e>>1 (talks 0x18d2, 0x18d5) — all script-controlled.
   - **5**: bounds [0x200,0–0x330,0x120]; NPC 0x4e at [0x51,0x15], talk 0x18d8.
5. Music: 0x5c if `$234c==4`; else 0x2c.
6. `$23bf = 1`.
7. If dog unavailable or `$2350 != 0`: hide dog, call sub 0x36, stop dog.

## Step-on Scripts (8 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [29,0c:2a,10] | `0x95c01e` | **Monk shop (Amulet of Annihilation)** — if boy controlled and not in dialog: if `$2848>0` and not `$2260&0x80`: "I can offer you this Amulet of Annihilation for 10,000 Jewels."; else first-time: full greeting; purchase via sub 0x95c0c4; NPC unload via sub 0x95c0b3. Sets `$2260\|=0x80` after sale. |
| [2f,0d:30,0e] | `0x95bfdc` | **Monk whisper tile A** — if boy near and no prior contact: show unwindowed "Pssst_ over here."; increment `$2848` |
| [31,0e:32,0f] | `0x95bfdc` | **Monk whisper tile B** — if `$2848==1` and `$2260&0x80` not set: show unwindowed "Over here. Near the big box."; increment `$2848` |
| [0a,18:0d,19] | `0x95bcb2` | **EXIT south** → 0x68 at [0x0098, 0x0068]; clears `$2350` if 1 or 2 |
| [3a,2c:3d,2d] | `0x95bce9` | **EXIT south** → 0x68 at [0x0190, 0x0200]; SET AUDIO 0xff restore |
| [26,2c:29,2d] | `0x95bcdf` | **EXIT south** → 0x68 at [0x0180, 0x0120] |
| [0a,31:0d,32] | `0x95bcd5` | **EXIT south** → 0x68 at [0x02c8, 0x0168] |
| [2a,15:2d,16] | `0x95bcf4` | **EXIT south** → 0x68 at [0x0258, 0x0068]; clears `$2350` if 1 or 2 |

## Exits

| Tiles | Destination | Coordinates | Notes |
|-------|-------------|-------------|-------|
| [0a,18:0d,19] | 0x68 — Crustacia exterior | [0x0098, 0x0068] | step-on |
| [3a,2c:3d,2d] | 0x68 — Crustacia exterior | [0x0190, 0x0200] | step-on |
| [26,2c:29,2d] | 0x68 — Crustacia exterior | [0x0180, 0x0120] | step-on |
| [0a,31:0d,32] | 0x68 — Crustacia exterior | [0x02c8, 0x0168] | step-on |
| [2a,15:2d,16] | 0x68 — Crustacia exterior | [0x0258, 0x0068] | step-on |

## B-Triggers (7 entries)

| Tile | Script | Contents | Flag |
|------|--------|----------|------|
| [13,0f:15,11] | `0x95bc16` | 🫙 Gourd MAP REF 0x03 looted (Water) | `$226b&0x04` |
| [2d,0a:2f,0c] | `0x95bc98` | 🫙 Gourd MAP REF 0x02 looted (Nectar) | `$226b&0x80` |
| [30,0c:32,0e] | `0x95bc30` | 🫙 Gourd MAP REF 0x01 looted (Clay) | `$226b&0x08` |
| [06,29:08,2b] | `0x95bc7e` | 🫙 Gourd MAP REF 0x04 looted (Nectar) | `$226b&0x40` |
| [3b,21:3d,22] | `0x95bc4a` | 🫙 Gourd MAP REF 0x06 looted (Wax) | `$226b&0x10` |
| [26,24:28,25] | `0x95bc64` | 🫙 Gourd MAP REF 0x05 looted (Water) | `$226b&0x20` |
| [33,25:35,26] | `0x95bd7d` | 📖 Dialog NPC — "You're not after treasure and riches like the rest of these louts... The last thing we need is more adventurers around here." | — (no persistence) |

## NPCs

| NPC | Qty | Spawn | Section | Notes |
|-----|-----|-------|---------|-------|
| NPC 0x1c | 1 | [0x19, 0x19] | 1 | Talk script 0x18db; stored in `$284e` |
| NPC 0x4e>>1 (guard) | 1 | [0x0f, 0x51] | 2 | Talk 0x18de; stored in `$284a` |
| NPC 0x4e>>1 (guard) | 1 | [0x41, 0x47] | 3 | Talk 0x18e1; stored in `$284c` |
| NPC 0x5a>>1 (captain?) | 1 | [0x6b, 0x3f] | 4 | Talk 0x18c0; `$2834` |
| NPC 0x5c>>1 | 1 | [0x6f, 0x3f] | 4 | Talk 0x18c3; `$2836` |
| NPC 0x5e>>1 | 2 | [0x63,0x46]/[0x6d,0x42] | 4 | Talks 0x18c6/0x18cf; `$283a`/`$2844` |
| NPC 0x60>>1 | 1 | [0x67, 0x46] | 4 | Talk 0x18c9; `$283c` |
| NPC 0x40>>1 | 1 | [0x5f, 0x40] | 4 | Talk 0x18cc; face south; `$2842` |
| NPC 0x4e>>1 (guard) | 2 | [0x61,0x49]/[0x71,0x47] | 4 | Talks 0x18d2/0x18d5 |
| NPC 0x4e>>1 (guard) | 1 | [0x51, 0x15] | 5 | Talk 0x18d8 |

## Notes

- **Section 4 captain's quarters**: Loaded with the most NPCs; music 0x5c (pirate/dramatic theme). This is likely where the main pirate story interaction occurs. NPC 0x5a>>1 (identity unresolved — possibly a pirate captain or Salabog) is the central character.
- **`$22ee&0x01` teleport**: Used in section 1 on re-entry after the Arena — teleports boy/dog to [0x24,0x19/0x1d] instead of the default spawn. This is the same flag that governs Arena return in [0x1e]; the pirate ship re-entry use is a second context.
- **Monk Amulet shop**: Located in section 1 at step-on tiles [29,0c:2a,10]. The "Pssst" whisper sequence at [2f,0d] / [31,0e] leads the player to the Monk. Purchase sub 0x95c0c4 handles the 10,000-jewel transaction. NPC unload sub 0x95c0b3 removes the Monk post-sale.
- **`$226b` byte**: Fully mapped — `$226b&0x01-0x02` = [0x4f] East of Crustacia gourds; `$226b&0x04-0x80` = [0x30] pirate ship gourds.
- // TODO: Identify NPC 0x5a>>1 (section 4 captain), NPC 0x1c (section 1), NPC 0x5c/0x5e/0x60/0x40 identity.
- // TODO: Read sub 0x95b2ca (Blimp's cave dialog pt. 2) and 0x95c0c4 (Monk Amulet purchase) for completeness.
