; Hotkey hack for Secret of Evermore (US). Asar, HiROM, ROM expanded to 4 MB.
;
; Press Start (optionally while holding L or R) and an everscript function starts, once per press:
;   press Start              -> "Start"
;   hold L, press Start      -> "Start+L"   (L and Start pressed in the same frame count too)
;   hold Start, then press L -> nothing (Start already fired when it went down)
;   keep holding Start       -> nothing more; release and press again to fire again
; Hotkeys only fire while the player has control (the gate below), never on the title screen,
; in cutscenes or text boxes, where vanilla uses Start itself.
;
; WRAM-identical. Unless a hotkey actually fires, the game runs cycle for cycle like vanilla:
; - The hook is the joypad-sequence matcher left over from the prototype ($8C:F121, run at the
;   start of every field tick from $8E:E426; in the final it only knows "Select = switch boy and
;   dog"). It returns at once when the held buttons did not change; that path is untouched.
; - The "held buttons changed" path from $8C:F134 is replaced by a copy specialised to the one
;   vanilla entry. It writes exactly what vanilla writes (chord history $3ABE/$3BBE, DP $26-$29,
;   the same stack bytes) and every branch of it takes exactly as many CPU cycles of each speed as
;   the vanilla path it replaces: ROM fetches and internal cycles (6 master clocks with FastROM,
;   which the game enables at $80:810C) and WRAM accesses (8 clocks). The counts are in the
;   comments ("F/W"); the padding (XBA, NOP, dummy WRAM reads) makes them equal. Extra cycles
;   anywhere in the main loop shift the game's timing and make a replay drift: the first version
;   of this hack, which only added ~30 cycles on these frames, lost sync with a vanilla
;   recording after 1600 frames.
; - Firing starts the script with the code Select uses ($8C:CE72 -> $8C:CF18 slot allocation,
;   $8C:CE86 run list), from the main loop. The old patches/hotkeys.asm started scripts inside the
;   NMI (hook at $80:84A3) and wrote $F0 every frame; an NMI landing while the main loop was using
;   DP $26-$28 or the run list corrupted them, which is why it crashed or glitched.

hirom

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; FEATURES (1 = on, 0 = off). Override from the .evs: #patch("hotkey_hack(!HOTKEY_GATE=0)")
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

!WITH_HOTKEY_START = 1 ; trigger alone          -> script at !SCRIPT_HOTKEY_START
!WITH_HOTKEY_START_L = 1 ; L held + trigger       -> !SCRIPT_HOTKEY_START_L
!WITH_HOTKEY_START_R = 1 ; R held + trigger       -> !SCRIPT_HOTKEY_START_R
!WITH_HOTKEY_START_LR = 0 ; L and R held + trigger -> !SCRIPT_HOTKEY_START_LR

!HOTKEY_GATE = 1 ; 1 = only while the boy is free to act (see GATE); 0 = whenever the field
                 ; runs, title screen and cutscenes included (Start there then fires a hotkey
                 ; and the game is no longer vanilla-identical)

!HOTKEY_TRIGGER = $1000 ; the button that fires (Start); one button, never Select ($2000)

!WITH_HOTKEY_TEXT = 1 ; the hotkey names as plain strings at !HOTKEY_HACK_TEXT, for subtext()
                      ; through a WRAM string key (see TEXT); costs nothing at runtime

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; ADDRESSES
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

!HOTKEY_HACK_CODE = $F80000 ; our code and table (bank plan: the $F8 lower half is free); keep
                            ; it out of the .evs #memory ranges. Any bank $C0-$FF works (FastROM,
                            ; same speed as $8C), the cycle counts depend on that.

; scripts: everscript's ADDRESS.HOTKEY_* (in/core 01_rom.evs), 40 bytes each, filled by
; @inject(ADDRESS.HOTKEY_..., True)
!SCRIPT_HOTKEY_START = $FD82C0
!SCRIPT_HOTKEY_START_L = $FD8300
!SCRIPT_HOTKEY_START_R = $FD8340
!SCRIPT_HOTKEY_START_LR = $FD8380 ; the old "hotkey B" slot (ADDRESS.HOTKEY_B)

