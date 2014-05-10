#!/usr/bin/python

import sys
import time

#RaspberryPi: sudo apt-get install python-serial
import serial

import RPi.GPIO as GPIO

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
	buf = {}
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
			doNothing =True
		elif recordType == 4:
			extAddr = int(line[9:13], 16) << 16
		else:
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
	for row in range(0, len (ppMemory)): #PM_SIZE + EE_SIZE + CM_SIZE):
		buf = [ 0x00 ];
		m_Address = ppMemory[row]['address']
		m_pBuffer = ppMemory[row]['buffer']

#		if((m_bEmpty == TRUE) && (ppMemory[row]['type'] != 2))
#			break

		while(buf[0] != COMMAND_ACK):
			if(ppMemory[row]['type'] == 0):
				buf = [ COMMAND_WRITE_PM, (m_Address) & 0xFF, (m_Address >> 8) & 0xFF, (m_Address >> 16) & 0xFF ]
				WriteCommBlock(comHandle, buf)
				WriteCommBlock(comHandle, m_pBuffer);
			elif(ppMemory[row]['type'] == 1):
				buf = [ COMMAND_WRITE_EE, (m_Address) & 0xFF, (m_Address >> 8) & 0xFF, (m_Address >> 16) & 0xFF ]
				WriteCommBlock(comHandle, buf)
				WriteCommBlock(comHandle, m_pBuffer);
			elif((ppMemory[row]['type'] == 2) and (m_RowNumber == 0)):
				buf = [ COMMAND_WRITE_CM, (char)(m_bEmpty)& 0xFF, m_pBuffer[0], m_pBuffer[1] ]
				WriteCommBlock(comHandle, buf)
			elif((ppMemory[row]['type'] == 2) and (m_RowNumber != 0)):
				if((m_eFamily == dsPIC30F) and (m_RowNumber == 7)):
					break
				buf = [ (char)(m_bEmpty)& 0xFF, m_pBuffer[0], m_pBuffer[1] ]
				WriteCommBlock(comHandle, buf)
			else:
				print "Unknown memory type"
				quit()

			buf = ReceiveData(comHandle, 1);
	
	#Reset target device
	buf = [ COMMAND_RESET ] 
	WriteCommBlock(comHandle, buf)

	time.sleep(.1)
	print "Done."

#******************************************************************************

def ReadID(comHandle):
	deviceId = 0;
	processId = 0;

	buf = [ COMMAND_READ_ID ];

	print "Reading Target Device ID"
	WriteCommBlock(comHandle, buf)
	buf = ReceiveData(comHandle, 8)

	if len(buf) != 8:
		return False

	deviceId  = (((buf[1] << 8) & 0xFF00) | (buf[0] & 0x00FF))
	processId = (buf[5] >> 4) & 0x0F

	#{"PIC24FJ64GA006",    0x405, 3, PIC24F},
	if (deviceId != 0x420F) or (processId != 3):
		print ".. PIC24FJ64GB004 not found! (ID: 0x%04x, processId: 0x%02x" % (deviceId, processId)
		return False
    
	print "..   Found PIC24FJ64GB004 (ID: 0x405)"
	return True

#******************************************************************************

def ReadPM(comHandle, readPMAddress):
	rowSize = PM30F_ROW_SIZE
	readAddress = readPMAddress - readPMAddress % (rowSize * 2);
	
	buf = [ COMMAND_READ_PM, readAddress & 0xFF, (readAddress >> 8) & 0xFF, (readAddress >> 16) & 0xFF ]

	WriteCommBlock(comHandle, buf)
	buf = ReceiveData(comHandle, rowSize * 3)

	if len(buf) < rowSize * 3:
		print "Error receiving data..."
		quit()

	for count in range(0, rowSize * 3, 12):
		print "0x%06x:" % readAddress,

		print " %02x" % (buf[count+0] & 0xFF),
		print " %02x" % (buf[count+1] & 0xFF),
		print " %02x" % (buf[count+2] & 0xFF),

		print " %02x" % (buf[count+3] & 0xFF),
		print " %02x" % (buf[count+4] & 0xFF),
		print " %02x" % (buf[count+5] & 0xFF),

		print " %02x" % (buf[count+6] & 0xFF),
		print " %02x" % (buf[count+7] & 0xFF),
		print " %02x" % (buf[count+8] & 0xFF),

		print " %02x" % (buf[count+9] & 0xFF),
		print " %02x" % (buf[count+10] & 0xFF),
		print " %02x" % (buf[count+11] & 0xFF)

		readAddress = readAddress + 8;

