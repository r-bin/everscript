# Scripts

- Currency convertion
  - ``"Unnamed Global script 0x55" = (id:55 => addr:0x92cac4)``
    - ``"Unnamed Global script 0x43" = (id:43 => addr:0x92bf96)``
    - ``"Unnamed Global script 0x45" = (id:45 => addr:0x92c0c4)``
    - ``"Unnamed Global script 0x46" = (id:46 => addr:0x92c14e)``
    - ``"Unnamed Global script 0x44" = (id:44 => addr:0x92c031)``

- SoETilesViewer
  - Memory:
    - ``0x23bf = 0x0001`` - Prevents attacking, e.g. villages
  - ``(6c) UNTRACED INSTR for boy with val1=0x5a,val2=0x14`` - Walks to x/y, kind of the same as ``6d``/``6e``
  - ``(78) UNTRACED INSTR for boy, 0x0028 4 changes sprite/animation/...?`` - See Enum ``ANIMATION_ALL``/``ANIMATION_BOY``/``ANIMATION_DOG``/``ANIMATION_PLACEHOLDER``/``ANIMATION_ENEMY``
  - ``(29) CALL 0x92d89b Unnamed ABS script 0x92d89b`` - Fade to night
    - ``(29) CALL 0x92d8c2 Unnamed ABS script 0x92d8c2`` - Fade from night
  - ``(29) CALL 0x92d723 Fade to/from/flash white B?`` - Fade to white
    - ``(29) CALL 0x92d752 Fade to/from/flash white C?``- Fade from white
  - ``(b4) CALL Absolute (24bit) script 0x92df1c ("Unnamed ABS script 0x92df1c") WITH 3 ARGS $249d, $249f, 2`` - Explode area y/x/radius (~30s)
    - ``(29) CALL 0x92df70 Boss kill part`` - Unexplode
  - ``(3f) WRITE last entity ($0341)+x68=0x300, last entity ($0341)+x66=0x1a82 (set script): Puppet damage/kill`` - See Enum ``SCRIPT_TRIGGER``
  - ``(47) UNTRACED INSTR, Open messagebox? slot=0x00 x=0x02 y=0x02 w=0x14 h=0x08`` - Yes, opens message boxes with x/y/w/h (Same for id:``02``/``04``/``05``/``06``/``07``/``09``/``0a``/``0b``/``0d``/``0e``/``13``/``18``)
    - Slot seems to be style, as in 0=borderd, 1=unbordered (but 0 crashes)
  - ``(29) CALL 0x92de75 Some cinematic script (used multiple times)`` - Fade in
  - ``(a3) CALL "Market NPC talk (and others?)" (0x32)`` - Start conversation (lock, face each other)
    - ``(a3) CALL "Market NPC end (and others?)" (0x33)`` - Stop conversation (unlock)
  - ``(ae) UNTRACED INSTR, vals 00 02 18 1d modifies current script`` - arg0=18, arg2=1d
  - ``(a9) UNTRACED INSTR modifies entity dog bits 28`` - See Enum ``ATTRIBUTE_BITS``
  - ``"Unknown 0eac+0 (set in lots of places)" = (id:172b => addr:0x92a4e1)`` - Default loot script (proccesses the rooms drops and rolls a reward)
  - ``(af) CALL Absolute (24bit) script 0x99cc1e ('Unnamed ABS script 0x99cc1e') WITH 4 ARGS $2836, $23b9, $23bb, 20`` - Drag entity to x/y (e.g. black owls during doubles)