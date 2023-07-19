from flask import Flask
from flask_graphql import GraphQLView
from graphene import ObjectType, String, DateTime, Field, Schema, List
import psycopg2
from psycopg2 import extras
import datetime

class Airline(ObjectType):
    id = String()
    name = String()
    iata = String()
    icao = String()

class Airport(ObjectType):
    airport = String()
    timezone = String()
    iata = String()
    icao = String()
    terminal = String()
    gate = String()

class Flight(ObjectType):
    id = String()
    flight_date = DateTime()
    flight_status = String()
    departure = Field(Airport)
    arrival = Field(Airport)
    airline = Field(Airline)
    flight_number = String()

class Query(ObjectType):
    flight = Field(Flight, airlineName=String(required=True), flightNumber=String(required=True))
    flights = List(Flight)

    def resolve_flight(root, info, airlineName, flightNumber):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='mysecretpassword',
            host='localhost',
            port='5433'
        )

        # Create a cursor object
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Execute a query to get the flight details
        cur.execute('''
            SELECT f.*, a.name AS airline_name, a.iata AS airline_iata, a.icao AS airline_icao 
            FROM flights f
            JOIN airlines a ON f.airline_id = a.id 
            WHERE a.name = %s AND f.flight_number = %s
        ''', (airlineName, flightNumber))

        # Fetch the result
        result = cur.fetchone()

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Check if a result was found
        if result is None:
            return None

        # Return the result as a Flight object
        return Flight(
            id=result['id'],
            flight_date=result['flight_date'],
            flight_status=result['flight_status'],
            departure=Airport(
                airport=result['departure_airport'],
                timezone=result['departure_timezone'],
                iata=result['departure_iata'],
                icao=result['departure_icao'],
                terminal=result['departure_terminal'],
                gate=result['departure_gate']
            ),
            arrival=Airport(
                airport=result['arrival_airport'],
                timezone=result['arrival_timezone'],
                iata=result['arrival_iata'],
                icao=result['arrival_icao'],
                terminal=result['arrival_terminal'],
                gate=result['arrival_gate']
            ),
            airline=Airline(
                id=result['airline_id'],
                name=result['airline_name'],
                iata=result['airline_iata'],
                icao=result['airline_icao']
            ),
            flight_number=result['flight_number']
        )

    def resolve_flights(root, info):
        # Connect to the PostgreSQL database
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            password='mysecretpassword',
            host='localhost',
            port='5433'
        )

        # Create a cursor object
        cur = conn.cursor(cursor_factory=extras.RealDictCursor)

        # Execute a query to get all flights
        cur.execute('''
            SELECT f.*, a.name AS airline_name, a.iata AS airline_iata, a.icao AS airline_icao 
            FROM flights f
            JOIN airlines a ON f.airline_id = a.id 
        ''')

        # Fetch all results
        results = cur.fetchall()

        # Close the cursor and connection
        cur.close()
        conn.close()

        # Return the results as a list of Flight objects
        return [
            Flight(
                id=result['id'],
                flight_date=result['flight_date'],
                flight_status=result['flight_status'],
                departure=Airport(
                    airport=result['departure_airport'],
                    timezone=result['departure_timezone'],
                    iata=result['departure_iata'],
                    icao=result['departure_icao'],
                    terminal=result['departure_terminal'],
                    gate=result['departure_gate']
                ),
                arrival=Airport(
                    airport=result['arrival_airport'],
                    timezone=result['arrival_timezone'],
                    iata=result['arrival_iata'],
                    icao=result['arrival_icao'],
                    terminal=result['arrival_terminal'],
                    gate=result['arrival_gate']
                ),
                airline=Airline(
                    id=result['airline_id'],
                    name=result['airline_name'],
                    iata=result['airline_iata'],
                    icao=result['airline_icao']
                ),
                flight_number=result['flight_number']
            ) for result in results
        ]


view_func = GraphQLView.as_view('graphql', schema=Schema(query=Query), graphiql=True)
from flask import Flask
from flask_graphql import GraphQLView
from flask_cors import CORS  # Import CORS


app = Flask(__name__)
CORS(app)  # Enable CORS on the Flask app
app.add_url_rule('/graphql', view_func=view_func)

if __name__ == '__main__':
    app.run()
