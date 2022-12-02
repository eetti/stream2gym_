#!/usr/bin/python3randint

from mininet.net import Mininet
from mininet.cli import CLI

from random import seed, randint, choice

import time
import os
import sys
import itertools
import logging

import subprocess
from subprocess import Popen, PIPE, STDOUT
from datetime import datetime

from emuLogs import ZOOKEEPER_LOG_FILE

# Method to extract Zookeeper leader information from Zookeeper log
def readCurrentZkLeader(logDir):
	zkLeader = None
	with open(logDir+"/" + ZOOKEEPER_LOG_FILE) as f:
		for line in f:
			if "LEADING - LEADER ELECTION TOOK " in line:
				first = line.split(">")[0]
				zkLeader = first[1:]
				# print(f'Zookeeper leader is {zkLeader}')
				break
	return zkLeader

# Method for logging topic(s) leader
def logTopicLeaders(net, logDir, topicPlace):
	# issuingNode = net.hosts[0]
	print("Finding topic leaders at localhost:2181")
	zkLeaderNode = readCurrentZkLeader(logDir)
	print("ZK Leader node is " + str(zkLeaderNode))
	logging.info("ZK Leader node is " + str(zkLeaderNode))
	for topic in topicPlace:
		topicName = topic["topicName"]
		issuingID = int(topic["topicBroker"])
		issuingNode = net.hosts[issuingID-1]
		out = issuingNode.cmd("kafka/bin/kafka-topics.sh --bootstrap-server 10.0.0."+str(issuingID)+":9092 --describe --topic "+str(topicName), shell=True)
		split1 = out.split('Leader: ')
		print(split1)
		split2 = split1[1].split('\t')
		topicLeaderNode = 'h' + split2[0]			
		print(f"Leader for topic {str(topicName)} is node {topicLeaderNode}")
		logging.info(str(topicName) +" leader is node " + topicLeaderNode)

# Method to log the wireshark traces
def traceWireshark(hostsToCapture, f, logDir):
	for h in hostsToCapture:		
		#temp = h.nameToIntf		
		hostName = h.name
		filename = logDir + "/pcapTraces/" + hostName + "-eth1" + "-" + f + ".pcap"
		output = h.cmd("sudo tcpdump -i " + hostName +"-eth1 -w "+ filename +" &", shell=True)	
		print(output)

def spawnProducers(net, mSizeString, mRate, tClassString, nTopics, args, prodDetailsList, topicPlace):
	acks = args.acks
	compression = args.compression
	batchSize = args.batchSize
	linger = args.linger
	requestTimeout = args.requestTimeout
	brokers = args.nBroker
	messageFilePath = args.messageFilePath   

	tClasses = tClassString.split(',')
	#print("Traffic classes: " + str(tClasses))

	nodeClassification = {}
	netNodes = {}    

	classID = 1

	for tClass in tClasses:
		nodeClassification[classID] = []
		classID += 1
	
	#Distribute nodes among classes
	for node in net.hosts:
		netNodes[node.name] = node

	j =0
	for j in prodDetailsList:
		j['tClasses'] = str(randint(1,len(tClasses)))
	
	for i in prodDetailsList:
		nodeID = 'h' + i['nodeId']
		
		producerType = i["producerType"]
		producerPath = i["producerPath"]
		messageFilePath = i['produceFromFile']
		tClasses = i['tClasses']
		prodTopic = i['produceInTopic']
		prodNumberOfFiles = i['prodNumberOfFiles']
		nProducerInstances = i['nProducerInstances']

		node = netNodes[nodeID]

		try:
			topicName = [x for x in topicPlace if x['topicName'] == prodTopic][0]["topicName"]
			brokerId = [x for x in topicPlace if x['topicName'] == prodTopic][0]["topicBroker"] 

			print("Producing messages to topic "+topicName+" at broker "+str(brokerId))
			print("Producer type: "+producerType)

			prodInstance = 1

			while prodInstance <= int(nProducerInstances):
				if producerType == 'INDIVIDUAL':
					node.popen("python3 "+ producerPath +" " +nodeID+" "+str(prodInstance)+" &", shell=True)
					
				else:
					node.popen("python3 "+producerPath+" " +nodeID+" "+tClasses+" "+mSizeString+" "+str(mRate)+" "+str(nTopics)+" "+str(acks)+" "+str(compression)\
					+" "+str(batchSize)+" "+str(linger)+" "+str(requestTimeout)+" "+str(brokerId)+" "+messageFilePath\
					+" "+topicName+" "+producerType+" "+prodNumberOfFiles+" "+str(prodInstance)+" &", shell=True)
				
				prodInstance += 1

		except IndexError:
			print("Error: Production topic name not matched with the already created topics")
			sys.exit(1)
			
