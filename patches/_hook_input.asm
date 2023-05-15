macro ai16()
	rep #$30
endmacro

hirom
header

!HOOK_MEMORY = $FE5000

!PREV_INPUT = $F0

; This is the start of the MNI routine
;C0/8247:	A90000  	lda #$0000
;C0/824A:	5B      	tcd
;org $C08247
;  jsl mni_begin
org $C084a3
  JSL start_practice_stuff ; size 4
  NOP ; size 1
  NOP ; size 1
 
org !HOOK_MEMORY
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
start_practice_stuff:
  and $0104 ;
  sta $0104 ; what we replaced
  
  PHA
  PHB
  PHP
  PHX
  PHY
  %ai16()

  JSL hook

  PLY
  PLX
  PLP
  PLB
  PLA
  RTL