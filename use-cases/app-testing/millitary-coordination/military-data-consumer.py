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

	consumptionLag = random() < 0.95
    
	logging.basicConfig(filename="logs/output/cons/"+"cons-node"+nodeID+\
		"-instance"+str(consInstance)+".log",\
		format='%(asctime)s %(levelname)s:%(message)s',\
		level=logging.INFO)    
	logging.info("node to initiate consumer: "+nodeID)
	logging.info("topicName "+topicName)
	logging.info("topicBroker "+brokerId)

	while True:
		bootstrapServers="10.0.0."+brokerId+":9092"
		
		consumer = KafkaConsumer(topicName,\
			bootstrap_servers=bootstrapServers,\
			auto_offset_reset='earliest',\
			group_id="group-"+topicName)
			# enable_auto_commit=True,                                     
			# )

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