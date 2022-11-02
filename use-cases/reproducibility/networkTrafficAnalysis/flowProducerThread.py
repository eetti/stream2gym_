from time import sleep
from struct import *
from kafka import KafkaProducer

import logging
import sys

import random as pythonRand
import string
import numpy as np

from threading import Thread

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

# Random string generator
def get_random_string(length):
	letters = string.ascii_lowercase + string.ascii_uppercase + string.digits       
	result_str = ''.join(pythonRand.choices(letters, k = length))
	return result_str

def generatePktData():
	pkt ={}

	# generating one packet with 5 flow-tuples and payload
	srcIP = "192.168.1.11"
	dstIP = "20.198.162.76" 
	dstPort = ["20", "443", "25", "53"] #"443" for https
	proto = "6" # for TCP

	srcPort = str(pythonRand.randint(49152,65535))
	dstPort = pythonRand.choice(dstPort)

	# attaching random payload and length of payload
	payloadLength = pythonRand.randint(1, 1500)
	payload = get_random_string(payloadLength)

	pkt = {"srcIP": srcIP, "dstIP":dstIP, "srcPort":srcPort, "dstPort": dstPort,\
		"proto":proto, "payloadLength":payloadLength, "payload":payload}

	return pkt

def prodInstanceThread(kProd, nodeID, prodInstanceID, inputTopic):
	try: 
		logFile = "logs/output/"+"prod-node"+nodeID+\
									"-instance"+str(prodInstanceID)+".log"
		threadLogger = setup_logger('threadLogger', logFile)
		# logging.basicConfig(filename="logs/output/"+"prod-node"+nodeID+\
		# 							"-instance"+str(prodInstanceID)+".log",
		# 							format='%(asctime)s %(levelname)s:%(message)s',
		# 							level=logging.INFO) 
		threadLogger.info("Thread: "+str(prodInstanceID))
									
		flowCount = 1
		while True:
			pktCount = 1 
			nPkts = pythonRand.randint(0,200)  # generating flows with random number of flows
			while pktCount <= nPkts:
				pkt = generatePktData()			

				msg = str(nodeID) + ',' + str(prodInstanceID)+','+ str(flowCount) +\
				',' + str(pktCount) +',' + pkt["srcIP"] + ',' +\
				pkt["dstIP"] + ',' + pkt["proto"] + ',' + pkt["srcPort"] + \
				',' + pkt["dstPort"] + ',' + str(pkt["payloadLength"]) + \
				',' + pkt["payload"]

				kProd.send(inputTopic, msg)
				threadLogger.info(msg)

				pktCount += 1 

			# sleep with a poisson distribution mean of 2mins
			sleepTime = np.random.poisson(120)
			sleep(sleepTime)
			flowCount += 1
	
	except Exception as e:
		threadLogger.error(e)
		sys.exit(1)
	

try:
	nodeName = sys.argv[1]
	nProdInstance = int(sys.argv[2])
	nodeID = nodeName[1:]

	bootstrapServers="10.0.0.1:9092"
	inputTopic = 'inputTopic'

	producer = KafkaProducer(bootstrap_servers=bootstrapServers,
							value_serializer=lambda x: x.encode('utf-8'))

	mainThreadLogger = setup_logger('mainThreadLogger', 'logs/output/mainThreadLogger.log')
	mainThreadLogger.info('bootstrapServers: '+bootstrapServers)
	mainThreadLogger.info("node to initiate producer: "+nodeID)
	mainThreadLogger.info("topic name: "+inputTopic)
	mainThreadLogger.info("number of producer instances: "+str(nProdInstance))
	
	i = 1
	while i <= nProdInstance:
		prodThread = Thread(target= prodInstanceThread, args = (producer, nodeID, i,inputTopic,), daemon= True)
		prodThread.start()
		mainThreadLogger.info("Thread "+str(i)+" started")
		i += 1
	

except Exception as e:
	mainThreadLogger.error(e)
	sys.exit(1)