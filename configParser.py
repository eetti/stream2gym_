
import yaml
from yaml.loader import SafeLoader

import sys
import networkx as nx

GROUP_MIN_SESSION_TIMEOUT_MS = 6000
GROUP_MAX_SESSION_TIMEOUT_MS = 1800000

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

# reading from producer YAML specification
def readProdConfig(prodConfigPath, producerType, nodeID):
	prodConfig = readYAMLConfig(prodConfigPath)
	if producerType == 'CUSTOM' and len(prodConfig[0]) != 2:
		print("ERROR: for CUSTOM producer please provide producer file path and number of producer instance on node "+str(nodeID))
		sys.exit(1)
	if producerType != 'CUSTOM' and len(prodConfig[0]) != 4:
		print("ERROR: to use any standard producer please provide filePath, name of the topic to produce, number of files and number of producer instances in node "+str(nodeID))
		sys.exit(1)

	prodFile = "" if prodConfig[0].get("filePath", "") is None else prodConfig[0].get("filePath", "")
	prodTopic = "" if prodConfig[0].get("topicName", "") is None else prodConfig[0].get("topicName", "")
	prodNumberOfFiles = "" if str(prodConfig[0].get("totalMessages", "")) is None else str(prodConfig[0].get("totalMessages", ""))
	nProducerInstances = "" if str(prodConfig[0].get("producerInstances", "")) is None else str(prodConfig[0].get("producerInstances", ""))
	producerPath = "producer.py" if prodConfig[0].get("producerPath", "producer.py") is None else prodConfig[0].get("producerPath", "producer.py")

	prodDetails = {"nodeId": nodeID, "producerType": producerType,\
					"produceFromFile":prodFile, "produceInTopic": prodTopic,\
					"prodNumberOfFiles": prodNumberOfFiles, "nProducerInstances": nProducerInstances, \
					"producerPath": producerPath}
					# , "messageRate":messageRate, \
					# "acks":acks, "compression":compression, "batchSize": batchSize, \
					# "linger": linger, "requestTimeout": requestTimeout}

	return prodDetails 

# reading from consumer YAML specification
def readConsConfig(consConfigPath, consumerType, nodeID):
	consConfig = readYAMLConfig(consConfigPath)
	consTopic = "" if consConfig[0].get("topicName", "") is None else consConfig[0].get("topicName", "")
	nConsumerInstances = "1" if str(consConfig[0].get("consumerInstances", "1")) is None else str(consConfig[0].get("consumerInstances", "1"))
	consumerPath = "consumer.py" if consConfig[0].get("consumerPath", "consumer.py") is None else consConfig[0].get("consumerPath", "consumer.py")
	fetchMinBytes = 1 if int(consConfig[0].get("fetchMinBytes", 1)) is None else int(consConfig[0].get("fetchMinBytes", 1))
	fetchMaxWait = 500 if int(consConfig[0].get("fetchMaxWait", 500)) is None else int(consConfig[0].get("fetchMaxWait", 500))
	sessionTimeout = 10000 if int(consConfig[0].get("sessionTimeout", 10000)) is None else int(consConfig[0].get("sessionTimeout", 10000))
	print(sessionTimeout)
	print(type(sessionTimeout))

	# Note that the value must be in the allowable range as configured in the broker configuration by group.min.session.timeout.ms and group.max.session.timeout.ms
	if sessionTimeout < GROUP_MIN_SESSION_TIMEOUT_MS or sessionTimeout > GROUP_MAX_SESSION_TIMEOUT_MS:
		print("ERROR: Session timeout must be in the allowable range as configured in the broker configuration by group.min.session.timeout.ms value of " + str(GROUP_MIN_SESSION_TIMEOUT_MS) + " and group.max.session.timeout.ms value of " + str(GROUP_MAX_SESSION_TIMEOUT_MS))
		sys.exit(1)

	if consumerType == 'CUSTOM' and consumerPath == "consumer.py":
		print("ERROR: for CUSTOM consumer, consumer file path is required")
		sys.exit(1)
	elif consumerType == 'STANDARD' and consTopic == "" :
		print("ERROR: for STANDARD consumer, topic name is required")	
		sys.exit(1)
	
	consDetails = {"nodeId": nodeID, "consumerType": consumerType,\
					"consumeFromTopic": consTopic, "nConsumerInstances": nConsumerInstances, \
					"consumerPath": consumerPath, "fetchMinBytes": fetchMinBytes, \
					"fetchMaxWait": fetchMaxWait, "sessionTimeout": sessionTimeout}

	return consDetails 

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

	consDetailsList = []
	consDetails = {}

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
				prodDetails = readProdConfig(data["producerConfig"], producerType, nodeID)
				prodDetailsList.append(prodDetails)
			if 'consumerType' in data:
				consumerType = data["consumerType"]
				nodeID = node[1:]
				consDetails = readConsConfig(data["consumerConfig"], consumerType, nodeID)
				consDetailsList.append(consDetails)
		elif node[0] == 's':
			nSwitches += 1
			switchPlace.append(node[1:]) 

	print("zookeepers:")
	print(*zkPlace)
	# print("brokers: \n")
	# print(*brokerPlace)

	print("producer details: ")
	print(*prodDetailsList)

	print("consumer details: ")
	print(*consDetailsList)

	return brokerPlace, zkPlace, topicPlace, prodDetailsList, consDetailsList, \
		isDisconnect, dcDuration, dcLinks, switchPlace, hostPlace