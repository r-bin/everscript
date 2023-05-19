hirom
header

!HOOK_MEMORY = $FE6000

!PREV_INPUT = $F0

; This is the start of the MNI routine
;C0/8247:	A90000  	lda #$0000
;C0/824A:	5B      	tcd
;org $C08247
;  jsl mni_begin
org $8facbd
  JSL start_practice_stuff ; size 4
  NOP ; size 1
  NOP ; size 1
  NOP ; size 1
  NOP ; size 1
  NOP ; size 1
  NOP ; size 1
 
org !HOOK_MEMORY

start_practice_stuff:
  lda $1064   ; ad 64 10
  sta $26     ; 85 26
  
  lda $1065   ; ad 65 10
  sta $27     ; 85 27
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
  ; $26 = 1b b5 ad

  lda $ADB
  
  CMP #$0033
  BNE .not_33

  ; lda #$000c
  lda #$0012
  sta $1062
  sta $1062

  ;lda $1064   ; ad 64 10
  ;sta $26     ; 85 26
  lda #$b51b
  sta $26
  
  ;lda $1065   ; ad 65 10
  ;sta $27     ; 85 27
  lda #$bdb5
  sta $27

  .not_33:

  RTL

; org $adb519
  ; dw $000c
  ; dw $0012
  ; dw $000c

org !TRIGGER_MEMORY
  db $0F, $27, $10, $28
  dw $0735
  ; db $2f, $31, $0d, $32
  db $0c, $2f, $0e, $30 ; left two
  dw $0738
  db $0c, $31, $0e, $32 ; right two
  dw $0735