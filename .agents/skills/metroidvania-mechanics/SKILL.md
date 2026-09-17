---
name: metroidvania-mechanics
description: Explains Metroidvania ability-gated progression in Secret of Evermore, weapon checks ($235F/$2360), alchemy barriers, and sequence-break prevention.
---

# Metroidvania Mechanics & Ability Gating

A major feature of both vanilla *Secret of Evermore* and the *Kaizo* overhaul is **Metroidvania-style progression**: non-linear world traversal where access to new regions, shortcuts, and treasures is gated by acquired weapons, alchemy formulas, and mobility abilities.

---

## 1. Gating Mechanics in Secret of Evermore

Progress barriers fall into three mechanical categories:

```
                       Metroidvania Barriers (🚪)
                                   │
      ┌────────────────────────────┼────────────────────────────┐
      ▼                            ▼                            ▼
Weapon Gating (Axe/Spear)     Alchemy Gating (Spells)     Item & Mobility
$235F (Index) / $2360 (Type)  Levitate, Revealer, Sting   Yump, Bomb, Cat Ring
```

### 1.1 Weapon Gates
Weapon gates check the equipped weapon index (`$235F`) or weapon type (`$2360`):
- **Axe Gates:**
  - Wood barriers and thick bushes: require `WEAPON_TYPE.AXE` (`0x02`).
  - Dark stone rubble and reinforced gates: require `WEAPON_INDEX.AXE_2` (`Knight's Basher`).
- **Spear Gates:**
  - Remote switches across chasms or rivers: hit by throwing `WEAPON_TYPE.SPEAR` (`0x04`).
- **Bazooka Gates:**
  - Heavy armored doors or long-range detonators: require `WEAPON_TYPE.BAZOOKA` (`0x06`).

```csharp
// Example: Checking for Axe in a B-trigger script
if (<0x2360> == WEAPON_TYPE.AXE) {
    sound(SFX.CHOP_WOOD);
    <0x2268, 0x04> = True; // Mark barrier cleared
    // Clear obstacle tiles...
} else {
    sound(SFX.CLANG_NO_DAMAGE);
}
```

### 1.2 Alchemy Gates
- **Revealer Spell:** Cast near specific chasms to materialize invisible bridges (e.g. crossing to Thraxx or the Act 3 bridge).
- **Levitate Spell:** Used on boulders and stone platforms to create stepping stones or trigger aerial switches.
- **Corrosion / Acid Rain:** Dissolves metal locks and organic barriers in prehistoric caves.

### 1.3 Custom Romhack Abilities (Kaizo Innovations)
Documented in [dev_notes.md](file:///Users/v/Documents/GitHub/everscript/dev_notes.md):
- **Cat Ring / Defend Mechanic:** Defend command acts as a cat ring, allowing survival of lethal drops or triggering specific defensive switches.
- **Yump Switches:** Jumping/stepping on one-time pressure plates.
- **Bombable Walls:** Bombs destroy rubble doors, temple axe-walls, and graveyard obstacles.

---

## 2. Sequence Breaking & Hard Mode Overrides

In Kaizo development, ensuring the player cannot bypass intended gates is critical:
- **Flag Clears:** Always verify that opening a barrier sets its persistent WRAM bit (`$2258..$23FF`) so it stays open across room reloads.
- **Hard Mode Overrides:**
  - In Hard Mode, certain utility spells are locked out ("revealer says nope", "levitate says nope") to force alternate, high-skill movement paths.
- **Standardized Documentation:**
  - Always prefix gating mechanics with the `🚪` emoji.
  - Never describe a weapon/alchemy gate using flavor words like "candles" or "lights"; describe the functional barrier type (e.g. `🚪 Knight's Basher barrier`, `🚪 Levitate boulder switch`).
