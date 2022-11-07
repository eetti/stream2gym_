#!/usr/bin/python3
# this script will duplicate data from one topic to another
# command to run this script: sudo python3 topicDuplicate.py

from kafka import KafkaConsumer
from kafka import KafkaProducer
from threading import Thread
from queue import Queue
import logging

topic1  = "inputTopic"
topic2 = "outputTopic"

data = Queue()

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

kafka_bootstrap_servers = "10.0.0.1:9092"
consumer = KafkaConsumer(
     topic1,
     bootstrap_servers=[kafka_bootstrap_servers]
    )

producer1 = KafkaProducer(bootstrap_servers=[kafka_bootstrap_servers])

def readTopicData(threadLogger):
    # print("received")    
    for message in consumer:
        msgValue = str(message.value, 'utf-8')
        threadLogger.info("Consumed: "+msgValue)
        data.put(msgValue)

def sendDataToTopic(threadLogger):
    while True:
        msgToSend = bytes(data.get(),'utf-8')
        producer1.send(topic2, value=msgToSend)
        threadLogger.info("Produced: "+data.get())
        # producer1.flush()

if __name__ == "__main__":
    logFile = "logs/output/"+"topicDuplicateLogger.log"
    threadLogger = setup_logger('threadLogger', logFile)

    read_thread = Thread(target=readTopicData, args=(threadLogger,))
    read_thread.start()
    write_thread = Thread(target=sendDataToTopic, args=(threadLogger,))
    write_thread.start()