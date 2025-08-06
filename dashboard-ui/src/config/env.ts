import { ApiConfig } from '../types';

export function getApiConfig(): ApiConfig {
  const apiKey = import.meta.env.VITE_PROMPTQL_API_KEY;
  const ddnToken = import.meta.env.VITE_DDN_TOKEN;
  
  if (!apiKey) {
    throw new Error('VITE_PROMPTQL_API_KEY environment variable is required');
  }
  
  if (!ddnToken) {
    throw new Error('VITE_DDN_TOKEN environment variable is required');
  }
  
  return {
    apiKey,
    ddnToken,
    baseUrl: 'https://enabled-stork-1938.ddn.hasura.app/promptql/automations/v1'
  };
}
