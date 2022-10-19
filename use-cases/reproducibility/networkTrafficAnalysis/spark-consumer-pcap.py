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

        logging.info("dataframe: ")
        logging.info(pkt_df1.isStreaming)
        logging.info("schema: ")
        logging.info(pkt_df1.printSchema())

        pkt_schema_string = "count INT,src_ip STRING,dst_ip STRING, \
                        proto INT, sport STRING, dport STRING" 

        pkt_df2 = pkt_df1 \
                .select(from_csv(col("value"), pkt_schema_string) \
                        .alias("pkt"), "timestamp")

        pkt_df3 = pkt_df2.select("pkt.*", "timestamp")

        groupedDf = pkt_df.selectExpr("CAST(value AS STRING)")

        # implementation of group by destination ip
        # specifiSrcIPDf = pkt_df3.filter( col("src_ip") == "131.202.240.87")\
        #         .select("count", "src_ip", "dst_ip","proto")
        # specifiSrcIPDf = pkt_df3.filter( col("src_ip") == "192.168.1.11")\
        #         .select("count", "src_ip", "dst_ip","proto")

        # groupedDf = specifiSrcIPDf.groupBy('dst_ip').count()
        # groupedDf = groupedDf.select( concat( lit('destination IP: '), 'dst_ip',\
        #         lit(' IP Counts: '), 'count').alias('value') )

        query = groupedDf.writeStream \
        .format("kafka") \
        .outputMode("update")\
        .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
        .option("topic", sparkOutputTo) \
        .option("checkpointLocation", "logs/output/wordcount_checkpoint_final") \
        .start()
        query.awaitTermination()

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
