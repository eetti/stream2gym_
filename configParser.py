
import yaml
from yaml.loader import SafeLoader

import sys
import networkx as nx

GROUP_MIN_SESSION_TIMEOUT_MS = 6000
GROUP_MAX_SESSION_TIMEOUT_MS = 1800000
REPLICA_LAG_TIME_MAX_MS = 30000

def readYAMLConfig(configPath):
	data = []

	try:
		with open(configPath, 'r') as f:
			data = list(yaml.load_all(f, Loader=SafeLoader))
			print(data)
	except yaml.YAMLError:
		print("Error in configuration file")

	return data


def validateBrokerParameters(brokerConfig, nodeID, replicaMaxWait, replicaMinBytes):
	# This value should always be less than the replica.lag.time.max.ms at all times to prevent frequent shrinking of ISR for low throughput topics
	if replicaMaxWait >= REPLICA_LAG_TIME_MAX_MS:
		print("ERROR in producer at node "+str(nodeID)+": replica.fetch.wait.max.ms must be less than the replica.lag.time.max.ms value of " +  str(REPLICA_LAG_TIME_MAX_MS) + " at all times.")
		sys.exit(1)
	
def readBrokerConfig(brokerConfigPath, nodeID):
	brokerConfig = readYAMLConfig(brokerConfigPath)

	# Apache Kafka broker parameters
	if len(brokerConfig) == 0:
		replicaMaxWait = 500
		replicaMinBytes = 1
	else:
		replicaMaxWait = 500 if brokerConfig[0].get("replicaMaxWait", 500) is None else brokerConfig[0].get("replicaMaxWait", 500)
		replicaMinBytes = 1 if brokerConfig[0].get("replicaMinBytes", 1) is None else brokerConfig[0].get("replicaMinBytes", 1)

	validateBrokerParameters(brokerConfig, nodeID, replicaMaxWait, replicaMinBytes)

	brokerDetails = {"nodeId": nodeID, "replicaMaxWait": replicaMaxWait, 'replicaMinBytes': replicaMinBytes}
	print("Broker details at node "+str(nodeID)+":")
	# print(brokerDetails)

	return brokerDetails 

# reading from producer YAML specification
def readProdConfig(prodConfigPath, producerType, nodeID, override_props=None):
	prodConfig = readYAMLConfig(prodConfigPath)
	if override_props:
		for key, value in override_props.items():
			prodConfig[0][key] = value
	prodFile = prodConfig[0].get("filePath", "None")
	prodTopic = prodConfig[0].get("topicName", "None")
	prodNumberOfFiles = str(prodConfig[0].get("totalMessages", "0"))
	nProducerInstances = str(prodConfig[0].get("producerInstances", "1"))
	producerPath = prodConfig[0].get("producerPath", "producer.py")
	acks = prodConfig[0].get("acks", 1)
	compression = str(prodConfig[0].get("compression", "None"))
	batchSize = prodConfig[0].get("batchSize", 16384)
	linger = prodConfig[0].get("linger", 0)
	requestTimeout = prodConfig[0].get("requestTimeout", 30000)
	bufferMemory = prodConfig[0].get("bufferMemory", 33554432)
	mRate = str(prodConfig[0].get("messageRate", "None"))

	print("Producer details at node "+str(nodeID)+":")
	print(prodConfig)
	validateProducerParameters(prodConfig, nodeID, producerType, acks, compression, mRate)

	prodDetails = {
		"nodeId": nodeID, "producerType": producerType,
		"produceFromFile": prodFile, "produceInTopic": prodTopic,
		"prodNumberOfFiles": prodNumberOfFiles, "nProducerInstances": nProducerInstances,
		"producerPath": producerPath, "acks": acks, "compression": compression,
		"batchSize": batchSize, "linger": linger, "requestTimeout": requestTimeout,
		"bufferMemory": bufferMemory, "mRate": mRate
	}
	
	# print("Producer details at node "+str(nodeID)+":")
	# print(prodDetails)

	return prodDetails 

# reading from consumer YAML specification
def readConsConfig(consConfigPath, consumerType, nodeID, override_props=None):
	consConfig = readYAMLConfig(consConfigPath)
	if override_props:
		for key, value in override_props.items():
			consConfig[0][key] = value
	consTopic = consConfig[0].get("topicName", "")
	nConsumerInstances = str(consConfig[0].get("consumerInstances", "1"))
	consumerPath = consConfig[0].get("consumerPath", "consumer.py")
	fetchMinBytes = int(consConfig[0].get("fetchMinBytes", 1))
	fetchMaxWait = int(consConfig[0].get("fetchMaxWait", 500))
	sessionTimeout = int(consConfig[0].get("sessionTimeout", 10000))

	if sessionTimeout < GROUP_MIN_SESSION_TIMEOUT_MS or sessionTimeout > GROUP_MAX_SESSION_TIMEOUT_MS:
		print(f"ERROR: Session timeout must be between {GROUP_MIN_SESSION_TIMEOUT_MS} and {GROUP_MAX_SESSION_TIMEOUT_MS}")
		sys.exit(1)

	consDetails = {
		"nodeId": nodeID, "consumerType": consumerType,
		"consumeFromTopic": consTopic, "nConsumerInstances": nConsumerInstances,
		"consumerPath": consumerPath, "fetchMinBytes": fetchMinBytes,
		"fetchMaxWait": fetchMaxWait, "sessionTimeout": sessionTimeout
	}
	return consDetails

