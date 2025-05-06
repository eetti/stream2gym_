#!/usr/bin/python3

from ast import arg
from re import I
from mininet.net import Mininet
from mininet.cli import CLI
from mininet.node import OVSController, RemoteController, CPULimitedHost
from mininet.link import TCLink

import os
import sys
import subprocess
import time
from datetime import datetime

import argparse
import logging

import psutil

import emuNetwork
import emuKafka
import emuZk
import emuLoad
import emuLogs
import emuStreamProc
import emuDataStore
import configParser

import csv
import json
import jmxquery as jmx
import pprint
import traceback

# console_log_level = 100

# logging.basicConfig(level=logging.INFO,
#                     format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
#                     filename="testing.log",
#                     filemode="w")
# console = logging.StreamHandler(sys.stdout)
# console.setLevel(console_log_level)
# root_logger = logging.getLogger("")
# root_logger.addHandler(console)

pID=0
popens = {}
logDir = "logs/output"
consLogs = []

prodCount = 0
interval = 5
consCount = 0
extraLatencyMessage = 0

# Kill all subprocesses
def killSubprocs(brokerPlace, zkPlace, prodDetailsList, streamProcDetailsList, consDetailsList):	
	os.system("sudo pkill -9 -f bandwidth-monitor.py")
	os.system("sudo pkill -9 -f producer.py")
	os.system("sudo pkill -9 -f consumer.py")

	# killing producer processes
	for prod in prodDetailsList:
		producerScript = prod["producerPath"]
		prodKillStatus = os.system("sudo pkill -9 -f "+producerScript)
	
	# killing spark processes
	for spe in streamProcDetailsList:
		speScript = spe["applicationPath"]
		speKillStatus = os.system("sudo pkill -9 -f "+speScript)

	# killing consumer processes
	for cons in consDetailsList:
		consScript = cons["consumerPath"]
		consKillStatus = os.system("sudo pkill -9 -f "+consScript)

	for bk in brokerPlace:
		bID = bk["nodeId"]
		os.system("sudo pkill -9 -f server"+str(bID)+".properties") 

	os.system("sudo pkill -9 -f zookeeper") 

	# killing the topic duplicate python script
	os.system("sudo pkill -9 -f topicDuplicate.py") 


# Additional functions

def plotLatencyScatter():
	lineXAxis = []
	latencyYAxis = []
	# global latencyYAxis
	with open(logDir+"/latency-log.txt", "r") as f:
		for lineNum, line in enumerate(f,1):         #to get the line number
			lineXAxis.append(lineNum)
			if "Latency of this message: " in line:
				firstSplit = line.split("Latency of this message: 0:")
				# print(firstSplit)
				if len(firstSplit) == 2:
					latencyYAxis.append(float(firstSplit[1][0:2])*60.0 + float(firstSplit[1][3:12]))
	return latencyYAxis

def readThroughput(switch,portNumber, portFlag):
	count=0
	dataList = []
	bandwidth =  [0]
	txFlag = 0
	maxBandwidth = -1.0
	
	with open('logs/output/bandwidth/'+'bandwidth-log'+str(switch)+'.txt') as f:
		
		for line in f:
			if portNumber >= 10:
				spaces = " "
			else:
				spaces = "  "
			if "port"+spaces+str(portNumber)+":" in line: 
				
				if portFlag == 'tx pkts':
					line = f.readline()
					
				elif portFlag == 'tx bytes':
					line = f.readline()
					txFlag = 1           
				if txFlag == 1:
					newPortFlag = "bytes"
					data = line.split(newPortFlag+"=")
				else:
					data = line.split(portFlag+"=")

				data = data[1].split(",")
				dataList.append(int(data[0]))
				if count>0: 
					individualBandwidth = (dataList[count]-dataList[count-1])/5
					bandwidth.append(individualBandwidth)
					if individualBandwidth > maxBandwidth:
						maxBandwidth = individualBandwidth
				count+=1

	return bandwidth,count, maxBandwidth

