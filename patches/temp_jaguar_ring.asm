hirom

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!ROM_EXTENSION = $FE6000 ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

!PREV_INPUT = $F0

; This is the start of the MNI routine
;C0/8247:	A90000  	lda #$0000
;C0/824A:	5B      	tcd
;org $C08247
;  jsl mni_begin
org $9082aa
  JSL rom_extension ; size 4
  NOP ; size 1
  NOP ; size 1
 
org !ROM_EXTENSION
rom_extension:
  TYA ; enemy_type

  CMP #$4e89 : BNE .not_boy ; boy?

  LDA $4F2F ; evade boost boy
  CMP #$0000

  BEQ .allow_running

  ; CMP #$ffff
  RTL

  .not_boy

  LDA $4FDB ; evade boost dog
  CMP #$0000

  BEQ .allow_running

  ; CMP #$ffff
  RTL


  .allow_running


  LDA $28fb
  BIT #$0008

  BEQ .force_walking ; ignore jaguar ring
  CMP $28fb
  RTL
  .force_walking

  LDA $2262 ; what we replaced
  BIT #$0002

  RTL