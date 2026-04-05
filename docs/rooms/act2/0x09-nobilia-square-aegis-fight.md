# 0x09 — Nobilia, Square during Aegis fight

| Field | Value |
|-------|-------|
| ROM pointer | `0x9ffe0b` |
| Data | `0xa9bde6` |
| Enter script | `0x928048` → `0x97bea8` |
| Step-on table | `0xa9bdf5` — 3 entries |
| B-trigger table | `0xa9be09` — 0 entries |
| Music (normal enter) | `0x02` (Nobilia) |

## Stats

| Sniff spots | Gourds | Exits (step-on) | B-Triggers |
|-------------|--------|-----------------|------------|
| 0 | 0 | 3 (arena boundary barriers) | 0 |

## Overview

Same physical map as [0x08 — Nobilia, Square](0x08-nobilia-square.md), but loaded for the Aegis boss fight. The room plays out entirely as a forced-cutscene + combat sequence:

1. **Cutscene enter**: Boy + Dog teleported in, brightness drops to 0. Five crowd guards (`$2836–$283e`) and Aegis in robed form (`$2840`, NPC 0x62) are loaded. A long cinematic begins — Aegis delivers a monologue, steals the Diamond Eyes from the Sacred Dog Statue with animated projectiles (`$2882`/`$2884`), and the statue collapses through states 1–15. Guards are destroyed; music shifts to `0x30`. Screen shaking accompanies multiple explosion NPCs (NPC 20, spawned and destroyed in waves). Player control is returned after the explosion sequence.

2. **Boss fight**: Object 3 state is set to val:17 (statue rubble loaded). Aegis (NPC 0x47) and a combat helper (NPC 0x20) are loaded as `$2862`/`$2864`. `$23bf` is written `0x0000`. A combat AI loop runs on `$2862`; the Aegis kill script (`id:199e`, `0x97b4e6`) fires when Aegis reaches 0 HP.

3. **Kill script (Aegis kill, `0x97b4e6`)**: Sets `$22d9|=0x08` (Aegis dead), `$225f|=0x20` (Vigor defeated), clears `$22ef&=0xfd`. Long post-kill cinematic: Horace/Timberdrake (`$284e`) and Tiny the Barbarian (`$2850`) appear, Tiny throws the energy core out of the city, Madronius (`$2852`) arrives with tunnel news, Horace rewards player (Call Beads or Staff of Life). Transitions to `0x0a` (Market) with `$22eb|=0x20`, `$238f=0x0002`.

**Three boundary step-ons** block the player from leaving during the fight (east, west, south exits). Each loads two guard NPCs and triggers an object state, then destroys them after 59 ticks.

## Exits (Step-On)

| # | Tile range | Effect |
|---|------------|--------|
| 1 | `[1c,1d : 1d,1f]` — east boundary | Blocks exit: load guards `$2858`/`$285a` at (47,47)/(51,47), SET OBJ 1 STATE = 1, 59 ticks, destroy |
| 2 | `[0f,1d : 10,1f]` — west boundary | Blocks exit: load guards `$2854`/`$2856` at (17,47)/(13,47), SET OBJ 2 STATE = 1, 59 ticks, destroy |
| 3 | `[15,28 : 17,2a]` — south boundary | Blocks exit: load guards `$285c`/`$285e` at (32,71)/(32,75), SET OBJ 0 STATE = 1, 59 ticks, destroy |

## Memory Access

| Address | Bit/Value | R/W | Notes |
|---------|-----------|-----|-------|
| `$22eb` | `&0x20` | R | IN_ANIMATION — if set, skip teleport/fadeout on enter |
| `$22eb` | `&= 0xdf` | W | Clear IN_ANIMATION on enter |
| `$238d` | `== 0x00` | R | CHANGE_MUSIC — if non-zero, play music 0x02 + fade in |
| `$23bf` | `= 0x0001` | W | PACIFIED — written on enter |
| `$23bf` | `= 0x0000` | W | Cleared when fight begins (Aegis + helper loaded) |
| `$2836`…`$283e` | entity refs | W | 5 crowd guard NPCs (NPC 0x1a–0x1d), session-local |
| `$2840` | entity ref | W | Aegis cutscene NPC (NPC 0x62), session-local |
| `$242b`/`$242d` | camera | W | Camera scroll target set multiple times during cutscene |
| `$22eb` | `\|= 0x01` | W | Written during cutscene sequence and again in kill script |
| `$2842`…`$284a` | entity refs | W | Explosion NPCs (NPC 20), reused across multiple waves |
| `$284c` | counter | W | Fade-in counter, session-local |
| `$2876`–`$287a` | coords | W | Diamond Eyes left projectile position, session-local |
| `$287c`–`$2880` | coords | W | Diamond Eyes right projectile position, session-local |
| `$2882`/`$2884` | entity refs | W | Diamond Eyes projectile NPCs (NPC 0x40>>1 = 0x20), session-local |
| `$2890`–`$289a` | trajectory | W | Diamond Eyes arc calculation scratchpad, session-local |
| `$2862` | entity ref | W | Aegis boss NPC (NPC 0x47), session-local |
| `$2864` | entity ref | W | Aegis combat helper NPC (NPC 0x20), session-local |
| `$2866` | attack type | W | Aegis attack variant (RANDRANGE 0–2), session-local |
| `$2868` | counter | W | Aegis attack phase counter, session-local |
| `$2870`/`$2872`/`$2874` | entity refs | W | Kill-reward NPC entity slots, session-local |
| `$2854`/`$2856` | entity refs | W | West boundary guard NPCs, session-local |
| `$2858`/`$285a` | entity refs | W | East boundary guard NPCs, session-local |
| `$285c`/`$285e` | entity refs | W | South boundary guard NPCs, session-local |
| `$22ef` | `&= 0xfd` | W | **Aegis kill**: clear Market-reminder message shown flag |
| `$22d9` | `\|= 0x08` | W | **Aegis kill**: Aegis dead |
| `$225f` | `\|= 0x20` | W | **Aegis kill**: Vigor defeated |
| `$22eb` | `&= 0xfe` / `\|= 0x20` | W | **Aegis kill**: animation flag management |
| `$2860` | entity ref | W | **Aegis kill**: energy core NPC (NPC 0x45), session-local |
| `$284e` | entity ref | W | **Aegis kill**: Horace/Timberdrake NPC (NPC 0x8a>>1 = 0x45... NPC 0x47?), session-local |
| `$2850` | entity ref | W | **Aegis kill**: Tiny the Barbarian NPC (NPC 0x46), session-local |
| `$2852` | entity ref | W | **Aegis kill**: Madronius NPC (NPC 0x32), session-local |
| `$22d9` | `&0x01` | R | **Aegis kill**: checks Horace met/Madronius spawned for dialogue variant |
| `$231c` | `= 0x0006` | W | **Aegis kill**: Call Beads count set to 6 (if < 6) |
| `$225c` | `\|= 0x80` | W | **Aegis kill**: Horace call beads flag set |
| `$225c` | `&0x80` | R | **Aegis kill**: checks if call beads already given |
| `$243d` | `= 0x0014` | W | **Aegis kill**: Staff of Life item grant (if Call Beads already maxed) |
| `$238f` | `= 0x0002` | W | **Aegis kill**: TRANSITION_ENTER_DIRECTION before map change |
| `$22eb` | `\|= 0x20` | W | **Aegis kill**: IN_ANIMATION set before CHANGE MAP |
| CHANGE MAP | `0x0a` | — | **Aegis kill**: transition to Nobilia, Market |
| `$2886`–`$288c` | coords | W | Tiny throw + Horace walk scratchpad, session-local |

