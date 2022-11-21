#!/usr/bin/python3

from kafka import KafkaConsumer

from random import seed, randint, random

import sys
import time

import logging


try:
	seed(2)

	nodeName = sys.argv[1]
	topicName = sys.argv[2]
	brokerId = sys.argv[3]
	consInstance = sys.argv[4]

	nodeID = nodeName[1:]

	tClass = 1.0
	mSizeString = 'fixed,10'
	mRate = 1.0
	nTopics = 1

	acks = 1
	compression = 'None'
	batchSize = 16384
	linger = 0
	requestTimeout = 30000
	brokers = 2
	messageFilePath = 'None'
	nSwitches = 1
	consumptionLag = random() < 0.95
	
	cRate = 0.5
	fetchMinBytes = 1
	fetchMaxWait = 500
	sessionTimeout = 10000

	timeout = int((1.0/cRate) * 1000)

	logDir = "logs/output"
    
	logging.basicConfig(filename=logDir+"/cons/"+"cons-node"+nodeID+\
		"-instance"+str(consInstance)+".log",\
		format='%(asctime)s %(levelname)s:%(message)s',\
		level=logging.INFO)    
	logging.info("Individual consumer")
	logging.info("node to initiate consumer: "+nodeID)
	logging.info("topicName "+topicName)
	logging.info("topicBroker "+brokerId)

	while True:
		bootstrapServers="10.0.0."+brokerId+":9092"
		# bootstrapServers="10.0.0."+nodeID+":9092"
		
		if consumptionLag == True:
				consumer = KafkaConsumer(topicName,
			 		bootstrap_servers=bootstrapServers,
			 		#auto_offset_reset='earliest',
			 		enable_auto_commit=True,
			 		consumer_timeout_ms=timeout,
			 		fetch_min_bytes=fetchMinBytes,
			 		fetch_max_wait_ms=fetchMaxWait,
			 		session_timeout_ms=sessionTimeout,
			 		group_id="group-"+str(nodeID)+"-instance"+str(consInstance)
					)
		else:
				consumer = KafkaConsumer(topicName,
			 		bootstrap_servers=bootstrapServers,
			 		auto_offset_reset='earliest',
			 		enable_auto_commit=True,
			 		consumer_timeout_ms=timeout,
			 		fetch_min_bytes=fetchMinBytes,
			 		fetch_max_wait_ms=fetchMaxWait,
			 		session_timeout_ms=sessionTimeout,
			 		group_id="group-"+str(nodeID)+"-instance"+str(consInstance)                                     
					)


		logging.info('Connect to broker looking for topic %s. ', topicName)
		i = 1

		for msg in consumer:
			msgContent = str(msg.value, 'utf-8', errors='ignore')
			prodID = msgContent[:2] 
			msgID = msgContent[2:8] 
			
			topic = msg.topic
			offset = str(msg.offset)
			
			logging.info("Message received: " + msgContent)
			logging.info('Prod ID: %s; Message ID: %s; Latest: %s; Topic: %s; Offset: %s; Size: %s',\
				 prodID, str(msgID), str(consumptionLag), topic, offset, str(len(msgContent)))
            
			i += 1

except Exception as e:
	logging.error(e)
	sys.exit(1)