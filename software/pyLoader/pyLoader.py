#!/usr/bin/python

import sys
import time

#RaspberryPi: sudo apt-get install python-serial
import serial

PM_SIZE = 1536 #/* Max: 144KB/3/32=1536 PM rows for 30F. */
EE_SIZE = 128 #/* 4KB/2/16=128 EE rows */
CM_SIZE = 8

#BYTESIZE   = 8
#PARITY     = NOPARITY
#STOPBITS   = ONESTOPBIT
#ASCII_XON  = 0x11
#ASCII_XOFF = 0x13

#BUFFER_SIZE         = 4096
#READ_BUFFER_TIMEOUT = 1000

PM30F_ROW_SIZE = 32
#PM33F_ROW_SIZE = 64*8
EE30F_ROW_SIZE = 16

COMMAND_NACK     = 0x00
COMMAND_ACK      = 0x01
COMMAND_READ_PM  = 0x02
COMMAND_WRITE_PM = 0x03
COMMAND_READ_EE  = 0x04
COMMAND_WRITE_EE = 0x05
COMMAND_READ_CM  = 0x06
COMMAND_WRITE_CM = 0x07
COMMAND_RESET    = 0x08
COMMAND_READ_ID  = 0x09

#******************************************************************************

def SendHexFile(comHandle, hexFileHandle):
	buffer = {}
	ppMemory = {}
	extAddr = 0

	for row in range(0, PM_SIZE):
		ppMemory[row] = {'type': 0, 'address': 0x000000, 'buffer': {}, 'data': None, 'byteCount':0}

	for row in range(0, EE_SIZE):
		ppMemory[row + PM_SIZE] = {'type': 1, 'address': 0x7FF000, 'buffer': {}, 'data': None, 'byteCount':0}

	for row in range(0, CM_SIZE):
		ppMemory[row + PM_SIZE + EE_SIZE] = {'type': 2, 'address': 0xF80000, 'buffer': {}, 'data': None, 'byteCount':0}

	print "Reading HexFile"

	line = hexFileHandle.readline()

	row = 0
	while line:
		if line[0] != ':':
			print "Error in file, quiting..."
			quit()

		byteCount = int(line[1:3], 16)
		address = int(line[3:7], 16)
		recordType = int(line[7:9], 16)

		if recordType == 0:
			address = (address + extAddr) / 2
			ppMemory[row]['address'] = address
			ppMemory[row]['byteCount'] = byteCount

			data = line[9:-2]
			ppMemory[row]['data'] = {}
			for i in range(0, byteCount / 2):
				ppMemory[row]['data'][i] = int(data[4*i:4*(i+1)] ,16)
		elif recordType == 1:
			#???
		elif recordType == 4:
			extAddr = int(line[9:13], 16) << 16
		else
			print "Unknown hex record type"

		line = hexFileHandle.readline()

	for row in range(0, len(ppMemory)):
		if ppMemory[row]['type'] == 0:
			for count in range(0, len(ppMemory[row]['data']), 2):
				ppMemory[row]['buffer'][0 + count * 3] = (ppMemory[row]['data'][count * 2]     >> 8) & 0xFF
				ppMemory[row]['buffer'][1 + count * 3] = (ppMemory[row]['data'][count * 2])          & 0xFF
				ppMemory[row]['buffer'][2 + count * 3] = (ppMemory[row]['data'][count * 2 + 1] >> 8) & 0xFF
		elif ppMemory[row]['type'] == 2:
			ppMemory[row]['buffer'][0] = (ppMemory[row]['data'][0]  >> 8) & 0xFF;
			ppMemory[row]['buffer'][1] = (ppMemory[row]['data'][0])       & 0xFF;
			ppMemory[row]['buffer'][2] = (ppMemory[row]['data'][1]  >> 8) & 0xFF;
		else:
			for count in range(0, m_RowSize):
				ppMemory[row]['buffer'][0 + count * 2] = (ppMemory[row]['data'][count * 2] >> 8) & 0xFF;
				ppMemory[row]['buffer'][1 + count * 2] = (ppMemory[row]['data'][count * 2])      & 0xFF;

	print "Programming Device"
	for row in range(0, len (ppMemory)) #PM_SIZE + EE_SIZE + CM_SIZE):
		buffer = [ 0x00 ];
		m_Address = ppMemory[row]['address']
		m_pBuffer = ppMemory[row]['buffer']

