/* Name: ZoneControlsSidebar.js */
/* Version: 0.1.2 */
/* Created: 250720 */
/* Modified: 250722 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Sidebar component for dynamic zone control AND real-time tag controls - visibility, transparency, colors, tag management */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.2: REAL-TIME TAG CONTROLS - Added tag connection toggle, tag selection, tag appearance controls */
/* - 0.1.1: Multi-map support, map filtering */

import React, { useState } from 'react';

const ZoneControlsSidebar = ({
  // Existing zone props (unchanged)
  zoneSettings = {},
  availableZones = [],
  onZoneSettingChange,
  onResetToDefaults,
  isVisible = true,
  selectedMapFilter = 'all',
  onMapFilterChange,
  showMapInfo = true,
  
  // NEW: Real-time tag props
  tagConnectionEnabled = false,
  onTagConnectionToggle,
  tagConnectionStatus = 'disconnected',
  allTagsData = {},
  selectedTags = new Set(),
  onTagSelectionChange,
  tagStats = { totalTags: 0, activeTags: 0, tagRate: 0 },
  tagConfig = {
    showLabels: true,
    showTrails: false,
    sphereRadius: 3,
    activeColor: '#00ff00'
  },
  onTagConfigChange
}) => {
  console.log(`🎛️ ZoneControlsSidebar v0.1.2: Rendering with ${availableZones.length} zones, ${Object.keys(allTagsData).length} tags`);

  // NEW: Collapsible sections state
  const [sectionsCollapsed, setSectionsCollapsed] = useState({
    zones: false,
    tags: false
  });

  // Toggle section collapse
  const toggleSection = (section) => {
    setSectionsCollapsed(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  // Get unique maps from available zones (existing functionality)
  const availableMaps = [...new Set(availableZones.map(zone => zone.map_id))]
    .sort((a, b) => a - b)
    .map(mapId => {
      const zoneWithMap = availableZones.find(z => z.map_id === mapId);
      return {
        id: mapId,
        name: `Map ${mapId}`,
        zones: availableZones.filter(z => z.map_id === mapId)
      };
    });

  // Filter zones by selected map (existing functionality)
  const filteredZones = selectedMapFilter === 'all' 
    ? availableZones 
    : availableZones.filter(zone => zone.map_id === parseInt(selectedMapFilter));

  // Default zone colors mapping (existing functionality)
  const defaultColors = {
    422: '#00ff00', // Campus = Green
    427: '#ff4500', // Wing = Orange Red
    1: '#ff0000',   // Type 1 (Campus) = Red
    2: '#00ff00',   // Type 2 (Building) = Green  
    3: '#0000ff',   // Type 3 (Floor) = Blue
    4: '#ff8800',   // Type 4 (Wing) = Orange
    5: '#8800ff'    // Type 5 (Room) = Purple
  };

  // Get default color for zone (existing functionality)
  const getDefaultColor = (zoneId, zoneType) => {
    return defaultColors[zoneId] || defaultColors[zoneType] || '#888888';
  };

  // Handle individual zone setting changes (existing functionality)
  const handleSettingChange = (zoneId, settingName, value) => {
    if (onZoneSettingChange) {
      onZoneSettingChange(zoneId, settingName, value);
    }
  };

  // Handle reset to defaults (existing functionality)
  const handleReset = () => {
    if (onResetToDefaults) {
      onResetToDefaults();
    }
  };

  // NEW: Handle tag connection toggle
  const handleTagConnectionToggle = () => {
    console.log(`🔌 Toggling tag connection: ${tagConnectionEnabled ? 'disconnect' : 'connect'}`);
    if (onTagConnectionToggle) {
      onTagConnectionToggle(!tagConnectionEnabled);
    }
  };

  // NEW: Handle individual tag selection
  const handleTagSelectionToggle = (tagId) => {
    console.log(`🏷️ Toggling tag selection: ${tagId}`);
    if (onTagSelectionChange) {
      onTagSelectionChange(tagId);
    }
  };

  // NEW: Handle select all/none tags
  const handleTagSelectAll = () => {
    const allTagIds = Object.keys(allTagsData);
    console.log(`✅ Selecting all ${allTagIds.length} tags`);
    if (onTagSelectionChange) {
      onTagSelectionChange('selectAll', allTagIds);
    }
  };

  const handleTagSelectNone = () => {
    console.log(`🚫 Clearing all tag selections`);
    if (onTagSelectionChange) {
      onTagSelectionChange('selectNone');
    }
  };

  // NEW: Handle tag configuration changes
  const handleTagConfigChange = (configKey, value) => {
    console.log(`🎨 Changing tag config ${configKey} to ${value}`);
    if (onTagConfigChange) {
      onTagConfigChange(configKey, value);
    }
  };

  if (!isVisible) return null;

  const sidebarStyle = {
    position: 'absolute',
    left: '10px',
    top: '10px',
    width: '300px', // Slightly wider for tag controls
    height: 'calc(100% - 20px)',
    background: 'rgba(255, 255, 255, 0.95)',
    border: '1px solid #ccc',
    borderRadius: '8px',
    padding: '15px',
    overflowY: 'auto',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
    zIndex: 1000,
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  };

  const headerStyle = {
    margin: '0 0 15px 0',
    fontSize: '16px',
    color: '#333',
    borderBottom: '2px solid #007bff',
    paddingBottom: '8px',
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center'
  };

  const resetButtonStyle = {
    background: '#6c757d',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '4px 8px',
    fontSize: '12px',
    cursor: 'pointer'
  };

  // NEW: Section header style
  const sectionHeaderStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: '8px 12px',
    background: 'rgba(0, 123, 255, 0.1)',
    borderRadius: '4px',
    margin: '10px 0',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#495057'
  };

  const zoneGroupStyle = {
    marginBottom: '15px', // Reduced for more compact layout
    padding: '10px', // Reduced padding
    border: '1px solid #e0e0e0',
    borderRadius: '6px',
    background: 'rgba(248, 249, 250, 0.8)'
  };

  const zoneHeaderStyle = {
    margin: '0 0 8px 0', // Reduced margin
    fontSize: '13px', // Slightly smaller
    fontWeight: 'bold',
    color: '#495057'
  };

  const controlRowStyle = {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '6px', // Reduced margin
    gap: '6px' // Reduced gap
  };

  const labelStyle = {
    minWidth: '60px', // Reduced width
    fontSize: '11px', // Smaller font
    color: '#666'
  };

  const checkboxStyle = {
    marginRight: '6px' // Reduced margin
  };

  const sliderStyle = {
    flex: 1,
    marginRight: '6px' // Reduced margin
  };

  const colorInputStyle = {
    width: '35px', // Slightly smaller
    height: '22px', // Slightly smaller
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  };

  const valueDisplayStyle = {
    minWidth: '30px', // Reduced width
    fontSize: '10px', // Smaller font
    color: '#666',
    textAlign: 'right'
  };

  // NEW: Tag-specific styles
  const tagStatusStyle = {
    padding: '8px 12px',
    borderRadius: '4px',
    marginBottom: '10px',
    fontSize: '12px',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between'
  };

  const getTagStatusStyle = () => {
    const baseStyle = { ...tagStatusStyle };
    switch (tagConnectionStatus) {
      case 'connected':
        return { ...baseStyle, background: '#d4edda', color: '#155724', border: '1px solid #c3e6cb' };
      case 'connecting':
        return { ...baseStyle, background: '#fff3cd', color: '#856404', border: '1px solid #ffeaa7' };
      case 'error':
        return { ...baseStyle, background: '#f8d7da', color: '#721c24', border: '1px solid #f5c6cb' };
      default:
        return { ...baseStyle, background: '#e2e3e4', color: '#6c757d', border: '1px solid #ced4da' };
    }
  };

  const tagControlButtonStyle = {
    background: tagConnectionEnabled ? '#dc3545' : '#28a745',
    color: 'white',
    border: 'none',
    borderRadius: '4px',
    padding: '4px 8px',
    fontSize: '11px',
    cursor: 'pointer'
  };

  return (
    <div style={sidebarStyle}>
      <div style={headerStyle}>
        <span>🎛️ Scene Controls</span>
        <button 
          onClick={handleReset}
          style={resetButtonStyle}
          title="Reset zone settings to defaults"
        >
          Reset Zones
        </button>
      </div>

      {/* NEW: REAL-TIME TAGS SECTION */}
      <div style={sectionHeaderStyle} onClick={() => toggleSection('tags')}>
        <span>🏷️ Real-Time Tags</span>
        <span>{sectionsCollapsed.tags ? '▶' : '▼'}</span>
      </div>

      {!sectionsCollapsed.tags && (
        <>
          {/* Tag Connection Status & Control */}
          <div style={getTagStatusStyle()}>
            <div>
              <div style={{ fontWeight: 'bold' }}>
                Connection: {tagConnectionStatus.toUpperCase()}
              </div>
              <div style={{ fontSize: '10px', opacity: 0.8 }}>
                Tags: {tagStats.activeTags} | Rate: {tagStats.tagRate.toFixed(1)}/s
              </div>
            </div>
            <button
              onClick={handleTagConnectionToggle}
              style={tagControlButtonStyle}
            >
              {tagConnectionEnabled ? 'Disconnect' : 'Connect'}
            </button>
          </div>

          {/* Tag Selection Controls */}
          {Object.keys(allTagsData).length > 0 && (
            <div style={{
              background: 'rgba(248, 249, 250, 0.8)',
              border: '1px solid #e0e0e0',
              borderRadius: '4px',
              padding: '10px',
              marginBottom: '10px'
            }}>
              <div style={{ 
                fontSize: '12px', 
                fontWeight: 'bold', 
                marginBottom: '8px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center'
              }}>
                <span>Tag Selection ({selectedTags.size}/{Object.keys(allTagsData).length})</span>
                <div style={{ display: 'flex', gap: '4px' }}>
                  <button
                    onClick={handleTagSelectAll}
                    style={{
                      background: '#007bff',
                      color: 'white',
                      border: 'none',
                      borderRadius: '3px',
                      padding: '2px 6px',
                      fontSize: '10px',
                      cursor: 'pointer'
                    }}
                  >
                    All
                  </button>
                  <button
                    onClick={handleTagSelectNone}
                    style={{
                      background: '#6c757d',
                      color: 'white',
                      border: 'none',
                      borderRadius: '3px',
                      padding: '2px 6px',
                      fontSize: '10px',
                      cursor: 'pointer'
                    }}
                  >
                    None
                  </button>
                </div>
              </div>

              {/* Individual Tag Checkboxes */}
              <div style={{ maxHeight: '120px', overflowY: 'auto' }}>
                {Object.entries(allTagsData).map(([tagId, tagData]) => (
                  <div key={tagId} style={{
                    display: 'flex',
                    alignItems: 'center',
                    marginBottom: '4px',
                    fontSize: '11px'
                  }}>
                    <input
                      type="checkbox"
                      checked={selectedTags.has(tagId)}
                      onChange={() => handleTagSelectionToggle(tagId)}
                      style={{ marginRight: '6px' }}
                    />
                    <span style={{ flex: 1 }}>{tagId}</span>
                    <span style={{ fontSize: '10px', color: '#666' }}>
                      ({tagData.x.toFixed(1)}, {tagData.y.toFixed(1)})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Tag Appearance Controls */}
          <div style={{
            background: 'rgba(248, 249, 250, 0.8)',
            border: '1px solid #e0e0e0',
            borderRadius: '4px',
            padding: '10px',
            marginBottom: '10px'
          }}>
            <div style={{ fontSize: '12px', fontWeight: 'bold', marginBottom: '8px' }}>
              Tag Appearance
            </div>

            {/* Show Labels Toggle */}
            <div style={controlRowStyle}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={tagConfig.showLabels}
                  onChange={(e) => handleTagConfigChange('showLabels', e.target.checked)}
                  style={checkboxStyle}
                />
                <span style={labelStyle}>Labels</span>
              </label>
            </div>

            {/* Show Trails Toggle */}
            <div style={controlRowStyle}>
              <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={tagConfig.showTrails}
                  onChange={(e) => handleTagConfigChange('showTrails', e.target.checked)}
                  style={checkboxStyle}
                />
                <span style={labelStyle}>Trails</span>
              </label>
            </div>

            {/* Sphere Size Slider */}
            <div style={controlRowStyle}>
              <span style={labelStyle}>Size:</span>
              <input
                type="range"
                min="1"
                max="8"
                step="0.5"
                value={tagConfig.sphereRadius}
                onChange={(e) => handleTagConfigChange('sphereRadius', parseFloat(e.target.value))}
                style={sliderStyle}
              />
              <span style={valueDisplayStyle}>
                {tagConfig.sphereRadius}
              </span>
            </div>

            {/* Tag Color Picker */}
            <div style={controlRowStyle}>
              <span style={labelStyle}>Color:</span>
              <input
                type="color"
                value={tagConfig.activeColor}
                onChange={(e) => handleTagConfigChange('activeColor', e.target.value)}
                style={colorInputStyle}
              />
              <span style={valueDisplayStyle}>
                {tagConfig.activeColor.toUpperCase()}
              </span>
            </div>
          </div>
        </>
      )}

      {/* EXISTING: ZONE CONTROLS SECTION (unchanged functionality) */}
      <div style={sectionHeaderStyle} onClick={() => toggleSection('zones')}>
        <span>🏢 Zone Controls</span>
        <span>{sectionsCollapsed.zones ? '▶' : '▼'}</span>
      </div>

      {!sectionsCollapsed.zones && (
        <>
          {/* Multi-Map Filter Controls (existing) */}
          {availableMaps.length > 1 && (
            <div style={{
              marginBottom: '15px',
              padding: '10px',
              background: 'rgba(0, 123, 255, 0.1)',
              borderRadius: '4px',
              border: '1px solid rgba(0, 123, 255, 0.2)'
            }}>
              <div style={{ 
                fontSize: '12px', 
                fontWeight: 'bold', 
                marginBottom: '8px',
                color: '#495057'
              }}>
                🗺️ Map Filter:
              </div>
              <select
                value={selectedMapFilter}
                onChange={(e) => onMapFilterChange && onMapFilterChange(e.target.value)}
                style={{
                  width: '100%',
                  padding: '4px 8px',
                  border: '1px solid #ced4da',
                  borderRadius: '4px',
                  fontSize: '12px'
                }}
              >
                <option value="all">All Maps ({availableZones.length} zones)</option>
                {availableMaps.map(map => (
                  <option key={map.id} value={map.id}>
                    Map {map.id} ({map.zones.length} zones)
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Zone Controls (existing functionality) */}
          {filteredZones.length === 0 ? (
            <div style={{ 
              textAlign: 'center', 
              color: '#666', 
              fontStyle: 'italic',
              padding: '20px 0'
            }}>
              {selectedMapFilter === 'all' ? 'No zones available' : `No zones in Map ${selectedMapFilter}`}
            </div>
          ) : (
            filteredZones.map(zone => {
              const settings = zoneSettings[zone.zone_id] || {
                visible: true,
                opacity: zone.zone_id === 422 ? 0.2 : 0.7,
                color: getDefaultColor(zone.zone_id, zone.zone_type)
              };

              return (
                <div key={zone.zone_id} style={zoneGroupStyle}>
                  <div style={zoneHeaderStyle}>
                    {zone.zone_name} 
                    <span style={{ fontSize: '11px', color: '#888' }}>
                      (ID: {zone.zone_id})
                    </span>
                  </div>

                  {/* Visibility Toggle */}
                  <div style={controlRowStyle}>
                    <label style={{ display: 'flex', alignItems: 'center', cursor: 'pointer' }}>
                      <input
                        type="checkbox"
                        checked={settings.visible}
                        onChange={(e) => handleSettingChange(zone.zone_id, 'visible', e.target.checked)}
                        style={checkboxStyle}
                      />
                      <span style={labelStyle}>Visible</span>
                    </label>
                  </div>

                  {/* Transparency Slider */}
                  <div style={controlRowStyle}>
                    <span style={labelStyle}>Opacity:</span>
                    <input
                      type="range"
                      min="0"
                      max="1"
                      step="0.1"
                      value={settings.opacity}
                      onChange={(e) => handleSettingChange(zone.zone_id, 'opacity', parseFloat(e.target.value))}
                      style={sliderStyle}
                      disabled={!settings.visible}
                    />
                    <span style={valueDisplayStyle}>
                      {Math.round(settings.opacity * 100)}%
                    </span>
                  </div>

                  {/* Color Picker */}
                  <div style={controlRowStyle}>
                    <span style={labelStyle}>Color:</span>
                    <input
                      type="color"
                      value={settings.color}
                      onChange={(e) => handleSettingChange(zone.zone_id, 'color', e.target.value)}
                      style={colorInputStyle}
                      disabled={!settings.visible}
                    />
                    <span style={valueDisplayStyle}>
                      {settings.color.toUpperCase()}
                    </span>
                  </div>

                  {/* Zone Type & Map Info */}
                  <div style={{ 
                    fontSize: '10px', 
                    color: '#888', 
                    marginTop: '6px',
                    fontStyle: 'italic'
                  }}>
                    Type: {zone.zone_type} | Map: {zone.map_id}
                    {showMapInfo && zone.map_id && (
                      <span style={{ color: zone.map_id === 39 ? '#28a745' : '#fd7e14' }}>
                        {zone.map_id === 39 ? ' (Campus)' : ' (Building)'}
                      </span>
                    )}
                  </div>
                </div>
              );
            })
          )}
        </>
      )}

      {/* Instructions (updated) */}
      <div style={{ 
        marginTop: '15px',
        padding: '8px',
        background: 'rgba(0, 123, 255, 0.1)',
        borderRadius: '4px',
        fontSize: '11px',
        color: '#495057'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '4px' }}>
          💡 v0.1.2 Instructions:
        </div>
        <div>• 🏷️ Connect to real-time tag stream</div>
        <div>• ✅ Select tags to display in 3D</div>
        <div>• 🎨 Configure tag appearance</div>
        <div>• 🏢 Control zone visibility/colors</div>
        <div>• 🗺️ Filter by map if needed</div>
      </div>
    </div>
  );
};

export default ZoneControlsSidebar;