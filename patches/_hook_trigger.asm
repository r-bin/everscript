hirom
header

!HOOK_MEMORY = $FE6000

!PREV_INPUT = $F0

; This is the start of the MNI routine
;C0/8247:	A90000  	lda #$0000
;C0/824A:	5B      	tcd
;org $C08247
;  jsl mni_begin
org $909062
  JSL start_practice_stuff ; size 4
 
org !HOOK_MEMORY

start_practice_stuff:
  ADC $1062
  TAY
  ; what we replaced
  
  PHA
  PHB
  PHP
  PHX
  PHY

  JSL hook

  PLY
  PLX
  PLP
  PLB
  PLA
  RTL

!TRIGGER_MEMORY = $bdb51b
; !TRIGGER_MEMORY =  $b00000
  
hook:  
  ; no og-trigger?
  LDY #$000d
  LDA [$8b], Y
  CMP #$0000

  BEQ .no_hack

  ; $26 = 1b b5 ad

  LDY #$0013
  LDA [$8b], Y
  AND #$00ff

  CMP #$0000
  BNE .no_hack
    ; $1062 = #$0012
    INY
    LDA [$8b], Y

    sta $1062

    ; $1064-66 = #$bdb51b
    INY
    INY
    LDA [$8b], Y
    sta $1064
    INY
    LDA [$8b], Y
    sta $1065

  .no_hack

  RTL

; org $adb519
org $adb51f
  ; dw $000c
  ; dw $0012
  ; dw $000c
  db $00
  dw $0012
  dl $bdb51b

org !TRIGGER_MEMORY
  ; db $00
  ; dw $0012
  ; dl $bdb51b

  db $0F, $27, $10, $28
  dw $0735

  ; db $2f, $31, $0d, $32
  db $0c, $2f, $0e, $30 ; left two
  dw $0738
  db $0c, $31, $0e, $32 ; right two
  dw $0735