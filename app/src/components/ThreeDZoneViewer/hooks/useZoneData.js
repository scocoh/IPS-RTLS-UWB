/* Name: useZoneData.js */
/* Version: 0.1.3 */
/* Created: 250719 */
/* Modified: 250721 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Data fetching hook for 3D zone visualization - CAMPUS-DEPENDENT loading */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.3: CAMPUS-DEPENDENT LOADING - Added campusId parameter, only fetch when campus selected, removed hardcoded defaults */
/* - 0.1.2: Enhanced zone data fetching and processing */

import { useState, useEffect } from 'react';
import { config } from '../../../config';

const useZoneData = ({ 
  fetchCampuses = true, 
  fetchMapData = true, 
  mapId = null,
  campusId = null // NEW v0.1.3: Campus ID parameter - only fetch when provided
}) => {
  const [campusData, setCampusData] = useState(null);
  const [mapData, setMapData] = useState(null);
  const [regionData, setRegionData] = useState({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // NEW v0.1.3: Fetch campus-specific data only when campusId is provided
  useEffect(() => {
    // Reset data when campusId changes
    if (!campusId) {
      setCampusData(null);
      setRegionData({});
      setError(null);
      console.log('🏫 No campus selected - cleared campus data');
      return;
    }

    if (!fetchCampuses) return;

    const fetchCampusData = async () => {
      setLoading(true);
      setError(null);
      
      try {
        console.log(`🏫 Fetching zones for campus ${campusId}...`);
        
        // NEW: Fetch zones specifically for the selected campus
        const response = await fetch(`${config.ZONEVIEWER_API_URL}/get_all_zones_for_campus/${campusId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log(`✅ Campus ${campusId} data fetched:`, data);
        
        // Structure data to match expected format (with campuses array)
        const structuredData = {
          campuses: data.zones || []
        };
        
        setCampusData(structuredData);
        
      } catch (err) {
        console.error(`❌ Error fetching campus ${campusId} data:`, err);
        setError(`Failed to fetch campus data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchCampusData();
  }, [fetchCampuses, campusId]); // NEW: Added campusId dependency

  // Fetch map data when mapId is provided
  useEffect(() => {
    if (!fetchMapData || !mapId) {
      setMapData(null);
      return;
    }

    const fetchMapMetadata = async () => {
      setLoading(true);
      setError(null);
      
      try {
        console.log(`🗺️ Fetching map data for map_id ${mapId}...`);
        const response = await fetch(`${config.ZONEVIEWER_API_URL}/get_map_data/${mapId}`);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        console.log('✅ Map data fetched:', data);
        setMapData(data);
        
      } catch (err) {
        console.error('❌ Error fetching map data:', err);
        setError(`Failed to fetch map data: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    fetchMapMetadata();
  }, [fetchMapData, mapId]);

  // Fetch regions for a specific zone
  const fetchRegionsForZone = async (zoneId) => {
    if (regionData[zoneId]) {
      console.log(`📦 Using cached region data for zone ${zoneId}`);
      return regionData[zoneId];
    }

    setLoading(true);
    setError(null);
    
    try {
      console.log(`🔍 Fetching vertices for zone ${zoneId}...`);
      const response = await fetch(`${config.API_BASE_URL}/zonebuilder/get_zone_vertices/${zoneId}`);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      
      const data = await response.json();
      console.log(`✅ Vertex data fetched for zone ${zoneId}:`, data);
      
      // Cache the vertex data
      const cachedData = data.vertices || [];
      setRegionData(prev => ({
        ...prev,
        [zoneId]: cachedData
      }));
      
      return cachedData;
      
    } catch (err) {
      console.error(`❌ Error fetching vertices for zone ${zoneId}:`, err);
      setError(`Failed to fetch vertices for zone ${zoneId}: ${err.message}`);
      return null;
    } finally {
      setLoading(false);
    }
  };

  // Get all zones flattened from campus hierarchy
  const getAllZones = () => {
    if (!campusData?.campuses) {
      console.log('🚫 No campus data available for getAllZones');
      return [];
    }
    
    const zones = [];
    
    const extractZones = (zoneArray) => {
      zoneArray.forEach(zone => {
        zones.push(zone);
        if (zone.children && zone.children.length > 0) {
          extractZones(zone.children);
        }
      });
    };
    
    extractZones(campusData.campuses);
    console.log(`📊 Extracted ${zones.length} zones from campus ${campusId} data`);
    return zones;
  };

  // Get zones by type
  const getZonesByType = (zoneType) => {
    const allZones = getAllZones();
    const filteredZones = allZones.filter(zone => zone.zone_type === zoneType);
    console.log(`🔍 Found ${filteredZones.length} zones of type ${zoneType} in campus ${campusId}`);
    return filteredZones;
  };

  // Get campus zones (zone_type = 1)
  const getCampusZones = () => getZonesByType(1);

  // Get building zones (zone_type = 2 and 10)
  const getBuildingZones = () => [
    ...getZonesByType(2),  // Building L3
    ...getZonesByType(10)  // Building Outside L2
  ];

  // Get all zones with their hierarchical paths
  const getZonesWithPaths = () => {
    const zones = getAllZones();
    const zoneMap = {};
    
    // Create lookup map
    zones.forEach(zone => {
      zoneMap[zone.zone_id] = zone;
    });
    
    // Build paths
    return zones.map(zone => {
      const path = [];
      let current = zone;
      
      while (current) {
        path.unshift(current.zone_name);
        current = current.parent_zone_id ? zoneMap[current.parent_zone_id] : null;
      }
      
      return {
        ...zone,
        path: path.join(' > '),
        pathArray: path
      };
    });
  };

  // NEW v0.1.3: Check if data is available (campus selected and loaded)
  const hasData = () => {
    return !!campusId && !!campusData;
  };

  // NEW v0.1.3: Get current campus info
  const getCurrentCampusInfo = () => {
    if (!campusId || !campusData) return null;
    
    const campusZones = getCampusZones();
    const campusZone = campusZones.find(z => z.zone_id === campusId);
    
    return campusZone ? {
      id: campusZone.zone_id,
      name: campusZone.zone_name,
      mapId: campusZone.map_id,
      zoneType: campusZone.zone_type
    } : null;
  };

  // Debug logging for campus changes
  console.log(`🔍 useZoneData v0.1.3 Debug:`, {
    campusId,
    hasCampusData: !!campusData,
    hasMapData: !!mapData,
    totalZones: getAllZones().length,
    loading,
    error: error ? 'Present' : 'None'
  });

  return {
    // Data
    campusData,
    mapData,
    regionData,
    
    // Status
    loading,
    error,
    hasData: hasData(), // NEW: Convenience method
    
    // Actions
    fetchRegionsForZone,
    
    // Computed data
    getAllZones,
    getZonesByType,
    getCampusZones,
    getBuildingZones,
    getZonesWithPaths,
    getCurrentCampusInfo, // NEW: Campus info helper
    
    // Raw data for debugging
    totalZones: getAllZones().length,
    campusCount: getCampusZones().length,
    buildingCount: getBuildingZones().length,
    
    // NEW v0.1.3: Campus-specific info
    selectedCampusId: campusId,
    isDataLoaded: hasData()
  };
};

export default useZoneData;