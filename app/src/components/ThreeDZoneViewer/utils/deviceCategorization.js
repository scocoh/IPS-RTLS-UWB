/* Name: deviceCategorization.js */
/* Version: 0.1.0 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: Device categorization utilities for real-time tag processing */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend Utility */
/* Status: Active */
/* Dependent: TRUE */

// Zone constants for categorization
export const ALLTRAQ_ZONE_ID = 451; // Boca campus zone for alltraq data
export const BOCA_CAMPUS_ID = 449;  // Boca campus parent zone

/**
 * Device categories for visualization and filtering
 */
export const DEVICE_CATEGORIES = {
  ALLTRAQ: 'alltraq',
  SIMULATOR: 'simulator', 
  TAG: 'tag',
  PERSONNEL: 'personnel',
  CART: 'cart',
  EQUIPMENT: 'equipment',
  INFRASTRUCTURE: 'infrastructure',
  CAMPUS: 'campus',
  OTHER: 'other',
  UNKNOWN: 'unknown'
};

/**
 * Priority mapping for device categories (lower = higher priority)
 */
export const CATEGORY_PRIORITIES = {
  [DEVICE_CATEGORIES.ALLTRAQ]: 1,
  [DEVICE_CATEGORIES.SIMULATOR]: 2,
  [DEVICE_CATEGORIES.TAG]: 3,
  [DEVICE_CATEGORIES.PERSONNEL]: 4,
  [DEVICE_CATEGORIES.CART]: 5,
  [DEVICE_CATEGORIES.EQUIPMENT]: 6,
  [DEVICE_CATEGORIES.INFRASTRUCTURE]: 9,
  [DEVICE_CATEGORIES.CAMPUS]: 7,
  [DEVICE_CATEGORIES.OTHER]: 10,
  [DEVICE_CATEGORIES.UNKNOWN]: 11
};

/**
 * Categorize a device based on its type and metadata
 * @param {Object} device - Device object from API
 * @param {Object} deviceTypeInfo - Device type metadata
 * @returns {Object} Enhanced device with category and priority
 */
export function categorizeDevice(device, deviceTypeInfo = null) {
  const deviceType = device.i_typ_dev || device.deviceTypeId;
  const deviceId = device.x_id_dev;
  const deviceName = device.x_nm_dev || deviceId;
  const deviceTypeDescription = deviceTypeInfo?.x_dsc_dev || `Type ${deviceType}`;

  let category = DEVICE_CATEGORIES.OTHER;
  let priority = CATEGORY_PRIORITIES[DEVICE_CATEGORIES.OTHER];

  // Categorize based on device type and name patterns
  if (deviceType === 27) {
    category = DEVICE_CATEGORIES.ALLTRAQ;
    priority = CATEGORY_PRIORITIES[DEVICE_CATEGORIES.ALLTRAQ];
  } else if (deviceType === 1 || deviceType === 2) {
    if (deviceId.toLowerCase().startsWith('sim') || 
        deviceName.toLowerCase().includes('sim')) {
      category = DEVICE_CATEGORIES.SIMULATOR;
      priority = CATEGORY_PRIORITIES[DEVICE_CATEGORIES.SIMULATOR];
    } else {
      category = DEVICE_CATEGORIES.TAG;
      priority = CATEGORY_PRIORITIES[DEVICE_CATEGORIES.TAG];
    }
  } else if (deviceType === 4) {
    category = DEVICE_CATEGORIES.PERSONNEL;
    priority = CATEGORY_PRIORITIES[DEVICE_CATEGORIES.PERSONNEL];
  } else if (deviceType === 24) {
    category = DEVICE_CATEGORIES.CART;
    priority = CATEGORY_PRIORITIES[DEVICE_CATEGORIES.CART];
  } else if ([19, 20, 21, 22].includes(deviceType)) {
    category = DEVICE_CATEGORIES.EQUIPMENT;
    priority = CATEGORY_PRIORITIES[DEVICE_CATEGORIES.EQUIPMENT];
  } else if ([6, 7, 8, 9, 10, 11].includes(deviceType)) {
    category = DEVICE_CATEGORIES.INFRASTRUCTURE;
    priority = CATEGORY_PRIORITIES[DEVICE_CATEGORIES.INFRASTRUCTURE];
  }

  return {
    ...device,
    deviceCategory: category,
    deviceTypeId: deviceType,
    deviceTypeDescription: deviceTypeDescription,
    subscription_priority: priority
  };
}

/**
 * Categorize tag data based on zone and device information
 * @param {string} tagId - Tag ID from GIS data
 * @param {number} zoneId - Zone ID from GIS data
 * @param {number} selectedCampusId - Currently selected campus
 * @param {Array} availableDevices - Array of known devices
 * @returns {Object} Tag categorization result
 */
