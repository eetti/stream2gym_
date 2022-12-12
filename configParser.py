
import yaml
from yaml.loader import SafeLoader

import sys
import networkx as nx

def readYAMLConfig(configPath):
	data = []

	try:
		with open(configPath, 'r') as f:
			data = list(yaml.load_all(f, Loader=SafeLoader))
			print(data)
	except yaml.YAMLError:
		print("Error in configuration file")

	return data

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


def readProdConfig(prodConfigPath, producerType, nodeID):
	prodConfig = readYAMLConfig(prodConfigPath)
	if producerType == 'INDIVIDUAL' and len(prodConfig[0]) != 2:
		print("ERROR: for CUSTOM producer please provide producer file path and number of producer instance on node "+str(nodeID))
		sys.exit(1)
	if producerType != 'INDIVIDUAL' and len(prodConfig[0]) != 4:
		print("ERROR: to use any standard producer please provide filePath, name of the topic to produce, number of files and number of producer instances in node "+str(nodeID))
		sys.exit(1)

	# prodFile = ""
	# prodTopic = ""
	# prodNumberOfFiles = ""
	# nProducerInstances = ""
	# producerPath = "producer.py"

	prodFile = "" if prodConfig[0].get("filePath", "") is None else prodConfig[0].get("filePath", "")
	prodTopic = "" if prodConfig[0].get("topicName", "") is None else prodConfig[0].get("topicName", "")
	prodNumberOfFiles = "" if str(prodConfig[0].get("totalMessages", "")) is None else str(prodConfig[0].get("totalMessages", ""))
	nProducerInstances = "" if str(prodConfig[0].get("producerInstances", "")) is None else str(prodConfig[0].get("producerInstances", ""))
	producerPath = "producer.py" if prodConfig[0].get("producerPath", "producer.py") is None else prodConfig[0].get("producerPath", "producer.py")
	
	# messageRate = 1.0
	# acks = 1
	# compression = 'None'
	# batchSize = 16384
	# linger = 0
	# requestTimeout = 30000

	# if prodConfig[0].get("filePath") is not None:
	# 	prodFile = prodConfig[0]["filePath"]
	# if prodConfig[0].get("topicName") is not None:
	# 	prodTopic = prodConfig[0]["topicName"]
	# if prodConfig[0].get("totalMessages") is not None:
	# 	prodNumberOfFiles = str(prodConfig[0]["totalMessages"])
	# if prodConfig[0].get("producerInstances") is not None:
	# 	nProducerInstances = str(prodConfig[0]["producerInstances"])	
	# if prodConfig[0].get("producerPath") is not None:
	# 	producerPath = prodConfig[0]["producerPath"]
	# if prodConfig[0].get("messageRate") is not None:
	# 	messageRate = prodConfig[0]["messageRate"]
	# if prodConfig[0].get("acks") is not None:
	# 	acks = prodConfig[0]["acks"]
	# if prodConfig[0].get("compression") is not None:
	# 	compression = prodConfig[0]["acks"]
	# if prodConfig[0].get("batchSize") is not None:
	# 	batchSize = prodConfig[0]["batchSize"]
	# if prodConfig[0].get("linger") is not None:
	# 	linger = prodConfig[0]["linger"]
	# if prodConfig[0].get("requestTimeout") is not None:
	# 	requestTimeout = prodConfig[0]["requestTimeout"]

	prodDetails = {"nodeId": nodeID, "producerType": producerType,\
					"produceFromFile":prodFile, "produceInTopic": prodTopic,\
					"prodNumberOfFiles": prodNumberOfFiles, "nProducerInstances": nProducerInstances, \
					"producerPath": producerPath}
					# , "messageRate":messageRate, \
					# "acks":acks, "compression":compression, "batchSize": batchSize, \
					# "linger": linger, "requestTimeout": requestTimeout}

	print("Prod details: "+str(prodDetails))
	return prodDetails #prodFile, prodTopic, prodNumberOfFiles, nProducerInstances, producerPath

def readConsConfig(consConfig):
	#topic list contains the topics from where the consumer will consume
	consTopic = consConfig.split(",")		

	return consTopic

def readConfigParams(net, args):
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
				producerType = data["producerType"]
				nodeID = node[1:]
				# prodFile, prodTopic, prodNumberOfFiles, nProducerInstances, producerPath = readProdConfig(data["producerConfig"], producerType, nodeID)
				prodDetails = readProdConfig(data["producerConfig"], producerType, nodeID)
				# prodDetails = {"nodeId": node[1:], "producerType": producerType,\
				# 	"produceFromFile":prodFile, "produceInTopic": prodTopic,\
				# 		"prodNumberOfFiles": prodNumberOfFiles, \
				# 		"nProducerInstances": nProducerInstances, \
				# 			"producerPath": producerPath}
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