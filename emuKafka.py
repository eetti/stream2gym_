#!/usr/bin/python3

from mininet.net import Mininet

import os
import sys
import subprocess
import time
import networkx as nx

from configParser import readYAMLConfig


def readTopicConfig(topicConfigPath, nBroker):
	allTopics = []
	topicDetails = {}
	
	f = open(topicConfigPath, "r")
	for line in f:
		data = line.split()
		topicName = data[0]
		topicBroker = data[2]
		if 'partition' in line:  
			topicPartition = data[4]
		else:
			topicPartition = "1"

		if 'replica' in line:  
			topicReplica = data[6]
			if int(topicReplica) > nBroker:
				print("ERROR: topic replication can't be greater than the number of brokers. Exiting...")
				sys.exit(1)
		else:
			topicReplica = "1"

		topicDetails = {"topicName": topicName, "topicBroker": topicBroker,\
			"topicPartition": topicPartition, "topicReplica": topicReplica}
		allTopics.append(topicDetails)
	
	f.close()
	# print(*allTopics)

	return allTopics

def readDisconnectionConfig(dcConfigPath):
	dcLinks  = []
	f = open(dcConfigPath, "r")
	for line in f:
		if 'duration: ' in line:
			dcDuration = int(line.split('duration: ')[1].strip())
		elif 'links: ' in line:
			allLinks = line.split('links: ')[1].strip()
			dcLinks = allLinks.split(',')

	print("read DC config:")
	print(dcDuration)
	print(*dcLinks)
	return dcDuration, dcLinks


def readProdConfig(prodConfig):
	lenProdCfg = len(prodConfig.split(","))
	if lenProdCfg != 2 and lenProdCfg != 4:
		print("ERROR: Producer config parameter should contain production file path(optional), \
			topic name to produce, number of producer files(optional) and number of producer intances in a node")
		sys.exit(1)
	
	if lenProdCfg == 4:
		prodFile = prodConfig.split(",")[0]     #prodFile will hold the file path/directory path based on producer type SFST or MFST respectively
		prodTopic = prodConfig.split(",")[1]
		prodNumberOfFiles = prodConfig.split(",")[2]
		nProducerInstances = prodConfig.split(",")[3]
	else:
		prodFile = ""
		prodTopic = prodConfig.split(",")[0]
		prodNumberOfFiles = 1
		nProducerInstances = prodConfig.split(",")[1]

	return prodFile, prodTopic, prodNumberOfFiles, nProducerInstances

def readConsConfig(consConfig):
	#topic list contains the topics from where the consumer will consume
	consTopic = consConfig.split(",")		

	return consTopic


def configureKafkaCluster(brokerPlace, zkPlace, args):
	print("Configure kafka cluster")

	propertyFile = open("kafka/config/server.properties", "r")
	serverProperties = propertyFile.read()

	for bID in brokerPlace:
		os.system("sudo mkdir kafka/kafka" + str(bID) + "/")

		bProperties = serverProperties
		bProperties = bProperties.replace("broker.id=0", "broker.id="+str(bID))
		bProperties = bProperties.replace(
			"#advertised.listeners=PLAINTEXT://your.host.name:9092", 
			"advertised.listeners=PLAINTEXT://10.0.0." + str(bID) + ":9092")
		bProperties = bProperties.replace("log.dirs=/tmp/kafka-logs",
			"log.dirs=./kafka/kafka" + str(bID))

		bProperties = bProperties.replace("#replica.fetch.wait.max.ms=500", "replica.fetch.wait.max.ms="+str(args.replicaMaxWait))
		bProperties = bProperties.replace("#replica.fetch.min.bytes=1", "replica.fetch.min.bytes="+str(args.replicaMinBytes))

		bProperties = bProperties.replace(
            "offsets.topic.replication.factor=1", "offsets.topic.replication.factor=2")

		#Specify zookeeper addresses to connect
		zkAddresses = ""
		zkPort = 2181

		for i in range(len(zkPlace)-1):
			zkAddresses += "10.0.0." + str(zkPlace[i]) + ":" +str(zkPort)+","
			# zkAddresses += "localhost:"+str(zkPort)+","
			zkPort += 1

		# zkAddresses += "localhost:"+str(zkPort)
		zkAddresses += "10.0.0."+str(zkPlace[-1])+ ":" +str(zkPort)
		print("zk connect: " + zkAddresses)

		bProperties = bProperties.replace(
			"zookeeper.connect=localhost:2181",
			"zookeeper.connect="+zkAddresses)

		#bProperties = bProperties.replace(
		#	"zookeeper.connection.timeout.ms=18000",
		#	"zookeeper.connection.timeout.ms=30000")

		bFile = open("kafka/config/server" + str(bID) + ".properties", "w")
		bFile.write(bProperties)
		bFile.close()

	propertyFile.close()


