import os
import requests
from dotenv import load_dotenv
from confluent_kafka.avro import AvroProducer
from confluent_kafka import avro

load_dotenv()

access_key = os.getenv('access_key')
if access_key is None:
    raise ValueError("Missing environment variable: 'access_key'")

url = "http://api.aviationstack.com/v1/flights"

# Define the query parameters
params = {
    'access_key': access_key
}

response = requests.get(url, params=params)
response.raise_for_status()  # Raise exception if the request failed
data = response.json()

# Define producer configuration
producer_config = {
    'bootstrap.servers': '172.23.0.5:9092',
    'schema.registry.url': 'http://localhost:8081'
}

# Load Avro schema from a file
value_schema = avro.load('flights-value.avsc')  # Update with your schema file path
key_schema = avro.load('key_schema.avsc')  # Update with your schema file path


# Create an AvroProducer
producer = AvroProducer(producer_config, default_key_schema=avro.load('key_schema.avsc'), default_value_schema=value_schema)

topic = 'flights'

# Iterate over each flight in the data
for flight in data['data']:
    # Generate a unique id for the flight
    flight_date = flight.get('flight_date', '') or ''
    flight_number = (flight.get('flight', {}) or {}).get('number', '') or ''
    departure_scheduled = (flight.get('departure', {}) or {}).get('scheduled', '') or ''

    flight_id = flight_date + '_' + flight_number + '_' + departure_scheduled
    flight['id'] = flight_id

    # Check if 'codeshared' field is None and if so, replace it with an empty dictionary
    if flight['flight'].get('codeshared') is None:
        flight['flight']['codeshared'] = {}

    # 'delay' is a field in 'departure', convert it to string if it exists
    if 'departure' in flight and 'delay' in flight['departure']:
        flight['departure']['delay'] = str(flight['departure']['delay']) if flight['departure']['delay'] is not None else None

    # Produce the message
    # Produce the message
    producer.produce(topic=topic, key=flight_id, value=flight)



producer.flush()
print('Data sent to Kafka')