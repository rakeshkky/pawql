import React from 'react';
import { ChevronDown, MapPin } from 'lucide-react';
import { Location } from '../types';

interface LocationSelectorProps {
  locations: Location[];
  selectedLocation: Location | null;
  onLocationChange: (location: Location) => void;
  loading?: boolean;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({
  locations,
  selectedLocation,
  onLocationChange,
  loading = false
}) => {
  return (
    <div className="relative">
      <label className="block text-sm font-medium text-gray-700 mb-2">
        <MapPin className="inline w-4 h-4 mr-1" />
        Select Location
      </label>
      <div className="relative">
        <select
          value={selectedLocation?.location_id || ''}
          onChange={(e) => {
            const location = locations.find(l => l.location_id === parseInt(e.target.value));
            if (location) onLocationChange(location);
          }}
          disabled={loading}
          className="w-full appearance-none bg-white border border-gray-300 rounded-lg px-4 py-3 pr-10 text-gray-900 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-all duration-200"
        >
          <option value="">Choose a location...</option>
          {locations.map((location) => (
            <option key={location.location_id} value={location.location_id}>
              {location.location_name} - {location.city}, {location.state}
            </option>
          ))}
        </select>
        <ChevronDown className="absolute right-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400 pointer-events-none" />
      </div>
      {selectedLocation && (
        <div className="mt-2 p-3 bg-blue-50 rounded-lg text-sm text-blue-800">
          <div className="font-medium">{selectedLocation.location_name}</div>
          <div>{selectedLocation.address}, {selectedLocation.city}, {selectedLocation.state} {selectedLocation.zip_code}</div>
          <div>Manager: {selectedLocation.manager_name} • Phone: {selectedLocation.phone}</div>
        </div>
      )}
    </div>
  );
};
