# Non-Room Scripts Reference

> **Source:** `script_all` lines 62142–end  
> **Stats (from dump footer):** 89 global scripts · 421 NPC scripts · 839 other scripts · 271,634 total instructions

The script dump is divided into three sections beyond the 127 room scripts:

| Section | Lines | Description |
|---------|-------|-------------|
| Known NPC and Short scripts | 62142 – ~77017 | Named boss/NPC/utility scripts |
| Unnamed NPC/short scripts | ~77017 – 103574 | Unnamed variants (kill, talk, short) |
| Map/NPC raw script table | 103575 – end | All 0x0000–0xFFFF slots; mostly Omnitopia/Doubles |

---

## Global Scripts

Global scripts are called via the `(a3) CALL "..." (0xNN)` opcode. The table is located at ROM `0x92990b`. There are **89 entries** in the table (indices 0x00–0xFF, most slots unused or unnamed).

### Music / Fade

| ID | Name | Notes |
|----|------|-------|
| 0x00 | Fade-out / stop music | Used at most room exits and cutscene transitions |
| 0x01 | Fade-in / start music | Used after room enters and post-boss sequences |

### Message Box / Dialog Frame

| ID | Name | Notes |
|----|------|-------|
| 0x02 | Open message box? (variant A) | Most common dialog opener |
| 0x07 | Open message box? (variant B) | Alternate speaker/frame |
| 0x0a | Open message box? (variant C) | Alternate speaker/frame |
| 0x0b | Open message box? (variant D) | Alternate speaker/frame |
| 0x0d | Prepare unframed text during Aquagoth defeat | Special cinematic text frame; called only in Aquagoth kill script |

### Room Transition Helpers

These scripts prepare the player position/facing for a CHANGE MAP. Names are the dumper's best guesses at direction semantics.

| ID | Name |
|----|------|
| 0x19 | Prepare room change? West exit / east entrance outdoor–outdoor |
| 0x1d | Prepare room change? East exit / west entrance outdoor–outdoor |
| 0x20 | Prepare room change? East exit / north entrance |
| 0x21 | Prepare room change? South exit / north entrance outdoor–outdoor |
| 0x22 | Prepare room change? South exit / north entrance indoor–outdoor |
| 0x26 | Prepare room change? North exit / south entrance outdoor–indoor |
| 0x27 | Prepare room change? North exit / south entrance indoor–outdoor |
| 0x2a | Prepare room change? North exit / north entrance |
| 0x1a, 0x1c, 0x1e, 0x1f, 0x28, 0x29, 0x2d, 0x2e | Unnamed transition variants | |

### NPC Interaction Wrappers

| ID | Name | Notes |
|----|------|-------|
| 0x32 | Market NPC talk (and others?) | Opens NPC interaction; called at start of most NPC talk scripts |
| 0x33 | Market NPC end (and others?) | Closes NPC interaction; called at end of most NPC talk scripts |

### Loot / Item Pickup

| ID | Name | Notes |
|----|------|-------|
| 0x39 | Loot nature? | Plays nature ingredient pickup sequence |
| 0x3a | Loot gourd? | Plays gourd loot sequence; sets looted flag |
| 0x3b | Loot other gourd? | Alternate gourd loot variant |
| 0x3e | Loot part 1? | First phase of loot animation |
| 0x3f | Loot part 2? | Second phase |
| 0x41 | Loot part 3? | Third phase / completion |
| 0x38, 0x3d, 0x40, 0x42–0x47 | Unnamed loot/item helpers | Various item-award sub-routines |

### Shop / Save

| ID | Name | Notes |
|----|------|-------|
| 0x48 | Open shop menu? | Triggers the shop interface |
| 0x4b | Open shop menu Pt2? | Continuation / confirm phase |
| 0x4c | Ask to equip spells | Prompt after learning a formula |
| 0x4d | Save dialog | Outer "Would you like to save?" prompt |
| 0x4e | Actual save dialog | Inner save confirmation |
| 0x4f | Actual saving | Writes save data |
| 0x54 | Buy ingredients dialog | Market ingredient purchase flow |
| 0x49, 0x4a | Unnamed shop helpers | |

### Misc UI / System

