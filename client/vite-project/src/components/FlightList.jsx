import React from 'react';
import { useQuery } from '@apollo/client';
import { gql } from '@apollo/client';
import { FaPlaneDeparture, FaPlaneArrival } from 'react-icons/fa';

// Define your GraphQL query
const GET_FLIGHTS_QUERY = gql`
  query {
    flights {
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
  
  function FlightList() {
    const { loading, error, data } = useQuery(GET_FLIGHTS_QUERY);
  
    if (loading) return <p>Loading...</p>;
    if (error) return <p>Error :(</p>;
  
    const randomFlights = Array.from({ length: 5 }, () => data.flights[Math.floor(Math.random() * data.flights.length)]);
  
    return (
      <div className="grid grid-cols-5 gap-4">
        {randomFlights.map((flight, index) => (
          <div key={index} className="p-4 bg-white rounded shadow-lg">
            <h2 className="text-2xl font-bold mb-2">{flight.airline.name}</h2>
            <p className="text-primary-orange">Flight Number: {flight.flightNumber}</p>
            <p>Status: <span className={getStatusColor(flight.flightStatus)}>{flight.flightStatus}</span></p>
            <div className="flex items-center mt-4">
              <FaPlaneDeparture className="mr-2 text-primary-orange" />
              <div>
                <p>Airport: {flight.departure.airport}</p>
                <p>Terminal: {flight.departure.terminal}</p>
                <p>Gate: {flight.departure.gate}</p>
              </div>
            </div>
  
            <div className="flex items-center mt-4">
              <FaPlaneArrival className="mr-2 text-primary-orange" />
              <div>
                <p>Airport: {flight.arrival.airport}</p>
                <p>Terminal: {flight.arrival.terminal}</p>
                <p>Gate: {flight.arrival.gate}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }
  
  export default FlightList;
