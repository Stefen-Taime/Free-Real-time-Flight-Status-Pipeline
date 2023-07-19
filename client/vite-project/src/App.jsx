import React from 'react';
import { ApolloProvider } from '@apollo/client';
import client from './apollo';
import FlightList from './components/FlightList';
import FlightSearch from './components/FlightSearch';

function App() {
  return (
    <ApolloProvider client={client}>
      <div className="App">
        <div className="mb-4">
          <FlightList />
        </div>
        <div>
          <FlightSearch />
        </div>
      </div>
    </ApolloProvider>
  );
}

export default App;
