FROM bitnami/spark:3.3.1

USER 1001
WORKDIR /app

# COPY requirements.txt .
COPY ./scripts .

# RUN rm -r /opt/bitnami/spark/jars && \
#     curl --location http://mirror.cc.columbia.edu/pub/software/apache/spark/spark-3.0.0/spark-3.0.0-bin-hadoop2.7.tgz | \
#     tar --extract --gzip --strip=1 --directory /opt/bitnami/spark/ spark-3.0.0-bin-hadoop2.7/jars/
    

# RUN apt-get update && apt-get install -y
# RUN python3 -m pip install --upgrade pip
# RUN pip3 install -r ./requirements.txt
RUN  spark-submit --master spark://spark:7077 \
            --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1,org.mongodb.spark:mongo-spark-connector:10.0.5 \
            --conf spark.mongodb.input.uri="mongodb+srv://admin:sU9MgLmRNY8K5TAi@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority" \
            --conf spark.mongodb.output.uri="mongodb+srv://admin:sU9MgLmRNY8K5TAi@devcluster.eeupfll.mongodb.net/?retryWrites=true&w=majority" \
            /app/scripts/readStreamData.py