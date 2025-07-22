/* Name: useZoneHierarchy.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Hook for managing zone hierarchy and relationships */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useEffect, useMemo } from 'react';

const useZoneHierarchy = ({ campusData, regionData = {} }) => {
  const [expandedZones, setExpandedZones] = useState(new Set());
  const [selectedZonePath, setSelectedZonePath] = useState([]);
  const [zoneVisibility, setZoneVisibility] = useState({
    campus: true,    // L1
    building: true,  // L2, L3
    floor: true,     // L4
    wing: true,      // L5
    room: true       // L6
  });

  // Zone type mappings
  const ZONE_TYPES = {
    CAMPUS_L1: 1,
    BUILDING_L3: 2,
    FLOOR_L4: 3,
    WING_L5: 4,
    ROOM_L6: 5,
    BUILDING_OUTSIDE_L2: 10,
    OUTDOOR_GENERAL: 20,
    VIRTUAL_SUBJECT: 901
  };

  const ZONE_TYPE_LABELS = {
    [ZONE_TYPES.CAMPUS_L1]: 'Campus L1',
    [ZONE_TYPES.BUILDING_L3]: 'Building L3',
    [ZONE_TYPES.FLOOR_L4]: 'Floor L4',
    [ZONE_TYPES.WING_L5]: 'Wing L5',
    [ZONE_TYPES.ROOM_L6]: 'Room L6',
    [ZONE_TYPES.BUILDING_OUTSIDE_L2]: 'Building Outside L2',
    [ZONE_TYPES.OUTDOOR_GENERAL]: 'Outdoor General',
    [ZONE_TYPES.VIRTUAL_SUBJECT]: 'Virtual Subject Zone'
  };

  const ZONE_TYPE_COLORS = {
    [ZONE_TYPES.CAMPUS_L1]: '#ff0000',        // Red
    [ZONE_TYPES.BUILDING_OUTSIDE_L2]: '#ff8800', // Orange
    [ZONE_TYPES.BUILDING_L3]: '#00ff00',      // Green
    [ZONE_TYPES.FLOOR_L4]: '#0000ff',         // Blue
    [ZONE_TYPES.WING_L5]: '#ff00ff',          // Magenta
    [ZONE_TYPES.ROOM_L6]: '#8800ff',          // Purple
    [ZONE_TYPES.OUTDOOR_GENERAL]: '#888888',  // Gray
    [ZONE_TYPES.VIRTUAL_SUBJECT]: '#ffff00'   // Yellow
  };

  // Flatten all zones from campus hierarchy
  const allZones = useMemo(() => {
    if (!campusData?.campuses) return [];
    
    const zones = [];
    
    const extractZones = (zoneArray, level = 0, parentPath = []) => {
      zoneArray.forEach(zone => {
        const zonePath = [...parentPath, zone.zone_id];
        const enhancedZone = {
          ...zone,
          level,
          path: zonePath,
          pathString: zonePath.join(' > '),
          regions: regionData[zone.zone_id] || [],
          hasRegions: (regionData[zone.zone_id] || []).length > 0
        };
        
        zones.push(enhancedZone);
        
        if (zone.children && zone.children.length > 0) {
          extractZones(zone.children, level + 1, zonePath);
        }
      });
    };
    
    extractZones(campusData.campuses);
    return zones;
  }, [campusData, regionData]);

  // Group zones by type
  const zonesByType = useMemo(() => {
    const grouped = {
      campus: [],
      building: [],
      floor: [],
      wing: [],
      room: [],
      other: []
    };

    allZones.forEach(zone => {
      switch (zone.zone_type) {
        case ZONE_TYPES.CAMPUS_L1:
          grouped.campus.push(zone);
          break;
        case ZONE_TYPES.BUILDING_L3:
        case ZONE_TYPES.BUILDING_OUTSIDE_L2:
          grouped.building.push(zone);
          break;
        case ZONE_TYPES.FLOOR_L4:
          grouped.floor.push(zone);
          break;
        case ZONE_TYPES.WING_L5:
          grouped.wing.push(zone);
          break;
        case ZONE_TYPES.ROOM_L6:
          grouped.room.push(zone);
          break;
        default:
          grouped.other.push(zone);
          break;
      }
    });

    return grouped;
  }, [allZones]);

  // Zone statistics
  const zoneStats = useMemo(() => {
    return {
      campus: zonesByType.campus.length,
      building: zonesByType.building.length,
      floor: zonesByType.floor.length,
      wing: zonesByType.wing.length,
      room: zonesByType.room.length,
      other: zonesByType.other.length,
      total: allZones.length,
      withRegions: allZones.filter(z => z.hasRegions).length
    };
  }, [zonesByType, allZones]);

  // Get visible zones based on current visibility settings
  const visibleZones = useMemo(() => {
    return allZones.filter(zone => {
      switch (zone.zone_type) {
        case ZONE_TYPES.CAMPUS_L1:
          return zoneVisibility.campus;
        case ZONE_TYPES.BUILDING_L3:
        case ZONE_TYPES.BUILDING_OUTSIDE_L2:
          return zoneVisibility.building;
        case ZONE_TYPES.FLOOR_L4:
          return zoneVisibility.floor;
        case ZONE_TYPES.WING_L5:
          return zoneVisibility.wing;
        case ZONE_TYPES.ROOM_L6:
          return zoneVisibility.room;
        default:
          return true; // Always show other types
      }
    });
  }, [allZones, zoneVisibility]);

  // Zone hierarchy tree (maintains parent-child relationships)
  const zoneTree = useMemo(() => {
    if (!campusData?.campuses) return [];
    
    const enhanceZoneTree = (zones, level = 0) => {
      return zones.map(zone => ({
        ...zone,
        level,
        regions: regionData[zone.zone_id] || [],
        hasRegions: (regionData[zone.zone_id] || []).length > 0,
        children: zone.children ? enhanceZoneTree(zone.children, level + 1) : []
      }));
    };
    
    return enhanceZoneTree(campusData.campuses);
  }, [campusData, regionData]);

  // Helper functions
  const getZoneById = (zoneId) => {
    return allZones.find(zone => zone.zone_id === zoneId);
  };

  const getZonesByParent = (parentId) => {
    return allZones.filter(zone => zone.parent_zone_id === parentId);
  };

  const getZoneChildren = (zoneId) => {
    const zone = getZoneById(zoneId);
    return zone?.children || [];
  };

  const getZonePath = (zoneId) => {
    const zone = getZoneById(zoneId);
    if (!zone) return [];
    
    const path = [];
    let current = zone;
    
    while (current) {
      path.unshift(current);
      current = current.parent_zone_id ? getZoneById(current.parent_zone_id) : null;
    }
    
    return path;
  };

  const getZoneDepth = (zoneId) => {
    const path = getZonePath(zoneId);
    return path.length - 1;
  };

  const isZoneExpanded = (zoneId) => {
    return expandedZones.has(zoneId);
  };

  const toggleZoneExpansion = (zoneId) => {
    setExpandedZones(prev => {
      const next = new Set(prev);
      if (next.has(zoneId)) {
        next.delete(zoneId);
      } else {
        next.add(zoneId);
      }
      return next;
    });
  };

  const expandAllZones = () => {
    const allZoneIds = allZones.map(z => z.zone_id);
    setExpandedZones(new Set(allZoneIds));
  };

  const collapseAllZones = () => {
    setExpandedZones(new Set());
  };

  const toggleZoneTypeVisibility = (zoneType) => {
    setZoneVisibility(prev => ({
      ...prev,
      [zoneType]: !prev[zoneType]
    }));
  };

  const showAllZoneTypes = () => {
    setZoneVisibility({
      campus: true,
      building: true,
      floor: true,
      wing: true,
      room: true
    });
  };

  const hideAllZoneTypes = () => {
    setZoneVisibility({
      campus: false,
      building: false,
      floor: false,
      wing: false,
      room: false
    });
  };

  const selectZone = (zoneId) => {
    const path = getZonePath(zoneId);
    setSelectedZonePath(path.map(z => z.zone_id));
    
    // Auto-expand parents
    path.forEach(zone => {
      if (zone.parent_zone_id) {
        setExpandedZones(prev => new Set([...prev, zone.parent_zone_id]));
      }
    });
  };

  const getZoneTypeLabel = (zoneType) => {
    return ZONE_TYPE_LABELS[zoneType] || `Type ${zoneType}`;
  };

  const getZoneTypeColor = (zoneType) => {
    return ZONE_TYPE_COLORS[zoneType] || '#666666';
  };

  const isZoneVisible = (zone) => {
    return visibleZones.includes(zone);
  };

  // Auto-expand first level on load
  useEffect(() => {
    if (allZones.length > 0 && expandedZones.size === 0) {
      const topLevelZones = allZones.filter(z => z.level === 0);
      setExpandedZones(new Set(topLevelZones.map(z => z.zone_id)));
    }
  }, [allZones, expandedZones.size]);

  return {
    // Data
    allZones,
    zonesByType,
    visibleZones,
    zoneTree,
    zoneStats,
    
    // State
    expandedZones,
    selectedZonePath,
    zoneVisibility,
    
    // Zone queries
    getZoneById,
    getZonesByParent,
    getZoneChildren,
    getZonePath,
    getZoneDepth,
    
    // Zone expansion
    isZoneExpanded,
    toggleZoneExpansion,
    expandAllZones,
    collapseAllZones,
    
    // Zone visibility
    toggleZoneTypeVisibility,
    showAllZoneTypes,
    hideAllZoneTypes,
    isZoneVisible,
    
    // Zone selection
    selectZone,
    
    // Utilities
    getZoneTypeLabel,
    getZoneTypeColor,
    
    // Constants
    ZONE_TYPES,
    ZONE_TYPE_LABELS,
    ZONE_TYPE_COLORS
  };
};

export default useZoneHierarchy;