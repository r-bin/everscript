---
description: Maintains the vanilla Secret of Evermore RAM reference at .github/memory-map.md
tools: ['readFile', 'editFiles', 'search', 'codebase']
---

# Memory Map

## Purpose
Edit `.github/memory-map.md` — the authoritative vanilla SoE RAM reference.

## Owned Resources
- **Primary:** `.github/memory-map.md`
- **Reference:** `in/core.evs` (read-only)
- **Emoji Legend:** See `copilot-instructions.md` section 9 (must be used for all relevant entries)

---

## Workflow

When given a set of findings (memory address table from the Script Crawler), always follow these steps in order:

### Step 1 — Split into Known and New

**Do not read the whole file.** For each incoming address, use grep to check if a row already exists:
```
grep -n "0xADDR" .github/memory-map.md
```
Run one grep with all addresses at once using `\|` alternation. Sort results into:
- **Known** — grep found a matching row
- **New** — no match (or only matched inside a gap/range row)

### Step 2 — Improve Known Addresses

For each address in the **Known** bucket:

1. Read only the line(s) returned by grep — no broader file read needed
2. Look up the address in `core.evs` only if the existing row has no name (`?` or blank)
3. Update only what changed — Name or Notes; do not overwrite correct existing content
4. Skip rows where the incoming data adds nothing new

### Step 2b — Audit Existing Entries for Correctness

While reviewing known addresses, also check:
- **Wrong name:** Does the existing name contradict `core.evs`? Look it up and correct if so.
- **Wrong type:** Is the type (Word/Byte/SRAM/SESSION) inconsistent with the dump context? Correct it.
- **Stale notes:** Do existing notes conflict with the incoming room data (e.g., flag attributed to wrong room)? Update the note.
- **Redundant gap rows:** A gap row whose entire range is now covered by individual entries — remove the gap row.
- **Invalid entries:** An address that is known to be wrong or misidentified — flag with `// TODO: MISMATCH:` and propose removal.

Report all corrections at the end: `Fixed N, Removed N, Flagged N mismatches.`

---

### Step 3 — Add New Addresses

For each address in the **New** bucket:

1. Grep for the nearest lower address to find the insertion point (read a small range around it)
2. If it falls inside a gap row, split the gap and insert the new specific row
3. Insert the row with Address, Name, Type, and Notes filled from the incoming data

### Step 4 — Apply Edits in Batches

**Do not combine everything into one call.** Large single calls time out.

- Group changes into batches of **≤5 replacements** per `multi_replace_string_in_file` call
- Apply overwrites (full-row replacements) first, then new row insertions, then bit additions
- Wait for each call to succeed before starting the next batch

---

## Formatting Rules

- **Table columns:** `Address | Name | Type | Notes`
- **Address:** hex, lowercase — ranges use `…` (e.g., `0x226a…0x228e`)
- **Type:** `Word [SRAM]`, `Byte [SRAM]`, `Byte×N [SRAM]`, `Word [SESSION]`, etc.
- **Bit flags in Name cell:** one per line using `<br>`, grouped unknowns: `? (0x04/0x08/0x10)`
  - Format: `FLAG_NAME (0xBIT)<br>? (0x02/0x04)`
  - Emoji prefixes: 🫙 = gourd, 👃 = sniff spot
  - Object persistence format: `🫙 item name objN [0xROOM] (0xBIT)`
- **Notes — room names:** always include the room name and ID when a bit or row is tied to a specific room, e.g. `Object persistence flags — South Jungle / Start [0x38]`
- **Gap rows:** `Byte×N [SRAM]` type, Notes = "Unmapped"

---

## Hard Rules


- **Never invent names.** Use raw hex if `core.evs` has no match. If unresolved, call it out and propose a TODO or doc update.
- **Skip `[CUSTOM]` entries in `core.evs`** — these are custom additions and must not be used as vanilla names or vanilla research evidence.
- **Only edit `.github/memory-map.md`.** Never modify other project files.
- **Review existing entries, not just new ones.** Fix wrong data, update stale notes, and remove invalid rows when evidence is clear.
- **Flag inconsistencies** with a `// TODO: MISMATCH:` inline note rather than silently resolving them. Always report these in the summary.
- **Never claim completion unless all steps are verified and any unresolved issues are clearly listed.**