export function categorizeTagByZone(tagId, zoneId, selectedCampusId, availableDevices = []) {
  // Check if this tag is in our available devices list
  const deviceInfo = availableDevices.find(device => device.x_id_dev === tagId);
  
  let tagCategory = DEVICE_CATEGORIES.OTHER;
  let isAlltraqTag = false;
  
  if (deviceInfo) {
    tagCategory = deviceInfo.deviceCategory;
    isAlltraqTag = tagCategory === DEVICE_CATEGORIES.ALLTRAQ;
  } else if (zoneId === ALLTRAQ_ZONE_ID || zoneId === BOCA_CAMPUS_ID) {
    tagCategory = DEVICE_CATEGORIES.ALLTRAQ;
    isAlltraqTag = true;
  } else if (selectedCampusId && zoneId === selectedCampusId) {
    tagCategory = DEVICE_CATEGORIES.CAMPUS;
  } else if (zoneId) {
    tagCategory = DEVICE_CATEGORIES.OTHER;
  } else {
    tagCategory = DEVICE_CATEGORIES.UNKNOWN;
  }

  return {
    category: tagCategory,
    isAlltraq: isAlltraqTag,
    source: isAlltraqTag ? 'alltraq' : 'parco',
    deviceInfo: deviceInfo || null,
    deviceType: deviceInfo?.i_typ_dev || null,
    deviceName: deviceInfo?.x_nm_dev || tagId
  };
}

/**
 * Group devices by category
 * @param {Array} devices - Array of devices
 * @returns {Object} Object with devices grouped by category
 */
export function groupDevicesByCategory(devices) {
  const grouped = {};
  
  // Initialize all categories
  Object.values(DEVICE_CATEGORIES).forEach(category => {
    grouped[category] = [];
  });
  
  devices.forEach(device => {
    const category = device.deviceCategory || DEVICE_CATEGORIES.OTHER;
    if (grouped[category]) {
      grouped[category].push(device);
    } else {
      grouped[DEVICE_CATEGORIES.OTHER].push(device);
    }
  });
  
  return grouped;
}

/**
 * Get device statistics by category
 * @param {Array} devices - Array of devices
 * @returns {Object} Statistics object with counts per category
 */
export function getDeviceStatsByCategory(devices) {
  const stats = {};
  
  // Initialize all categories with 0
  Object.values(DEVICE_CATEGORIES).forEach(category => {
    stats[category] = 0;
  });
  
  devices.forEach(device => {
    const category = device.deviceCategory || DEVICE_CATEGORIES.OTHER;
    if (stats[category] !== undefined) {
      stats[category]++;
    } else {
      stats[DEVICE_CATEGORIES.OTHER]++;
    }
  });
  
  // Add totals
  stats.total = devices.length;
  stats.tracking = stats[DEVICE_CATEGORIES.ALLTRAQ] + 
                   stats[DEVICE_CATEGORIES.SIMULATOR] + 
                   stats[DEVICE_CATEGORIES.TAG] + 
                   stats[DEVICE_CATEGORIES.PERSONNEL];
  
  return stats;
}

/**
 * Sort devices by priority and name
 * @param {Array} devices - Array of devices
 * @returns {Array} Sorted array of devices
 */
export function sortDevicesByPriority(devices) {
  return [...devices].sort((a, b) => {
    const priorityA = a.subscription_priority || CATEGORY_PRIORITIES[DEVICE_CATEGORIES.OTHER];
    const priorityB = b.subscription_priority || CATEGORY_PRIORITIES[DEVICE_CATEGORIES.OTHER];
    
    if (priorityA !== priorityB) {
      return priorityA - priorityB;
    }
    
    // Secondary sort by device ID
    const idA = a.x_id_dev || '';
    const idB = b.x_id_dev || '';
    return idA.localeCompare(idB);
  });
}

/**
 * Filter devices by categories
 * @param {Array} devices - Array of devices
 * @param {Array<string>} allowedCategories - Array of allowed category names
 * @returns {Array} Filtered array of devices
 */
export function filterDevicesByCategories(devices, allowedCategories) {
  if (!Array.isArray(allowedCategories) || allowedCategories.length === 0) {
    return devices;
  }
  
  return devices.filter(device => {
    const category = device.deviceCategory || DEVICE_CATEGORIES.OTHER;
    return allowedCategories.includes(category);
  });
}

/**
 * Get category display information for UI
 * @param {string} category - Category name
 * @returns {Object} Display information with icon, color, and label
 */
export function getCategoryDisplayInfo(category) {
  const displayMap = {
    [DEVICE_CATEGORIES.ALLTRAQ]: { icon: '🎯', color: '#ff4400', label: 'AllTraq Tags' },
    [DEVICE_CATEGORIES.SIMULATOR]: { icon: '🎮', color: '#00ff00', label: 'Simulator Tags' },
    [DEVICE_CATEGORIES.TAG]: { icon: '🏷️', color: '#0066ff', label: 'Standard Tags' },
    [DEVICE_CATEGORIES.PERSONNEL]: { icon: '👤', color: '#ff6600', label: 'Personnel Badges' },
    [DEVICE_CATEGORIES.CART]: { icon: '🛒', color: '#ffcc00', label: 'Case Carts' },
    [DEVICE_CATEGORIES.EQUIPMENT]: { icon: '⚕️', color: '#cc00ff', label: 'Medical Equipment' },
    [DEVICE_CATEGORIES.INFRASTRUCTURE]: { icon: '🔧', color: '#666666', label: 'Infrastructure' },
    [DEVICE_CATEGORIES.CAMPUS]: { icon: '🏫', color: '#00cc66', label: 'Campus Tags' },
    [DEVICE_CATEGORIES.OTHER]: { icon: '📦', color: '#888888', label: 'Other Devices' },
    [DEVICE_CATEGORIES.UNKNOWN]: { icon: '❓', color: '#cccccc', label: 'Unknown' }
  };
  
  return displayMap[category] || displayMap[DEVICE_CATEGORIES.UNKNOWN];
}