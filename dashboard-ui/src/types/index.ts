export interface Location {
  location_id: number;
  location_name: string;
  address: string;
  city: string;
  state: string;
  zip_code: string;
  manager_name: string;
  phone: string;
  park_capacity: number;
  grooming_stations: number;
  boarding_kennels: number;
}

export interface DashboardData {
  dashboard_html: string;
  location_name: string;
  date: string;
}

export interface ApiResponse<T> {
  output: {
    data: T[];
    logs: string;
    llm_usage: any[];
    error: string | null;
  };
  execution_time_ms: number;
  status: string;
}

export interface ApiConfig {
  apiKey: string;
  ddnToken: string;
  baseUrl: string;
}
