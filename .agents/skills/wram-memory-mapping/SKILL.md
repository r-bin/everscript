---
name: wram-memory-mapping
description: Explains how SNES WRAM ($7E0000..$7FFFFF) is organized, endianness rules, player stats, persistence flags, and using .github/memory-map.md as the single source of truth.
---

# SNES WRAM Architecture & Memory Mapping in Secret of Evermore

In SNES ROM hacking, Work RAM (WRAM) stores the dynamic state of the game: player statistics, inventory, camera positions, entity coordinates, and persistent event flags. Reading or writing WRAM requires exact alignment with address offsets, data sizes, and byte endianness.

---

## 1. WRAM Memory Layout Overview

The SNES provides **128 KB of WRAM**, mapped across banks `$7E` and `$7F`:

```
SNES Bus Address         Size      Role in Secret of Evermore
$7E0000 - $7E01FF        512 B     Direct Page, scratchpad registers, frame counters ($0100, $0102)
$7E0200 - $7E0FFF        3.5 KB    System registers, controller inputs ($0104), ring menu pointers, character stats
$7E1000 - $7E1FFF        4 KB      Entity tables, enemy/NPC instance data, sprite active buffers
$7E2000 - $7E2257        600 B     Character names (Boy: $2210..$2233, Dog: $2234..$2257)
$7E2258 - $7E23FF        424 B     Persistent Story & Room Flags (saved to SRAM!)
$7E2400 - $7E27FF        1 KB      Market states, alchemy ingredient quantities, weapon levels
$7E2834 - $7E28FF        204 B     Temporary / Session Scratch RAM (cleared on map reload)
$7E2900 - $7EFFFF        ~53 KB    Tilemap cache, decompression scratchpad, script VM stack
$7F0000 - $7FFFFF        64 KB     High WRAM: graphical buffers, sound queue buffers, background layers
```

> [!IMPORTANT]
> **Mirrored Low RAM:** Addresses `$0000..$1FFF` in banks `$00..$3F` and `$80..$BF` mirror `$7E0000..$7E1FFF`. In 65c816 assembly, these are accessed with fast 16-bit direct addressing (e.g. `LDA $0A35` instead of `LDA $7E0A35`).

---

## 2. Endianness & Data Sizes

The 65c816 CPU is strictly **little-endian**:
- **Byte (8-bit):** Occupies 1 byte.
- **Word (16-bit):** Occupies 2 bytes. The **least significant byte (LSB)** is stored at the lower address, and the **most significant byte (MSB)** is stored at address $+1$.
  - *Example:* Boy Max HP of `999` (`0x03E7`) at `$0A35` is stored in RAM as:
    ```
    Address: $0A35    $0A36
    Value:   $E7      $03
    ```
- **Bit Flags:** Multiple boolean flags packed into a single byte. Each bit (`0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40, 0x80`) tracks a distinct world event or looted chest.

---

## 3. The Authoritative Single Source of Truth: `.github/memory-map.md`

All verified RAM addresses in Secret of Evermore are documented in:
👉 **[.github/memory-map.md](file:///Users/v/Documents/GitHub/everscript/.github/memory-map.md)**

Never guess an address. Use `.github/memory-map.md` or `in/core/[group] 00_general_enums/02_ram.evs` to look up addresses:

### Common Player & Engine Lookups:

| Symbol / Meaning | Address | Size | Notes |
|---|---|---|---|
| `FRAME_COUNTER_1` | `0x0100` | Word | Increments every V-Blank |
| `INPUT_P1` | `0x0104` | Word | Current controller button mask |
| `BOY_MAX_HP` | `0x0A35` | Word | Current maximum health |
| `BOY_HIT` / Attack | `0x0A47` | Word | Effective attack power |
| `BOY_XP` | `0x0A49` | Word | Low word of experience |
| `BOY_LEVEL` | `0x0A50` | Word | Player level (1–99) |
| `DOG_MAX_HP` | `0x0A7F` | Word | Dog maximum health |
| `DOG_LEVEL` | `0x0A9A` | Word | Dog level |
| `CURRENT_WEAPON` | `0x0ABA` | Byte | Raw equipped weapon index |
| `CURRENT_WEAPON_TYPE` | `0x2360` | Byte | `0x00`=Sword, `0x02`=Axe, `0x04`=Spear, `0x06`=Bazooka |
| `TALONS` (Act 1 Money) | `0x0AC6` | Word | Currency in Prehistoria |
| `JEWELS` (Act 2 Money) | `0x0AC9` | Word | Currency in Antiqua |
| `GOLD` (Act 3 Money) | `0x0ACC` | Word | Currency in Gothica |
| `CREDITS` (Act 4 Money)| `0x0ACF` | Word | Currency in Omnitopia |

---

## 4. Reading & Writing WRAM in Everscript

Everscript provides first-class syntax for manipulating WRAM directly:

### 4.1 Word & Byte Access: `<address>`
```csharp
// Set Boy's Max HP to 500 (0x01F4)
<0x0A35> = 500;

// Read controller input
if (<0x0104> & 0x0080) { // Start button pressed
    // Action
}
```

### 4.2 Bit Flag Access: `<address, bit>`
For persistence flags (e.g. tracking whether a chest is opened or a boss is defeated):
```csharp
// Test if Thraxx is defeated ($2260 bit 0x10)
if (<0x2260, 0x10>) {
    // Thraxx is already dead
} else {
    // Initiate boss encounter
}

// Mark a gourd as looted ($2268 bit 0x01)
<0x2268, 0x01> = True;
```
