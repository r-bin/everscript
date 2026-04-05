# 0x7e — Omnitopia: Jail

| Key | Value |
|-----|-------|
| ROM | `0x9fffdf` |
| Data | `0xa89236` |
| Enter script | `0x9b92e1` |
| Step-ons | 1 entry @ `0xa89245` |
| B-triggers | 17 entries @ `0xa8924d` (len=0x0066) |
| Music | 0x88 |
| Dog form | Toaster (`0x0C`) — forced on every enter |
| PACIFIED | `0x0000` (enemies active) |

---

## Overview

The Jail is a wide detention block in Omnitopia, entered from the Metroplex Tunnels (0x48) and leading down to the Junkyard (0x49) via a drop hatch. It contains twelve sniff-spot loot caches spread across the cells, all pickable by the dog (`$22c2`/`$22c3` flags). The warden is a GUARD_BOT (`0x9c>>1 = 0x4e`); once defeated (`$22e7&0x01`), the player can open three prisoner cell doors by interacting with levers whose required values (`$2839`/`$283b`/`$283d`, set by the GUARD_BOT kill script) open OBJ 1/2/3. Two additional enemies (RAPTOR_TEAL 0x79 and SLIME_PINK 0x6f) patrol the east wing; OWL_GREEN (0x78) spawners appear along the centre. The east block also has a toggle light switch (OBJ 4/8). A special re-entry path (`$22f9&0x40`) handles arriving back from the Junkyard.

---

## Enter Logic

```
0x9b92e1:
  if $22eb&0x20:
    $22eb &= 0xdf
  else:
    teleport both to (0x0f, 0x27)
    CALL "Fade-out / stop music"

  WRITE CHANGE DOGGO ($2443) = Toaster (0x0C)
  WRITE $2348 = 0x0009
  WRITE $23bf = 0x0000

  // Restore sniff-spot loot state (12 flags)
  if $22c2&0x01: UNLOAD OBJ 0x0a   // Gunpowder #10
  if $22c2&0x02: UNLOAD OBJ 0x0b   // Gunpowder #11
  if $22c2&0x04: UNLOAD OBJ 0x0c   // Grease #12
  if $22c2&0x08: UNLOAD OBJ 0x0d   // Grease #13
  if $22c2&0x10: UNLOAD OBJ 0x0e   // Meteorite #14
  if $22c2&0x20: UNLOAD OBJ 0x0f   // Dry Ice #15
  if $22c2&0x40: UNLOAD OBJ 0x10   // Iron #16
  if $22c2&0x80: UNLOAD OBJ 0x11   // Iron #17
  if $22c3&0x01: UNLOAD OBJ 0x12   // Crystal #18
  if $22c3&0x02: UNLOAD OBJ 0x13   // Wax #19
  if $22c3&0x04: UNLOAD OBJ 0x14   // Brimstone #20
  if $22c3&0x08: UNLOAD OBJ 0x15   // Brimstone #21

  if CHANGE MUSIC ($238d) != 0: PLAY MUSIC 0x88

  CALL 0x9b93ed                     // load enemies / NPC sub-routine

  if !$22e7&0x01:                   // warden alive
    LOAD NPC (0x9c>>1 = 0x4e GUARD_BOT) at (0xb5, 0x18) → $2835
    SET talk script 0x1b42 for $2835
  else:                             // warden defeated
    SET OBJ 3 STATE = 0x7e
    if $2839 == 3: SET OBJ 5=0x7e; $2839 = 0
    if $283b == 3: SET OBJ 6=0x7e; $283b = 0
    if $283d == 3: SET OBJ 7=0x7e; $283d = 0

  LOAD NPC 0x79 (RAPTOR_TEAL) at (0xb5, 0x36) → $283f
  SET entity bits 0x20; kill script 0x1b45
  LOAD NPC 0x6f (SLIME_PINK) at (0x9f, 0x36) → $2841
  SET entity bits 0x20; kill script 0x1b48

  Add NPC 0x78 (OWL_GREEN) spawner at (0x16, 0x36)   // WRITE $2433=4 (×4)
  Add NPC 0x78 (OWL_GREEN) spawner at (0x7a, 0x36)

  if $22f9&0x40:
    CALL 0x9b9692                   // special re-entry from junkyard
    END

  if $22f8&0x04:
    CALL "Omnitopia hatch fade-in"
    $22f8 &= 0xfb
    END
  else:
    CALL "Some cinematic script"
    END
```

---

## Step-On Zones

