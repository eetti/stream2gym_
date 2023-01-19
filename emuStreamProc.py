#!/usr/bin/python3

import sys
import os
import networkx as nx

# Add relevant dependency to connect Apache Kafka with stream processing engine
def addStreamProcDependency():
    src = "dependency/*"

	# Local maven directory
    dst = "/root/.ivy2"

    os.system("sudo mkdir -p "+dst+"/cache "+dst+"/jars")
    os.system("sudo cp -r "+src+" "+dst)

def readStreamProcConfig(streamProcConfig):
    streamProcApp = streamProcConfig.split(",")[0]
    produceTo = streamProcConfig.split(",")[1]
    
    return streamProcApp, produceTo
    
def getStreamProcDetails(net, inputTopoFile):

	# streamProcDetailsList = []
	# streamProcDetails = {}
	# streamProcDetailsKeys = {"nodeId", "applicationPath", "produceTo"}

	storePath = ''

	#Read topo information
	try:
		inputTopo = nx.read_graphml(inputTopoFile)
	except Exception as e:
		print("ERROR: Could not read topo properly.")
		print(str(e))
		sys.exit(1)
	
	try:
		#Read nodewise streamProc information
		for node, data in inputTopo.nodes(data=True):  
			if node[0] == 'h':
				# if 'streamProcConfig' in data: 
				# 	streamProcType = ""
				# 	if 'streamProcType' in data: 
				# 		streamProcType = data['streamProcType']
				# 	streamProcApp, produceTo = readStreamProcConfig(data["streamProcConfig"])
				# 	streamProcDetails = {"nodeId": node[1:], 'streamProcType': streamProcType, \
				# 						"applicationPath": streamProcApp, "produceTo": produceTo}
					
				# 	streamProcDetailsList.append(streamProcDetails)
				
				if 'storeConfig' in data:
					storeType = ""
					if 'storeType' in data: 
						storeType = data['storeType']
					storePath = storePath + data["storeConfig"]

	except KeyError as e:
		print("Node attributes are not set properly: "+str(e))
		sys.exit(1)
	# print("streamProc details")
	# print(*streamProcDetailsList)

	print("store config path: "+storePath)

	# return streamProcDetailsList,storePath
	return storePath

def cleanStreamProcDependency():
# 	os.system("sudo rm -rf logs/kafka/")
	os.system("sudo rm -rf /root/.ivy2/cache")
	os.system("sudo rm -rf /root/.ivy2/jars")