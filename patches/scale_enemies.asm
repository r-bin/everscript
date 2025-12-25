hirom

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; DESCRIPTION                                                                                                           ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; - The games has 142 sprite IDs: (Corresponds to ID=0…141 from the SoETilesViewer, contains 0x4a bytes of data each)
;   - boy = 0A26? B678? (0)
;   - …
;   - FE = b9f0 (12)
;   - … (96)
;   - flower_orange = d5b0 (108)
;   - flower_purple = d5fa (109)
;   - raptor_purple = d644 (110)
;   - … (31)
;   - carltron = df3a (141)
; - There are at least two special sprites, that are being excluded from any calculations
;   - !ID_BOY = #$0a26
;   - !ID_DOG = #$0a70
; - The scaling covers:
;   - HP (Triggered when the entity spawns, also injects the sprites level)
;   - Attack
;   - Defend
;   - Magic Defend
;   - Experience (Triggers twice after killing an enemy)
;   - Money (Triggers a "Received {x} {current_currency}" message for x>=500)
; - At the bottom is the table for all stats
;   - 142 * 37 entries of 2 bytes
;   - Default value is 0 (HP has to be 1 for enemies to spawn)
; - The memory map is very wasteful and unoptimized at the moment
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!ROM_EXTENSION = $FE8000 ; 
!ENEMY_LEVEL = $2700 ; has to be set before add_enemy() is being called (before the HP is being defined, which is on spawn)
!ENEMY_PALETTE = $2702 ; just for debugging
!ENEMY_SPRITE_LEVEL_OFFSET = $008a ; sprite data to store the level (sprite+0x8a seems to be unused for normal enemies)
!ENEMY_LEVEL_COUNT = 37 ; reuses the !ENEMY_SPRITE_LEVEL_OFFSET bytes, which resulsts in 37 available levels
;
!WITH_INVERTED_MAGIC_DEFEND = 0 ; currently disabled, because calculating $40-x was too difficult
!WITH_DEBUG_PALETTE = 0 ; enemy palette = !ENEMY_PALETTE
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

!MEMORY_TABLE_HP := !ROM_EXTENSION+$1000+($4000*0)
!MEMORY_TABLE_ATTACK := !ROM_EXTENSION+$1000+($4000*1)
!MEMORY_TABLE_DEFEND := !ROM_EXTENSION+$1000+($4000*2)
!MEMORY_TABLE_MAGIC_DEFEND := !ROM_EXTENSION+$1000+($4000*3)
!MEMORY_TABLE_EXPERIENCE := !ROM_EXTENSION+$1000+($4000*4)
!MEMORY_TABLE_MONEY := !ROM_EXTENSION+$1000+($4000*5)

!OFFSET_FIRST_ID = $B678
!OFFSET_TABLE_WIMPY = $d5fa-!OFFSET_FIRST_ID
!SIZE_MONSTER_BLOCK = $4a

!ID_BOY = #$0a26
!ID_DOG = #$0a70

!M7A = $00211b
!M7B = $00211c
!MPYM = $002135

org $90cd44
  if !WITH_DEBUG_PALETTE
    JSL hook_palette_calculation ; size 4
  endif

; hp calculation (when sprite is created, includes boy and dog)
org $8fb15b
  JSL hp_calculation ; size 4

; attack calculation (when hit, instantly dies at 0hp, includes boy and dog)
org $8fc041
  NOP ; TAX (size 1)
  JSL attack_calculation ; LDA $8e0019,x (size 4)

; defend calculation (when hit, includes boy and dog)
org $8fc072
  JSL defend_calculation ; size 4

; magic defend calculation (when hit)
; range: #$40 - x (min: 0, max: 64/65473)
org $919cce
    NOP ; LDA #$40 (size 2)
    JML magic_defend_calculation ; SBC $8e001d,x (size 4)
    magic_defend_calculation_return:
    NOP
    NOP ; STA M7B (size 4)
    NOP
    NOP
    NOP
    NOP ; REP #$30 (size 2)
    NOP
    NOP ; LDA MPYM (size 4)
    NOP
    NOP
    NOP
    NOP ; PLX (size 1)
  
; experience calculation (when dies)
org $8f8292
  JSL experience_calculation ; LDA $8e0023,x (size 4)
org $8f82d4
  JSL experience_calculation ; LDA $8e0023,x (size 4)
 
; money calculation (when hit, includes boy and dog)
org $8f868e
  JSL money_calculation ; LDA $8e0027,x (size 4)


org !ROM_EXTENSION
db "+ScaleEnemies"

macro get_scaled_value(table, is_negative)
  ; [IN] A:#$____ (source type) X:#$____ y:#$____ (source id)

  if 0
    CLC : ADC !ENEMY_LEVEL ; example: contains 00, 02, …, 48 [49 4a] (offset in the wimpy stats table)
  else
    CLC : ADC !ENEMY_SPRITE_LEVEL_OFFSET,y
  endif

  TAX ; tranfer "source type"
  LDA <table>-!OFFSET_FIRST_ID,x ; example: !MEMORY_TABLE_ATTACK + 00 = wimpy level 1 attack
  
  if <is_negative> > 0
    ; TODO: currently doesn't calculates $40-x, but a weird indirect memory value

    TAX
    SEC : SBC <is_negative>,x
    REP #$ff
  endif
endmacro
macro inject_level()
  LDA !ENEMY_LEVEL
  sta !ENEMY_SPRITE_LEVEL_OFFSET,y
endmacro

hook_palette_calculation:
  LDA !ENEMY_PALETTE

  RTL

hp_calculation:
  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PHX ; push "source type"

  %inject_level()
  TXA
  
  %get_scaled_value(!MEMORY_TABLE_HP, 0)
  
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
  PHY ; push "target id"

  TXY ; transfer "source id"
  %get_scaled_value(!MEMORY_TABLE_ATTACK, 0)

  PLY ; pull "target id"

  BRA .doneModifying
  .skipBoyDog

  PLA ; pull "source type"

  TAX ; original code
  LDA $8e0019,x ; original code

  .doneModifying

  RTL