def spawnConsumers(net, consDetailsList, topicPlace):

	netNodes = {}

	for node in net.hosts:
		netNodes[node.name] = node
        
	for cons in consDetailsList:
		consInstance = 1
		
		consNode = cons["nodeId"]
		topicName = cons["consumeFromTopic"][0]
		consumerType = cons["consumerType"]
		consumerPath = cons["consumerPath"]

		consID = "h"+consNode      
		node = netNodes[consID]

		# number of consumers
		numberOfConsumers = int(cons["consumeFromTopic"][-1])

		print("consumer node: "+consNode)
		print("topic: "+topicName)
		print("Number of consumers for this topic: "+str(numberOfConsumers))

		try:
			topicName = [x for x in topicPlace if x['topicName'] == topicName][0]["topicName"]
			brokerId = [x for x in topicPlace if x['topicName'] == topicName][0]["topicBroker"] 

			print("Consuming messages from topic "+topicName+" at broker "+str(brokerId))

			while consInstance <= int(numberOfConsumers):
				node.popen("python3 "+consumerPath+" "+str(node.name)+" "+topicName+" "+str(brokerId)+" "+str(consInstance)+" &", shell=True)
				
				consInstance += 1

		except IndexError:
			print("Error: Consume topic name not matched with the already created topics")
			sys.exit(1)

def spawnSparkClients(net, sparkDetailsList):
	netNodes = {}

	for node in net.hosts:
		netNodes[node.name] = node

	for sprk in sparkDetailsList:
		time.sleep(30)
		
		sparkNode = sprk["nodeId"]
		# sparkInputFrom = sprk["topicsToConsume"]
		sparkApp = sprk["applicationPath"]
		sparkOutputTo = sprk["produceTo"]
		print("spark node: "+sparkNode)
		print("spark App: "+sparkApp)
		print("spark output to: "+sparkOutputTo)
		print("*************************")

		sprkID = "h"+sparkNode
		node = netNodes[sprkID]

		# node.popen("sudo spark/pyspark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 "+sparkApp\
		# 			+" "+str(node.name)+" "+sparkOutputTo+" &", shell=True)

		node.popen("sudo spark/pyspark/bin/spark-submit --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.2.1 "+sparkApp\
					+" &", shell=True)


def spawnKafkaMySQLConnector(net, prodDetailsList, mysqlPath):
	netNodes = {}

	for node in net.hosts:
		netNodes[node.name] = node
	
	connNode = prodDetailsList[0]["nodeId"]
	connID = "h"+connNode      
	node = netNodes[connID]

	print("=========")
	print("connector starts on node: "+connID)
	
	node.popen("sudo kafka/bin/connect-standalone.sh kafka/config/connect-standalone-new.properties "+ mysqlPath +" > logs/connectorOutput.txt &", shell=True)

