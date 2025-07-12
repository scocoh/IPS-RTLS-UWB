/* Name: dashboardApi.js */
/* Version: 0.1.1 */
/* Created: 250711 */
/* Modified: 250712 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for dashboard operations with dynamic device categories */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/DashboardDemo/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// Import centralized configuration
import { getApiUrl } from '../../../config';

const BASE_URL = getApiUrl('');
console.log('Dashboard BASE_URL:', BASE_URL); // Debug line

class DashboardApiService {
  async makeRequest(endpoint, options = {}) {
    try {
      // Remove leading slash from endpoint to avoid double slash
      const cleanEndpoint = endpoint.startsWith('/') ? endpoint.slice(1) : endpoint;
      // Remove trailing slash from BASE_URL to avoid double slash
      const cleanBaseUrl = BASE_URL.endsWith('/') ? BASE_URL.slice(0, -1) : BASE_URL;
      const url = `${cleanBaseUrl}/${cleanEndpoint}`;
      
      console.log('Dashboard API calling:', url); // Debug line
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`Dashboard API error for ${endpoint}:`, error);
      throw error;
    }
  }

  // Get all dashboard metrics
  async getMetrics() {
    return this.makeRequest('/dashboard/metrics');
  }

  // Get dashboard locations
  async getLocations() {
    return this.makeRequest('/dashboard/locations');
  }

  // Get device categories for a customer
  async getDeviceCategories(customerId = 1) {
    return this.makeRequest(`/dashboard/device_categories/${customerId}`);
  }

  // Get customer configuration
  async getCustomerConfig(customerId = 1) {
    return this.makeRequest(`/dashboard/customer_config/${customerId}`);
  }

  // Get activity feed
  async getActivity(limit = 50) {
    return this.makeRequest(`/dashboard/activity?limit=${limit}`);
  }

  // Get autoclave data
  async getAutoclave() {
    return this.makeRequest('/dashboard/autoclave');
  }

  // Get alert summary
  async getAlerts() {
    return this.makeRequest('/dashboard/alerts');
  }

  // Get sensor readings
  async getSensors() {
    return this.makeRequest('/dashboard/sensors');
  }

  // Get complete dashboard overview for a customer
  async getOverview(customerId = 1) {
    return this.makeRequest(`/dashboard/overview/${customerId}`);
  }

  // Update a specific metric
  async updateMetric(metricName, value) {
    return this.makeRequest(`/dashboard/metrics/${metricName}`, {
      method: 'POST',
      body: JSON.stringify({ value }),
    });
  }

  // Add activity item
  async addActivity(activityData) {
    return this.makeRequest('/dashboard/activity', {
      method: 'POST',
      body: JSON.stringify(activityData),
    });
  }
}

// Export singleton instance
export const dashboardApi = new DashboardApiService();