defend_calculation:
  TXA ; transfer "source type"

  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PHX ; push "source type"
  
  %get_scaled_value(!MEMORY_TABLE_DEFEND, 0)
  
  PLX ; pull "source type"

  BRA .doneModifying
  .skipBoyDog

  LDA $8e001b,x ; original code

  .doneModifying

  RTL
magic_defend_calculation:
  ; [IN]     A:#$____ (unknown) X:#$d5fa (wimpy) Y:#$3364 (unknown)
  ; [DURING] A:#$d5fa (wimpy) (todo) X:#$d5fa (wimpy) Y:#$3364 (unknown)
  ; [DURING] A:#$d5fa (wimpy) (todo) X:#$401d (wimpy id #1) Y:#$3364 (unknown)
  ; [DURING] A:#$d5fa (wimpy) (todo) X:#$401d (wimpy id #1) Y:#$3364 (unknown)  
  ; [DURING] A:#$____ (todo) X:#$d5fa (wimpy) Y:#$401d (wimpy id #1)

  PHP ; push "original flags"
  REP #$ff ; clear "all flags"

  TXA ; transfer "target type" ; TODO: not in memory mode?
  
  PLP ; pull "original flags"
  PLX ; pull "target id" ; TODO: for whatever reason needs to be in memory mode?
  PHX ; push "target id"
  PHP ; push "original flags"
  REP #$ff ; clear "all flags"

  PHY ; push "unknown"
  
  TXY ; transfer "target id"
  TAX ; transfer "target type"
  PHX ; push "target type"

  if !WITH_INVERTED_MAGIC_DEFEND
    %get_scaled_value(!MEMORY_TABLE_MAGIC_DEFEND, $40)
  else
    %get_scaled_value(!MEMORY_TABLE_MAGIC_DEFEND, 0)
  endif

  PLX ; pull "target type"
  PLY ; pull "unknown"
  
  PLP ; pull "original flags"

  STA !M7B ; original code
  REP #$30 ; original code
  LDA !MPYM ; original code
  PLX ; original code

  JML magic_defend_calculation_return ; TODO: JSL and RTL instead of JML and JML back
experience_calculation:
  LDA $28fb
  BIT #$0020
  
  BEQ .withXp ; 

  LDA #$0000
  BRA .doneModifying

  .withXp

  TXA ; transfer "source type"

  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PHX ; push "source type"


  
  %get_scaled_value(!MEMORY_TABLE_EXPERIENCE, 0)

  PLX ; pull "source type"
  REP #$ff

  BRA .doneModifying
  .skipBoyDog

  LDA $8e0023,x ; original code

  .doneModifying

  RTL
money_calculation:
  LDA $28fb
  BIT #$0020
  
  BEQ .withMoney ; 

  LDA #$0000
  BRA .doneModifying

  .withMoney

  TXA
  CMP !ID_BOY : BEQ .skipBoyDog
  CMP !ID_DOG : BEQ .skipBoyDog

  PHX ; push "source type"
  
  %get_scaled_value(!MEMORY_TABLE_MONEY, 0)
  
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

macro default_stats(value)
  !counter = 0
  while !counter < !ENEMY_LEVEL_COUNT
    dw #<value>

    !counter #= !counter+1
  endwhile
endmacro