def runLoad(net, args, topicPlace, prodDetailsList, consDetailsList, sparkDetailsList, \
	mysqlPath, brokerPlace, isDisconnect, dcDuration, dcLinks, logDir, topicWaitTime=100):

	nTopics = len(topicPlace)
	mSizeString = args.mSizeString
	mRate = args.mRate
	tClassString = args.tClassString
	consumerRate = args.consumerRate
	duration = args.duration

	# give some time to warm up the brokers
	time.sleep(5)

	print("Start workload")
	if args.captureAll:
		print("Started capturing wireshark traces")
		traceWireshark(net.hosts, "start", logDir)

	seed(1)

	nHosts = len(net.hosts)
	print("Number of hosts: " + str(nHosts))
    
	#Creating topic(s) in respective broker
	topicNodes = []
	startTime = time.time()

	for topic in topicPlace:
		topicName = topic["topicName"]
		issuingID = int(topic["topicBroker"])
		topicPartition = topic["topicPartition"]
		topicReplica = topic["topicReplica"]
		issuingNode = net.hosts[issuingID-1]

		print("Creating topic "+topicName+" at broker "+str(issuingID)+" partition "+str(topicPartition))

		out = issuingNode.cmd("kafka/bin/kafka-topics.sh --create --bootstrap-server 10.0.0."+str(issuingID)+
			":9092 --replication-factor "+str(topicReplica)+" --partitions " + str(topicPartition) +
			" --topic "+topicName, shell=True)
		
		print(out)
		topicNodes.append(issuingNode)

		topicDetails = issuingNode.cmd("kafka/bin/kafka-topics.sh --describe --bootstrap-server 10.0.0."+str(issuingID)+":9092", shell=True)
		print("Topic description at the beginning of the simulation:")
		print(topicDetails)

	stopTime = time.time()
	totalTime = stopTime - startTime
	print("Successfully Created " + str(len(topicPlace)) + " Topics in " + str(totalTime) + " seconds")
	
	#starting Kafka-MySQL connector
	if mysqlPath != "":
		spawnKafkaMySQLConnector(net, prodDetailsList, mysqlPath)
		print("Kafka-MySQL connector instance created")

	if args.onlyKafka == 0:
		spawnSparkClients(net, sparkDetailsList)
		time.sleep(30)
		print("Spark Clients created")

	spawnProducers(net, mSizeString, mRate, tClassString, nTopics, args, prodDetailsList, topicPlace)
	# time.sleep(120)
	print("Producers created")
	
	spawnConsumers(net, consDetailsList, topicPlace)
	# time.sleep(10)
	print("Consumers created")

	# Log the topic leaders
	logTopicLeaders(net, logDir, topicPlace)	

	timer = 0

	# Set up disconnect
	if isDisconnect:
		isDisconnected = False
		disconnectTimer = dcDuration
		hostsToDisconnect = []

	print(f"Starting workload at {str(datetime.now())}")
	logging.info('Starting workload at ' + str(datetime.now()))
	
	while timer < duration:
		time.sleep(10)
		percentComplete = int((timer/duration)*100)
		print("Processing workload: "+str(percentComplete)+"%")

		if isDisconnect and percentComplete >= 10:
			if not isDisconnected:	
				for link in dcLinks:
					linkSplit = link.split('-')
					n1 = net.getNodeByName(linkSplit[0])
					n2 = net.getNodeByName(linkSplit[1])
					hostsToDisconnect.append(n2)
					disconnectLink(net, n1, n2)

				isDisconnected = True

			elif isDisconnected and disconnectTimer <= 0: 	
				for link in dcLinks:
					linkSplit = link.split('-')
					n1 = net.getNodeByName(linkSplit[0])
					n2 = net.getNodeByName(linkSplit[1])				
					reconnectLink(net, n1, n2)
					if args.captureAll:
						traceWireshark(hostsToDisconnect, "reconnect", logDir)

					# checking topic leader after reconnection
					topicDetails = topicNodes[0].cmd("kafka/bin/kafka-topics.sh --describe --bootstrap-server 10.0.0.1:9092", shell=True)
					print("Topic description after reconnection")
					print(topicDetails)

				isDisconnected = False
				isDisconnect = False
				
			if isDisconnected:
				disconnectTimer -= 10

		timer += 10

	logTopicLeaders(net, logDir, topicPlace)
	print(f"Workload finished at {str(datetime.now())}")	
	logging.info('Workload finished at ' + str(datetime.now()))

def disconnectLink(net, n1, n2):
	print(f"***********Setting link down from {n1.name} <-> {n2.name} at {str(datetime.now())}")
	logging.info(f"***********Setting link down from {n1.name} <-> {n2.name} at {str(datetime.now())}")
	net.configLinkStatus(n2.name, n1.name, "down")
	net.pingAll()

def reconnectLink(net, n1, n2):
	print(f"***********Setting link up from {n1.name} <-> {n2.name} at {str(datetime.now())}")
	logging.info(f"***********Setting link up from {n1.name} <-> {n2.name} at {str(datetime.now())}")
	net.configLinkStatus(n2.name, n1.name, "up")
	net.pingAll()