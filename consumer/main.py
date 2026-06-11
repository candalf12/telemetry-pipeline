import json
import redis
import psycopg2
import time
from confluent_kafka import Consumer

#connection to redis.
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

while True:
    try:
        db_conn = psycopg2.connect(
            host="db",
            database="telemetry_db",
            user="sre_user",
            password="sre_password"
        )
        cursor = db_conn.cursor()
        break
    except psycopg2.OperationalError:
        print("Postgres not ready yet.")
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
#kafka's ports
conf = {
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'sre-telemetry-group', # consumer's name.
    'auto.offset.reset': 'latest'      # reading the mru value.
}

consumer = Consumer(conf)
consumer.subscribe(['system_metrics'])


try:
    while True:
        msg = consumer.poll(1.0)
        
        if msg is None: 
            continue
        if msg.error():
            print(f"Redis offline: {msg.error()}")
            continue

        raw_data = msg.value().decode('utf-8')
        # Jfrom json to phyton readable form.
        data = json.loads(raw_data)
        ram_usage = data['ram_usage_percent']
        
        # reads to Redis.
        # change the value continously.
        r.set('agent:ram_usage', ram_usage)
        cursor.execute(
            "INSERT INTO system_metrics (ram_usage) VALUES (%s);",
            (ram_usage,)
        )
        db_conn.commit()

        print(f" Redis is cached, postgres has been written to: {ram_usage}%")        
        print(f"Redis works, agent:ram_usage -> {ram_usage}%")

except KeyboardInterrupt:
    pass
finally:
    #shut down the connection of kafka.
    consumer.close()