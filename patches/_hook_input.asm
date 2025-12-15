hirom

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!ROM_EXTENSION = $FE5000 ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

!PREV_INPUT = $F0

; This is the start of the MNI routine
;C0/8247:	A90000  	lda #$0000
;C0/824A:	5B      	tcd
;org $C08247
;  jsl mni_begin
org $C084a3
  JSL rom_extension ; size 4
  NOP ; size 1
  NOP ; size 1
 
org !ROM_EXTENSION
hook:
  ; hook 1
  NOP
  NOP
  NOP
  NOP
	; hook 2
  NOP
  NOP
  NOP
  NOP
	; hook 3
  NOP
  NOP
  NOP
  NOP
	; hook 4
  NOP
  NOP
  NOP
  NOP
	; hook 5
  NOP
  NOP
  NOP
  NOP
	; hook 6
  NOP
  NOP
  NOP
  NOP
	; hook 7
  NOP
  NOP
  NOP
  NOP
	; hook 8
  NOP
  NOP
  NOP
  NOP
	; hook 9
  NOP
  NOP
  NOP
  NOP
	; hook 10
  NOP
  NOP
  NOP
  NOP

  RTL
rom_extension:
  and $0104 ;
  sta $0104 ; what we replaced
  
  PHA
  PHB
  PHP
  PHX
  PHY

  JSL hook

  lda $104
  sta !PREV_INPUT

  PLY
  PLX
  PLP
  PLB
  PLA
  RTL