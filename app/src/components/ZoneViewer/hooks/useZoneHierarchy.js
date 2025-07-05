/* Name: useZoneHierarchy.js */
/* Version: 0.1.3 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Custom hook for zone hierarchy logic */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import { useMemo, useCallback } from "react";

// Move helper functions OUTSIDE the hook to make them stable
const getZoneHierarchyHelper = (zoneId, zones) => {
  const hierarchy = new Set([parseInt(zoneId)]);
  const addChildren = (parentId) => {
    zones.forEach(z => {
      // Check both i_pnt_zn (parent zone) from zones_with_maps and parent_zone_id from hierarchical data
      if (z.i_pnt_zn === parentId || z.parent_zone_id === parentId) {
        hierarchy.add(z.i_zn || z.zone_id);
        addChildren(z.i_zn || z.zone_id);
      }
    });
  };
  addChildren(parseInt(zoneId));
  console.log("Zone hierarchy for", zoneId, ":", Array.from(hierarchy));
  return hierarchy;
};

const findCampusForZoneHelper = (zoneId, zones) => {
  let currentZone = zones.find(z => z.i_zn === parseInt(zoneId));
  while (currentZone && currentZone.i_pnt_zn) {
    currentZone = zones.find(z => z.i_zn === currentZone.i_pnt_zn);
  }
  return currentZone ? currentZone.i_zn : parseInt(zoneId);
};

export const useZoneHierarchy = ({ allZones, zoneType, selectedZone }) => {

  // Use useCallback to create stable function references
  const getZoneHierarchy = useCallback((zoneId, zones) => {
    return getZoneHierarchyHelper(zoneId, zones);
  }, []);

  const findCampusForZone = useCallback((zoneId, zones) => {
    return findCampusForZoneHelper(zoneId, zones);
  }, []);

  // Filter zones by selected zone type - EXACT MATCH ONLY
  const filteredZones = useMemo(() => {
    return allZones.filter(z => {
      if (!zoneType) return true; // Show all if no zone type selected
      return z.i_typ_zn === parseInt(zoneType); // Show only zones of the selected type
    });
  }, [allZones, zoneType]);

  // Get selected zone data
  const selectedZoneData = useMemo(() => {
    return allZones.find(z => z.i_zn === parseInt(selectedZone));
  }, [allZones, selectedZone]);

  // Get available maps in the zone hierarchy
  const availableMaps = useMemo(() => {
    if (!selectedZone || !allZones.length) return [];

    // Get the zone hierarchy (selected zone + all children)
    const hierarchy = getZoneHierarchyHelper(selectedZone, allZones);
    
    // Also walk up to parent zones to include their maps
    const allRelatedZones = new Set(hierarchy);
    let currentZone = selectedZoneData;
    while (currentZone && currentZone.i_pnt_zn) {
      allRelatedZones.add(currentZone.i_pnt_zn);
      currentZone = allZones.find(z => z.i_zn === currentZone.i_pnt_zn);
    }

    // Find all zones with maps in the hierarchy
    const zonesWithMaps = allZones
      .filter(z => allRelatedZones.has(z.i_zn) && z.i_map)
      .map(z => ({
        mapId: z.i_map,
        zoneId: z.i_zn,
        zoneName: z.x_nm_zn,
        zoneType: z.i_typ_zn
      }))
      .sort((a, b) => a.zoneType - b.zoneType); // Sort by zone type (Campus first, then Building, etc.)

    console.log("Available maps for zone hierarchy:", zonesWithMaps);
    return zonesWithMaps;
  }, [selectedZone, selectedZoneData, allZones]);

  // Zone type name lookup
  const getZoneTypeName = useCallback((typeId) => {
    const typeNames = {
      1: "Campus",
      2: "Building", 
      3: "Floor",
      4: "Wing",
      5: "Room",
      10: "Area"
    };
    return typeNames[typeId] || `Type ${typeId}`;
  }, []);

  // Get zone hierarchy for display
  const getZoneHierarchyDisplay = useCallback((zoneId) => {
    if (!zoneId || !allZones.length) return [];
    
    const hierarchy = [];
    let currentZone = allZones.find(z => z.i_zn === parseInt(zoneId));
    
    while (currentZone) {
      hierarchy.unshift({
        id: currentZone.i_zn,
        name: currentZone.x_nm_zn,
        type: getZoneTypeName(currentZone.i_typ_zn)
      });
      currentZone = currentZone.i_pnt_zn ? 
        allZones.find(z => z.i_zn === currentZone.i_pnt_zn) : null;
    }
    
    return hierarchy;
  }, [allZones, getZoneTypeName]);

  // Get children zones
  const getChildZones = useCallback((parentId) => {
    return allZones.filter(z => z.i_pnt_zn === parseInt(parentId));
  }, [allZones]);

  // Check if zone has children
  const hasChildren = useCallback((zoneId) => {
    return allZones.some(z => z.i_pnt_zn === parseInt(zoneId));
  }, [allZones]);

  // Get zone depth (how many levels from campus)
  const getZoneDepth = useCallback((zoneId) => {
    let depth = 0;
    let currentZone = allZones.find(z => z.i_zn === parseInt(zoneId));
    
    while (currentZone && currentZone.i_pnt_zn) {
      depth++;
      currentZone = allZones.find(z => z.i_zn === currentZone.i_pnt_zn);
    }
    
    return depth;
  }, [allZones]);

  return {
    getZoneHierarchy,
    findCampusForZone,
    filteredZones,
    selectedZoneData,
    availableMaps,
    getZoneTypeName,
    getZoneHierarchyDisplay,
    getChildZones,
    hasChildren,
    getZoneDepth
  };
};