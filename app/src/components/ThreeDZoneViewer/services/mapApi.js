/* Name: mapApi.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: API service for map data operations */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/services */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { config } from '../../../config';

class MapApi {
  constructor() {
    this.baseUrl = config.ZONEVIEWER_API_URL;
    this.cache = new Map();
    this.cacheTimeout = 5 * 60 * 1000; // 5 minutes
  }

  /**
   * Get cached data if available and not expired
   */
  getCachedData(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      console.log(`📋 Using cached data for ${key}`);
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
      console.log(`🌐 Fetching: ${url}`);
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
      console.log(`✅ Fetch successful: ${url}`);
      return data;

    } catch (error) {
      console.error(`❌ Fetch failed: ${url}`, error);
      throw new Error(`Failed to fetch from ${url}: ${error.message}`);
    }
  }

  /**
   * Get map data by map ID
   */
  async getMapData(mapId) {
    const cacheKey = `map_data_${mapId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.baseUrl}/get_map_data/${mapId}`;
    const data = await this.fetchWithErrorHandling(url);
    
    this.setCachedData(cacheKey, data);
    return data;
  }

  /**
   * Get map metadata by map ID
   */
  async getMapMetadata(mapId) {
    const cacheKey = `map_metadata_${mapId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.baseUrl}/get_map_metadata/${mapId}`;
    const data = await this.fetchWithErrorHandling(url);
    
    this.setCachedData(cacheKey, data);
    return data;
  }

  /**
   * Get map image URL
   */
  getMapImageUrl(mapId) {
    return `${this.baseUrl}/get_map/${mapId}`;
  }

  /**
   * Get map image as blob
   */
  async getMapImage(mapId) {
    const cacheKey = `map_image_${mapId}`;
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = this.getMapImageUrl(mapId);
    
    try {
      console.log(`🖼️ Fetching map image: ${url}`);
      const response = await fetch(url);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const blob = await response.blob();
      console.log(`✅ Map image fetched: ${mapId}`);
      
      this.setCachedData(cacheKey, blob);
      return blob;
      
    } catch (error) {
      console.error(`❌ Failed to fetch map image ${mapId}:`, error);
      throw error;
    }
  }

  /**
   * Get all maps with zone types
   */
  async getMapsWithZoneTypes() {
    const cacheKey = 'maps_with_zone_types';
    const cached = this.getCachedData(cacheKey);
    if (cached) return cached;

    const url = `${this.baseUrl}/get_maps_with_zone_types`;
    const data = await this.fetchWithErrorHandling(url);
    
    this.setCachedData(cacheKey, data);
    return data;
  }

  /**
   * Get map bounds in different formats
   */
  async getMapBounds(mapId, format = 'leaflet') {
    const mapData = await this.getMapData(mapId);
    
    if (!mapData || !mapData.bounds) {
      throw new Error(`No bounds data available for map ${mapId}`);
    }

    const bounds = mapData.bounds;
    
    switch (format) {
      case 'leaflet':
        // Leaflet format: [[min_lat, min_lng], [max_lat, max_lng]]
        return bounds;
        
      case 'threejs':
        // Three.js format: {minX, minY, maxX, maxY}
        return {
          minX: bounds[0][1],
          minY: bounds[0][0],
          maxX: bounds[1][1],
          maxY: bounds[1][0]
        };
        
      case 'size':
        // Size format: {width, height, centerX, centerY}
        return {
          width: bounds[1][1] - bounds[0][1],
          height: bounds[1][0] - bounds[0][0],
          centerX: (bounds[1][1] + bounds[0][1]) / 2,
          centerY: (bounds[1][0] + bounds[0][0]) / 2
        };
        
      case 'raw':
        // Raw format from API
        return bounds;
        
      default:
        throw new Error(`Unknown bounds format: ${format}`);
    }
  }

  /**
   * Convert coordinates between different systems
   */
  convertCoordinates(x, y, fromBounds, toBounds, fromFormat = 'parco', toFormat = 'threejs') {
    // ParcoRTLS coordinate system to Three.js coordinate system
    if (fromFormat === 'parco' && toFormat === 'threejs') {
      // ParcoRTLS: Y increases going north, X increases going east
      // Three.js: Z increases going north, X increases going east
      return {
        x: x,
        y: 0, // Ground level
        z: y
      };
    }
    
    // Three.js to ParcoRTLS
    if (fromFormat === 'threejs' && toFormat === 'parco') {
      return {
        x: x,
        y: y // Assuming y in threejs represents z in parco
      };
    }
    
    // Normalize coordinates to 0-1 range
    if (fromFormat === 'parco' && toFormat === 'normalized') {
      const normalizedX = (x - fromBounds.minX) / (fromBounds.maxX - fromBounds.minX);
      const normalizedY = (y - fromBounds.minY) / (fromBounds.maxY - fromBounds.minY);
      return { x: normalizedX, y: normalizedY };
    }
    
    // Denormalize coordinates from 0-1 range
    if (fromFormat === 'normalized' && toFormat === 'parco') {
      const denormalizedX = x * (toBounds.maxX - toBounds.minX) + toBounds.minX;
      const denormalizedY = y * (toBounds.maxY - toBounds.minY) + toBounds.minY;
      return { x: denormalizedX, y: denormalizedY };
    }
    
    // Default: return as-is
    return { x, y };
  }

  /**
   * Validate map data
   */
  validateMapData(mapData) {
    if (!mapData) {
      return { valid: false, error: 'Map data is null or undefined' };
    }
    
    if (!mapData.bounds) {
      return { valid: false, error: 'Map data missing bounds' };
    }
    
    if (!Array.isArray(mapData.bounds) || mapData.bounds.length !== 2) {
      return { valid: false, error: 'Map bounds should be array of 2 elements' };
    }
    
    const [min, max] = mapData.bounds;
    if (!Array.isArray(min) || !Array.isArray(max) || min.length !== 2 || max.length !== 2) {
      return { valid: false, error: 'Map bound elements should be arrays of 2 coordinates' };
    }
    
    if (min[0] >= max[0] || min[1] >= max[1]) {
      return { valid: false, error: 'Invalid bounds: min values should be less than max values' };
    }
    
    return { valid: true };
  }

  /**
   * Get map statistics
   */
  async getMapStats(mapId) {
    try {
      const [mapData, mapMetadata] = await Promise.all([
        this.getMapData(mapId),
        this.getMapMetadata(mapId)
      ]);
      
      const bounds = await this.getMapBounds(mapId, 'size');
      
      return {
        mapId,
        hasData: !!mapData,
        hasMetadata: !!mapMetadata,
        bounds,
        area: bounds.width * bounds.height,
        aspectRatio: bounds.width / bounds.height,
        imageUrl: this.getMapImageUrl(mapId)
      };
      
    } catch (error) {
      console.error(`❌ Error getting map stats for ${mapId}:`, error);
      return {
        mapId,
        hasData: false,
        hasMetadata: false,
        error: error.message
      };
    }
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
    console.log('🧹 Map API cache cleared');
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
export default new MapApi();