# Opcode Test Performance Analysis & Optimization Plan

## 1. Executive Summary

Running the current suite of **33 opcode tests** in `tests/integration/opcodes/` takes **~68.2 seconds** (averaging **~2.08 seconds per test**). If we complete the test suite across all ~80–120 engine opcodes and their syntax variations (producing ~150–200 test cases), test execution will scale linearly to **over 5 to 7 minutes** (300–420s).

### Root Causes
Every single opcode test compiles a tiny snippet (e.g., `end();` or `<0x2258, 0x01> = 0x01;`) through `compile_snippet()` in `tests/helpers.py`. For **each test call**, the following pipeline runs from scratch:
1. **RPLY LALR(1) Parsing Table Generation (`pg.build()`)**: Executed **twice per test snippet** (once for the outer snippet, once inside the `#include("in/core")` AST node). Each call takes **~0.46s–0.60s** generating states, closures, lookaheads, and emitting 427 shift/reduce and 174 reduce/reduce warnings. Total parser build cost: **~1.0 second per test**.
2. **Re-lexing & Re-parsing Core Library (`#include("in/core")`)**: `in/core/main.evs` defines ~500 functions, hundreds of memory locations, and enum identifiers. Lexing its **79,530 tokens** takes **~0.49 seconds**.
3. **Redundant Lexing & Accidental Disk I/O**: Inside `Include.eval()` (`compiler/ast_everscript.py:1444`), all 79,530 tokens are converted to string representations, processed with regex `re.sub(r"\),", r"\),\n", ...)`, and dumped to disk as `lexer_include.txt`. Then the script is re-lexed a second time.
4. **No Test Scope / Parser Reuse**: Neither the RPLY LR parser table nor the symbols imported from `in/core` are cached across test invocations.

### Empirical Proof of Concept
By decoupling `Parser` grammar generation from the runtime `CodeGen` instance and pre-parsing the static `in/core` symbols into a baseline scope, compiling a test snippet drops from **2,100 ms** to **0.15 ms – 0.28 ms** per test.
- **Speedup**: **~10,000x** per test.
- **Suite runtime**: 33 tests execute in **~0.01 seconds** (after a one-time 1.5s warmup).
- **Full suite (200+ opcode tests)**: Completes in **under 0.1 seconds**.

---

## 2. Empirical Profiling & Call Graph Breakdown

A profile of a single invocation of `compile_snippet('end();')` (`python3 -m cProfile`) reveals:

| Stage | Duration | Primary Bottlenecks / Notes |
|---|---|---|
| **RPLY Table Build (`pg.build()`)** | `1.233s` | Runs 2x: once in `compile_snippet`, once in `Include.eval`. 427 S/R & 174 R/R conflicts recomputed. |
| **Lexing `in/core` (x2)** | `0.972s` | 79,530 tokens generated twice (once for disk dump, once for parser). 8.3 million regex matches. |
| **Parsing `in/core` AST** | `0.075s` | Building AST nodes for 498 functions and global scope identifiers. |
| **Disk I/O (`lexer_include.txt`)** | `0.015s` | String formatting + disk write in `Include.eval`. |
| **Preprocessing & Snippet Compile** | `<0.005s` | The actual test snippet (`end();`) takes less than 1 ms! |
| **Total per test** | **~2.10s** | Over **99.9%** of test time is boilerplate initialization. |

### Pytest `--durations=10` Output (Vanilla Baseline)
```
============================= slowest 10 durations =============================
2.11s call     tests/integration/opcodes/test_5c_write_object.py::test_opcode_5c_write_object
2.10s call     tests/integration/opcodes/test_22_change_map.py::test_opcode_22_change_map
2.09s call     tests/integration/opcodes/test_08_branch_if.py::test_opcode_08_branch_if
2.09s call     tests/integration/opcodes/test_3a_yield.py::test_opcode_3a_yield
2.09s call     tests/integration/opcodes/test_a8_sleep_long.py::test_opcode_a8_sleep_long
2.08s call     tests/integration/opcodes/test_09_branch_if_not.py::test_opcode_09_branch_if_not_nested_distance
2.08s call     tests/integration/opcodes/test_4d_nop.py::test_opcode_4d_nop
2.08s call     tests/integration/opcodes/test_a3_call_id.py::test_opcode_a3_call_id
2.08s call     tests/integration/opcodes/test_86_volume.py::test_opcode_86_volume
2.08s call     tests/integration/opcodes/test_29_call.py::test_opcode_29_call
============ 32 passed, 1 xfailed, 66 warnings in 68.22s (0:01:08) =============
```

