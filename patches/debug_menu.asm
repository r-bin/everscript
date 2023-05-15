; Created by XaserLE (See https://www.romhacking.net/hacks/4638/)
hirom

!RING_MENU_MEMORY = $FE0000
!BUTTON_MEMORY = $FE0300

!NUMBER_OF_BUTTONS = #$000B

!BUTTON_1_TITLE_MEMORY = $c4668e ; "Debug: Create a Monster[END]" (24 bytes)
!BUTTON_1_TITLE = "Character Presets"
!BUTTON_2_TITLE_MEMORY = $c466cd ; "Debug: Heel[END]" (12 bytes)
!BUTTON_2_TITLE = "Dog"
!BUTTON_3_TITLE_MEMORY = $c465f5 ; "Debug: Show thud balls on path[END]" (31 bytes)
!BUTTON_3_TITLE = "Atlas"
!BUTTON_4_TITLE_MEMORY = $c46614 ; "Debug: Turn off both backgrounds[END]" (33 bytes)
!BUTTON_4_TITLE = "No-Clip"
!BUTTON_5_TITLE_MEMORY = $c46635 ; "Debug: Show background 1 only[END]" (30 bytes)
!BUTTON_5_TITLE = "Available Character (Careful)"
!BUTTON_6_TITLE_MEMORY = $c46653 ; "Debug: Show background 2 only[END]" (30 bytes)
!BUTTON_6_TITLE = "Set/Unset Flags"
!BUTTON_7_TITLE_MEMORY = $c46671 ; "Debug: Show both backgrounds[END]" (29 bytes)
!BUTTON_7_TITLE = "Spawn Enemy"
!BUTTON_8_TITLE_MEMORY = $c466a6 ; "Debug: Select map[END]" (18 bytes)
!BUTTON_8_TITLE = "Unlock Items"
!BUTTON_9_TITLE_MEMORY = $c466b8 ; "Debug: Mode 7 Flight[END]" (21 bytes)
!BUTTON_9_TITLE = "Windwalker"
!BUTTON_10_TITLE_MEMORY = $c46e07 ; "Alchemist[END]" (10 bytes)
!BUTTON_10_TITLE = "Alchemy"
!BUTTON_11_TITLE_MEMORY = $c46771 ; "ROM Creation Date[END]" (18 bytes)
!BUTTON_11_TITLE = "Brian's Test Room"


; NOP-out a RTS that that makes it impossible to access the debug ring.
ORG $CEA3EA
    NOP

; Hook into the routine that loads the config ring.
ORG $CE9A86
    JSL LOAD_DEBUG_RING  ; Jump to extended space to load the debug ring.
    NOP          ; \ NOP-out original code we will repeat in extended space.
    NOP          ; /

; Hook into the routine that executes the corresponding item code when clicking on it (in config ring).
ORG $CEA439  ; This is a LDA we will repeat in extended space.
    JSL CLICK_EVENT  ; Jump to extended space.

ORG !RING_MENU_MEMORY

; Go to extended space to load the debug ring.
LOAD_DEBUG_RING:
    LDA #$0016   ; \ Repeat a part of the original code that loads the config ring.
    STA $0814    ; /
    LDA !NUMBER_OF_BUTTONS  ; \ 
    STA $0F5A    ;  | = count
    ;LDA #$000B   ;  |
    ;STA $0F5C    ;  | = last selected
    LDA #$0000   ;  |
    STA $0F5E    ;  |
    LDA #$0002   ;  |
    STA $0F60    ;  |
    LDA #$0004   ;  |
    STA $0F62    ;  |
    LDA #$0006   ;  |
    STA $0F64    ;  |
    LDA #$0008   ;  | Load the debug ring items.
    STA $0F66    ;  |
    LDA #$000A   ;  |
    STA $0F68    ;  |
    LDA #$000C   ;  |
    STA $0F6A    ;  |
    LDA #$000E   ;  |
    STA $0F6C    ;  |
    LDA #$0010   ;  |
    STA $0F6E    ;  |
    LDA #$0012   ;  |
    STA $0F70    ;  |
    LDA #$0014   ;  |
    STA $0F72    ; /
    LDA #$0000   ;  |
    STA $0F78    ; /
    RTL          ; Jump back to original code to finish loading the config ring.

CLICK_EVENT:
    LDA $8E0006,x; Repeat original code we overwrote by a long jump.
                ; Now check for clicked item in the debug ring and long jump (JML without return) to the corresponding
                ; routine. Y-Register holds RAM-Address minus 0x04 of selected item so it is easy to check for debug items.
                ; Minus 0x04 because it starts at the beginning of the debug ring where we have 2 bytes for number of items
                ; and two bytes for selected item (4 bytes). We could also subtract #$0F5A from Y-Register and then check
                ; for the index of the item beginning with 0.
    CPY #$0F5A   ; \
    BNE $04      ;  | Create a monster (not implemented yet)
    ;JML START_SCRIPT  ; | NEW: We use this for 'Full equipment'-code
    JML BUTTON_1_PRESSED  ; /
    CPY #$0F5C   ; \
    BNE $04      ;  | Heel
    JML BUTTON_2_PRESSED  ; /
    CPY #$0F5E   ; \
    BNE $04      ;  | Show thud balls on path (not implemented yet)
    ;JML START_SCRIPT  ; | NEW: We use this for 'Walk throug walls'-code
    JML BUTTON_3_PRESSED  ; /
    CPY #$0F60   ; \
    BNE $04      ;  | Turn off both backgrounds
    JML BUTTON_4_PRESSED  ; /
    CPY #$0F62   ; \
    BNE $04      ;  | Show background 1 only
    JML BUTTON_5_PRESSED  ; /
    CPY #$0F64   ; \
    BNE $04      ;  | Show background 2 only
    JML BUTTON_6_PRESSED  ; /
    CPY #$0F66   ; \
    BNE $04      ;  | Show both backgrounds
    JML BUTTON_7_PRESSED  ; /
    CPY #$0F68   ; \
    BNE $04      ;  | Select map (not implemented yet)
    JML BUTTON_8_PRESSED  ; /
    CPY #$0F6A   ; \
    BNE $04      ;  | Mode 7 flight
    JML BUTTON_9_PRESSED  ; /
    CPY #$0F6C   ; \
    BNE $04      ;  | Alchemist
    ;JML $CE95A6  ; | (normal alchemy menu)
    JML BUTTON_10_PRESSED  ; /  (alchemy setup to select new spells)
    CPY #$0F6E   ; \
    BNE $04      ;  | ROM Creation Date
    JML BUTTON_11_PRESSED  ; /
    RTL          ; Item was not from the debug ring, so go back to normal execution.

ORG !BUTTON_MEMORY

START_SCRIPT:
    JSL $8ccf18
    TXA
    LDX $86
    STA $7e2f28,x 
    INX
    INX
    TDC
    STA $7e2f28,x
    STX $86
    JML $cead67

; button 1, "Create a monster"/"Debug: Full equipment", 40 bytes, script 0xfd8000
BUTTON_1_PRESSED:
    LDA #$0000
    STA $0026
    LDA #$1580
    STA $0027
    JML START_SCRIPT

; button 2, "Debug: Heel", 40 bytes, script 0xfd8040
BUTTON_2_PRESSED:
    LDA #$0040
    STA $0026
    LDA #$1580
    STA $0027
    JML START_SCRIPT

; button 3, "Show thud balls on path"/"Debug: Walk through walls", 40 bytes, script 0xfd8080
BUTTON_3_PRESSED:
    LDA #$0080
    STA $0026
    LDA #$1580
    STA $0027
    JML START_SCRIPT

; button 4, "Debug: Turn off both backgrounds", 40 bytes, script 0xfd80c0
BUTTON_4_PRESSED:
    LDA #$00c0
    STA $0026
    LDA #$1580
    STA $0027
    JML START_SCRIPT

; button 5, "Debug: Show background 1 only", 40 bytes, script 0xfd8100
BUTTON_5_PRESSED:
    LDA #$0000
    STA $0026
    LDA #$1581
    STA $0027
    JML START_SCRIPT

; button 6, "Debug: Show background 2 only", 40 bytes, script 0xfd8140
BUTTON_6_PRESSED:
    LDA #$0040
    STA $0026
    LDA #$1581
    STA $0027
    JML START_SCRIPT

; button 7, "Debug: Show both backgrounds", 40 bytes, script 0xfd8180
BUTTON_7_PRESSED:
    LDA #$0080
    STA $0026
    LDA #$1581
    STA $0027
    JML START_SCRIPT

; button 8, "Debug: Select map", 40 bytes, script 0xfd81c0
BUTTON_8_PRESSED:
    LDA #$00c0
    STA $0026
    LDA #$1581
    STA $0027
    JML START_SCRIPT

; button 9, "Debug: Mode 7 Flight", 40 bytes, script 0xfd8200
BUTTON_9_PRESSED:
    LDA #$0000
    STA $0026
    LDA #$1582
    STA $0027
    JML START_SCRIPT

; button 10, "Alchemist", 40 bytes, script 0xfd8240
BUTTON_10_PRESSED:
    LDA #$0040
    STA $0026
    LDA #$1582
    STA $0027
    JML START_SCRIPT

; button 11, "ROM Creation Date", 40 bytes, script 0xfd8280
BUTTON_11_PRESSED:
    LDA #$0080
    STA $0026
    LDA #$1582
    STA $0027
    JML START_SCRIPT


ORG !BUTTON_1_TITLE_MEMORY
    db "!BUTTON_1_TITLE", 00

ORG !BUTTON_2_TITLE_MEMORY
    db "!BUTTON_2_TITLE", 00

ORG !BUTTON_3_TITLE_MEMORY
    db "!BUTTON_3_TITLE", 00

ORG !BUTTON_4_TITLE_MEMORY
    db "!BUTTON_4_TITLE", 00

ORG !BUTTON_5_TITLE_MEMORY
    db "!BUTTON_5_TITLE", 00

ORG !BUTTON_6_TITLE_MEMORY
    db "!BUTTON_6_TITLE", 00

ORG !BUTTON_7_TITLE_MEMORY
    db "!BUTTON_7_TITLE", 00

ORG !BUTTON_8_TITLE_MEMORY
    db "!BUTTON_8_TITLE", 00

ORG !BUTTON_9_TITLE_MEMORY
    db "!BUTTON_9_TITLE", 00

ORG !BUTTON_10_TITLE_MEMORY
    db "!BUTTON_10_TITLE", 00

ORG !BUTTON_11_TITLE_MEMORY
    db "!BUTTON_11_TITLE", 00