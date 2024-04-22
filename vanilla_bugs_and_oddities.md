# General
- NPCs:
    - **[UNUSED]** Flag `0x0004` makes enemies untargetable, immune to regular damage, but still interactable with bombs (Presumable for the speakers/vents during the final boss rush?)

# Act 1
- NPCs:
    - **[BUG]** Coleoptera's right claw contains a copy&paste error, compared to the left claw:
        - `2250 hp` vs. `2500 hp`
        - `17 attack` vs. `175 attack` (Same as Thraxx' right claw)
    - **[ODD]** Both the levitate alchemist and Blimp are called `"Harry"` in the game files (Their names never show up)
- Raptors:
    - **[BUG]** The active raptor runs to the closes bush, unless it's the bottom right one. Then they choose the top left one
- Village:
    - **[BUG]** Broken sniff spot: 1 Root (B-trigger #19/Object #1)
- Salabog:
    - **[BUG]** Has 5 spawn points, but only 3 are reachable in the script (`rand(0x5)` instad of `randrange(0d6)`)
- Magmar:
    - **[BUG]** Has 6(?) spawn points, but only 4 are reachable in the script (`rand(0x5)` instad of `randrange(0d6)`)

# Act 2
- NPCs:
    - **[UNUSED]** NPC #36 is named `"Madronius"` (White haired guy, green scarf), but in the camp NPC #32 is being used (White haired guy, purple scarf)
    - **[ODD]** The two boxers and two drunk inside the ship are all named `"Mad Monk"` in the game files (Their names never show up)
    - **[ODD]** NPC #18 and #21 look identical (White haired guy, purple scarf)
    - **[ODD]** NPC #64 and #65 are identical ("Dancin' Fool")

# Act 3
- NPCs:
    - **[ODD]** The NPC guiding the player through the freak show is called `"Barker"` in the game files (Their names never show up)