org !MEMORY_TABLE_HP
  %default_stats(30) ; "<Boy Name>" (0) = 30
  %default_stats(36) ; "<Dog Name>" (1) = 36
  %default_stats(1) ; "Boy" (2) = 1
  %default_stats(1) ; "Girl" (3) = 1
  %default_stats(1) ; "Man" (4) = 1
  %default_stats(1) ; "Woman" (5) = 1
  %default_stats(1) ; "Old man" (6) = 1
  %default_stats(1) ; "Old woman" (7) = 1
  %default_stats(1) ; "Child's Pet" (8) = 1
  %default_stats(1) ; "Child's Pet" (9) = 1
  %default_stats(1) ; "Alchemist" (10) = 1
  %default_stats(1) ; "Harry" (11) = 1
  %default_stats(30) ; "Fire Eyes" (12) = 1
  %default_stats(1) ; "Evil Fire Eyes" (13) = 1
  %default_stats(1) ; "Boy" (14) = 1
  %default_stats(1) ; "Girl" (15) = 1
  %default_stats(1) ; "Man" (16) = 1
  %default_stats(1) ; "Woman" (17) = 1
  %default_stats(1) ; "Old man" (18) = 1
  %default_stats(1) ; "Old woman" (19) = 1
  %default_stats(1) ; "Advisor" (20) = 1
  %default_stats(1) ; "Alchemist" (21) = 1
  %default_stats(1) ; "Horace" (22) = 1
  %default_stats(1) ; "Rock" (23) = 1
  %default_stats(1) ; "Rock" (24) = 1
  %default_stats(1) ; "$0" (25) = 1
  %default_stats(1) ; "$0" (26) = 1
  %default_stats(1) ; "Statue" (27) = 1
  %default_stats(1) ; "Bridge" (28) = 1
  %default_stats(1) ; "Legendary boy" (29) = 1
  %default_stats(1) ; "Legendary girl" (30) = 1
  %default_stats(1) ; "Legendary Grandma" (31) = 1
  %default_stats(1) ; "Legendary King" (32) = 1
  %default_stats(1) ; "Legendary Man" (33) = 1
  %default_stats(1) ; "Legendary Wiking" (34) = 1
  %default_stats(1) ; "Strongheart" (35) = 1
  %default_stats(1) ; "Madronius" (36) = 1
  %default_stats(30) ; "Horace's Twin" (37) = 30
  %default_stats(30) ; "Carltron" (38) = 30
  %default_stats(30) ; "Gomi" (39) = 30
  %default_stats(30) ; "Tinker Tinderbox" (40) = 30
  %default_stats(30) ; "Professor Ruffleberg" (41) = 30
  %default_stats(30) ; "Camilla Bluegarden" (42) = 30
  %default_stats(30) ; "White Queen" (43) = 30
  %default_stats(10) ; "Barker" (44) = 10
  %default_stats(150) ; "Tiny" (45) = 150
  %default_stats(1) ; "Harry" (46) = 1
  %default_stats(1) ; "Mad Monk" (47) = 1
  %default_stats(1) ; "Mad Monk" (48) = 1
  %default_stats(1) ; "Mad Monk" (49) = 1
  %default_stats(1) ; "Mad Monk" (50) = 1
  %default_stats(120) ; "Bad Dawg" (51) = 120
  %default_stats(200) ; "Skullclaw" (52) = 200
  %default_stats(40) ; "Will o' the Wisp" (53) = 40
  %default_stats(100) ; "Stone Cobra" (54) = 100
  %default_stats(100) ; "Stone Cobra" (55) = 100
  dw #40, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Oglin" (56) = 120
  %default_stats(90) ; "Hedgadillo" (57) = 90
  dw #90, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Bad Boy" (58) = 700
  dw #10, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Tumble Weed" (59) = 60
  %default_stats(100) ; "Mummy Cat" (60) = 100
  %default_stats(100) ; "Red Jelly Bal" (61) = 100
  dw #15, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Lime Slime" (62) = 70
  %default_stats(70) ; "Blue Goo" (63) = 70
  %default_stats(100) ; "Dancin' Fool" (64) = 100
  %default_stats(100) ; "Dancin' Fool" (65) = 100
  %default_stats(300) ; "Neo Greeble" (66) = 300
  %default_stats(30) ; "Greeble" (67) = 30
  %default_stats(30) ; "Guardbot" (68) = 30
  %default_stats(500) ; "Guardbot" (69) = 500
  %default_stats(600) ; "Mechaduster" (70) = 600
  %default_stats(3800) ; "Aegis" (71) = 3800
  %default_stats(400) ; "Tentacle" (72) = 400
  %default_stats(200) ; "Tiny Tentacle" (73) = 200
  %default_stats(2500) ; "Aquagoth" (74) = 2500
  %default_stats(1) ; ""(spark) (75) = 1
  %default_stats(2000) ; "Timberdrake" (76) = 2000
  %default_stats(3200) ; "Sterling" (77) = 3200
  %default_stats(2400) ; "FootKnight" (78) = 2400
  %default_stats(3425) ; "Verminator" (79) = 3425
  dw #1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Rat" (80) = 20
  dw #1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Rat" (81) = 20
  %default_stats(1050) ; "Vigor" (82) = 1050
  %default_stats(1) ; "Rimsala" (83) = 1
  %default_stats(1200) ; "Rimsala" (84) = 1200
  %default_stats(3000) ; "Rimsala" (85) = 3000
  %default_stats(40) ; "Will o' the Wisp" (86) = 40
  %default_stats(1000) ; "Magmar" (87) = 1000
  %default_stats(2600) ; "Megataur" (88) = 2600
  dw #30, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Raptor" (89) = 50
  %default_stats(300) ; "Raptor" (90) = 300
  %default_stats(250) ; "Viper Commander" (91) = 250
  %default_stats(125) ; "Viper" (92) = 125
  %default_stats(200) ; "Rogue" (93) = 200
  dw #30, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Mad Monk" (94) = 60
  %default_stats(160) ; "Son of Set" (95) = 160
  %default_stats(200) ; "Son of Anhur" (96) = 200
  %default_stats(500) ; "Minitaur" (97) = 500
  %default_stats(30) ; "Skelesnail" (98) = 30
  %default_stats(40) ; "Frippo" (99) = 40
  %default_stats(40) ; "Widowmaker" (100) = 40
  %default_stats(74) ; "Sand Spider" (101) = 74
  %default_stats(160) ; "Wood Mite" (102) = 160
  %default_stats(40) ; "Bone Buzzard" (103) = 40
  %default_stats(90) ; "Skullclaw" (104) = 90
  %default_stats(50) ; "Tar Skull" (105) = 50
  %default_stats(2000) ; "Salabog" (106) = 2000
  %default_stats(10000) ; "Flowering Deaths" (107) = 10000
  %default_stats(30) ; "Carniflower" (108) = 30
  %default_stats(18) ; "Wimpy Flower" (109) = 18
  dw #20, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Raptor" (110) = 40
  %default_stats(150) ; "Gore Grub" (111) = 150
  %default_stats(30) ; "Maggot" (112) = 30
  %default_stats(1) ; "Mosquito" (113) = 1
  %default_stats(1) ; "Mosquito" (114) = 1
  %default_stats(5000) ; "Mungola" (115) = 5000
  dw #150, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Old Nick" (116) = 500
  dw #200, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ;  "Mephista" (117) = 500
  %default_stats(600) ; "Thraxx's Heart" (118) = 600
  %default_stats(6000) ; "Coleoptera's Heart" (119) = 6000
  %default_stats(2250) ; "Right Claw" (120) = 2250
  %default_stats(2500) ; "Left Claw" (121) = 2500
  %default_stats(250) ; "Right Claw" (122) = 250
  %default_stats(250) ; "Left Claw" (123) = 250
  %default_stats(4000) ; "Face" (124) = 4000
  %default_stats(300) ; "Gargon" (125) = 300
  %default_stats(300) ; "Dragoil" (126) = 300
  %default_stats(700) ; "Floating Fans" (127) = 700
  %default_stats(1000) ; "Sphere Bot" (128) = 1000
  %default_stats(2500) ; "Fan" (129) = 2500
  %default_stats(1040) ; "Speaker" (130) = 1040
  %default_stats(20) ; "Rat" (131) = 20
  %default_stats(600) ; "Mechaduster" (132) = 600
  %default_stats(400) ; "Tentacle" (133) = 400
  %default_stats(200) ; "Tiny Tentacle" (134) = 200
  %default_stats(200) ; "Bomb" (135) = 200
  dw #40, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Raptor" (136) = 4000
  %default_stats(6000) ; "Death Spider" (137) = 6000
  dw #100, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Eye of Rimsala" (138) = 6000
  dw #150, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Dark Toaster" (139) = 10000
  %default_stats(25000) ; "Magmar" (140) = 25000
  %default_stats(30000) ; "Carltron's Robot" (141) = 30000
