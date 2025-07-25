/* Name: useRealTimeTags.js */
/* Version: 0.2.1 */
/* Created: 250722 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: MODULAR VERSION - Main hook orchestrating device types, loading, and WebSocket connection - FIXED auto-select tags */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend Hook */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.2.1: FIXED auto-select tags for display - tags now automatically selected when processed */
/* - 0.2.0: MODULAR REFACTOR - Split into focused sub-hooks and utilities */

import { useState, useCallback, useEffect, useRef } from 'react';
import { useDeviceTypes } from './useDeviceTypes.js';
import { useDeviceLoader } from './useDeviceLoader.js';
import { useWebSocketConnection } from './useWebSocketConnection.js';
import TagDataProcessor from '../utils/tagDataProcessor.js';
import { DEVICE_CATEGORIES } from '../utils/deviceCategorization.js';

/**
 * Main hook for real-time tag management (modular version)
 * @param {Object} options - Hook options
 * @param {number} options.selectedCampusId - Selected campus zone ID
 * @param {boolean} options.isEnabled - Enable real-time connection
 * @param {Array<number>} options.selectedDeviceTypes - Device type IDs to track
 * @param {Function} options.onConnectionChange - Connection change callback
 * @param {Function} options.onTagUpdate - Tag update callback
 * @param {number} options.maxTagHistory - Maximum tag history length
 * @returns {Object} Real-time tags state and functions
 */
