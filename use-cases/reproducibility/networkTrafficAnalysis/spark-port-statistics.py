from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import time

import sys
import logging

try:
        sparkInputFrom = "inputTopic" 
        sparkOutputTo = "outputTopic" 
        kafka_bootstrap_servers = "10.0.0.1:9092"

        logging.basicConfig(filename="logs/output/spark1.log",\
		format='%(asctime)s %(levelname)s:%(message)s',\
		level=logging.INFO)

        logging.info("kafka server: "+kafka_bootstrap_servers)
        logging.info("input: "+sparkInputFrom)
        logging.info("output: "+sparkOutputTo)

        spark = SparkSession \
                .builder \
                .appName("Structured Streaming Pkt") \
                .master("local[*]") \
                .getOrCreate()

        spark.sparkContext.setLogLevel("ERROR")

        # Construct a streaming DataFrame that reads from topic
        pkt_df = spark \
                .readStream \
                .format("kafka") \
                .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
                .option("subscribe", sparkInputFrom) \
                .load()

        pkt_df1 = pkt_df.selectExpr("CAST(value AS STRING)", "timestamp")


        pkt_schema_string = "nodeID INT, prodInstanceID INT, flowCount INT,\
                pktCount INT,srcIP STRING,dstIP STRING, \
                proto INT, srcPort STRING, dstPort STRING,payloadLength INT, \
                payload STRING" 

        pkt_df2 = pkt_df1 \
                .select(from_csv(col("value"), pkt_schema_string) \
                        .alias("pkt"), "timestamp")

        pkt_df3 = pkt_df2.select("pkt.*", "timestamp")

        groupedDf = pkt_df3.groupBy('nodeID', 'prodInstanceID', 'flowCount', 'dstPort')\
                .agg(count("pktCount").alias("totalPkts"),\
                collect_set("pktCount").alias("pktIDList"))

        groupedDf2 = groupedDf.withColumn("pktIDs", concat_ws(",", col("pktIDList")))

        # to produce the message in Kafka topic
        groupedDf = groupedDf2.select( concat( \
                lit(' Producer Node: '), 'nodeID',\
                lit(' user: '), 'prodInstanceID',\
                lit(' flow ID: '), 'flowCount',\
                lit(' destination Port: '), 'dstPort',\
                lit(' total packets: '), 'totalPkts',\
                lit(' packet IDs: '), 'pktIDs',\
                ).alias('value') )

        query = groupedDf.writeStream \
        .trigger(processingTime='1 seconds')\
        .format("kafka") \
        .outputMode("update")\
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("topic", sparkOutputTo) \
        .option("checkpointLocation", "logs/output/wordcount_checkpoint_final") \
        .start()

        while query.isActive:
                logging.info("\n")
                logging.info(query.status)
                logging.info("\n")
                logging.info(query.lastProgress)

                time.sleep(1)
        
        # query.awaitTermination()

        # ==========================================
        #pkt_df3 = pkt_df2.select("pkt.*")

        #summary = pkt_df3 \
        #         .groupBy("proto") \
        #         .count()

        #query = summary \
        # query = groupedDf \
        #         .writeStream \
        #         .trigger(processingTime='5 seconds') \
        #         .outputMode("complete") \
        #         .format("console") \
        #         .start()

        ### If you want to try storing the data frames in files.
        #query = pkt_df3 \
        #        .writeStream \
        #        .trigger(processingTime='5 seconds') \
        #        .outputMode("append") \
        #        .format("csv") \
        #        .option("checkpointLocation", "/home/raja/kafka/pkt-example") \
        #        .option("path", "/home/raja/kafka/pkt-example") \
        #        .start()


        # query.awaitTermination()

except Exception as e:
    logging.error(e)
    sys.exit(1)
