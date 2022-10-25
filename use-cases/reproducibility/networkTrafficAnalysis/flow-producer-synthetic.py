from time import sleep
from struct import *
from kafka import KafkaProducer

import logging
import sys

import scapyExtract as myscap

import random as pythonRand
import string
from numpy import random

# Random string generator
def get_random_string(length):
	letters = string.ascii_lowercase + string.ascii_uppercase + string.digits       
	result_str = ''.join(pythonRand.choices(letters, k = length))
	return result_str

try:
	logging.basicConfig(filename="logs/output/"+"prod-individual.log",
								format='%(asctime)s %(levelname)s:%(message)s',
								level=logging.INFO) 
	logging.info("Inside producer")

	bootstrapServers="10.0.0.1:9092"
	inputTopic = 'inputTopic'

	producer = KafkaProducer(bootstrap_servers=bootstrapServers,
							value_serializer=lambda x: x.encode('utf-8'))
	                            
	srcIP = "192.168.1.11"
	dstIP = "20.198.162.76" 
	dstPort = ["20", "443", "25", "53"] #"443" for https
	proto = "6" # for TCP
	nPacketsPerflow = [100,500]

	for flowCount in range(len(nPacketsPerflow)):
		srcPort = str(pythonRand.randint(49152,65535))
		dstPort = pythonRand.choice(dstPort)
		pktCount = 1 
		nPkts = nPacketsPerflow[flowCount]
		while pktCount <= nPkts:
			# attaching random payload and length of payload
			payloadLength = pythonRand.randint(1, 1500)
			payload = get_random_string(payloadLength)

			msg = str(flowCount+1) + ',' + str(pktCount) + ',' + srcIP + ',' \
			 + dstIP + ',' + proto + ',' + srcPort + \
			',' + dstPort + ',' + str(payloadLength) + \
			',' + payload

			logging.info(msg)
			pktCount += 1 

			producer.send(inputTopic, msg)  

		# sleep with a poisson distribution mean of 2mins
		sleepTime = random.poisson(120)
		sleep(sleepTime)

except Exception as e:
	logging.error(e)
	sys.exit(1)