def placeKafkaBrokers(net, args):
	inputTopoFile = args.topo
	onlySpark =  args.onlySpark
	nBroker = int(args.nBroker)

	brokerPlace = []
	zkPlace = []
	switchPlace = []
	hostPlace = []

	topicPlace = []

	prodDetailsList = []
	prodDetails = {}
	prodDetailsKeys = {"nodeId", "producerType","produceFromFile", "produceInTopic"}

	consDetailsList = []
	consDetails = {}
	consDetailsKeys = {"nodeId", "consumeFromTopic"}

	#Read topo information
	try:
		inputTopo = nx.read_graphml(inputTopoFile)
	except Exception as e:
		print("ERROR: Could not read topo properly.")
		print(str(e))
		sys.exit(1)

	#Read topic information
	if onlySpark == 0: 
		topicConfigPath = inputTopo.graph["topicConfig"]
		print("topic config directory: " + topicConfigPath)
		#topicPlace = readTopicConfig(topicConfigPath, nBroker) 
		topicPlace = readYAMLConfig(topicConfigPath)

	# reading disconnection config
	try:
		dcPath = inputTopo.graph["disconnectionConfig"]
		isDisconnect = 1
		print("Disconnection config directory: " + dcPath)
		dcDuration, dcLinks = readDisconnectionConfig(dcPath)
	except KeyError:
		print("No disconnection is set")
		isDisconnect = 0
		dcDuration = 0
		dcLinks = []

	#Read nodewise switch, host, broker, zookeeper, producer, consumer information
	nSwitches = 0
	nHosts = 0
	for node, data in inputTopo.nodes(data=True):  
		if node[0] == 'h':
			nHosts += 1 
			hostPlace.append(node[1:]) 
			if 'zookeeper' in data: 
				zkPlace.append(node[1:]) 
			if 'broker' in data: 
				brokerPlace.append(node[1:])
			if 'producerType' in data: 
				if data["producerType"] != "SFST" and data["producerType"] != "MFST"\
					and data["producerType"] != "ELTT":
					producerType = data["producerType"].split(",")[0]
					producerPath = data["producerType"].split(",")[1].strip()
				else:
					producerType = data["producerType"]
					producerPath = "producer.py"

				prodFile, prodTopic, prodNumberOfFiles, nProducerInstances = readProdConfig(data["producerConfig"])
				prodDetails = {"nodeId": node[1:], "producerType": producerType,\
					"produceFromFile":prodFile, "produceInTopic": prodTopic,\
						"prodNumberOfFiles": prodNumberOfFiles, \
						"nProducerInstances": nProducerInstances, \
							"producerPath": producerPath}
				prodDetailsList.append(prodDetails)

			if 'consumerType' in data and 'consumerConfig' in data: 
				if data["consumerType"] != "STANDARD":
					consumerType = data["consumerType"].split(",")[0]
					consumerPath = data["consumerType"].split(",")[1].strip()
				else:
					consumerType = "STANDARD"
					consumerPath = "consumer.py"

				consTopics = readConsConfig(data["consumerConfig"])
				consDetails = {"nodeId": node[1:], "consumeFromTopic": consTopics,\
								"consumerType": consumerType, "consumerPath": consumerPath}
				consDetailsList.append(consDetails)
 
			# elif 'consumerType' not in data and 'consumerConfig' in data:
			# 	consumerType = "STANDARD"
			# 	consumerPath = "consumer.py"

			# 	consTopics = readConsConfig(data["consumerConfig"])
			# 	consDetails = {"nodeId": node[1:], "consumeFromTopic": consTopics,\
			# 					"consumerType": consumerType, "consumerPath": consumerPath}
			# 	consDetailsList.append(consDetails)

		elif node[0] == 's':
			nSwitches += 1
			switchPlace.append(node[1:]) 
	print("zookeepers:")
	print(*zkPlace)
	# print("brokers: \n")
	# print(*brokerPlace)

	print("producer details")
	print(*prodDetailsList)

	print("consumer details")
	print(*consDetailsList)

	return brokerPlace, zkPlace, topicPlace, prodDetailsList, consDetailsList, \
		isDisconnect, dcDuration, dcLinks, switchPlace, hostPlace




def runKafka(net, brokerPlace, brokerWaitTime=200):

	netNodes = {}

	for node in net.hosts:
		netNodes[node.name] = node
		
	startTime = time.time()
	popens = {}
	for bNode in brokerPlace:
		bID = "h"+str(bNode)

		startingHost = netNodes[bID]
		
		print("Creating Kafka broker at node "+str(bNode))

		# startingHost.popen("kafka/bin/kafka-server-start.sh kafka/config/server"+str(bNode)+".properties &", shell=True)
		popens[startingHost] = startingHost.popen(
            "kafka/bin/kafka-server-start.sh kafka/config/server"+str(bNode)+".properties &", shell=True)
		
		time.sleep(1)

	brokerWait = True
	totalTime = 0
	brokerCount = 0
	for bNode in brokerPlace:
		while brokerWait:
			print("Testing Connection to Broker " + str(bNode) + "...")
			out, err, exitCode = startingHost.pexec(
				"nc -z -v 10.0.0." + str(bNode) + " 9092")
			stopTime = time.time()
			totalTime = stopTime - startTime
			if(exitCode == 0):
				brokerWait = False
				brokerCount += 1
			# elif(totalTime > brokerWaitTime):
			#    print("ERROR: Timed out waiting for Kafka brokers to start")
			#    sys.exit(1)
			else:
				print("Waiting for Broker " + str(bNode) + " to Start...")
				time.sleep(10)
		brokerWait = True
	print("Successfully Created "+str(brokerCount)+" Kafka Brokers in " + str(totalTime) + " seconds")

def cleanKafkaState(brokerPlace):
	for bID in brokerPlace:
		os.system("sudo rm -rf kafka/kafka" + str(bID) + "/")
		os.system("sudo rm -f kafka/config/server" + str(bID) + ".properties")









