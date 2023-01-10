#!/usr/bin/python3

import os
import logging

from mininet.util import pmonitor

ZOOKEEPER_LOG_FILE = "zk-log.txt"

def configureLogDir(nSwitches, nTopics, captureAll):  
	logDir = "logs/output"

	os.system("sudo rm -rf " + logDir + "/" + ZOOKEEPER_LOG_FILE)
	os.system("sudo rm -rf " + logDir + "/bandwidth/; " + "sudo mkdir -p " + logDir + "/bandwidth/")
	os.system("sudo rm -rf " + logDir + "/prod/; " + "sudo mkdir -p " + logDir + "/prod/")    
	os.system("sudo rm -rf " + logDir + "/cons/; " + "sudo mkdir -p " + logDir + "/cons/")

	if captureAll:
		os.system("sudo rm -rf " + logDir + "/pcapTraces/; " + "sudo mkdir -p " + logDir + "/pcapTraces/")

	logging.basicConfig(filename=logDir+"/events.log",
						format='%(levelname)s:%(message)s',
 						level=logging.INFO)
	return logDir


def cleanLogs():
	os.system("sudo rm -rf logs/kafka/")
	os.system("sudo rm -rf logs/output/")
	os.system("sudo rm -rf kafka/logs/")    

def logMininetProcesses(popens, logFilePath):
	bandwidthLog = open(logFilePath, "a")
	for host, line in pmonitor(popens):
		if host:
			bandwidthLog.write("<%s>: %s" % (host.name, line))