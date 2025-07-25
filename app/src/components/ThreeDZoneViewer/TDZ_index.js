/* Name: TDZ_index.js */
/* Version: 0.3.0 */
/* Created: 250719 */
/* Modified: 250725 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: FULLY MODULAR VERSION - Refactored into separate components to reduce complexity */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.3.0: FULL MODULAR REFACTOR - Split into StatusPanel, CampusControls, ZoneControls components */
/* - 0.2.2: ADDED collapsible database debug panel for validation before WebSocket integration */
/* - 0.2.0: MODULAR INTEGRATION - Updated to use new modular hook system with device type selection */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import Scene3D from './components/Scene3D';
import ZoneControlsSidebar from './components/ZoneControlsSidebar';
import StatusPanel from './components/StatusPanel';
import CampusControls from './components/CampusControls';
import DatabaseDebugPanel from './components/DatabaseDebugPanel';
import useZoneData from './hooks/useZoneData';
import { useRealTimeTags } from './hooks/useRealTimeTags';
import {
  fetchCampusHierarchy,
  calculateHierarchyOpacity,
  getHierarchyColor,
  getCascadeHiddenZones,
  generateHierarchySettings
} from './utils/hierarchyUtils';
import { DEFAULT_TAG_CONFIG } from './utils/tagRenderingUtils';
import './styles/ThreeDZoneViewer.css';

