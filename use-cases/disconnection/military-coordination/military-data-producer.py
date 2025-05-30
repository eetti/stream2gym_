#!/usr/bin/python3

from kafka import KafkaProducer

from random import seed, randint, gauss
from queue import Queue
from threading import Thread

import time
import sys
import logging
import re
import random
import os
import traceback

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


def readXmlFileMessage(file):
	lines = file.readlines()
	readFile = ' '
	for line in lines:
		readFile += line
	# logging.info("Read xml file is : %s", readFile)
	return readFile

def processXmlMessage(message):
	processedMessage = ' '
	randomNum = str(random.randint(1,999))
	# Randomize values in XML message
	processedMessage = re.sub('[0-9]+', randomNum, message)	
	encodedMessage = processedMessage.encode()	
	return encodedMessage

def processFileMessage(file):
	message = file.read().encode()
	return message

def readMessageFromFile(filePath):
	file = open(filePath, 'r')
	_, fileExt = os.path.splitext(filePath)

	if(fileExt.lower() == '.xml'):
		message = readXmlFileMessage(file)
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

try:
	print("System args ",sys.argv)
	node = sys.argv[1]
	prodInstanceID = sys.argv[2]
	nodeID = node[1:]
	
	tClass = 1.0
	mSizeString = 'fixed,10'
	mRate = 30   #1.0
	nTopics = 2

	acks = 1
	compression = sys.argv[7]
	batchSize = int(sys.argv[8])
	linger = int(sys.argv[9])    #0
	requestTimeout = int(sys.argv[10])  #30000
	bufferMemory = int(sys.argv[11])
	brokers = 10
	messageFilePath = 'use-cases/disconnection/military-coordination/Cars103.xml'
	nSwitches = 10

	logDir = "logs/output"
	print(f"in military-data-producer.py: {logDir}")
	# Apache Kafka producer parameters
	# logging.info(acks)
	# logging.info(compression)
	# logging.info(batchSize)
	# logging.info(linger)
	# logging.info(requestTimeout)
	# logging.info(bufferMemory)
	# logDir = "logs/output"
	# os.makedirs(os.path.join(logDir, "prod"), exist_ok=True)  # Create directory if missing
	# log_file = os.path.join(logDir, "prod", f"prod-node{nodeID}-instance{prodInstanceID}.log")
	# print(f"Logging to: {log_file}")
	# logging.basicConfig(filename=log_file, format='%(asctime)s %(levelname)s:%(message)s', level=logging.INFO, force=True)
	# logging.getLogger().handlers[0].flush()  # Ensure immediate write
	# logging.info("Logging initialized")

	logging.basicConfig(filename=logDir+"/prod/"+"prod-node"+nodeID+\
								"-instance"+str(prodInstanceID)+".log",
								format='%(asctime)s %(levelname)s:%(message)s',
								level=logging.INFO) 
 
	

	seed(1)

	mSizeParams = mSizeString.split(',')
	msgID = 0
         
	logging.info("node: "+nodeID)
	print("node: "+nodeID)
    
	bootstrapServers="10.0.0."+nodeID+":9092"

	# Convert acks=2 to 'all'
	if(acks == 2):
		acks = 'all'

	logging.info("**Configuring KafkaProducer** bootstrap_servers=" + str(bootstrapServers) + 
		" acks=" + str(acks) + " compression_type=" + str(compression) + " batch_size=" + str(batchSize) + 
		" linger_ms=" + str(linger) + " request_timeout_ms=" + str(requestTimeout))


	if(compression == 'None'):
		producer = KafkaProducer(bootstrap_servers=bootstrapServers,
			acks=acks,
			batch_size=batchSize,
			linger_ms=linger,
			request_timeout_ms=requestTimeout)
	else:
		producer = KafkaProducer(bootstrap_servers=bootstrapServers,
			acks=acks,
			compression_type=compression,
			batch_size=batchSize,
			linger_ms=linger,
			request_timeout_ms=requestTimeout)

	# Read the message once and save in cache
	if(messageFilePath != 'None'):
		readMessage = readMessageFromFile(messageFilePath)
		logging.info("Messages generated from file")
	else:
		logging.info("Messages generated")

	#Use a queue and a separate thread to log messages that were not produced properly
	q = Queue(maxsize=0)
	prodMsgThread = Thread(target=processProdMsg, args=(q,))
	prodMsgThread.start()

	while True:
		if(messageFilePath != 'None'):
			message = processXmlMessage(readMessage)
			# print("Message from file: ", message)
		else:
			message = generateMessage(mSizeParams)			
		newMsgID = str(msgID).zfill(6)
		bMsgID = bytes(newMsgID, 'utf-8')
		newNodeID = nodeID.zfill(2)
		bNodeID = bytes(newNodeID, 'utf-8')
		bMsg = bNodeID + bMsgID + bytearray(message)
		topicID = randint(0, nTopics-1)
		topicName = 'topic-'+str(topicID)

		prodStatus = producer.send(topicName, bMsg)
		logging.info('Topic-name: %s; Message ID: %s; Message: %s',\
					topicName, newMsgID, message)

		msgInfo = {}
		msgInfo[newMsgID] = prodStatus
		q.put(msgInfo)

# 		logging.info('Topic: %s; Message ID: %s;', topicName, str(msgID).zfill(3))        
		msgID += 1
		# logging.info(f"mRate type: {type(mRate)}, value: {mRate}")
		time.sleep(1.0/(mRate*tClass))

except Exception as e:
	# traceback.print_exc()
	# print("Error in military-data-producer.py: ", e)
	logging.error(e)
	sys.exit(1)