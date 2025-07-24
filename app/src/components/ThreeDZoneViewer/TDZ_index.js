/* Name: TDZ_index.js */
/* Version: 0.1.17 */
/* Created: 250719 */
/* Modified: 250722 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: ENHANCED TAG INTEGRATION - Updated to use tagRenderingUtils v0.1.2 with actual height and alltraq filtering */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.17: ENHANCED TAG INTEGRATION - Updated tagConfig with useActualHeight, enhanced alltraq support */
/* - 0.1.16: REAL-TIME TAGS COMPLETE - Added useRealTimeTags hook, wired up all tag props, added UI controls */
/* - 0.1.15: RESTORE CASCADE CHECKBOX - Added back missing cascade visibility checkbox in Zone Selection section */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import Scene3D from './components/Scene3D';
import ZoneControlsSidebar from './components/ZoneControlsSidebar';
import useZoneData from './hooks/useZoneData';
// Import enhanced real-time tags hook
import { useRealTimeTags } from './hooks/useRealTimeTags';
import {
  fetchCampusHierarchy,
  calculateHierarchyOpacity,
  getHierarchyColor,
  getCascadeHiddenZones,
  generateHierarchySettings,
  validateHierarchySettings
} from './utils/hierarchyUtils';
// Import enhanced tag utilities
import { DEFAULT_TAG_CONFIG } from './utils/tagRenderingUtils';
import './styles/ThreeDZoneViewer.css';