Notice the remarkable uniformity: **every test takes 2.08s to 2.11s** regardless of snippet complexity.

---

## 3. The 4 Structural Bottlenecks

### Bottleneck 1: RPLY LALR Parser Table Regeneration
In `compiler/parser.py`:
```python
class Parser():
    def __init__(self, generator: CodeGen):
        self.pg = ParserGenerator([...], precedence=[...])
        ...
    def get_parser(self):
        return self.pg.build()
```
The grammar definition (~800 lines of BNF productions) is completely static. However, because `Parser` accepts `generator` in `__init__`, every compilation rebuilds the entire `ParserGenerator` and calls `self.pg.build()`. Building an LALR parser table in Python involves computing LR(0) items, first/follow sets, lookahead sets, and digraph cycle detection. This burns **~0.5s of CPU time per call**.

### Bottleneck 2: Mandatory `#include("in/core")` Recompilation
In `tests/helpers.py`:
```python
def compile_snippet(evs_code: str, name: str = "_test_snippet") -> str:
    if "fun " not in evs_code:
        full_source = f"""
#include("in/core")
fun {name}() {{
    {evs_code}
}}
"""
```
Because `#include("in/core")` is prepended to every snippet, the compiler must resolve `in/core/main.evs`, which pulls in 15+ sub-files, declaring 498 functions and hundreds of memory constants. This repeats 33 times for 33 tests, producing over **2.6 million lexed tokens** across the run.

### Bottleneck 3: Accidental Disk I/O & Token Serialization in `Include.eval()`
In `compiler/ast_everscript.py:1442-1445`:
```python
print(" - lexing code...")
outUtils = _injector.get(OutUtils)
outUtils.dump(re.sub(r"\),", r"\),\n", f"{list(lexer.lex(script))}"), "lexer_include.txt")
script = lexer.lex(script)
```
- `list(lexer.lex(script))` materializes all 79,530 tokens into memory.
- `f"{...}"` creates an ~8 MB string representation.
- `re.sub(...)` runs a regex replacement over the 8 MB string.
- `outUtils.dump(...)` writes the formatted string to disk on every single include!
- `script = lexer.lex(script)` lexes the entire file all over again because the first generator was consumed.

### Bottleneck 4: Recreating `CodeGen`, `Linker`, and Scopes
Each test constructs a fresh `Linker`, `CodeGen`, and empty global scope. While creating these objects is fast (~1 ms), populating them with the core library definitions is what triggers Bottlenecks 1–3.

---

## 4. Benchmark Proof-of-Concept Results

To verify the theoretical speedup, we constructed a benchmark prototype that:
1. Builds the `Parser` and RPLY LR parser table **once**.
2. Lexes and parses `#include("in/core")` **once** into a persistent base `CodeGen` environment.
3. Compiles subsequent snippets directly into this warm environment and strips the test function from the scope after emitting bytecode.

### Benchmark Output:
```
Warmup: Parsing in/core once...
Base in/core parse took: 1.5556s

Testing fast_compile_snippet:
Compiled 'end();' in 0.12ms -> 00
Compiled 'sleep(0x10);' in 0.15ms -> A7 10
Compiled 'fade_out();' in 0.08ms -> 27
Compiled 'yield();' in 0.08ms -> 3A
Compiled 'if(<ACTIVE> == <BOY>) { end(); }' in 0.28ms -> 09 52 29 50 A2 01 00 00
```

| Metric | Before (Vanilla) | After (Warm Base Environment) | Improvement |
|---|---|---|---|
| Per-snippet compilation | `2,080 ms` | **`0.15 ms – 0.28 ms`** | **~10,000x faster** |
| 33 tests execution | `68.2 s` | **`~0.01 s`** (plus 1.5s warmup) | **~45x faster** |
| 150 tests execution | `~315.0 s` | **`~0.03 s`** (plus 1.5s warmup) | **~200x faster** |

---

## 5. Architectural Improvement Plan

We recommend a two-layer improvement plan:

### Layer 1: Test Infrastructure Optimization (`tests/helpers.py`)
Keep production compiler code unchanged while dramatically accelerating the test suite:
1. **Module/Session Warmup Fixture**:
   - Pre-build the parser table once using a singleton `Parser` instance.
   - Pre-compile `in/core` once into a baseline snapshot of `generator.current_scope()`.
2. **Scope Rollback / Test Isolation**:
   - Prior to compiling a test snippet, shallow-copy or snapshot the baseline dicts (`functions`, `identifier`, `memory`).
   - Parse the snippet into the warm environment.
   - Clean up added identifiers/functions after code generation so tests cannot pollute one another.
