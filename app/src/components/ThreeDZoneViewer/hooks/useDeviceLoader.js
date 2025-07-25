/* Name: useDeviceLoader.js */
/* Version: 0.1.0 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: React hook for loading and managing devices from API */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend Hook */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useCallback, useEffect, useRef } from 'react';
import DeviceApi from '../services/deviceApi.js';
import { categorizeDevice, sortDevicesByPriority, getDeviceStatsByCategory } from '../utils/deviceCategorization.js';

/**
 * Hook for loading and managing device data
 * @param {Object} options - Hook options
 * @param {Array<number>} options.deviceTypes - Device type IDs to load
 * @param {Array} options.availableDeviceTypes - Device type metadata
 * @param {boolean} options.autoLoad - Auto-load when device types change
 * @param {number} options.cacheTimeout - Cache timeout in milliseconds
 * @returns {Object} Device loading state and functions
 */
export const useDeviceLoader = ({
  deviceTypes = [],
  availableDeviceTypes = [],
  autoLoad = true,
  cacheTimeout = 300000 // 5 minutes
} = {}) => {
  console.log(`📱 useDeviceLoader: Initializing for types [${deviceTypes.join(', ')}]`);
  
  // Device state
  const [devices, setDevices] = useState([]);
  const [devicesByType, setDevicesByType] = useState({});
  const [devicesByCategory, setDevicesByCategory] = useState({});
  
  // Loading and error state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [lastLoadTime, setLastLoadTime] = useState(null);
  
  // Statistics
  const [stats, setStats] = useState({
    totalDevices: 0,
    deviceTypeBreakdown: {},
    categoryBreakdown: {},
    loadedTypes: 0,
    failedTypes: []
  });
  
  // Cache management
  const cacheRef = useRef(new Map());
  const loadingRef = useRef(new Set());
  
  /**
   * Load devices for specified device types
   * @param {Array<number>} typeIds - Device type IDs to load
   * @param {boolean} forceRefresh - Skip cache and force refresh
   */
  const loadDevices = useCallback(async (typeIds = deviceTypes, forceRefresh = false) => {
    if (!Array.isArray(typeIds) || typeIds.length === 0) {
      console.log(`📱 No device types specified, clearing devices`);
      setDevices([]);
      setDevicesByType({});
      setDevicesByCategory({});
      setStats(prev => ({ ...prev, totalDevices: 0, loadedTypes: 0 }));
      return;
    }
    
    setLoading(true);
    setError(null);
    const loadStartTime = Date.now();
    
    try {
      console.log(`📱 Loading devices for types: [${typeIds.join(', ')}]`);
      
      // Check cache for non-expired data
      const cachedData = [];
      const typesToLoad = [];
      
      if (!forceRefresh) {
        typeIds.forEach(typeId => {
          const cached = cacheRef.current.get(typeId);
          if (cached && (loadStartTime - cached.timestamp) < cacheTimeout) {
            console.log(`📱 Using cached data for type ${typeId} (${cached.devices.length} devices)`);
            cachedData.push(...cached.devices);
          } else {
            typesToLoad.push(typeId);
          }
        });
      } else {
        typesToLoad.push(...typeIds);
      }
      
      // Load fresh data for non-cached types
      let freshDevices = [];
      const failedTypes = [];
      
      if (typesToLoad.length > 0) {
        console.log(`📱 Loading fresh data for types: [${typesToLoad.join(', ')}]`);
        
        // Prevent concurrent loading of same types
        const alreadyLoading = typesToLoad.filter(typeId => loadingRef.current.has(typeId));
        if (alreadyLoading.length > 0) {
          console.log(`📱 Already loading types: [${alreadyLoading.join(', ')}], skipping duplicates`);
        }
        
        const toLoad = typesToLoad.filter(typeId => !loadingRef.current.has(typeId));
        toLoad.forEach(typeId => loadingRef.current.add(typeId));
        
        try {
          freshDevices = await DeviceApi.getDevicesByTypes(toLoad);
          
          // Cache the loaded data by type
          const devicesByTypeId = {};
          freshDevices.forEach(device => {
            const typeId = device.deviceTypeId;
            if (!devicesByTypeId[typeId]) {
              devicesByTypeId[typeId] = [];
            }
            devicesByTypeId[typeId].push(device);
          });
          
          // Update cache
          Object.entries(devicesByTypeId).forEach(([typeId, typeDevices]) => {
            cacheRef.current.set(parseInt(typeId), {
              devices: typeDevices,
              timestamp: loadStartTime
            });
          });
          
          console.log(`✅ Loaded ${freshDevices.length} fresh devices`);
          
        } catch (err) {
          console.error(`❌ Error loading devices:`, err);
          toLoad.forEach(typeId => failedTypes.push(typeId));
        } finally {
          toLoad.forEach(typeId => loadingRef.current.delete(typeId));
        }
      }
      
      // Combine cached and fresh data
      const allDevices = [...cachedData, ...freshDevices];
      
      // Enhance devices with categorization
      const enhancedDevices = allDevices.map(device => {
        const deviceTypeInfo = availableDeviceTypes.find(dt => dt.i_typ_dev === device.deviceTypeId);
        return categorizeDevice(device, deviceTypeInfo);
      });
      
      // Sort devices by priority
      const sortedDevices = sortDevicesByPriority(enhancedDevices);
      
      // Group by type
      const byType = {};
      sortedDevices.forEach(device => {
        const typeId = device.deviceTypeId;
        if (!byType[typeId]) {
          byType[typeId] = [];
        }
        byType[typeId].push(device);
      });
      
      // Group by category
      const byCategory = {};
      sortedDevices.forEach(device => {
        const category = device.deviceCategory;
        if (!byCategory[category]) {
          byCategory[category] = [];
        }
        byCategory[category].push(device);
      });
      
      // Calculate statistics
      const typeBreakdown = {};
      typeIds.forEach(typeId => {
        const typeDevices = byType[typeId] || [];
        const typeInfo = availableDeviceTypes.find(dt => dt.i_typ_dev === typeId);
        typeBreakdown[typeId] = {
          count: typeDevices.length,
          description: typeInfo?.x_dsc_dev || `Type ${typeId}`,
          loaded: !failedTypes.includes(typeId)
        };
      });
      
      const categoryBreakdown = getDeviceStatsByCategory(sortedDevices);
      
      const newStats = {
        totalDevices: sortedDevices.length,
        deviceTypeBreakdown: typeBreakdown,
        categoryBreakdown: categoryBreakdown,
        loadedTypes: typeIds.length - failedTypes.length,
        failedTypes: failedTypes
      };
      
      // Update state
      setDevices(sortedDevices);
      setDevicesByType(byType);
      setDevicesByCategory(byCategory);
      setStats(newStats);
      setLastLoadTime(loadStartTime);
      
      const loadTime = Date.now() - loadStartTime;
      console.log(`✅ Loaded ${sortedDevices.length} devices in ${loadTime}ms:`, newStats);
      
    } catch (err) {
      console.error(`❌ Error in loadDevices:`, err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [deviceTypes, availableDeviceTypes, cacheTimeout]);
  
  /**
   * Refresh device data (force reload from API)
   */
  const refreshDevices = useCallback(() => {
    console.log(`🔄 Refreshing device data...`);
    return loadDevices(deviceTypes, true);
  }, [loadDevices, deviceTypes]);
  
  /**
   * Get devices by category
   * @param {string} category - Device category name
   * @returns {Array} Array of devices in category
   */
  const getDevicesByCategory = useCallback((category) => {
    return devicesByCategory[category] || [];
  }, [devicesByCategory]);
  
  /**
   * Get devices by type ID
   * @param {number} typeId - Device type ID
   * @returns {Array} Array of devices of specified type
   */
  const getDevicesByTypeId = useCallback((typeId) => {
    return devicesByType[typeId] || [];
  }, [devicesByType]);
  
  /**
   * Find device by ID
   * @param {string} deviceId - Device ID to find
   * @returns {Object|null} Device object or null if not found
   */
  const findDeviceById = useCallback((deviceId) => {
    return devices.find(device => device.x_id_dev === deviceId) || null;
  }, [devices]);
  
  /**
   * Check if device exists
   * @param {string} deviceId - Device ID to check
   * @returns {boolean} True if device exists
   */
  const deviceExists = useCallback((deviceId) => {
    return devices.some(device => device.x_id_dev === deviceId);
  }, [devices]);
  
  /**
   * Get cache status
   * @returns {Object} Cache information
   */
  const getCacheStatus = useCallback(() => {
    const now = Date.now();
    const cacheEntries = [];
    
    cacheRef.current.forEach((entry, typeId) => {
      const age = now - entry.timestamp;
      const expired = age > cacheTimeout;
      cacheEntries.push({
        typeId,
        deviceCount: entry.devices.length,
        age: Math.round(age / 1000), // seconds
        expired
      });
    });
    
    return {
      entries: cacheEntries,
      totalCached: cacheEntries.reduce((sum, entry) => sum + entry.deviceCount, 0),
      expiredEntries: cacheEntries.filter(entry => entry.expired).length
    };
  }, [cacheTimeout]);
  
  /**
   * Clear cache
   */
  const clearCache = useCallback(() => {
    cacheRef.current.clear();
    console.log(`🧹 Device cache cleared`);
  }, []);
  
  /**
   * Check if data is stale
   * @returns {boolean} True if data should be refreshed
   */
  const isStale = useCallback(() => {
    if (!lastLoadTime) return true;
    return (Date.now() - lastLoadTime) > cacheTimeout;
  }, [lastLoadTime, cacheTimeout]);
  
  // Auto-load when device types change
  useEffect(() => {
    if (autoLoad && deviceTypes.length > 0 && availableDeviceTypes.length > 0) {
      loadDevices(deviceTypes);
    }
  }, [autoLoad, deviceTypes, availableDeviceTypes, loadDevices]);
  
  // Cleanup on unmount
  useEffect(() => {
    return () => {
      console.log(`🧹 useDeviceLoader cleanup`);
      loadingRef.current.clear();
    };
  }, []);
  
  console.log(`📱 useDeviceLoader status:`, {
    devices: devices.length,
    loading,
    error: !!error,
    lastLoad: lastLoadTime ? new Date(lastLoadTime).toLocaleTimeString() : 'Never',
    cache: getCacheStatus().totalCached,
    stats: stats.totalDevices
  });
  
  return {
    // State
    devices,
    devicesByType,
    devicesByCategory,
    loading,
    error,
    stats,
    lastLoadTime,
    
    // Actions
    loadDevices,
    refreshDevices,
    clearCache,
    
    // Getters
    getDevicesByCategory,
    getDevicesByTypeId,
    findDeviceById,
    deviceExists,
    getCacheStatus,
    isStale
  };
};

export default useDeviceLoader;