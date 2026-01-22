hirom

incsrc "_evermore.asm"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!ROM_EXTENSION = $FE7000 ;
!WITH_VANILLA_STAT_CALCULATION = 1 ; 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

macro original_code()
  PLY ; (1 byte)
  INY ; (1 byte)
  INY ; (1 byte)
  JML $91ACF6 ; (4 bytes, BRA -> JML)
endmacro

; after status effect is being applied
org $91ad0e
  ; PLY (1 byte)
  ; INY (1 byte)
  ; INY (1 byte)
  ; BRA $91ACF6 (2 bytes)
  JML fix_status_effects ; (4 bytes)
  NOP ; (1 byte)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

org !ROM_EXTENSION
db "+5StatusEffects"

macro remove_flag(character_byte, flag)
  LDA <character_byte>,Y
  AND #~<flag>
  STA <character_byte>,Y
endmacro
macro compare_status(offset_slot, status_id)
  LDA <offset_slot>,Y
  AND #$00ff
  CMP #<status_id>
endmacro

macro fix_entity(entity, stat, boost)
  CMP <entity> : BNE ?end
    LDA <stat>
    SEC : SBC <boost>,Y
    STA <stat>
  ?end
endmacro
macro clear_boost(boost)
  LDA #$0000
  STA <boost>,Y
endmacro
macro clear_outline(flag)
  LDA #$0000
  STA !OFFSET_OUTLINE__TIMER,Y ; reset outline timer (to prevent lingering colors)

  %remove_flag(!OFFSET_OUTLINE, <flag>)
endmacro
macro _fix_boost_status(status_id, stat_boy, stat_dog, boost, outline_id)
  ; IN; X=Y = boy/dog

  ; check status effect #1-#4
  %compare_status(!OFFSET_STATUS_EFFECT_ID_1, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_STATUS_EFFECT_ID_2, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_STATUS_EFFECT_ID_3, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_STATUS_EFFECT_ID_4, <status_id>) : BEQ ?end

  TYA ; A=Y = boy/dog

  if !WITH_VANILLA_STAT_CALCULATION == 0 ; handled by !FUNCTION_UPDATE_STATS
    %fix_entity(!POINTER_BOY, <stat_boy>, <boost>)
    %fix_entity(!POINTER_DOG, <stat_dog>, <boost>)
  endif

  %clear_boost(<boost>)
  %clear_outline(<outline_id>)

  ?end
endmacro
macro fix_boost_status(alchemy, boost)
  %_fix_boost_status(!{STATUS_ID_<alchemy>}, !{BOY_<boost>}, !{DOG_<boost>}, !{OFFSET_BOOST_<boost>}, !{OUTLINE_ID_<alchemy>})
endmacro

macro _fix_flag_status(status_id, character_byte, character_flag, outline_id)
  ; IN; X=Y = boy/dog

  ; check status effect #1-#4
  %compare_status(!OFFSET_STATUS_EFFECT_ID_1, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_STATUS_EFFECT_ID_2, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_STATUS_EFFECT_ID_3, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_STATUS_EFFECT_ID_4, <status_id>) : BEQ ?end
  
  if <character_byte> && <character_flag>
    %remove_flag(<character_byte>, <character_flag>)
  endif
  %clear_outline(<outline_id>)

  ?end
endmacro
macro fix_flag_status(alchemy)
  %_fix_flag_status(!{STATUS_ID_<alchemy>}, !{CHARACTER_STATUS_<alchemy>__OFFSET}, !{CHARACTER_STATUS_<alchemy>__FLAG}, !{OUTLINE_ID_<alchemy>})
endmacro

macro fix_all_status_effects()
  %fix_boost_status(!A_ATLAS, !S_ATTACK)
  %fix_boost_status(!A_DEFEND, !S_DEFENSE)
  %fix_boost_status(!A_SPEED, !S_HIT)
  %fix_boost_status(!A_SPEED, !S_EVASION)

  %fix_flag_status(!A_AURA)
  %fix_flag_status(!A_BARRIER)
  %fix_flag_status(!A_ENERGIZE) ; neither flag nor stat
  %fix_flag_status(!A_FORCEFIELD)
  %fix_flag_status(!A_REFLECT)
  %fix_flag_status(!A_SHIELD)
  %fix_flag_status(!A_REGROWTH) ; neither flag nor stat
  %fix_flag_status(!C_PIXIEDUST) ; uses 2 bytes, but works like a flag
endmacro

fix_status_effects:
  ; IN: A=??, X=Y=entity

  PHA ; store A

  TXA ; A=X = entity
  CMP !POINTER_BOY : BEQ .boy_or_dog
  CMP !POINTER_DOG : BEQ .boy_or_dog
  ; A = boy/dog

  JMP .not_boy_or_dog

  .boy_or_dog %fix_all_status_effects()

  if !WITH_VANILLA_STAT_CALCULATION == 1
    JSL !FUNCTION_UPDATE_STATS
  endif

  .not_boy_or_dog

  PLA ; restore A

  %original_code()

db "-5StatusEffects"