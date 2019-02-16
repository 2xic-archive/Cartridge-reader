### Cartridge reader for the Game Boy
This repository contains code for interacting with the Game Boy cartridge MBC. You need a Raspberry Pi 3 and a cartridge slot for the Game Boy (you can buy this cheaply online). You probably have to solder some wires onto the pins on the cartridge slot to be able to connect it to the Raspberry Pi. I have tested it on the Game Boy and Game Boy Color cartridges that I have and things seems to work flawlessly.


### Usage
1. Change the "romBanks" variable to the number of ROM banks that your cartridge have ( http://gbdev.gg8.se/wiki/articles/The_Cartridge_Header )
2. Run the code 
    >> python3 code.py

### Notes
Support for reading GBA ROMs will come in next commit. Currently no plans for adding support for reading/writing save files, but I can add it if there is a demand.

***No warranty is given. No complaints will be answered.***