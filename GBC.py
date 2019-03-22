import os
import time
import binascii
import RPi.GPIO as GPIO
import sys
import time

class progressBar():
	def __init__(self, currentValue, maxValue):
		self.currentValue = currentValue
		self.maxValue = maxValue
		self.size = 50

	def tick(self):
		self.currentValue += 1

		progress = int(float(self.currentValue)/float(self.maxValue)*self.size)

		paddingSize = len(str(self.maxValue))
		currentProgress = str(int(self.currentValue)).rjust(paddingSize,'0')
		goalProgress = str(int(self.maxValue)).rjust(paddingSize,'0')

		sys.stdout.write("\r" + (currentProgress +"/"+ goalProgress) + ' [' + '#' * progress + ' ' *  (self.size-progress) + ']')

		if(self.currentValue == self.maxValue):
			print("")

class Cartridge():
	def __init__(self):
		GPIO.setmode(GPIO.BOARD)

		self.progress = None

		#	Raspberry Pi GPIO pins (BOARD mode)
		self.WR = 10
		self.RD = 12

		self.IO = [
			18,	
			22,	
			24,	
			26,	
			32,	
			36,	
			38,	
			40,	
			37,	
			35,	
			33,	
			31,	
			29,	
			23,		
			21,
			19,
			15,
			13,
			11,
			7,
			5,
			3,
			8,
			16
		]

		self.output = self.IO[:16] # A0-A15
		self.input = self.IO[16:] #	D0-D7

		GPIO.setup(self.RD, GPIO.OUT)
		GPIO.setup(self.WR, GPIO.OUT)
		
		for inputPin in self.input:
			GPIO.setup(inputPin, GPIO.IN)  
		
		for outputPin in self.output:
			GPIO.setup(outputPin, GPIO.OUT)
			GPIO.output(outputPin, 0)

		self.noReadWrite()

	def noReadWrite(self):
		GPIO.output(self.RD, 1)		
		GPIO.output(self.WR, 1)
		time.sleep(1)

	def read(self):
		GPIO.output(self.RD, 0)		
		GPIO.output(self.WR, 1)
		time.sleep(1)

	def write(self):
		GPIO.output(self.RD, 1)		
		GPIO.output(self.WR, 0)
		time.sleep(1)

	def intToBinary(self, integer, maxSize=None):
		if(maxSize == None):
			maxSize = len(self.output)
		binary = "{0:b}".format(integer)
		padding = ((maxSize-len(binary)) * "0")
		binary = padding + binary
		return binary

	def switchBank(self, bank):
		self.noReadWrite()
		self.read()
		for inputPin in self.input:
			GPIO.setup(inputPin, GPIO.OUT)
			GPIO.output(inputPin, 0)

		'''
		intToBinary gives the least significant bit on the right side.
		We want D0=the least significant bit -> D7=the most significant bit, the easiest way to 
		align the bit values to the correct line is to just reverse the output from intToBinary.
		'''
		binaryBank = list(reversed(self.intToBinary(bank, maxSize=8)))
		for bit in range(len(binaryBank)):
			if(int(binaryBank[bit]) == 1):
				GPIO.output(self.input[bit], 1)
			else:
				GPIO.output(self.input[bit], 0)

		time.sleep(0.0001)

		'''
		intToBinary gives the least significant bit on the right side.
		We want A0=the least significant bit -> A15=the most significant bit, the easiest way to 
		align the bit values to the correct line is to just reverse the output from intToBinary.
		'''
		binaryAddress = list(reversed(self.intToBinary(0x2000)))
		for bit in range(len(binaryAddress)):
			if(int(binaryAddress[bit]) == 1):
				GPIO.output(self.output[bit], 1)
			else:	 
				GPIO.output(self.output[bit], 0)

		time.sleep(0.0001) 

		self.write()
		self.noReadWrite()

		for inputPin in self.input:
			GPIO.output(inputPin, 0)
			GPIO.setup(inputPin, GPIO.IN)

		time.sleep(0.0001)


	def readAddressRange(self, start, end=None):
		if(end == None):
			end = start + 1

		self.read()
		for address in range(start, end):
			'''
			intToBinary gives the least significant bit on the right side.
			We want A0=the least significant bit -> A15=the most significant bit, the easiest way to 
			align the bit values to the correct line is to just reverse the output from intToBinary.
			'''
			binaryAddress = list(reversed(self.intToBinary(address)))
			for bit in range(len(binaryAddress)):
				if(int(binaryAddress[bit]) == 1):
					GPIO.output(self.output[bit], 1)
				else:	 
					GPIO.output(self.output[bit], 0)

			time.sleep(0.0001)

			valueAtAddress = 0
			for index, inputPin in enumerate(self.input):
				if(GPIO.input(inputPin) == 1):
					valueAtAddress += 2**(index)

			time.sleep(0.0001)

			valueAtAddressHex = hex(valueAtAddress).replace("0x","")
			valueAtAddressHex = ("0" + valueAtAddressHex) if(len(valueAtAddressHex) == 1) else valueAtAddressHex

			yield (binascii.a2b_hex(valueAtAddressHex))
		
			if(self.progress != None):
				self.progress.tick()


	def decideName(self, inputName):
		response = input("Do you want to call the rom file, '{}' ?[Y/n]\n".format(inputName))
		if(response.lower() == "y"):
			return inputName
		elif(response.lower() == "n"):
			newName = input("What do you want the file to be called ?\n")
			if(len(newName) > 0):
				return self.decideName(newName)
			else:
				return self.decideName(inputName)	
		else:
			return self.decideName(inputName)


	def getName(self):
		name = []
		for byte in self.readAddressRange(0x0134, 0x0143 + 1):
			name.append(byte.decode())
		return "".join(name).replace("\x00", "").replace(" ", "_")

	def getROM(self):
		outputFile = open(self.decideName(self.getName()), "wb")
		startTime = time.time()
		romBanks = 32
		startAddress = 0
		
		self.progress = progressBar(0,  (0x7FFF + 1) + (0x7FFF-0x4000 + 1) * (romBanks - 2))
		
		for bank in range(1, romBanks):
			self.switchBank(bank)
			if(bank > 1):
				startAddress = 0x4000		

			for byte in self.readAddressRange(startAddress, 0x7FFF + 1):	
				outputFile.write(byte)
		outputFile.close()	
		GPIO.cleanup()

		print("")
		print("Done (time {} mins)".format( int(time.time()-startTime) / 60) )		

if __name__ == "__main__":
	cartridge = Cartridge()
	cartridge.getROM()