org !MEMORY_TABLE_ATTACK
  skip 51*!SIZE_MONSTER_BLOCK
  %default_stats(61) ; "Bad Dawg" (51) = 61
  %default_stats(36) ; "Skullclaw" (52) = 36
  %default_stats(41) ; "Will o' the Wisp" (53) = 41
  %default_stats(88) ; "Stone Cobra" (54) = 88
  %default_stats(88) ; "Stone Cobra" (55) = 88
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Oglin" (56) = 47
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; ; "Hedgadillo" (57) = 53
  dw #8, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Bad Boy" (58) = 85
  %default_stats(23) ; "Tumble Weed" (59) = 23
  %default_stats(41) ; "Mummy Cat" (60) = 41
  %default_stats(110) ; "Red Jelly Bal" (61) = 110
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Lime Slime" (62) = 31
  dw #20, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1, #$1 : dw #$1, #$1, #$1, #$1, #$1, #$1, #$1 ; "Blue Goo" (63) = 42
  %default_stats(50) ; "Dancin' Fool" (64) = 50
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Dancin' Fool" (65) = 50
  %default_stats(117) ; "Neo Greeble" (66) = 117
  %default_stats(0) ; "Greeble" (67) = 0
  %default_stats(15) ; "Guardbot" (68) = 2
  %default_stats(125) ; "Guardbot" (69) = 125
  %default_stats(85) ; "Mechaduster" (70) = 85
  %default_stats(20) ; "Aegis" (71) = 20
  %default_stats(52) ; "Tentacle" (72) = 52
  %default_stats(32) ; "Tiny Tentacle" (73) = 32
  %default_stats(0) ; "Aquagoth" (74) = 0
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; ""(spark) (75) = 32
  %default_stats(86) ; "Timberdrake" (76) = 86
  %default_stats(71) ; "Sterling" (77) = 71
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "FootKnight" (78) = 55
  dw #30, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Verminator" (79) = 0
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rat" (80) = 30
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rat" (81) = 35
  dw #15, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Vigor" (82) = 53
  %default_stats(0) ; "Rimsala" (83) = 0
  dw #7, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rimsala" (84) = 40
  %default_stats(145) ; "Rimsala" (85) = 145
  %default_stats(13) ; "Will o' the Wisp" (86) = 13
  %default_stats(37) ; "Magmar" (87) = 37
  dw #30, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Megataur" (88) = 70
  dw #15, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Raptor" (89) = 27
  %default_stats(80) ; "Raptor" (90) = 80
  dw #15, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Viper Commander" (91) = 30
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Viper" (92) = 25
  %default_stats(53) ; "Rogue" (93) = 53
  dw #15, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Mad Monk" (94) = 28
  %default_stats(36) ; "Son of Set" (95) = 36
  %default_stats(41) ; "Son of Anhur" (96) = 41
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Minitaur" (97) = 56
  %default_stats(14) ; "Skelesnail" (98) = 14
  %default_stats(18) ; "Frippo" (99) = 18
  %default_stats(14) ; "Widowmaker" (100) = 14
  %default_stats(33) ; "Sand Spider" (101) = 33
  %default_stats(47) ; "Wood Mite" (102) = 47
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Bone Buzzard" (103) = 28
  %default_stats(47) ; "Skullclaw" (104) = 47
  %default_stats(18) ; "Tar Skull" (105) = 18
  %default_stats(32) ; "Salabog" (106) = 32
  %default_stats(2125) ; "Flowering Deaths" (107) = 2125
  %default_stats(17) ; "Carniflower" (108) = 17
  %default_stats(9) ; "Wimpy Flower" (109) = 9
  %default_stats(11) ; "Raptor" (110) = 11
  %default_stats(88) ; "Gore Grub" (111) = 88
  %default_stats(12) ; "Maggot" (112) = 12
  %default_stats(2) ; "Mosquito" (113) = 2
  %default_stats(175) ; "Mosquito" (114) = 175
  %default_stats(0) ; "Mungola" (115) = 0
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Old Nick" (116) = 78
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Mephista" (117) = 78
  %default_stats(0) ; "Thraxx's Heart" (118) = 0
  %default_stats(0) ; "Coleoptera's Heart" (119) = 0
  %default_stats(17) ; "Right Claw" (120) = 17 (vanilla bug)
  %default_stats(175) ; "Left Claw" (121) = 175
  %default_stats(17) ; "Right Claw" (122) = 17
  %default_stats(17) ; "Left Claw" (123) = 17
  %default_stats(0) ; "Face" (124) = 0
  %default_stats(55) ; "Gargon" (125) = 55
  %default_stats(88) ; "Dragoil" (126) = 88
  %default_stats(101) ; "Floating Fans" (127) = 101
  %default_stats(101) ; "Sphere Bot" (128) = 101
  %default_stats(0) ; "Fan" (129) = 0
  %default_stats(0) ; "Speaker" (130) = 0
  %default_stats(35) ; "Rat" (131) = 35
  %default_stats(85) ; "Mechaduster" (132) = 85
  %default_stats(105) ; "Tentacle" (133) = 105
  %default_stats(85) ; "Tiny Tentacle" (134) = 85
  %default_stats(0) ; "Bomb" (135) = 0
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Raptor" (136) = 225
  %default_stats(325) ; "Death Spider" (137) = 325
  dw #15, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Eye of Rimsala" (138) = 175
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Dark Toaster" (139) = 175
  %default_stats(170) ; "Magmar" (140) = 170
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Carltron's Robot" (141) = 220

