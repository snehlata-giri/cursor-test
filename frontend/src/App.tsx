import React from 'react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import VendorDashboard from './components/VendorDashboard';
import './App.css';

const queryClient = new QueryClient();

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <div className="App">
        <VendorDashboard />
      </div>
    </QueryClientProvider>
  );
}

export default App;