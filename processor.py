from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType

# Spark Session
spark = SparkSession.builder \
    .appName("TrafficProcessor") \
    .getOrCreate()

# Schema
schema = StructType() \
    .add("type", StringType()) \
    .add("location", StringType()) \
    .add("severity", StringType())

# Kafka Stream
traffic_stream = spark.readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "traffic-events") \
    .load()

# Process the data
traffic_data = traffic_stream.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

# Write to Cassandra
traffic_data.writeStream \
    .format("org.apache.spark.sql.cassandra") \
    .option("keyspace", "traffic") \
    .option("table", "historical_events") \
    .start()

# Write to Elasticsearch
traffic_data.writeStream \
    .format("org.elasticsearch.spark.sql") \
    .option("es.nodes", "elasticsearch") \
    .option("es.port", "9200") \
    .option("checkpointLocation", "/tmp/checkpoints") \
    .option("es.resource", "traffic-events/_doc") \
    .start() \
    .awaitTermination()
