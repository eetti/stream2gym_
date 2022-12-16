# Sentiment analysis

In this application, we use python's specialized NLP library 'Textblob' to analyse the subjectivity and objectivity of those tweets. We first connect to Twitter using developer API and store tweets on a specific topic. As part of the pre-processing, we clean the unnecessary details (e.g., links, usernames, hashtags, re-tweets). Data is ingested to Kafka topic and then to the Spark Structured Streaming(SS) dataframe for real-time analysis. Using user-defined functions in Apache Spark, we imply text classification rules on received data and finally get a score of subjectivity and polarity. Subjectivity will be in the floating range of [0.0,1.0] where 0.0 denotes as very subjective and 1.0 denotes very objective. Polarity varies within [0.0,-1.0]. 

### Textblob
This is a python library supports various operation for Natural language processing (NLP) - parts-of-speech tagging, sentiment analysis, parsing, classification, noun phrase extraction etc. It is built over two python modules – pattern and NLTK. For sentiment analysis, it uses pattern library mainly. For a given text, it matches each word of that text with a dictionary of adjectives and their manual-tagged values and computes average polarity and subjectivity. 

## Architecture

### Application Chain
![image](https://user-images.githubusercontent.com/6629591/179554976-efa59ad7-baa8-44ca-b9cf-560db7c48ade.png)

### Topology
![image](https://user-images.githubusercontent.com/6629591/179555037-35379a7e-6e4e-46dc-a5ae-7f7865e898e0.png)



## Queries  
  
  select(explode(split(lines.value, "t_end")).alias("word"))
  
  polarity_detection
  
  subjectivity_detection
  
## Operations
  
  Selection
  
  User-defined function
  
## Input details
1. data.txt : contains input data
2. topicConfiguration.yaml :
   - contains topic configurations
     - specify topic name ('topicName')
     - specify broker ID to initiate this topic ('topicBroker')
     - number of partition(s) in this topic ('topicPartition')
     - number of replica(s) in this topic ('topicReplica')
3. sentimentAnalysis.py : Spark SS application
4. input.graphml:
   - contains topology description
     - node details (switch, host)
     - edge details (bandwidth, latency, source port, destination port)
   - contains component(s) configurations 
     - topicConfig : path to the topic configuration file
     - zookeeper : 1 = hostnode contains a zookeeper instance
     - broker : 1 = hostnode contains a zookeeper instance
     - producerType: producer type can be SFST/MFMT/ELTT/INDIVIDUAL; SFST denotes from Single File to Single Topic. ELTT is defined when Each line To Topic i.e. each line of the file is produced to the topic as a single message. For SFST/MFMT/ELTT, a standard producer will work be default.
     Provided that the user has his own producer, he can use it by specifying INDIVIDUAL in the producerType and give the relative path as input in producerType attribute as a pair of producerType,producerFilePath.
     - producerConfig: specified in producerConfiguration.yaml
          for SFST/ELTT, user needs to specify filePath, name of the topic to produce, number of files and number of producer instances in this node. For INDIVIDUAL producer type, only producer script path and number of producer instances on this node are the two required parameters to specify.
     - consumerType: consumer type can be STANDARD/INDIVIDUAL; To use standard consumer, specify 'STANDARD'. Provided that the user has his own consumer, he can use it by specifying INDIVIDUAL in the consumerType and give the relative path as input in producerType attribute as a pair like INDIVIDUAL,producerFilePath
     - consumerConfig: each consumer configuration is specified in consumerConfiguration.yaml file. In the YAML file, 
         - for STNDARD consumer, specify the topic name where the consumer will consumer from and number of consumer instances in this node.
         - for INDIVIDUAL consumer, specify the consumer script path and number of consumer instances in this node.
     - sparkConfig: sparkConfig will contain the spark application path and output sink. Output sink can be kafka topic/a file directory.
     
## Running
   
 ```sudo python3 main.py use-cases/app-testing/sentiment-analysis/input.graphml --nzk 1 --nbroker 2```
