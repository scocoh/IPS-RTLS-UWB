/* Name: deviceApi.js */
/* Version: 0.1.0 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: Device API service for fetching devices from ParcoRTLS FastAPI */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/services */
/* Role: Frontend Service */
/* Status: Active */
/* Dependent: TRUE */

// Centralized configuration
const getServerHost = () => window.location.hostname || 'localhost';
const API_BASE_URL = () => `http://${getServerHost()}:8000/api`;

/**
 * Device API service for interacting with ParcoRTLS device endpoints
 */
export class DeviceApi {
  /**
   * Fetch devices by device type ID
   * @param {number} deviceType - Device type ID (e.g., 27 for AllTraq)
   * @returns {Promise<Array>} Array of device objects
   */
  static async getDevicesByType(deviceType) {
    try {
      console.log(`📱 Fetching devices for type ${deviceType}...`);
      
      const response = await fetch(`${API_BASE_URL()}/get_device_by_type/${deviceType}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log(`📱 No devices found for type ${deviceType}`);
          return [];
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const devices = await response.json();
      console.log(`✅ Fetched ${devices.length} devices for type ${deviceType}`);
      
      return devices;
    } catch (error) {
      console.error(`❌ Error fetching devices for type ${deviceType}:`, error);
      throw error;
    }
  }

  /**
   * Fetch devices for multiple device types
   * @param {Array<number>} deviceTypes - Array of device type IDs
   * @returns {Promise<Array>} Array of device objects with type metadata
   */
  static async getDevicesByTypes(deviceTypes) {
    if (!Array.isArray(deviceTypes) || deviceTypes.length === 0) {
      console.log(`📱 No device types specified, returning empty array`);
      return [];
    }

    console.log(`🔍 Fetching devices for types: [${deviceTypes.join(', ')}]`);
    
    try {
      const results = await Promise.allSettled(
        deviceTypes.map(async (deviceType) => {
          const devices = await this.getDevicesByType(deviceType);
          return devices.map(device => ({
            ...device,
            deviceTypeId: deviceType
          }));
        })
      );

      const allDevices = [];
      const errors = [];

      results.forEach((result, index) => {
        if (result.status === 'fulfilled') {
          allDevices.push(...result.value);
        } else {
          errors.push({
            deviceType: deviceTypes[index],
            error: result.reason
          });
        }
      });

      if (errors.length > 0) {
        console.warn(`⚠️ Some device type fetches failed:`, errors);
      }

      console.log(`✅ Successfully fetched ${allDevices.length} devices across ${deviceTypes.length} types`);
      return allDevices;
      
    } catch (error) {
      console.error(`❌ Error in getDevicesByTypes:`, error);
      throw error;
    }
  }

  /**
   * Fetch a specific device by ID
   * @param {string} deviceId - Device ID
   * @returns {Promise<Object|null>} Device object or null if not found
   */
  static async getDeviceById(deviceId) {
    try {
      console.log(`🔍 Fetching device by ID: ${deviceId}`);
      
      const response = await fetch(`${API_BASE_URL()}/get_device_by_id/${deviceId}`);
      
      if (!response.ok) {
        if (response.status === 404) {
          console.log(`📱 Device not found: ${deviceId}`);
          return null;
        }
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const device = await response.json();
      console.log(`✅ Fetched device: ${deviceId}`);
      
      return device;
    } catch (error) {
      console.error(`❌ Error fetching device ${deviceId}:`, error);
      throw error;
    }
  }

  /**
   * Check if a device ID exists
   * @param {string} deviceId - Device ID to check
   * @returns {Promise<boolean>} True if device exists
   */
  static async checkDeviceExists(deviceId) {
    try {
      console.log(`🔍 Checking if device exists: ${deviceId}`);
      
      const response = await fetch(`${API_BASE_URL()}/check_device_id/${deviceId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const result = await response.json();
      const exists = result.exists === true;
      
      console.log(`✅ Device ${deviceId} exists: ${exists}`);
      return exists;
      
    } catch (error) {
      console.error(`❌ Error checking device ${deviceId}:`, error);
      return false;
    }
  }

  /**
   * Get all devices (no filtering)
   * @returns {Promise<Array>} Array of all device objects
   */
  static async getAllDevices() {
    try {
      console.log(`📱 Fetching all devices...`);
      
      const response = await fetch(`${API_BASE_URL()}/get_all_devices`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const devices = await response.json();
      console.log(`✅ Fetched ${devices.length} total devices`);
      
      return devices;
    } catch (error) {
      console.error(`❌ Error fetching all devices:`, error);
      throw error;
    }
  }
}

export default DeviceApi;