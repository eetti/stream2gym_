#!/usr/bin/python3

from email.headerregistry import MessageIDHeader
from kafka import KafkaProducer

from queue import Queue
from threading import Thread

from random import seed, randint, gauss

import time
import sys
import logging
import re
import random
import os

msgID = 0

def processProdMsg(q):
	while True:
		msgStatus = q.get()
		kPointerKey = list(msgStatus.keys())
		kPointerValue = list(msgStatus.values())

		try:
			logMsgStatus = kPointerValue[0].get(timeout=5000)
			logging.info('Produced message ID: %s; Value: %s', str(kPointerKey[0]), logMsgStatus)
		except Exception as e:
			logging.info('Message not produced. ID: %s; Error: %s', str(kPointerKey[0]), e)

def processXmlFileMessage(file):
	lines = file.readlines()
	processedFile = ' '
	for line in lines:
		randomNum = str(random.randint(1,999))
		# Randomize values in XML file
		line = re.sub('[0-9]+', randomNum, line)
		processedFile += line
	return processedFile.encode()

def processFileMessage(file):
	message = file.read().encode()
	return message

def readMessageFromFile(filePath):
	file = open(filePath, 'r')
	_, fileExt = os.path.splitext(filePath)

	if(fileExt.lower() == '.xml'):
		message = processXmlFileMessage(file)
	#elif(fileExt.lower == '.svg'):
	#	message = processSvgFile(file)
	else:
		message = processFileMessage(file)

	return message

def generateMessage(mSizeParams):
	if mSizeParams[0] == 'fixed':
		msgSize = int(mSizeParams[1])
	elif mSizeParams[0] == 'gaussian':
		msgSize = int(gauss(float(mSizeParams[1]), float(mSizeParams[2])))
	
		if msgSize < 1:
			msgSize = 1
		
	payloadSize = msgSize - 4
            

	if payloadSize < 0:
		payloadSize = 0

	message = [97] * payloadSize
	return message

def messageProductionSFST(messageFilePath, fileID):
	if(messageFilePath != 'None'):
			message = readMessageFromFile(messageFilePath)
			logging.info("Message Generated From File "+messageFilePath)

	else:
		message = generateMessage(mSizeParams)
		logging.info("Generated Message")
	
	# sending a single file till the duration of the simulation
	separator = 'rrrr '
	sentMessage = message + bytes(separator,'utf-8') + bytes(str(fileID), 'utf-8')       

	return sentMessage

def messageProductionMFST(messageFilePath,fileNumber, topicName):
	if(messageFilePath != 'None'):
			message = readMessageFromFile(messageFilePath)
			logging.info("Message Generated From File "+messageFilePath)

	# separator = 'rrrr '
	# sentMessage = message + bytes(separator,'utf-8') + bytes(str(fileNumber), 'utf-8')

	topicAdd = " Topic: "
	FileNumberAdd = " File: "
	sentMessage = message + bytes(topicAdd,'utf-8')\
         + bytes(str(topicName), 'utf-8')\
            +bytes(FileNumberAdd,'utf-8')\
            + bytes(str(fileNumber), 'utf-8')

	return sentMessage

def messageProductionELTT(messageFilePath, fileID):
	file = open(messageFilePath, 'r')
	return 

