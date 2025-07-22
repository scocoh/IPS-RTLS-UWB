/* Name: TDZ_index.js */
/* Version: 0.1.15 */
/* Created: 250719 */
/* Modified: 250722 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: RESTORE CASCADE CHECKBOX - Added back missing cascade visibility checkbox in Zone Selection section */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.15: RESTORE CASCADE CHECKBOX - Added back missing "Cascade Visibility (Hide Parent → Hide Children)" checkbox */
/* - 0.1.14: CAMPUS-FIRST SELECTION - Removed hardcoded 422, added campus dropdown, make zone loading campus-dependent */
/* - 0.1.13: WIREFRAME FEATURE CONTROLS - Added showZoneLabels and showCornerMarkers toggles for v0.1.12/v0.1.28 compatibility */

import React, { useState, useCallback, useMemo, useEffect } from 'react';
import Scene3D from './components/Scene3D';
import ZoneControlsSidebar from './components/ZoneControlsSidebar';
import useZoneData from './hooks/useZoneData';
import {
  fetchCampusHierarchy,
  calculateHierarchyOpacity,
  getHierarchyColor,
  getCascadeHiddenZones,
  generateHierarchySettings,
  validateHierarchySettings
} from './utils/hierarchyUtils';
import './styles/ThreeDZoneViewer.css';

