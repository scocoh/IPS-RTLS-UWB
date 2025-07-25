/* Name: deviceSubscriptionBuilder.js */
/* Version: 0.2.1 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: WebSocket subscription builder for real-time device tracking - MULTI-ZONE SUPPORT */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend Utility */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.2.0: MULTI-ZONE SUPPORT - Added dynamic zone hierarchy discovery to subscribe to parent + child zones */

import { ALLTRAQ_ZONE_ID, sortDevicesByPriority } from './deviceCategorization.js';
import { config } from '../../../config';

// Configuration constants
const MAX_DEVICES_PER_SUBSCRIPTION = 50; // Limit to avoid message size issues
const MAX_SUBSCRIPTION_ATTEMPTS = 15; // Increased to accommodate multiple zones
const ZONE_CACHE_TIMEOUT = 300000; // 5 minutes cache for zone hierarchy

/**
 * Build WebSocket subscriptions for real-time device tracking with multi-zone support
 */
export class DeviceSubscriptionBuilder {
  
  static zoneCache = new Map();
  
  /**
   * Get zone hierarchy from cache or API
   * @param {number} campusId - Campus zone ID
   * @returns {Promise<Array>} Array of zone IDs to subscribe to
   */
  static async getZoneHierarchy(campusId) {
    const cacheKey = `zones_${campusId}`;
    const cached = this.zoneCache.get(cacheKey);
    
    // Check cache first
    if (cached && (Date.now() - cached.timestamp) < ZONE_CACHE_TIMEOUT) {
      console.log(`📋 Using cached zone hierarchy for campus ${campusId}`);
      return cached.zoneIds;
    }
    
    try {
      console.log(`🔍 Fetching zone hierarchy for campus ${campusId}...`);
      
      // Fetch zones for the campus
      const response = await fetch(`${config.ZONEVIEWER_API_URL}/get_all_zones_for_campus/${campusId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      const zones = data.zones || [];
      
      // Extract all zone IDs from the hierarchy
      const zoneIds = [];
      const extractZoneIds = (zoneArray) => {
        zoneArray.forEach(zone => {
          zoneIds.push(zone.zone_id);
          if (zone.children && zone.children.length > 0) {
            extractZoneIds(zone.children);
          }
        });
      };
      
      extractZoneIds(zones);
      
      // Always include the parent campus zone
      if (!zoneIds.includes(campusId)) {
        zoneIds.unshift(campusId);
      }
      
      // Cache the result
      this.zoneCache.set(cacheKey, {
        zoneIds: zoneIds,
        timestamp: Date.now()
      });
      
      console.log(`✅ Found ${zoneIds.length} zones for campus ${campusId}: [${zoneIds.join(', ')}]`);
      return zoneIds;
      
    } catch (error) {
      console.error(`❌ Error fetching zone hierarchy for campus ${campusId}:`, error);
      
      // Fallback to just the campus ID and known AllTraq zone
      const fallbackZones = [campusId];
      if (campusId !== ALLTRAQ_ZONE_ID) {
        fallbackZones.push(ALLTRAQ_ZONE_ID);
      }
      
      console.log(`🔄 Using fallback zones: [${fallbackZones.join(', ')}]`);
      return fallbackZones;
    }
  }
  
  /**
   * Generate comprehensive device subscriptions with multi-zone support
   * @param {Object} options - Subscription options
   * @param {Array} options.devices - Array of device objects
   * @param {number} options.selectedCampusId - Selected campus zone ID
   * @param {boolean} options.enableAlltraqFiltering - Enable AllTraq zone filtering
   * @param {boolean} options.includeWildcardSubscriptions - Include wildcard subscriptions (DISABLED - server bug)
   * @returns {Promise<Array>} Array of subscription objects
   */
  static async generateDeviceSubscriptions({
    devices = [],
    selectedCampusId = null,
    enableAlltraqFiltering = true,
    includeWildcardSubscriptions = false // DISABLED due to server wildcard bug
  }) {
    console.log(`📡 Building multi-zone subscriptions for ${devices.length} devices, campus: ${selectedCampusId}`);
    
    if (!selectedCampusId) {
      console.warn(`⚠️ No campus selected - using fallback subscriptions`);
      return this.buildFallbackSubscriptions(null);
    }
    
    const subscriptions = [];
    
    // Get all zones to subscribe to (parent + children)
    const zoneIds = await this.getZoneHierarchy(selectedCampusId);
    
    console.log(`📡 Creating subscriptions for ${zoneIds.length} zones: [${zoneIds.join(', ')}]`);
    
    // Create device-specific subscriptions for each zone
    if (devices.length > 0) {
      const sortedDevices = sortDevicesByPriority(devices);
      const deviceChunks = this._chunkDevices(sortedDevices, MAX_DEVICES_PER_SUBSCRIPTION);
      
      // Create subscriptions for each zone
      zoneIds.forEach((zoneId, zoneIndex) => {
        deviceChunks.forEach((chunk, chunkIndex) => {
          const deviceParams = chunk.map(device => ({
            id: device.x_id_dev,
            data: "true"
          }));
          
          const subscription = {
            type: "request",
            request: "BeginStream",
            reqid: `threeDZoneViewer_zone${zoneId}_chunk${chunkIndex + 1}`,
            params: deviceParams,
            zone_id: zoneId,
            description: `Zone ${zoneId} devices chunk ${chunkIndex + 1}: ${chunk.length} devices`
          };
          
          subscriptions.push(subscription);
          console.log(`📡 Created subscription for zone ${zoneId}, chunk ${chunkIndex + 1}: ${chunk.length} devices`);
        });
      });
      
    } else {
      console.warn(`⚠️ No devices provided - creating fallback subscriptions for each zone`);
      
      // Create fallback subscriptions for each zone
      zoneIds.forEach(zoneId => {
        const knownDevices = zoneId === ALLTRAQ_ZONE_ID 
          ? ["26070", "26071", "26072", "26073", "26074", "26075"]
          : ["SIM1", "SIM2", "SIM3", "SIM4", "SIM5"];
        
        const subscription = {
          type: "request",
          request: "BeginStream",
          reqid: `threeDZoneViewer_fallback_zone${zoneId}`,
          params: knownDevices.map(id => ({ id, data: "true" })),
          zone_id: zoneId,
          description: `Fallback for zone ${zoneId}: ${knownDevices.length} known devices`
        };
        
        subscriptions.push(subscription);
      });
    }
    
    // Limit total subscriptions to prevent overwhelming the server
    const limitedSubscriptions = subscriptions.slice(0, MAX_SUBSCRIPTION_ATTEMPTS);
    
    console.log(`📡 Generated ${limitedSubscriptions.length} multi-zone WebSocket subscriptions (${zoneIds.length} zones)`);
    return limitedSubscriptions;
  }
  
  /**
   * Build device-specific subscriptions (WORKING - proven with tag 26070)
   * @param {Array} devices - Array of device objects
   * @param {number} selectedCampusId - Campus zone ID for subscription
   * @returns {Array} Array of device-specific subscription objects
   */
  static _buildDeviceSpecificSubscriptions(devices, selectedCampusId) {
    if (!devices || devices.length === 0) {
      return [];
    }
    
    // Sort devices by priority to ensure important devices are subscribed first
    const sortedDevices = sortDevicesByPriority(devices);
    const subscriptions = [];
    
    // Group devices into chunks to avoid oversized messages
    const deviceChunks = this._chunkDevices(sortedDevices, MAX_DEVICES_PER_SUBSCRIPTION);
    
    deviceChunks.forEach((chunk, index) => {
      const deviceParams = chunk.map(device => ({
        id: device.x_id_dev,
        data: "true"
      }));
      
      subscriptions.push({
        type: "request",
        request: "BeginStream",
        reqid: `threeDZoneViewer_devices_${index + 1}`,
        params: deviceParams,
        zone_id: selectedCampusId || ALLTRAQ_ZONE_ID,
        description: `Device chunk ${index + 1}: ${chunk.length} devices`
      });
      
      console.log(`📡 Built device subscription ${index + 1}: ${chunk.length} devices (${chunk.slice(0, 3).map(d => d.x_id_dev).join(', ')}${chunk.length > 3 ? '...' : ''})`);
    });
    
    return subscriptions;
  }
  
  /**
   * Build fallback subscriptions for known working device IDs
   * @param {number} selectedCampusId - Campus zone ID
   * @returns {Array} Array of fallback subscription objects
   */
  static _buildFallbackDeviceSubscriptions(selectedCampusId) {
    // Use known working AllTraq device IDs (from testing)
    const knownWorkingDevices = ["26070", "26071", "26072", "26073", "26074", "26075"];
    
    const subscription = {
      type: "request",
      request: "BeginStream",
      reqid: "threeDZoneViewer_fallback_alltraq",
      params: knownWorkingDevices.map(id => ({ id, data: "true" })),
      zone_id: ALLTRAQ_ZONE_ID, // Use AllTraq zone as these are AllTraq devices
      description: "Fallback AllTraq devices (known working)"
    };
    
    console.log(`📡 Built fallback subscription for known working AllTraq devices: ${knownWorkingDevices.join(', ')}`);
    return [subscription];
  }
  
  /**
   * Build fallback subscriptions for common simulator tags and zones
   * @param {number} selectedCampusId - Campus zone ID
   * @returns {Array} Array of fallback subscription objects
   */
  static buildFallbackSubscriptions(selectedCampusId) {
    const subscriptions = [];
    
    // Campus simulator subscription
    if (selectedCampusId) {
      const simulatorDevices = ["SIM1", "SIM2", "SIM3", "SIM4", "SIM5"];
      subscriptions.push({
        type: "request",
        request: "BeginStream",
        reqid: "threeDZoneViewer_fallback_simulators",
        params: simulatorDevices.map(id => ({ id, data: "true" })),
        zone_id: selectedCampusId,
        description: "Fallback simulator tags for campus"
      });
    }
    
    // AllTraq subscription
    const alltraqDevices = ["26070", "26071", "26072", "26073", "26074"];
    subscriptions.push({
      type: "request",
      request: "BeginStream",
      reqid: "threeDZoneViewer_fallback_alltraq",
      params: alltraqDevices.map(id => ({ id, data: "true" })),
      zone_id: ALLTRAQ_ZONE_ID,
      description: "Fallback AllTraq tags"
    });
    
    console.log(`📡 Built ${subscriptions.length} fallback subscriptions: simulators + AllTraq devices`);
    return subscriptions;
  }
  
  /**
   * Chunk devices into smaller groups to avoid message size limits
   * @param {Array} devices - Array of device objects
   * @param {number} chunkSize - Maximum devices per chunk
   * @returns {Array<Array>} Array of device chunks
   */
  static _chunkDevices(devices, chunkSize) {
    const chunks = [];
    for (let i = 0; i < devices.length; i += chunkSize) {
      chunks.push(devices.slice(i, i + chunkSize));
    }
    return chunks;
  }
  
  /**
   * Build subscription for specific device categories
   * @param {Array} devices - Array of device objects
   * @param {Array<string>} categories - Array of category names to include
   * @param {number} selectedCampusId - Campus zone ID
   * @returns {Array} Array of category-specific subscription objects
   */
  static buildCategorySubscriptions(devices, categories, selectedCampusId) {
    if (!Array.isArray(categories) || categories.length === 0) {
      return [];
    }
    
    const subscriptions = [];
    
    categories.forEach(category => {
      const categoryDevices = devices.filter(device => device.deviceCategory === category);
      
      if (categoryDevices.length > 0) {
        const deviceChunks = this._chunkDevices(categoryDevices, MAX_DEVICES_PER_SUBSCRIPTION);
        
        deviceChunks.forEach((chunk, index) => {
          const deviceParams = chunk.map(device => ({
            id: device.x_id_dev,
            data: "true"
          }));
          
          subscriptions.push({
            type: "request",
            request: "BeginStream",
            reqid: `threeDZoneViewer_${category}_${index + 1}`,
            params: deviceParams,
            zone_id: selectedCampusId || ALLTRAQ_ZONE_ID,
            description: `${category} devices chunk ${index + 1}: ${chunk.length} devices`
          });
        });
      }
    });
    
    console.log(`📡 Built ${subscriptions.length} category-specific subscriptions for categories: ${categories.join(', ')}`);
    return subscriptions;
  }
  
  /**
   * Validate subscription object format
   * @param {Object} subscription - Subscription object to validate
   * @returns {boolean} True if subscription is valid
   */
  static validateSubscription(subscription) {
    const required = ['type', 'request', 'reqid', 'params'];
    
    for (const field of required) {
      if (!(field in subscription)) {
        console.error(`❌ Invalid subscription: missing field '${field}'`, subscription);
        return false;
      }
    }
    
    if (!Array.isArray(subscription.params)) {
      console.error(`❌ Invalid subscription: 'params' must be an array`, subscription);
      return false;
    }
    
    if (subscription.params.length === 0) {
      console.warn(`⚠️ Empty subscription params`, subscription);
    }
    
    // Validate that we're not using broken wildcards
    const hasWildcard = subscription.params.some(param => param.id === "*");
    if (hasWildcard) {
      console.error(`❌ Invalid subscription: wildcard "*" not supported by server`, subscription);
      return false;
    }
    
    return true;
  }
  
  /**
   * Log subscription summary for debugging
   * @param {Array} subscriptions - Array of subscription objects
   */
  static logSubscriptionSummary(subscriptions) {
    // Validate input
    if (!Array.isArray(subscriptions)) {
      console.error(`❌ logSubscriptionSummary: Expected array, got ${typeof subscriptions}`);
      return;
    }
    
    console.log(`📡 Multi-Zone Subscription Summary:`);
    console.log(`   Total subscriptions: ${subscriptions.length}`);
    
    const deviceCount = subscriptions.reduce((count, sub) => {
      return count + (sub.params ? sub.params.length : 0);
    }, 0);
    
    const zoneBreakdown = {};
    subscriptions.forEach(sub => {
      const zoneId = sub.zone_id;
      if (!zoneBreakdown[zoneId]) {
        zoneBreakdown[zoneId] = { count: 0, devices: 0 };
      }
      zoneBreakdown[zoneId].count++;
      zoneBreakdown[zoneId].devices += sub.params?.length || 0;
    });
    
    console.log(`   Total device subscriptions: ${deviceCount}`);
    console.log(`   Zone breakdown:`, Object.entries(zoneBreakdown).map(([zoneId, info]) => 
      `Zone ${zoneId}: ${info.count} subscriptions, ${info.devices} devices`
    ).join('; '));
    
    subscriptions.forEach((sub, index) => {
      console.log(`   ${index + 1}. ${sub.reqid}: ${sub.params?.length || 0} devices (${sub.description || 'no description'})`);
    });
    
    // Log wildcard status
    const wildcardCount = subscriptions.reduce((count, sub) => {
      const wildcards = sub.params?.filter(param => param.id === "*").length || 0;
      return count + wildcards;
    }, 0);
    
    if (wildcardCount > 0) {
      console.error(`❌ WARNING: ${wildcardCount} wildcard subscriptions detected - these will fail due to server bug`);
    } else {
      console.log(`✅ No wildcard subscriptions - all device-specific (server compatible)`);
    }
  }
  
  /**
   * Clear zone cache
   */
  static clearZoneCache() {
    this.zoneCache.clear();
    console.log(`🧹 Zone hierarchy cache cleared`);
  }
  
  /**
   * Get zone cache info
   */
  static getZoneCacheInfo() {
    const entries = Array.from(this.zoneCache.entries()).map(([key, value]) => ({
      key,
      zoneCount: value.zoneIds.length,
      age: Date.now() - value.timestamp,
      expired: Date.now() - value.timestamp > ZONE_CACHE_TIMEOUT
    }));
    
    return {
      totalEntries: this.zoneCache.size,
      entries
    };
  }
}

export default DeviceSubscriptionBuilder;