try:
	node = sys.argv[1]
	# tClass = int(sys.argv[2])
	mSizeString = sys.argv[3]
	prodInstanceID = sys.argv[2]
	mRate = sys.argv[4]
	nTopics = int(sys.argv[5])

	acks = int(sys.argv[6])
	compression = sys.argv[7]
	batchSize = int(sys.argv[8])
	linger = int(sys.argv[9])
	requestTimeout = int(sys.argv[10])
	bufferMemory = int(sys.argv[11])
	brokerId = sys.argv[12]
	directoryPath = sys.argv[13]  #it will hold the file path/directory path based on producer type SFST or MFST respectively
	prodTopic = sys.argv[14] 
	prodType = sys.argv[15] 
	prodNumberOfFiles = int(sys.argv[16])
	# prodInstanceID = sys.argv[17]

	# node = 'h1'
	# tClass = 1.0
	# mSizeString = 'fixed,10'
	# mRate = 'None'   #1.0
	# nTopics = 1
	# acks = 1
	# compression = 'gzip'   #'None'
	# batchSize = 16384
	# linger = 5000    #0
	# requestTimeout = 100000  #30000
	# bufferMemory = 33554432
	# brokerId = '1'
	# directoryPath = 'use-cases/disconnection/millitary-coordination/'
	# prodTopic = 'topic-0'
	# prodType = 'STANDARD'
	# prodNumberOfFiles = 1
	# prodInstanceID = 1
	# messageFilePath = 'use-cases/disconnection/millitary-coordination/Cars103.xml'

	seed(1)

	# mSizeParams = mSizeString.split(',')
	nodeID = node[1:]
	logDir = 'logs/output'
                         
	logging.basicConfig(filename=logDir+"/prod/"+"prod-node"+nodeID+\
								"-instance"+str(prodInstanceID)+".log",
								format='%(asctime)s %(levelname)s:%(message)s',
								level=logging.INFO) 
	logging.info('here')
	logging.info("node to initiate producer: "+nodeID)
	logging.info("topic name: "+prodTopic)
	logging.info("topic broker: "+brokerId)

	logging.info('producer at node: '+str(nodeID))
	logging.info(nodeID)
	
	logging.info(prodType)
	# logging.info(tClass)
	logging.info(prodTopic)
	logging.info(prodNumberOfFiles)
	logging.info(prodInstanceID)
	
	# Apache Kafka producer parameters
	logging.info(acks)
	logging.info(compression)
	logging.info(batchSize)
	logging.info(linger)
	logging.info(requestTimeout)
	logging.info(bufferMemory)

	# S2G producer parameters
	logging.info(mRate)


	bootstrapServers="10.0.0."+brokerId+":9092"

	# Convert acks=2 to 'all'
	if(acks == 2):
		acks = 'all'

	logging.info("**Configuring KafkaProducer** bootstrap_servers=" + str(bootstrapServers) + 
		" acks=" + str(acks) + " compression_type=" + str(compression) + " batch_size=" + str(batchSize) + 
		" linger_ms=" + str(linger) + " request_timeout_ms=" + str(requestTimeout)  + " buffer_memory=" + str(bufferMemory))

	if(compression == 'None'):
		producer = KafkaProducer(bootstrap_servers=bootstrapServers,
			acks=acks,
			batch_size=batchSize,
			linger_ms=linger,
			request_timeout_ms=requestTimeout,
			buffer_memory=bufferMemory)
	else:
		producer = KafkaProducer(bootstrap_servers=bootstrapServers,
			acks=acks,
			compression_type=compression,
			batch_size=batchSize,
			linger_ms=linger,
			request_timeout_ms=requestTimeout,
			buffer_memory=bufferMemory)

	i = 1
	
	if prodType == "MFST":
		files = os.listdir(directoryPath)
		
		while True:
			if i<= len(files):
				for oneFile in files:
					messageFilePath = directoryPath + oneFile
					sentMessage = messageProductionMFST(messageFilePath, i, prodTopic)
					fileID = "File: " +str(i)
					
					producer.send(prodTopic, sentMessage)

					#log after producing to topic
					logging.info('      File has been sent ->  Topic: %s; File ID: %s', \
										prodTopic, str(fileID))
					logging.info('Topic-name: %s; Message ID: %s; Message: %s', prodTopic, i, sentMessage.decode())
					
					i += 1
					if mRate != "None":
						time.sleep(1.0/float(mRate))

			else:
				continue


	elif prodType == "SFST":
		while True:
			if i <= prodNumberOfFiles:
				sentMessage = messageProductionSFST(directoryPath, i)
				fileID = "File: " +str(i)

				producer.send(prodTopic, sentMessage)
				# log after producing to topic
				logging.info('      File has been sent ->  Topic: %s; File ID: %s', \
				   prodTopic, fileID)
				logging.info('Topic-name: %s; Message ID: %s; Message: %s', prodTopic, i, sentMessage.decode())

				i += 1
				if mRate != "None":
					time.sleep(1.0/float(mRate))
	
	elif prodType == "ELTT":
		msgNo = 1
		while i <= prodNumberOfFiles:  
			with open(directoryPath,'r') as file:
				for count, line in enumerate(file):
					sentMessage = line.encode()
					producer.send(prodTopic, sentMessage)
					
					# log after producing to topic
					logging.info('      Message has been sent ->  Topic: %s; Message ID: %s', \
					prodTopic, str(msgNo))
					logging.info('Topic-name: %s; Message ID: %s; Message: %s', prodTopic, i, sentMessage.decode())

					msgNo += 1
					if mRate != "None":
						time.sleep(1.0/float(mRate))

			i += 1

	elif prodType == "STANDARD":
		msgID = 0
		logging.info("mRate: "+mRate)
		logging.info('producer type: ')
		#Use a queue and a separate thread to log messages that were not produced properly
		q = Queue(maxsize=0)
		prodMsgThread = Thread(target=processProdMsg, args=(q,))
		prodMsgThread.start()

		while True:
			message = generateMessage(mSizeParams)			
			newMsgID = str(msgID).zfill(6)
			bMsgID = bytes(newMsgID, 'utf-8')
			newNodeID = nodeID.zfill(2)
			bNodeID = bytes(newNodeID, 'utf-8')
			bMsg = bNodeID + bMsgID + bytearray(message)

			prodStatus = producer.send(prodTopic, bMsg)
			logging.info('Topic-name: %s; Message ID: %s; Message: %s',\
						prodTopic, newMsgID, message)

			msgInfo = {}
			msgInfo[newMsgID] = prodStatus
			q.put(msgInfo)

			logging.info('Topic: %s; Message ID: %s;', prodTopic, str(msgID).zfill(3))        
			msgID += 1
			if mRate != "None":
				time.sleep(1.0/float(mRate))

except Exception as e:
	logging.error(e)
	sys.exit(1)