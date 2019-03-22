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

		#	CS2 connected to 3.3 v.
		#	WR connected to ground.
		self.CS = 10
		self.RD = 12
		self.IO = [
			8,
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
			18,	
			16
		]

		GPIO.setup(self.CS, GPIO.OUT)
		GPIO.setup(self.RD, GPIO.OUT)

		GPIO.output(self.CS, 1 )
		GPIO.output(self.RD, 1 )


	def intToBinary(self, integer, maxSize=None):
		if(maxSize == None):
			maxSize = len(self.IO)
		binary = "{0:b}".format(integer)
		padding = ((maxSize-len(binary)) * "0")
		binary = padding + binary
		return binary

	def getAddress(self, intaddress):
		GPIO.output(self.CS, 1 )
		GPIO.output(self.RD, 1 )

		'''
			intToBinary gives the least significant bit on the right side.
			We want A0=the least significant bit -> A15=the most significant bit, the easiest way to 
			align the bit values to the correct line is to just reverse the output from intToBinary.
		'''
		address = list(reversed(self.intToBinary(intaddress)))
		for bit in range(len(address)):
			GPIO.setup(self.IO[bit], GPIO.OUT)
			if(int(address[bit]) == 1):
				GPIO.output(self.IO[bit], 1)
			else:
				GPIO.output(self.IO[bit], 0)

		time.sleep(0.001)
		GPIO.output(self.CS, 0 )
		time.sleep(0.001)

		for pin in self.IO:
			GPIO.setup(pin, GPIO.IN)

		time.sleep(0.001)
		GPIO.output(self.RD, 0 )
		time.sleep(0.001)

	def getBus(self):
		valueAtAddress = 0
		for index, inputPin in enumerate(self.IO):
			if(GPIO.input(inputPin) == 1):
				valueAtAddress += 2 ** index
			
		value1 = (valueAtAddress << 8 & 0xFF00) >> 8		
		value2 = (valueAtAddress >> 8 & 0x00FF)
		
		value1 = hex(value1).replace("0x", "")
		value2 = hex(value2).replace("0x", "")

		if(len(value1) % 2 == 1):
			value1 = "0" + value1

		if(len(value2) % 2 == 1):
			value2 = "0" + value2

		return value1, value2

	def highLowRD(self):
		GPIO.output(self.RD, 1 )
		time.sleep(0.01)
		GPIO.output(self.RD, 0 )
		time.sleep(0.01)

	def sequential(self, start, finish):
		self.getAddress(start)
		
		for i in range(start, finish):
			busvalue = self.getBus()
			
			yield (binascii.a2b_hex(busvalue[0]))
			yield (binascii.a2b_hex(busvalue[1]))

			if(self.progress != None):
				self.progress.tick()
			self.highLowRD()

	def nonSequential(self, start, finish):		
		for address in range(start, finish):
			self.getAddress(address)
			busvalue = self.getBus()
			
			yield (binascii.a2b_hex(busvalue[0]))
			yield (binascii.a2b_hex(busvalue[1]))

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
		for byte in self.nonSequential(0x50, 0x50 + 6):
			name.append(byte.decode())	
		return "".join(name).replace("\x00", "").replace(" ", "_")

	def getROM(self):
		name = self.decideName(self.getName())
		outputFile = open(name, "wb")
		startTime = time.time()
		
		maxAddress = 0x800000
		self.progress = progressBar(0,  maxAddress)
		for byte in cartridge.nonSequential(0x000, maxAddress):
			outputFile.write(byte)

		outputFile.close()
		GPIO.cleanup()
		print("")
		print("Done (time {} mins)".format( int(time.time()-startTime) / 60) )	

if __name__ == "__main__":
	cartridge = Cartridge()
	cartridge.getROM()

