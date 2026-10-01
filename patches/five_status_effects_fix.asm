hirom

incsrc "_evermore.asm"

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; FIVE STATUS EFFECTS FIX                                                                                              ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Patch type: SNES ROM hook/extension patch for Secret of Evermore.                                                    ;;
;;                                                                                                                       ;;
;; The vanilla bug:                                                                                                      ;;
;; - When a status lands in an occupied slot, $91B7FA runs the slot's cleanup handler (table $91AE33,X) before the     ;;
;;   new status is written. It does LDX $02 -- the NEW status id -- instead of the id already in the slot.             ;;
;; - Recasting the same status (refresh) is unaffected: both ids are equal.                                             ;;
;; - Evicting a different status (5th cast) runs the WRONG cleanup: the evicted status never reverts its bonus,       ;;
;;   never removes its outline bit ($9A,X), and never shows its "has worn off" message.                                ;;
;;                                                                                                                       ;;
;; The fix:                                                                                                              ;;
;; - Load the id that is really in the slot, and run its own cleanup handler -- the exact same routine a natural       ;;
;;   expiry runs (message -> revert bonus -> JSL $91B9A7, which frees the slot and removes the outline).               ;;
;; - Evictions are announced ($15D2 = 0); refreshes of the same status stay silent ($15D2 = $FFFF) like vanilla.       ;;
;; - $02 (new status id) is saved/restored around the cleanup, since $91B9A7 reuses $02 as scratch.                    ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; INPUT                                                                                                                 ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;
!ROM_EXTENSION = $FE7000 ;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

; replace a status in an occupied slot (27 bytes, $91B7FA..$91B814)
; IN: A = slot timer pointer, Y = entity, $02 = new status id, DB = $7E
; called by the 4 per-slot stubs at $91B815/$91B81F/$91B829/$91B834
org $91B7FA
  STA $60 ; timer pointer (vanilla)
  INC : INC
  STA $62 ; boost/param pointer (vanilla)
  JSL status_slot_cleanup_prepare ; X = id in slot, $15D2 = message on/off
  PHY
  PEI ($02) ; $91B9A7 (called by every cleanup) overwrites $02
  JSR ($AE33,X) ; cleanup handler of the status that is in the slot
  STZ $15D2
  PLA : STA $02
  PLY
  RTS
warnpc $91B815
padbyte $EA : pad $91B815

;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;;

org !ROM_EXTENSION
db "+5StatusEffects"

status_slot_cleanup_prepare:
  ; IN: $60 = slot timer pointer (slot id word is 2 bytes before it), $02 = new status id, DB = $7E
  ; OUT: X = status id in the slot, $15D2 = 0 (evict: show "has worn off") or $FFFF (refresh: silent)
  LDA $60
  DEC : DEC
  TAX
  LDA $0000,X ; slot id (bank $7E; an $FFFE,X read would cross into $7F)
  AND #$7FFF ; drop the "most recent" bit
  TAX

  LDA #$0000
  CPX $02 : BNE +
    DEC ; same status recast: keep vanilla's silent cleanup
  +
  STA $15D2
  RTL

db "-5StatusEffects"
