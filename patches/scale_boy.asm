hirom

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!TABLE_ENTRIES = 110 ;

!BOY_HP_ADDRESS = $8c919f ;
!BOY_HP_BASE = 30 ;
!BOY_HP_INCREMENT = 9 ;

!DOG_HP_ADDRESS = $8c9517 ;
!DOG_HP_BASE = 36 ;
!DOG_HP_INCREMENT = 9 ;
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