export const useRealTimeTags = ({
  selectedCampusId = null,
  isEnabled = false,
  selectedDeviceTypes = [27], // Default to AllTraq
  onConnectionChange = null,
  onTagUpdate = null,
  maxTagHistory = 50
} = {}) => {
  console.log(`🏷️ useRealTimeTags v0.2.1: Modular version initializing with auto-select fix`);
  
  // Tag data state
  const [allTagsData, setAllTagsData] = useState({});
  const [selectedTags, setSelectedTags] = useState(new Set());
  const [tagHistory, setTagHistory] = useState({});
  
  // Zone-categorized data
  const [alltraqTags, setAlltraqTags] = useState({});
  const [campusTags, setCampusTags] = useState({});
  const [otherTags, setOtherTags] = useState({});
  
  // Processing state
  const lastUpdateTime = useRef(0);
  const tagTimestamps = useRef([]);
  
  // Device type management
  const {
    availableDeviceTypes,
    selectedDeviceTypes: currentDeviceTypes,
    setSelectedTypes,
    loading: deviceTypesLoading,
    error: deviceTypesError,
    stats: deviceTypeStats
  } = useDeviceTypes({
    initialSelectedTypes: selectedDeviceTypes,
    autoLoad: true
  });
  
  // Device loading
  const {
    devices: availableDevices,
    loading: devicesLoading,
    error: devicesError,
    stats: deviceStats,
    refreshDevices
  } = useDeviceLoader({
    deviceTypes: currentDeviceTypes,
    availableDeviceTypes: availableDeviceTypes,
    autoLoad: true
  });
  
  /**
   * Handle incoming GIS data messages - FIXED v0.2.1: Auto-select tags for display
   */
  const handleGISMessage = useCallback((data) => {
    const processed = TagDataProcessor.processGISData(data, {
      availableDevices,
      selectedCampusId,
      lastUpdateTime: lastUpdateTime.current
    });
    
    if (!processed) return;
    
    lastUpdateTime.current = Date.now();
    
    // Update all tags data
    setAllTagsData(prev => ({
      ...prev,
      [processed.id]: processed
    }));
    
    // FIXED v0.2.1: AUTO-SELECT TAGS FOR DISPLAY - This was the missing piece!
    setSelectedTags(prev => new Set([...prev, processed.id]));
    
    // Update zone-categorized data
    if (processed.category === DEVICE_CATEGORIES.ALLTRAQ) {
      setAlltraqTags(prev => ({
        ...prev,
        [processed.id]: processed
      }));
    } else if (processed.category === DEVICE_CATEGORIES.CAMPUS) {
      setCampusTags(prev => ({
        ...prev,
        [processed.id]: processed
      }));
    } else {
      setOtherTags(prev => ({
        ...prev,
        [processed.id]: processed
      }));
    }
    
    // Update tag history
    setTagHistory(prev => {
      const currentHistory = prev[processed.id] || [];
      const updatedHistory = TagDataProcessor.updateTagHistory(
        processed, 
        currentHistory, 
        maxTagHistory
      );
      
      return {
        ...prev,
        [processed.id]: updatedHistory
      };
    });
    
    // Track timestamps for rate calculation
    tagTimestamps.current.push(Date.now());
    if (tagTimestamps.current.length > 100) {
      tagTimestamps.current = tagTimestamps.current.slice(-100);
    }
    
    // External callback
    if (onTagUpdate) {
      onTagUpdate(processed);
    }
  }, [availableDevices, selectedCampusId, maxTagHistory, onTagUpdate]);
  
  // WebSocket connection
  const {
    isConnected,
    connectionStatus,
    lastDataTime,
    stats: connectionStats,
    connect,
    disconnect
  } = useWebSocketConnection({
    enabled: isEnabled,
    devices: availableDevices,
    selectedCampusId: selectedCampusId,
    onMessage: handleGISMessage,
    onConnectionChange: onConnectionChange,
    enableAlltraqFiltering: true
  });
  
  // Tag selection management
  const toggleTagSelection = useCallback((tagId) => {
    setSelectedTags(prev => {
      const updated = new Set(prev);
      if (updated.has(tagId)) {
        updated.delete(tagId);
      } else {
        updated.add(tagId);
      }
      return updated;
    });
  }, []);
  
  const selectAllTags = useCallback(() => {
    const allTagIds = Object.keys(allTagsData);
    setSelectedTags(new Set(allTagIds));
  }, [allTagsData]);
  
  const selectAlltraqTags = useCallback(() => {
    const alltraqTagIds = Object.keys(alltraqTags);
    setSelectedTags(prev => new Set([...prev, ...alltraqTagIds]));
  }, [alltraqTags]);
  
  const selectCampusTags = useCallback(() => {
    const campusTagIds = Object.keys(campusTags);
    setSelectedTags(prev => new Set([...prev, ...campusTagIds]));
  }, [campusTags]);
  
  const selectOtherTags = useCallback(() => {
    const otherTagIds = Object.keys(otherTags);
    setSelectedTags(prev => new Set([...prev, ...otherTagIds]));
  }, [otherTags]);
  
  const clearTagSelection = useCallback(() => {
    setSelectedTags(new Set());
  }, []);
  
  // Get display tags
  const getDisplayTags = useCallback(() => {
    return TagDataProcessor.getDisplayTags(allTagsData, selectedTags);
  }, [allTagsData, selectedTags]);
  
  const getDisplayAlltraqTags = useCallback(() => {
    return TagDataProcessor.getDisplayTags(alltraqTags, selectedTags);
  }, [alltraqTags, selectedTags]);
  
  // Calculate comprehensive statistics
  const getTagStats = useCallback(() => {
    const now = Date.now();
    const windowStart = now - 10000; // 10 second window
    const recentTimestamps = tagTimestamps.current.filter(ts => ts >= windowStart);
    const timeSpan = recentTimestamps.length > 1 ? 
      (recentTimestamps[recentTimestamps.length - 1] - recentTimestamps[0]) / 1000 : 0;
    const tagRate = timeSpan > 0 ? (recentTimestamps.length - 1) / timeSpan : 0;
    
    return {
      totalTags: Object.keys(allTagsData).length,
      activeTags: Object.values(allTagsData).filter(tag => tag.isActive).length,
      tagRate: tagRate,
      lastUpdateTime: lastDataTime,
      alltraqCount: Object.keys(alltraqTags).length,
      campusCount: Object.keys(campusTags).length,
      otherCount: Object.keys(otherTags).length,
      selectedCount: selectedTags.size,
      deviceTypeBreakdown: deviceStats.deviceTypeBreakdown,
      availableDevicesCount: availableDevices.length
    };
  }, [allTagsData, alltraqTags, campusTags, otherTags, selectedTags, lastDataTime, deviceStats, availableDevices]);
  
  // Update device type selection
  useEffect(() => {
    if (JSON.stringify(currentDeviceTypes) !== JSON.stringify(selectedDeviceTypes)) {
      setSelectedTypes(selectedDeviceTypes);
    }
  }, [selectedDeviceTypes, currentDeviceTypes, setSelectedTypes]);
  
  // Cleanup stale data periodically
  useEffect(() => {
    const cleanup = () => {
      setAllTagsData(prev => TagDataProcessor.cleanupStaleData(prev, 300000)); // 5 minutes
    };
    
    const interval = setInterval(cleanup, 60000); // Every minute
    return () => clearInterval(interval);
  }, []);
  
  console.log(`🏷️ useRealTimeTags v0.2.1 status:`, {
    isConnected,
    connectionStatus,
    totalTags: Object.keys(allTagsData).length,
    selectedTags: selectedTags.size,
    availableDevices: availableDevices.length,
    selectedDeviceTypes: currentDeviceTypes.length,
    loading: deviceTypesLoading || devicesLoading
  });
  
  return {
    // Connection state
    isConnected,
    connectionStatus,
    
    // Tag data
    allTagsData,
    displayTags: getDisplayTags(),
    tagHistory,
    tagStats: getTagStats(),
    
    // Zone-categorized data
    alltraqTags,
    campusTags,
    otherTags,
    displayAlltraqTags: getDisplayAlltraqTags(),
    
    // Device management
    availableDevices,
    availableDeviceTypes,
    deviceTypeStats,
    devicesLoading: devicesLoading || deviceTypesLoading,
    devicesError: devicesError || deviceTypesError,
    refreshDevices,
    
    // Tag selection
    selectedTags,
    toggleTagSelection,
    selectAllTags,
    selectAlltraqTags,
    selectCampusTags,
    selectOtherTags,
    clearTagSelection,
    
    // Device type management
    selectedDeviceTypes: currentDeviceTypes,
    setSelectedDeviceTypes: setSelectedTypes,
    
    // Connection controls
    connect,
    disconnect
  };
};

export default useRealTimeTags;