#!/usr/bin/python3

import subprocess
import os
import time
import sys

interval = 5

nSwitches = int(sys.argv[1])
mSizeString = sys.argv[2]
mRate = float(sys.argv[3])
nTopics = int(sys.argv[4])

while True:

	for i in range(nSwitches):
        
		bandwidthLog = open("logs/kafka/"+"switches:" +str(nSwitches)+ "_mSize:"\
			+ mSizeString+ "_mRate:"+ str(mRate)+ "_topics:"+str(nTopics) \
			+"/bandwidth/bandwidth-log" + str(i+1) + ".txt", "a")

		statsProcess = subprocess.Popen("sudo ovs-ofctl dump-ports s"+str(i+1), shell=True, stdout=subprocess.PIPE)
		stdout = statsProcess.communicate()[0]
		bandwidthLog.write(stdout.decode("utf-8"))  #converting bytes to string
		bandwidthLog.close()

	time.sleep(interval)










