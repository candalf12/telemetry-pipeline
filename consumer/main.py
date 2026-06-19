import os
import json
import redis
import psycopg2
import time
from confluent_kafka import Consumer

REDIS_HOST = os.environ.get('REDIS_HOST', 'redis')
REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

PG_HOST = os.environ.get('PG_HOST', 'db')
PG_PORT = os.environ.get('PG_PORT', '5432')
PG_USER = os.environ.get('PG_USER', 'sre_user')
PG_PASSWORD = os.environ.get('PG_PASSWORD', 'sre_password')
PG_DB = os.environ.get('PG_DB', 'telemetry_db')

KAFKA_BROKER = os.environ.get('KAFKA_BROKER', 'kafka:29092')

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

while True:
    try:
        db_conn = psycopg2.connect(
            host=PG_HOST,
            port=PG_PORT,
            database=PG_DB,
            user=PG_USER,
            password=PG_PASSWORD
        )
        cursor = db_conn.cursor()
        break
    except psycopg2.OperationalError as e:
        print(f"Postgres not ready yet. Error: {e}")
        time.sleep(2)

cursor.execute("""
    CREATE TABLE IF NOT EXISTS system_metrics (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ram_usage REAL NOT NULL
    );
""")
db_conn.commit()
print("PostgreSQL connection has been established.")

conf = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'sre-telemetry-group', 
    'auto.offset.reset': 'latest'      
}

consumer = Consumer(conf)
consumer.subscribe(['system_metrics'])

try:
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None: 
            continue
        if msg.error():
            print(f"Kafka error: {msg.error()}")
            continue

        raw_data = msg.value().decode('utf-8')
        data = json.loads(raw_data)
        ram_usage = data['ram_usage_percent']
        
        r.set('agent:ram_usage', ram_usage)
        cursor.execute(
            "INSERT INTO system_metrics (ram_usage) VALUES (%s);",
            (ram_usage,)
        )
        db_conn.commit()

        print(f"Redis is cached, postgres has been written to: {ram_usage}%")        

except KeyboardInterrupt:
    pass
finally:
    consumer.close()
    if 'db_conn' in locals():
        db_conn.close()