org !MEMORY_TABLE_DEFEND
  skip 51*!SIZE_MONSTER_BLOCK
  %default_stats(160) ; "Bad Dawg" (51) = 160
  %default_stats(0) ; "Skullclaw" (52) = 0
  %default_stats(160) ; "Will o' the Wisp" (53) = 160
  %default_stats(1200) ; "Stone Cobra" (54) = 1200
  %default_stats(1200) ; "Stone Cobra" (55) = 1200
  dw #50, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Oglin" (56) = 88
  %default_stats(180) ; "Hedgadillo" (57) = 180
  dw #40, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Bad Boy" (58) = 200
  dw #40, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Tumble Weed" (59) = 80
  %default_stats(240) ; "Mummy Cat" (60) = 240
  %default_stats(240) ; "Red Jelly Bal" (61) = 240
  dw #50, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Lime Slime" (62) = 120
  dw #50, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Blue Goo" (63) = 160
  %default_stats(160) ; "Dancin' Fool" (64) = 160
  %default_stats(160) ; "Dancin' Fool" (65) = 160
  %default_stats(200) ; "Neo Greeble" (66) = 200
  %default_stats(0) ; "Greeble" (67) = 0
  %default_stats(0) ; "Guardbot" (68) = 0
  %default_stats(320) ; "Guardbot" (69) = 320
  %default_stats(160) ; "Mechaduster" (70) = 160
  %default_stats(80) ; "Aegis" (71) = 80
  %default_stats(160) ; "Tentacle" (72) = 160
  %default_stats(160) ; "Tiny Tentacle" (73) = 160
  %default_stats(0) ; "Aquagoth" (74) = 0
  %default_stats(0) ; ""(spark) (75) = 0
  %default_stats(120) ; "Timberdrake" (76) = 120
  %default_stats(160) ; "Sterling" (77) = 160
  dw #40, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "FootKnight" (78) = 200
  %default_stats(0) ; "Verminator" (79) = 0
  dw #0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rat" (80) = 120
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rat" (81) = 120
  dw #40, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Vigor" (82) = 100
  %default_stats(0) ; "Rimsala" (83) = 0
  dw #40, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rimsala" (84) = 80
  %default_stats(80) ; "Rimsala" (85) = 80
  %default_stats(40) ; "Will o' the Wisp" (86) = 40
  %default_stats(40) ; "Magmar" (87) = 40
  dw #40, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Megataur" (88) = 120
  %default_stats(48) ; "Raptor" (89) = 48
  %default_stats(48) ; "Raptor" (90) = 48
  dw #40, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Viper Commander" (91) = 92
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Viper" (92) = 80
  %default_stats(40) ; "Rogue" (93) = 40
  %default_stats(80) ; "Mad Monk" (94) = 80
  %default_stats(80) ; "Son of Set" (95) = 80
  %default_stats(120) ; "Son of Anhur" (96) = 120
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Minitaur" (97) = 76
  %default_stats(56) ; "Skelesnail" (98) = 56
  %default_stats(60) ; "Frippo" (99) = 60
  %default_stats(48) ; "Widowmaker" (100) = 48
  %default_stats(48) ; "Sand Spider" (101) = 48
  %default_stats(160) ; "Wood Mite" (102) = 160
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Bone Buzzard" (103) = 80
  %default_stats(80) ; "Skullclaw" (104) = 80
  %default_stats(32) ; "Tar Skull" (105) = 32
  %default_stats(80) ; "Salabog" (106) = 80
  %default_stats(2400) ; "Flowering Deaths" (107) = 2400
  %default_stats(48) ; "Carniflower" (108) = 48
  %default_stats(28) ; "Wimpy Flower" (109) = 28
  %default_stats(32) ; "Raptor" (110) = 32
  %default_stats(12) ; "Gore Grub" (111) = 12
  %default_stats(12) ; "Maggot" (112) = 12
  %default_stats(0) ; "Mosquito" (113) = 0
  %default_stats(0) ; "Mosquito" (114) = 0
  %default_stats(160) ; "Mungola" (115) = 160
  dw #30, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Old Nick" (116) = 100
  %default_stats(0) ; "Mephista" (117) = 0
  %default_stats(0) ; "Thraxx's Heart" (118) = 0
  %default_stats(0) ; "Coleoptera's Heart" (119) = 0
  %default_stats(32) ; "Right Claw" (120) = 32
  %default_stats(32) ; "Left Claw" (121) = 32
  %default_stats(32) ; "Right Claw" (122) = 32
  %default_stats(32) ; "Left Claw" (123) = 32
  %default_stats(800) ; "Face" (124) = 800
  %default_stats(160) ; "Gargon" (125) = 160
  %default_stats(160) ; "Dragoil" (126) = 160
  dw #30, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; ; "Floating Fans" (127) = 300
  %default_stats(80) ; "Sphere Bot" (128) = 80
  %default_stats(1400) ; "Fan" (129) = 1400
  %default_stats(1400) ; "Speaker" (130) = 1400
  %default_stats(120) ; "Rat" (131) = 120
  %default_stats(160) ; "Mechaduster" (132) = 160
  %default_stats(280) ; "Tentacle" (133) = 280
  %default_stats(240) ; "Tiny Tentacle" (134) = 240
  %default_stats(800) ; "Bomb" (135) = 800
  dw #80, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Raptor" (136) = 400
  %default_stats(400) ; "Death Spider" (137) = 400
  dw #0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Eye of Rimsala" (138) = 400
  dw #50, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Dark Toaster" (139) = 240
  %default_stats(360) ; "Magmar" (140) = 360
  dw #50, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Carltron's Robot" (141) = 360

