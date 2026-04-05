# Room 0x60 — Gothica: Ebon Keep Storage Room

| Field | Value |
|-------|-------|
| **Room ID** | 0x60 |
| **Act** | 3 — Gothica |
| **Data** | `0x9fff67` |
| **Enter script** | `0x9281fb` → `0x9a83d9` |
| **Dog sprite** | Default (no override) |
| **Music** | 0x5c (dungeon) |
| **Step-ons** | 1 entry |
| **B-triggers** | 3 entries (all gourds) |
| **Connections** | 0x5e (Ebon Keep Front Room) |

---

## Overview

A small storage room off Ebon Keep's front area. Contains three Ratling soldiers (NPC 0x42, loaded directly at fixed positions — not spawners), three gourds, and one exit back to 0x5e. Windwalker unlock status affects `$2437` on entry (enables the windwalker-mode Alchemy feature). Gourd OBJs 0–2 are force-unloaded on entry if already looted.

---

## Enter Logic

1. If NOT `$22eb&0x20`: teleport both to `[09,19]`; fade music
2. If `$22eb&0x20`: clear in-animation flag
3. If `$22dc&0x08` (windwalker unlocked): `$2437 = 0x0004`
4. If `$2287&0x04`: unload OBJ 0 (Feather gourd already looted)
5. If `$2287&0x08`: unload OBJ 1 (Brimstone gourd already looted)
6. If `$2287&0x10`: unload OBJ 2 (Acorns gourd already looted)
7. Set enemy loot: Prize 1 = Bead (0x0801) ×3, Prize 2 = Talons (0x0001) qty 0x50 ×2, Prize 3 = Biscuit (0x0802) ×1
8. Load NPC 0x42 at `[09,17]`, `[11,19]`, `[1f,1d]`
9. If music not locked: PLAY MUSIC 0x5c; fade in
10. `$23bf = 0x0000`; `CALL 0x92de75`; END

---

## Step-On Table

| Tile(s) | Action |
|---------|--------|
| `[21,11:23,13]` | Fade out; → 0x5e `[00c8, 0268]` (Ebon Keep Front Room) |

---

## B-Trigger Table (Gourds)

| Tile(s) | Guard flag | Item | Qty | MAP REF |
|---------|-----------|------|-----|---------|
| `[11,15:13,16]` | `$2287&0x04` | 🫙 Feather (0x020c) | 2 | 0x0000 |
| `[14,15:16,16]` | `$2287&0x08` | 🫙 Brimstone (0x0211) | 3 | 0x0001 |
| `[1e,18:20,19]` | `$2287&0x10` | 🫙 Acorns (0x0215) | 1 | 0x0002 |

All gourds: `flag |= bit if $22ea&0x01 else flag &= ~bit` (standard loot-gourd pattern).

---

## Memory Access

| Address | Bits | Access | Description |
|---------|------|--------|-------------|
| `$22eb` | 0x20 | R/W | In-animation flag |
| `$22dc` | 0x08 | R | 📖 Windwalker unlocked |
| `$2287` | 0x04 | R/W | 🫙 Gourd MAP REF 0x00 looted (Feather) |
| `$2287` | 0x08 | R/W | 🫙 Gourd MAP REF 0x01 looted (Brimstone) |
| `$2287` | 0x10 | R/W | 🫙 Gourd MAP REF 0x02 looted (Acorns) |
| `$22ea` | 0x01 | R | Loot-gourd success flag |
| `$2437` | word | W | Windwalker mode (0x0004 if unlocked) |
| `$23bf` | word | W | Unknown (cleared) |
| `$238d` | word | R | Music lock |
| `$2391` | word | W | Gourd prize item |
| `$2395` | word | W | Gourd MAP REF |
| `$2461` | word | W | Gourd prize quantity |

## Notes

- Unlike most combat rooms, the three Ratling soldiers are loaded directly at fixed map positions (not spawners) — they do not respawn on re-entry.
- Three gourds (Feather `$2287&0x04`, Brimstone `$2287&0x08`, Acorns `$2287&0x10`) are tracked in `$2287`; OBJs 0–2 are force-unloaded on entry if their flags are set.
- WindWalker unlock (`$22dc&0x08`) sets `$2437=0x0004` on entry; this same WW-mode Alchemy enable pattern appears in several other Act 3 interior rooms.
