# Room 0x77 — Gothica: Ivor Tower Puppet Show / Mungola

| Field | Value |
|-------|-------|
| **Room ID** | 0x77 |
| **Act** | 3 — Gothica |
| **Data** | `0x9fffc3` |
| **Enter script** | `0x92826e` → `0x9a8bff` |
| **Dog sprite** | Poodle (`$2443=0x08` on enter) |
| **Music** | 0x58 (Sterling alive) / 0x5a (Sterling dead / post-fight) |
| **Step-ons** | 3 entries |
| **B-triggers** | 0 entries |
| **Connections** | 0x78 (Ivor Tower Queen's Room, 2 exits east) |

---

## Overview

The puppet show theater and Mungola boss arena. The room has two major paths based on story state:

1. **Mungola boss fight path** (`!($22dc&0x08) && ($22dd&0x02)` — windwalker NOT unlocked AND Sterling dead): Full Mungola battle sequence. Includes:
   - Opening cutscene with Sterling and the Queen
   - Two-phase puppet fight (Mephista × Mungola, both phases)
   - On death: elaborate light-show destruction sequence
   - Sterling reward: 10,000 Gold Coins
   - Sets `$22ee|=0x80`; transitions to 0x78 (Queen's Room)

2. **Puppet show viewing path** (all other states): Loads Sterling and two puppet NPCs, plays ambient dialogue about the puppet show. Records game timer in `$284f`. Runs the puppet show management script (0x9a8870). Sets `$2834|=0x04` (viewing flag) and `$2834|=0x02`.

Debug mode (`$22eb&0x08`) forces `$22dd|=0x02` (Sterling dead) on entry.

---

## Enter Logic

1. Set scroll limits: `$2413=0x0088`, `$240f=0x0058`, `$2411=0x0058`
2. If NOT `$22eb&0x20`: if debug → `$22dd|=0x02`. Teleport both to `[1e,25]`; fade music
3. If `$22eb&0x20`: clear in-animation flag
4. `$2443 = 0x08` (Poodle)
5. If music not locked:
   - If `$22dd&0x02` (Sterling dead): PLAY MUSIC 0x5a
   - Else: PLAY MUSIC 0x58
   - Fade in
6. If `$22dc&0x08` (windwalker unlocked): load multiple OBJ states for post-fight room layout (OBJ 5/6/7/9/10/11/12/13)
7. **If `!($22dc&0x08) && ($22dd&0x02)`** (Mungola fight path):
   - `$23bf = 0x0000`; stop party
   - Unload OBJ 14 (blocking object)
   - Load Sterling NPC (0x40>>1) at `[30,11]` → `$2835`; sprite 0x00fe
   - Load Queen NPC (0x96>>1) at `[05,15]` → `$2837`; script control
   - Teleport both to `[39,24]`; walk west 13+13 tiles; wait; sleep 29 ticks
   - **"Puppet Show [1] Fight"** setup (RCALL 0x9a845c): move camera to focus on stage
   - Queen dialog: *"I'll get you, you little pest! And that mangy cur, too!"*
   - Boy+dog walk to `[1c,23]` and `[20,23]`; sleep 119 ticks; player control
   - `$283d = 0x0001` (phase 1 combat flag)
   - Load Mephista (NPC 0x67) at `[29,23]` → `$2839`; set damage/kill script 0x1a82
   - Load Mungola (NPC 0x68) at `[13,23]` → `$283b`; set damage/kill script 0x1a82
   - Run "Show of Life" script (0x9a848d); fight loop until one puppet dies
   - `$283d = 0x0002` (phase 2 flag); unload OBJ 13
   - Load Phase 2: new Mephista at `[23,0f]` → `$2839`; new Mungola at `[19,0f]` → `$283b`; Mungola NPC 0x6c at `[1e,09]` → `$283f`; set Mungola's damage script 0x1a85
   - Fight loop phase 2:
     - If windwalker unlocked: skip combat (jump to finish)
     - While alive: random spells cast on boy+dog; Mephista can heal Mungola for 20–83 HP (showing "Mephista heals Mungola!" if triggered)
   - **Death sequence**: destroy Mephista+Mungola; spawn 6 temporary NPC 0x14 at `[1a,0e]` (explosion particles); toggle random OBJ states in loop; flash music
   - Flash white (`$22eb|=0x01`, 0x92d723); reload OBJ 5/6/7/9/10/11/12
   - Fade music out; play victory fanfare (0x36); hold up weapon (0x92bf33); sleep 239 ticks
   - Return to MUSIC 0x58; sprite animation reset
   - Walk controlled char to `[15,26]`, non-controlled to `[15,26]`; Queen shakes head
   - Load new Sterling NPC (0x36>>1, "Eronio") at `[39,24]` → `$2835`
   - Interpolation: teleport `$2835` from offscreen-east to `[*(boy+26)+0x20, *(boy+28)]`
   - Queen walks to `[15,26]`; tilt camera; second interpolation for Sterling → final pos
   - Sterling: *"Here, lad! Take this for your troubles!"* → give **10,000 Gold Coins**
   - `$22ee |= 0x80`; OBJ 14 → state 0; Sterling: *"Follow me! I think her majesty has damaged the foundation!"*
   - Set volume 0x96; screen shake (magnitude 1,1); infinite chase camera
   - Escort walk (boy+dog+Sterling) to `[39,24]`; fade screen out; `$22eb|=0x20`
   - CHANGE MAP → 0x78 `[0018, 01a8]` (Ivor Tower Queen's Room)
8. **Else** (puppet show viewing path — RCALL 0x9a8aea):
   - `$2834 |= 0x04`
   - Load Sterling (0x40>>1) at `[30,11]` → `$2835`; script control; talk script 0x1a88
   - Load two puppet NPCs: NPC 0xce>>1 at `[23,04]` → `$283b` (sprite 0x00ec), NPC 0xd0>>1 at `[1b,15]` → `$2839` (sprite 0x00f6)
   - `$23bf = 0x0001`; cinematic call
   - If `$22f5&0x10` not yet set:
     - `$22f5 |= 0x10` (one-shot guard)
     - If `$234b == 0x30` (from north entrance): walk characters 10+4 tiles west; face north; yield
     - Else: walk 2+1 tiles
     - Show dialog: *"Look [dog name]! A puppet show."*
     - If `$234b == 0x30`: move north; show: *"This reminds me of the classic, Memphis Topples Leaves."*
   - Record `$284f = GameTimer & 0xffff`; `$234b = 0x0000`
   - Call puppet show management script (0x9a8870)
   - `$2834 |= 0x02`; yield; END

---

## Step-On Table

| Tile(s) | Action |
|---------|--------|
| `[36,37:3a,38]` | **Puppet-watch / puppet-attack**: if `$2834&0x04` (currently watching): stop, show *"Can't see! Down in front!"* (0x1d1f), clear `$2834&0x04`, set `$2834\|=0x02`, sleep. Else if `$283d==1` (phase 1 fight): script-controls player, teleports Mephista or Mungola to player position, deals 18+ (RAND & 7) damage, walks puppet back. |
| `[44,33:46,36]` | Fade out; → 0x78 `[0018, 00d0]` (Ivor Tower Queen's Room, upper exit) |
| `[44,3b:46,3d]` | Fade out; → 0x78 `[0018, 01a8]` (Ivor Tower Queen's Room, lower exit) |

---

## Cutscene Dialog Reference

| Speaker | Text |
|---------|------|
| Queen (0x1d8b) | *"I'll get you, you little pest! And that mangy cur, too!"* |
| Text 0x1d8e | `"Mephista heals Mungola!"` (unwindowed) |
| Queen (0x1d91) | *"I don't believe it! You've dispatched Mungola! Come closer, that I may give you your just reward!"* |
| Queen (0x1d94) | *"Take this, little man, for what you have done!"* |
| Queen (0x1d97) | *"I meant to do that..."* |
| Boy (0x1d9a) | *"Look, [dog name], a gear… I'm beginning to think that queen was no lady…"* |
| Sterling (0x1d9d) | *"Here, lad! Take this for your troubles!"* |
| Sterling (0x1da3) | *"Follow me! I think her majesty has damaged the foundation!"* |
| Boy (0x1d85) | *"Look [dog name]! A puppet show."* |
| Boy (0x1d88) | *"This reminds me of the classic, Memphis Topples Leaves."* |

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$22eb` | 0x08 | R | Debug mode |
| `$22eb` | 0x01 | W | Flash effect flag (set during Mungola death) |
| `$22dc` | 0x08 | R/W | 📖 Windwalker unlocked |
| `$22dd` | 0x02 | R | 📖 Sterling dead |
| `$22ee` | 0x80 | W | 📖 Mungola defeated (triggers collapse in 0x78) |
| `$22f5` | 0x10 | R/W | 📖 Puppet show dialog seen (one-shot) |
| `$234b` | byte (low) | R/W | Entry source (0x30/0x31 = from Queen's Room exits) |
| `$238d` | word | R | Music lock |
| `$2443` | word | W | Dog sprite (Poodle) |
| `$23bf` | word | W | Unknown |
| `$240f/$2411/$2413` | word | W | ⚙️ Scroll limit registers |
| `$2409/$240b` | word | W | Screen shake magnitude |
| `$2834` | 0x02 | R/W | ⚙️ Puppet show running flag |
| `$2834` | 0x04 | R/W | ⚙️ Puppet show viewing in progress |
| `$2835` | word | W | Sterling / Eronio NPC pointer |
| `$2837` | word | W | Queen NPC pointer |
| `$2839` | word | W | Mephista NPC pointer |
| `$283b` | word | W | Mungola NPC pointer (also puppet NPC in viewing mode) |
| `$283d` | word | R/W | ⚙️ Combat phase (0=none, 1=phase1, 2=phase2, 3=Mungola full fight) |
| `$283f` | word | W | Mungola boss NPC pointer (phase 2) |
| `$284f` | word | W | Game timer snapshot (puppet show start time) |

## Notes

- Mungola's boss fight only triggers if WindWalker is NOT unlocked AND Sterling is dead (`!($22dc&0x08) && ($22dd&0x02)`); all other states lead to the ambient puppet show viewing path.
- The boss fight is two-phased: Mephista puppet fight first (`$283d=1`), then full Mungola battle (`$283d=3`); death triggers an elaborate light-show destruction sequence before room transition.
- `$22ee&0x80` (Mungola defeated) is written here and read by 0x78 on the next entry to trigger the castle collapse cutscene — the bridge flag between the two rooms.
- Debug mode (`$22eb&0x08`) forces `$22dd|=0x02` (Sterling dead) on entry, bypassing directly to the boss path.
