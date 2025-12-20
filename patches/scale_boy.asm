hirom

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!TABLE_OFFSET = 1 ; offset to not change level 0
!TABLE_ENTRIES = 111-!TABLE_OFFSET ; starts with level 0 (which is unreachable)

!BOY_HP_ADDRESS = $8c919d+(2*!TABLE_OFFSET) ; table for boy hp
!BOY_HP_BASE = 30 ;
!BOY_HP_INCREMENT = 9 ;

!DOG_HP_ADDRESS = $8c9515+(2*!TABLE_OFFSET) ; table for dog hp
!DOG_HP_BASE = 36 ;
!DOG_HP_INCREMENT = 9 ;

!BOY_ATTACK_ADDRESS = $8c9359+(2*!TABLE_OFFSET) ; table for boy attack
!BOY_ATTACK_BASE = 0 ;
!BOY_ATTACK_INCREMENT = 2 ;
!BOY_ATTACK_DIVISOR = 1 ; allows 0.5 steps

!DOG_ATTACK_ADDRESS = $8c96d1+(2*!TABLE_OFFSET) ; table for dog attack

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

org !BOY_HP_ADDRESS
  !counter = 0
  while !counter < !TABLE_ENTRIES
    dw #!BOY_HP_BASE+(!BOY_HP_INCREMENT*!counter)

    !counter #= !counter+1
  endwhile

org !DOG_HP_ADDRESS
  !counter = 0
  while !counter < !TABLE_ENTRIES
    dw #!DOG_HP_BASE+(!DOG_HP_INCREMENT*!counter)

    !counter #= !counter+1
  endwhile

org !BOY_ATTACK_ADDRESS
  !counter = 0
  while !counter < !TABLE_ENTRIES
    dw #(!BOY_ATTACK_BASE+(!BOY_ATTACK_INCREMENT*!counter)/!BOY_ATTACK_DIVISOR)

    !counter #= !counter+1
  endwhile