| ID | Name | Notes |
|----|------|-------|
| 0x03–0x06 | Unnamed Global scripts 0x03–0x06 | Short utility stubs |
| 0x09 | Unnamed Global script 0x09 | |
| 0x0e, 0x13, 0x18 | Unnamed Global scripts | |
| 0x50–0x53 | Unnamed Global scripts 0x50–0x53 | |
| 0x55–0x58 | Unnamed Global scripts 0x55–0x58 | |
| 0x5b | Unnamed Global script 0x5b | |
| 0x5f | Unnamed Global script 0x5f | |
| 0x56 | Unnamed Global script 0x56 | |
| 0x90, 0xa3, 0xb2 | Unnamed Global scripts | |
| 0xbb–0xc0 | Unnamed Global scripts 0xbb–0xc0 | Cluster near Rimsala (addr 0x95ab6d–0x95ac30) |
| 0xd4 | Unnamed Global script 0xd4 | Shares address 0x95c752 with "North of Market Tiny dialog" NPC |
| 0xf1 | Unnamed Global script 0xf1 | |
| 0xff | Salabog dead?? | Triggered by Salabog damage/kill; meaning unclear |

### Special

| ID | Name | Notes |
|----|------|-------|
| 0x59 | Attraction mode, after Thraxx | Triggers attract/demo mode; called after Thraxx is killed in attract sequence |
| 0x5a | Credits | Rolls end credits |

---

## Named ABS Utility Scripts

These scripts are called by direct ROM address (opcode `0x29` / `0x07`) rather than via the global index table. They are shared sub-routines invoked from many different room and NPC scripts.

| Address | Name | Notes |
|---------|------|-------|
| `0x92a3e7` | Hide status bar layer | Called from ~20+ room enter/cutscene scripts to suppress HUD |
| `0x92a3ed` | Show status bar layer | Restores HUD; paired with above |
| `0x92bf33` | Hold up weapon | Victory weapon raise animation (boy lifts acquired weapon) |
| `0x92d501` | Despawn entity | Called with entity pointer; used in Aegis kill to remove the 3 orbiting spheres |
| `0x92d723` | Fade to/from/flash white B? | White-flash cinematic variant; used in boss kills (Verminator, etc.) |
| `0x92d752` | Fade to/from/flash white C? | Another white-flash variant |
| `0x92de75` | Cinematic script | Used in multiple story cutscenes |
| `0x92ded8` | Unnamed | Called in Omnitopia sphere CHANGE MAP scripts (0x0000/0x0003) |
| `0x92df1c` | Unnamed 3-arg ABS script | Used in Aegis defeat for explosion effect |
| `0x92df70` | Boss kill part | Shared boss-death sequence (fanfare, spawn reward chest, etc.); called by most boss kill scripts |
| `0x92c9c5` | Unnamed | Called in act 1 enter script |
| `0x93ca9f` | Thraxx maggot trigger | Spawns maggots during Thraxx fight; called from Thraxx damage/kill |
| `0x93d036` | Thraxx damage / kill part 1 | First phase of Thraxx damage handler |
| `0x92a4e1` | Prize drop handler | "Unknown eac+0 script. Prize drops?" — triggers enemy item drops; `$0eac` is set in many places |

---

## Named NPC / Boss Scripts

### Boss Kill / Damage Scripts

Called from the NPC entity script slot. On kill, most call `0x92df70` Boss kill part then set a persistence flag.

