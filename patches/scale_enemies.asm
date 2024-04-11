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

!MEMORY_STAT_HOOKS = $FE8000
!MEMORY_TABLE_HP = $FE9000
!MEMORY_TABLE_ATTACK = $FEd000
!MEMORY_TABLE_DEFEND = $Ff1000
!MEMORY_TABLE_MAGIC_DEFEND = $Ff5000
!MEMORY_TABLE_EXPERIENCE = $Ff9000
!MEMORY_TABLE_MONEY = $Ffc000

!OFFSET_FIRST_ID = $B678
!OFFSET_TABLE_WIMPY = $d5fa-!OFFSET_FIRST_ID

!ID_BOY = #$0a26
!ID_DOG = #$0a70

; hp calculation (when sprite is created, includes boy and dog)
org $8fb15b 
  JSL hp_calculation ; size 4

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

org !MEMORY_STAT_HOOKS
db "+ScaleEnemies"
hp_calculation:
  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PHX ; push "source type"
  
  CLC : ADC !ENEMY_LEVEL ; example: contains 00, 02, …, 48 [49 4a] (offset in the wimpy stats table)
  TAX ; tranfer "source type"

  LDA !MEMORY_TABLE_HP-!OFFSET_FIRST_ID,x ; example: !MEMORY_TABLE_ATTACK + 00 = wimpy level 1 attack
  
  PLX ; pull "source type"

  BRA .doneModifying
  .skipBoyDog

  LDA $8e000f,x ; original code

  .doneModifying

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
  ; SEC : SBC #!OFFSET_FIRST_ID ; redundant with "LDA !MEMORY_TABLE_ATTACK-!OFFSET_FIRST_ID,x"
  TAX ; tranfer "source type"

  LDA !MEMORY_TABLE_ATTACK-!OFFSET_FIRST_ID,x ; example: !MEMORY_TABLE_ATTACK + 00 = wimpy level 1 attack

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

  PHX ; push "source type"
  
  CLC : ADC !ENEMY_LEVEL ; example: contains 00, 02, …, 48 [49 4a] (offset in the wimpy stats table)
  TAX ; tranfer "source type"

  LDA !MEMORY_TABLE_DEFEND-!OFFSET_FIRST_ID,x ; example: !MEMORY_TABLE_ATTACK + 00 = wimpy level 1 attack
  
  PLX ; pull "source type"

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
  PHP

  REP #$ff

  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  
  PHX ; push "source type"
  TXA ; tranfer "target type"
  CLC : ADC !ENEMY_LEVEL ; example: contains 00, 02, …, 48 [49 4a] (offset in the wimpy stats table)
  TAX ; tranfer "target type"

  ; LDA #$40 ; original code
  ; SEC : SBC !ENEMY_LEVEL
  ; SBC $8e001d,x ; original code
  LDA !MEMORY_TABLE_MAGIC_DEFEND-!OFFSET_FIRST_ID,x ; example: !MEMORY_TABLE_ATTACK + 00 = wimpy level 1 attack
  
  PLX ; pull "source type"
  PLP

  BRA .doneModifying
  .skipBoyDog

  PLP

  LDA #$40 ; original code
  SBC $8e001d,x ; original code

  .doneModifying

  RTL
experience_calculation:
  TXA ; transfer "source type"

  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PHX ; push "source type"
  
  CLC : ADC !ENEMY_LEVEL ; example: contains 00, 02, …, 48 [49 4a] (offset in the wimpy stats table)
  TAX ; tranfer "source type"

  LDA !MEMORY_TABLE_EXPERIENCE-!OFFSET_FIRST_ID,x ; example: !MEMORY_TABLE_ATTACK + 00 = wimpy level 1 attack

  PLX ; pull "source type"
  REP #$ff

  BRA .doneModifying
  .skipBoyDog

  LDA $8e0023,x ; original code

  .doneModifying

  RTL
money_calculation:
  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PHX ; push "source type"
  
  CLC : ADC !ENEMY_LEVEL ; example: contains 00, 02, …, 48 [49 4a] (offset in the wimpy stats table)
  TAX ; tranfer "source type"

  LDA !MEMORY_TABLE_MONEY-!OFFSET_FIRST_ID,x ; example: !MEMORY_TABLE_ATTACK + 00 = wimpy level 1 attack
  
  PLX ; pull "source type"

  BRA .doneModifying
  .skipBoyDog

  LDA $8e0027,x ; original code

  .doneModifying

  RTL


; ALL UPCOMMING TABLES:
; #$4a (37) per entry (unmodified "monster" stat size)
; currently uses FE9000…FEc000
; available space: fe9000-ffffff

macro pad_monster_stat(number, value)
  ;skip !OFFSET_TABLE_WIMPY ; the first !OFFSET_TABLE_WIMPY (108) entries

  !counter = 0
  while !counter < <number>
    !sub_counter = 0
    while !sub_counter < 37
      dw #<value>
      !sub_counter #= !sub_counter+1
    endwhile

    !counter #= !counter+1
  endwhile
endmacro

org !MEMORY_TABLE_HP
%pad_monster_stat(108+1, 1)
dw #18, #30, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001, #$0001 ; "Wimpy Flower" (109)

org !MEMORY_TABLE_ATTACK
skip !OFFSET_TABLE_WIMPY ; the first !OFFSET_TABLE_WIMPY (108) entries
dw #9, #18, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000 ; "Wimpy Flower" (109)

org !MEMORY_TABLE_DEFEND
skip !OFFSET_TABLE_WIMPY ; the first !OFFSET_TABLE_WIMPY (108) entries
dw #28, #60, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000 ; "Wimpy Flower" (109)

org !MEMORY_TABLE_MAGIC_DEFEND
%pad_monster_stat(108+1, $40)
dw #32, #32, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000 ; "Wimpy Flower" (109)

org !MEMORY_TABLE_EXPERIENCE
skip !OFFSET_TABLE_WIMPY ; the first !OFFSET_TABLE_WIMPY (108) entries
dw #2, #4, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000 ; "Wimpy Flower" (109)

org !MEMORY_TABLE_MONEY
skip !OFFSET_TABLE_WIMPY ; the first !OFFSET_TABLE_WIMPY (108) entries
dw #2, #4, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000, #$0000 ; "Wimpy Flower" (109)

db "-ScaleEnemies"