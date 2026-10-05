# Lua In-Game Overlay & VS Code Sync Architecture

This document specifies the design for a universal, multi-emulator **Lua Debug Overlay** for *Secret of Evermore*, and how to keep it **automatically synchronized** with the `everscript-vscode` extension and `everscript` compiler without manual maintenance.

---

## 1. The Core Problems to Solve

1. **Information Drift:**
   * Hand-coded Lua scripts break whenever memory addresses, room IDs, or trigger offsets change in romhacks.
   * Modifying room triggers in the VS Code map editor would require manually re-typing coordinates into Lua scripts.
2. **Emulator Fragmentation:**
   * Different SNES emulators (Mesen 2, Snes9x, BizHawk) have completely different, incompatible Lua scripting APIs.
   * Maintaining separate scripts for each emulator leads to abandoned, outdated tools.

---

## 2. Syncing VS Code Extension $\longleftrightarrow$ Lua Script (Zero-Maintenance Pipeline)

To avoid updating the Lua script manually, we establish a **Single Source of Truth** using two complementary sync mechanisms:

```
┌─────────────────────────────────┐
│  in/core/ + tools/dump_room.py  │
└────────────────┬────────────────┘
                 │ (1) Compile / Save Event
                 ▼
┌────────────────────────────────────────────────────────┐
│              Auto-Exported Shared Assets               │
│  • out/debug_symbols.json (Addresses from in/core/)    │
│  • out/rooms_manifest.json (Triggers, Dims, Objects)   │
│  • .everscript/live_state.json (Active editor state)   │
└───────────────▲────────────────────────▲───────────────┘
                │                        │
       (2) IPC / File Watch     (3) Read on Frame / Room Change
                │                        │
┌───────────────┴────────┐      ┌────────┴───────────────┐
│ everscript-vscode      │      │ Universal Lua Overlay  │
│ (Inspector, Map Editor)│      │ (Mesen2 / Snes9x / etc)│
└────────────────────────┘      └────────────────────────┘
```

### 2.1 Level 1: Static Export (Build Artifacts)

Whenever `everscript` compiles or the VS Code extension saves:
1. **Symbol Table Export (`out/debug_symbols.json`):**
   * Automatically dumps authoritative addresses from `in/core/` (`CAMERA_X_MIN`, `BOY_X`, `DOG_X`, `COLLISION_BASE`, `MAP_INDEX`).
2. **Room Metadata Export (`out/rooms_manifest.json`):**
   * Pre-extracted by `tools/dump_room.py`: contains bounding boxes for every step-on trigger, B-trigger, object stamp, and door transition for all 127 rooms.
3. **Lua Consumes the JSON:**
   * On startup, the Lua script loads `debug_symbols.json` and `rooms_manifest.json`.
   * **Result:** If a room's triggers or an engine address changes, the Lua overlay automatically updates without touching a single line of Lua code.

### 2.2 Level 2: Real-Time Live Sync (Bidirectional IPC / File Watch)

For interactive editing between the VS Code map editor and the emulator:

1. **Lightweight Shared State (`.everscript/live_state.json`):**
   * VS Code writes when the user interacts:
     ```json
     {
       "selected_room": "0x3D",
       "hovered_trigger": 2382,
       "highlight_coords": [52, 60],
       "show_collision": true,
       "show_drift": true
     }
     ```
2. **Fast Polling or Localhost Socket:**
   * The Lua script polls the file once every 10–30 frames (or connects via `luasocket` to `ws://localhost:9099`).
   * **In the emulator:** When the user clicks a trigger in VS Code, that trigger immediately flashes or highlights in the running game.
   * **In VS Code:** When the player steps on a trigger in the emulator, the Lua script reports `{"active_trigger": 2382}`, causing VS Code to instantly jump to that script line in `in/kaizo/` or `in/practice/main.evs`!

---

## 3. Universal Emulator Compatibility (The Emulator HAL)

Different emulators expose different Lua globals:
* **Mesen 2:** `emu.readWord(addr, emu.memType.snesWram)`, `emu.drawRectangle()`, modern Lua 5.4.
* **Snes9x:** `memory.readword(addr)`, `gui.box()`, `gui.register(fn)`, Lua 5.1.
* **BizHawk:** `memory.read_u16_le(addr, "WRAM")`, `gui.drawBox()`, `event.onframeend(fn)`, Lua 5.1.

We solve this with a single **Hardware Abstraction Layer (HAL)** file (`snes_hal.lua`) that auto-detects the host emulator at runtime and provides unified calls.

---

## 4. Reference Implementation: `snes_hal.lua`

