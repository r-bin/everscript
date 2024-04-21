# Monster Stats

- Act 1:
    - Coleoptera's right claw contains a copy&paste error, compared to the left claw:
        - `2250 hp` vs. `2500 hp`
        - `17 attack` vs. `175 attack` (Same as Thraxx' right claw)
    - NPCs:
        - Both the levitate alchemist and Blimp are called `"Harry"` in the game files (Their names never show up)
- Act 2:
    - NPCs:
        - The two boxers and two drunk inside the ship are all named `"Mad Monk"` in the game files (Their names never show up)
- Act 3:
    - NPCs:
        - The NPC guiding the player through the freak show is called `"Barker"` in the game files (Their names never show up)

# Scripts

- Act 1:
    - Raptors:
        - The active raptor runs to the closes bush, unless it's the bottom right one. Then they choose the top left one
    - Salabog:
        - Has 5 spawn points, but only 3 are reachable
    - Magmar:
        - Has 6(?) spawn points, but only 4 are reachable (`rand(0x5)` instad of `randrange(0d6)`)