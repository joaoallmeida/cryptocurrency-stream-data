# Databricks notebook source
from pyspark.sql import SparkSession
import pyspark.sql.functions as f
import pyspark.sql.types as t
import datetime ,json , os, platform, getpass


credentials = {"username" :os.getenv('MONGODB_USER'), "password": os.getenv('MONGODB_PASS')}
now = datetime.datetime.now()
user = f'{getpass.getuser()}@{platform.node()}'

spark = (SparkSession 
            .builder 
            .appName("myApp") 
            .config("spark.mongodb.output.uri", f"mongodb+srv://{credentials['username']}:{credentials['password']}@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority") 
            .config("spark.mongodb.input.uri", f"mongodb+srv://{credentials['username']}:{credentials['password']}@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority") 
            .getOrCreate())          

## Reading data from Kafka
topicName = 'crypto-data-stream'
server = os.getenv('KAFKA_CLUSTER')
streamName = 'crypto'


streamDf = (spark.readStream   
     .format('kafka')
     .option('kafka.bootstrap.servers',server)
     .option('subscribe',topicName)
     .option("startingOffsets", "earliest") #latest earliest
     .load()
     .select(f.col("value").cast('string'))
)

schema = t.StructType([
  t.StructField("data",t.ArrayType(t.StructType([
      t.StructField("id",t.StringType(), True),
      t.StructField("rank",t.StringType(), True),
      t.StructField("symbol",t.StringType(), True),
      t.StructField("name",t.StringType(), True),
      t.StructField("supply",t.StringType(), True),
      t.StructField("maxSupply",t.StringType(), True),
      t.StructField("marketCapUsd",t.StringType(), True),
      t.StructField("volumeUsd24Hr",t.StringType(), True),
      t.StructField("priceUsd",t.StringType(), True),
      t.StructField("changePercent24Hr",t.StringType(), True),
      t.StructField("vwap24Hr",t.StringType(), True),
      t.StructField("explorer",t.StringType(), True)])),True),
  t.StructField("timestamp",t.LongType(), True)                 
  ]
)

ingestDf = (streamDf.withColumn('value',f.from_json('value',schema))
                    .withColumn('data',f.explode('value.data'))
                    .withColumn('ingestBy',f.lit(user))
                    .withColumn('ingestAt',f.lit(now))
                    .select('data.*','value.timestamp','ingestBy','ingestAt')
)


# Refined Step
longColumnsList = ["marketCapUsd","volumeUsd24Hr","priceUsd","changePercent24Hr","vwap24Hr","maxSupply","supply"]
intColumnsList = ['rank']

refinedDf = ingestDf

for col in longColumnsList:
  refinedDf = refinedDf.withColumn( col , f.col(col).cast(t.DecimalType(38,5)))

for col in intColumnsList:
  refinedDf = refinedDf.withColumn( col , f.col(col).cast(t.IntegerType()) )

refinedDf = refinedDf.na.fill({"explorer":"N/D","marketCapUsd": 0, "volumeUsd24Hr": 0,"priceUsd":0 ,"changePercent24Hr": 0,"vwap24Hr": 0,"maxSupply": 0,"supply": 0})
refinedDf = (refinedDf.withColumn('timestamp', f.from_unixtime((f.col('timestamp')/1000)).cast(t.TimestampType())) 
                      .withColumn('refinedBy', f.lit(user))
                      .withColumn('refinedAt', f.lit(now))
)

# Debug
# query = (
#   refinedDf
#     .writeStream 
#     .format("console") 
#     .start()
# )
# query.awaitTermination()

## Write to mongoDb
connString = f"mongodb+srv://{credentials['username']}:{credentials['password']}@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority"
database = 'financial'
collection = 'crypto'

def writeToMongo(df,epoch_id):
  df.write.format("mongodb").option("connection.uri", connString ).option("database", database).option("collection", collection).mode('append').save()

query = refinedDf.writeStream.foreachBatch(writeToMongo).start()

query.awaitTermination()