; joypad word ($4218 layout, as in $0EC6)
!BUTTON_B = $8000
!BUTTON_Y = $4000
!BUTTON_SELECT = $2000
!BUTTON_START = $1000
!BUTTON_UP = $0800
!BUTTON_DOWN = $0400
!BUTTON_LEFT = $0200
!BUTTON_RIGHT = $0100
!BUTTON_A = $0080
!BUTTON_X = $0040
!BUTTON_L = $0020
!BUTTON_R = $0010

; held buttons that pick the hotkey; every other held button (d-pad, A, B, ...) is ignored
!MODIFIERS = !BUTTON_L|!BUTTON_R

; GATE: the boy's entity flags (+$10 of $4E89). Bits $0021 are what the entity update ($8F:CD02)
; checks before it runs a character's AI, and with it the player's control routine. Measured on
; two vanilla recordings: set on the title, in the intro and in every cutscene and text box,
; clear while the player walks around. While the dog is the active character and the boy is
; down, hotkeys are off too.
!GATE_FLAGS = $4E99
!GATE_MASK = $0021

; vanilla
!JOYPAD_HELD = $0EC6                ; held buttons, written by the NMI
!JOYPAD_HISTORY = $3ABE             ; the matcher's chord history, newest at $3ABE + X
!JOYPAD_HISTORY_INDEX = $3BBE
!MATCHER_CHANGED = $8CF134          ; PHA / LDA $3ABE,x: start of the "chord changed" path
!MATCHER_SELECT = $8CF156           ; vanilla, reached when the chord is the Select entry
!MATCHER_EXIT = $8CF16C             ; vanilla REP #$10 / PLB / RTL
!SELECT_ENTRY = $F21A               ; the matcher's one table entry ($8C:F21A): [$2000] -> $8C:F17C
!SCRIPT_START_BOUND = $8CCE72       ; inside $8C:CE5C: packed pointer in DP $26-$28, Y = entity (0 = none)

; a script's bus address as the 3-byte packed pointer $8C:CF18 decodes:
; bank = $92 + (p >> 15), address = $8000 | (p & $7FFF)
function packed_script(addr) = ((((addr>>16)&$3F)|$80)-$92)<<15|(addr&$7FFF)

assert !HOTKEY_TRIGGER != !BUTTON_SELECT, "hotkey_hack: Select is the vanilla character switch"
assert (!HOTKEY_TRIGGER&(!MODIFIERS)) == 0, "hotkey_hack: the trigger cannot also be a modifier"

; refuse a ROM whose matcher is not the US one
assert read4($8CF121) == $7E7EF48B, "hotkey_hack: $8C:F121 is not the US joypad-sequence matcher"
assert read4(!MATCHER_CHANGED) == $3ABEBD48, "hotkey_hack: $8C:F134 is not PHA / LDA $3ABE,x"
assert read4($8CF143) == $85008CA9, "hotkey_hack: $8C:F143 is not LDA #$008C / STA $28"
assert read4(!MATCHER_SELECT) == $E8E8C8C8, "hotkey_hack: $8C:F156 is not INY INY INX INX"
assert read4(!MATCHER_EXIT) == $6BAB10C2, "hotkey_hack: $8C:F16C is not REP #$10 / PLB / RTL"
assert read4($8CF216) == $0000F21A, "hotkey_hack: the matcher table at $8C:F216 is not [$F21A]"
assert read2($8CCE72) == $225A, "hotkey_hack: $8C:CE72 is not PHY / JSL"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; HOOK
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

org !MATCHER_CHANGED
  JML hotkey_matcher                ; 4/0, counted in every path below