org !MEMORY_TABLE_MAGIC_DEFEND
  skip 51*!SIZE_MONSTER_BLOCK
  %default_stats($40-32) ; "Bad Dawg" (51) = 32
  %default_stats($40-16) ; "Skullclaw" (52) = 16
  %default_stats($40-0) ; "Will o' the Wisp" (53) = 0
  %default_stats($40-51) ; "Stone Cobra" (54) = 51
  %default_stats($40-51) ; "Stone Cobra" (55) = 51
  %default_stats($40-0) ; "Oglin" (56) = 0
  %default_stats($40-38) ; "Hedgadillo" (57) = 38
  %default_stats($40-32) ; "Bad Boy" (58) = 32
  %default_stats($40-0) ; "Tumble Weed" (59) = 0
  %default_stats($40-0) ; "Mummy Cat" (60) = 0
  %default_stats($40-0) ; "Red Jelly Bal" (61) = 0
  dw #$40-0, #$40, #$40, #$40, #$40, #$40, #$40, #$40, #$40, #$40 : dw #$40, #$40, #$40, #$40, #$40, #$40, #$40, #$40, #$40, #$40 : dw #$40, #$40, #$40, #$40, #$40, #$40, #$40, #$40, #$40, #$40 : dw #$40, #$40, #$40, #$40, #$40, #$40, #$40 ; "Lime Slime" (62) = 0
  %default_stats($40-0) ; "Blue Goo" (63) = 0
  %default_stats($40-16) ; "Dancin' Fool" (64) = 16
  %default_stats($40-16) ; "Dancin' Fool" (65) = 16
  %default_stats($40-0) ; "Neo Greeble" (66) = 0
  %default_stats($40-0) ; "Greeble" (67) = 0
  %default_stats($40-0) ; "Guardbot" (68) = 0
  %default_stats($40-32) ; "Guardbot" (69) = 32
  %default_stats($40-57) ; "Mechaduster" (70) = 57
  %default_stats($40-32) ; "Aegis" (71) = 32
  %default_stats($40-12) ; "Tentacle" (72) = 12
  %default_stats($40-16) ; "Tiny Tentacle" (73) = 16
  %default_stats($40-22) ; "Aquagoth" (74) = 22
  %default_stats($40-0) ; ""(spark) (75) = 0
  %default_stats($40-0) ; "Timberdrake" (76) = 0
  %default_stats($40-0) ; "Sterling" (77) = 0
  %default_stats($40-51) ; "FootKnight" (78) = 51
  %default_stats($40-0) ; "Verminator" (79) = 0
  %default_stats($40-38) ; "Rat" (80) = 38
  %default_stats($40-38) ; "Rat" (81) = 38
  %default_stats($40-51) ; "Vigor" (82) = 51
  %default_stats($40-0) ; "Rimsala" (83) = 0
  %default_stats($40-16) ; "Rimsala" (84) = 16
  %default_stats($40-16) ; "Rimsala" (85) = 16
  %default_stats($40-0) ; "Will o' the Wisp" (86) = 0
  %default_stats($40-41) ; "Magmar" (87) = 41
  %default_stats($40-0) ; "Megataur" (88) = 0
  %default_stats($40-38) ; "Raptor" (89) = 38
  %default_stats($40-38) ; "Raptor" (90) = 38
  %default_stats($40-16) ; "Viper Commander" (91) = 16
  %default_stats($40-16) ; "Viper" (92) = 16
  %default_stats($40-48) ; "Rogue" (93) = 48
  %default_stats($40-16) ; "Mad Monk" (94) = 16
  %default_stats($40-16) ; "Son of Set" (95) = 16
  %default_stats($40-32) ; "Son of Anhur" (96) = 32
  %default_stats($40-48) ; "Minitaur" (97) = 48
  %default_stats($40-0) ; "Skelesnail" (98) = 0
  %default_stats($40-32) ; "Frippo" (99) = 32
  %default_stats($40-38) ; "Widowmaker" (100) = 38
  %default_stats($40-48) ; "Sand Spider" (101) = 48
  %default_stats($40-48) ; "Wood Mite" (102) = 48
  %default_stats($40-$ffc1) ; "Bone Buzzard" (103) = $ffc1
  %default_stats($40-$ffc1) ; "Skullclaw" (104) = $ffc1
  %default_stats($40-0) ; "Tar Skull" (105) = 0
  %default_stats($40-32) ; "Salabog" (106) = 32
  %default_stats($40-63) ; "Flowering Deaths" (107) = 63
  %default_stats($40-32) ; "Carniflower" (108) = 32
  %default_stats($40-32) ; "Wimpy Flower" (109) = 32
  %default_stats($40-38) ; "Raptor" (110) = 38
  %default_stats($40-16) ; "Gore Grub" (111) = 16
  %default_stats($40-16) ; "Maggot" (112) = 16
  %default_stats($40-0) ; "Mosquito" (113) = 0
  %default_stats($40-0) ; "Mosquito" (114) = 0
  %default_stats($40-13) ; "Mungola" (115) = 13
  %default_stats($40-0) ; "Old Nick" (116) = 0
  %default_stats($40-0) ; "Mephista" (117) = 0
  %default_stats($40-0) ; "Thraxx's Heart" (118) = 0
  %default_stats($40-0) ; "Coleoptera's Heart" (119) = 0
  %default_stats($40-0) ; "Right Claw" (120) = 0
  %default_stats($40-0) ; "Left Claw" (121) = 0
  %default_stats($40-0) ; "Right Claw" (122) = 0
  %default_stats($40-0) ; "Left Claw" (123) = 0
  %default_stats($40-0) ; "Face" (124) = 0
  %default_stats($40-0) ; "Gargon" (125) = 0
  %default_stats($40-0) ; "Dragoil" (126) = 0
  %default_stats($40-48) ; "Floating Fans" (127) = 48
  %default_stats($40-64) ; "Sphere Bot" (128) = 64
  %default_stats($40-57) ; "Fan" (129) = 57
  %default_stats($40-57) ; "Speaker" (130) = 57
  %default_stats($40-38) ; "Rat" (131) = 38
  %default_stats($40-57) ; "Mechaduster" (132) = 57
  %default_stats($40-12) ; "Tentacle" (133) = 12
  %default_stats($40-16) ; "Tiny Tentacle" (134) = 16
  %default_stats($40-$ffc1) ; "Bomb" (135) = $ffc1
  %default_stats($40-51) ; "Raptor" (136) = 51
  %default_stats($40-57) ; "Death Spider" (137) = 57
  %default_stats($40-0) ; "Eye of Rimsala" (138) = 0
  %default_stats($40-57) ; "Dark Toaster" (139) = 57
  %default_stats($40-0) ; "Magmar" (140) = 0
  %default_stats($40-60) ; "Carltron's Robot" (141) = 60

