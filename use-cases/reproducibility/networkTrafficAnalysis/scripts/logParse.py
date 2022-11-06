# to run this file sudo python3 logParse.py <consumer log file path>
#!/usr/bin/python3
import sys
from datetime import datetime, timedelta

prodLogDir = "/home/monzurul/Desktop/stream2gym/logs/output/" #sys.argv[1]
consLogFile = "/home/monzurul/Desktop/stream2gym/logs/output/cons-node3-instance1.log" #sys.argv[2]

def producerLogParse(prodLogDir):
    pktList = []
    i = 1
    while i <= 5:
        with open(prodLogDir+'prod-node1-instance'+str(i)+'.log','r') as prodFp:
            lines = prodFp.readlines()
            for line in lines:
                if 'Message: ' in line:
                    productionTimeStr = line.split(' INFO:')[0]
                    productionTime = datetime.strptime(productionTimeStr, "%Y-%m-%d %H:%M:%S,%f")
                    message = line.split('Message: ')[1]
                    messageList = message.split(",")
                    pktDetails = {"nodeID": int(messageList[0]), \
                        "prodInstanceID": int(messageList[1]),\
                        "flowID": int(messageList[2]), "pktID": int(messageList[3]),\
                         "productionTime": productionTime}
                    pktList.append(pktDetails)
        i += 1
    print("Total produced packets: "+str(len(pktList)))
    return pktList

def topicDuplicateLogParse(prodLogFile):
    pktList = []

    with open(prodLogFile,'r') as prodFp:
        lines = prodFp.readlines()
        for line in lines:
            if 'Message: ' in line:
                productionTimeStr = line.split(' INFO:')[0]
                productionTime = datetime.strptime(productionTimeStr, "%Y-%m-%d %H:%M:%S,%f")
                message = line.split('Message: ')[1]
                messageList = message.split(",")
                pktDetails = {"nodeID": int(messageList[0]), \
                    "prodInstanceID": int(messageList[1]),\
                    "flowID": int(messageList[2]), "pktID": int(messageList[3]),\
                        "productionTime": productionTime}
                pktList.append(pktDetails)
    print("Total produced packets: "+str(len(pktList)))
    return pktList


def consumerLogParse(consLogFile):
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
                pktIDs = line.split('packet IDs: ')[1].strip()
                pktIDList = pktIDs.split(",")

                for pkt in pktIDList:
                    pktDetails = {"nodeID": nodeID, "prodInstanceID": prodInstanceID,\
                    "flowID": flowID, "pktID": int(pkt), "consumptionTime": consumptionTime}
                    pktList.append(pktDetails)
                
            lineIndex += 1
    print("Total consumed packets: "+str(len(pktList)))
    # print("Pkt count:  "+str(pktCount))
    return pktList

def comparePkt(prodPktList, consPktList):
    msgLatencyList = []
    consumedMsg = 0
    for index,val in enumerate(prodPktList):
        for index2, val2 in enumerate(consPktList):
            if prodPktList[index]["nodeID"] == consPktList[index2]["nodeID"] and \
                prodPktList[index]["prodInstanceID"] == consPktList[index2]["prodInstanceID"] and \
                prodPktList[index]["flowID"] == consPktList[index2]["flowID"] and \
                prodPktList[index]["pktID"] == consPktList[index2]["pktID"]:

                print("producer message: "+str(val))
                print("consumer message: "+str(val2))
                print("index1: "+str(index))
                print("index2: "+str(index2))
                print("==================")
                latencyMessage = consPktList[index]["consumptionTime"] - prodPktList[index]["productionTime"]
                
                msgLatencyList.append(latencyMessage)
                
                consumedMsg += 1

    avgProcessingTime =  sum(msgLatencyList,timedelta()) / consumedMsg
    print("No of processed pakcets: "+str(consumedMsg))
    print("Avg. processing time per pakcet: "+str(avgProcessingTime))

# prodPktList = producerLogParse(prodLogDir)
# consPktList = consumerLogParse(consLogFile)
# comparePkt(prodPktList, consPktList)

prodPktList = producerLogParse(prodLogDir)
prodPktList2 = topicDuplicateLogParse(consLogFile)
comparePkt(prodPktList, prodPktList2)