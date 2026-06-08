import json
import redis
from confluent_kafka import Consumer

#connection to redis.
r = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)

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
        
        print(f"Redis works, agent:ram_usage -> {ram_usage}%")

except KeyboardInterrupt:
    pass
finally:
    #shut down the connection of kafka.
    consumer.close()