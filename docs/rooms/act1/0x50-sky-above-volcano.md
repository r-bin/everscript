# 0x50 — Sky above Volcano

**ROM:** `0x9fff27` | **Data:** `0xa5fd60` | **Enter:** `0x9281ab` → `0x9486a1`

## Statistics

| Field | Value |
|-------|-------|
| Music | `0x26` |
| Map bounds | X: 0x0000–0x0100, Y: 0x0000–0x00e0 |
| Objects | 0 |
| NPCs | 0 |
| Step-on zones | 0 |
| B-triggers | 0 |

## Connections

| Direction | Destination | Trigger | Notes |
|-----------|-------------|---------|-------|
| Auto-exit | `0x52` Top of Volcano @ `[0x0008\|0x00e8]` | End of cutscene | Unconditional; sets `$22ee\|=0x01` |

## Memory Access

| Address | Bit | Type | Description |
|---------|-----|------|-------------|
| `$22ee` | `0x01` | 📖 | Arrived from Sky above Volcano — **SET here** before warp to 0x52 |

## Enter Script Summary

1. Teleport both to `(0x07, 0x0b)`, face west.
2. Set `$23bf = 0x0001`.
3. Call `0x9485f6` (volcanic explosion VFX, phase 1).
4. Call `0x948613` (volcanic explosion VFX, phase 2).
5. Set `$22ee|=0x01`.
6. **CHANGE MAP = `0x52` Top of Volcano** @ `[0x0008|0x00e8]`.

## External Scripts

| Address | Purpose |
|---------|---------|
| `0x9485f6` | Volcanic explosion VFX, phase 1 |
| `0x948613` | Volcanic explosion VFX, phase 2 |

## Notes

- This is a pure cutscene room with no interaction possible.
- Part of the geyser sequence: 0x69 Volcano Path → 0x52 Top of Volcano → **0x50** → 0x52 Top of Volcano.
- The `$22ee&0x01` flag set here causes 0x52's enter script to run Branch B (sky return), placing the player on the summit walkway rather than replaying the geyser launch.
- `$23bf = 0x0001` is set by this room; likely a screen effect register — TODO: identify.
