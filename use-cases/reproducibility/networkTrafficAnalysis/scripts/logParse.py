# to run this file sudo python3 logParse.py <producer log dir> 
# <consumer log file path> <no of producer instances> <spark/td>
#!/usr/bin/python3
import sys
from datetime import datetime, timedelta

# prodLogDir = "/home/monzurul/Desktop/stream2gym/logs/output/" #sys.argv[1]
# consLogFile = "/home/monzurul/Desktop/stream2gym/logs/output/cons-node3-instance1.log" #sys.argv[2]

prodLogDir = sys.argv[1]
consLogFile = sys.argv[2]
prodInstances = int(sys.argv[3])
choice = sys.argv[4]

def producerLogParse(prodLogDir, prodInstances):
    pktList = []
    i = 1
    while i <= prodInstances:
        with open(prodLogDir+'/prod-node1-instance'+str(i)+'.log','r') as prodFp:
            lines = prodFp.readlines()
            searchWord = 'Message produced: '
            for line in lines:
                if searchWord in line:
                    productionTimeStr = line.split(' INFO:')[0]
                    productionTime = datetime.strptime(productionTimeStr, "%Y-%m-%d %H:%M:%S,%f")
                    message = line.split(searchWord)[1]
                    messageList = message.split(",")
                    pktDetails = {"nodeID": int(messageList[0]), \
                        "prodInstanceID": int(messageList[1]),\
                        "flowID": int(messageList[2]), "pktID": int(messageList[3]),\
                         "productionTime": productionTime}
                    pktList.append(pktDetails)
        i += 1
    print("Total produced packets: "+str(len(pktList)))
    return pktList

def topicDuplicateLogParse(consLogFile):
    pktList = []

    with open(consLogFile,'r') as consFp:
        lines = consFp.readlines()
        searchWord = 'Message received: '
        for line in lines:
            if searchWord in line:
                consumptionTimeStr = line.split(' INFO:')[0]
                consumptionTime = datetime.strptime(consumptionTimeStr, "%Y-%m-%d %H:%M:%S,%f")
                message = line.split(searchWord)[1]
                messageList = message.split(",")
                pktDetails = {"nodeID": int(messageList[0]), \
                    "prodInstanceID": int(messageList[1]),\
                    "flowID": int(messageList[2]), "pktID": int(messageList[3]),\
                        "consumptionTime": consumptionTime}
                pktList.append(pktDetails)
    print("Total consumed packets(in duplicate topic): "+str(len(pktList)))
    return pktList


def sparkConsumerLogParse(consLogFile):
    pktCount = 0
    pktIDList = []
    pktList = []

    with open(consLogFile, 'r') as fp:
        lines = fp.readlines()
        searchWord = 'total packets: '
        lineIndex = 1
        for line in lines:
            if searchWord in line:
                # print("Line no: "+str(lineIndex))
                pktCount += int(line.split(searchWord)[1].split(' ')[0])

                # generating packet wise consumption log
                consumptionTimeStr = line.split(' INFO:')[0]
                consumptionTime = datetime.strptime(consumptionTimeStr, "%Y-%m-%d %H:%M:%S,%f")
                nodeID = int(line.split('Producer Node: ')[1].split(' ')[0])
                prodInstanceID = int(line.split('user: ')[1].split(' ')[0])
                flowID = int(line.split('flow ID: ')[1].split(' ')[0])
                portID = int(line.split('destination Port: ')[1].split(' ')[0])
                pktIDs = line.split('packet IDs: ')[1].strip()
                pktIDList = pktIDs.split(",")

                for pktID in pktIDList:
                    pktDetails = {"nodeID": nodeID, "prodInstanceID": prodInstanceID,\
                    "flowID": flowID, "portID": portID, "pktID": int(pktID), "consumptionTime": consumptionTime}

                    # checking if there is already any entry for this packet
                    if not any(pkt['nodeID'] == nodeID and
                        pkt['prodInstanceID'] == prodInstanceID and\
                        pkt['flowID'] == flowID and\
                        pkt['portID'] == portID and\
                        pkt['pktID'] == int(pktID) \
                        for pkt in pktList):
                            pktList.append(pktDetails)
                    # else:
                    #     print("Producer Node: "+str(nodeID)+" "+"user: "+str(prodInstanceID)+\
                    #         " "+"flow ID: "+str(flowID)+" "+"destination Port: "+\
                    #         str(portID)+" "+"packet ID: "+str(pktID))
                    
            lineIndex += 1
    print("Total consumed packets: "+str(len(pktList)))
    print("Pkt count:  "+str(pktCount))
    return pktList

def comparePkt(prodPktList, consPktList):
    msgLatencyList = []
    consumedMsg = 0
    for index,val in enumerate(consPktList):
        for index2, val2 in enumerate(prodPktList):
            if consPktList[index]["nodeID"] == prodPktList[index2]["nodeID"] and \
                consPktList[index]["prodInstanceID"] == prodPktList[index2]["prodInstanceID"] and \
                consPktList[index]["flowID"] == prodPktList[index2]["flowID"] and \
                consPktList[index]["pktID"] == prodPktList[index2]["pktID"]:

                # print("producer message: "+str(val2))
                # print("consumer message: "+str(val))                
                # print("producerindex: "+str(index2))
                # print("consumer index: "+str(index))
                # print("==================")
                latencyMessage = consPktList[index]["consumptionTime"] - prodPktList[index2]["productionTime"]
                
                msgLatencyList.append(latencyMessage)
                
                consumedMsg += 1

    diff =  sum(msgLatencyList,timedelta()) / consumedMsg
    # Convert timedelta object to Milliseconds
    avgProcessingTime = diff.total_seconds() * 1000
    # print("No of processed packets: "+str(consumedMsg))
    print("Avg. end-to-end latency per packet(in ms): "+str(avgProcessingTime))

# processing Spark log
if choice == 'spark':
    prodPktList = producerLogParse(prodLogDir, prodInstances)
    consPktList = sparkConsumerLogParse(consLogFile)
    comparePkt(prodPktList, consPktList)

# processing topicDuplicate log
elif choice == 'td':
    prodPktList = producerLogParse(prodLogDir, prodInstances)
    consPktList = topicDuplicateLogParse(consLogFile)
    comparePkt(prodPktList, consPktList)