| Zone (tile) | `$24fd` | Destination |
|-------------|---------|-------------|
| `[64,0c:66,0d]` | 1 | Walk to (0x0630, 0x00a0), fade-out → **CHANGE MAP 0x48** @ [0x0078, 0x0088] |

---

## B-Trigger Zones

### Sniff-Spot Loot (12 — dog only)

| Zone (tile) | Item | SRAM flag | OBJ | NEXT ADD |
|-------------|------|-----------|-----|----------|
| `[2d,15:2e,16]` | 👃 Gunpowder (#10) `[0x7e]` (0x01) | `$22c2&0x01` | OBJ 0x0a | 1 |
| `[0f,10:10,11]` | 👃 Gunpowder (#11) `[0x7e]` (0x02) | `$22c2&0x02` | OBJ 0x0b | 2 |
| `[14,13:15,14]` | 👃 Grease (#12) `[0x7e]` (0x04) | `$22c2&0x04` | OBJ 0x0c | 2 |
| `[2a,15:2b,16]` | 👃 Grease (#13) `[0x7e]` (0x08) | `$22c2&0x08` | OBJ 0x0d | 1 |
| `[3f,11:40,12]` | 👃 Meteorite (#14) `[0x7e]` (0x10) | `$22c2&0x10` | OBJ 0x0e | 3 |
| `[67,17:68,18]` | 👃 Dry Ice (#15) `[0x7e]` (0x20) | `$22c2&0x20` | OBJ 0x0f | 2 |
| `[58,0c:59,0d]` | 👃 Iron (#16) `[0x7e]` (0x40) | `$22c2&0x40` | OBJ 0x10 | 1 |
| `[4d,1c:4e,1d]` | 👃 Iron (#17) `[0x7e]` (0x80) | `$22c2&0x80` | OBJ 0x11 | 0 |
| `[60,1c:61,1d]` | 👃 Crystal (#18) `[0x7e]` (0x01) | `$22c3&0x01` | OBJ 0x12 | 1 |
| `[4d,13:4e,14]` | 👃 Wax (#19) `[0x7e]` (0x02) | `$22c3&0x02` | OBJ 0x13 | 2 |
| `[38,15:39,16]` | 👃 Brimstone (#20) `[0x7e]` (0x04) | `$22c3&0x04` | OBJ 0x14 | 1 |
| `[27,13:28,14]` | 👃 Brimstone (#21) `[0x7e]` (0x08) | `$22c3&0x08` | OBJ 0x15 | 2 |

### Functional B-triggers (5)

| Zone (tile) | Action |
|-------------|--------|
| `[08,10:0a,12]` | Drop-hatch: walk to (0x0070, 0x00e0), SET OBJ 0=0x7e, SFX 0xb0, fall animation, SET OBJ 0=0, `$22f9\|=0x08`, → **CHANGE MAP 0x49** @ [0x01f0, 0x00b0] |
| `[51,0c:52,0d]` | Light switch toggle: if `$2837==0` → SET OBJ 8=0x7e, SET OBJ 4=0x7e, `$2837=1`; else → SET OBJ 8=0, SET OBJ 4=0, `$2837=0`, SFX 0xaa |
| `[52,0c:53,0d]` | Cell A lever: based on `$2839` (1→OBJ 1, 2→OBJ 2, 3→OBJ 3) SET state=0x7e, `$2834\|=0x10/0x20/0x40`, SET OBJ 5=0x7e, `$2839=0` |
| `[53,0c:54,0d]` | Cell B lever: based on `$283b` → SET OBJ 6=0x7e, `$2834\|=...`, `$283b=0` |
| `[54,0c:55,0d]` | Cell C lever: based on `$283d` → SET OBJ 7=0x7e, `$2834\|=...`, `$283d=0` |

---

## Connections

| Direction | Destination | Condition |
|-----------|-------------|-----------|
| In | 0x48 Metroplex Tunnels | `$24fd = 1` (set by 0x48) |
| In | 0x49 Junkyard | Step-on `[26,15:28,16]` in 0x49 sets `$22f9&0x40`; enter triggers `0x9b9692` |
| Out | 0x48 Metroplex Tunnels | Step-on `[64,0c]`, `$24fd=1` |
| Out | 0x49 Junkyard | Drop-hatch B-trigger `[08,10:0a,12]`, sets `$22f9&0x08` |

---

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22c2` | `0x01` | 👃 | Sniffed Gunpowder (#10) `[0x7e]` (0x01) |
| `$22c2` | `0x02` | 👃 | Sniffed Gunpowder (#11) `[0x7e]` (0x02) |
| `$22c2` | `0x04` | 👃 | Sniffed Grease (#12) `[0x7e]` (0x04) |
| `$22c2` | `0x08` | 👃 | Sniffed Grease (#13) `[0x7e]` (0x08) |
| `$22c2` | `0x10` | 👃 | Sniffed Meteorite (#14) `[0x7e]` (0x10) |
| `$22c2` | `0x20` | 👃 | Sniffed Dry Ice (#15) `[0x7e]` (0x20) |
| `$22c2` | `0x40` | 👃 | Sniffed Iron (#16) `[0x7e]` (0x40) |
| `$22c2` | `0x80` | 👃 | Sniffed Iron (#17) `[0x7e]` (0x80) |
| `$22c3` | `0x01` | 👃 | Sniffed Crystal (#18) `[0x7e]` (0x01) |
| `$22c3` | `0x02` | 👃 | Sniffed Wax (#19) `[0x7e]` (0x02) |
| `$22c3` | `0x04` | 👃 | Sniffed Brimstone (#20) `[0x7e]` (0x04) |
| `$22c3` | `0x08` | 👃 | Sniffed Brimstone (#21) `[0x7e]` (0x08) |
| `$22e7` | `0x01` | 📖 | Warden defeated — enables prisoner cell lever interactions |
| `$22f8` | `0x04` | ⚙️ | Hatch-entry flag; cleared after fade-in |
| `$22f9` | `0x08` | ⚙️ | Dropped to junkyard via hatch (set on B-trigger exit) |
| `$22f9` | `0x40` | ⚙️ | Re-entered from junkyard — triggers special `0x9b9692` path |
| `$2834` | `0x10` | ⚙️ | Prisoner cell A opened |
| `$2834` | `0x20` | ⚙️ | Prisoner cell B opened |
| `$2834` | `0x40` | ⚙️ | Prisoner cell C opened |
| `$2835` | — | ⚙️ | GUARD_BOT warden entity handle |
| `$2837` | — | ⚙️ | Light switch state (0=off, 1=on) |
| `$2839` | — | ⚙️ | Cell A lever code (1/2/3 → which OBJ opens); cleared after use |
| `$283b` | — | ⚙️ | Cell B lever code; cleared after use |
| `$283d` | — | ⚙️ | Cell C lever code; cleared after use |
| `$283f` | — | ⚙️ | RAPTOR_TEAL entity handle |
| `$2841` | — | ⚙️ | SLIME_PINK entity handle |

---

## Object List

| OBJ | Purpose |
|-----|---------|
| 0 | Drop-hatch lid (SET 0x7e = open, SET 0 = closed during fall animation) |
| 1 | Prisoner cell door A (opened when `$2839` lever matches) |
| 2 | Prisoner cell door B |
| 3 | Prisoner cell door C (SET 0x7e when warden defeated) |
| 4 | East block ceiling light (toggle via `$2837`) |
| 5 | Prisoner cell A state (SET 0x7e after lever) |
| 6 | Prisoner cell B state |
| 7 | Prisoner cell C state |
| 8 | East block light switch OBJ (toggle pair with OBJ 4) |
| 9 | Unknown |
| 0x0a–0x15 | Sniff-spot loot items 10–21 (unloaded when corresponding flag set) |

---

## Notes

- The 12 sniff-spot items are the richest single-room ingredient cache in Omnitopia: Gunpowder, Grease, Meteorite, Dry Ice, Iron, Crystal, Wax, and Brimstone. All require the dog (Toaster) to sniff.
- The warden GUARD_BOT (`0x9c>>1 = 0x4e`, talk script 0x1b42) presumably has a kill script that sets `$22e7|=0x01` and assigns codes 1/2/3 to `$2839`/`$283b`/`$283d` (determining which OBJ lever opens which cell).
- The prisoner cell lever values (1/2/3) determine which of OBJ 1/2/3 each lever opens. This is set by the warden kill script and is likely randomized or fixed. Once a lever is used, its variable is cleared to 0.
- The "light switch" toggle (OBJ 4/8) at `[51,0c]` affects only the east block illumination — distinct from the room-wide `$22e6&0x40` flag used in 0x44 (Greenhouse).
- RAPTOR_TEAL (`0x79`, "Raptor", enemy #136) and SLIME_PINK (`0x6f`, "Red Jelly Ball", enemy #61) are loaded unconditionally — they always respawn. OWL_GREEN (`0x78`, "Neo Greeble", enemy #66) spawns in two groups of 4.
- `$22f9&0x40` re-entry path calls `0x9b9692` — this is triggered when returning from the Junkyard (0x49) via the step-on there. The special path likely positions the player at the jail hatch origin rather than the default spawn.
