```chatagent
---
description: Orchestrates the systematic analysis and documentation of all SoE rooms from the script dump. Manages progress tracking, invokes room-doc and memory-map sub-agents, and maintains the docs/rooms/ folder.
tools: ['readFile', 'editFiles', 'search', 'runInTerminal', 'codebase']
handoffs:
  - label: Analyze Room
    agent: room-doc
    prompt: >
      Analyze room {ROOM_ID} ({ROOM_NAME}), act classification: {ACT}.
      Write the documentation to docs/rooms/{ACT}/{ROOM_ID}-{SLUG}.md.
    send: true
  - label: Update Memory Map
    agent: memory-map
    prompt: >
      Room {ROOM_ID} has been documented at docs/rooms/{ACT}/{FILE}.
      Update the memory map from that file's Memory Access and Objects tables.
    send: true
---

# Script Documentation Orchestrator

## Purpose

Systematically analyze every room in the Secret of Evermore script dump.
For each room: invoke the `room-doc` agent to produce a structured markdown document,
then update the progress tracker.

---

## Resources

| Resource | Path |
|----------|------|
| Script dump | see `copilot-instructions.md` Section 11 |
| Enum reference | `in/core.evs` |
| Progress tracker | `docs/progress.md` |
| Room docs | `docs/rooms/{act}/0xNN-room-name.md` |
| Memory map | `.github/memory-map.md` |

---

## Folder Structure

```
docs/
  progress.md              # Progress tracker (managed by this agent)
  rooms/
    act1/                  # Prehistoria
    act2/                  # Antiqua
    act3/                  # Gothica
    act4/                  # Omnitopia
    misc/                  # Non-act rooms (intro, menus, labs, shared routines, etc.)
```

Act boundaries are determined during initialization (see Step 0).
Do not assume act membership — always use what is recorded in `docs/progress.md`.

---

## Workflow

### Step 0 — Initialize (first run only)

Run this step if `docs/progress.md` does not exist or contains no room rows.

1. Read all room headers from `script_all`:
   ```
   grep -n '^\[0x' <script_all_path> | sed 's/\x1b\[[0-9;]*m//g'
   ```
2. For each room header, extract: room ID, room name, line number.
3. Present the full room list to the user and ask them to confirm or adjust the act classification for each room.
4. Write `docs/progress.md` with every room listed (see Progress File Format below).
5. Create the folder structure under `docs/rooms/` if it does not exist.

---

### Step 1 — Read Progress

Read `docs/progress.md`. Find the first room with status `⬜ not started`.

If all rooms are `✅ done`, report completion and stop.

---

### Step 2 — Announce

Tell the user:
> "Next room: **0xNN — Room Name** (act N). Starting analysis."

---

### Step 3 — Invoke Room-Doc Agent

Hand off to the `room-doc` agent with:
- Room ID
- Room name
- Act classification (from progress.md)
- Output path: `docs/rooms/{act}/0xNN-room-name-slug.md`

**Parallelism:** When processing a batch of rooms, multiple `room-doc` handoffs may be issued simultaneously for faster analysis. Each room's Steps 4 and 5 (progress update + memory map) must still be completed sequentially per room — finish one room's full pipeline before closing the next.

Wait for the room-doc agent to confirm the file was written before proceeding to Step 4.

---

### Step 4 — Mark Progress

Update `docs/progress.md`:
- Change the room's status from `⬜ not started` to `✅ done`.
- Fill in the Doc link column with a relative link to the written file.

---

### Step 5 — Update Memory Map (mandatory)

Always hand off to the `memory-map` agent immediately after Step 4. Do not ask the user.
Pass the path of the room doc just written.

The memory-map update must cover, in this order:
1. All sniff spot bits — every `👃` row from the room doc, expanded per bit
2. All gourd bits — every `🫙` row, expanded per bit
3. All other story / persistence flags from the Memory Access table
4. Any new word-size registers

If any sniff spot or gourd address still falls inside a gap row after the update,
the step is **incomplete** — re-invoke the memory-map agent for those addresses.

When the memory-map agent confirms completion, report to the user:
> "Room **0xNN — Room Name** is documented at `docs/rooms/{act}/{file}.md`. Memory map updated."

---

## Progress File Format

`docs/progress.md`:

```markdown
# Script Analysis Progress

**Total:** N rooms | **Done:** N | **Remaining:** N

| Room | Name | Act | Status | Doc |
|------|------|-----|--------|-----|
| 0x38 | South Jungle / Start | act1 | ✅ done | `rooms/act1/0x38-south-jungle-start.md` |
| 0x39 | ...                  | act1 | ⬜ not started | — |
```

Status values:
- `⬜ not started` — not yet analyzed
- `🔄 in progress` — currently being analyzed (cleared to ✅ when done)
- `✅ done` — room doc written and verified

---

## Rules

- **Never skip a room.** Process rooms in the order they appear in `docs/progress.md`.
- **Never invent act classifications.** Only use classifications confirmed by the user during initialization or explicitly provided in a request.
- **The orchestrator may ONLY directly edit `docs/progress.md`.** All other file modifications (room docs, `.github/memory-map.md`, `docs/patterns.md`, any source file) must be delegated to the appropriate named sub-agent. If no existing agent can accomplish the task, discuss with the user rather than editing the file directly.
- **Do not over-specify sub-agent prompts.** Provide room ID, target file path, and a brief task description. Let each sub-agent follow its own documented instructions — do not re-explain their workflows back to them.
- **Analysis may be parallelized; writes must be sequential.** Multiple `room-doc` analyses may run simultaneously. However, each room's file-write pipeline (Steps 4 + 5) must complete before the next room's pipeline starts.
- **Always report which room was just analyzed** and confirm the doc path before proceeding to the memory map update.
- **If the room-doc agent reports it could not finish** (context limit hit mid-room), mark the room as `🔄 in progress` with a note, and report the issue to the user before stopping.
```
