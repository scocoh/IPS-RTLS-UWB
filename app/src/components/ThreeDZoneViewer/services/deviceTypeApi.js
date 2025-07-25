/* Name: deviceTypeApi.js */
/* Version: 0.1.0 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: Device Type API service for fetching device types from ParcoRTLS FastAPI */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/services */
/* Role: Frontend Service */
/* Status: Active */
/* Dependent: TRUE */

// Centralized configuration
const getServerHost = () => window.location.hostname || 'localhost';
const API_BASE_URL = () => `http://${getServerHost()}:8000/api`;

/**
 * Device Type API service for interacting with ParcoRTLS device type endpoints
 */
export class DeviceTypeApi {
  /**
   * Fetch all available device types
   * @returns {Promise<Array>} Array of device type objects
   */
  static async getDeviceTypes() {
    try {
      console.log(`📋 Fetching device types...`);
      
      const response = await fetch(`${API_BASE_URL()}/list_device_types`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const deviceTypes = await response.json();
      console.log(`✅ Fetched ${deviceTypes.length} device types:`, 
        deviceTypes.map(dt => `${dt.i_typ_dev}: ${dt.x_dsc_dev}`));
      
      return deviceTypes;
    } catch (error) {
      console.error(`❌ Error fetching device types:`, error);
      throw error;
    }
  }

  /**
   * Get device type by ID
   * @param {number} deviceTypeId - Device type ID
   * @returns {Promise<Object|null>} Device type object or null if not found
   */
  static async getDeviceTypeById(deviceTypeId) {
    try {
      const deviceTypes = await this.getDeviceTypes();
      const deviceType = deviceTypes.find(dt => dt.i_typ_dev === deviceTypeId);
      
      if (!deviceType) {
        console.log(`📋 Device type not found: ${deviceTypeId}`);
        return null;
      }
      
      console.log(`✅ Found device type ${deviceTypeId}: ${deviceType.x_dsc_dev}`);
      return deviceType;
    } catch (error) {
      console.error(`❌ Error fetching device type ${deviceTypeId}:`, error);
      throw error;
    }
  }

  /**
   * Get device types by IDs
   * @param {Array<number>} deviceTypeIds - Array of device type IDs
   * @returns {Promise<Array>} Array of device type objects
   */
  static async getDeviceTypesByIds(deviceTypeIds) {
    if (!Array.isArray(deviceTypeIds) || deviceTypeIds.length === 0) {
      return [];
    }

    try {
      console.log(`📋 Fetching device types for IDs: [${deviceTypeIds.join(', ')}]`);
      
      const allDeviceTypes = await this.getDeviceTypes();
      const requestedTypes = allDeviceTypes.filter(dt => 
        deviceTypeIds.includes(dt.i_typ_dev)
      );
      
      const foundIds = requestedTypes.map(dt => dt.i_typ_dev);
      const missingIds = deviceTypeIds.filter(id => !foundIds.includes(id));
      
      if (missingIds.length > 0) {
        console.warn(`⚠️ Device types not found: [${missingIds.join(', ')}]`);
      }
      
      console.log(`✅ Found ${requestedTypes.length} device types out of ${deviceTypeIds.length} requested`);
      return requestedTypes;
    } catch (error) {
      console.error(`❌ Error fetching device types by IDs:`, error);
      throw error;
    }
  }

  /**
   * Check if device type exists
   * @param {number} deviceTypeId - Device type ID to check
   * @returns {Promise<boolean>} True if device type exists
   */
  static async deviceTypeExists(deviceTypeId) {
    try {
      const deviceType = await this.getDeviceTypeById(deviceTypeId);
      return deviceType !== null;
    } catch (error) {
      console.error(`❌ Error checking device type ${deviceTypeId}:`, error);
      return false;
    }
  }

  /**
   * Get commonly used device types for quick selection
   * @returns {Promise<Array>} Array of common device type objects
   */
  static async getCommonDeviceTypes() {
    try {
      const allTypes = await this.getDeviceTypes();
      
      // Define commonly used device type IDs
      const commonTypeIds = [1, 2, 4, 24, 27]; // Tag, Tag with Batt, Personnel, CASE Cart, AllTraq
      
      const commonTypes = allTypes.filter(dt => commonTypeIds.includes(dt.i_typ_dev));
      
      console.log(`✅ Found ${commonTypes.length} common device types`);
      return commonTypes;
    } catch (error) {
      console.error(`❌ Error fetching common device types:`, error);
      throw error;
    }
  }

  /**
   * Group device types by category for UI organization
   * @returns {Promise<Object>} Object with categorized device types
   */
  static async getCategorizedDeviceTypes() {
    try {
      const allTypes = await this.getDeviceTypes();
      
      const categories = {
        tracking: [], // Tags and tracking devices
        infrastructure: [], // Network equipment
        equipment: [], // Hospital/facility equipment
        other: [] // Everything else
      };

      allTypes.forEach(deviceType => {
        const typeId = deviceType.i_typ_dev;
        const description = deviceType.x_dsc_dev.toLowerCase();

        if ([1, 2, 4, 27, 901].includes(typeId) || description.includes('tag') || description.includes('badge')) {
          categories.tracking.push(deviceType);
        } else if ([6, 7, 8, 9, 10, 11, 18].includes(typeId) || description.includes('network') || description.includes('hub')) {
          categories.infrastructure.push(deviceType);
        } else if ([19, 20, 21, 22, 24, 25].includes(typeId) || description.includes('cart') || description.includes('rack')) {
          categories.equipment.push(deviceType);
        } else {
          categories.other.push(deviceType);
        }
      });

      console.log(`✅ Categorized device types:`, {
        tracking: categories.tracking.length,
        infrastructure: categories.infrastructure.length,
        equipment: categories.equipment.length,
        other: categories.other.length
      });

      return categories;
    } catch (error) {
      console.error(`❌ Error categorizing device types:`, error);
      throw error;
    }
  }
}

export default DeviceTypeApi;