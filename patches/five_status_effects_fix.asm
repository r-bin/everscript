hirom

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!ROM_EXTENSION = $FE7000 ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; after status effect is being applied
org $91ad0e
  ; PLY (1 bytes)
  ; INY (1 bytes)
  ; INY (1 bytes)
  ; BRA $91ACF6 (2 bytes)
  JML fix_status_effects ; size 4
  NOP

org !ROM_EXTENSION
db "+5StatusEffects"

macro remove_flag(character_byte, flag)
  LDA <character_byte>,Y
  AND #~<flag>
  STA <character_byte>,Y
endmacro

macro remove_outline(flag)
  LDA #$0000

  STA $009e,Y ; reset outline timer (to prevent lingering colors)

  %remove_flag($009a, <flag>)
endmacro

macro fix_flag(status_id, character_byte, character_flag, outline_id)
  LDA $0046,Y ; status effect #1
  AND #$00ff
  CMP #<status_id> : BEQ ?not_fix_status
  
  LDA $004c,Y ; status effect #1
  AND #$00ff
  CMP #<status_id> : BEQ ?not_fix_status
  
  LDA $0052,Y ; status effect #1
  AND #$00ff
  CMP #<status_id> : BEQ ?not_fix_status
  
  LDA $0058,Y ; status effect #1
  AND #$00ff
  CMP #<status_id> : BEQ ?not_fix_status
  
  %remove_flag(<character_byte>, <character_flag>)
  %remove_outline(<outline_id>)

  ?not_fix_status
endmacro
macro fix_stat(status_id, stat_boy, stat_dog, boost, outline_id)
  LDA $0046,Y ; status effect #1
  AND #$00ff
  CMP #<status_id> : BEQ ?not_fix_status
  
  LDA $004c,Y ; status effect #1
  AND #$00ff
  CMP #<status_id> : BEQ ?not_fix_status
  
  LDA $0052,Y ; status effect #1
  AND #$00ff
  CMP #<status_id> : BEQ ?not_fix_status
  
  LDA $0058,Y ; status effect #1
  AND #$00ff
  CMP #<status_id> : BEQ ?not_fix_status

  TYA ; target stats
  CMP #$4e89 : BNE ?not_boy
    LDA <stat_boy>
    SEC : SBC <boost>,Y
    STA <stat_boy>

    BRA ?not_dog
  ?not_boy

  CMP #$4F37 : BNE ?not_dog
    LDA <stat_dog>
    SEC : SBC <boost>,Y
    STA <stat_dog>
  ?not_dog

  LDA #$0000
  STA <boost>,Y

  %remove_outline(<outline_id>)

  ?not_fix_status
endmacro

macro fix_all_status_effects()
  %fix_stat($0000, $0A3F, $0A89, $00a0, $0001) ; atlas
  %fix_stat($0018, $0A41, $0A8B, $00a2, $0010) ; defend
  %fix_stat($0048, $0A47, $0A91, $00a4, $0008) ; speed (hit%)
  %fix_stat($0048, $0A45, $0A8F, $00a6, $0008) ; speed (evasion)

  %fix_flag($0008, $0014, $0001, $0002) ; aura
  %fix_flag($0010, $0014, $0004, $0004) ; barrier
  ; %fix_flag($0020, $0014, $????, $0020) ; energize (neither flag nor stat)
  %fix_flag($0028, $0014, $0002, $0040) ; force_field
  %fix_flag($0030, $0014, $0040, $0080) ; reflect
  %fix_flag($0038, $0013, $0020, $0100) ; shield
  ; %fix_flag($0040, $0014, $????, $0400) ; regrowth (neither flag nor stat)
  %fix_flag($0050, $00ac, $0001, $0200) ; pixie dust (neither flag nor stat)
endmacro

fix_status_effects:
  ; IN: A=??, X=0, Y=4e89=target(BOY)

  PHA
  
  %fix_all_status_effects()

  PLA

  PLY ; original code
  INY ; original code
  INY ; original code
  JML $91ACF6 ; original code (BRA -> JML)

db "-5StatusEffects"