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

!CURRENT_WEAPON_TYPE = $2360
!CURRENT_WEAPON_TYPE__SWORD = $00
!CURRENT_WEAPON_TYPE__AXE = $02
!CURRENT_WEAPON_TYPE__SPEAR = $04
!CURRENT_WEAPON_TYPE__BAZOOKA = $06

; dog (addresses corresponding to <DOG>[ATTRIBUTE])

!DOG_ATTACK = $0A89
!DOG_DEFENSE = $0A8B
!DOG_EVASION = $0A8F
!DOG_HIT = $0A91

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; entity struct
; (see ATTRIBUTE)

!OFFSET_ATTRIBUTE_BOOST_ATTACK = $00a0
!OFFSET_ATTRIBUTE_BOOST_DEFENSE = $00a2
!OFFSET_ATTRIBUTE_BOOST_HIT = $00a4
!OFFSET_ATTRIBUTE_BOOST_EVASION = $00a6
!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_1 = $0046
!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_2 = $004c
!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_3 = $0052
!OFFSET_ATTRIBUTE_STATUS_EFFECT_ID_4 = $0058
!OFFSET_ATTRIBUTE_OUTLINE = $009a
!OFFSET_ATTRIBUTE_OUTLINE__TIMER = $009e

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

; alchemy type
; (see ALCHEMY_TYPE_*)

!ALCHEMY_TYPE_FLASH = $8756
!ALCHEMY_TYPE_HARD_BALL = $926c

!ALCHEMY_TYPE_FLARE = $8110

!ALCHEMY_TYPE_ACID_RAIN = $86f0
!ALCHEMY_TYPE_ATLAS = $8b2a
!ALCHEMY_TYPE_BARRIER = $944c
!ALCHEMY_TYPE_CALL_UP = $95fa
!ALCHEMY_TYPE_CORROSION = $8f20
!ALCHEMY_TYPE_CRUSH = $8a9c
!ALCHEMY_TYPE_CURE = $85da
!ALCHEMY_TYPE_DEFEND = $872a

!ALCHEMY_TYPE_DOUBLE_DRAIN = $9362
!ALCHEMY_TYPE_DRAIN = $8984
!ALCHEMY_TYPE_ENERGIZE = $9610
!ALCHEMY_TYPE_ESCAPE = $8e22
!ALCHEMY_TYPE_EXPLOSION = $9002
!ALCHEMY_TYPE_FIRE_POWER = $8f8e

!ALCHEMY_TYPE_FORCE_FIELD = $962a
!ALCHEMY_TYPE_HEAL = $886c
!ALCHEMY_TYPE_LANCE = $8e36
!ALCHEMY_TYPE_LASER = $86f0
!ALCHEMY_TYPE_LEVITATE = $896e
!ALCHEMY_TYPE_LIGHTNING_STORM = $91cc
!ALCHEMY_TYPE_MIRACLE_CURE = $920c

!ALCHEMY_TYPE_NITRO = $94f6
!ALCHEMY_TYPE_ONE_UP = $9072
!ALCHEMY_TYPE_REFLECT = $95dc
!ALCHEMY_TYPE_REGROWTH = $90ae
!ALCHEMY_TYPE_REVEALER = $8c5c
!ALCHEMY_TYPE_REVIVE = $8b60
!ALCHEMY_TYPE_SLOW_BURN = $91e6
!ALCHEMY_TYPE_SPEED = $898b

!ALCHEMY_TYPE_STING = $8b10
!ALCHEMY_TYPE_STOP = $9406
!ALCHEMY_TYPE_SUPER_HEAL = $947e

!ALCHEMY_TYPE_HEAT_WAVE = $8164
!ALCHEMY_TYPE_STORM = $81c0
!ALCHEMY_TYPE_LIFE_SPARK = $81da

!ALCHEMY_TYPE_CONFOUND = $82ce
!ALCHEMY_TYPE_REGENERATE = $830e
!ALCHEMY_TYPE_AURA = $8356
!ALCHEMY_TYPE_TIME_WARP = $8200
!ALCHEMY_TYPE_FIRST_AID = $8270

!ALCHEMY_TYPE_PLAGUE = $8416
!ALCHEMY_TYPE_HYPNOTIZE = $84ac
!ALCHEMY_TYPE_SHOCK_WAVE = $837e
!ALCHEMY_TYPE_SHIELD = $83f8

!ALCHEMY_TYPE_RESTORE = $8554
!ALCHEMY_TYPE_ELECTRA_BOLT = $8580
!ALCHEMY_TYPE_DISRUPT = $8512

!ALCHEMY_TYPE_PETAL = $9690
!ALCHEMY_TYPE_NECTAR = $9690
!ALCHEMY_TYPE_HONEY = $9690
!ALCHEMY_TYPE_DOG_BISCUIT = $96d8
!ALCHEMY_TYPE_WINGS = $8e22
!ALCHEMY_TYPE_HERBAL_ESSENCE = $9644
!ALCHEMY_TYPE_PIXIE_DUST = $830e

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

!OFFSET_ALCHEMY_TYPE = $0012 ; see ALCHEMY_TYPE_*
!OFFSET_ALCHEMY_TARGET_1 = $002e
!OFFSET_DAMAGE_SOURCE = $0036
!OFFSET_DAMAGE_SOURCE_TIMER = $0038

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