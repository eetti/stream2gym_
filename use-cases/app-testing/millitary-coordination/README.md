# Document Analytics


## Architecture

### Application Chain




### Topology



## Queries  
  

  
## Operations
  

  
## Input details
1. topicConfiguration.yaml :
   - contains topic configurations
     - specify topic name ('topicName')
     - specify broker ID to initiate this topic ('topicBroker')
     - number of partition(s) in this topic ('topicPartition')
     - number of replica(s) in this topic ('topicReplica')
2. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations 
     - topicConfig: path to the topic configuration file
     - zookeeper: 1 = hostnode contains a zookeeper instance
     - broker: 1 = hostnode contains a zookeeper instance
     - producerType: producer type can be SFST/MFMT/ELTT/INDIVIDUAL; SFST denotes from Single File to Single Topic. ELTT is defined when Each line To Topic i.e. each line of the file is produced to the topic as a single message. For SFST/MFMT/ELTT, a standard producer will work be default.
     Provided that the user has his own producer, he can use it by specifying INDIVIDUAL in the producerType and give the relative path as input in producerType attribute as a pair of producerType,producerFilePath.
     - producerConfig: specified in producerConfiguration.yaml
          for SFST/ELTT, user needs to specify filePath, name of the topic to produce, number of files and number of producer instances in this node. For INDIVIDUAL producer type, only producer script path and number of producer instances on this node are the two required parameters to specify.
     - consumerType: consumer type can be STANDARD/INDIVIDUAL; To use standard consumer, specify 'STANDARD'. Provided that the user has his own consumer, he can use it by specifying INDIVIDUAL in the consumerType and give the relative path as input in producerType attribute as a pair like INDIVIDUAL,producerFilePath
     - consumerConfig: specify the topic name to  consumer from and number of consumer instances in this node as a comma separated pair.

 
## Running
   
 ```sudo python3 main.py use-cases/app-testing/millitary-coordination/input.graphml --nzk 10 --nbroker 10 --replica-min-bytes 200000 --replica-max-wait 5000 --capture-all --time 300``