# Document Analytics


## Architecture

### Application Chain




### Topology



## Queries  
  

  
## Operations
  

  
## Input details
1. topicConfiguration.txt : associated topic name(s) in each line
2. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations 
     - topicConfig: path to the topic configuration file
     - zookeeper: 1 = hostnode contains a zookeeper instance
     - broker: 1 = hostnode contains a zookeeper instance
     - producerType: producer type can be SFST/MFMT/RND; SFST denotes from Single File to Single Topic. MFMT,RND not supported right now.
     - producerConfig: for SFST, one pair of filePath, topicName
     - sparkConfig: sparkConfig will contain the input source, spark application path and output sink. Input source is a kafka topic, output sink can be kafka topic/a file directory.
 
## Running
   
 ```sudo python3 main.py use-cases/app-testing/millitary-coordination/input.graphml --nzk 1 --nbroker 3 --only-kafka 1```
