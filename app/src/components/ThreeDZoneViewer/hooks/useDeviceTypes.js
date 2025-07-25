/* Name: useDeviceTypes.js */
/* Version: 0.1.0 */
/* Created: 250724 */
/* Modified: 250724 */
/* Creator: ParcoAdmin + Claude */
/* Description: React hook for device type management and selection */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/hooks */
/* Role: Frontend Hook */
/* Status: Active */
/* Dependent: TRUE */

import { useState, useCallback, useEffect } from 'react';
import DeviceTypeApi from '../services/deviceTypeApi.js';

/**
 * Hook for managing device types and selection
 * @param {Object} options - Hook options
 * @param {Array<number>} options.initialSelectedTypes - Initial device type IDs to select
 * @param {boolean} options.autoLoad - Automatically load device types on mount
 * @returns {Object} Device type management state and functions
 */
export const useDeviceTypes = ({
  initialSelectedTypes = [27], // Default to AllTraq
  autoLoad = true
} = {}) => {
  console.log(`📋 useDeviceTypes: Initializing with types [${initialSelectedTypes.join(', ')}]`);
  
  // Device type state
  const [availableDeviceTypes, setAvailableDeviceTypes] = useState([]);
  const [selectedDeviceTypes, setSelectedDeviceTypes] = useState(initialSelectedTypes);
  const [categorizedDeviceTypes, setCategorizedDeviceTypes] = useState({});
  
  // Loading and error state
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Statistics
  const [stats, setStats] = useState({
    total: 0,
    selected: initialSelectedTypes.length,
    tracking: 0,
    infrastructure: 0,
    equipment: 0,
    other: 0
  });
  
  /**
   * Load available device types from API
   */
  const loadDeviceTypes = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      console.log(`📋 Loading device types from API...`);
      
      // Load both basic types and categorized types
      const [deviceTypes, categorized] = await Promise.all([
        DeviceTypeApi.getDeviceTypes(),
        DeviceTypeApi.getCategorizedDeviceTypes()
      ]);
      
      setAvailableDeviceTypes(deviceTypes);
      setCategorizedDeviceTypes(categorized);
      
      // Update statistics
      const newStats = {
        total: deviceTypes.length,
        selected: selectedDeviceTypes.length,
        tracking: categorized.tracking?.length || 0,
        infrastructure: categorized.infrastructure?.length || 0,
        equipment: categorized.equipment?.length || 0,
        other: categorized.other?.length || 0
      };
      setStats(newStats);
      
      console.log(`✅ Loaded ${deviceTypes.length} device types:`, newStats);
      
    } catch (err) {
      console.error(`❌ Error loading device types:`, err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [selectedDeviceTypes.length]);
  
  /**
   * Select/deselect a device type
   * @param {number} deviceTypeId - Device type ID to toggle
   */
  const toggleDeviceType = useCallback((deviceTypeId) => {
    setSelectedDeviceTypes(prev => {
      const isSelected = prev.includes(deviceTypeId);
      const newSelection = isSelected
        ? prev.filter(id => id !== deviceTypeId)
        : [...prev, deviceTypeId];
      
      console.log(`📋 ${isSelected ? 'Deselected' : 'Selected'} device type ${deviceTypeId}`);
      console.log(`📋 Current selection: [${newSelection.join(', ')}]`);
      
      return newSelection;
    });
  }, []);
  
  /**
   * Set selected device types
   * @param {Array<number>} deviceTypeIds - Array of device type IDs
   */
  const setSelectedTypes = useCallback((deviceTypeIds) => {
    if (!Array.isArray(deviceTypeIds)) {
      console.warn(`⚠️ Invalid device type selection: expected array, got ${typeof deviceTypeIds}`);
      return;
    }
    
    // Validate that all provided IDs exist
    const validIds = deviceTypeIds.filter(id => 
      availableDeviceTypes.some(dt => dt.i_typ_dev === id)
    );
    
    if (validIds.length !== deviceTypeIds.length) {
      const invalidIds = deviceTypeIds.filter(id => !validIds.includes(id));
      console.warn(`⚠️ Invalid device type IDs filtered out: [${invalidIds.join(', ')}]`);
    }
    
    setSelectedDeviceTypes(validIds);
    console.log(`📋 Set device type selection: [${validIds.join(', ')}]`);
  }, [availableDeviceTypes]);
  
  /**
   * Select all device types in a category
   * @param {string} category - Category name (tracking, infrastructure, equipment, other)
   */
  const selectCategory = useCallback((category) => {
    if (!categorizedDeviceTypes[category]) {
      console.warn(`⚠️ Unknown device type category: ${category}`);
      return;
    }
    
    const categoryTypeIds = categorizedDeviceTypes[category].map(dt => dt.i_typ_dev);
    const newSelection = [...new Set([...selectedDeviceTypes, ...categoryTypeIds])];
    
    setSelectedDeviceTypes(newSelection);
    console.log(`📋 Selected ${category} category: ${categoryTypeIds.length} types added`);
  }, [categorizedDeviceTypes, selectedDeviceTypes]);
  
  /**
   * Deselect all device types in a category
   * @param {string} category - Category name
   */
  const deselectCategory = useCallback((category) => {
    if (!categorizedDeviceTypes[category]) {
      console.warn(`⚠️ Unknown device type category: ${category}`);
      return;
    }
    
    const categoryTypeIds = categorizedDeviceTypes[category].map(dt => dt.i_typ_dev);
    const newSelection = selectedDeviceTypes.filter(id => !categoryTypeIds.includes(id));
    
    setSelectedDeviceTypes(newSelection);
    console.log(`📋 Deselected ${category} category: ${categoryTypeIds.length} types removed`);
  }, [categorizedDeviceTypes, selectedDeviceTypes]);
  
  /**
   * Select all available device types
   */
  const selectAll = useCallback(() => {
    const allTypeIds = availableDeviceTypes.map(dt => dt.i_typ_dev);
    setSelectedDeviceTypes(allTypeIds);
    console.log(`📋 Selected all device types: ${allTypeIds.length} types`);
  }, [availableDeviceTypes]);
  
  /**
   * Clear all device type selections
   */
  const selectNone = useCallback(() => {
    setSelectedDeviceTypes([]);
    console.log(`📋 Cleared all device type selections`);
  }, []);
  
  /**
   * Get device types by IDs
   * @param {Array<number>} deviceTypeIds - Array of device type IDs
   * @returns {Array} Array of device type objects
   */
  const getDeviceTypesByIds = useCallback((deviceTypeIds) => {
    if (!Array.isArray(deviceTypeIds)) {
      return [];
    }
    
    return availableDeviceTypes.filter(dt => deviceTypeIds.includes(dt.i_typ_dev));
  }, [availableDeviceTypes]);
  
  /**
   * Get selected device type objects
   * @returns {Array} Array of selected device type objects
   */
  const getSelectedDeviceTypes = useCallback(() => {
    return getDeviceTypesByIds(selectedDeviceTypes);
  }, [getDeviceTypesByIds, selectedDeviceTypes]);
  
  /**
   * Check if a device type is selected
   * @param {number} deviceTypeId - Device type ID to check
   * @returns {boolean} True if selected
   */
  const isSelected = useCallback((deviceTypeId) => {
    return selectedDeviceTypes.includes(deviceTypeId);
  }, [selectedDeviceTypes]);
  
  /**
   * Check if a category is fully selected
   * @param {string} category - Category name
   * @returns {boolean} True if all types in category are selected
   */
  const isCategorySelected = useCallback((category) => {
    if (!categorizedDeviceTypes[category]) {
      return false;
    }
    
    const categoryTypeIds = categorizedDeviceTypes[category].map(dt => dt.i_typ_dev);
    return categoryTypeIds.every(id => selectedDeviceTypes.includes(id));
  }, [categorizedDeviceTypes, selectedDeviceTypes]);
  
  /**
   * Get preset device type selections
   * @returns {Object} Preset selections for common use cases
   */
  const getPresetSelections = useCallback(() => {
    return {
      alltraqOnly: [27],
      trackingDevices: categorizedDeviceTypes.tracking?.map(dt => dt.i_typ_dev) || [],
      commonTracking: [1, 2, 4, 27], // Tag, Tag with Batt, Personnel, AllTraq
      hospitalEquipment: [24, 19, 20, 21, 22], // Carts, Sink, Washer, Autoclave, Cooling Rack
      all: availableDeviceTypes.map(dt => dt.i_typ_dev)
    };
  }, [categorizedDeviceTypes, availableDeviceTypes]);
  
  /**
   * Apply a preset selection
   * @param {string} presetName - Name of preset to apply
   */
  const applyPreset = useCallback((presetName) => {
    const presets = getPresetSelections();
    if (presets[presetName]) {
      setSelectedDeviceTypes(presets[presetName]);
      console.log(`📋 Applied preset '${presetName}': [${presets[presetName].join(', ')}]`);
    } else {
      console.warn(`⚠️ Unknown preset: ${presetName}`);
    }
  }, [getPresetSelections]);
  
  // Update stats when selection changes
  useEffect(() => {
    setStats(prev => ({
      ...prev,
      selected: selectedDeviceTypes.length
    }));
  }, [selectedDeviceTypes.length]);
  
  // Auto-load device types on mount
  useEffect(() => {
    if (autoLoad) {
      loadDeviceTypes();
    }
  }, [autoLoad, loadDeviceTypes]);
  
  console.log(`📋 useDeviceTypes status:`, {
    available: availableDeviceTypes.length,
    selected: selectedDeviceTypes.length,
    loading,
    error: !!error,
    stats
  });
  
  return {
    // State
    availableDeviceTypes,
    selectedDeviceTypes,
    categorizedDeviceTypes,
    loading,
    error,
    stats,
    
    // Actions
    loadDeviceTypes,
    toggleDeviceType,
    setSelectedTypes,
    selectCategory,
    deselectCategory,
    selectAll,
    selectNone,
    applyPreset,
    
    // Getters
    getDeviceTypesByIds,
    getSelectedDeviceTypes,
    isSelected,
    isCategorySelected,
    getPresetSelections
  };
};

export default useDeviceTypes;