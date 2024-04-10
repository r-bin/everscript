hirom
header

; TODO: currently adds the content of $2700/entity+0x30 to the stats, instead of scaling them properly

!MODIFICATION_MEMORY = $FE8000

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
  CLC
  ADC $2700

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

  PHA
  PHB
  PHP
  PHX
  PHY

  ; TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PLY
  PLX
  PLP
  PLB
  PLA

  ; without juggling the game doesn't know which ID is the source (TAX overrides that information)
  PHY

  TXY
  TAX
  LDA $8e0019,x ; original code
  CLC
  ;ADC $2700
  ADC $0030,y
  ; TAX ; original code

  PLY

  BRA .doneModifying
  .skipBoyDog

  PLY
  PLX
  PLP
  PLB
  PLA

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
  CLC
  ;ADC $2700
  ADC $0030,y

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
  SEC
  SBC $2700
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
  CLC
  ADC $2700

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
  CLC
  ADC $2700

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