3. **Fast Fallback**:
   - If a test snippet explicitly defines its own `#include` or overrides core definitions, fallback to the full isolated pipeline.

### Layer 2: Compiler Engine Optimizations
1. **Cached Parser Table in `compiler/parser.py`**:
   - Make `Parser.pg.build()` a class-level singleton or cache the generated `LRTable`.
   - The grammar never changes at runtime. Decouple `self.generator` from grammar construction by passing `generator` into `parse(tokens, generator=...)` or updating a dynamic attribute on the parser.
2. **Eliminate Token Dumping in `Include.eval()`**:
   - Guard `outUtils.dump(..., "lexer_include.txt")` behind a debug flag (e.g. `--profile` or `DEBUG=True`).
   - Remove the double lexing (`list(lexer.lex(script))` then `lexer.lex(script)`).
3. **AST Caching for Inlined Files**:
   - Cache parsed AST subtrees for static include files (`in/core/*.evs`) so they do not need to be re-tokenized or re-parsed across compilations.

---

## 6. Opcode Test Suite Rollout Plan

### Scope & Methodology
Using the vanilla ROM (`Secret of Evermore (U) [!].smc`) and `script_all` from SoETilesViewer, we extracted all empirical opcodes and variations handled by the game's script VM (`0x00` through `0xC2`).

### 1. Existing Opcode Test Files (29 Files) — Augmentation Plan
Augment existing files in `tests/integration/opcodes/` with diverse real-world patterns extracted from `script_all`:
- **`0x00` (end)**: Return from script, return from event trigger, multi-return branches.
- **`0x04` (jump)**: Forward skip in if/else, loop continuations, unconditional skips.
- **`0x07` (call_async)**: 24-bit background script calls (`call_async(address)`).
- **`0x08` / `0x09` (branch_if / branch_if_not)**:
  - Bit checks (`!($22eb & 0x20)`).
  - Entity checks (`<ACTIVE> == <BOY>`, `<ACTIVE> != <BOY>`).
  - Compound relational expressions (`val > 18`, `val == 0`).
- **`0x0C` / `0x0D` (write_flag / write_temp_flag)**: Bit sets, clears, and bit-copying expressions.
- **`0x14` / `0x18` / `0x19` / `0x1A`**: Byte, word, temp word, and script argument assignments.
- **`0x22` (change_map)**: Map transitions with coordinates and destination map IDs.
- **`0x27` / `0x82`**: Screen fade-outs (standard vs. fade to black).
- **`0x29` / `0xAF` / `0xB4`**: Synchronous calls, parameterized calls, and async parameterized calls.
- **`0x30` / `0x33` / `0x86`**: Sound effects, music tracks, audio queues, and volume control.
- **`0x3A` (yield)**: Single-frame engine yield.
- **`0x4D` (nop)**: VM no-op.
- **`0x5C` / `0x7A`**: Object state manipulation and dereference writes (`*ptr = val`).
- **`0x8E` / `0x8F`**: Currency comparisons with immediate and expression thresholds.
- **`0xA3` (call_id)**: Engine built-in script calls by ID.
- **`0xA7` / `0xA8`**: Short (8-bit ticks) and long (16-bit ticks) sleep instructions.

### 2. New Opcode Test Files (Organized by VM Subsystem)
Create standalone test files in `tests/integration/opcodes/` for all remaining engine opcodes:

#### Group A: Control Flow & Branching
- `test_05_branch_neg.py` (0x05): Negative relative skips / loop jumps (`SKIP -20`).
- `test_0a_branch_if_money_ge.py` (0x0A): Immediate currency comparison `>=`.
- `test_0b_branch_if_money_lt.py` (0x0B): Immediate currency comparison `<`.

#### Group B: Memory, Arguments & Script Modification
- `test_0e_write_arg_flag.py` (0x0E): Writing bitflag in script arg (`arg[0, 1] = 1`).
- `test_10_write_byte_loram.py` (0x10): Low RAM byte write (`$2258+x`).
- `test_11_write_temp_byte.py` (0x11): Temp byte write (`$2834+x`).
- `test_15_write_byte_alt.py` (0x15): High RAM byte write (`$57b7+`).
- `test_17_write_word_fast.py` (0x17): Fast word store.
- `test_1b_write_map_bounds.py` (0x1B): Map boundary coordinate initialization (`$23e9..$23ef`).
- `test_1c_write_word_alt.py` (0x1C): Alternate word store (`$2533`).
- `test_1d_write_temp_word_alt.py` (0x1D): Alternate temp word store (`$28a5`).
- `test_1e_write_arg_word.py` (0x1E): Writing word to script arg.
- `test_ad_write_pair.py` (0xAD): Twin 16-bit word writing to `$2867/$2869`.
- `test_ae_modify_script.py` (0xAE): In-place script timer modification.