#		if((m_bEmpty == TRUE) && (ppMemory[row]['type'] != 2))
#			break

		while(buffer[0] != COMMAND_ACK):
			if(ppMemory[row]['type'] == 0):
				buffer = [ COMMAND_WRITE_PM, (m_Address) & 0xFF, (m_Address >> 8) & 0xFF, (m_Address >> 16) & 0xFF ]
				WriteCommBlock(comHandle, buffer)
				WriteCommBlock(comHandle, m_pBuffer);
			elif(ppMemory[row]['type'] == 1):
				buffer = [ COMMAND_WRITE_EE, (m_Address) & 0xFF, (m_Address >> 8) & 0xFF, (m_Address >> 16) & 0xFF ]
				WriteCommBlock(comHandle, buffer)
				WriteCommBlock(comHandle, m_pBuffer);
			elif((ppMemory[row]['type'] == 2) && (m_RowNumber == 0)):
				buffer = [ COMMAND_WRITE_CM, (char)(m_bEmpty)& 0xFF, m_pBuffer[0], m_pBuffer[1] ]
				WriteCommBlock(comHandle, buffer)
			elif((ppMemory[row]['type'] == 2) && (m_RowNumber != 0)):
				if((m_eFamily == dsPIC30F) && (m_RowNumber == 7))
					break
				buffer = [ (char)(m_bEmpty)& 0xFF, m_pBuffer[0], m_pBuffer[1] ]
				WriteCommBlock(comHandle, buffer)
			else:
				assert(!"Unknown memory type");
				quit()

			buffer = ReceiveData(comHandle, 1);
	
	#Reset target device
	buffer = [ COMMAND_RESET ] 
	WriteCommBlock(comHandle, buffer)

	time.sleep(.1)
	print "Done."

#******************************************************************************

def readID(comHandle):
	deviceId = 0;
	processId = 0;

	buffer = [ COMMAND_READ_ID ];

	print "Reading Target Device ID"
	WriteCommBlock(comHandle, Buffer)
	buffer = ReceiveData(comHandle, 8)

	deviceId  = ((buffer[1] << 8) & 0xFF00) | (buffer[0] & 0x00FF))
	processId = (buffer[5] >> 4) & 0x0F

	#{"PIC24FJ64GA006",    0x405, 3, PIC24F},
	if (deviceId != 0x420F) || (processId != 3):
		print ".. PIC24FJ64GB004 not found! (ID: 0x%04x, processId: 0x%02x" % (deviceId, processId)
		return False
    
	print "..   Found PIC24FJ64GB004 (ID: 0x405)"
	return True

#******************************************************************************

def ReadPM(comHandle, readPMAddress):
	rowSize = PM33F_ROW_SIZE
	readAddress = readPMAddress - readPMAddress % (rowSize * 2);
		
	buffer = [ COMMAND_READ_PM, readAddress & 0xFF, (readAddress >> 8) & 0xFF, (readAddress >> 16) & 0xFF ]

	WriteCommBlock(comHandle, buffer)
	ReceiveData(comHandle, buffer, rowSize * 3)

	for count in range(0, rowSize * 3):
		print "0x%06x:" % hex(readAddress),

		print " %02x" % (buffer[count++] & 0xFF),
		print " %02x" % (buffer[count++] & 0xFF),
		print " %02x" % (buffer[count++] & 0xFF),

		print " %02x" % (buffer[count++] & 0xFF),
		print " %02x" % (buffer[count++] & 0xFF),
		print " %02x" % (buffer[count++] & 0xFF),

		print " %02x" % (buffer[count++] & 0xFF),
		print " %02x" % (buffer[count++] & 0xFF),
		print " %02x" % (buffer[count++] & 0xFF),

		print " %02x" % (buffer[count++] & 0xFF),
		print " %02x" % (buffer[count++] & 0xFF),
		print " %02x" % (buffer[count++] & 0xFF)

		readAddress = readAddress + 8;

#******************************************************************************