const TDZ_index = () => {
  console.log(`🚀 TDZ_index v0.3.0: Fully modular version with separated components`);

  // ==================== CORE STATE ====================
  
  // Campus and zone selection state
  const [selectedCampusId, setSelectedCampusId] = useState(null);
  const [selectedCampusName, setSelectedCampusName] = useState("");
  const [selectedZoneType, setSelectedZoneType] = useState(1);
  const [selectedZone, setSelectedZone] = useState("");
  const [selectedMapId, setSelectedMapId] = useState(null);
  const [showCampusZone, setShowCampusZone] = useState(false);
  const [checkedZones, setCheckedZones] = useState([]);
  const [zoneSettings, setZoneSettings] = useState({});
  
  // UI toggle states
  const [showSidebar, setShowSidebar] = useState(true);
  const [showDebugOverlays, setShowDebugOverlays] = useState(true);
  const [showControlsHint, setShowControlsHint] = useState(true);
  const [showDatabaseDebug, setShowDatabaseDebug] = useState(false);
  const [showZoneLabels, setShowZoneLabels] = useState(false);
  const [showCornerMarkers, setShowCornerMarkers] = useState(false);
  const [selectedMapFilter, setSelectedMapFilter] = useState('all');
  
  // Hierarchy controls
  const [useHierarchyTransparency, setUseHierarchyTransparency] = useState(true);
  const [useCascadeVisibility, setUseCascadeVisibility] = useState(true);
  const [hierarchyData, setHierarchyData] = useState(null);
  const [hierarchyLoading, setHierarchyLoading] = useState(false);
  
  // Campus data
  const [availableCampuses, setAvailableCampuses] = useState([]);
  const [campusesLoading, setCampusesLoading] = useState(false);
  
  // Tag system state
  const [tagConnectionEnabled, setTagConnectionEnabled] = useState(false);
  const [selectedTagDeviceTypes, setSelectedTagDeviceTypes] = useState([27]);
  const [tagConfig, setTagConfig] = useState({
    ...DEFAULT_TAG_CONFIG,
    showLabels: true,
    showTrails: false,
    sphereRadius: 3,
    activeColor: '#00ff00',
    useActualHeight: true,
    minHeightAboveGround: 2,
    alltraqColor: '#ff4400',
    campusColor: '#00ff00',
    showAlltraqSeparately: true
  });
  const [showTags, setShowTags] = useState(true);

  // ==================== HOOKS ====================
  
  // Real-time tags hook
  const {
    isConnected: tagIsConnected,
    connectionStatus: tagConnectionStatus,
    allTagsData,
    displayTags,
    tagHistory,
    tagStats,
    selectedTags,
    alltraqTags,
    campusTags,
    otherTags,
    displayAlltraqTags,
    availableDevices,
    availableDeviceTypes,
    deviceTypeStats,
    devicesLoading,
    devicesError,
    refreshDevices,
    toggleTagSelection,
    selectAllTags,
    selectAlltraqTags,
    selectCampusTags,
    selectOtherTags,
    clearTagSelection,
    selectedDeviceTypes,
    setSelectedDeviceTypes,
    connect: connectTags,
    disconnect: disconnectTags
  } = useRealTimeTags({
    selectedCampusId,
    isEnabled: tagConnectionEnabled,
    selectedDeviceTypes: selectedTagDeviceTypes,
    onConnectionChange: (connected, status) => {
      console.log(`🔌 Tag connection changed: ${connected ? 'connected' : 'disconnected'} (${status})`);
    },
    onTagUpdate: (tagData) => {
      console.log(`📍 Tag update: ${tagData.id} (${tagData.deviceName}) at (${tagData.x.toFixed(2)}, ${tagData.y.toFixed(2)}, ${tagData.z.toFixed(2)}) [${tagData.category}]`);
    },
    maxTagHistory: 20
  });

  // Zone data hook
  const {
    campusData,
    mapData,
    loading,
    error,
    getCampusZones,
    getBuildingZones,
    getAllZones,
    getZonesByType,
    totalZones,
    campusCount,
    buildingCount
  } = useZoneData({
    fetchCampuses: !!selectedCampusId,
    fetchMapData: !!selectedMapId,
    mapId: selectedMapId,
    campusId: selectedCampusId
  });

  // ==================== COMPUTED VALUES ====================
  
  const sceneWidth = useMemo(() => {
    return showSidebar ? 800 : 1000;
  }, [showSidebar]);

  const zoneTypes = [
    { value: 1, label: "Campus", icon: "🏛️" },
    { value: 2, label: "Building", icon: "🏢" },
    { value: 10, label: "Area", icon: "📍" },
    { value: 3, label: "Floor", icon: "🏗️" },
    { value: 4, label: "Wing", icon: "🔄" },
    { value: 5, label: "Room", icon: "🚪" }
  ];

  const filteredZones = useMemo(() => {
    if (!selectedCampusId) return [];
    const zones = getAllZones();
    if (!selectedZoneType) return zones;
    return zones.filter(z => z.zone_type === selectedZoneType);
  }, [getAllZones, selectedZoneType, selectedCampusId]);

  const currentZones = useMemo(() => {
    if (!selectedCampusId) return [];
    if (selectedZone) {
      const allZones = getAllZones();
      const zone = allZones.find(z => z.zone_id === parseInt(selectedZone));
      return zone ? [zone] : [];
    } else {
      return getZonesByType(selectedZoneType);
    }
  }, [selectedZone, selectedZoneType, getAllZones, getZonesByType, selectedCampusId]);

  const availableZonesForSidebar = useMemo(() => {
    if (!selectedCampusId) return [];
    const allZones = getAllZones();
    const zonesWithSettings = Object.keys(zoneSettings)
      .map(zoneId => allZones.find(z => z.zone_id === parseInt(zoneId)))
      .filter(zone => zone !== undefined);
    
    if (selectedMapFilter === 'all') {
      return zonesWithSettings;
    } else {
      return zonesWithSettings.filter(zone => zone.map_id === parseInt(selectedMapFilter));
    }
  }, [getAllZones, zoneSettings, selectedMapFilter, selectedCampusId]);

  const availableMaps = useMemo(() => {
    if (!selectedCampusId) return [];
    const zones = selectedZone ? currentZones : getCampusZones();
    const maps = [];
    
    zones.forEach(zone => {
      if (zone.map_id && !maps.find(m => m.id === zone.map_id)) {
        maps.push({
          id: zone.map_id,
          name: `${zone.zone_name} (Map ${zone.map_id})`,
          zoneId: zone.zone_id,
          zoneName: zone.zone_name
        });
      }
    });
    
    return maps.sort((a, b) => a.id - b.id);
  }, [selectedZone, currentZones, getCampusZones, selectedCampusId]);

  // ==================== EVENT HANDLERS ====================
  
  const handleCampusChange = useCallback((newCampusId) => {
    const campusId = newCampusId ? parseInt(newCampusId) : null;
    setSelectedCampusId(campusId);
    
    if (campusId) {
      const campus = availableCampuses.find(c => c.zone_id === campusId);
      if (campus) {
        setSelectedCampusName(campus.zone_name);
        setSelectedMapId(campus.map_id);
        console.log(`🏫 Campus selected: ${campus.zone_name} (ID: ${campusId}, Map: ${campus.map_id})`);
      }
    } else {
      setSelectedCampusName("");
      setSelectedMapId(null);
      setZoneSettings({});
      setCheckedZones([]);
      setSelectedZone("");
      if (tagConnectionEnabled) {
        setTagConnectionEnabled(false);
      }
      setShowDatabaseDebug(false);
      console.log('🚫 Campus selection cleared');
    }
    
    setSelectedZoneType(1);
    setSelectedZone("");
    setCheckedZones([]);
  }, [availableCampuses, tagConnectionEnabled]);

  const handleDeviceTypeSelectionChange = useCallback((deviceTypeIds) => {
    console.log(`🎯 Device type selection changed:`, deviceTypeIds);
    setSelectedTagDeviceTypes(deviceTypeIds);
    setSelectedDeviceTypes(deviceTypeIds);
    
    if (tagConnectionEnabled && tagIsConnected) {
      console.log(`🔄 Reconnecting to update device type subscriptions...`);
      setTagConnectionEnabled(false);
      setTimeout(() => setTagConnectionEnabled(true), 1000);
    }
  }, [tagConnectionEnabled, tagIsConnected, setSelectedDeviceTypes]);

  const handleTagConnectionToggle = useCallback((enabled) => {
    console.log(`🔌 Tag connection toggle: ${enabled ? 'connecting' : 'disconnecting'}`);
    setTagConnectionEnabled(enabled);
  }, []);

  const handleTagSelectionChange = useCallback((action, data) => {
    console.log(`✅ Tag selection change: ${action}`, data);
    
    if (action === 'selectAll' && Array.isArray(data)) {
      selectAllTags();
    } else if (action === 'selectAlltraq') {
      selectAlltraqTags();
    } else if (action === 'selectCampus') {
      selectCampusTags();
    } else if (action === 'selectOther') {
      selectOtherTags();
    } else if (action === 'selectNone') {
      clearTagSelection();
    } else if (typeof action === 'string') {
      toggleTagSelection(action);
    }
  }, [toggleTagSelection, selectAllTags, selectAlltraqTags, selectCampusTags, selectOtherTags, clearTagSelection]);

  const handleTagConfigChange = useCallback((configKey, value) => {
    console.log(`🎨 Tag config change: ${configKey} = ${value}`);
    setTagConfig(prev => {
      const newConfig = { ...prev, [configKey]: value };
      
      if (configKey === 'sphereRadius' && (value < 1 || value > 10)) {
        console.warn(`⚠️ Invalid sphere radius: ${value}, keeping previous value`);
        return prev;
      }
      
      return newConfig;
    });
  }, []);

  const handleTagClick = useCallback((tagId, tagData) => {
    console.log(`🖱️ Tag clicked: ${tagId}`, tagData);
    
    const zoneInfo = tagData.zone_id ? ` (Zone: ${tagData.zone_id})` : '';
    const categoryInfo = tagData.category ? ` [${tagData.category}]` : '';
    const heightInfo = tagConfig.useActualHeight ? 
      `\nActual Height: ${tagData.z?.toFixed(2) || 'N/A'}` :
      '\nUsing Fixed Height Offset';
    
    alert(
      `Tag: ${tagId}${categoryInfo}${zoneInfo}\n` +
      `Position: (${tagData.x.toFixed(2)}, ${tagData.y.toFixed(2)}, ${tagData.z?.toFixed(2) || 'N/A'})` +
      heightInfo +
      `\nSource: ${tagData.source || 'unknown'}`
    );
  }, [tagConfig.useActualHeight]);

  const handleZoneTypeChange = useCallback((newZoneType) => {
    setSelectedZoneType(parseInt(newZoneType));
    setSelectedZone("");
    setCheckedZones([]);
  }, []);

  const handleZoneChange = useCallback((newZone) => {
    setSelectedZone(newZone);
    
    const zones = getAllZones();
    const zone = zones.find(z => z.zone_id === parseInt(newZone));
    if (zone && zone.map_id) {
      setSelectedMapId(zone.map_id);
    }
  }, [getAllZones]);

  const handleMapChange = useCallback((newMapId) => {
    setSelectedMapId(parseInt(newMapId));
  }, []);

  const handleZoneToggle = useCallback((zoneId) => {
    setCheckedZones(prev => 
      prev.includes(zoneId) 
        ? prev.filter(id => id !== zoneId)
        : [...prev, zoneId]
    );
  }, []);

  const handleCheckAll = useCallback((checked) => {
    if (checked) {
      setCheckedZones(currentZones.map(z => z.zone_id));
    } else {
      setCheckedZones([]);
    }
  }, [currentZones]);

  const handleZoneLabelsToggle = useCallback((enabled) => {
    setShowZoneLabels(enabled);
    console.log(`📋 Zone labels ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  const handleCornerMarkersToggle = useCallback((enabled) => {
    setShowCornerMarkers(enabled);
    console.log(`🔴🔵 Corner markers ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  const handleCascadeVisibilityToggle = useCallback((enabled) => {
    setUseCascadeVisibility(enabled);
    console.log(`🔗 Cascade visibility ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  const handleZoneSettingChange = useCallback((zoneId, settingName, value) => {
    setZoneSettings(prev => {
      let newSettings = {
        ...prev,
        [zoneId]: { ...prev[zoneId], [settingName]: value }
      };
      
      if (settingName === 'visible' && useCascadeVisibility && hierarchyData) {
        if (!value) {
          const descendantIds = getCascadeHiddenZones([parseInt(zoneId)], hierarchyData);
          descendantIds.forEach(descendantId => {
            if (newSettings[descendantId]) {
              newSettings[descendantId].visible = false;
              console.log(`🔗 Cascade hide: ${descendantId} hidden due to parent ${zoneId}`);
            }
          });
        }
      }
      
      return newSettings;
    });
    
    console.log(`🎛️ Zone ${zoneId} ${settingName} changed to:`, value);
  }, [useCascadeVisibility, hierarchyData]);

  const addZoneToSettings = useCallback((zoneId, zoneType, mapId) => {
    if (!zoneSettings[zoneId]) {
      let defaultOpacity, defaultColor;
      
      if (useHierarchyTransparency && hierarchyData) {
        defaultOpacity = calculateHierarchyOpacity(zoneId, hierarchyData);
        defaultColor = getHierarchyColor(zoneType);
        console.log(`➕ Adding zone ${zoneId} with hierarchy-based settings: opacity=${defaultOpacity.toFixed(2)}, color=${defaultColor}`);
      } else {
        const defaultColors = {
          1: '#ff0000', 2: '#00ff00', 3: '#0000ff', 4: '#ff8800', 5: '#ffff00'
        };
        defaultOpacity = zoneType === 1 ? 0.2 : 0.7;
        defaultColor = defaultColors[zoneType] || '#888888';
        console.log(`➕ Adding zone ${zoneId} with manual settings: opacity=${defaultOpacity}, color=${defaultColor}`);
      }
      
      setZoneSettings(prev => ({
        ...prev,
        [zoneId]: { visible: true, opacity: defaultOpacity, color: defaultColor }
      }));
    }
  }, [zoneSettings, useHierarchyTransparency, hierarchyData]);

  // ==================== EFFECTS ====================
  
  // Load available campuses on mount
  useEffect(() => {
    const loadAvailableCampuses = async () => {
      setCampusesLoading(true);
      try {
        console.log('🏫 Loading available campuses...');
        const response = await fetch('/zoneviewer/get_campus_zones');
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        const data = await response.json();
        const campuses = data.campuses || [];
        
        const campusZones = campuses
          .filter(zone => zone.zone_type === 1 && zone.map_id)
          .map(zone => ({
            zone_id: zone.zone_id,
            zone_name: zone.zone_name,
            map_id: zone.map_id
          }));
        
        setAvailableCampuses(campusZones);
        console.log(`✅ Loaded ${campusZones.length} available campuses:`, campusZones);
        
      } catch (err) {
        console.error('❌ Error loading campuses:', err);
      } finally {
        setCampusesLoading(false);
      }
    };
    
    loadAvailableCampuses();
  }, []);

  // Load hierarchy data
  useEffect(() => {
    const loadHierarchy = async () => {
      if (!useHierarchyTransparency || !selectedCampusId) return;
      
      setHierarchyLoading(true);
      try {
        console.log(`🌳 Loading campus hierarchy for campus ${selectedCampusId}...`);
        const hierarchyApiData = await fetchCampusHierarchy(selectedCampusId);
        setHierarchyData(hierarchyApiData);
        
        if (hierarchyApiData && hierarchyApiData.zones) {
          console.log('🏗️ Generating hierarchy-based zone settings...');
          const hierarchySettings = generateHierarchySettings(hierarchyApiData);
          
          setZoneSettings(prev => {
            const newSettings = { ...hierarchySettings };
            Object.keys(prev).forEach(zoneId => {
              if (newSettings[zoneId]) {
                newSettings[zoneId].visible = prev[zoneId].visible;
                if (prev[zoneId].color !== getHierarchyColor(hierarchySettings[zoneId]?.zoneType || 1)) {
                  newSettings[zoneId].color = prev[zoneId].color;
                }
              }
            });
            return newSettings;
          });
          
          console.log('✅ Applied hierarchy-based auto-transparency');
        }
      } catch (error) {
        console.error('❌ Error loading hierarchy:', error);
      } finally {
        setHierarchyLoading(false);
      }
    };
    
    loadHierarchy();
  }, [useHierarchyTransparency, selectedCampusId]);

  // ==================== RENDER ====================
  
  return (
    <div className="three-d-zone-viewer">
      <h2>🎮 3D Zone Viewer v0.3.0 - Fully Modular Architecture</h2>
      
      {/* Status Panel Component */}
      <StatusPanel
        selectedCampusId={selectedCampusId}
        selectedCampusName={selectedCampusName}
        availableCampuses={availableCampuses}
        loading={loading}
        campusesLoading={campusesLoading}
        totalZones={totalZones}
        selectedMapId={selectedMapId}
        zoneSettings={zoneSettings}
        tagConnectionEnabled={tagConnectionEnabled}
        tagIsConnected={tagIsConnected}
        displayTags={displayTags}
        devicesLoading={devicesLoading}
        devicesError={devicesError}
        availableDevices={availableDevices}
        selectedTagDeviceTypes={selectedTagDeviceTypes}
        deviceTypeStats={deviceTypeStats}
        alltraqTags={alltraqTags}
        campusTags={campusTags}
        tagConfig={tagConfig}
        tagStats={tagStats}
        showZoneLabels={showZoneLabels}
        showCornerMarkers={showCornerMarkers}
        useCascadeVisibility={useCascadeVisibility}
        error={error}
        showDatabaseDebug={showDatabaseDebug}
        setShowDatabaseDebug={setShowDatabaseDebug}
      />

      {/* Debug Panel Toggle Button - Separate from StatusPanel */}
      {selectedCampusId && availableDevices.length > 0 && (
        <div style={{
          marginBottom: '15px',
          textAlign: 'center'
        }}>
          <button
            onClick={() => setShowDatabaseDebug(!showDatabaseDebug)}
            style={{
              padding: '8px 16px',
              fontSize: '14px',
              backgroundColor: showDatabaseDebug ? '#007bff' : '#6c757d',
              color: 'white',
              border: 'none',
              borderRadius: '6px',
              cursor: 'pointer',
              fontWeight: 'bold'
            }}
            title={showDatabaseDebug ? 'Hide device debug info' : 'Show device debug info'}
          >
            🔍 {showDatabaseDebug ? 'Hide Database Debug Panel' : 'Show Database Debug Panel'}
          </button>
          <div style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>
            {availableDevices.length} devices loaded • Click to validate for WebSocket integration
          </div>
        </div>
      )}

      {/* Collapsible Database Debug Panel */}
      {selectedCampusId && showDatabaseDebug && (
        <div style={{ marginBottom: '15px', animation: 'slideDown 0.3s ease-out' }}>
          <DatabaseDebugPanel
            availableDevices={availableDevices}
            availableDeviceTypes={availableDeviceTypes}
            deviceTypeStats={deviceTypeStats}
            devicesLoading={devicesLoading}
            devicesError={devicesError}
            refreshDevices={refreshDevices}
            selectedDeviceTypes={selectedTagDeviceTypes}
          />
        </div>
      )}

      {/* Campus Selection Component */}
      <CampusControls
        selectedCampusId={selectedCampusId}
        availableCampuses={availableCampuses}
        campusesLoading={campusesLoading}
        handleCampusChange={handleCampusChange}
      />

      {/* Zone Selection Controls - Only when campus selected */}
      {selectedCampusId && (
        <div className="controls-panel">
          <h3>🎛️ Zone & Tag Controls</h3>
          <div className="controls-grid">
            
            <div className="control-group">
              <label>Zone Type:</label>
              <select value={selectedZoneType} onChange={(e) => handleZoneTypeChange(e.target.value)}>
                {zoneTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.icon} {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="control-group">
              <label>Specific Zone:</label>
              <select value={selectedZone} onChange={(e) => handleZoneChange(e.target.value)}>
                <option value="">
                  All {zoneTypes.find(t => t.value === selectedZoneType)?.label}
                  {selectedZoneType === 1 ? 'es' : 's'}
                </option>
                {filteredZones.map(zone => (
                  <option key={zone.zone_id} value={zone.zone_id}>
                    {zone.zone_name} (ID: {zone.zone_id})
                  </option>
                ))}
              </select>
            </div>

            <div className="control-group">
              <label>Map:</label>
              <select value={selectedMapId || ""} onChange={(e) => handleMapChange(e.target.value)}>
                {availableMaps.map(map => (
                  <option key={map.id} value={map.id}>
                    {map.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={showCampusZone}
                onChange={(e) => setShowCampusZone(e.target.checked)}
              />
              <label>Show Zone Geometry</label>
            </div>

            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={showZoneLabels}
                onChange={(e) => handleZoneLabelsToggle(e.target.checked)}
              />
              <label>Show Zone Labels</label>
            </div>

            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={showCornerMarkers}
                onChange={(e) => handleCornerMarkersToggle(e.target.checked)}
              />
              <label>Show Corner Markers</label>
            </div>

            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={useCascadeVisibility}
                onChange={(e) => handleCascadeVisibilityToggle(e.target.checked)}
              />
              <label>Cascade Visibility</label>
            </div>

            <div className="control-group">
              <label>Device Types to Track:</label>
              <div style={{ 
                display: 'flex', 
                flexDirection: 'column', 
                gap: '4px',
                maxHeight: '150px',
                overflowY: 'auto',
                border: '1px solid #ccc',
                padding: '8px',
                borderRadius: '4px'
              }}>
                {availableDeviceTypes.map(deviceType => (
                  <label key={deviceType.i_typ_dev} style={{ 
                    display: 'flex', 
                    alignItems: 'center', 
                    fontSize: '12px',
                    cursor: 'pointer'
                  }}>
                    <input
                      type="checkbox"
                      checked={selectedTagDeviceTypes.includes(deviceType.i_typ_dev)}
                      onChange={(e) => {
                        const newSelection = e.target.checked
                          ? [...selectedTagDeviceTypes, deviceType.i_typ_dev]
                          : selectedTagDeviceTypes.filter(id => id !== deviceType.i_typ_dev);
                        handleDeviceTypeSelectionChange(newSelection);
                      }}
                      style={{ marginRight: '6px' }}
                    />
                    <span>
                      {deviceType.x_dsc_dev} (ID: {deviceType.i_typ_dev})
                      {deviceTypeStats[deviceType.i_typ_dev] && 
                        ` - ${deviceTypeStats[deviceType.i_typ_dev].count} devices`
                      }
                    </span>
                  </label>
                ))}
                {availableDeviceTypes.length === 0 && (
                  <span style={{ color: '#666', fontStyle: 'italic' }}>
                    {devicesLoading ? 'Loading device types...' : 'No device types available'}
                  </span>
                )}
              </div>
            </div>

            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={showTags}
                onChange={(e) => setShowTags(e.target.checked)}
              />
              <label>Show Real-Time Tags</label>
            </div>
            
            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={tagConfig.useActualHeight}
                onChange={(e) => handleTagConfigChange('useActualHeight', e.target.checked)}
              />
              <label>Use Actual Tag Height</label>
            </div>
          </div>

          {/* Zone Information Display */}
          {currentZones.length > 0 && (
            <div className="zone-info-display" style={{
              marginTop: '15px',
              padding: '10px',
              backgroundColor: '#f8f9fa',
              border: '1px solid #dee2e6',
              borderRadius: '4px'
            }}>
              <h4 style={{ margin: '0 0 8px 0', color: '#495057' }}>
                Available Zones ({currentZones.length}):
              </h4>
              <div style={{ fontSize: '12px', color: '#666' }}>
                {currentZones.map(zone => (
                  <div key={zone.zone_id} style={{ marginBottom: '4px' }}>
                    <strong>{zone.zone_name}</strong> (ID: {zone.zone_id}, Type: {zone.zone_type}, Map: {zone.map_id})
                    {!zoneSettings[zone.zone_id] && (
                      <button 
                        onClick={() => addZoneToSettings(zone.zone_id, zone.zone_type, zone.map_id)}
                        style={{ 
                          marginLeft: '10px', 
                          fontSize: '11px',
                          padding: '2px 6px',
                          backgroundColor: '#007bff',
                          color: 'white',
                          border: 'none',
                          borderRadius: '3px',
                          cursor: 'pointer'
                        }}
                      >
                        + Add to Sidebar
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Debug and Hint Toggle Buttons */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'flex-end',
        alignItems: 'center',
        marginBottom: '10px',
        gap: '8px'
      }}>
        <button
          onClick={() => setShowDebugOverlays(!showDebugOverlays)}
          style={{
            padding: '6px 12px',
            backgroundColor: showDebugOverlays ? '#17a2b8' : '#6c757d',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
        >
          {showDebugOverlays ? '🐛 Hide Debug' : '📊 Show Debug'}
        </button>

        <button
          onClick={() => setShowControlsHint(!showControlsHint)}
          style={{
            padding: '6px 12px',
            backgroundColor: showControlsHint ? '#ffc107' : '#6c757d',
            color: showControlsHint ? 'black' : 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer',
            fontSize: '12px',
            fontWeight: 'bold'
          }}
        >
          {showControlsHint ? '💡 Hide Hint' : '🎮 Show Hint'}
        </button>
      </div>

      {/* 3D Scene Container */}
      {selectedCampusId ? (
        <div className="visualization-container" style={{ position: 'relative' }}>
          <div style={{ 
            display: 'flex', 
            justifyContent: 'space-between', 
            alignItems: 'center',
            marginBottom: '10px',
            flexWrap: 'wrap',
            gap: '10px'
          }}>
            <h3>🌐 3D Visualization - {selectedCampusName}</h3>
          </div>

          <div style={{ 
            border: '2px solid #333',
            borderRadius: '8px',
            padding: '10px',
            background: '#fafafa',
            position: 'relative'
          }}>
            {/* Zone Controls Sidebar */}
            {showSidebar && (
              <ZoneControlsSidebar
                zoneSettings={zoneSettings}
                availableZones={availableZonesForSidebar}
                onZoneSettingChange={handleZoneSettingChange}
                onResetToDefaults={() => setZoneSettings({})}
                isVisible={showSidebar}
                selectedMapFilter={selectedMapFilter}
                onMapFilterChange={setSelectedMapFilter}
                showMapInfo={true}
                tagConnectionEnabled={tagConnectionEnabled}
                onTagConnectionToggle={handleTagConnectionToggle}
                tagConnectionStatus={tagConnectionStatus}
                allTagsData={allTagsData}
                selectedTags={selectedTags}
                onTagSelectionChange={handleTagSelectionChange}
                tagStats={tagStats}
                tagConfig={tagConfig}
                onTagConfigChange={handleTagConfigChange}
                alltraqTags={alltraqTags}
                campusTags={campusTags}
                otherTags={otherTags}
                availableDevices={availableDevices}
                availableDeviceTypes={availableDeviceTypes}
                selectedDeviceTypes={selectedTagDeviceTypes}
                onDeviceTypeSelectionChange={handleDeviceTypeSelectionChange}
                deviceTypeStats={deviceTypeStats}
                devicesLoading={devicesLoading}
                devicesError={devicesError}
                onRefreshDevices={refreshDevices}
              />
            )}
            
            {/* Scene3D */}
            <div style={{ 
              marginLeft: showSidebar ? '320px' : '0',
              transition: 'margin-left 0.3s ease'
            }}>
              {!loading ? (
                <Scene3D 
                  mapData={mapData}
                  zoneData={{ zones: checkedZones.length > 0 ? currentZones.filter(z => checkedZones.includes(z.zone_id)) : currentZones }}
                  showCampusZone={showCampusZone}
                  selectedCampusId={selectedCampusId}
                  selectedCampusName={selectedCampusName}
                  selectedZoneType={selectedZoneType}
                  zoneSettings={zoneSettings}
                  height={500}
                  width={sceneWidth}
                  showDebugOverlays={showDebugOverlays}
                  showControlsHint={showControlsHint}
                  showZoneLabels={showZoneLabels}
                  showCornerMarkers={showCornerMarkers}
                  displayTags={displayTags}
                  tagHistory={tagHistory}
                  tagConfig={tagConfig}
                  showTags={showTags && tagConnectionEnabled}
                  onTagClick={handleTagClick}
                  displayAlltraqTags={displayAlltraqTags}
                  alltraqTags={alltraqTags}
                  campusTags={campusTags}
                />
              ) : (
                <div style={{ 
                  width: `${sceneWidth}px`,
                  height: '500px',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  background: '#f0f0f0',
                  border: '1px dashed #ccc'
                }}>
                  ⏳ Loading scene data for {selectedCampusName}...
                </div>
              )}
            </div>
          </div>

          {/* Footer Info */}
          <div style={{ 
            textAlign: 'center', 
            marginTop: '15px',
            color: '#666',
            fontSize: '14px'
          }}>
            🖱️ <strong>Mouse Controls:</strong> Click and drag to rotate • Scroll to zoom • Right-click to pan
            {showTags && tagConnectionEnabled && Object.keys(displayTags).length > 0 && (
              <span> • Click tags for details</span>
            )}
            <br />
            🏫 <strong>Campus:</strong> {selectedCampusName} (ID: {selectedCampusId})
            <br />
            🎛️ <strong>v0.3.0 Features:</strong> Fully Modular Architecture • Separated Components • Reduced Complexity
            <br />
            🏷️ <strong>Real-Time Tags:</strong> {tagConnectionEnabled ? 
              (tagIsConnected ? 
                `🔗 Connected - ${Object.keys(displayTags).length} shown (${Object.keys(alltraqTags).length} alltraq) at ${tagStats.tagRate.toFixed(1)}/s` : 
                '⏳ Connecting...') : 
              '🚫 Disabled (enable in sidebar)'
            }
            <br />
            📱 <strong>Devices:</strong> {devicesLoading ? 
              '⏳ Loading from FastAPI' : 
              devicesError ? 
                `❌ ${devicesError}` : 
                `${availableDevices.length} loaded from ${selectedTagDeviceTypes.length} device types`
            }
            <br />
            🔍 <strong>Debug Panel:</strong> {showDatabaseDebug ? 
              'Visible - validating database integration' : 
              'Hidden - click Debug button to validate database integration'
            }
          </div>
        </div>
      ) : (
        <div style={{
          textAlign: 'center',
          padding: '40px',
          background: '#f8f9fa',
          border: '2px dashed #dee2e6',
          borderRadius: '8px',
          color: '#6c757d'
        }}>
          <h3>🏫 Select Campus to Begin</h3>
          <p>Choose a campus from the dropdown above to view zones and 3D visualization.</p>
          <p><strong>Available:</strong> {availableCampuses.length} campuses loaded</p>
          <p><em>Fully modular real-time tag visualization with device type selection and enhanced filtering.</em></p>
        </div>
      )}
    </div>
  );
};

export default TDZ_index;