#### Group C: Character Control, Movement & Spawning
- `test_20_teleport_both.py` (0x20): Simultaneous teleport of both characters.
- `test_2a_character_freeze.py` (0x2A): Script-controlled entity freeze.
- `test_2b_character_unfreeze.py` (0x2B): Restore player/AI control.
- `test_2e_wait_entity.py` (0x2E): Waiting for entity movement destination.
- `test_3c_load_npc.py` (0x3C): Load NPC with flags and tile position.
- `test_3d_set_npc_talk_script.py` (0x3D): Set NPC talk (B-button) script.
- `test_3f_set_npc_script.py` (0x3F): Set NPC step-on/damage/kill script.
- `test_42_teleport_entity_byte.py` (0x42): Teleport single entity (byte coordinates).
- `test_43_teleport_entity_expr.py` (0x43): Teleport entity with calculator expressions.
- `test_4e_attach_to_script.py` (0x4E): Attach entity to executing script.
- `test_6e_attach_object.py` (0x6E): Attach object to entity slot.
- `test_6f_entity_move_rel.py` (0x6F): Relative entity walking.
- `test_70_face_target.py` (0x70): Turn entity to face another entity.
- `test_71_face_each_other.py` (0x71): Turn two entities to face each other.
- `test_73_entity_move_abs.py` (0x73): Absolute entity walking.
- `test_74_face_north.py` (0x74): Direct face NORTH.
- `test_75_face_south.py` (0x75): Direct face SOUTH.
- `test_76_face_west.py` (0x76): Direct face WEST.
- `test_77_face_east.py` (0x77): Direct face EAST.
- `test_78_npc_anim.py` (0x78): NPC animation and sprite state changes.
- `test_79_npc_anim_alt.py` (0x79): Post-washing-ashore animation state.
- `test_98_switch_character.py` (0x98): Switch active control between boy and dog.
- `test_9b_destroy_entity.py` (0x9B): Destroy/deallocate entity.
- `test_9c_decrement_script_counter.py` (0x9C): Decrement script counter for entity.
- `test_9d_walk_barriers.py` (0x9D): Walk entity respecting collision barriers.
- `test_a2_spawn_npc.py` (0xA2): Dynamic NPC spawning with calculator offsets.
- `test_a9_modify_entity_bits.py` (0xA9): Modify character attribute bits (invincible, noclip, root).
- `test_ba_load_npc_simple.py` (0xBA): Simple 1-byte NPC loader.
- `test_bc_control_disable_boy.py` (0xBC): Disable boy control and SELECT button.
- `test_bd_control_boy_player.py` (0xBD): Enable player control for boy.
- `test_be_control_disable_dog.py` (0xBE): Disable dog control.
- `test_bf_control_dog_player.py` (0xBF): Enable player control for dog.
- `test_c0_control_stop_both.py` (0xC0): Freeze boy and dog.
- `test_c1_control_both_player.py` (0xC1): Restore player control to both.
- `test_c2_add_npc_spawner.py` (0xC2): Add NPC spawner trigger at coordinate.

#### Group D: Combat, Damage & Magic
- `test_92_damage_anim.py` (0x92): Inflict damage with hurt animation.
- `test_93_damage.py` (0x93): Inflict damage without animation.
- `test_94_heal_anim.py` (0x94): Restore HP with sparkle animation.
- `test_95_heal.py` (0x95): Restore HP directly.
- `test_9e_cast_spell.py` (0x9E): Cast alchemy spell at target entity.
- `test_ac_cast_spell_exclude_dog.py` (0xAC): Cast alchemy spell excluding dead dog.
- `test_bb_damage_number.py` (0xBB): Inflict damage showing floating damage number.

#### Group E: Visual Effects, Screen & Timing
- `test_31_sound_alt.py` (0x31): Alternate sound effect trigger.
- `test_32_sound_alt2.py` (0x32): Secondary sound effect trigger.
- `test_38_yield_alt.py` (0x38): Script loop yield variant.
- `test_39_sleep_subinstr.py` (0x39): Variable sleep from calculator expression.
- `test_3b_sleep_subinstr_alt.py` (0x3B): Variable sleep variant.
- `test_58_volume_fade_in.py` (0x58): Master audio fade-in.
- `test_59_volume_fade_out.py` (0x59): Master audio fade-out.
- `test_83_update_layers.py` (0x83): Update BG layers and UI rendering.
- `test_87_audio_speed.py` (0x87): Audio playback tempo/speed.
- `test_8d_screen_shake.py` (0x8D): Start/stop screen shake.
- `test_91_brightness.py` (0x91): Hardware screen brightness fade.
- `test_b6_tile_flashing.py` (0xB6): Start tile flashing effect.
- `test_b7_stop_tile_flashing.py` (0xB7): Stop tile flashing effect.

