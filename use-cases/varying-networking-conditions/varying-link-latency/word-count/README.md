# Word count

In this application, we facilated the running word-count application using a two Spark structured streaming(SS) applications chain. We use two Kafka topic respectively for input source and output sink. In the first application, textual data is ingested from one kafka topic to another via spark structured stream. The second application splits each line into words, generates running word count on those words and lastly, store the calculated value at a local file.


## Architecture

### Application Chain

![image](https://user-images.githubusercontent.com/6629591/185228018-2c9f9701-ff7e-42e0-9df2-d5042b49a8bb.png)


### Topology

![image](https://user-images.githubusercontent.com/6629591/185228142-f6256cf9-4e13-4e1c-a1b6-2c137382ea83.png)


## Queries  
  
      lines.select(explode(split(lines.value, ' ')).alias('word'))
      
      words.groupBy('word').count()
  
## Operations
  
  Selection
  
  Aggegation
  
## Input details
1. dataDir: contains textual data files.
2. topicConfiguration.yaml :
   - contains topic configurations
     - specify topic name ('topicName')
     - specify broker ID to initiate this topic ('topicBroker')
     - number of partition(s) in this topic ('topicPartition')
     - number of replica(s) in this topic ('topicReplica')
3. wordCount.py: Spark SS application
4. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations 
     - topicConfig: path to the topic configuration file
     - zookeeper: 1 = hostnode contains a zookeeper instance
     - broker: 1 = hostnode contains a zookeeper instance
     - producerType: producer type can be SFST/MFMT/ELTT/CUSTOM; SFST denotes from Single File to Single Topic. ELTT is defined when Each line To Topic i.e. each line of the file is produced to the topic as a single message. For SFST/MFMT/ELTT, a standard producer will work be default.
     Provided that the user has his own producer, he can use it by specifying CUSTOM in the producerType and give the relative path as input in producerType attribute as a pair of producerType,producerFilePath.
     - producerConfig: specified in producerConfiguration.yaml
          for SFST/ELTT, user needs to specify filePath, name of the topic to produce, number of files and number of producer instances in this node. For CUSTOM producer type, only producer script path and number of producer instances on this node are the two required parameters to specify.
     - consumerType: consumer type can be STANDARD/CUSTOM; To use standard consumer, specify 'STANDARD'. Provided that the user has his own consumer, he can use it by specifying CUSTOM in the consumerType and give the relative path as input in producerType attribute as a pair like CUSTOM,producerFilePath
     - consumerConfig: each consumer configuration is specified in consumerConfiguration.yaml file. In the YAML file, 
         - for STNDARD consumer, specify the topic name where the consumer will consumer from and number of consumer instances in this node.
         - for CUSTOM consumer, specify the consumer script path and number of consumer instances in this node.
     - sparkConfig: sparkConfig will contain the spark application path and output sink. Output sink can be kafka topic/a file directory.
 
## Running
   
 ```sudo python3 main.py use-cases/varying-networking-conditions/varying-link-latency/word-count/input.graphml --nzk 1 --nbroker 1```


<!-- to run the temporary configuration:
sudo python3 main.py use-cases/varying-networking-conditions/varying-link-latency/word-count/input-temp.graphml --nzk 1 --nbroker 2 -->