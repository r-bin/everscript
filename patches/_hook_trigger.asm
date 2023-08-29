hirom
header

!HOOK_MEMORY = $FE6000

!PREV_INPUT = $F0

; This is the start of the MNI routine
;C0/8247:	A90000  	lda #$0000
;C0/824A:	5B      	tcd
;org $C08247
;  jsl mni_begin
org $909079
  JSL start_practice_stuff ; size 4
 
org !HOOK_MEMORY

start_practice_stuff:
  ADC $1067
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
  ; no og step-on trigger?
  LDY #$000d
  LDA [$8b], Y
  CMP #$0000

  BEQ .no_hack

  ; memory[#13] = first step-on trigger byte contain magic byte #00?

  LDY #$0013
  LDA [$8b], Y
  AND #$00ff

  CMP #$0000
  BNE .no_hack
    ; $1062 = #$0012
    ; $1067 = #$0012

    ; $1062 = step-on trigger count
    INY
    LDA [$8b], Y    ; A = #$0303
    AND #$00ff      ; A = #$03 = step-on count
    ASL A           ; A = #$06
    STA $00

    CLC
    ADC $00         ; A = #$0C
    ADC $00         ; A = #$12

    sta $1062
    
    ; $1067 = b trigger count
    INY
    LDA [$8b], Y    ; A = #$xx03
    AND #$00ff      ; A = #$03 = b count
    ASL A           ; A = #$06
    STA $00

    CLC
    ADC $00         ; A = #$0C
    ADC $00         ; A = #$12

    sta $1067

    TAX             ; X = b trigger count

    ; $1064-66 = #$bdb51b
    INY
    LDA [$8b], Y
    sta $1064
    INY
    LDA [$8b], Y
    sta $1065
    
    ; $1064-66 = #$bdb51b + b trigger count = #$bdb52d
    DEY
    LDA [$8b], Y
    CLC
    ADC $1062
    sta $1069
    INY
    LDA [$8b], Y
    sta $106a

    STZ $00
  .no_hack

  RTL

; org $adb519
org $adb51f
  ; dw $000c
  ; dw $0012
  ; dw $000c
  
  ; dw $0000
  ; dl $bdb51b

  db $00        ; magic byte $#00
  db $03        ; step-on trigger count
  db $03        ; b trigger count
  dl $bdb51b    ; trigger blob (step-on + b)

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

  db $0F, $27, $10, $28
  dw $0735
  db $0c, $2f, $0e, $30 ; left two
  dw $0738
  db $0c, $31, $0e, $32 ; right two
  dw $0735

; strong heart entrance
org $9e800f
  ; db $18, $13, $1c, $14

  ; db $10, $42, $12, $44
  ; db $18, $15, $1c, $16

; strong heart entrance
org $9e8015
  ; db $18, $13, $1c, $14

  ; db $00, $00, $ff, $ff
  ; db $18, $15, $1c, $16

; ash sniff spot
org $9e803b
  ; db $1a, $1b, $1c, $1d
  
  ; db $1d, $17, $1f, $1a
  ; db $10, $17, $2f, $2a

; shell hat gourd
org $9e80ad
  ; db $1a, $1b, $1c, $1d
  
  ; db $19, $1a, $1b, $1c