FILENAME 	= main
DEVICE 		= atmega328p
PROGRAMMER 	= usbasp
COMPILER 	= avr-gcc 
COMPILER_FLAGS  = -v -Wall -mmcu=$(DEVICE)
AVRDUDE_PATH	= /mnt/c/avrdude/avrdude.exe
PORT 		= COM4
LOWFUSE		= 0xFF
HIGHFUSE	= 0xDE
EXTFUSE		= 0xFF

default: set_fuses asm upload clean 



asm:
	$(COMPILER) $(COMPILER_FLAGS) -c  $(FILENAME).s -o $(FILENAME).o
	$(COMPILER) $(COMPILER_FLAGS) -o  $(FILENAME).elf $(FILENAME).o
	avr-objcopy -j .data -j .text -O ihex $(FILENAME).elf $(FILENAME).hex
	avr-size --format=avr --mcu=$(DEVICE) $(FILENAME).elf


upload:
	$(AVRDUDE_PATH) -v -p $(DEVICE) -c $(PROGRAMMER) -P $(PORT) -U flash:w:./$(FILENAME).hex:iv


clean: 
	rm $(FILENAME).o
	rm $(FILENAME).elf

set_fuses:
	$(AVRDUDE_PATH)  -v -p $(DEVICE) -c $(PROGRAMMER) -P $(PORT) -B3 -U lfuse:w:$(LOWFUSE):m -U hfuse:w:$(HIGHFUSE):m -U efuse:w:$(EXTFUSE):m