## NPCs

| Entity ref | NPC ID | Role |
|------------|--------|------|
| `$2836` | NPC 0x1d | Crowd guard (cutscene), NE position |
| `$2838` | NPC 0x1c | Crowd guard (cutscene) |
| `$283a` | NPC 0x1b | Crowd guard (cutscene) |
| `$283c` | NPC 0x1a | Crowd guard (cutscene), NW position |
| `$283e` | NPC 0x1c | Crowd guard (cutscene) |
| `$2840` | NPC 0x62 | Aegis (robed cutscene form), despawned after monologue |
| `$2842`–`$284a` | NPC 0x14 | Explosion/earthquake projectile NPCs (multiple waves) |
| `$2882`/`$2884` | NPC 0x20 | Diamond Eyes projectile entities |
| `$2862` | NPC 0x47 | Aegis (battle form) — kill script `0x199e` set on load |
| `$2864` | NPC 0x20 | Aegis combat helper (attack animation NPC) |
| `$2860` | NPC 0x45? | Energy core (thrown by Tiny) — loaded in kill script |
| `$284e` | NPC 0x45 | Horace/Timberdrake — loaded in kill script |
| `$2850` | NPC 0x46 | Tiny the Barbarian — loaded in kill script |
| `$2852` | NPC 0x32 | Madronius — loaded in kill script |

## Obj 3 States (Sacred Dog Statue)

Object 3 = the Sacred Dog Statue, cycling through animation/destruction frames:

| State | Description |
|-------|-------------|
| 0 | Default (intact) |
| 1–15 | Progressive destruction during Aegis's Diamond Eyes theft |
| 16 | Aegis defeated (set in combat helper end) |
| 17 | Statue rubble — initial state on combat enter |
| 18–21+ | Post-kill animation (Boss kill part, Horace NPC reveal sequence) |

---

## Notes

- **No return**: The Aegis kill script ends with a direct `CHANGE MAP → 0x0a` (Market). This room is never re-entered after Aegis is defeated — `$22d9&0x08` in [0x08] unloads the relevant objects so the player never gets routed here again.
- **Boundary step-ons are cosmetic**: Each barrier loads two guard NPCs, waits 59 ticks, then destroys them and restores player control. They do not set any persistent flags.
- **Explosion NPC reuse**: NPC 0x14 (the earthquake/explosion entity) is allocated and freed in six distinct waves (`$2842`/`$2844`/`$2846`/`$2848`/`$284a`), with different spawn positions each wave. The entity refs are reused across waves.
- **`$23bf` PACIFIED toggle**: Written `0x0001` on enter, then cleared to `0x0000` when the boss is loaded. Confirmed to be written/cleared in the same room within the same enter script.
- **Aegis attack helper (`$2864`)**: Uses three attack variants indexed by `$2866` (0/1/2), chosen based on Aegis's current HP relative to thresholds `0x0534` and `0x0318`. Each variant uses a different animation parameter (`0x00c6`, `0x00c2`, `0x00c4`).
- **Kill script dialogue branch**: Checks `$22d9&0x01` (Horace met / Madronius spawned). If Horace was encountered before Aegis fight, he gives a personalized post-battle speech; otherwise a generic NPC appears.
- **Item award logic**: If player has fewer than 6 Call Beads (`$231c < 6`), Horace tops them up to 6; otherwise awards Staff of Life (`$243d = 0x0014`). Horace call beads flag (`$225c&0x80`) tracks whether the intro speech has been given.
- **`$22ef&0x02` cleared twice**: Once in [0x08] Sacred Dog ceremony, and again at the start of the Aegis kill script here. Belt-and-suspenders clear for the Market reminder message flag.
