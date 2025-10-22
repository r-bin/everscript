hirom

; Hook into the routine that loads the config ring.
;ORG $8cce5e
ORG $8cce5e
    ADC $928000
    TAX
    LDA $928000,X
    STA $26
    LDA $928002,X
    ; AND #$00FF
    ; STA $28