## multi-producer, multi-consumer with multi-thread

#!/usr/bin/python3
# this script will duplicate data from one topic to another
# command to run this script: sudo python3 topicDuplicate.py

from kafka import KafkaConsumer
from kafka import KafkaProducer
import logging

from threading import Thread
from queue import Queue

from time import sleep
from random import random
from threading import Barrier

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def producerToQueue(consumer1, threadLogger, threadID, data, barrier):   #producer
    for message in consumer1:
        # block, to simulate effort
        sleep(0)
        msgValue = str(message.value, 'utf-8')     
        data.put(msgValue)
        threadLogger.info("Consumed in thread "+str(threadID)+" : "+msgValue)
    # wait for all producers to finish
    barrier.wait()
    # signal that there are no further items
    if threadID == 0:
        data.put(None)

def consumeFromQueue(threadLogger,threadID, data): # consumer
    topic2 = "outputTopic"
    kafka_bootstrap_servers = "10.0.0.1:9092"
    producer1 = KafkaProducer(bootstrap_servers=kafka_bootstrap_servers)
    while True:
        # get a unit of work
        item = data.get()
        # check for stop
        if item is None:
            # add the signal back for other consumers
            queue.put(item)
            # stop running
            break
        # block, to simulate effort
        sleep(0)
        # send
        producer1.send(topic2, item.encode())
        threadLogger.info("Produced in thread "+str(threadID)+": "+item)

if __name__ == "__main__":
    # create the shared barrier
    nConsumers = 1
    nProducers = 1
    
    queue = Queue()
    logFile = "logs/output/"+"topicDuplicateLogger.log"
    threadLogger = setup_logger('threadLogger', logFile)

    topic1  = "inputTopic"
    kafka_bootstrap_servers = "10.0.0.1:9092"
    consumer1 = KafkaConsumer(
        topic1,
        bootstrap_servers=[kafka_bootstrap_servers],
        auto_offset_reset='earliest'
        )

    barrier = Barrier(nProducers)
    # start the consumers
    consumers = [Thread(target=consumeFromQueue, args=(threadLogger,i, queue, ))\
         for i in range(nConsumers)]
    for consumer in consumers:
        consumer.start()
    # start the producers
    producers = [Thread(target=producerToQueue, args=(consumer1, threadLogger, i, \
        queue, barrier))\
         for i in range(nProducers)]
    # start the producers
    for producer in producers:
        producer.start()