from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, explode
from pyspark.sql.types import StructType, StructField, StringType, IntegerType, ArrayType
from Elasticsearch import save_to_elasticsearch   # Importar la función de Elasticsearch
from Cassandra import save_to_cassandra  # Importar la función de Cassandra
import json

# Configuración dinámica
kafka_brokers = "localhost:9092"  # Cambia esto si Kafka no está en localhost
topic_name = "reportes_trafico"   # Asegúrate de usar el nombre correcto del tópico

# Esquema del JSON (ajustado según el ejemplo proporcionado)
alert_schema = StructType([
    StructField("alerts", ArrayType(StructType([
        StructField("country", StringType(), True),
        StructField("city", StringType(), True),
        StructField("type", StringType(), True),
        StructField("street", StringType(), True),
        StructField("confidence", IntegerType(), True),
        StructField("reliability", IntegerType(), True)
    ])))
])

# Iniciar SparkSession
spark = SparkSession \
    .builder \
    .appName("KafkaMessageReader") \
    .config("spark.jars.packages",
        "org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.0,com.google.code.findbugs:jsr305:3.0.2") \
    .getOrCreate()

# Leer datos de Kafka
kafka_df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", kafka_brokers) \
    .option("subscribe", topic_name) \
    .option("startingOffsets", "earliest") \
    .option("failOnDataLoss", "false") \
    .load()

# Procesar el mensaje JSON
processed_df = kafka_df \
    .selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), alert_schema).alias("data")) \
    .select(explode(col("data.alerts")).alias("alert")) \
    .select(
        col("alert.country").alias("Country"),
        col("alert.city").alias("City"),
        col("alert.type").alias("Type"),
        col("alert.street").alias("Street"),
        col("alert.confidence").alias("Confidence"),
        col("alert.reliability").alias("Reliability")
    )

# Filtrar datos válidos (opcional)
valid_df = processed_df.filter(
    col("Country").isNotNull() & 
    col("City").isNotNull() & 
    col("Type").isNotNull() & 
    col("Street").isNotNull() & 
    col("Confidence").isNotNull() & 
    col("Reliability").isNotNull()
)

# # Función para guardar en Elasticsearch
def write_to_elasticsearch(df, epoch_id):
    try:
        data = df.toJSON().map(lambda x: json.loads(x)).collect()
        save_to_elasticsearch(data)
        print(f"Datos guardados en Elasticsearch en epoch {epoch_id}.")
    except Exception as e:
        print(f"Error al guardar en Elasticsearch: {e}")

# Escribir en Elasticsearch
elasticsearch_query = valid_df.writeStream \
    .foreachBatch(write_to_elasticsearch) \
    .outputMode("append") \
    .start()


# Función para guardar en Cassandra
def write_to_cassandra(df, epoch_id):
    try:
        data = df.toJSON().map(lambda x: json.loads(x)).collect()
        save_to_cassandra(data)
        print(f"Datos guardados en Cassandra en epoch {epoch_id}.")
    except Exception as e:
        print(f"Error al guardar en Cassandra: {e}")

# Escribir en Cassandra
cassandra_query = valid_df.writeStream \
    .foreachBatch(write_to_cassandra) \
    .outputMode("append") \
    .start()


# Mostrar mensajes procesados en la consola
console_query = valid_df \
    .writeStream \
    .outputMode("append") \
    .format("console") \
    .start()

# Esperar hasta que terminen todos los streams
elasticsearch_query.awaitTermination()
console_query.awaitTermination()
cassandra_query.awaitTermination()
