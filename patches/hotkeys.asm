
macro ai16()
  rep #$30
endmacro

hirom

!HOOK_MEMORY = $FE5000
!HOTKEY_MEMORY = $FD0000

!PREV_INPUT = $F0
!WRAM_PACIFIED = $7e23bf

!HOTKEY_START = #$1000 ; BYs(S) ↑↓←→ AXLR 0123
!HOTKEY_START_L = #$1020 ; BYs(S) ↑↓←→ AX(L)R 0123
!HOTKEY_START_R = #$1010 ; BYs(S) ↑↓←→ AXL(R) 0123
!HOTKEY_B = #$8000 ; (B)YsS ↑↓←→ AXLR 0123

org !HOOK_MEMORY+0
  JSL start_practice_stuff

org !HOTKEY_MEMORY
start_practice_stuff:
  %ai16()
  ldx !PREV_INPUT
  lda $0104
  CMP !PREV_INPUT
  BEQ .noInput

  lda $0104

  ; hotkeys
  CMP !HOTKEY_START : BNE .after_hotkey_start
    JSL hotkey_pressed_start
  .after_hotkey_start
  CMP !HOTKEY_START_L : BNE .after_hotkey_start_l
    JSL hotkey_pressed_start_l
  .after_hotkey_start_l
  CMP !HOTKEY_START_R : BNE .after_hotkey_start_r
    JSL hotkey_pressed_start_r
  .after_hotkey_start_r
  CMP !HOTKEY_B : BNE .after_hotkey_b
    LDA !WRAM_PACIFIED
    CMP #$0001 : BNE .after_hotkey_b
      JSL hotkey_pressed_b
  .after_hotkey_b

  .noInput

  RTL

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

; 40 bytes, script 0xfd82c0
hotkey_pressed_start:
	LDA #$00c0
  STA $0026
  LDA #$1582
  STA $0027
  JML START_SCRIPT
  rtl
; 40 bytes, script 0xfd8300
hotkey_pressed_start_l:
	LDA #$0000
  STA $0026
  LDA #$1583
  STA $0027
  JML START_SCRIPT
  rtl
; 40 bytes, script 0xfd8340
hotkey_pressed_start_r:
	LDA #$0040
  STA $0026
  LDA #$1583
  STA $0027
  JML START_SCRIPT
  rtl
; 40 bytes, script 0xfd8380
hotkey_pressed_b:
	LDA #$0080
  STA $0026
  LDA #$1583
  STA $0027
  JML START_SCRIPT
  rtl