def ReadEE(comHandle, readEEAddress):
	readAddress = readEEAddress - readEEAddress % (EE30F_ROW_SIZE * 2);
	
	buffer = [ COMMAND_READ_EE, readAddress & 0xFF, (readAddress >> 8) & 0xFF, (readAddress >> 16) & 0xFF ]

	WriteCommBlock(comHandle, buffer)

	ReceiveData(comHandle, buffer, EE30F_ROW_SIZE * 2)

	for count in (0, EE30F_ROW_SIZE * 2):
		print "0x%06x:", ReadAddress),

		print " %02x" % (Buffer[Count++] & 0xFF),
		print " %02x " % (Buffer[Count++] & 0xFF),

		print " %02x" % (Buffer[Count++] & 0xFF),
		print " %02x " % (Buffer[Count++] & 0xFF),

		print " %02x" % (Buffer[Count++] & 0xFF),
		print " %02x " % (Buffer[Count++] & 0xFF),

		print " %02x" % (Buffer[Count++] & 0xFF),
		print " %02x " % (Buffer[Count++] & 0xFF),

		print " %02x" % (Buffer[Count++] & 0xFF),
		print " %02x " % (Buffer[Count++] & 0xFF),

		print " %02x" % (Buffer[Count++] & 0xFF),
		print " %02x " % (Buffer[Count++] & 0xFF),

		print " %02x" % (Buffer[Count++] & 0xFF),
		print " %02x " % (Buffer[Count++] & 0xFF),

		print " %02x" % (Buffer[Count++] & 0xFF),
		print " %02x",Buffer[Count++] & 0xFF)

		readAddress = readAddress + 16;

#******************************************************************************

def PrintUsage:
	print "\nUsage: \"pyLoader.py\" [-pe] hexfile\n\n"
	print "Options:\n\n"
	print "  -rp\n"
	print "       read program flash. Must provide address to read in HEX format: -p 0x000100"
	print "  -re\n"
	print "       read EEPROM. Must provide address to read in HEX format: -e 0x7FFC00"

#******************************************************************************

def ReceiveData(comHandle, bytesToReceive):
	buffer = comHandle.read(bytesToReceive)
	return buffer

#******************************************************************************

def WriteCommBlock(comHandle, buffer):
	print "."
	if comHandle.write(buffer) < len(buffer):
		return False
	return True

#******************************************************************************

def ReadCommBlock(comHandle, maxLength):
	#/* only try to read number of bytes in queue */
	#ClearCommError(*pComDev, &ErrorFlags, &ComStat);

	buffer = None
	length = min(maxLength, comHandle.inWaiting());
   
	if length > 0:
		buffer = comHandle.read(length)
	else:
		#wait one second
		time.sleep(1);

	return buffer;

#******************************************************************************

def OpenConnection(portName, baudRate):
	return serial.Serial(port=self.device, baudrate=self.baud, timeout=self.timeout

#******************************************************************************

def CloseConnection(comHandle):
	if comHandle != None:
		comHandle.close()

#******************************************************************************

if  __name__ =='__main__':
	comInterface = '/dev/ttyS0'
	baudRate = 115200

	comPort = None
	readPMAddress = None
	readEEAddress = None
	deviceFamily = None
	
	hexFile = None

	#Open connection
	comPort = OpenConnection(comInterface, baudRate)
	if comPort == None:
		print "Opening port " + comInterface + " failed..."
		quit()

	#Parse parameters
	for i in range(1, len(sys.argv)):
		if sys.argv[i] == "-rp":
			i=i+1
			readPMAddress = int(sys.argv[i], 16)
		elif sys.argv[i] == "-re":
			i=i+1
			readEEAddress = int(sys.argv[i], 16)
		else:
			hexFile = file.open(sys.argv[i], 'r')
			if hexFile == None:
				print "Error opening file " + sys.argv[i]
				quit()

	#Read device ID
	deviceFamily = ReadID(comPort);

	if readPMAddress != None:
		ReadPM(comPort, pReadPMAddress, Family)
	elif readEEAddress != None:
		ReadEE(comPort, pReadEEAddress, Family)
	elif hexFile == None:
		print "Please provide HEX file name to read"
		PrintUsage();
	else:
		#Read Hex file and transfer it to target
		SendHexFile(comPort, hexFile)
	
	CloseConnection(comPort)
	if hexFile != None:
		hexFile.close()