; Vanilla from $8C:F134 to $8C:F16C (cycles F = 6-clock, W = 8-clock; c1/c2 = the page-crossing
; cycle of LDA/CMP $3ABE,x, the same instruction with the same X on both sides):
;   prev chord != 0, no Select:  78F 21W      prev chord == 0, no Select:  72F 20W
;   to $8C:F156 (Select):        64F 20W      prev == 0, to $8C:F156:      58F 19W
; Entered with A = held, X = history index (8 bit), M = 16 bit, DB = $7E, D = 0.

org !HOTKEY_HACK_CODE
hotkey_matcher:
  BIT #!HOTKEY_TRIGGER              ; 3
  BNE .trigger_held                 ; 2 / 3 taken

; trigger not held: the vanilla bookkeeping, specialised to the one table entry
.vanilla:
  PHA                               ; 2/2
  LDA !JOYPAD_HISTORY,x             ; 3+c1/2   previous chord
  BEQ ..released                    ; 2 / 3    0 = released: overwrite that slot
  DEX                               ; 2
  DEX                               ; 2
  STX !JOYPAD_HISTORY_INDEX         ; 3/1
..released:
  PLA                               ; 3/2
  STA !JOYPAD_HISTORY,x             ; 4/2
  LDA #$008C                        ; 3        $28 before $26, vanilla's order
  STA $28                           ; 2/2
  LDA #!SELECT_ENTRY                ; 3
  STA $26                           ; 2/2
  LDY #$00                          ; 2
  PHY                               ; 2/1      vanilla PHX of the table index 0
  LDA #!BUTTON_SELECT               ; 3
  CMP !JOYPAD_HISTORY,x             ; 3+c2/2   C as vanilla's compare
  BEQ ..select                      ; 2 / 3
  PLY                               ; 3/1
  LDX #$02                          ; 2
  LDA ($26)                         ; 2/4      pad ($7E:F21A)
  XBA                               ; 3        pad
  XBA                               ; 3        pad
  XBA                               ; 3        pad
  NOP                               ; 2        pad
  NOP                               ; 2        pad
  TDC                               ; 2        A = 0, N/Z as vanilla's load of the table end
  JML !MATCHER_EXIT                 ; 4        = 78F 21W / 72F 20W
..select:
  LDA ($26)                         ; 2/4      pad
  XBA                               ; 3        pad
  NOP                               ; 2        pad
  JML !MATCHER_SELECT               ; 4        = 64F 20W / 58F 19W

; trigger held: it cannot be Select's chord
.trigger_held:
  PHA                               ; 2/2
  LDA !JOYPAD_HISTORY,x             ; 3+c1/2
  BEQ .pressed_after_release        ; 2 / 3
  BIT #!HOTKEY_TRIGGER              ; 3
  BNE .still_held                   ; 2 / 3

; the trigger went down, the previous chord was not empty
  if !HOTKEY_GATE
    LDA !GATE_FLAGS                 ; 3/2
    AND #!GATE_MASK                 ; 3
    BEQ .fire                       ; 2
  else
    BRA .fire
  endif
  DEX                               ; 2
  DEX                               ; 2
  STX !JOYPAD_HISTORY_INDEX         ; 3/1
  LDA !JOYPAD_HELD                  ; 3/2      pad
; falls into the tail: 40F 9W so far, + 38F 12W = 78F 21W

.tail_after_pad:                    ; 38F 12W
  PLA                               ; 3/2
  STA !JOYPAD_HISTORY,x             ; 4/2
  LDA #$008C                        ; 3        $28 before $26, vanilla's order
  STA $28                           ; 2/2
  LDA #!SELECT_ENTRY                ; 3
  STA $26                           ; 2/2
  LDY #$00                          ; 2
  PHY                               ; 2/1
  LDA #!BUTTON_SELECT               ; 3
  CMP !JOYPAD_HISTORY,x             ; 3+c2/2   never equal here
  PLY                               ; 3/1
  LDX #$02                          ; 2
  TDC                               ; 2
  JML !MATCHER_EXIT                 ; 4

