/* Name: tagDataProcessor.js */
/* Version: 0.1.2 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: Tag data processing utilities for real-time GIS data handling - REMOVED ALL THROTTLING */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend Utility */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.2: REMOVED ALL THROTTLING - per-tag throttle was still dropping legitimate updates, now matches 2D viewer behavior */
/* - 0.1.1: FIXED throttling issue - removed global throttle that was dropping 47+ tags per second */

import { categorizeTagByZone, DEVICE_CATEGORIES } from './deviceCategorization.js';

// Processing configuration
const MAX_HISTORY_LENGTH = 50; // Maximum historical positions per tag
const POSITION_VALIDATION_THRESHOLD = 1000; // Maximum reasonable coordinate value

/**
 * Tag data processor for handling real-time GIS data
 */
export class TagDataProcessor {
  
  /**
   * Process incoming GIS data message
   * @param {Object} data - Raw GIS data from WebSocket
   * @param {Object} context - Processing context
   * @param {Array} context.availableDevices - Known devices
   * @param {number} context.selectedCampusId - Selected campus ID
   * @param {number} context.lastUpdateTime - Last update timestamp
   * @returns {Object|null} Processed tag data or null if invalid
   */
  static processGISData(data, context = {}) {
    const {
      availableDevices = [],
      selectedCampusId = null,
      lastUpdateTime = 0
    } = context;
    
    // Extract and validate basic data
    const validation = this._validateGISData(data);
    if (!validation.isValid) {
      console.warn(`⚠️ Invalid GISData message:`, validation.errors, data);
      return null;
    }
    
    const { tagId, x, y, z, sequence, zoneId } = validation.data;
    const now = Date.now();
    
    // REMOVED v0.1.2: All throttling removed to match 2D viewer behavior
    // Now processes every incoming tag update immediately
    
    // Categorize the tag
    const categorization = categorizeTagByZone(tagId, zoneId, selectedCampusId, availableDevices);
    
    // Build enhanced tag data object
    const tagData = {
      id: tagId,
      x: x,
      y: y,
      z: z,
      zone_id: zoneId,
      sequence: sequence,
      timestamp: now,
      isActive: true,
      // Enhanced metadata from categorization
      category: categorization.category,
      isAlltraq: categorization.isAlltraq,
      source: categorization.source,
      deviceInfo: categorization.deviceInfo,
      deviceType: categorization.deviceType,
      deviceName: categorization.deviceName,
      // Processing metadata
      processedAt: now,
      isThrottled: false
    };
    
    console.log(`📍 Processed tag ${tagId} (${tagData.deviceName}): (${x.toFixed(2)}, ${y.toFixed(2)}, ${z.toFixed(2)}) [${categorization.category}] zone ${zoneId}`);
    
    return tagData;
  }
  
  /**
   * Validate incoming GIS data
   * @param {Object} data - Raw GIS data
   * @returns {Object} Validation result with extracted data
   */
  static _validateGISData(data) {
    const errors = [];
    
    // Extract tag ID with multiple fallback formats
    const tagId = data.ID || data.id || data.tagId;
    if (!tagId) {
      errors.push('Missing tag ID (ID, id, or tagId)');
    }
    
    // Extract coordinates with validation
    const x = parseFloat(data.X || data.x);
    const y = parseFloat(data.Y || data.y);
    const z = parseFloat(data.Z || data.z || 0);
    
    if (isNaN(x) || isNaN(y)) {
      errors.push('Invalid coordinates: X and Y must be numbers');
    }
    
    // Validate coordinate ranges (basic sanity check)
    if (Math.abs(x) > POSITION_VALIDATION_THRESHOLD || Math.abs(y) > POSITION_VALIDATION_THRESHOLD) {
      errors.push(`Coordinates out of reasonable range: (${x}, ${y})`);
    }
    
    // Extract optional fields
    const sequence = parseInt(data.Sequence || data.sequence || 0);
    const zoneId = data.zone_id || data.zoneId;
    
    const isValid = errors.length === 0;
    
    return {
      isValid,
      errors,
      data: isValid ? { tagId, x, y, z, sequence, zoneId } : null
    };
  }
  
  /**
   * Update tag history with new position
   * @param {Object} tagData - Processed tag data
   * @param {Array} currentHistory - Current tag history array
   * @param {number} maxLength - Maximum history length
   * @returns {Array} Updated history array
   */
  static updateTagHistory(tagData, currentHistory = [], maxLength = MAX_HISTORY_LENGTH) {
    const newPosition = {
      x: tagData.x,
      y: tagData.y,
      z: tagData.z,
      timestamp: tagData.timestamp,
      zone_id: tagData.zone_id,
      category: tagData.category,
      deviceName: tagData.deviceName,
      sequence: tagData.sequence
    };
    
    // Add new position and limit history length
    const updatedHistory = [...currentHistory, newPosition].slice(-maxLength);
    
    console.debug(`📈 Updated history for ${tagData.id}: ${updatedHistory.length} positions`);
    
    return updatedHistory;
  }
  
