## Dependency
Following dependencies are required to be installed to run this application:
```bash
$ sudo pip3 install scapy 
$ sudo apt install python3-pcapy 
```

## Input details
1. topicConfiguration.yaml :
   - contains topic configurations
     - specify topic name ('topicName')
     - specify broker ID to initiate this topic ('topicBroker')
     - number of partition(s) in this topic ('topicPartition')
     - number of replica(s) in this topic ('topicReplica')
2. flow-producer-synthetic.py : user specified producer 
   MyScapyExtract.py : helper script for the producer
3. spark-consumer-pcap : user specified spark structured streaming application
4. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations 
     - topicConfig: path to the topic configuration file
     - zookeeper: 1 = hostnode contains a zookeeper instance
     - broker: 1 = hostnode contains a zookeeper instance
     - producerType: producer type can be SFST/MFMT/ELTT/INDIVIDUAL; SFST denotes from Single File to Single Topic. ELTT is defined when Each line To Topic i.e. each line of the file is produced to the topic as a single message. For SFST/MFMT/ELTT, a standard producer will work be default.
     Provided that the user has his own producer, he can use it by specifying INDIVIDUAL in the producerType and give the relative path as input in producerType attribute as a pair of producerType,producerFilePath.
     - producerConfig: for SFST/ELTT, one tuple of filePath, topicName, number of files and number of producer instances in this node. For INDIVIDUAL producer type, filePath and number of files are two optional parameters
     - consumerConfig: a pair containing information of topic name for consumption and number of consumer instances in this node.

## Running
   
 ```sudo python3 main.py use-cases/reproducibility/networkTrafficAnalysis/input.graphml --nzk 1 --nbroker 1 --time 50```