def overheadCheckPlot(portFlag, msgSize):
	
	allBandwidth = []
	countX = 0
	interval = 5
	
	portParams = [(1,1),(2,1),(3,1),(4,1),(5,1),(6,1),(7,1),(8,1),(9,1),(10,1),
				  (1,2),(2,2),(1,3),(3,3),(1,4),(4,4),(1,5),(5,5),(1,6),(6,6),
				  (1,7),(7,7),(1,8),(8,8),(1,9),(9,9),(1,10),(10,10)]

	# portParams = [(1,1),(1,2),(1,3),(2,1),(2,2),(2,3),(3,1),(3,2),(3,3)] #testing with only 3 nodes
	# portParams = [(1,1)]
	for ports in portParams:
		portId, switchId = ports
	
		bandwidth, occurrence, maxBandwidth = readThroughput(switchId,portId, portFlag)
		
		if countX == 0:
			countX = occurrence
		
		if len(bandwidth)<countX:
			for k in range(countX-len(bandwidth)):
				bandwidth.append(0)                    #filling with 0's to match up the length
			
		allBandwidth.append(bandwidth)

	bandwidthSum = []
	bandwidthSumLeaderLess = []
	for i in range(countX):
		valWithLeader = 0
#         valWithoutLeader = 0
		for j in range(1):
			valWithLeader = valWithLeader+allBandwidth[j][i]
#             if (j+1) not in leaderReplicaList:         #to skip the leader replica curves
#                 valWithoutLeader = valWithoutLeader+allBandwidth[j][i]
		
		bandwidthSum.append(valWithLeader)
#         bandwidthSumLeaderLess.append(valWithoutLeader)
		
	timeList = list(range(0,countX*interval,interval))


	newBandwidthSum = [x / 1000000 for x in bandwidthSum]
	
	return newBandwidthSum
		
def plotAggregatedBandwidth():   
	msgSize = 10
	return overheadCheckPlot("bytes", msgSize)

def initConsStruct(switches):
    global consLogs

    for consId in range(switches):
        newDict = {}
        consLogs.append(newDict)

def getProdDetails(prod, consDetails, logDir):
    global prodCount
    global consLogs
	
    # print(prod)
    latencyLog = open(logDir+"/latency-log.txt", "a")
    instance = prod['nProducerInstances']
    prodLog = logDir+'/prod/prod-node'+str(prod['nodeId'])+'-instance'+str(instance)+'.log'
    prodId = prod['nodeId']
    
    with open(prodLog) as f:
        for line in f:
            if "Topic-name: topic-" in line:
#                 msgProdTime = line.split(",")[0]
                msgProdTime = line.split(" INFO:Topic-name:")[0]
                topicSplit = line.split("topic-")
                topicId = topicSplit[1].split(";")[0]
                msgIdSplit = line.split("Message ID: ")
                msgId = msgIdSplit[1].split(";")[0]
                
                #print("producer: "+str(prodId)+" time: "+msgProdTime+" topic: "+topicId+" message ID: "+msgId)
                prodCount+=1

                if int(prodId) < 10:
                    formattedProdId = "0"+str(prodId)
                else:
                    formattedProdId = str(prodId)

                for consId in range(nConsumer):
                    #print(formattedProdId+"-"+msgId+"-topic-"+topicId)
                    if formattedProdId+"-"+msgId+"-topic-"+topicId in consLogs[consId].keys():
                        msgConsTime = consLogs[consId][formattedProdId+"-"+msgId+"-topic-"+topicId]
                        
                        prodTime = datetime.strptime(msgProdTime, "%Y-%m-%d %H:%M:%S,%f")
                        consTime = datetime.strptime(msgConsTime, "%Y-%m-%d %H:%M:%S,%f")
                        latencyMessage = consTime - prodTime

                        #print(latencyMessage)
                        latencyLog.write("Producer ID: "+str(prodId)+" Message ID: "+msgId+" Topic ID: "+topicId+" Consumer ID: "+str(consId+1)+" Production time: "+msgProdTime+" Consumtion time: "+str(msgConsTime)+" Latency of this message: "+str(latencyMessage))
                        latencyLog.write("\n")    #latencyLog.write("\r\n")

                        # Write to the consumer latency log
                        consLatencyLog = open(logDir+"/cons-latency-logs/latency-log-cons-"+\
                            str(consDetails[consId]['nodeId'])+'-instance'+str(consDetails[consId]['nConsumerInstances']) + ".txt", "a")
                        # consLatencyLog = logDir+'prod-node'+str(prod['prodNodeID'])+'-instance'+str(prod['prodInstID'])+'.log'
                        consLatencyLog.write("Producer ID: "+str(prodId)+" Message ID: "+msgId+" Topic ID: "+topicId+" Consumer ID: "+str(consId)+" Production time: "+msgProdTime+" Consumtion time: "+str(msgConsTime)+" Latency of this message: "+str(latencyMessage))
                        consLatencyLog.write("\n")    #latencyLog.write("\r\n")
                        consLatencyLog.close()

                        #getConsDetails(consId+1, prodId, msgProdTime, topicId, msgId)

        print("Prod " + str(prodId) + ": " + str(datetime.now()))

    latencyLog.close()