| Name | ID | Address | Key flags set | Notes |
|------|----|---------|---------------|-------|
| Thraxx damage/kill | 0x17cd | `0x93c8a1` | `$2260\|=0x10` (Thraxx dead) | Arg 0x0100 = hit mode: increments `$2863` hit counter, deals `$2863 × (RAND&9+1)` damage to `$2869`; spawns maggots via `0x93ca9f`. Arg 0x0200 = alt trigger → calls `0x93d036` |
| Cave raptors kill | 0x1818 | `0x94a727` | `$22df\|=0x80` (Cave raptors killed) | Basic raptor pack death |
| Magmar damage | 0x181e | `0x94b8ca` | `$2260\|=0x40` (Magmar dead) | Acts as damage handler |
| Rimsala kill | 0x18a5 | `0x95aaf5` | — | Calls Boss kill part |
| Salabog damage/kill | 0x1980 | `0x978c0c` | — | Calls global `"Salabog dead??" (0xff)` |
| Aegis kill | 0x199e | `0x97b4e6` | `$22d9\|=0x08` (Aegis dead); `$225f\|=0x20` (Vigor defeated) | **Longest single NPC script — the Act 2 ending cutscene.** Despawns Aegis's 3 orbiting spheres via `0x92d501`. Spawns Horace (NPC 0x45), Tiny (NPC 0x46), and Madronius (NPC 0x32). Gives Call Beads or Staff of Life based on `$231c` (call beads count). CHANGE MAP → 0x0a (Antiqua / Nobilia Market) |
| Aquagoth | 0x19b0 | `0x97e25e` | — | Gives 5000 Jewels + Honey. CHANGE MAP → 0x6c (Gothica — SE of Ivor Tower / Well) |
| Halls Mad Monk kill | 0x1995 | `0x97a157` | — | Mad Monk death in Halls of Collosia |
| Megataur kill | 0x1998 | `0x97a3d5` | — | Calls Boss kill part. CHANGE MAP → 0x2b (Outside of Halls) |
| Doubles kill (first?) | 0x1a5e | `0x99c637` | — | On kill, transitions remaining enemies to "others?" script (0x1a61) |
| Doubles kill (others?) | 0x1a61 | `0x99c72c` | — | On kill, transitions last enemy to "last?" script (0x1a64) |
| Doubles kill (last?) | 0x1a64 | `0x99c821` | `$22df\|=0x01` (Doubles dead) | Plays 3-part music sequence (0x36 → 0x78 → 0x68) |
| Timberdrake kill | 0x1a6d | `0x99ce38` | `$22dd\|=0x04` (Timberdrake dead) | Calls Boss kill part |
| Footknight kill | 0x1a70 | `0x99d46e` | — | Calls Boss kill part |
| Vigor damage | 0x1a79 | `0x99e69e` | — | Clears `$2834&0x04`; damage handler for Vigor boss |
| Verm kill | 0x1a7c | `0x9a8000` | `$22dd\|=0x01` (Verminator dead) | Calls Boss kill part. If `!($22db&0x20)` (no Bazooka), awards Bazooka and shows "Received Bazooka" |
| Puppet damage/kill | 0x1a82 | `0x9a8674` | — | Branches on `$22dc&0x08` (windwalker unlocked); re-assigns own script on hit |
| Mungola damage/kill | 0x1a85 | `0x9a8791` | — | Same windwalker check as Puppet |
| Sterling | 0x1a52 | `0x999432` | `$22dd\|=0x02` (Sterling dead) | |
| Raptors kill | 0x17af | `0x938fe8` | — | Generic raptor death |
| Viper commander kill | 0x17f4 | `0x949310` | — | Viper commander (Act 1) |
| Mammoth Viper 1 | 0x17d3 | `0x93d560` | — | Individual viper kill |
| Mammoth Viper 2 | 0x17d6 | — | — | |
| Mammoth Viper 3 | 0x17d9 | — | — | |
| Mammoth Viper 4 | 0x17dc | — | — | |
| Mammoth Viper Commander | 0x17df | `0x93d5da` | — | Final viper pack leader |
| Doggo dies in prison? | 0x19c5 | `0x98a642` | — | Dog death handler in prison sequence |
| Doubles room save point | 0x1a6a | `0x99ccbe` | — | Not-dog skip |

### Formula / Spell Vendor NPCs

These NPCs teach or unlock alchemy formulas. Most check a flag to skip their teaching dialog if the player already has the spell.

| Name | ID | Address | Spell / Flag |
|------|----|---------|-------------|
| Acid Rain Guy | 0x17b8 | `0x93ae4f` | Acid Rain; not-dog skip |
| Drain Guy | 0x1815 | `0x94a66f` | Drain; checks `$2259&0x02` |
| Defend Guy | 0x1860 | `0x94e4d5` | Defend; not-dog skip |
| Speed Dude | 0x1803 | `0x949c89` | Speed; checks `$225b&0x80`; alternate dialog if `$2260&0x04` |
| Fire Power Dude | 0x19b3 | `0x97e9ca` | Fire Power; skips if `$2259&0x40` |
| Corrosion Guy | 0x19cb | `0x98b2e8` | Corrosion; checks `$2258&0x10` |
| Regrowth Lady | 0x1a46 | `0x98de00` | Regrowth; checks `$225b&0x08` |
| One Up Guy | 0x1a58 | `0x99b73b` | One Up; checks `$225b&0x02`; not-dog skip |
| Naris | 0x1ad3 | `0x9abb82` | Super Heal; checks `$225c&0x04`; long dialog tree |
| Tinker | 0x1a4f | `0x998b88` | Gauge / Wheel / Diamond Eyes; checks `$22dc&0x10/0x20/0x40` |
| Junkyard Robot / Reflect | 0x1b75 | `0x9bdff6` | Reflect; checks `$22e7&0x01/0x02`, `$225b&0x04` |

