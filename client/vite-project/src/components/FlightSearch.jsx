import React, { useState } from 'react';
import { useQuery, gql } from '@apollo/client';
import { FaPlaneDeparture, FaPlaneArrival } from 'react-icons/fa';

// Define your GraphQL query
const GET_FLIGHT_QUERY = gql`
  query GetFlight($airlineName: String!, $flightNumber: String!) {
    flight(airlineName: $airlineName, flightNumber: $flightNumber) {
      id
      flightDate
      flightStatus
      departure {
        airport
        timezone
        iata
        icao
        terminal
        gate
      }
      arrival {
        airport
        timezone
        iata
        icao
        terminal
        gate
      }
      airline {
        id
        name
        iata
        icao
      }
      flightNumber
    }
  }
`;

function getStatusColor(status) {
  switch (status) {
    case 'scheduled':
      return 'text-green-500';
    case 'active':
      return 'text-blue-500';
    case 'landed':
      return 'text-gray-500';
    case 'cancelled':
      return 'text-red-500';
    case 'incident':
      return 'text-yellow-500';
    case 'diverted':
      return 'text-orange-500';
    default:
      return 'text-black';
  }
}

function FlightSearch() {
  const [airlineName, setAirlineName] = useState("");
  const [flightNumber, setFlightNumber] = useState("");

  const { loading, error, data } = useQuery(GET_FLIGHT_QUERY, {
    variables: { airlineName, flightNumber },
    skip: !airlineName || !flightNumber,
  });

  const handleSubmit = (event) => {
    event.preventDefault();
  };

  if (loading) return <p>Loading...</p>;
  if (error) return <p>Error :(</p>;

  return (
    <div className="flex flex-col items-center mt-8">
      <form onSubmit={handleSubmit} className="mb-4 flex flex-col items-center space-y-2">
        <input
          value={airlineName}
          onChange={(e) => setAirlineName(e.target.value)}
          type="text"
          placeholder="Airline name"
          className="p-1 border border-gray-400"
        />
        <input
          value={flightNumber}
          onChange={(e) => setFlightNumber(e.target.value)}
          type="text"
          placeholder="Flight number"
          className="p-1 border border-gray-400"
        />
        <button type="submit" className="p-1 bg-primary-orange text-white">Search</button>
      </form>

      {data && data.flight && (
        <div className="p-4 bg-white rounded shadow-lg">
          <h2 className="text-2xl font-bold mb-2">{data.flight.airline.name}</h2>
          <p className="text-primary-orange">Flight Number: {data.flight.flightNumber}</p>
          <p className={getStatusColor(data.flight.flightStatus)}>Status: {data.flight.flightStatus}</p>
          <div className="flex items-center mt-4">
            <FaPlaneDeparture className="mr-2 text-primary-orange" />
            <div>
              <p>Airport: {data.flight.departure.airport}</p>
              <p>Terminal: {data.flight.departure.terminal}</p>
              <p>Gate: {data.flight.departure.gate}</p>
            </div>
          </div>

          <div className="flex items-center mt-4">
            <FaPlaneArrival className="mr-2 text-primary-orange" />
            <div>
              <p>Airport: {data.flight.arrival.airport}</p>
              <p>Terminal: {data.flight.arrival.terminal}</p>
              <p>Gate: {data.flight.arrival.gate}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default FlightSearch;
