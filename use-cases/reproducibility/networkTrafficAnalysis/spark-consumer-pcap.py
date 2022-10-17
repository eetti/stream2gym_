from pyspark.sql import SparkSession
from pyspark.sql.functions import *
import time

kafka_topic_name = "outputTopic" #"pkttest_pcap"
kafka_bootstrap_servers = "10.0.0.1:9092"

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
        .option("subscribe", kafka_topic_name) \
        .load()


pkt_df1 = pkt_df.selectExpr("CAST(value AS STRING)", "timestamp")

pkt_schema_string = "count INT,src_ip STRING,dst_ip STRING, \
                     proto INT, sport STRING, dport STRING" 

pkt_df2 = pkt_df1 \
        .select(from_csv(col("value"), pkt_schema_string) \
                .alias("pkt"), "timestamp")

pkt_df3 = pkt_df2.select("pkt.*", "timestamp")

# implementation of group by destination ip
specifiSrcIPDf = pkt_df3.filter( col("src_ip") == "131.202.240.87")\
        .select("count", "src_ip", "dst_ip","proto")
# pkt_df3 = pkt_df3.select("pkt").where("src_ip > 192.168.1.11")

groupedDf = specifiSrcIPDf.groupBy('dst_ip').count()
groupedDf = groupedDf.select( concat( lit('destination IP: '), 'dst_ip',\
        lit(' IP Counts: '), 'count').alias('value') )

query = groupedDf.writeStream \
    .format("kafka") \
    .outputMode("complete")\
    .option("kafka.bootstrap.servers", kafka_bootstrap_servers) \
    .option("topic", kafka_topic_name) \
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


