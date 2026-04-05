# [0x64] Antiqua — Cave Entrance Under 'mids

## Header

| Field | Value |
|-------|-------|
| Room ID | 0x64 |
| Act | Antiqua (Act 2) |
| Data | `0xadb0aa` |
| Enter script ptr | `0x92820f` → `0x97de4a` |
| Step-on table | `0xadb0b9`, len=0x000c (2 entries) |
| B-trigger table | `0xadb0c7`, len=0x0000 (0 entries) |
| Music | 0x44 |
| Dog | Greyhound |

## Overview

Short cave passage connecting Outside of 'mids (0x06) to the 'mids basement level (0x57). Contains a pit/hole in the floor used to enter 0x57 via a fall animation. When returning from 0x57, an emergence animation plays (characters climb out of the hole).

## Memory Access

| Address | Bits | R/W | Description |
|---------|------|-----|-------------|
| `$22eb` | 0x20 | R/W | ⚙️ IN_ANIMATION — entry teleport guard |
| `$238d` | — | R | 🎵 CHANGE_MUSIC flag |
| `$238f` | — | R/W | ⚙️ TRANSITION_ENTER_DIRECTION — value 5 = returning from 0x57 basement |

## Enter Script Summary (`0x97de4a`)

1. **Entry guard**: if `$22eb&0x20`: teleport both to [0x15,0x1b] + fade; else clear flag.
2. CHANGE DOGGO = Greyhound (0x06).
3. `$0ea2+0=0x40`, `$0eac+0=0x172b` (talk script assignment, unknown).
4. **Enemy drops**: PRIZE1=0x0801 (rate 10); PRIZE2=0x0001 qty 0x46 (rate 3); PRIZE3=0x0802 (rate 1).
5. **NPCs**: LOAD NPC 0x6e at [0x0b,0x1b]; [0x10,0x12]; [0x21,0x1b].
6. **Music**: if `$238d != 0`: PLAY MUSIC 0x44; fade in.
7. **Emergence animation** (if `$238f == 5`, returning from 0x57):
   - LOAD NPC 0x20 at [0x00,0x00] → stored to arg0.
   - Teleport boy, dog, and NPC to [0x12,0x17].
   - Boy and NPC animate (sound 0x36; NPC exits frame); boy walks by [1,2], faces south.
   - Dog and NPC animate (sound 0x36; NPC exits frame); dog walks by [-1,2], faces south.
   - DESTROY NPC. BOY+DOG = Player controlled. END.
8. **Otherwise**: call global `0x92de75` (generic cinematic/fade-in script). BOY+DOG = Player controlled.

## Step-on Scripts (2 entries)

| Tile | Script | Description |
|------|--------|-------------|
| [0b,12:0e,13] | `0x97de40` | **EXIT south → 0x06** (Outside of 'mids) at [0x0438,0x0420] |
| [0c,0a:0f,0c] | `0x97ddc7` | **ENTER 'mids basement → 0x57** — walk to [0x17,0x12]; fall animation with NPC 0x20; set `$22eb\|=0x20`; WRITE `$238f=5`; fade out; call global 0x2e; CHANGE MAP 0x57 @ [0x0408,0x02e8] |

## Exits

| Destination | Trigger | Player Spawn |
|-------------|---------|--------------|
| 0x06 Outside of 'mids | Step-on [0b,12:0e,13] | [0x0438, 0x0420] |
| 0x57 'mids basement | Step-on [0c,0a:0f,0c] | [0x0408, 0x02e8] |

## B-Triggers

None.

## NPCs

| NPC | Type | Load Condition | Pos | Notes |
|-----|------|----------------|-----|-------|
| NPC 0x6e | Unknown enemy | Always (enter script) | [0x0b,0x1b] | One of three spawned |
| NPC 0x6e | Unknown enemy | Always (enter script) | [0x10,0x12] | |
| NPC 0x6e | Unknown enemy | Always (enter script) | [0x21,0x1b] | |
| NPC 0x20 | Prop/chute | Step-on only | [0x17,0x12] | Used for fall/emerge animation; destroyed after |

## Notes

- **`$238f=5`** is written by the step-on going to 0x57 and read back on re-entry to trigger the emergence animation. This is a two-way animation handshake.
- No B-triggers. Shortest room in this act.
