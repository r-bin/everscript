
macro ai16()
  rep #$30
endmacro

hirom

!HOOK_MEMORY = $FE5000
!HOTKEY_MEMORY = $FD0000

org !HOOK_MEMORY+0
  JSL start_practice_stuff

org !HOTKEY_MEMORY
start_practice_stuff:
  ; lda #$0000



  ;lda #$1111
  ; lda $2834
  LDA $7e2834

  CMP #$0000

  BEQ .SKIP_AUTO_SAVE

  ; reset autosave logic
  LDA #$0000
  STA $7e2834
  
  ; 2836++
  LDA $7e2836
  INC
  STA $7e2836

  ; slot=4
  LDA #$0006
  STA $7e0b3b

  ; init registers for the upcomming JSL
  LDA #$8000
  LDX #$0000
  LDY #$000f

  ;JSL $8dd345
  ;JSL $8dd349 ; no crash
  JSL $8dd3a9
  ;JSL $8c82dc ; no crash, but no save state


  ; 8DD436 = open menu?

  ;JSL $8dd432
  ;JSL $8db1ed

  ;LDA $7e2836
  ;INC
  ;STA $7e2836


  .SKIP_AUTO_SAVE

  RTL

;org $8DD436
org $8Db203 ; -> fade to black 
test:
  ; JSL $8EE56A (4)
  nop 
  nop
  nop
  nop
;org $8Db219 ; ?
;test2:
;  nop ; JSL $8EE56A (4)
;  nop
;  nop
;  nop
