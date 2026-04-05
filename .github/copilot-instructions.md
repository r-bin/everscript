# Global Agent Rules

These rules apply to **all agents** in this project. Individual agent specs may add to them but never override them.

---

## 1. Naming & Identifiers

- **Never invent names, values, or identifiers.** Every symbol used in output must be traceable to a named source: the script dump or `in/core.evs`.
- If a value has no documented name (e.g. an unnamed music ID), use the raw hex value and flag it — do not assign a label.
- If you know the contextual meaning of something that is not yet documented, **say so explicitly** and propose adding documentation rather than silently using an invented name.

## 2. Inconsistencies

- Any inconsistency between sources (e.g. a value in the script dump that differs from a constant in `core.evs`, or a spawn coordinate that doesn't match a stub) must be **explicitly called out** in the output.
- In generated code or comments, inconsistencies go in a `// TODO:` or `// MISMATCH:` comment at the relevant line.
- Never silently resolve a conflict by picking one side.

## 3. File Editing

- **Never edit any project file** (`.evs`, `.py`, `.md`, `.asm`, etc.) without explicit user instruction naming the target file.
- When producing code output with no specified target, print to console only.
- Always ask before modifying source files (`core.evs`, `linker.py`, map stubs, etc.).

## 4. Boolean Inference

- Only use `True` / `False` for a memory field when there is credible evidence it is boolean — e.g. the field name implies boolean semantics, it is tagged `[BOOLEAN]` in `core.evs`, or it is consistently written as 0/1 paired with a meaningful name.
- When uncertain, use the raw value and add a comment.

## 5. Memory Map Agent: Strict Documentation Rules

- **Every persistence flag, object, and contained item must be documented as a separate, explicit row.**
- **No grouping:** Do not combine multiple objects or flags into a single entry. Each address/bit/object must be listed individually.
- **No omission:** Do not skip any flag, object, or item found in the crawl. If a mapping is unknown, include the row with a `?` or `unknown` and a comment.
- **No invention:** Do not invent or guess at object types, items, or addresses. Use only what is present in the source data or handoff.
- **All columns required:** Each row must include: Address, Bit, Object ID (MAP REF?), Type (emoji), and Contained Item. If any value is missing, mark it as `?` and add a comment.
- **If uncertainty exists:** Add a comment at the row explaining what is missing or ambiguous.
- **If a handoff table is provided:** The output must match the handoff table exactly, row for row, with no grouping, omission, or invention.

## 6. Documentation & Examples

- Examples in agent specs must be **generic** — no game-specific names, no real file snippets, no hardcoded paths.
- Describe patterns and structures in abstract terms; concrete room/address examples belong only in the working output section of a session, not in the spec itself.

## 7. External Projects

- Do not reference files outside this project in documentation or examples.
- Agents that need to read the script dump have **explicit permission** to read it. Use the path defined in **Section 11** — do not hardcode it in individual agent files.

## 8. Handoffs

- Handoff prompts must be written as **direct, executable instructions** — specific enough that the receiving agent can begin work immediately without clarification.
- The receiving agent must re-read the relevant source material itself; it does not inherit session memory.

## 9. Translate First, Verify on Correction

- When converting an analysis table to code, translate directly using identifiers established in session context.
- Do **not** preemptively re-verify every enum value, function signature, or constant by re-reading source files.
- Perform targeted lookups only for identifiers that are **not already resolved** in the current session.
- Full cross-referencing is reserved for when the user explicitly flags something as wrong or missing.

---

## 10. Emoji Legend

Use these emojis globally to categorize bit flags and persistent data:

| Category | Emoji |
|----------|-------|-----------------------------|
| Story flags | 📖 | plot progress, quest triggers |
| Ingredients | 🌿 | wax, ash, roots, clay |
| Consumables | 🧪 | petals, nectar, biscuits |
| Rare/key items | 💎 | wheel, diamond eyes, keys |
| Weapons | ⚔️ | sword, spear, bazooka |
| Armor | 🛡️ | armor, helmet, shield |
| Trading goods | 🏺 | rice, spice, beads, perfume |
| Currency | 💰 | talons, jewels, gold coins |
| Alchemy spells | ⚗️ | hard ball, crush, heal |
| Gourds | 🫙 | gourd |
| Sniff spots | 👃 | scent flags |
| Protagonist/boy | 🧑 | boy |
| Protagonist/dog | 🐶 | dog |
| System/engine | ⚙️ | engine, core system flags |
| System/camera | 🎥 | camera position, scroll |
| System/music | 🎵 | music, sound, sfx |

---

## 11. Script Dump Location

The raw disassembly lives in the **SoETilesViewer sibling project**:

- **Path:** `/Users/v/Documents/GitHub/SoETilesViewer/SoEScriptDumper/script_all`
- **Strip ANSI codes:** `sed 's/\x1b\[[0-9;]*m//g'`
- **Read a line range:** `sed -n 'START,ENDp' <path> | sed 's/\x1b\[[0-9;]*m//g'`
- **Read in passes of ≤400 lines** to avoid context overflow.

All agents with permission to read the script dump must use this path. Do not hardcode it in individual agent files — reference this section instead.

---

## 12. Gating Emoji (Metroidvania Barriers)

Use 🚪 for any barrier, gate, or locked door that requires a specific weapon, alchemy spell, or item to pass. Examples include weapon-gated barriers and alchemy-gated doors.

- **Never label a weapon/alchemy-gated mechanic as "candles," "lights," or similar flavour.** Use the functional term (barrier, gate, locked door) plus the 🚪 emoji.
- In section headings and the overview, call these "weapon-gated barriers" or "alchemy-gated barriers" as appropriate.
- In the Memory Access table, prefix the description with 🚪.

---

## 13. Object List: Mandatory

Every room document **must include** a complete `## Object List` section listing every OBJ index (0 through N) and its purpose. If an object's type or contents are unknown, include the row with a `?` and a comment. Do not omit OBJs that are always unloaded on entry — note them as "always unloaded (looted/dead)" with their flag.

---

## 14. Memory Map: Update After Every Room

The memory map (`/.github/memory-map.md`) **must be updated immediately after each room is documented**, not at end-of-session. The memory-map agent must be invoked as the final step in each room's workflow. Do not defer memory map updates.

---

## 15. Overview Section: Mandatory

Every room document **must include** a `## Overview` section as the first content section (after the header table). The overview must:
- Summarize the room's purpose and context in 2–5 sentences.
- Name the major gameplay paths or branches (e.g., story-gated variants).
- Mention any cross-room relationships (e.g., "same tileset as 0x12," "entered from 0x7b via the east gate").
- Omitting this section is a documentation error.

---

## 16. Cross-Room Cutscenes and Relationships

When a room is part of a cross-room relationship (shared tileset, mirrored structure, or continuation of a cutscene from another room), **explicitly note it** in the Overview and in a dedicated `## Cross-Room Relationships` section if the relationship is complex. Examples:
- Ebon Keep and Ivor Tower share room IDs in pairs (0x12/0x79, 0x7b/0x7b, 0x7c/0x7c) — the east castle flag `$22dd&0x40` controls which "side" of the room is active.
- Cutscenes that begin in room A and complete in room B (e.g., Mungola death → collapse in 0x78) must be referenced in both room docs.