```lua
-- snes_hal.lua
-- Hardware Abstraction Layer for Mesen 2, Snes9x, and BizHawk
local HAL = {}

-- Detect Emulator Environment
if emu and emu.readWord then
    HAL.host = "mesen2"
elseif memory and memory.readword and gui and gui.box then
    HAL.host = "snes9x"
elseif memory and memory.read_u16_le and client then
    HAL.host = "bizhawk"
else
    HAL.host = "unknown"
end

-- 1. Memory Access Abstraction (WRAM)
function HAL.read_u16(addr)
    if HAL.host == "mesen2" then
        return emu.readWord(addr, emu.memType.snesWram)
    elseif HAL.host == "snes9x" then
        return memory.readword(0x7E0000 + addr)
    elseif HAL.host == "bizhawk" then
        return memory.read_u16_le(addr, "WRAM")
    end
    return 0
end

function HAL.read_u8(addr)
    if HAL.host == "mesen2" then
        return emu.readByte(addr, emu.memType.snesWram)
    elseif HAL.host == "snes9x" then
        return memory.readbyte(0x7E0000 + addr)
    elseif HAL.host == "bizhawk" then
        return memory.read_u8(addr, "WRAM")
    end
    return 0
end

-- 2. Vector Drawing Abstraction
function HAL.draw_box(x, y, w, h, fill_color, border_color)
    if HAL.host == "mesen2" then
        if fill_color then emu.drawRectangle(x, y, w, h, fill_color, true) end
        if border_color then emu.drawRectangle(x, y, w, h, border_color, false) end
    elseif HAL.host == "snes9x" then
        gui.box(x, y, x + w, y + h, fill_color or 0, border_color or 0)
    elseif HAL.host == "bizhawk" then
        gui.drawBox(x, y, x + w, y + h, border_color or 0, fill_color or 0)
    end
end

function HAL.draw_line(x1, y1, x2, y2, color)
    if HAL.host == "mesen2" then
        emu.drawLine(x1, y1, x2, y2, color)
    elseif HAL.host == "snes9x" then
        gui.line(x1, y1, x2, y2, color)
    elseif HAL.host == "bizhawk" then
        gui.drawLine(x1, y1, x2, y2, color)
    end
end

function HAL.draw_text(x, y, text, color)
    if HAL.host == "mesen2" then
        emu.drawString(x, y, text, color, 0x000000FF)
    elseif HAL.host == "snes9x" then
        gui.text(x, y, text, color)
    elseif HAL.host == "bizhawk" then
        gui.drawText(x, y, text, color)
    end
end

-- 3. Frame Callback Abstraction
function HAL.on_frame(callback)
    if HAL.host == "mesen2" then
        emu.addEventCallback(callback, emu.eventType.postFrame)
    elseif HAL.host == "snes9x" then
        gui.register(callback)
    elseif HAL.host == "bizhawk" then
        event.onframeend(callback)
    end
end

return HAL
```

---

## 5. Main Script Template (`overlay.lua`)

With `snes_hal.lua`, the main overlay script remains completely agnostic of the host emulator:

```lua
local HAL = require("snes_hal")

-- Load auto-generated symbols from the compiler/plugin
local symbols = {
    cam_x = 0x2401,
    cam_y = 0x2405,
    room_w = 0x0F82,
    room_id = 0x24BF,
    boy_x = 0x0E2B,
    boy_y = 0x0E2D,
    dog_x = 0x0EEB,
    dog_y = 0x0EED
}

local function render()
    local cx = HAL.read_u16(symbols.cam_x)
    local cy = HAL.read_u16(symbols.cam_y)
    local bx = HAL.read_u16(symbols.boy_x)
    local by = HAL.read_u16(symbols.boy_y)

    -- Boy Hitbox (16x16)
    local sx = bx - cx
    local sy = by - cy
    HAL.draw_box(sx, sy, 16, 16, 0x60FF0000, 0xFFFF0000)
    HAL.draw_text(sx, sy - 10, "BOY", 0xFFFFFFFF)
end

HAL.on_frame(render)
```

---

## 6. Action Items / Backlog

- [ ] **Compiler/CLI Export (`tools/export_debug_json.py`):**
  - Extract WRAM addresses from `in/core/` and room trigger bounding boxes into `out/debug_symbols.json`.
- [ ] **Universal HAL (`tools/lua/snes_hal.lua`):**
  - Implement full color normalization (converting `#RRGGBBAA` into native color integers for Mesen, Snes9x, and BizHawk).
- [ ] **VS Code Live Sync Extension (`everscript-vscode`):**
  - Hook map editor selection events to write `.everscript/live_state.json`.
  - Add file watcher in Lua to react to trigger/room selections.
- [ ] **Visual Features:**
  - Continuous collision contour tracing (matching `tools/render_map.py`).
  - Forced drift direction vectors (Bit 13 arrows).
  - Step-on and B-trigger interactive bounding boxes.