const TDZ_index = () => {
  // NEW v0.1.14: Campus selection first - no hardcoded defaults
  const [selectedCampusId, setSelectedCampusId] = useState(null); // CHANGED: was 422
  const [selectedCampusName, setSelectedCampusName] = useState(""); // NEW: for display
  
  // Zone selection state - now dependent on campus selection
  const [selectedZoneType, setSelectedZoneType] = useState(1); // Default to Campus
  const [selectedZone, setSelectedZone] = useState("");
  const [selectedMapId, setSelectedMapId] = useState(null); // CHANGED: was 39
  const [showCampusZone, setShowCampusZone] = useState(false);
  const [checkedZones, setCheckedZones] = useState([]);
  
  // Dynamic zone settings state - now starts empty
  const [zoneSettings, setZoneSettings] = useState({}); // CHANGED: was hardcoded 422/427
  
  // Independent toggle states for UI elements
  const [showSidebar, setShowSidebar] = useState(true);
  const [showDebugOverlays, setShowDebugOverlays] = useState(true);
  const [showControlsHint, setShowControlsHint] = useState(true);
  
  // Wireframe feature controls
  const [showZoneLabels, setShowZoneLabels] = useState(false);
  const [showCornerMarkers, setShowCornerMarkers] = useState(false);
  
  // Multi-map support state
  const [selectedMapFilter, setSelectedMapFilter] = useState('all');

  // Hierarchy controls state
  const [useHierarchyTransparency, setUseHierarchyTransparency] = useState(true);
  const [useCascadeVisibility, setUseCascadeVisibility] = useState(true);
  
  // Hierarchy data state
  const [hierarchyData, setHierarchyData] = useState(null);
  const [hierarchyLoading, setHierarchyLoading] = useState(false);

  // NEW v0.1.14: Available campuses for dropdown
  const [availableCampuses, setAvailableCampuses] = useState([]);
  const [campusesLoading, setCampusesLoading] = useState(false);

  // Calculate responsive dimensions for 3D scene
  const sceneWidth = useMemo(() => {
    return showSidebar ? 800 : 1000;
  }, [showSidebar]);

  // NEW v0.1.14: Fetch zone data only when campus is selected
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
    fetchCampuses: !!selectedCampusId, // Only fetch when campus selected
    fetchMapData: !!selectedMapId,
    mapId: selectedMapId,
    campusId: selectedCampusId // NEW: Pass campus ID to hook
  });

  // NEW v0.1.14: Load available campuses on component mount
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
        
        // Extract just campus-level zones (zone_type = 1) - they're already at the top level
        const campusZones = campuses
          .filter(zone => zone.zone_type === 1 && zone.map_id) // Only campus-level with maps
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

  // Zone type options
  const zoneTypes = [
    { value: 1, label: "Campus", icon: "🏛️" },
    { value: 2, label: "Building", icon: "🏢" },
    { value: 10, label: "Area", icon: "📍" },
    { value: 3, label: "Floor", icon: "🏗️" },
    { value: 4, label: "Wing", icon: "🔄" },
    { value: 5, label: "Room", icon: "🚪" }
  ];

  // Get filtered zones based on selected type - only if campus selected
  const filteredZones = useMemo(() => {
    if (!selectedCampusId) return [];
    const zones = getAllZones();
    if (!selectedZoneType) return zones;
    return zones.filter(z => z.zone_type === selectedZoneType);
  }, [getAllZones, selectedZoneType, selectedCampusId]);

  // Get zones for current selection to pass to Scene3D
  const currentZones = useMemo(() => {
    if (!selectedCampusId) return [];
    if (selectedZone) {
      // If specific zone selected, get its hierarchy
      const allZones = getAllZones();
      const zone = allZones.find(z => z.zone_id === parseInt(selectedZone));
      return zone ? [zone] : [];
    } else {
      // Otherwise show zones by type
      return getZonesByType(selectedZoneType);
    }
  }, [selectedZone, selectedZoneType, getAllZones, getZonesByType, selectedCampusId]);

  // Get available zones for sidebar (zones that exist in data and have settings)
  const availableZonesForSidebar = useMemo(() => {
    if (!selectedCampusId) return [];
    const allZones = getAllZones();
    const zonesWithSettings = Object.keys(zoneSettings)
      .map(zoneId => allZones.find(z => z.zone_id === parseInt(zoneId)))
      .filter(zone => zone !== undefined);
    
    // Apply map filter if not 'all'
    if (selectedMapFilter === 'all') {
      return zonesWithSettings;
    } else {
      return zonesWithSettings.filter(zone => zone.map_id === parseInt(selectedMapFilter));
    }
  }, [getAllZones, zoneSettings, selectedMapFilter, selectedCampusId]);

  // Get available maps from current zones
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

  // NEW v0.1.14: Campus selection handler
  const handleCampusChange = useCallback((newCampusId) => {
    const campusId = newCampusId ? parseInt(newCampusId) : null;
    setSelectedCampusId(campusId);
    
    if (campusId) {
      // Find campus details
      const campus = availableCampuses.find(c => c.zone_id === campusId);
      if (campus) {
        setSelectedCampusName(campus.zone_name);
        setSelectedMapId(campus.map_id);
        console.log(`🏫 Campus selected: ${campus.zone_name} (ID: ${campusId}, Map: ${campus.map_id})`);
      }
    } else {
      // Clear selection
      setSelectedCampusName("");
      setSelectedMapId(null);
      setZoneSettings({});
      setCheckedZones([]);
      setSelectedZone("");
      console.log('🚫 Campus selection cleared');
    }
    
    // Reset zone-related state
    setSelectedZoneType(1);
    setSelectedZone("");
    setCheckedZones([]);
  }, [availableCampuses]);

  // Fetch hierarchy data and apply auto-transparency - only when campus selected
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
          
          // Apply hierarchy settings while preserving user visibility choices
          setZoneSettings(prev => {
            const newSettings = { ...hierarchySettings };
            Object.keys(prev).forEach(zoneId => {
              if (newSettings[zoneId]) {
                // Preserve user's visibility choice
                newSettings[zoneId].visible = prev[zoneId].visible;
                // Preserve custom colors if user changed them
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
  }, [useHierarchyTransparency, selectedCampusId]); // CHANGED: Added selectedCampusId dependency

  // Handlers
  const handleZoneTypeChange = useCallback((newZoneType) => {
    setSelectedZoneType(parseInt(newZoneType));
    setSelectedZone(""); // Reset zone selection
    setCheckedZones([]); // Reset checked zones
  }, []);

  const handleZoneChange = useCallback((newZone) => {
    setSelectedZone(newZone);
    
    // Auto-select map for this zone
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

  // Wireframe feature toggle handlers
  const handleZoneLabelsToggle = useCallback((enabled) => {
    setShowZoneLabels(enabled);
    console.log(`📋 Zone labels ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  const handleCornerMarkersToggle = useCallback((enabled) => {
    setShowCornerMarkers(enabled);
    console.log(`🔴🔵 Corner markers ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  // RESTORED v0.1.15: Cascade visibility toggle handler
  const handleCascadeVisibilityToggle = useCallback((enabled) => {
    setUseCascadeVisibility(enabled);
    console.log(`🔗 Cascade visibility ${enabled ? 'enabled' : 'disabled'}`);
  }, []);

  // Zone settings handlers remain the same...
  const handleZoneSettingChange = useCallback((zoneId, settingName, value) => {
    setZoneSettings(prev => {
      let newSettings = {
        ...prev,
        [zoneId]: {
          ...prev[zoneId],
          [settingName]: value
        }
      };
      
      // Handle cascade visibility if enabled
      if (settingName === 'visible' && useCascadeVisibility && hierarchyData) {
        if (!value) {
          // Zone being hidden - hide all children
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

  // Enhanced zone addition with HIERARCHY SUPPORT
  const addZoneToSettings = useCallback((zoneId, zoneType, mapId) => {
    if (!zoneSettings[zoneId]) {
      let defaultOpacity, defaultColor;
      
      if (useHierarchyTransparency && hierarchyData) {
        // Use hierarchy-based defaults
        defaultOpacity = calculateHierarchyOpacity(zoneId, hierarchyData);
        defaultColor = getHierarchyColor(zoneType);
        console.log(`➕ Adding zone ${zoneId} with hierarchy-based settings: opacity=${defaultOpacity.toFixed(2)}, color=${defaultColor}`);
      } else {
        // Use manual defaults
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

  console.log('🎮 TDZ_index v0.1.15 Debug (Cascade Checkbox Restored):', {
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
    useCascadeVisibility, // RESTORED: Now shows in debug
    loading,
    error
  });

  return (
    <div className="three-d-zone-viewer">
      <h2>🎮 3D Zone Viewer v0.1.15 - Cascade Checkbox Restored</h2>
      
      {/* Status Panel */}
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

      {/* STEP 1: Campus Selection - NEW v0.1.14 */}
      <div className="controls-panel">
        <h3>🏫 Campus Selection (Required First)</h3>
        <div className="controls-grid">
          
          {/* Campus Dropdown */}
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
              ⚠️ Please select a campus first to view zones and maps
            </div>
          )}
        </div>
      </div>

      {/* STEP 2: Zone Selection - Only available after campus selection */}
      {selectedCampusId && (
        <div className="controls-panel">
          <h3>🎛️ Zone Selection</h3>
          <div className="controls-grid">
            
            {/* Zone Type Selection */}
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

            {/* Specific Zone Selection */}
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

            {/* Map Selection */}
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

            {/* Zone Visibility Toggle */}
            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={showCampusZone}
                onChange={(e) => setShowCampusZone(e.target.checked)}
              />
              <label>Show Zone Geometry</label>
            </div>

            {/* Wireframe Feature Controls */}
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

            {/* RESTORED v0.1.15: Cascade Visibility Checkbox */}
            <div className="checkbox-control">
              <input 
                type="checkbox" 
                checked={useCascadeVisibility}
                onChange={(e) => handleCascadeVisibilityToggle(e.target.checked)}
              />
              <label>Cascade Visibility (Hide Parent → Hide Children)</label>
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
              <div style={{ 
                marginTop: '8px', 
                fontSize: '11px', 
                color: '#6c757d',
                fontStyle: 'italic'
              }}>
                💡 Use the sidebar controls to show/hide zones and adjust settings
                <br />
                🔗 Cascade Visibility: {useCascadeVisibility ? 'ON - Hiding parent zones will hide children' : 'OFF - Each zone independent'}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Debug and Hint Toggle Buttons - Always Available */}
      <div style={{ 
        display: 'flex', 
        justifyContent: 'flex-end',
        alignItems: 'center',
        marginBottom: '10px',
        gap: '8px'
      }}>
        {/* Debug Overlays Toggle */}
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

        {/* Controls Hint Toggle */}
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

      {/* 3D Scene Container - Only show when campus is selected */}
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
              />
            )}
            
            {/* Scene3D */}
            <div style={{ 
              marginLeft: showSidebar ? '300px' : '0',
              transition: 'margin-left 0.3s ease'
            }}>
              {!loading ? (
                <Scene3D 
                  mapData={mapData}
                  zoneData={{ zones: checkedZones.length > 0 ? currentZones.filter(z => checkedZones.includes(z.zone_id)) : currentZones }}
                  showCampusZone={showCampusZone}
                  selectedCampusId={selectedCampusId}
                  selectedZoneType={selectedZoneType}
                  zoneSettings={zoneSettings}
                  height={500}
                  width={sceneWidth}
                  showDebugOverlays={showDebugOverlays}
                  showControlsHint={showControlsHint}
                  showZoneLabels={showZoneLabels}
                  showCornerMarkers={showCornerMarkers}
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
            <br />
            🏫 <strong>Selected Campus:</strong> {selectedCampusName} (ID: {selectedCampusId})
            <br />
            🎛️ <strong>v0.1.15 Features:</strong> Campus-First Selection • Zone Boundary Filter • Cascade Visibility Control
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
        </div>
      )}
    </div>
  );
};

export default TDZ_index;