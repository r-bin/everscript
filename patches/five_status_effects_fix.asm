hirom

incsrc "_evermore.asm"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; FIVE STATUS EFFECTS FIX                                                                                              ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Patch type: SNES ROM hook/extension patch for Secret of Evermore.                                                    ;;
;;                                                                                                                       ;;
;; What this patch fixes:                                                                                                ;;
;; - Hooks the vanilla "status effect applied" path and adds cleanup when a status expires.                            ;;
;; - Applies cleanup for both playable entities (boy and dog).                                                          ;;
;; - Removes lingering visual outline/glow bits and resets the outline timer.                                           ;;
;; - Clears temporary boost values for stat-based buffs (attack/defense/hit/evasion related boosts).                   ;;
;; - Clears flag-based statuses for ability-style effects (aura/barrier/forcefield/etc.).                              ;;
;;                                                                                                                       ;;
;; Notes on stat handling:                                                                                               ;;
;; - If !WITH_VANILLA_STAT_CALCULATION == 1 (default), vanilla update routine recalculates final stats.                ;;
;; - If !WITH_VANILLA_STAT_CALCULATION == 0, this patch subtracts stored temporary boost values directly.              ;;
;;                                                                                                                       ;;
;; Safety behavior:                                                                                                      ;;
;; - For each status type, cleanup runs only if that status is no longer present in status slots #1..#4.               ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!ROM_EXTENSION = $FE7000 ;
!WITH_VANILLA_STAT_CALCULATION = 1 ; 
!WITH_ATLAS_FIX = 1 ; 
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

macro original_code()
  ; Replays the displaced vanilla bytes, then jumps back to vanilla flow.
  PLY ; (1 byte)
  INY ; (1 byte)
  INY ; (1 byte)
  JML $91ACF6 ; (4 bytes, BRA -> JML)
endmacro

; after status effect is being applied
org $91ad0e
  ; Overwrite the local branch with a long jump into free space.
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
  ; Only subtract boost from the matching entity (boy or dog).
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
  ; Status glows use timer+bit state; clear both to avoid lingering color.
  LDA #$0000
  STA !OFFSET_ATTRIBUTE_OUTLINE__TIMER,Y ; reset outline timer (to prevent lingering colors)

  %remove_flag(!OFFSET_ATTRIBUTE_OUTLINE, <flag>)
endmacro
macro _fix_boost_status(status_id, stat_boy, stat_dog, boost, outline_id)
  ; IN; X=Y = boy/dog

  ; If status is still active in any slot, do nothing.
  %compare_status(!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_1, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_2, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_3, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_4, <status_id>) : BEQ ?end

  TYA ; A=Y = boy/dog

  if !WITH_VANILLA_STAT_CALCULATION == 0 ; otherwise handled by !FUNCTION_UPDATE_STATS
    %fix_entity(!POINTER_BOY, <stat_boy>, <boost>)
    %fix_entity(!POINTER_DOG, <stat_dog>, <boost>)
  endif

  ; Always clear stored boost and the associated outline/glow.
  %clear_boost(<boost>)
  %clear_outline(<outline_id>)

  ?end
endmacro
macro fix_boost_status(alchemy, boost)
  %_fix_boost_status(!{STATUS_ID_<alchemy>}, !{BOY_<boost>}, !{DOG_<boost>}, !{OFFSET_ATTRIBUTE_BOOST_<boost>}, !{OUTLINE_ID_<alchemy>})
endmacro

macro _fix_flag_status(status_id, character_byte, character_flag, outline_id)
  ; IN; X=Y = boy/dog

  ; If status is still active in any slot, do nothing.
  %compare_status(!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_1, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_2, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_3, <status_id>) : BEQ ?end
  %compare_status(!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_4, <status_id>) : BEQ ?end
  
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
  ; Boost statuses: clear temp boost storage (and optionally subtract from live stat).
  if !WITH_ATLAS_FIX == 1
    %fix_boost_status(!A_ATLAS, !S_ATTACK)
  endif
  %fix_boost_status(!A_DEFEND, !S_DEFENSE)
  %fix_boost_status(!A_SPEED, !S_HIT)
  %fix_boost_status(!A_SPEED, !S_EVASION)

  ; Flag statuses: clear state bits and outline state.
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

  ; Run fix logic only for playable entities.
  TXA ; A=X = entity
  CMP !POINTER_BOY : BEQ .boy_or_dog
  CMP !POINTER_DOG : BEQ .boy_or_dog
  ; A = boy/dog

  JMP .not_boy_or_dog

  .boy_or_dog %fix_all_status_effects()

  if !WITH_VANILLA_STAT_CALCULATION == 1
    ; Vanilla post-cleanup stat recomputation path.
    JSL !FUNCTION_UPDATE_STATS
  endif

  .not_boy_or_dog

  PLA ; restore A

  %original_code()

db "-5StatusEffects"