  /**
   * Calculate tag movement statistics
   * @param {Array} tagHistory - Tag position history
   * @returns {Object} Movement statistics
   */
  static calculateMovementStats(tagHistory) {
    if (!Array.isArray(tagHistory) || tagHistory.length < 2) {
      return {
        distance: 0,
        speed: 0,
        direction: 0,
        isMoving: false,
        lastMovement: null
      };
    }
    
    const latest = tagHistory[tagHistory.length - 1];
    const previous = tagHistory[tagHistory.length - 2];
    
    // Calculate distance between last two positions
    const dx = latest.x - previous.x;
    const dy = latest.y - previous.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    
    // Calculate time difference
    const timeDiff = (latest.timestamp - previous.timestamp) / 1000; // seconds
    
    // Calculate speed (units per second)
    const speed = timeDiff > 0 ? distance / timeDiff : 0;
    
    // Calculate direction (angle in degrees)
    const direction = Math.atan2(dy, dx) * (180 / Math.PI);
    
    // Determine if tag is moving (threshold: 0.1 units)
    const isMoving = distance > 0.1;
    
    return {
      distance: distance,
      speed: speed,
      direction: direction,
      isMoving: isMoving,
      lastMovement: isMoving ? latest.timestamp : null,
      timeSinceLastUpdate: timeDiff
    };
  }
  
  /**
   * Group tags by category for efficient processing
   * @param {Object} allTagsData - Object with all tag data
   * @returns {Object} Tags grouped by category
   */
  static groupTagsByCategory(allTagsData) {
    const grouped = {
      [DEVICE_CATEGORIES.ALLTRAQ]: {},
      [DEVICE_CATEGORIES.CAMPUS]: {},
      [DEVICE_CATEGORIES.SIMULATOR]: {},
      [DEVICE_CATEGORIES.TAG]: {},
      [DEVICE_CATEGORIES.PERSONNEL]: {},
      [DEVICE_CATEGORIES.CART]: {},
      [DEVICE_CATEGORIES.EQUIPMENT]: {},
      [DEVICE_CATEGORIES.OTHER]: {},
      [DEVICE_CATEGORIES.UNKNOWN]: {}
    };
    
    Object.values(allTagsData).forEach(tagData => {
      const category = tagData.category || DEVICE_CATEGORIES.OTHER;
      if (grouped[category]) {
        grouped[category][tagData.id] = tagData;
      } else {
        grouped[DEVICE_CATEGORIES.OTHER][tagData.id] = tagData;
      }
    });
    
    return grouped;
  }
  
  /**
   * Filter tags for display based on selection
   * @param {Object} allTagsData - All available tag data
   * @param {Set} selectedTags - Set of selected tag IDs
   * @returns {Object} Filtered tag data for display
   */
  static getDisplayTags(allTagsData, selectedTags) {
    const displayTags = {};
    
    selectedTags.forEach(tagId => {
      if (allTagsData[tagId]) {
        displayTags[tagId] = allTagsData[tagId];
      }
    });
    
    console.debug(`🎯 Display tags filtered: ${Object.keys(displayTags).length} selected from ${Object.keys(allTagsData).length} total`);
    
    return displayTags;
  }
  
  /**
   * Calculate tag statistics for monitoring
   * @param {Object} allTagsData - All tag data
   * @param {Array} timestamps - Recent update timestamps
   * @returns {Object} Tag statistics
   */
  static calculateTagStats(allTagsData, timestamps = []) {
    const now = Date.now();
    const windowStart = now - 10000; // 10 second window
    
    // Filter timestamps to window
    const recentTimestamps = timestamps.filter(ts => ts >= windowStart);
    
    // Calculate update rate
    const timeSpan = recentTimestamps.length > 1 ? 
      (recentTimestamps[recentTimestamps.length - 1] - recentTimestamps[0]) / 1000 : 0;
    const updateRate = timeSpan > 0 ? (recentTimestamps.length - 1) / timeSpan : 0;
    
    // Group by category for stats
    const categoryStats = {};
    const groupedTags = this.groupTagsByCategory(allTagsData);
    
    Object.keys(groupedTags).forEach(category => {
      categoryStats[category] = Object.keys(groupedTags[category]).length;
    });
    
    return {
      totalTags: Object.keys(allTagsData).length,
      activeTags: Object.values(allTagsData).filter(tag => tag.isActive).length,
      updateRate: updateRate,
      lastUpdateTime: recentTimestamps.length > 0 ? recentTimestamps[recentTimestamps.length - 1] : null,
      categoryBreakdown: categoryStats,
      recentUpdates: recentTimestamps.length
    };
  }
  
  /**
   * Clean up old or stale tag data
   * @param {Object} allTagsData - All tag data
   * @param {number} maxAge - Maximum age in milliseconds
   * @returns {Object} Cleaned tag data
   */
  static cleanupStaleData(allTagsData, maxAge = 300000) { // 5 minutes default
    const now = Date.now();
    const cleanedData = {};
    let removedCount = 0;
    
    Object.entries(allTagsData).forEach(([tagId, tagData]) => {
      const age = now - tagData.timestamp;
      if (age <= maxAge) {
        cleanedData[tagId] = tagData;
      } else {
        removedCount++;
        console.debug(`🧹 Removed stale tag data: ${tagId} (age: ${Math.round(age / 1000)}s)`);
      }
    });
    
    if (removedCount > 0) {
      console.log(`🧹 Cleaned up ${removedCount} stale tag entries`);
    }
    
    return cleanedData;
  }
}

export default TagDataProcessor;