const TDZ_index = () => {
  console.log(`🚀 TDZ_index v0.1.17: Initializing with enhanced tag support (actual height + alltraq)`);

  // Campus selection first - no hardcoded defaults (existing v0.1.14)
  const [selectedCampusId, setSelectedCampusId] = useState(null);
  const [selectedCampusName, setSelectedCampusName] = useState("");
  
  // Zone selection state - now dependent on campus selection (existing)
  const [selectedZoneType, setSelectedZoneType] = useState(1);
  const [selectedZone, setSelectedZone] = useState("");
  const [selectedMapId, setSelectedMapId] = useState(null);
  const [showCampusZone, setShowCampusZone] = useState(false);
  const [checkedZones, setCheckedZones] = useState([]);
  
  // Dynamic zone settings state - now starts empty (existing)
  const [zoneSettings, setZoneSettings] = useState({});
  
  // Independent toggle states for UI elements (existing)
  const [showSidebar, setShowSidebar] = useState(true);
  const [showDebugOverlays, setShowDebugOverlays] = useState(true);
  const [showControlsHint, setShowControlsHint] = useState(true);
  
  // Wireframe feature controls (existing)
  const [showZoneLabels, setShowZoneLabels] = useState(false);
  const [showCornerMarkers, setShowCornerMarkers] = useState(false);
  
  // Multi-map support state (existing)
  const [selectedMapFilter, setSelectedMapFilter] = useState('all');

  // Hierarchy controls state (existing)
  const [useHierarchyTransparency, setUseHierarchyTransparency] = useState(true);
  const [useCascadeVisibility, setUseCascadeVisibility] = useState(true);
  
  // Hierarchy data state (existing)
  const [hierarchyData, setHierarchyData] = useState(null);
  const [hierarchyLoading, setHierarchyLoading] = useState(false);

  // Available campuses for dropdown (existing v0.1.14)
  const [availableCampuses, setAvailableCampuses] = useState([]);
  const [campusesLoading, setCampusesLoading] = useState(false);

  // ENHANCED v0.1.17: Real-time tag state with new features
  const [tagConnectionEnabled, setTagConnectionEnabled] = useState(false);
  const [tagConfig, setTagConfig] = useState({
    ...DEFAULT_TAG_CONFIG,
    showLabels: true,
    showTrails: false,
    sphereRadius: 3,
    activeColor: '#00ff00',
    // NEW v0.1.17: Enhanced height configuration
    useActualHeight: true,        // Use real ParcoRTLS z-coordinates
    minHeightAboveGround: 2,      // Safety margin above ground
    // NEW v0.1.17: Alltraq-specific configuration
    alltraqColor: '#ff4400',      // Orange for alltraq tags
    campusColor: '#00ff00',       // Green for campus tags
    showAlltraqSeparately: true   // Show alltraq tags with different styling
  });
  const [showTags, setShowTags] = useState(true);

  // ENHANCED v0.1.17: Initialize enhanced real-time tags hook
  const {
    isConnected: tagIsConnected,
    connectionStatus: tagConnectionStatus,
    allTagsData,
    displayTags,
    tagHistory,
    tagStats,
    selectedTags,
    // NEW v0.1.17: Enhanced zone-categorized data
    alltraqTags,
    campusTags,
    otherTags,
    displayAlltraqTags,
    // Enhanced selection methods
    toggleTagSelection,
    selectAllTags,
    selectAlltraqTags,
    selectCampusTags,
    clearTagSelection,
    connect: connectTags,
    disconnect: disconnectTags
  } = useRealTimeTags({
    selectedCampusId,
    isEnabled: tagConnectionEnabled,
    // NEW v0.1.17: Enhanced options
    enableAlltraqFiltering: true,
    showAlltraqSeparately: tagConfig.showAlltraqSeparately,
    onConnectionChange: (connected, status) => {
      console.log(`🔌 Tag connection changed: ${connected ? 'connected' : 'disconnected'} (${status})`);
    },
    onTagUpdate: (tagData) => {
      console.log(`📍 Tag update: ${tagData.id} at (${tagData.x.toFixed(2)}, ${tagData.y.toFixed(2)}, ${tagData.z.toFixed(2)}) [${tagData.category}]`);
    },
    maxTagHistory: 20
  });

  // Calculate responsive dimensions for 3D scene (existing)
  const sceneWidth = useMemo(() => {
    return showSidebar ? 800 : 1000;
  }, [showSidebar]);

  // Fetch zone data only when campus is selected (existing v0.1.14)
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

  // Load available campuses on component mount (existing v0.1.14)
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

  // Zone type options (existing)
  const zoneTypes = [
    { value: 1, label: "Campus", icon: "🏛️" },
    { value: 2, label: "Building", icon: "🏢" },
    { value: 10, label: "Area", icon: "📍" },
    { value: 3, label: "Floor", icon: "🏗️" },
    { value: 4, label: "Wing", icon: "🔄" },
    { value: 5, label: "Room", icon: "🚪" }
  ];

  // Get filtered zones based on selected type (existing)
  const filteredZones = useMemo(() => {
    if (!selectedCampusId) return [];
    const zones = getAllZones();
    if (!selectedZoneType) return zones;
    return zones.filter(z => z.zone_type === selectedZoneType);
  }, [getAllZones, selectedZoneType, selectedCampusId]);

  // Get zones for current selection to pass to Scene3D (existing)
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

  // Get available zones for sidebar (existing)
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

  // Get available maps from current zones (existing)
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

  // Campus selection handler (existing v0.1.14)
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
      // Disconnect tags when campus cleared
      if (tagConnectionEnabled) {
        setTagConnectionEnabled(false);
      }
      console.log('🚫 Campus selection cleared');
    }
    
    setSelectedZoneType(1);
    setSelectedZone("");
    setCheckedZones([]);
  }, [availableCampuses, tagConnectionEnabled]);

  // ENHANCED v0.1.17: Tag connection toggle handler
  const handleTagConnectionToggle = useCallback((enabled) => {
    console.log(`🔌 Tag connection toggle: ${enabled ? 'connecting' : 'disconnecting'}`);
    setTagConnectionEnabled(enabled);
  }, []);

  // ENHANCED v0.1.17: Tag selection change handler with zone categories
  const handleTagSelectionChange = useCallback((action, data) => {
    console.log(`✅ Tag selection change: ${action}`, data);
    
    if (action === 'selectAll' && Array.isArray(data)) {
      selectAllTags();
    } else if (action === 'selectAlltraq') {
      selectAlltraqTags();
    } else if (action === 'selectCampus') {
      selectCampusTags();
    } else if (action === 'selectNone') {
      clearTagSelection();
    } else if (typeof action === 'string') {
      // Single tag toggle
      toggleTagSelection(action);
    }
  }, [toggleTagSelection, selectAllTags, selectAlltraqTags, selectCampusTags, clearTagSelection]);

  // ENHANCED v0.1.17: Tag configuration change handler with validation
  const handleTagConfigChange = useCallback((configKey, value) => {
    console.log(`🎨 Tag config change: ${configKey} = ${value}`);
    setTagConfig(prev => {
      const newConfig = {
        ...prev,
        [configKey]: value
      };
      
      // VALIDATION: Ensure valid configuration
      if (configKey === 'sphereRadius' && (value < 1 || value > 10)) {
        console.warn(`⚠️ Invalid sphere radius: ${value}, keeping previous value`);
        return prev;
      }
      
      return newConfig;
    });
  }, []);

  // ENHANCED v0.1.17: Tag click handler with zone information
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

  // Fetch hierarchy data and apply auto-transparency (existing)
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

  // Existing handlers (unchanged)
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

  // Wireframe feature toggle handlers (existing)
  const handleZoneLabelsToggle = useCallback((enabled) => {
    setShowZoneLabels(enabled);
    console.log(`📋 Zone labels ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  const handleCornerMarkersToggle = useCallback((enabled) => {
    setShowCornerMarkers(enabled);
    console.log(`🔴🔵 Corner markers ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  // Cascade visibility toggle handler (existing v0.1.15)
  const handleCascadeVisibilityToggle = useCallback((enabled) => {
    setUseCascadeVisibility(enabled);
    console.log(`🔗 Cascade visibility ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  // Zone settings handlers (existing)
  const handleZoneSettingChange = useCallback((zoneId, settingName, value) => {
    setZoneSettings(prev => {
      let newSettings = {
        ...prev,
        [zoneId]: {
          ...prev[zoneId],
          [settingName]: value
        }
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

  // Enhanced zone addition with HIERARCHY SUPPORT (existing)
  const addZoneToSettings = useCallback((zoneId, zoneType, mapId) => {
    if (!zoneSettings[zoneId]) {
      let defaultOpacity, defaultColor;
      
      if (useHierarchyTransparency && hierarchyData) {
        defaultOpacity = calculateHierarchyOpacity(zoneId, hierarchyData);
        defaultColor = getHierarchyColor(zoneType);
        console.log(`➕ Adding zone ${zoneId} with hierarchy-based settings: opacity=${defaultOpacity.toFixed(2)}, color=${defaultColor}`);
      } else {
        const defaultColors = {
          1: '#ff0000',   // Campus = Red
          2: '#00ff00',   // Building = Green  
          3: '#0000ff',   // Floor = Blue
          4: '#ff8800',   // Wing = Orange
          5: '#ffff00'    // Room = Yellow
        };
        defaultOpacity = zoneType === 1 ? 0.2 : 0.7;
        defaultColor = defaultColors[zoneType] || '#888888';
        console.log(`➕ Adding zone ${zoneId} with manual settings: opacity=${defaultOpacity}, color=${defaultColor}`);
      }
      
      setZoneSettings(prev => ({
        ...prev,
        [zoneId]: {
          visible: true,
          opacity: defaultOpacity,
          color: defaultColor
        }
      }));
    }
  }, [zoneSettings, useHierarchyTransparency, hierarchyData]);

  console.log('🎮 TDZ_index v0.1.17 Debug (Enhanced Tag Integration):', {
    selectedCampusId,
    selectedCampusName,
    selectedMapId,
    availableCampuses: availableCampuses.length,
    campusesLoading,
    selectedZoneType,
    selectedZone,
    showCampusZone,
    currentZones: currentZones.length,
    checkedZones: checkedZones.length,
    zoneSettings,
    showZoneLabels,
    showCornerMarkers,
    useCascadeVisibility,
    // ENHANCED v0.1.17: Tag debugging
    tagConnectionEnabled,
    tagIsConnected,
    tagConnectionStatus,
    allTagsDataCount: Object.keys(allTagsData).length,
    alltraqTagsCount: Object.keys(alltraqTags).length,
    campusTagsCount: Object.keys(campusTags).length,
    selectedTagsCount: selectedTags.size,
    displayTagsCount: Object.keys(displayTags).length,
    showTags,
    tagConfigActualHeight: tagConfig.useActualHeight,
    loading,
    error
  });

  return (
    <div className="three-d-zone-viewer">
      <h2>🎮 3D Zone Viewer v0.1.17 - Enhanced Tag Integration</h2>
      
      {/* Status Panel (updated with enhanced tag info) */}
      <div className="status-panel">
        <h3>📊 Status</h3>
        <div className="status-grid">
          <div className="status-item">
            <strong>Campus Selected:</strong>
            <span className="status-value">
              {selectedCampusId ? `✅ ${selectedCampusName} (${selectedCampusId})` : '❌ None'}
            </span>
          </div>
          <div className="status-item">
            <strong>Available Campuses:</strong>
            <span className="status-value">{availableCampuses.length}</span>
          </div>
          <div className="status-item">
            <strong>Loading:</strong>
            <span className="status-value">{loading || campusesLoading ? '⏳ Yes' : '✅ No'}</span>
          </div>
          <div className="status-item">
            <strong>Total Zones:</strong>
            <span className="status-value">{totalZones}</span>
          </div>
          <div className="status-item">
            <strong>Selected Map:</strong>
            <span className="status-value">{selectedMapId || 'None'}</span>
          </div>
          <div className="status-item">
            <strong>Zone Settings:</strong>
            <span className="status-value">{Object.keys(zoneSettings).length} zones</span>
          </div>
          {/* ENHANCED v0.1.17: Enhanced tag status items */}
          <div className="status-item">
            <strong>Real-Time Tags:</strong>
            <span className="status-value">
              {tagConnectionEnabled ? 
                (tagIsConnected ? `🔗 ${Object.keys(displayTags).length} shown` : '⏳ Connecting') : 
                '🚫 Disabled'
              }
            </span>
          </div>
          <div className="status-item">
            <strong>Alltraq Tags:</strong>
            <span className="status-value">
              {tagConnectionEnabled ? `🎯 ${Object.keys(alltraqTags).length} detected` : '➖ N/A'}
            </span>
          </div>
          <div className="status-item">
            <strong>Tag Height Mode:</strong>
            <span className="status-value">
              {tagConfig.useActualHeight ? '📏 Actual Z-coord' : '🔧 Fixed Offset'}
            </span>
          </div>
          <div className="status-item">
            <strong>Tag Rate:</strong>
            <span className="status-value">
              {tagIsConnected ? `📈 ${tagStats.tagRate.toFixed(1)}/s` : '➖ N/A'}
            </span>
          </div>
          <div className="status-item">
            <strong>Zone Labels:</strong>
            <span className="status-value">{showZoneLabels ? '📋 ON' : '🚫 OFF'}</span>
          </div>
          <div className="status-item">
            <strong>Corner Markers:</strong>
            <span className="status-value">{showCornerMarkers ? '🔴🔵 ON' : '🚫 OFF'}</span>
          </div>
          <div className="status-item">
            <strong>Cascade Visibility:</strong>
            <span className="status-value">{useCascadeVisibility ? '🔗 ON' : '🚫 OFF'}</span>
          </div>
        </div>
        
        {error && (
          <div className="error-message">
            ❌ <strong>Error:</strong> {error}
          </div>
        )}
      </div>

      {/* STEP 1: Campus Selection (existing v0.1.14) */}
      <div className="controls-panel">
        <h3>🏫 Campus Selection (Required First)</h3>
        <div className="controls-grid">
          
          <div className="control-group">
            <label>Select Campus:</label>
            <select 
              value={selectedCampusId || ""} 
              onChange={(e) => handleCampusChange(e.target.value)}
              disabled={campusesLoading}
            >
              <option value="">-- Select Campus First --</option>
              {availableCampuses.map(campus => (
                <option key={campus.zone_id} value={campus.zone_id}>
                  🏫 {campus.zone_name} (ID: {campus.zone_id}, Map: {campus.map_id})
                </option>
              ))}
            </select>
          </div>

          {campusesLoading && (
            <div style={{ color: '#666', fontStyle: 'italic' }}>
              ⏳ Loading available campuses...
            </div>
          )}

          {!selectedCampusId && (
            <div style={{ 
              color: '#856404', 
              backgroundColor: '#fff3cd', 
              border: '1px solid #ffeaa7', 
              borderRadius: '4px', 
              padding: '8px',
              marginTop: '10px'
            }}>
              ⚠️ Please select a campus first to view zones and real-time tags
            </div>
          )}
        </div>
      </div>

      {/* STEP 2: Zone Selection - Only available after campus selection (existing) */}
      {selectedCampusId && (
        <div className="controls-panel">
          <h3>🎛️ Zone Selection</h3>
          <div className="controls-grid">
            
            <div className="control-group">
              <label>Zone Type:</label>
              <select 
                value={selectedZoneType} 
                onChange={(e) => handleZoneTypeChange(e.target.value)}
              >
                {zoneTypes.map(type => (
                  <option key={type.value} value={type.value}>
                    {type.icon} {type.label}
                  </option>
                ))}
              </select>
            </div>

            <div className="control-group">
              <label>Specific Zone:</label>
              <select 
                value={selectedZone} 
                onChange={(e) => handleZoneChange(e.target.value)}
              >
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
              <select 
                value={selectedMapId || ""} 
                onChange={(e) => handleMapChange(e.target.value)}
              >
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
              <label>Show Zone Labels (Text)</label>
            </div>

            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={showCornerMarkers}
                onChange={(e) => handleCornerMarkersToggle(e.target.checked)}
              />
              <label>Show Corner Markers (Red/Blue Spheres)</label>
            </div>

            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={useCascadeVisibility}
                onChange={(e) => handleCascadeVisibilityToggle(e.target.checked)}
              />
              <label>Cascade Visibility (Hide Parent → Hide Children)</label>
            </div>

            {/* ENHANCED v0.1.17: Real-Time Tags Controls */}
            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={showTags}
                onChange={(e) => setShowTags(e.target.checked)}
              />
              <label>Show Real-Time Tags</label>
            </div>
            
            {/* NEW v0.1.17: Height mode indicator */}
            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={tagConfig.useActualHeight}
                onChange={(e) => handleTagConfigChange('useActualHeight', e.target.checked)}
              />
              <label>Use Actual Tag Height (Z-coordinate)</label>
            </div>
          </div>

          {/* Zone Information Display (enhanced with tag info) */}
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
              <div style={{ 
                marginTop: '8px', 
                fontSize: '11px', 
                color: '#6c757d',
                fontStyle: 'italic'
              }}>
                💡 Use the sidebar controls to show/hide zones and adjust settings
                <br />
                🔗 Cascade Visibility: {useCascadeVisibility ? 'ON - Hiding parent zones will hide children' : 'OFF - Each zone independent'}
                <br />
                {/* ENHANCED v0.1.17: Enhanced tag status in zone info */}
                🏷️ Real-Time Tags: {tagConnectionEnabled ? 
                  (tagIsConnected ? 
                    `Connected - ${Object.keys(displayTags).length} shown (${Object.keys(alltraqTags).length} alltraq, ${Object.keys(campusTags).length} campus)` : 
                    'Connecting...') : 
                  'Enable in sidebar to see live tag positions'}
                <br />
                📏 Height Mode: {tagConfig.useActualHeight ? 'Using actual ParcoRTLS Z-coordinates' : 'Using fixed height offset'}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Debug and Hint Toggle Buttons (existing) */}
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
          title={showDebugOverlays ? 'Hide debug info overlays' : 'Show debug info overlays'}
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
          title={showControlsHint ? 'Hide controls hint' : 'Show controls hint'}
        >
          {showControlsHint ? '💡 Hide Hint' : '🎮 Show Hint'}
        </button>
      </div>

      {/* 3D Scene Container - Only show when campus is selected (ENHANCED tag integration) */}
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
            {/* Zone Controls Sidebar (enhanced with tag props) */}
            {showSidebar && (
              <ZoneControlsSidebar
                // Existing zone props (unchanged)
                zoneSettings={zoneSettings}
                availableZones={availableZonesForSidebar}
                onZoneSettingChange={handleZoneSettingChange}
                onResetToDefaults={() => setZoneSettings({})}
                isVisible={showSidebar}
                selectedMapFilter={selectedMapFilter}
                onMapFilterChange={setSelectedMapFilter}
                showMapInfo={true}
                
                // ENHANCED v0.1.17: Enhanced real-time tag props
                tagConnectionEnabled={tagConnectionEnabled}
                onTagConnectionToggle={handleTagConnectionToggle}
                tagConnectionStatus={tagConnectionStatus}
                allTagsData={allTagsData}
                selectedTags={selectedTags}
                onTagSelectionChange={handleTagSelectionChange}
                tagStats={tagStats}
                tagConfig={tagConfig}
                onTagConfigChange={handleTagConfigChange}
                // NEW v0.1.17: Zone-categorized tag data
                alltraqTags={alltraqTags}
                campusTags={campusTags}
                otherTags={otherTags}
              />
            )}
            
            {/* Scene3D (enhanced with tag props) */}
            <div style={{ 
              marginLeft: showSidebar ? '320px' : '0', // Slightly more space for wider sidebar
              transition: 'margin-left 0.3s ease'
            }}>
              {!loading ? (
                <Scene3D 
                  // Existing props (unchanged)
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
                  
                  // ENHANCED v0.1.17: Enhanced real-time tag props
                  displayTags={displayTags}
                  tagHistory={tagHistory}
                  tagConfig={tagConfig}
                  showTags={showTags && tagConnectionEnabled}
                  onTagClick={handleTagClick}
                  // NEW v0.1.17: Zone-categorized tag display
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

          <div style={{ 
            textAlign: 'center', 
            marginTop: '15px',
            color: '#666',
            fontSize: '14px'
          }}>
            🖱️ <strong>Mouse Controls:</strong> Click and drag to rotate • Scroll to zoom • Right-click to pan
            {/* ENHANCED v0.1.17: Enhanced tag interaction hint */}
            {showTags && tagConnectionEnabled && Object.keys(displayTags).length > 0 && (
              <span> • Click tags for details (with zone/height info)</span>
            )}
            <br />
            🏫 <strong>Selected Campus:</strong> {selectedCampusName} (ID: {selectedCampusId})
            <br />
            🎛️ <strong>v0.1.17 Features:</strong> Campus-First Selection • Zone Boundary Filter • Cascade Visibility Control • Enhanced Real-Time Tags
            {/* ENHANCED v0.1.17: Enhanced tag status in footer */}
            <br />
            🏷️ <strong>Real-Time Tags:</strong> {tagConnectionEnabled ? 
              (tagIsConnected ? 
                `🔗 Connected - ${Object.keys(displayTags).length} shown (${Object.keys(alltraqTags).length} alltraq) at ${tagStats.tagRate.toFixed(1)}/s` : 
                '⏳ Connecting...') : 
              '🚫 Disabled (enable in sidebar)'
            }
            {tagConfig.useActualHeight && (
              <span> • 📏 Using actual ParcoRTLS heights</span>
            )}
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
          {/* ENHANCED v0.1.17: Enhanced tag capability hint */}
          <p><em>Real-time tag visualization with actual height support and alltraq filtering will be available after campus selection.</em></p>
        </div>
      )}
    </div>
  );
};

export default TDZ_index;