### Story / Cutscene NPCs

| Name | ID | Address | Key checks / actions |
|------|----|---------|---------------------|
| Jaguar Ring Dude | 0x180c | `0x94a457` | Dog skip; checks `$2262&0x02` (Jaguar Ring), `$22ef&0x04` |
| HB Guy (cave) | 0x1809 | `0x94a412` | Dog skip |
| Cave NPC 3 | 0x180f | `0x94a554` | Dog skip |
| Cave NPC 4 | 0x1812 | `0x94a573` | Not-dog skip |
| Volcano Room NPC | 0x1806 | `0x949cee` | Volcano approach NPC |
| Fire Eyes | 0x1857 | `0x94d5c7` | Not-dog skip (19 instr); checks Thraxx dead |
| Strong Heart (inside hut) | 0x1863 | `0x94e692` | Not-dog skip (108 instr); checks Miracle Cure, `$22ec&0x80`, `$22e8&0x04` |
| Blimp (in cave) | 0x18bd | `0x95b207` | Not-dog skip |
| Blimp (in hut) | 0x185d | `0x94de48` | Not-dog skip |
| Sting Man | 0x1971 | `0x96e119` | Not-dog skip (34 instr) |
| Horace in Camp? | 0x1968 | `0x96da8c` | Not-dog skip; skips 48 instr if `$225c&0x80` (Horace call beads) |
| Horace Camp Madronius | 0x196b | `0x96db1c` | Checks `$225b&0x10` (Revealer), `$2259&0x20` (Fireball) |
| Act 2 / Horace camp Inn keeper | 0x196e | `0x96dc17` | Not-dog skip |
| Madronius' Brother in Ruins | 0x1992 | `0x97a11e` | Not-dog skip (34 instr) |
| Prof. Ruffelburg | 0x1b72 | `0x9bcf23` | Not-dog skip; Omnitopia professor |
| Dude below chessboard | 0x1a73 | `0x99d9e4` | Not-dog skip; checks `$22e7&0x80` (talked) |
| Ivor Tower Well Guy | 0x1ad0 | `0x9ab880` | |
| Dog Maze Lady | 0x19b6 | `0x989495` | Act 3 dog maze NPC |
| Lance dialog | 0x1a07 | `0x98d377` | |
| Horace first-meeting cutscene | 0x06c3 | `0x92c9a3` | Act 2 camp; short script |

### Village / Town NPCs

| Name | ID | Address | Notes |
|------|----|---------|-------|
| Hut NPC 1–7 | 0x1845–0x185a | `0x94d0bc`+ | Fire Eyes' village huts; various spell/item checks |
| FE Village NPC 1–12 | 0x1821–0x1842 | `0x94c184`+ | Fire Eyes outdoor village NPCs |
| Market NPC 1–18 | 0x191d–0x1953 | `0x96b1bd`+ | Antiqua/Nobilia market NPCs; most check `$22d9&0x08` (Aegis dead) for post-Aegis dialog |
| North of Market Tiny dialog | 0x18f3 | `0x95c752` | Short Tiny NPC dialog north of market |
| Act 3 Houses NPCs 1–20 | 0x1a07–0x1a40 | `0x98d377`+ | Gothica town NPCs |
| Act 3 shop? | 0x1a43 | `0x98d68a` | |

### Pyramid (Ae Mor / 'Mids) Scripts

| Name | ID | Address | Notes |
|------|----|---------|-------|
| 'mids [1] | 0x187b | `0x9592c3` | Combat/NPC script inside pyramid |
| 'mids [2] | 0x187e | `0x959342` | CHANGE MAP → 0x06 (Outside of Pyramids) |
| 'mids [4] (sons?) | 0x1872 | `0x95888f` | "Sons?" enemy combat |

### Wings (Fast Travel)

These are very short scripts — just a CHANGE MAP call.

| Name | ID | Address | CHANGE MAP target |
|------|----|---------|------------------|
| BBM Wings | 0x178e | `0x92d493` | → 0x67 (Bugmuck exterior) |
| Halls Wings | 0x1794 | `0x92d4a3` | → 0x2b (Outside of Halls) |
| Tiny Wings | 0x1797 | `0x92d4ab` | → 0x06 (Outside of Pyramids) |

