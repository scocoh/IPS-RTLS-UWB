/* Name: config.js */
/* Version: 0.1.0 */
/* Created: 250703 */
/* Modified: 250703 */
/* Creator: AI Assistant */
/* Modified By: AI Assistant */
/* Description: Centralized configuration for ParcoRTLS frontend */
/* Location: /home/parcoadmin/parco_fastapi/app/src/config.js */
/* Role: Frontend Configuration */
/* Status: Active */
/* Dependent: FALSE */

// Default API configuration
const DEFAULT_API_HOST = window.location.hostname || 'localhost';
const DEFAULT_API_PORT = '8000';
const DEFAULT_WS_PORT = '8002';

// Allow override from environment variables (if using process.env in build)
const API_HOST = process.env.REACT_APP_API_HOST || DEFAULT_API_HOST;
const API_PORT = process.env.REACT_APP_API_PORT || DEFAULT_API_PORT;
const WS_PORT = process.env.REACT_APP_WS_PORT || DEFAULT_WS_PORT;

// Construct URLs
const API_BASE_URL = `http://${API_HOST}:${API_PORT}`;
const WS_BASE_URL = `ws://${API_HOST}:${WS_PORT}`;

// Export configuration
export const config = {
  // API endpoints
  API_BASE_URL,
  API_URL: API_BASE_URL,
  
  // WebSocket endpoints
  WS_BASE_URL,
  WS_REALTIME_URL: `${WS_BASE_URL}/ws/realtime`,
  WS_CONTROL_URL: `ws://${API_HOST}:8001`,
  WS_HISTORICAL_URL: `ws://${API_HOST}:8003`,
  WS_AVERAGED_URL: `ws://${API_HOST}:8004`,
  
  // Individual service URLs (for backward compatibility)
  DEVICE_API_URL: `${API_BASE_URL}/api`,
  ENTITY_API_URL: `${API_BASE_URL}/api`,
  ZONE_API_URL: `${API_BASE_URL}/api`,
  MAP_API_URL: `${API_BASE_URL}/api`,
  TRIGGER_API_URL: `${API_BASE_URL}/api`,
  ZONEVIEWER_API_URL: `${API_BASE_URL}/zoneviewer`,
  ZONEBUILDER_API_URL: `${API_BASE_URL}/zonebuilder`,
  
  // MQTT configuration
  MQTT_HOST: API_HOST,
  MQTT_PORT: 1883,
  
  // Other configuration
  DEFAULT_ZONE_ID: 1,
  DEFAULT_MAP_ID: 24,
  HEARTBEAT_INTERVAL: 30000, // 30 seconds
  
  // Feature flags
  ENABLE_WEBSOCKET_LOGGING: true,
  ENABLE_DEBUG_MODE: false,
};

// Helper function to get full API URL
export const getApiUrl = (endpoint) => {
  if (endpoint.startsWith('http://') || endpoint.startsWith('https://')) {
    return endpoint;
  }
  if (endpoint.startsWith('/')) {
    return `${config.API_BASE_URL}${endpoint}`;
  }
  return `${config.API_BASE_URL}/${endpoint}`;
};

// Helper function to get WebSocket URL
export const getWsUrl = (endpoint) => {
  if (endpoint.startsWith('ws://') || endpoint.startsWith('wss://')) {
    return endpoint;
  }
  if (endpoint.startsWith('/')) {
    return `${config.WS_BASE_URL}${endpoint}`;
  }
  return `${config.WS_BASE_URL}/${endpoint}`;
};

// Export for backward compatibility
export default config;