#******************************************************************************

def ReadEE(comHandle, readEEAddress):
	readAddress = readEEAddress - readEEAddress % (EE30F_ROW_SIZE * 2);
	
	buf = [ COMMAND_READ_EE, readAddress & 0xFF, (readAddress >> 8) & 0xFF, (readAddress >> 16) & 0xFF ]

	WriteCommBlock(comHandle, buf)

	ReceiveData(comHandle, buf, EE30F_ROW_SIZE * 2)

	for count in (0, EE30F_ROW_SIZE * 2, 16):
		print "0x%06x: " % readAddress,

		print " %02x " % (buf[count+0] & 0xFF),
		print " %02x " % (buf[count+1] & 0xFF),

		print " %02x " % (buf[count+2] & 0xFF),
		print " %02x " % (buf[count+3] & 0xFF),

		print " %02x " % (buf[count+4] & 0xFF),
		print " %02x " % (buf[count+5] & 0xFF),

		print " %02x " % (buf[count+6] & 0xFF),
		print " %02x " % (buf[count+7] & 0xFF),

		print " %02x " % (buf[count+8] & 0xFF),
		print " %02x " % (buf[count+9] & 0xFF),

		print " %02x " % (buf[count+10] & 0xFF),
		print " %02x " % (buf[count+11] & 0xFF),

		print " %02x " % (buf[count+12] & 0xFF),
		print " %02x " % (buf[count+13] & 0xFF),

		print " %02x " % (buf[count+14] & 0xFF),
		print " %02x " % (buf[count+15] & 0xFF)

		readAddress = readAddress + 16;

#******************************************************************************

def PrintUsage():
	print "\nUsage: \"pyLoader.py\" [-pe] hexfile\n\n"
	print "Options:\n\n"
	print "  -p\n"
	print "       read program flash. Must provide address to read in HEX format: -p 0x000100"
	print "  -e\n"
	print "       read EEPROM. Must provide address to read in HEX format: -e 0x7FFC00"

#******************************************************************************

def ReceiveData(comHandle, bytesToReceive):
	buf = comHandle.read(bytesToReceive)
	return buf

#******************************************************************************

def PrintChars(text):
	sys.stdout.write(text)
	sys.stdout.flush()

#******************************************************************************

def WriteCommBlock(comHandle, buf):
	PrintChars('.')
	if comHandle.write(bytearray(buf)) < len(buf):
		return False
	return True

#******************************************************************************

def ReadCommBlock(comHandle, maxLength):
	#/* only try to read number of bytes in queue */
	#ClearCommError(*pComDev, &ErrorFlags, &ComStat);

	buf = None
	length = min(maxLength, comHandle.inWaiting());
   
	if length > 0:
		buf = comHandle.read(length)
	else:
		#wait one second
		time.sleep(1);

	return buf;

#******************************************************************************

def OpenConnection(portName, baudRate):
	return serial.Serial(port=portName, baudrate=baudRate, timeout=1)

#******************************************************************************

def CloseConnection(comHandle):
	if comHandle != None:
		comHandle.close()

#******************************************************************************

if  __name__ =='__main__':
	comInterface = '/dev/ttyAMA0'
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

	#Reset microcontroller
	GPIO.setup(7, GPIO.OUT)
	GPIO.output(7, True)
	time.sleep(1)
	GPIO.output(7, False)

	#Parse parameters
	i = 1
	while i < len(sys.argv):
		if sys.argv[i] == "-p":
			i=i+1
			readPMAddress = int(sys.argv[i], 16)
		elif sys.argv[i] == "-e":
			i=i+1
			readEEAddress = int(sys.argv[i], 16)
		else:
			hexFile = open(sys.argv[i], 'r')
			if hexFile == None:
				print "Error opening file " + sys.argv[i]
				quit()
		i=i+1

	#Read device ID
	if not ReadID(comPort):
		print "Error reading deviceID..."
		quit()

	if readPMAddress != None:
		ReadPM(comPort, readPMAddress)
	elif readEEAddress != None:
		ReadEE(comPort, readEEAddress)
	elif hexFile == None:
		print "Please provide HEX file name to read"
		PrintUsage();
	else:
		#Read Hex file and transfer it to target
		SendHexFile(comPort, hexFile)
	
	CloseConnection(comPort)
	if hexFile != None:
		hexFile.close()