### Desert Wraps

| Name | ID | Address | Behavior |
|------|----|---------|---------|
| Desert of Doom — wrap West | 0x040e | `0x96e3b4` | Teleports player from east edge to west edge (seamless desert loop) |
| Desert of Doom — wrap East | 0x03f9 | `0x96e366` | Teleports player from west edge to east edge |

### Boss Rush

| Name | ID | Address | Notes |
|------|----|---------|-------|
| Boss rush kill script | 0x1b5d | `0x9ba155` | Boss rush enemy death handler |
| Boss rush loot script | 0x1b5a | `0x9ba14b` | Boss rush reward/loot |

### Misc Named Scripts

| Name | ID | Address | Notes |
|------|----|---------|-------|
| Unknown script in Halls NE | 0x198f | `0x979fab` | Purpose unclear |
| Unknown 0eac+0 / Prize drops? | 0x172b | `0x92a4e1` | `$0eac` set in many places; likely enemy drop trigger. Same address as the ABS utility `0x92a4e1` |

---

## Unnamed Script Categories

Lines ~70024–103574 contain unnamed scripts, grouped by type:

### Unnamed NPC Kill Scripts
Script IDs that are simple enemy death handlers with no named flag:  
`0x17ac`, `0x17b2`, `0x17bb`, `0x17be`, `0x17c1`, `0x17c4`, `0x17c7`, `0x17ca`, `0x17e5`, `0x17e8`, `0x17eb`, `0x17ee`, `0x17f1`, `0x19a1`, `0x19a4`, `0x19a7`, `0x1956`

### Unnamed NPC Talk Scripts
Scripts that follow the `CALL 0x32` / dialog / `CALL 0x33` pattern with various flag checks:  
`0x17e2`, `0x17fa`, `0x17fd`, `0x1800`, `0x181b`, `0x194a`, `0x18f6`, `0x18f9`, `0x18fc`, `0x18ff`, `0x1902`, `0x1905`, `0x190b`, `0x190e`, `0x1911`, `0x191a`, `0x1917`, `0x1962`, `0x1965`, `0x0222`, `0x18e4`, `0x18e7`, `0x18ea`, `0x18ed`, `0x18c0`–`0x18d8` (range), `0x18db`–`0x18e1`, `0x1866`, `0x1869`, `0x186c`, `0x186f`

### Unnamed Short Scripts
Very short utility or trigger scripts (1–10 instructions):  
`0x178b`, `0x1791`, `0x07e9`, `0x17b5`, `0x17f7`, `0x0d17`, `0x01c8`, `0x0168`, `0x01dd`, `0x18f0`, `0x03f6`, `0x0405`, `0x1959`, `0x1a76`

---

## Map/NPC Raw Script Table (0x0000–0xFFFF)

Starting at line 103575, the dump enumerates every potential NPC/Map script slot. The vast majority are empty. The populated early slots are all related to **Omnitopia** mechanics:

| ID | Address | Behavior |
|----|---------|---------|
| 0x0000 | `0x9b9277` | Walk boy to position; call `0x92ded8`; set `$24fd = 0x0005`; CHANGE MAP → 0x48 (Metroplex Tunnels) |
| 0x0003 | `0x9b9241` | Same pattern; `$24fd = 0x000c`; CHANGE MAP → 0x48 |
| 0x0006 | `0x9b907a` | Walk to pos; check `$22e6&0x10`; fade + music 0x8c; SFX 0xaa; set `$2834\|=0x01` (Omnitopia sphere open) |
| 0x0009 | `0x9b904a` | Same as 0x0006 (different coordinates) |
| 0x000c | `0x9b90aa` | Check `$2835&0x02`; if `$22e6&0x10` skip; unload OBJ 5; spawn Doubles enemy wave 1; set `$2835\|=0x02` |
| 0x000f | `0x9b90f1` | Check `$2835&0x04`; if `$2834&0x02 && 0x04`; spawn Doubles wave 2 |
| 0x0012 | `0x9b913d` | Check `$2835&0x08`; if `$2834&0x08 && 0x10`; spawn Doubles wave 3 |

The three wave-spawn scripts (0x000c / 0x000f / 0x0012) work in tandem with the **Doubles kill scripts** (0x1a5e / 0x1a61 / 0x1a64) to drive the three-wave boss encounter in Omnitopia.
