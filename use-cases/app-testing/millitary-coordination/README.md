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
     - producerType: producer type is a pair of producer type and producer script path. Here, INDIVIDUAL refers to the producer served by the user.
     - producerConfig: it is a tuple of topic name, number of producer instances on this node.

 
## Running
   
 ```sudo python3 main.py use-cases/app-testing/millitary-coordination/input.graphml --nzk 3 --nbroker 3 --time 300``
