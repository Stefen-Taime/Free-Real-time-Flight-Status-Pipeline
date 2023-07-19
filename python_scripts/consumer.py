import psycopg2
import psycopg2.extras
import json
from confluent_kafka import KafkaError
from confluent_kafka.avro import AvroConsumer
from confluent_kafka.avro.serializer import SerializerError

# Define consumer configuration
consumer_config = {
    'bootstrap.servers': '172.23.0.5:9092',
    'group.id': 'flights-group',
    'auto.offset.reset': 'earliest',
    'schema.registry.url': 'http://localhost:8081'
}

# Create an AvroConsumer
consumer = AvroConsumer(consumer_config)

# Subscribe to the 'flights' topic
consumer.subscribe(['flights'])

# Connect to the PostgreSQL database
conn = psycopg2.connect("dbname=postgres user=postgres password=mysecretpassword host=localhost port=5433")

# Create a cursor object
cur = conn.cursor()

try:
    while True:
        # Poll for messages
        msg = consumer.poll(1.0)

        if msg is None:
            continue

        if msg.error():
            if msg.error().code() == KafkaError._PARTITION_EOF:
                continue
            else:
                print(msg.error())
                break

        # Extract the key and value
        key = msg.key()
        value = msg.value()

        # Insert the airline into the airlines table
        airline_id = value['airline']['iata']
        cur.execute(
            "INSERT INTO airlines (id, name, iata, icao) VALUES (%s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
            (airline_id, value['airline']['name'], value['airline']['iata'], value['airline']['icao'])
        )

        # Insert the codeshared flight into the flights_codeshared table if it exists
        codeshared_flight_id = None
        if value['flight']['codeshared'] is not None and 'flight_iata' in value['flight']['codeshared'] and value['flight']['codeshared']['flight_iata'] is not None:
            codeshared_flight_id = value['flight']['codeshared']['flight_iata']
            data = (codeshared_flight_id, value['flight']['codeshared']['airline_iata'], value['flight']['codeshared']['flight_number'], value['flight']['codeshared']['flight_iata'], value['flight']['codeshared']['flight_icao'])
            print(f"Inserting into flights_codeshared: {data}")
            cur.execute(
                "INSERT INTO flights_codeshared (id, airline_id, flight_number, flight_iata, flight_icao) VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) DO NOTHING",
                data
            )

        # Insert the flight into the flights table
        data = (key, value['flight_date'], value['flight_status'], value['departure']['airport'], value['departure']['timezone'], value['departure']['iata'], value['departure']['icao'], value['departure']['terminal'], value['departure']['gate'], value['departure']['delay'], value['departure']['scheduled'], value['departure']['estimated'], value['departure']['actual'], value['departure']['estimated_runway'], value['departure']['actual_runway'], value['arrival']['airport'], value['arrival']['timezone'], value['arrival']['iata'], value['arrival']['icao'], value['arrival']['terminal'], value['arrival']['gate'], value['arrival']['baggage'], value['arrival']['delay'], value['arrival']['scheduled'], value['arrival']['estimated'], value['arrival']['actual'], value['arrival']['estimated_runway'], value['arrival']['actual_runway'], airline_id, value['flight']['number'], codeshared_flight_id)
        print(f"Inserting into flights: {data}, length: {len(data)}")
        cur.execute(
            "INSERT INTO flights (id, flight_date, flight_status, departure_airport, departure_timezone, departure_iata, departure_icao, departure_terminal, departure_gate, departure_delay, departure_scheduled, departure_estimated, departure_actual, departure_estimated_runway, departure_actual_runway, arrival_airport, arrival_timezone, arrival_iata, arrival_icao, arrival_terminal, arrival_gate, arrival_baggage, arrival_delay, arrival_scheduled, arrival_estimated, arrival_actual, arrival_estimated_runway, arrival_actual_runway, airline_id, flight_number, codeshared_flight_id) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (id) DO UPDATE SET flight_status = excluded.flight_status, departure_delay = excluded.departure_delay, departure_estimated = excluded.departure_estimated, departure_actual = excluded.departure_actual, departure_estimated_runway = excluded.departure_estimated_runway, departure_actual_runway = excluded.departure_actual_runway, arrival_delay = excluded.arrival_delay, arrival_estimated = excluded.arrival_estimated, arrival_actual = excluded.arrival_actual, arrival_estimated_runway = excluded.arrival_estimated_runway, arrival_actual_runway = excluded.arrival_actual_runway",
            data
        )
        conn.commit()

except SerializerError as e:
    print(f"Message deserialization failed: {e}")
    exit(1)

except KeyboardInterrupt:
    pass

finally:
    # Close down consumer to commit final offsets.
    consumer.close()
    # Close the PostgreSQL connection
    cur.close()
    conn.close()
