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

## 5. Documentation & Examples

- Examples in agent specs must be **generic** — no game-specific names, no real file snippets, no hardcoded paths.
- Describe patterns and structures in abstract terms; concrete room/address examples belong only in the working output section of a session, not in the spec itself.

## 6. External Projects

- Do not reference files outside this project in documentation or examples.
- Agents that need to read the script dump have **explicit permission** to search for it in sibling projects. They should locate it dynamically rather than assuming a fixed path.

## 7. Handoffs

- Handoff prompts must be written as **direct, executable instructions** — specific enough that the receiving agent can begin work immediately without clarification.
- The receiving agent must re-read the relevant source material itself; it does not inherit session memory.

## 8. Translate First, Verify on Correction

- When converting an analysis table to code, translate directly using identifiers established in session context.
- Do **not** preemptively re-verify every enum value, function signature, or constant by re-reading source files.
- Perform targeted lookups only for identifiers that are **not already resolved** in the current session.
- Full cross-referencing is reserved for when the user explicitly flags something as wrong or missing.
