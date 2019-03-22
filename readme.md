### Cartridge reader for the Game Boy
This repository contains code for interacting with the Game Boy cartridge MBC. You need a Raspberry Pi 3 and a cartridge slot for the Game Boy (you can buy this cheaply online). You probably have to solder some wires onto the pins on the cartridge slot to be able to connect it to the Raspberry Pi. I have tested it on the Game Boy, Game Boy Color and Game Boy Advance cartridges that I have and things seems to work flawlessly.

### Usage
1. 	**Game Boy (Color)**, change the "romBanks" variable to the number of ROM banks that your cartridge have ( http://gbdev.gg8.se/wiki/articles/The_Cartridge_Header ). 
	**Game boy Advance**, change the number 0x800000 depending on the size of the game.
2. Run the code for Game Boy (Color)
    > python3 GBC.py
   Run the code for Game Boy Advance
    > python3 GBA.py

### Notes
* GBA have support for two modes nonSequential and sequential. The sequential mode is faster, but it seems more unstable (maybe longer delays can fix that).
* Check the __init__ of the classes for the GPIO layout.
* Currently no plans for adding support for reading/writing save files, but I can add it if there is a demand.
* I changed my coding style after this project :=)

***No warranty is given. No complaints will be answered.***