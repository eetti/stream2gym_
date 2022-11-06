#!/usr/bin/python3
# this script will duplicate data from one topic to another
# command to run this script: sudo python3 topicDuplicate.py

from kafka import KafkaConsumer
from kafka import KafkaProducer
from threading import Thread
from queue import Queue

topic1  = "inputTopic"
topic2 = "outputTopic"

data = Queue()

kafka_bootstrap_servers = "10.0.0.1:9092"
consumer = KafkaConsumer(
     topic1,
     bootstrap_servers=[kafka_bootstrap_servers],
     group_id='my-group'
    )

producer1 = KafkaProducer(bootstrap_servers=[kafka_bootstrap_servers])

def readTopicData():
    print("received")
    for message in consumer:
        msgValue = str(message.value, 'utf-8')
        print(msgValue)
        data.put(msgValue)

def sendDataToTopic():
    while True:
        msgToSend = bytes(data.get(),'utf-8')
        producer1.send(topic2, value=msgToSend)
        producer1.flush()

if __name__ == "__main__":
    read_thread = Thread(target=readTopicData)
    read_thread.start()
    write_thread = Thread(target=sendDataToTopic)
    write_thread.start()