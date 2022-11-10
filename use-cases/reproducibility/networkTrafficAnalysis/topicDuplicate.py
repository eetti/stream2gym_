#!/usr/bin/python3
# this script will duplicate data from one topic to another
# command to run this script: sudo python3 topicDuplicate.py

from kafka import KafkaConsumer
from kafka import KafkaProducer
import logging

from multiprocessing import Process
from multiprocessing import Queue

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def readTopicData(threadLogger, data):  
    topic1  = "inputTopic"
    kafka_bootstrap_servers = "10.0.0.1:9092"
    consumer = KafkaConsumer(
        topic1,
        bootstrap_servers=[kafka_bootstrap_servers]
        )   
    for message in consumer:
        msgValue = str(message.value, 'utf-8')     
        data.put(msgValue)
        threadLogger.info("Consumed: "+msgValue)
    data.put(None)

def sendDataToTopic(threadLogger,threadID, data):
    topic2 = "outputTopic"
    kafka_bootstrap_servers = "10.0.0.1:9092"
    producer1 = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
    while True:
        # get a unit of work
        item = data.get()
        # check for stop
        if item is None:
            break
        # send
        producer1.send(topic2, item.encode())
        threadLogger.info("Produced in Process "+str(threadID)+": "+item)

if __name__ == "__main__":
    queue = Queue()
    logFile = "logs/output/"+"topicDuplicateLogger.log"
    threadLogger = setup_logger('threadLogger', logFile)

    read_thread = Process(target=readTopicData, args=(threadLogger,queue,))
    read_thread.start()
    write_thread = Process(target=sendDataToTopic, args=(threadLogger,1, queue))
    write_thread.start()