---
name: kaizo-design-philosophy
description: Explains the Kaizo game design philosophy, how it shapes the in/kaizo/ overhaul romhack, boss design principles, and backlog triage for shipping v1.0.
---

# Kaizo Design Philosophy & Project Relevance

"Kaizo" (from *Kaizo Mario World*, Japanese for "restructured" or "remodeled") has evolved within the ROM hacking community from a niche genre of punitive hacks into a respected school of game design focused on high-skill execution, mechanical depth, and fair challenge.

---

## 1. What Modern Kaizo Means

Modern Kaizo design rejects unfair "troll" mechanics in favor of deliberate, telegraph-driven difficulty:

- **Fairness Over Frustration:** Every trap, attack pattern, or puzzle must be readable. A death should always be the player's mistake, never an unavoidable ambush or invisible hazard.
- **Mastery of Engine Mechanics:** Challenges require the player to understand and execute mechanics that vanilla game balance allowed them to ignore (stutter-stepping, dog distraction, charge attacks, weapon ranges).
- **Eliminating Degenerate Strategies:** In vanilla *Secret of Evermore*, players could pause the game to spam unlimited alchemy spells or hide while the companion killed bosses. Kaizo redesigns boss AI and resource economies to demand active engagement.

---

## 2. Relevance to This Project (`in/kaizo/`)

The directory [in/kaizo/](file:///Users/v/Documents/GitHub/everscript/in/kaizo/) is the flagship romhack of this repository. It transforms Secret of Evermore into a cohesive, high-difficulty action RPG.

### Core Kaizo Systems in Evermore:
1. **Custom Boss Encounters (`in/kaizo/[group] custom_bosses/`):**
   - Multi-phase bosses (e.g. Minitaur, Gideon, Thraxx, Diablo, Pudge, Ornstein & Smough).
   - Enrage timers, dynamic projectile patterns, arena hazards, and minion cleanup routines.
   - Damage scaling tailored to weapon tiers: ensuring specific weapons (e.g. Weapon Level 20 vs Level 25) deal balanced, calibrated damage.
2. **Circle Gating & Progression:**
   - Structured milestones (Circle 1, Circle 2, Circle 3) gating access to late-game areas until core challenges are mastered.
3. **Restricted Resource Economies:**
   - Currencies, alchemy ingredients, and weapon levels are tightly metered to prevent over-leveling trivialization.

---

## 3. Shipping Kaizo 1.0: Backlog Triage & Scope Cutting

The primary hurdle to finishing `in/kaizo/` is feature creep. The canonical backlog is maintained in [dev_notes.md](file:///Users/v/Documents/GitHub/everscript/dev_notes.md).

When triaging tasks to push towards a stable **1.0 release**:

```
Backlog Item in dev_notes.md
             │
             ├──► 1. Game-Breaking Crash or Softlock? ──► CRITICAL: Fix Immediately
             │
             ├──► 2. Critical Path Progression Blocker? ──► HIGH: Implement/Fix
             │
             ├──► 3. Core Boss Tuning (HP/Damage)?   ──► MEDIUM: Calibrate
             │
             └──► 4. "Nice to have" / Polish?        ──► CUT: Defer to post-1.0
```

### Guiding Question:
*"Does this issue prevent a player from completing the game?"*  
If no, it is a candidate for scope cut. Treat [dev_notes.md](file:///Users/v/Documents/GitHub/everscript/dev_notes.md) as a prioritization guide, not an immutable contract.