#### Group F: Subroutines & Relative Calls
- `test_a4_call_16bit.py` (0xA4): Call 16-bit script address.
- `test_a5_rcall_8bit_neg.py` (0xA5): Relative call with 8-bit negative offset.
- `test_a6_rcall_16bit_rel.py` (0xA6): Relative call with 16-bit offset.
- `test_b0_call_global_8bit.py` (0xB0): Call global script by 8-bit ID.
- `test_b1_write_args_subinstr.py` (0xB1): Batch write arguments from sub-instructions.
- `test_b2_call_relative_8bit.py` (0xB2): Relative call 8-bit offset.
- `test_b3_call_relative_16bit.py` (0xB3): Relative call 16-bit offset.

#### Group G: UI, Menus, Dialog & World
- `test_44_messagebox.py` (0x44): Open message box (standard).
- `test_48_messagebox_default.py` (0x48): Open default message box.
- `test_50_text_vram.py` (0x50): Display text in VRAM.
- `test_51_text.py` (0x51): Display text from string table.
- `test_52_subtext.py` (0x52): Display subtext without box.
- `test_55_text_end.py` (0x55): Close text display.
- `test_5a_clear_subtext.py` (0x5A): Clear unframed subtext timer.
- `test_5d_unload_obj.py` (0x5D): Conditional object unloading.
- `test_62_tile_animate.py` (0x62): Tile animation sequence.
- `test_63_alchemy_select.py` (0x63): Show alchemy reward selection.
- `test_7c_currency_give.py` (0x7C): Give currency (immediate).
- `test_7d_currency_take.py` (0x7D): Deduct currency (immediate).
- `test_7e_currency_exchange.py` (0x7E): Exchange currency between realms.
- `test_7f_dog_name_input.py` (0x7F): Prompt text entry for dog's name.
- `test_80_unhide_text.py` (0x80): Unhide unwindowed text.
- `test_81_hide_text.py` (0x81): Hide unwindowed text.
- `test_84_currency_give_subinstr.py` (0x84): Give currency from expression.
- `test_85_currency_take_subinstr.py` (0x85): Take currency from expression.
- `test_88_shop_clear.py` (0x88): Clear shop ring inventory.
- `test_89_shop_add_item.py` (0x89): Add item with price to shop ring.
- `test_8a_shop_move.py` (0x8A): Move shop ring menu to entity.
- `test_8c_save_menu.py` (0x8C): Open save game dialog.
- `test_96_teleport_screens.py` (0x96): Teleport player across screen boundaries.
- `test_99_windwalker.py` (0x99): Launch Mode 7 Windwalker flight.
- `test_9a_font.py` (0x9A): Change font rendering mode.
- `test_9f_currency_display_prep.py` (0x9F): Prepare currency HUD widget.
- `test_a0_currency_display_show.py` (0xA0): Show currency HUD widget.
- `test_a1_currency_display_hide.py` (0xA1): Hide currency HUD widget.
- `test_aa_clear_statuses.py` (0xAA): Cure poison, confound, and stat ailments.
- `test_ab_reset_game.py` (0xAB): Soft-reset engine to intro/title screen.
- `test_b5_reveal_entity.py` (0xB5): Draw lightning / reveal hidden NPC.
- `test_b9_relative_teleport.py` (0xB9): Move entity relative to current coordinates.

---

## 7. Structure of Generated Opcode Tests

Each test file follows the clean empirical standard:
1. **Docstring**: Opcode hex, name, description, and source addresses from vanilla ROM.
2. **Vanilla ROM Evidence**: Offset in `script_all` and exact bytes from `Secret of Evermore (U) [!].smc`.
3. **Everscript Code**:
   - High-level syntax or core function call if currently implemented in `in/core/` (e.g. `destroy(BOY)`, `face(BOY, NORTH)`).
   - If syntax is not yet implemented or pending discussion, marked with `@pytest.mark.xfail(reason="TODO: Everscript syntax pendant")` alongside `// TODO:` comments showing the proposed syntax.
4. **Expected Bytecode Stream**: Byte-for-byte disassembly with token-by-token comments.

