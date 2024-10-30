hirom

!RING_MENU_MEMORY = $FE6200

; Hook into the routine that loads the config ring.
;ORG $8EE524
ORG $8EE520
    ; JMP $e543

    JSL LOAD_DEBUG_RING  ; NOP-out original code we will repeat in extended space. Jump to extended space to load the debug ring.
    ;NOP
    ;NOP

    ;JMP LOAD_DEBUG_RING  ; NOP-out original code we will repeat in extended space. Jump to extended space to load the debug ring.

ORG !RING_MENU_MEMORY

; Go to extended space to load the debug ring.
LOAD_DEBUG_RING:
    ;JMP $e543   ; Repeat a part of the original code that loads the config ring.
    ;LDA #$0004

    ;JML hotkey_pressed_start_r

    ;RTL          ; Jump back to original code to finish loading the config ring.
    ;JMP $E527



    JSL $8EA091 ; Repeat a part of the original code that loads the config ring.

    JML hotkey_pressed_start_r

    RTL          ; Jump back to original code to finish loading the config ring.


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
  rtl

; 40 bytes, script 0xfd83c0
hotkey_pressed_start_r:
	LDA #$00C0
  STA $0026
  LDA #$1583
  STA $0027
  JML START_SCRIPT
  rtl