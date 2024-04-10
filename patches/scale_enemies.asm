hirom
header

; TODO: currently adds the content of $2700/entity+0x30 to the stats, instead of scaling them properly

; IDs:
; boy = 0A26? B678? (0)
; …
; FE = b9f0 (12)
; … (96)
; flower_orange = d5b0 (108)
; flower_purple = d5fa (109)
; raptor_purple = d644 (110)
; … (31)
; carltron = df3a (141)

!ENEMY_LEVEL = $2700

!MODIFICATION_MEMORY = $FE8000
!TABLE_MEMORY = $FE9000

!OFFSET_FIRST_ID = $B678
!OFFSET_TABLE_START = $d5fa-!OFFSET_FIRST_ID

!ID_BOY = #$0a26
!ID_DOG = #$0a70

; hp calculation (when sprite is created, includes boy and dog)
org $8fb15b 
  ;JSL hp_calculation ; size 4

; attack calculation (when hit, includes boy and dog)
org $8fc041
  NOP ; TAX (size 1)
  JSL attack_calculation ; LDA $8e0019,x (size 4)

; defend calculation (when hit, includes boy and dog)
org $8fc072
  JSL defend_calculation ; size 4

; magic defend calculation (when hit, includes boy and dog)
; range: #$40 - x (min: 0, max: 64/65473)
org $919cce
  NOP ; LDA #$40 (size 2)
  NOP
  JSL magic_defend_calculation ; SBC $8e001d,x (size 4)
  
; experience calculation (when dies)
org $8f8292
  JSL experience_calculation ; LDA $8e0023,x (size 4)
org $8f82d4
  JSL experience_calculation ; LDA $8e0023,x (size 4)
 
; defend calculation (when hit, includes boy and dog)
org $8f868e
  JSL money_calculation ; LDA $8e0027,x (size 4)

org !MODIFICATION_MEMORY
db "+ScaleEnemies"
hp_calculation:
  ;PHA
  PHB
  PHP
  PHX
  PHY

  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  LDA $8e000f,x ; original code
  CLC : ADC !ENEMY_LEVEL

  BRA .doneModifying
  .skipBoyDog

  LDA $8e000f,x ; original code

  .doneModifying

  PLY
  PLX
  PLP
  PLB
  ;PLA

  RTL
attack_calculation:
  ; example: wimpy #1 attacks boy
  ; [IN]     A:#$d5fa (wimpy) X:#$401d (wimpy id #1) Y:#$4e89 (boy)
  ; [DURING] A:#$____ (todo) X:#$d5fa (wimpy) Y:#$401d (wimpy id #1)
  ; [OUT]    A:#$0009 (wimpy attack) X:#$d5fa (wimpy) Y:#$4e89 (boy)

  PHA ; push "source type"

  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PLA ; pull "source type"

  ; without juggling the game doesn't know which ID is the source (TAX overrides that information)
  PHY ; push "target id"

  TXY ; transfer "source id"
  CLC : ADC !ENEMY_LEVEL ; example: contains 00, 02, …, 48 [49 4a] (offset in the wimpy stats table)
  ; SEC : SBC #!OFFSET_FIRST_ID ; redundant with "LDA !TABLE_MEMORY-!OFFSET_FIRST_ID,x"
  TAX ; tranfer "source type"

  LDA !TABLE_MEMORY-!OFFSET_FIRST_ID,x ; example: !TABLE_MEMORY + 00 = wimpy level 1 attack

  PLY ; pull "target id"

  BRA .doneModifying
  .skipBoyDog

  PLA ; pull "source type"

  TAX ; original code
  LDA $8e0019,x ; original code

  .doneModifying

  RTL
defend_calculation:
  ;PHA
  PHB
  PHP
  PHX
  PHY

  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog
  
  LDA $8e001b,x ; original code
  CLC : ADC !ENEMY_LEVEL
  ; ADC $0030,y

  BRA .doneModifying
  .skipBoyDog

  LDA $8e001b,x ; original code

  .doneModifying

  PLY
  PLX
  PLP
  PLB
  ;PLA

  RTL
magic_defend_calculation:
  ;PHA
  PHB
  PHP
  PHX
  PHY

  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  LDA #$40 ; original code
  SEC : SBC !ENEMY_LEVEL
  SBC $8e001d,x ; original code

  BRA .doneModifying
  .skipBoyDog

  LDA #$40 ; original code
  SBC $8e001d,x ; original code

  .doneModifying

  PLY
  PLX
  PLP
  PLB
  ;PLA

  RTL
experience_calculation:
  ;PHA
  PHB
  PHP
  PHX
  PHY

  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  LDA $8e0023,x ; original code
  CLC : ADC !ENEMY_LEVEL

  BRA .doneModifying
  .skipBoyDog

  LDA $8e0023,x ; original code

  .doneModifying

  PLY
  PLX
  PLP
  PLB
  ;PLA

  RTL
money_calculation:
  ;PHA
  PHB
  PHP
  PHX
  PHY

  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  LDA $8e0027,x ; original code
  CLC : ADC !ENEMY_LEVEL

  BRA .doneModifying
  .skipBoyDog

  LDA $8e0027,x ; original code

  .doneModifying

  PLY
  PLX
  PLP
  PLB
  ;PLA

  RTL


  org !TABLE_MEMORY
  ; skip !OFFSET_TABLE_START
  !counter = 0
  while !counter < !OFFSET_TABLE_START
    db #$ff
    !counter #= !counter+1
  endwhile
  dw #$0000, #$1111, #$2222, #$3333 ; "Wimpy Flower" (109)

  db "-ScaleEnemies"