; the trigger went down after all buttons were released: 26F 6W + pad 5F 2W + BRA 3F + tail = 72F 20W
.pressed_after_release:
  if !HOTKEY_GATE
    LDA !GATE_FLAGS                 ; 3/2
    AND #!GATE_MASK                 ; 3
    BEQ .fire                       ; 2
  else
    BRA .fire
  endif
  LDA !JOYPAD_HELD                  ; 3/2      pad
  NOP                               ; 2        pad
  BRA .tail_after_pad               ; 3

; the trigger was already held, another button changed: 30F 5W + pad 7F 4W + BRA 3F + tail = 78F 21W
.still_held:
  DEX                               ; 2
  DEX                               ; 2
  STX !JOYPAD_HISTORY_INDEX         ; 3/1
  LDA ($26)                         ; 2/4      pad
  XBA                               ; 3        pad
  NOP                               ; 2        pad
  BRA .tail_after_pad               ; 3

; the gate is open: start the script, then do the vanilla bookkeeping (cycles no longer matter)
.fire:
  PLA                               ; A = held again, stack as at the hook
  JSR hotkey_fire
  BRL .vanilla

; A = held buttons, X = history index (8 bit)
hotkey_fire:
  PHP
  REP #$30
  PHA
  PHX
  PHY
  AND.w #!MODIFIERS
  PHA                               ; 1,s = modifiers held
  LDX #$0000
.next:
  LDA.l hotkey_table,x              ; modifiers, $FFFF ends the table
  BMI .end
  CMP 1,s
  BNE .skip
  PHX
  LDA.l hotkey_table+2,x
  STA $26
  LDA.l hotkey_table+3,x
  STA $27                           ; $27-$28
  LDY #$0000                        ; bound to no entity
  JSL !SCRIPT_START_BOUND
  PLX
.skip:
  INX
  INX
  INX
  INX
  INX
  BRA .next
.end:
  PLA
  PLY
  PLX
  PLA
  PLP
  RTS

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; TABLE: dw modifiers held, dl packed script pointer
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

macro hotkey(modifiers, script)
  dw <modifiers>
  dl packed_script(<script>)
endmacro

hotkey_table:
  if !WITH_HOTKEY_START
    %hotkey(0, !SCRIPT_HOTKEY_START)
  endif
  if !WITH_HOTKEY_START_L
    %hotkey(!BUTTON_L, !SCRIPT_HOTKEY_START_L)
  endif
  if !WITH_HOTKEY_START_R
    %hotkey(!BUTTON_R, !SCRIPT_HOTKEY_START_R)
  endif
  if !WITH_HOTKEY_START_LR
    %hotkey(!BUTTON_L|!BUTTON_R, !SCRIPT_HOTKEY_START_LR)
  endif
  dw $FFFF

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; TEXT: subtitles without taking a vanilla string key
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; All 3002 vanilla string keys point at live text, so every string an .evs adds normally
; replaces one. A key does not have to be a table entry, though: $8C:CD33 reads the 3-byte
; pointer at $91:D000 + key with a 24-bit index, so key $3000 + w lands in bank $92, whose
; $0000-$1FFF is the WRAM mirror: the pointer is read from WRAM w. The hotkey script writes the
; pointer to w = $0690 and shows key $3690 (main.evs). $062B-$06A2 is only cleared at boot and
; never read in the vanilla CDL library, so this touches no game state. (Everscript cannot write
; $0000-$00FF: <0x00..0xff> are its special entity variables.)
; Pointer format (24 bits, little endian): bits 0-14 the address, bits 15-22 the bank - $C0,
; bit 23 set = compressed. The text must sit in the lower half of a bank $C0-$FF; for $F8:4000
; the value is $1C4000. Plain text is ASCII, 0-terminated.

!HOTKEY_HACK_TEXT = $F84000

if !WITH_HOTKEY_TEXT
  org !HOTKEY_HACK_TEXT          ; 16 bytes per name
    db "Start", $00
  org !HOTKEY_HACK_TEXT+$10
    db "Start+L", $00
  org !HOTKEY_HACK_TEXT+$20
    db "Start+R", $00
  org !HOTKEY_HACK_TEXT+$30
    db "Start+L+R", $00
endif
