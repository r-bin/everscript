includeonce

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; KNOWN SECRET OF EVERMORE CONSTANTS/ADDRESSES
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; useful vanilla functions

!FUNCTION_UPDATE_STATS = $8F8398 ; updates character stats, including charms, status effects and min/max values

; hooks

; TODO

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; entity pointer (static)
; (see ATTRIBUTE)

!POINTER_BOY = #$4e89
!POINTER_DOG = #$4F37

; entity pointer (dynamic)

; TODO: known slots = $3de5…$4DFB

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; boy (addresses corresponding to <BOY>[ATTRIBUTE])
; (see ATTRIBUTE)

!BOY_ATTACK = $0A3F
!BOY_DEFENSE = $0A41
!BOY_EVASION = $0A45
!BOY_HIT = $0A47

; dog (addresses corresponding to <DOG>[ATTRIBUTE])

!DOG_ATTACK = $0A89
!DOG_DEFENSE = $0A8B
!DOG_EVASION = $0A8F
!DOG_HIT = $0A91

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; entity struct
; (see ATTRIBUTE)

!OFFSET_BOOST_ATTACK = $00a0
!OFFSET_BOOST_DEFENSE = $00a2
!OFFSET_BOOST_HIT = $00a4
!OFFSET_BOOST_EVASION = $00a6
!OFFSET_STATUS_EFFECT_ID_1 = $0046
!OFFSET_STATUS_EFFECT_ID_2 = $004c
!OFFSET_STATUS_EFFECT_ID_3 = $0052
!OFFSET_STATUS_EFFECT_ID_4 = $0058
!OFFSET_OUTLINE = $009a
!OFFSET_OUTLINE__TIMER = $009e

; attribute bits
; (see ATTRIBUTE_BITS)

!CHARACTER_STATUS_AURA__OFFSET = $0014
!CHARACTER_STATUS_AURA__FLAG = $0001
!CHARACTER_STATUS_BARRIER__OFFSET = $0014
!CHARACTER_STATUS_BARRIER__FLAG = $0004
!CHARACTER_STATUS_ENERGIZE__OFFSET = -1 ; #????
!CHARACTER_STATUS_ENERGIZE__FLAG = -1 ; #????
!CHARACTER_STATUS_FORCEFIELD__OFFSET = $0014
!CHARACTER_STATUS_FORCEFIELD__FLAG = $0002
!CHARACTER_STATUS_REFLECT__OFFSET = $0014
!CHARACTER_STATUS_REFLECT__FLAG = $0040
!CHARACTER_STATUS_SHIELD__OFFSET = $0013
!CHARACTER_STATUS_SHIELD__FLAG = $0020
!CHARACTER_STATUS_REGROWTH__OFFSET = -1 ; #????
!CHARACTER_STATUS_REGROWTH__FLAG = -1 ; #????
!CHARACTER_STATUS_PIXIEDUST__OFFSET = $00ac
!CHARACTER_STATUS_PIXIEDUST__FLAG = $0001

; status ID (friendly)
; (see STATUS_ID)

!STATUS_ID_ATLAS = $0000
!STATUS_ID_DEFEND = $0018
!STATUS_ID_SPEED = $0048
!STATUS_ID_AURA = $0008
!STATUS_ID_BARRIER = $0010
!STATUS_ID_ENERGIZE = $0020
!STATUS_ID_FORCEFIELD = $0028
!STATUS_ID_REFLECT = $0030
!STATUS_ID_SHIELD = $0038
!STATUS_ID_REGROWTH = $0040
!STATUS_ID_PIXIEDUST = $0050

; status ID (enemy)

; TODO

; outline ID
; (see OUTLINE)

!OUTLINE_ID_ATLAS = $0001
!OUTLINE_ID_AURA = $0002
!OUTLINE_ID_BARRIER = $0004
!OUTLINE_ID_SPEED = $0008
!OUTLINE_ID_DEFEND = $0010
!OUTLINE_ID_ENERGIZE = $0020
!OUTLINE_ID_FORCEFIELD = $0040
!OUTLINE_ID_REFLECT = $0080
!OUTLINE_ID_SHIELD = $0100
!OUTLINE_ID_PIXIEDUST = $0200
!OUTLINE_ID_REGROWTH = $0400

; character type (determines sprite and attributes)
; (see CHARACTER_TYPE)

!TYPE_BOY = #$0a26
!TYPE_DOG = #$0a70

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; alchemy

!A_ATLAS = "ATLAS"
!A_AURA = "AURA"
!A_BARRIER = "BARRIER"
!A_DEFEND = "DEFEND"
!A_ENERGIZE = "ENERGIZE"
!A_FORCEFIELD = "FORCEFIELD"
!A_REFLECT = "REFLECT"
!A_SHIELD = "SHIELD"
!A_SPEED = "SPEED"
!A_REGROWTH = "REGROWTH"

; consumable

!C_PIXIEDUST = "PIXIEDUST"

; stat (attribute)

!S_ATTACK = "ATTACK"
!S_DEFENSE = "DEFENSE"
!S_HIT = "HIT"
!S_EVASION = "EVASION"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
; experimental
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

struct Boy $7E4e89
    .Unknown: skip 16
    .Flags_1: skip 1
    .Flags_2: skip 1
    .Flags_3: skip 1
    .Flags_4: skip 1
    .Flags_5: skip 1
    .Flags_6: skip 1
    .Flags_7: skip 1
endstruct align $ae