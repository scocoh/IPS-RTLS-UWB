/* Name: zoneApi.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for zone data operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { config } from '../../../config';

class ZoneApi {
  constructor() {
    this.baseUrl = config.API_BASE_URL;
    this.zoneViewerUrl = config.ZONEVIEWER_API_URL;
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Get cached data if available and not expired
   */
  getCachedData(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      console.log(`📋 Using cached zone data for ${key}`);
      return cached.data;
    }
    return null;
  }

  /**
   * Set cached data with timestamp
   */
  setCachedData(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  /**
   * Generic fetch with error handling
   */
  async fetchWithErrorHandling(url, options = {}) {
    try {
      console.log(`🌐 Fetching zone data: ${url}`);
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers
        },
        ...options
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      console.log(`✅ Zone fetch successful: ${url}`);
      return data;

    } catch (error) {
      console.error(`❌ Zone fetch failed: ${url}`, error);
      throw new Error(`Failed to fetch zone data from ${url}: ${error.message}`);
    }
  }

  /**
   * Get all campus zones with hierarchy
   */
  async getCampusZones() {
    const cacheKey = 'campus_zones';
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.zoneViewerUrl}/get_campus_zones`;
    const data = await this.fetchWithErrorHandling(url);
    
    this.setCachedData(cacheKey, data);
    return data;
  }

  /**
   * Get all zones for a specific campus
   */
  async getZonesForCampus(campusId) {
    const cacheKey = `campus_zones_${campusId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.zoneViewerUrl}/get_all_zones_for_campus/${campusId}`;
    const data = await this.fetchWithErrorHandling(url);
    
    this.setCachedData(cacheKey, data);
    return data;
  }

  /**
   * Get regions for a specific zone
   */
  async getRegionsForZone(zoneId) {
    const cacheKey = `regions_${zoneId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.baseUrl}/api/get_regions_by_zone/${zoneId}`;
    
    try {
      const data = await this.fetchWithErrorHandling(url);
      this.setCachedData(cacheKey, data);
      return data;
    } catch (error) {
      // If no regions found, return empty array instead of throwing
      if (error.message.includes('404')) {
        console.log(`ℹ️ No regions found for zone ${zoneId}`);
        const emptyData = [];
        this.setCachedData(cacheKey, emptyData);
        return emptyData;
      }
      throw error;
    }
  }

  /**
   * Get vertices for a campus (all zones under campus)
   */
  async getVerticesForCampus(campusId) {
    const cacheKey = `vertices_campus_${campusId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.zoneViewerUrl}/get_vertices_for_campus/${campusId}`;
    const data = await this.fetchWithErrorHandling(url);
    
    this.setCachedData(cacheKey, data);
    return data;
  }

  /**
   * Get vertices for a specific zone
   */
  async getVerticesForZone(zoneId) {
    const cacheKey = `vertices_${zoneId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.baseUrl}/api/get_zone_vertices/${zoneId}`;
    
    try {
      const data = await this.fetchWithErrorHandling(url);
      this.setCachedData(cacheKey, data);
      return data.vertices || [];
    } catch (error) {
      // If no vertices found, return empty array
      if (error.message.includes('404')) {
        console.log(`ℹ️ No vertices found for zone ${zoneId}`);
        const emptyData = [];
        this.setCachedData(cacheKey, emptyData);
        return emptyData;
      }
      throw error;
    }
  }

  /**
   * Get zone details by ID
   */
  async getZoneById(zoneId) {
    const cacheKey = `zone_${zoneId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.baseUrl}/api/get_zone_by_id/${zoneId}`;
    const data = await this.fetchWithErrorHandling(url);
    
    this.setCachedData(cacheKey, data);
    return data;
  }

  /**
   * Get zones by type
   */
  async getZonesByType(zoneType) {
    const cacheKey = `zones_type_${zoneType}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    // Get all campus zones and filter by type
    const campusData = await this.getCampusZones();
    const allZones = this.flattenZoneHierarchy(campusData.campuses || []);
    const filteredZones = allZones.filter(zone => zone.zone_type === zoneType);
    
    this.setCachedData(cacheKey, filteredZones);
    return filteredZones;
  }

  /**
   * Get complete zone data (zone + regions + vertices)
   */
  async getCompleteZoneData(zoneId) {
    const cacheKey = `complete_zone_${zoneId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      // Fetch zone, regions, and vertices in parallel
      const [zone, regions, vertices] = await Promise.all([
        this.getZoneById(zoneId),
        this.getRegionsForZone(zoneId),
        this.getVerticesForZone(zoneId)
      ]);

      const completeData = {
        zone,
        regions,
        vertices,
        hasRegions: regions && regions.length > 0,
        hasVertices: vertices && vertices.length > 0
      };

      this.setCachedData(cacheKey, completeData);
      return completeData;

    } catch (error) {
      console.error(`❌ Error getting complete zone data for ${zoneId}:`, error);
      throw error;
    }
  }

  /**
   * Get bulk zone data for multiple zones
   */
  async getBulkZoneData(zoneIds) {
    const results = {};
    const promises = zoneIds.map(async (zoneId) => {
      try {
        const data = await this.getCompleteZoneData(zoneId);
        results[zoneId] = data;
      } catch (error) {
        console.error(`❌ Error fetching data for zone ${zoneId}:`, error);
        results[zoneId] = { error: error.message };
      }
    });

    await Promise.all(promises);
    return results;
  }

  /**
   * Flatten zone hierarchy into a single array
   */
  flattenZoneHierarchy(zones) {
    const flattened = [];
    
    const flatten = (zoneArray) => {
      zoneArray.forEach(zone => {
        flattened.push(zone);
        if (zone.children && zone.children.length > 0) {
          flatten(zone.children);
        }
      });
    };
    
    flatten(zones);
    return flattened;
  }

  /**
   * Get zone statistics
   */
  async getZoneStats() {
    const cacheKey = 'zone_stats';
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    try {
      const campusData = await this.getCampusZones();
      const allZones = this.flattenZoneHierarchy(campusData.campuses || []);
      
      const stats = {
        total: allZones.length,
        byType: {},
        campuses: campusData.campuses?.length || 0,
        withMaps: allZones.filter(z => z.map_id).length,
        withoutMaps: allZones.filter(z => !z.map_id).length
      };

      // Count by zone type
      allZones.forEach(zone => {
        const type = zone.zone_type;
        stats.byType[type] = (stats.byType[type] || 0) + 1;
      });

      this.setCachedData(cacheKey, stats);
      return stats;

    } catch (error) {
      console.error('❌ Error getting zone stats:', error);
      throw error;
    }
  }

  /**
   * Search zones by name
   */
  async searchZones(searchTerm) {
    const campusData = await this.getCampusZones();
    const allZones = this.flattenZoneHierarchy(campusData.campuses || []);
    
    const lowerSearchTerm = searchTerm.toLowerCase();
    return allZones.filter(zone => 
      zone.zone_name.toLowerCase().includes(lowerSearchTerm)
    );
  }

  /**
   * Get zone path (breadcrumb) by zone ID
   */
  async getZonePath(zoneId) {
    const campusData = await this.getCampusZones();
    const allZones = this.flattenZoneHierarchy(campusData.campuses || []);
    
    const zoneMap = {};
    allZones.forEach(zone => {
      zoneMap[zone.zone_id] = zone;
    });
    
    const path = [];
    let currentZone = zoneMap[zoneId];
    
    while (currentZone) {
      path.unshift(currentZone);
      currentZone = currentZone.parent_zone_id ? zoneMap[currentZone.parent_zone_id] : null;
    }
    
    return path;
  }

  /**
   * Validate zone data
   */
  validateZoneData(zone) {
    if (!zone) {
      return { valid: false, error: 'Zone data is null or undefined' };
    }
    
    if (!zone.zone_id) {
      return { valid: false, error: 'Zone missing zone_id' };
    }
    
    if (!zone.zone_name) {
      return { valid: false, error: 'Zone missing zone_name' };
    }
    
    if (zone.zone_type === undefined || zone.zone_type === null) {
      return { valid: false, error: 'Zone missing zone_type' };
    }
    
    return { valid: true };
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
    console.log('🧹 Zone API cache cleared');
  }

  /**
   * Get cache info
   */
  getCacheInfo() {
    const entries = Array.from(this.cache.entries()).map(([key, value]) => ({
      key,
      size: JSON.stringify(value.data).length,
      age: Date.now() - value.timestamp,
      expired: Date.now() - value.timestamp > this.cacheTimeout
    }));
    
    return {
      totalEntries: this.cache.size,
      totalSize: entries.reduce((sum, entry) => sum + entry.size, 0),
      entries
    };
  }
}

// Export singleton instance
export default new ZoneApi();