def readFaultConfig(faultConfigPath):
	faultyLinks  = []
	faultConfig = readYAMLConfig(faultConfigPath)
	faultDuration = 60 if int(faultConfig[0].get("duration", 60)) is None else int(faultConfig[0].get("duration", 60))
	links = "" if faultConfig[0].get("links", "") is None else faultConfig[0].get("links", "")
	faultyLinks = links.split(',')

	print("read fault config:")
	print(faultDuration)
	print(*faultyLinks)
	return faultDuration, faultyLinks


def validateProducerParameters(prodConfig, nodeID, producerType, acks, compression, mRate):
	if producerType == 'CUSTOM' and len(prodConfig[0]) < 2:
		print("ERROR: required parameters for CUSTOM producer at producer on node "+str(nodeID)+": producer file path and number of producer instance")
		sys.exit(1)
	if producerType == 'STANDARD' and len(prodConfig[0]) < 2:
		print("ERROR: required parameters for STANDARD producer at producer on node "+str(nodeID)+": name of the topic to produce and number of producer instances")
		sys.exit(1)
	if producerType != 'CUSTOM' and producerType != 'STANDARD' and len(prodConfig[0]) < 4:
		print("ERROR: required parameters for "+str(producerType)+" producer at producer on node "+str(nodeID)+": file to produce, name of the topic to produce, number of files and number of producer instances")
		sys.exit(1)

	if acks < 0 or acks >= 3:
		print("ERROR: acks value should be 0, 1 or 2 (which represents all) in producer at node "+str(nodeID))
		sys.exit(1)

	compressionList = ['gzip', 'snappy', 'lz4']
	if not (compression in compressionList) and compression != 'None':
		print("ERROR: at producer on node "+str(nodeID)+" compression should be None or one of the following:")
		print(*compressionList, sep = ", ") 
		sys.exit(1)
	if mRate != "None" and float(mRate) > 100:
		print("ERROR: Message rate on producer at node "+str(nodeID)+" should be less than 100 msg/second.")
		sys.exit(1)

def readStreamProcConfig(streamProcConfigPath, nodeID):
	streamProcConfig = readYAMLConfig(streamProcConfigPath)
	speApp = "" if streamProcConfig[0].get("app", "") is None else streamProcConfig[0].get("app", "")
	if speApp == "" or speApp == None:
		print('ERROR: stream processing application path not specified correctly in node '+str(nodeID))
	
	return speApp

def readConfigParams(net, args, override_props=None):
	inputTopoFile = args.topo
	onlySpark =  args.onlySpark

	brokerPlace = []
	zkPlace = []
	switchPlace = []
	hostPlace = []

	topicPlace = []

	prodDetailsList = []
	consDetailsList = []
	streamProcDetailsList = []

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
		topicPlace = readYAMLConfig(topicConfigPath)

	# reading fault config
	try:
		dcPath = inputTopo.graph["faultConfig"]
		isDisconnect = 1
		print("Fault config directory: " + dcPath)
		dcDuration, dcLinks = readFaultConfig(dcPath)
	except KeyError:
		print("No fault is set")
		isDisconnect = 0
		dcDuration = 0
		dcLinks = []

	#Read nodewise switch, host, broker, zookeeper, producer, consumer information
	nSwitches = 0
	nHosts = 0
	try:
		for node, data in inputTopo.nodes(data=True):  
			if node[0] == 'h':
				nodeID = node[1:]
				nHosts += 1 
				hostPlace.append(node[1:]) 
				if 'zookeeper' in data: 
					if data["zookeeper"] == 1:
						zkPlace.append(node[1:]) 
					elif data["zookeeper"] == 0:
						pass
					else:
						print("ERROR: zookeeper attribute only supports boolean input. Please check zookeeper attribute seting in node "+str(node))
						sys.exit(1)
				if 'brokerConfig' in data: 
					brokerDetails = readBrokerConfig(data["brokerConfig"], nodeID)
					brokerPlace.append(brokerDetails)
				if 'producerType' in data:
					producerType = data["producerType"]
					prodDetails = readProdConfig(data["producerConfig"], producerType, nodeID, override_props.get("producer", {}) if override_props else None)
					prodDetailsList.append(prodDetails)
				if 'consumerType' in data:
					consumerType = data["consumerType"]
					consDetails = readConsConfig(data["consumerConfig"], consumerType, nodeID, override_props.get("consumer", {}) if override_props else None)
					consDetailsList.append(consDetails)
				if 'streamProcConfig' in data: 
					streamProcType = ""
					if 'streamProcType' in data: 
						streamProcType = data['streamProcType']
					streamProcApp = readStreamProcConfig(data["streamProcConfig"], nodeID)
					streamProcDetails = {"nodeId": nodeID, 'streamProcType': streamProcType, \
										"applicationPath": streamProcApp}
					streamProcDetailsList.append(streamProcDetails)
			elif node[0] == 's':
				nSwitches += 1
				switchPlace.append(node[1:]) 
	except KeyError as e:
		print("Node attributes are not set properly: "+str(e))
		sys.exit(1)

	print("zookeepers:")
	print(*zkPlace)
	# print("brokers: \n")
	# print(*brokerPlace)

	print("producer details: \n")
	print(*prodDetailsList)

	print("consumer details: \n")
	print(*consDetailsList)

	return brokerPlace, zkPlace, topicPlace, prodDetailsList, consDetailsList, \
		isDisconnect, dcDuration, dcLinks, switchPlace, hostPlace, streamProcDetailsList