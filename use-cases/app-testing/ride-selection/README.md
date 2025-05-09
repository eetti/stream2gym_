# Ride Selection

In this application, we present a use-case where the taxi driver can yield higher tips using real-time ride selection. We use original data from New York City Taxi and Limyousine Commission \([TLC dataset](https://www1.nyc.gov/site/tlc/about/tlc-trip-record-data.page)\) and customize it according to our need. These data contains both geographical and financial information of the ride. Taxi ride data are ingested to the event streaming application. In the Spark structured streaming(SS) applicaiton, stream processing engine consume that data and process it in near real-time. To do that, at first, we clean the data. Then, we introduce stream-stream joining with watermarking between geospatial and financial streams. Later, we then take the leverage of geographic coordinates of Manhattan neighbourhoods only (for simplicity)  to find out the relevant rides. Finally, we take a window of thirty minutes to aggregate the average tip in Manhattan locality. The application will inform the taxi driver which area the driver should choose to get a higher tip.

## Architecture

### Application Chain
![image](https://user-images.githubusercontent.com/6629591/182680217-92a61549-0b9c-4e18-afc9-e5cf32d3b8e9.png)


### Topology
![image](https://user-images.githubusercontent.com/6629591/179554520-5b9c84a3-f479-4df4-8405-bc749feaeaa9.png)



## Queries  
  
    sdfFaresWithWatermark = sdfFares.selectExpr("rideId AS rideId_fares", "startTime", "totalFare", "tip").withWatermark("startTime", "30 minutes")
  
    sdfFaresWithWatermark.join(sdfRidesWithWatermark, \
      expr(""" 
       rideId_fares = rideId AND 
        endTime > startTime AND
        endTime <= startTime + interval 2 hours
        """))
  
    sdf.groupBy(window("endTime", "30 minutes", "10 minutes"),"stopNbhd").agg(avg("tip"))
  
## Operations
  
  Selection
  
  Watermarking
  
  Stream-stream join
  
  Broadcasting
  
  Windowed grouped aggegation
  
## Input details
1. About data
   - nycTaxiRidesdata.csv: mostly geographical details of the ride
   - nycTaxiFaresdata.csv : ride financial information
2. topicConfiguration.yaml :
   - contains topic configurations
     - specify topic name ('topicName')
     - specify broker ID to initiate this topic ('topicBroker')
     - number of partition(s) in this topic ('topicPartition')
     - number of replica(s) in this topic ('topicReplica')
3. rideSelection.py : Spark SS application
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
     - consumerConfig: each consumer configuration is specified in ''consumerConfiguration<HostID>.yaml' file. In the YAML file, 
         - for STNDARD consumer, specify the topic name where the consumer will consumer from and number of consumer instances in this node.
         - for CUSTOM consumer, specify the consumer script path and number of consumer instances in this node.
     - sparkConfig: sparkConfig will contain the input source, spark application path and output sink. Input source is a kafka topic, output sink can be kafka topic/a file directory.
 5. nbhd.jsonl: contains all Manhattan neighborhoods coordinates one per line.
 
## Running
   
 ```sudo python3 main.py use-cases/app-testing/ride-selection/input.graphml```