org !MEMORY_TABLE_EXPERIENCE
  skip 51*!SIZE_MONSTER_BLOCK
  %default_stats(1) ; "Bad Dawg" (51) = 20
  %default_stats(1) ; "Skullclaw" (52) = 20
  %default_stats(1) ; "Will o' the Wisp" (53) = 20
  %default_stats(1) ; "Stone Cobra" (54) = 100
  %default_stats(1) ; "Stone Cobra" (55) = 100
  %default_stats(1) ; "Oglin" (56) = 150
  %default_stats(1) ; "Hedgadillo" (57) = 180
  %default_stats(1) ; "Bad Boy" (58) = 400
  %default_stats(1) ; "Tumble Weed" (59) = 50
  %default_stats(1) ; "Mummy Cat" (60) = 160
  %default_stats(1) ; "Red Jelly Bal" (61) = 600
  %default_stats(1) ; "Lime Slime" (62) = 50
  %default_stats(1) ; "Blue Goo" (63) = 150
  %default_stats(1) ; "Dancin' Fool" (64) = 70
  %default_stats(1) ; "Dancin' Fool" (65) = 70
  %default_stats(1) ; "Neo Greeble" (66) = 500
  %default_stats(1) ; "Greeble" (67) = 0
  %default_stats(1) ; "Guardbot" (68) = 0
  %default_stats(1) ; "Guardbot" (69) = 500
  %default_stats(1) ; "Mechaduster" (70) = 600
  %default_stats(1) ; "Aegis" (71) = 3000
  %default_stats(1) ; "Tentacle" (72) = 500
  %default_stats(1) ; "Tiny Tentacle" (73) = 300
  %default_stats(1) ; "Aquagoth" (74) = 5000
  %default_stats(1) ; ""(spark) (75) = 100
  %default_stats(1) ; "Timberdrake" (76) = 2200
  %default_stats(1) ; "Sterling" (77) = 3300
  %default_stats(1) ; "FootKnight" (78) = 850
  %default_stats(1) ; "Verminator" (79) = 1050
  %default_stats(1) ; "Rat" (80) = 30
  %default_stats(1) ; "Rat" (81) = 30
  %default_stats(1) ; "Vigor" (82) = 1050
  %default_stats(1) ; "Rimsala" (83) = 0
  %default_stats(1) ; "Rimsala" (84) = 1200
  %default_stats(1) ; "Rimsala" (85) = 3000
  %default_stats(1) ; "Will o' the Wisp" (86) = 4
  %default_stats(1) ; "Magmar" (87) = 500
  %default_stats(1) ; "Megataur" (88) = 2500
  %default_stats(1) ; "Raptor" (89) = 24
  %default_stats(1) ; "Raptor" (90) = 290
  %default_stats(1) ; "Viper Commander" (91) = 160
  %default_stats(1) ; "Viper" (92) = 80
  %default_stats(1) ; "Rogue" (93) = 100
  %default_stats(1) ; "Mad Monk" (94) = 20
  %default_stats(1) ; "Son of Set" (95) = 120
  %default_stats(1) ; "Son of Anhur" (96) = 250
  %default_stats(1) ; "Minitaur" (97) = 1000
  %default_stats(1) ; "Skelesnail" (98) = 20
  %default_stats(1) ; "Frippo" (99) = 12
  %default_stats(1) ; "Widowmaker" (100) = 40
  %default_stats(1) ; "Sand Spider" (101) = 72
  %default_stats(1) ; "Wood Mite" (102) = 180
  %default_stats(1) ; "Bone Buzzard" (103) = 300
  %default_stats(1) ; "Skullclaw" (104) = 400
  %default_stats(1) ; "Tar Skull" (105) = 22
  %default_stats(1) ; "Salabog" (106) = 700
  %default_stats(1) ; "Flowering Deaths" (107) = 600
  %default_stats(1) ; "Carniflower" (108) = 6
  %default_stats(1) ; "Wimpy Flower" (109) = 2
  %default_stats(1) ; "Raptor" (110) = 16
  %default_stats(1) ; "Gore Grub" (111) = 85
  %default_stats(1) ; "Maggot" (112) = 4
  %default_stats(1) ; "Mosquito" (113) = 1
  %default_stats(1) ; "Mosquito" (114) = 1
  %default_stats(1) ; "Mungola" (115) = 8000
  %default_stats(1) ; "Old Nick" (116) = 1000
  %default_stats(1) ; "Mephista" (117) = 1000
  %default_stats(1) ; "Thraxx's Heart" (118) = 500
  %default_stats(1) ; "Coleoptera's Heart" (119) = 10000
  %default_stats(1) ; "Right Claw" (120) = 4166
  %default_stats(1) ; "Left Claw" (121) = 4166
  %default_stats(1) ; "Right Claw" (122) = 250
  %default_stats(1) ; "Left Claw" (123) = 250
  %default_stats(1) ; "Face" (124) = 4000
  %default_stats(1) ; "Gargon" (125) = 150
  %default_stats(1) ; "Dragoil" (126) = 150
  %default_stats(1) ; "Floating Fans" (127) = 300
  %default_stats(1) ; "Sphere Bot" (128) = 70
  %default_stats(1) ; "Fan" (129) = 0
  %default_stats(1) ; "Speaker" (130) = 0
  %default_stats(1) ; "Rat" (131) = 30
  %default_stats(1) ; "Mechaduster" (132) = 50
  %default_stats(1) ; "Tentacle" (133) = 500
  %default_stats(1) ; "Tiny Tentacle" (134) = 300
  %default_stats(1) ; "Bomb" (135) = 0
  %default_stats(1) ; "Raptor" (136) = 24
  %default_stats(1) ; "Death Spider" (137) = 5000
  %default_stats(1) ; "Eye of Rimsala" (138) = 1050
  %default_stats(1) ; "Dark Toaster" (139) = 5000
  %default_stats(1) ; "Magmar" (140) = 50000
  %default_stats(1) ; "Carltron's Robot" (141) = 100000

