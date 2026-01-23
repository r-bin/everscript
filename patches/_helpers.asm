includeonce

incsrc "_evermore.asm"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; ASAR HELPERS
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; constants used in MESEN with no ASAR pendant
!M7A = $00211b ; "Mode 7 Matrix Registers"
!M7B = $00211c ; "Mode 7 Matrix Registers"
!MPYM = $002135 ; "Multiplication Result Registers"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; CUSTOM EVERSCRIPT LOGIC/CONSTANTS
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; temporarily disable xp and money
; (see CUSTOM_FLAG.NO_XP_NO_MONEY)
!FLAG_NO_XP_NO_MONEY__MEMORY = $28fb
!FLAG_NO_XP_NO_MONEY__BIT = #$0020

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; entity struct extension
; (see ATTRIBUTE)

!OFFSET_ATTRIBUTE_ENEMY_LEVEL = $008a ; injected while spawning
!OFFSET_ATTRIBUTE_SPELL_NAME_DUMP = $0086 ; contains $0000 if physical damage was dealt and $ (see DAMAGE_SOURCE_SPELL, ALCHEMY_TYPE_PROJECTILE and ALCHEMY_TYPE_ANIMATION)

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

macro compare_no_money_no_xp()
  LDA !FLAG_NO_XP_NO_MONEY__MEMORY
  BIT !FLAG_NO_XP_NO_MONEY__BIT
endmacro

macro compare_holding_axe()
  LDA !CURRENT_WEAPON_TYPE
  CMP #$0000+!CURRENT_WEAPON_TYPE__AXE 
endmacro

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; EXPERIMENTAL
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; 10 slots available
struct Hook $FE5000
    .Jump: skip 4
endstruct align 4