def readConsumerData(prodDetails, consDetails, nProducer, nConsumer, logDir):
    consId = 1
    #print("Start reading cons data: " + str(datetime.now()))
    for cons in consDetails:
        print("Reading consumer data for consumer: "+str(cons['nodeId']))
        # print(logDir+'/cons/cons-'+str(consId)+'.log')

        instance = cons['nConsumerInstances']
        f = open(logDir+'/cons/'+'cons-node'+str(cons['nodeId'])\
				+'-instance'+str(instance)+'.log')
        
        for lineNum, line in enumerate(f,1):         #to get the line number
            #print(line)

            if "Prod ID: " in line:
                lineParts = line.split(" ")
                #print(lineParts)

                prodID = lineParts[4][0:-1]
                #print(prodID)

                msgID = lineParts[7][0:-1]
                #print(msgID)

                topic = lineParts[11][0:-1]
                #print(topic)

                #print(prodID+"-"+msgID+"-"+topic)
                consLogs[consId-1][prodID+"-"+msgID+"-"+topic] = lineParts[0] + " " + lineParts[1]

        f.close()
        consId += 1


if __name__ == '__main__': 
	try:
		parser = argparse.ArgumentParser(description='Emulate data sync in mission critical networks.')
		parser.add_argument('topo', type=str, help='Network topology')
		parser.add_argument('--time', dest='duration', type=int, default=10, help='Duration of the simulation (in seconds)')
		parser.add_argument('--capture-all', dest='captureAll', action='store_true', help='Capture the traffic of all the hosts')
		parser.add_argument('--only-spark', dest='onlySpark', type=int, default=0, help='To run Spark application only')
		parser.add_argument("--override", type=str, default=None, help="JSON string of override properties")
		parser.add_argument("--index", type=int, help="Run index from schedule.csv")
		
		args = parser.parse_args()
		# print(args)
		# field_names = ['compression', 'batchSize', 'linger','n_topics','fetch_time','Throughput', 'Latency', 'avg_cpu', 'avg_mem']
		# filename = 'data.csv'
		# with open(filename, 'a', newline='') as file:
		# 	writer = csv.DictWriter(file, fieldnames=field_names)
			
		# 	if file.tell() == 0:
		# 		writer.writeheader()

		#Clean up mininet state
		cleanProcess = subprocess.Popen("sudo mn -c", shell=True)
		emuLogs.cleanLogs()
		time.sleep(2)
	
		# Parse override properties if provided
		override_props = json.loads(args.override) if args.override else None

		#Instantiate network
		emulatedTopo = emuNetwork.CustomTopo(args.topo)

		print("Emulated topology: "+str(emulatedTopo))
		net = Mininet(topo = None,
				controller=RemoteController,
				link = TCLink,
				autoSetMacs = True,
				autoStaticArp = True,
				build=False,
				host= CPULimitedHost)  # support for CPU limited host

		# Persist namespaces for all hosts
		net.topo = emulatedTopo
		net.build()
		print("Network built")
		# Start SSH daemon on each host
		for host in net.hosts:
			print("Starting SSH daemon on host: "+host.name)
			pid = host.pid  # Get the PID of the host process
			ns_name = f"mn-{host.name}"  # Namespace name (e.g., mn-h1)
			print(ns_name+"\n")
			# Register the namespace in /var/run/netns/
			subprocess.run(f"sudo mkdir -p /var/run/netns/", shell=True)
			subprocess.run(f"sudo ln -sf /proc/{pid}/ns/net /var/run/netns/{ns_name}", shell=True)
			# Start SSH daemon on each host
			host.cmd("/usr/sbin/sshd -D &")

			# os.system(f"sudo ip netns exec {ns_name} -c \"python3 /users/grad/etti/pinet/stream2gym/metrics_script.py\" --host {host.name}&")

		brokerPlace, zkPlace, topicPlace, prodDetailsList, consDetailsList, isDisconnect, \
			dcDuration, dcLinks, switchPlace, hostPlace, streamProcDetailsList = configParser.readConfigParams(net, args, override_props)
	
		# print("Producer details: ")
		# pprint(isinstance prodDetailsList))
		# print("Consumer details: ")
		# pprint(consDetailsList)
		# print("Stream processing details: ")
		# pprint(streamProcDetailsList)
		
		

		nTopics = len(topicPlace)
		nSwitches = len(switchPlace)
		nHosts = len(hostPlace)
		print("Number of switches in the topology: "+str(nSwitches))
		print("Number of hostnodes in the topology: "+str(nHosts))
		print("Number of zookeepers in the topology: "+str(len(zkPlace)))
		print("Number of brokers in the topology: "+str(len(brokerPlace)))
		print("Number of topics: "+str(nTopics))
		
		# checking whether the application is only kafka or kafka-spark
		storePath = emuStreamProc.getStreamProcDetails(net, args.topo)
		if not streamProcDetailsList:   # if there is no configuration for spark
			args.onlyKafka = 1
		else:
			args.onlyKafka = 0
			#Add dependency to connect kafka & Spark
			emuStreamProc.addStreamProcDependency()
			
		killSubprocs(brokerPlace, zkPlace, prodDetailsList, streamProcDetailsList, consDetailsList)
		
		emuLogs.cleanLogs()
		emuDataStore.cleanDataStoreState()
		emuKafka.cleanKafkaState(brokerPlace)
		emuZk.cleanZkState(zkPlace)
			
		if storePath != "":
			print("Data store path: "+storePath)
			emuDataStore.configureKafkaDataStoreConnection(brokerPlace)
			# Add NAT connectivity
			net.addNAT().configDefault()  

		logDir = emuLogs.configureLogDir(nSwitches, nTopics, args.captureAll)
		print("Log directory: "+logDir)
		emuZk.configureZkCluster(zkPlace)
		emuKafka.configureKafkaCluster(brokerPlace, zkPlace)

		#Start network
		net.start()
		for switch in net.switches:
			net.get(switch.name).start([])

		logging.info('Network started')
		# Log IP addresses of all hosts
		# with open(f"{logDir}/host_ips.log", "w") as ip_log_file:
		# 	for host in net.hosts:
		# 		ip_output = host.cmd('ip addr')
		# 		log_message = f"Host {host.name}:\n{ip_output}"
		# 		logging.info(log_message)
		# 		ip_log_file.write(f"{log_message}\n")
	

		#emuNetwork.configureNetwork(args.topo)
		time.sleep(1)

		print("Testing network connectivity")
		net.pingAll()
		print("Finished network connectivity test")
				
		#Start monitoring tasks
		popens[pID] = subprocess.Popen("sudo python3 bandwidth-monitor.py "+str(nSwitches)+" &", shell=True)
		pID += 1

		emuZk.runZk(net, zkPlace, logDir)
		emuKafka.runKafka(net, brokerPlace)
		
		emuLoad.runLoad(net, args, topicPlace, prodDetailsList, consDetailsList, streamProcDetailsList,\
			storePath, isDisconnect, dcDuration, dcLinks, logDir)

		# CLI(net)
		print("Simulation complete")
		data = {}
		for j in prodDetailsList:
			if j['nodeId'] == '1':
				data['compression'] = j['compression']
				data['batchSize'] = j['batchSize']
				data['linger'] = j['linger']
				data['n_topics'] = len(topicPlace)
				# data['fetch_time'] = brokerPlace[0]['replicaMaxWait']
				break
		
		for j in consDetailsList:
			if j['nodeId'] == '1':
				data['fetch_time'] = j['fetchMaxWait']
				break
		# to kill all the running subprocesses
		killSubprocs(brokerPlace, zkPlace, prodDetailsList, streamProcDetailsList, consDetailsList)

		net.stop()
		logging.info('Network stopped')
	
		# Clean up namespaces after stopping
		for host in net.hosts:
			ns_name = f"mn-{host.name}"
			subprocess.run(f"sudo rm -f /var/run/netns/{ns_name}", shell=True)

		# Clean kafka-MySQL connection state before new simulation
		if storePath != "":
			emuDataStore.cleanDataStoreState()
	
		#Need to clean both kafka and zookeeper state before a new simulation
		emuKafka.cleanKafkaState(brokerPlace)
		emuZk.cleanZkState(zkPlace)

		#Need to clean spark dependency before a new simulation
		emuStreamProc.cleanStreamProcDependency()

		# collect data
		Thr = plotAggregatedBandwidth()
		Thr_avg = sum(Thr) / len(Thr)
		print(f"Throughput: , {Thr_avg} Mbps")
	
		prodDetails = [{'prodNodeID':1, 'prodInstID':1},{'prodNodeID':2, 'prodInstID':1},{'prodNodeID':2, 'prodInstID':1},{'prodNodeID':2, 'prodInstID':1},
					{'prodNodeID':3, 'prodInstID':1},{'prodNodeID':4, 'prodInstID':1},{'prodNodeID':5, 'prodInstID':1},{'prodNodeID':6, 'prodInstID':1},
					{'prodNodeID':7, 'prodInstID':1},{'prodNodeID':8, 'prodInstID':1},{'prodNodeID':9, 'prodInstID':1},{'prodNodeID':10, 'prodInstID':1}]
		consDetails = [{'consNodeID':1, 'consInstID':1}, {'consNodeID':2, 'consInstID':1},{'consNodeID':3, 'consInstID':1},{'consNodeID':4, 'consInstID':1},
				{'consNodeID':5, 'consInstID':1},{'consNodeID':6, 'consInstID':1},{'consNodeID':7, 'consInstID':1},{'consNodeID':8, 'consInstID':1}
				,{'consNodeID':9, 'consInstID':1},{'consNodeID':10, 'consInstID':1}]
	
		switches = 10

		os.system("sudo rm "+logDir+"/latency-log.txt"+"; sudo touch "+logDir+"/latency-log.txt")
		os.makedirs(logDir+"/cons-latency-logs", exist_ok=True)

		print(datetime.now())

		nProducer = len(prodDetailsList)
		nConsumer = len(consDetailsList)

		initConsStruct(switches)
		readConsumerData(prodDetailsList, consDetailsList, nProducer, nConsumer, logDir)

		# for prodId in range(switches):
		for producer in prodDetailsList:
			getProdDetails(producer, consDetailsList, logDir)


		Late = plotLatencyScatter()
		# print(Late)
		late_avg = sum(Late)/len(Late)
		print(f"Latency: , {late_avg} ms")

		data['Throughput'] = Thr_avg
		data['Latency'] = late_avg
	
		# Calculate average CPU and memory from metrics
		# cpu_values, mem_values = [], []
		# with open(f"{logDir}/metrics.txt", "r") as f:
		# 	for line in f:
		# 		parts = line.split(", ")
		# 		cpu = float(parts[1].split(": ")[1].strip("%"))
		# 		mem = float(parts[2].split(": ")[1].split(" MB")[0])
		# 		cpu_values.append(cpu)
		# 		mem_values.append(mem)
		# avg_cpu = sum(cpu_values) / len(cpu_values) if cpu_values else 0
		# avg_mem = sum(mem_values) / len(mem_values) if mem_values else 0
		# data['avg_cpu'] = avg_cpu
		# data['avg_mem'] = avg_mem
		field_names = ['index','compression', 'batchSize', 'linger','n_topics','fetch_time','Throughput', 'Latency']
		data['index'] = args.index
		filename = 'data.csv'
		with open(filename, 'a', newline='') as file:
			writer = csv.DictWriter(file, fieldnames=field_names)
			
			if file.tell() == 0:
				writer.writeheader()
			writer.writerow(data)
			# writer.close()
		print(data["index"],'-------------------------------------------------------------------------------------------')
		emuLogs.cleanLogs()
	except Exception as e:
		print(f"An error occurred: {e}")
		print(traceback.format_exc())
     

	