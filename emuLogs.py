#!/usr/bin/python3

import os
import logging

def configureLogDir(nSwitches, mSizeString, mRate, nTopics):  
	os.system("sudo rm -rf logs/kafka/"+"switches:" +str(nSwitches)+ "_mSize:"+ mSizeString\
		+ "_mRate:"+ str(mRate)+ "_topics:"+str(nTopics)\
		+"/bandwidth/"+"; sudo mkdir -p logs/kafka/"+"switches:" +str(nSwitches)+ "_mSize:"\
		+ mSizeString+ "_mRate:"+ str(mRate)+ "_topics:"+str(nTopics)+"/bandwidth/")
    
	os.system("sudo rm -rf logs/kafka/"+"switches:" +str(nSwitches)+ "_mSize:"+ mSizeString\
		+ "_mRate:"+ str(mRate)+ "_topics:"+str(nTopics)\
		+"/prod/"+"; sudo mkdir -p logs/kafka/"+"switches:" +str(nSwitches)+ "_mSize:"\
		+ mSizeString+ "_mRate:"+ str(mRate)+ "_topics:"+str(nTopics)+"/prod/")    

	os.system("sudo rm -rf logs/kafka/"+"switches:" +str(nSwitches)+ "_mSize:"+ mSizeString\
		+ "_mRate:"+ str(mRate)+ "_topics:"+str(nTopics)\
		+"/cons/"+"; sudo mkdir -p logs/kafka/"+"switches:" +str(nSwitches)+ "_mSize:"\
		+ mSizeString+ "_mRate:"+ str(mRate)+ "_topics:"+str(nTopics) +"/cons/")

	# os.system("sudo rm -rf logs/output/; sudo mkdir -p logs/output/")
	os.system("sudo rm -rf logs/output/prod/; sudo mkdir -p logs/output/prod/")
	os.system("sudo rm -rf logs/output/cons/; sudo mkdir -p logs/output/cons/")

	logging.basicConfig(filename="logs/kafka/"+"switches:" +str(nSwitches)+ "_mSize:"\
							+ mSizeString+ "_mRate:"+ str(mRate)+ "_topics:"+str(nTopics) \
							+"/events.log",\
						format='%(levelname)s:%(message)s',\
 						level=logging.INFO)


def cleanLogs():
	os.system("sudo rm -rf logs/kafka/")
	os.system("sudo rm -rf logs/output/")
	os.system("sudo rm -rf kafka/logs/")    