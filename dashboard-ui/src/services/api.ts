import { ApiConfig, ApiResponse, Location, DashboardData } from '../types';

export class ApiService {
  constructor(private config: ApiConfig) {}

  private async makeRequest<T>(endpoint: string, data: any): Promise<ApiResponse<T>> {
    const response = await fetch(`${this.config.baseUrl}/${endpoint}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'authorization': `api-key ${this.config.apiKey}`,
      },
      body: JSON.stringify({
        input: [data],
        ddn_headers: {
          'x-hasura-ddn-token': this.config.ddnToken
        }
      })
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  async fetchLocations(): Promise<Location[]> {
    const response = await this.makeRequest<Location>('fetch_all_locations', {});
    
    if (response.output.error) {
      throw new Error(`API Error: ${response.output.error}`);
    }
    
    return response.output.data;
  }

  async fetchDashboard(locationId: number, date: string): Promise<DashboardData> {
    const response = await this.makeRequest<DashboardData>('visual_location_dashboard', {
      location_id: locationId,
      date: date
    });
    
    if (response.output.error) {
      throw new Error(`API Error: ${response.output.error}`);
    }
    
    return response.output.data[0];
  }
}
