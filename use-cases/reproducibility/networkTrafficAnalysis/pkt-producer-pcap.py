from time import sleep
from struct import *
from kafka import KafkaProducer

import logging
import sys

import scapyExtract as myscap

import random as pythonrand
import string
from numpy import random

def get_random_string(length):
	letters = string.ascii_lowercase + string.ascii_uppercase + string.digits       
	result_str = ''.join(pythonrand.choices(letters, k = length))
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
	                            
	file0 = 'use-cases/reproducibility/networkTrafficAnalysis/laptop-pcap.pcap'
	# file0 = 'use-cases/reproducibility/networkTrafficAnalysis/AIMchat1.pcap'
	packets = myscap.scapy_read_packets(file0)


	datalst = myscap.parse_scapy_packets(packets)
	logging.info(datalst[0:2])
	logging.info(len(datalst))

	count = 1 
	noOfService = 4
	j = 0
	while j<noOfService:
		for i in range(len(datalst)):
			pkt = datalst[i]

			if (pkt['etype'] == '2048'):
				isrc = pkt['isrc']
				idst = pkt['idst']
				iproto = pkt['iproto']
			
				if (iproto == '17'):
					sport = pkt['utsport']
					dport = pkt['utdport']
				else:
					sport = pkt['tsport']
					dport = pkt['tdport']

				# attaching random payload and length of payload
				payloadLength = pythonrand.randint(1, 100)
				payload = get_random_string(payloadLength)

				msg = str(count) + ',' + str(isrc) + ',' + str(idst) + \
				',' + str(iproto) + ',' + str(sport) + \
				',' + str(dport) + ',' + str(payloadLength) + \
				',' + str(payload) 

				logging.info(msg)
				count+=1 

				producer.send(inputTopic, msg)  
				# sleep(1)

		x = random.poisson(lam=2, size=noOfService)
		sleep(x[j])
		j += 1



except Exception as e:
	logging.error(e)
	sys.exit(1)