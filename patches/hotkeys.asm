macro ai16()
	rep #$30
endmacro

hirom
header

!PREV_INPUT = $F0

!HOTKEY_START = #$1000 ; BYs(S) ↑↓←→ AXLR 0123
!HOTKEY_START_L = #$1020 ; BYs(S) ↑↓←→ AX(L)R 0123
!HOTKEY_START_R = #$1010 ; BYs(S) ↑↓←→ AXL(R) 0123


; This is the start of the MNI routine
;C0/8247:	A90000  	lda #$0000
;C0/824A:	5B      	tcd
;org $C08247
;  jsl mni_begin
org $C084a3
  JSL start_practice_stuff ; size 4
  NOP ; size 1
  NOP ; size 1
 
org $F00000
start_practice_stuff:
  and $0104 ;
  sta $0104 ; what we replaced
  
  PHA
  PHB
  PHP
  PHX
  PHY
  %ai16()

  ldx !PREV_INPUT
  lda $0104
  CMP !PREV_INPUT
  BEQ .noInput
  ; hotkeys
  CMP !HOTKEY_START : BNE .after_hotkey_start
    JSR hotkey_pressed_start
  .after_hotkey_start
  CMP !HOTKEY_START_L : BNE .after_hotkey_start_l
    JSR hotkey_pressed_start_l
  .after_hotkey_start_l
  CMP !HOTKEY_START_R : BNE .after_hotkey_start_r
    JSR hotkey_pressed_start_r
  .after_hotkey_start_r
  .noInput

  lda $104
  sta !PREV_INPUT
  PLY
  PLX
  PLP
  PLB
  PLA
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
  rts

; 40 bytes, script 0xfd82c0
hotkey_pressed_start:
	LDA #$00c0
  STA $0026
  LDA #$1582
  STA $0027
  JML START_SCRIPT
  rts
; 40 bytes, script 0xfd8300
hotkey_pressed_start_l:
	LDA #$0000
  STA $0026
  LDA #$1583
  STA $0027
  JML START_SCRIPT
  rts
; 40 bytes, script 0xfd8340
hotkey_pressed_start_r:
	LDA #$0040
  STA $0026
  LDA #$1583
  STA $0027
  JML START_SCRIPT
  rts