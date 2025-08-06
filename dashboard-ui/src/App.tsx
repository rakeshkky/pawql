import React, { useState, useEffect } from 'react';
import { Heart, BarChart3, Search } from 'lucide-react';
import { LocationSelector } from './components/LocationSelector';
import { DateSelector } from './components/DateSelector';
import { DashboardRenderer } from './components/DashboardRenderer';
import { LoadingSpinner } from './components/LoadingSpinner';
import { ErrorMessage } from './components/ErrorMessage';
import { ApiService } from './services/api';
import { getApiConfig } from './config/env';
import { Location, DashboardData } from './types';

function App() {
  const [apiService, setApiService] = useState<ApiService | null>(null);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>(
    new Date().toISOString().split('T')[0]
  );
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [initError, setInitError] = useState<string | null>(null);

  // Initialize API service and load locations
  useEffect(() => {
    try {
      const config = getApiConfig();
      const service = new ApiService(config);
      setApiService(service);

      // Load locations
      setLoading(true);
      service.fetchLocations()
        .then(setLocations)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false));
    } catch (err) {
      setInitError(err instanceof Error ? err.message : 'Failed to initialize API');
    }
  }, []);

  const loadDashboard = async () => {
    if (!apiService || !selectedLocation) return;

    setLoading(true);
    setError(null);

    try {
      const data = await apiService.fetchDashboard(selectedLocation.location_id, selectedDate);
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setLoading(false);
    }
  };

  // Remove automatic loading - dashboard will only load when button is clicked

  if (initError) {
    return (
      <div className="min-h-screen flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <ErrorMessage
            message={initError}
            onRetry={() => window.location.reload()}
          />
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen p-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <header className="mb-8">
          <div className="flex items-center space-x-3 mb-2">
            <Heart className="w-8 h-8 text-blue-600" />
            <h1 className="text-3xl font-bold text-gray-900">PawQL Dashboard</h1>
          </div>
          <p className="text-gray-600">Monitor your pet care locations with real-time insights</p>
        </header>

        {/* Controls */}
        <div className="card mb-6">
          <div className="flex items-center space-x-3 mb-4">
            <BarChart3 className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-800">Dashboard Controls</h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <LocationSelector
              locations={locations}
              selectedLocation={selectedLocation}
              onLocationChange={setSelectedLocation}
              loading={loading}
            />
            <DateSelector
              selectedDate={selectedDate}
              onDateChange={setSelectedDate}
            />
          </div>

          <div className="mt-6 flex justify-center">
            <button
              onClick={loadDashboard}
              disabled={!selectedLocation || !selectedDate || loading}
              className="inline-flex items-center px-8 py-4 text-lg font-semibold text-white bg-gradient-to-r from-blue-600 to-blue-700 border border-transparent rounded-xl shadow-lg hover:from-blue-700 hover:to-blue-800 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed transition-all duration-200 transform hover:scale-105 disabled:hover:scale-100 hover:shadow-xl"
            >
              <Search className="w-6 h-6 mr-3" />
              {loading ? 'Loading Dashboard...' : 'Load Dashboard'}
            </button>
          </div>
        </div>

        {/* Dashboard Content */}
        {loading && (
          <div className="card">
            <LoadingSpinner message="Loading dashboard data..." />
          </div>
        )}

        {error && (
          <ErrorMessage
            message={error}
            onRetry={loadDashboard}
          />
        )}

        {dashboardData && !loading && !error && (
          <DashboardRenderer dashboardData={dashboardData} />
        )}

        {!dashboardData && !loading && !error && (
          <div className="card text-center py-12">
            <Heart className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {!selectedLocation ? 'Select a Location' : 'Ready to Load Dashboard'}
            </h3>
            <p className="text-gray-600">
              {!selectedLocation
                ? 'Choose a location and date, then click "Load Dashboard" to view insights'
                : 'Click the "Load Dashboard" button to fetch the latest data'
              }
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
