// File: /home/parcoadmin/parco_fastapi/app/src/components/DashboardManager/services/dashboardManagerApi.js
/* Name: dashboardManagerApi.js */
/* Version: 0.1.1 */
/* Created: 250713 */
/* Modified: 250713 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for Dashboard Manager operations - Added data source discovery and management methods */

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://192.168.210.226:8000';

class DashboardManagerAPI {
  constructor() {
    this.baseURL = `${API_BASE_URL}/api`;
  }

  async makeRequest(endpoint, options = {}) {
    try {
      const url = `${this.baseURL}${endpoint}`;
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Manager Status and Control
  async getManagerStatus() {
    return this.makeRequest('/dashboard-manager/status');
  }

  async startManager() {
    return this.makeRequest('/dashboard-manager/start', {
      method: 'POST',
    });
  }

  async stopManager() {
    return this.makeRequest('/dashboard-manager/stop', {
      method: 'POST',
    });
  }

  async restartManager() {
    return this.makeRequest('/dashboard-manager/restart', {
      method: 'POST',
    });
  }

  async getManagerHealth() {
    return this.makeRequest('/dashboard-manager/health');
  }

  // Customer Management
  async getCustomerStats() {
    return this.makeRequest('/dashboard-manager/customers');
  }

  async getCustomerConfig(customerId) {
    return this.makeRequest(`/dashboard-manager/customers/${customerId}`);
  }

  async updateCustomerConfig(customerId, config) {
    return this.makeRequest(`/dashboard-manager/customers/${customerId}`, {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  async addCustomer(customerData) {
    return this.makeRequest('/dashboard-manager/customers', {
      method: 'POST',
      body: JSON.stringify(customerData),
    });
  }

  async removeCustomer(customerId) {
    return this.makeRequest(`/dashboard-manager/customers/${customerId}`, {
      method: 'DELETE',
    });
  }

  // Message and Performance Statistics
  async getMessageStats() {
    return this.makeRequest('/dashboard-manager/messages/stats');
  }

  async getPerformanceMetrics() {
    return this.makeRequest('/dashboard-manager/performance');
  }

  async getMessageFlow() {
    return this.makeRequest('/dashboard-manager/messages/flow');
  }

  // Client Connections
  async getClientConnections() {
    return this.makeRequest('/dashboard-manager/clients');
  }

  async getClientDetails(clientId) {
    return this.makeRequest(`/dashboard-manager/clients/${clientId}`);
  }

  async disconnectClient(clientId) {
    return this.makeRequest(`/dashboard-manager/clients/${clientId}/disconnect`, {
      method: 'POST',
    });
  }

  // Dashboard WebSocket Status
  async getDashboardWebSocketStatus() {
    return this.makeRequest('/dashboard-manager/websocket/status');
  }

  async getDashboardWebSocketClients() {
    return this.makeRequest('/dashboard-manager/websocket/clients');
  }

  // Configuration Management
  async getRouterConfiguration() {
    return this.makeRequest('/dashboard-manager/router/config');
  }

  async updateRouterConfiguration(config) {
    return this.makeRequest('/dashboard-manager/router/config', {
      method: 'PUT',
      body: JSON.stringify(config),
    });
  }

  async reloadRouterConfiguration() {
    return this.makeRequest('/dashboard-manager/router/reload', {
      method: 'POST',
    });
  }

  // Debugging and Logs
  async getManagerLogs(lines = 100) {
    return this.makeRequest(`/dashboard-manager/logs?lines=${lines}`);
  }

  async getDebugInfo() {
    return this.makeRequest('/dashboard-manager/debug');
  }

  async clearMessageQueue() {
    return this.makeRequest('/dashboard-manager/queue/clear', {
      method: 'POST',
    });
  }

  // Test Methods
  async testDashboardConnection() {
    return this.makeRequest('/dashboard-manager/test/connection');
  }

  async sendTestMessage(message) {
    return this.makeRequest('/dashboard-manager/test/message', {
      method: 'POST',
      body: JSON.stringify(message),
    });
  }

  // Database Operations
  async getDashboardTables() {
    return this.makeRequest('/dashboard-manager/database/tables');
  }

  async createDashboardTables() {
    return this.makeRequest('/dashboard-manager/database/tables/create', {
      method: 'POST',
    });
  }

  async initializeDefaultData() {
    return this.makeRequest('/dashboard-manager/database/initialize', {
      method: 'POST',
    });
  }

  // Data Source Management
  async discoverDataSources() {
    return this.makeRequest('/dashboard-manager/data-sources/discover');
  }

  async getDataSourceStatus(sourceId) {
    return this.makeRequest(`/dashboard-manager/data-sources/${sourceId}/status`);
  }

  async checkDataSourceHealth(sourceId) {
    return this.makeRequest(`/dashboard-manager/data-sources/${sourceId}/health`);
  }

  async startDataSource(sourceId) {
    return this.makeRequest(`/dashboard-manager/data-sources/${sourceId}/start`, {
      method: 'POST'
    });
  }

  async stopDataSource(sourceId) {
    return this.makeRequest(`/dashboard-manager/data-sources/${sourceId}/stop`, {
      method: 'POST'
    });
  }

  async restartDataSource(sourceId) {
    return this.makeRequest(`/dashboard-manager/data-sources/${sourceId}/restart`, {
      method: 'POST'
    });
  }
}

// Create and export singleton instance
const dashboardManagerApi = new DashboardManagerAPI();
export default dashboardManagerApi;