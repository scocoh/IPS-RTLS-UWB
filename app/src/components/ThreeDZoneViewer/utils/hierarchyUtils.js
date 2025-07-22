/* Name: hierarchyUtils.js */
/* Version: 0.1.1 */
/* Created: 250720 */
/* Modified: 250720 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Zone hierarchy management utilities with full API integration for auto-transparency and cascade controls */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/utils */
/* Role: Frontend Utility */
/* Status: Active */
/* Dependent: TRUE */

import { config } from '../../../config';

/**
 * Fetch parent zones from API
 */
export const fetchParentZones = async () => {
  try {
    const response = await fetch(`${config.API_URL}/api/get_parents`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    console.log('📊 Fetched parent zones:', data);
    return data;
  } catch (error) {
    console.error('❌ Error fetching parent zones:', error);
    return [];
  }
};

/**
 * Fetch children zones for a specific zone
 */
export const fetchChildrenZones = async (zoneId) => {
  try {
    const response = await fetch(`${config.API_URL}/api/get_children/${zoneId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(`📊 Fetched children for zone ${zoneId}:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Error fetching children for zone ${zoneId}:`, error);
    return [];
  }
};

/**
 * Fetch all zones for a campus (full hierarchy)
 */
export const fetchCampusHierarchy = async (campusId) => {
  try {
    const response = await fetch(`${config.API_URL}/zoneviewer/get_all_zones_for_campus/${campusId}`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const data = await response.json();
    console.log(`📊 Fetched campus ${campusId} hierarchy:`, data);
    return data;
  } catch (error) {
    console.error(`❌ Error fetching campus ${campusId} hierarchy:`, error);
    return [];
  }
};

/**
 * Build hierarchy tree from flat zone list
 */
export const buildHierarchyTree = (zones) => {
  const zoneMap = new Map();
  const rootZones = [];
  
  // Create zone map
  zones.forEach(zone => {
    zoneMap.set(zone.zone_id, { ...zone, children: [] });
  });
  
  // Build parent-child relationships
  zones.forEach(zone => {
    if (zone.parent_zone_id) {
      const parent = zoneMap.get(zone.parent_zone_id);
      const child = zoneMap.get(zone.zone_id);
      if (parent && child) {
        parent.children.push(child);
      }
    } else {
      // Root zone (no parent)
      rootZones.push(zoneMap.get(zone.zone_id));
    }
  });
  
  console.log('🌳 Built hierarchy tree:', { rootZones, totalZones: zones.length });
  return rootZones;
};

/**
 * ENHANCED: Calculate zone hierarchy level from actual API data
 */
export const calculateZoneLevel = (zoneId, hierarchyData) => {
  // Handle both old flat array format and new API format
  if (Array.isArray(hierarchyData)) {
    // Old format - flat array of zones
    const zoneMap = new Map(hierarchyData.map(z => [z.zone_id, z]));
    
    const getLevel = (id, visited = new Set()) => {
      if (visited.has(id)) return 0; // Prevent infinite loops
      visited.add(id);
      
      const zone = zoneMap.get(id);
      if (!zone || !zone.parent_zone_id) return 0;
      
      return 1 + getLevel(zone.parent_zone_id, visited);
    };
    
    return getLevel(parseInt(zoneId));
  }
  
  // New format - hierarchical API data
  if (!hierarchyData || !hierarchyData.zones) return 0;
  
  const findZoneLevel = (zones, targetId, level = 0) => {
    for (const zone of zones) {
      if (zone.zone_id === targetId) {
        return level;
      }
      if (zone.children && zone.children.length > 0) {
        const childLevel = findZoneLevel(zone.children, targetId, level + 1);
        if (childLevel !== -1) return childLevel;
      }
    }
    return -1;
  };
  
  const level = findZoneLevel(hierarchyData.zones, parseInt(zoneId));
  console.log(`📊 Zone ${zoneId} hierarchy level: ${level}`);
  return Math.max(0, level);
};

/**
 * ENHANCED: Get all descendant zone IDs using actual API data
 */
export const getDescendantZoneIds = (zoneId, hierarchyData) => {
  const descendants = [];
  
  // Handle both old flat array format and new API format
  if (Array.isArray(hierarchyData)) {
    // Old format - flat array of zones
    const collectDescendants = (id) => {
      hierarchyData.forEach(zone => {
        if (zone.parent_zone_id === id) {
          descendants.push(zone.zone_id);
          collectDescendants(zone.zone_id); // Recursive for grandchildren
        }
      });
    };
    
    collectDescendants(parseInt(zoneId));
    return descendants;
  }
  
  // New format - hierarchical API data
  if (!hierarchyData || !hierarchyData.zones) return descendants;
  
  const findZoneAndGetDescendants = (zones, targetId) => {
    for (const zone of zones) {
      if (zone.zone_id === targetId) {
        // Found the target zone, collect all its descendants
        const collectDescendants = (children) => {
          children.forEach(child => {
            descendants.push(child.zone_id);
            if (child.children && child.children.length > 0) {
              collectDescendants(child.children);
            }
          });
        };
        
        if (zone.children) {
          collectDescendants(zone.children);
        }
        return true;
      }
      
      if (zone.children && zone.children.length > 0) {
        if (findZoneAndGetDescendants(zone.children, targetId)) {
          return true;
        }
      }
    }
    return false;
  };
  
  findZoneAndGetDescendants(hierarchyData.zones, parseInt(zoneId));
  console.log(`👥 Zone ${zoneId} descendants:`, descendants);
  return descendants;
};

/**
 * ENHANCED: AUTO-TRANSPARENCY with better hierarchy scaling
 * Senior zones (parents) = subtle, Progeny zones (children) = prominent
 */
export const calculateHierarchyOpacity = (zoneId, hierarchyData, baseOpacity = 0.2, increment = 0.1) => {
  const level = calculateZoneLevel(zoneId, hierarchyData);
  const opacity = Math.min(baseOpacity + (level * increment), 1.0);
  
  console.log(`🎨 Zone ${zoneId} hierarchy level ${level} → opacity ${opacity.toFixed(2)}`);
  return opacity;
};

/**
 * AUTO-COLORS: Get default color based on zone type with hierarchy consideration
 */
export const getHierarchyColor = (zoneType, hierarchyLevel = 0) => {
  const baseColors = {
    1: '#ff0000',   // Campus = Red
    2: '#00ff00',   // Building = Green  
    3: '#0000ff',   // Floor = Blue
    4: '#ff8800',   // Wing = Orange
    5: '#ffff00',   // Room = Yellow
    10: '#ff00ff',  // Area = Magenta
    901: '#800080'  // Virtual = Purple
  };
  
  // Adjust brightness based on hierarchy level (deeper = more saturated)
  const baseColor = baseColors[zoneType] || '#888888';
  
  // For now, return base color (future: could adjust saturation by hierarchy)
  return baseColor;
};

/**
 * ENHANCED: CASCADE VISIBILITY using API data
 */
export const getCascadeHiddenZones = (hiddenZoneIds, hierarchyData) => {
  const allHidden = new Set(hiddenZoneIds);
  
  hiddenZoneIds.forEach(zoneId => {
    const descendants = getDescendantZoneIds(zoneId, hierarchyData);
    descendants.forEach(id => allHidden.add(id));
  });
  
  return Array.from(allHidden);
};

/**
 * ENHANCED: HIERARCHY VALIDATION using API data
 */
export const validateHierarchySettings = (zoneSettings, hierarchyData) => {
  const warnings = [];
  
  // Handle both formats
  let zones = [];
  if (Array.isArray(hierarchyData)) {
    zones = hierarchyData;
  } else if (hierarchyData && hierarchyData.zones) {
    // Flatten the hierarchical structure for validation
    const flattenZones = (zoneList) => {
      let flattened = [];
      zoneList.forEach(zone => {
        flattened.push(zone);
        if (zone.children && zone.children.length > 0) {
          flattened = flattened.concat(flattenZones(zone.children));
        }
      });
      return flattened;
    };
    zones = flattenZones(hierarchyData.zones);
  }
  
  Object.keys(zoneSettings).forEach(zoneIdStr => {
    const zoneId = parseInt(zoneIdStr);
    const zone = zones.find(z => z.zone_id === zoneId);
    
    if (!zone) return;
    
    // Check if parent is visible when child is visible
    if (zoneSettings[zoneIdStr].visible && zone.parent_zone_id) {
      const parentSettings = zoneSettings[zone.parent_zone_id];
      if (parentSettings && !parentSettings.visible) {
        warnings.push(`Zone ${zone.zone_name} (${zoneId}) is visible but parent ${zone.parent_zone_id} is hidden`);
      }
    }
  });
  
  if (warnings.length > 0) {
    console.warn('⚠️ Hierarchy validation warnings:', warnings);
  }
  
  return warnings;
};

/**
 * ENHANCED: Generate hierarchy settings using API data
 */
export const generateHierarchySettings = (hierarchyData) => {
  const settings = {};
  
  // Handle both old flat array format and new API format
  if (Array.isArray(hierarchyData)) {
    // Old format - flat array of zones
    hierarchyData.forEach(zone => {
      const opacity = calculateHierarchyOpacity(zone.zone_id, hierarchyData);
      const color = getHierarchyColor(zone.zone_type, calculateZoneLevel(zone.zone_id, hierarchyData));
      
      settings[zone.zone_id] = {
        visible: true,
        opacity: opacity,
        color: color
      };
    });
    
    console.log('🏗️ Generated hierarchy-based settings for', hierarchyData.length, 'zones');
    return settings;
  }
  
  // New format - hierarchical API data
  if (!hierarchyData || !hierarchyData.zones) {
    console.warn('⚠️ No hierarchy data available for settings generation');
    return settings;
  }
  
  const processZones = (zones) => {
    zones.forEach(zone => {
      const level = calculateZoneLevel(zone.zone_id, hierarchyData);
      const opacity = calculateHierarchyOpacity(zone.zone_id, hierarchyData);
      const color = getHierarchyColor(zone.zone_type, level);
      
      settings[zone.zone_id] = {
        visible: true,
        opacity: opacity,
        color: color
      };
      
      // Process children recursively
      if (zone.children && zone.children.length > 0) {
        processZones(zone.children);
      }
    });
  };
  
  processZones(hierarchyData.zones);
  
  console.log('🏗️ Generated hierarchy-based settings for', Object.keys(settings).length, 'zones');
  console.log('📊 Settings by level:', settings);
  return settings;
};