org !MEMORY_TABLE_MONEY
  skip 51*!SIZE_MONSTER_BLOCK
  %default_stats(0) ; "Bad Dawg" (51) = 20
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Skullclaw" (52) = 20
  %default_stats(0) ; "Will o' the Wisp" (53) = 20
  %default_stats(0) ; "Stone Cobra" (54) = 10
  %default_stats(0) ; "Stone Cobra" (55) = 10
  dw #4, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Oglin" (56) = 100
  %default_stats(10) ; "Hedgadillo" (57) = 10
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Bad Boy" (58) = 333
  dw #4, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Tumble Weed" (59) = 40
  %default_stats(0) ; "Mummy Cat" (60) = 60
  %default_stats(0) ; "Red Jelly Bal" (61) = 40
  dw #3, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Lime Slime" (62) = 30
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Blue Goo" (63) = 30
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Dancin' Fool" (64) = 10
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Dancin' Fool" (65) = 10
  %default_stats(0) ; "Neo Greeble" (66) = 0
  %default_stats(0) ; "Greeble" (67) = 0
  %default_stats(5) ; "Guardbot" (68) = 0
  %default_stats(5) ; "Guardbot" (69) = 20
  %default_stats(0) ; "Mechaduster" (70) = 280
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Aegis" (71) = 1200
  %default_stats(0) ; "Tentacle" (72) = 0
  %default_stats(0) ; "Tiny Tentacle" (73) = 0
  dw #30, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Aquagoth" (74) = 0
  %default_stats(1) ; ""(spark) (75) = 0
  dw #30, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Timberdrake" (76) = 2000
  dw #30, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Sterling" (77) = 2000
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "FootKnight" (78) = 200
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Verminator" (79) = 1000
  dw #1, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rat" (80) = 10
  dw #1, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rat" (81) = 10
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Vigor" (82) = 1000
  %default_stats(10) ; "Rimsala" (83) = 0
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rimsala" (84) = 1000
  %default_stats(0) ; "Rimsala" (85) = 1000
  %default_stats(0) ; "Will o' the Wisp" (86) = 4
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Magmar" (87) = 900
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Megataur" (88) = 3000
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Raptor" (89) = 48
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Raptor" (90) = 48
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Viper Commander" (91) = 200
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Viper" (92) = 50
  %default_stats(10) ; "Rogue" (93) = 10
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Mad Monk" (94) = 75
  dw #8, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Son of Set" (95) = 40
  dw #8, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Son of Anhur" (96) = 250
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Minitaur" (97) = 10
  %default_stats(0) ; "Skelesnail" (98) = 15
  dw #2, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Frippo" (99) = 19
  dw #2, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Widowmaker" (100) = 12
  dw #4, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Sand Spider" (101) = 18
  %default_stats(0) ; "Wood Mite" (102) = 30
  dw #7, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Bone Buzzard" (103) = 40
  %default_stats(5) ; "Skullclaw" (104) = 50
  %default_stats(0) ; "Tar Skull" (105) = 17
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Salabog" (106) = 66
  %default_stats(0) ; "Flowering Deaths" (107) = 100
  %default_stats(7) ; "Carniflower" (108) = 7
  %default_stats(2) ; "Wimpy Flower" (109) = 2
  dw #2, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Raptor" (110) = 29
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Gore Grub" (111) = 10
  dw #2, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Maggot" (112) = 4
  %default_stats(1) ; "Mosquito" (113) = 1
  %default_stats(1) ; "Mosquito" (114) = 1
  %default_stats(20) ; "Mungola" (115) = 0
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Old Nick" (116) = 250
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Mephista" (117) = 250
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ;  "Thraxx's Heart" (118) = 750
  %default_stats(0) ; "Coleoptera's Heart" (119) = 4000
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Right Claw" (120) = 400
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Left Claw" (121) = 400
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Right Claw" (122) = 150
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Left Claw" (123) = 150
  dw #20, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Face" (124) = 2000
  %default_stats(0) ; "Gargon" (125) = 60
  dw #10, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Dragoil" (126) = 60
  %default_stats(10) ; "Floating Fans" (127) = 10
  %default_stats(10) ; "Sphere Bot" (128) = 10
  %default_stats(0) ; "Fan" (129) = 0
  %default_stats(0) ; "Speaker" (130) = 0
  dw #2, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ; "Rat" (131) = 10
  %default_stats(0) ; "Mechaduster" (132) = 280
  %default_stats(0) ; "Tentacle" (133) = 0
  %default_stats(0) ; "Tiny Tentacle" (134) = 0
  %default_stats(0) ; "Bomb" (135) = 0
  dw #5, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0, #$0 : dw #$0, #$0, #$0, #$0, #$0, #$0, #$0 ;  "Raptor" (136) = 48
  %default_stats(0) ; "Death Spider" (137) = 250
  %default_stats(0) ; "Eye of Rimsala" (138) = 0
  %default_stats(0) ; "Dark Toaster" (139) = 20
  %default_stats(0) ; "Magmar" (140) = 0
  %default_stats(0) ; "Carltron's Robot" (141) = 0

db "-ScaleEnemies"