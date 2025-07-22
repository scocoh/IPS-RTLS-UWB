/* Name: ZoneControlsSidebar.js */
/* Version: 0.1.1 */
/* Created: 250720 */
/* Modified: 250720 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Sidebar component for dynamic zone control - visibility, transparency, colors */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const ZoneControlsSidebar = ({
  zoneSettings = {},
  availableZones = [],
  onZoneSettingChange,
  onResetToDefaults,
  isVisible = true,
  // NEW: Multi-map support props
  selectedMapFilter = 'all', // 'all', or specific map_id
  onMapFilterChange,
  showMapInfo = true
}) => {
  // Get unique maps from available zones
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

  // Filter zones by selected map
  const filteredZones = selectedMapFilter === 'all' 
    ? availableZones 
    : availableZones.filter(zone => zone.map_id === parseInt(selectedMapFilter));

  // Default zone colors mapping
  const defaultColors = {
    422: '#00ff00', // Campus = Green
    427: '#ff4500', // Wing = Orange Red
    // Add more defaults as needed
    1: '#ff0000',   // Type 1 (Campus) = Red
    2: '#00ff00',   // Type 2 (Building) = Green  
    3: '#0000ff',   // Type 3 (Floor) = Blue
    4: '#ff8800',   // Type 4 (Wing) = Orange
    5: '#8800ff'    // Type 5 (Room) = Purple
  };

  // Get default color for zone
  const getDefaultColor = (zoneId, zoneType) => {
    return defaultColors[zoneId] || defaultColors[zoneType] || '#888888';
  };

  // Handle individual zone setting changes
  const handleSettingChange = (zoneId, settingName, value) => {
    if (onZoneSettingChange) {
      onZoneSettingChange(zoneId, settingName, value);
    }
  };

  // Handle reset to defaults
  const handleReset = () => {
    if (onResetToDefaults) {
      onResetToDefaults();
    }
  };

  if (!isVisible) return null;

  const sidebarStyle = {
    position: 'absolute',
    left: '10px',
    top: '10px',
    width: '280px',
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

  const zoneGroupStyle = {
    marginBottom: '20px',
    padding: '12px',
    border: '1px solid #e0e0e0',
    borderRadius: '6px',
    background: 'rgba(248, 249, 250, 0.8)'
  };

  const zoneHeaderStyle = {
    margin: '0 0 10px 0',
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#495057'
  };

  const controlRowStyle = {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '8px',
    gap: '8px'
  };

  const labelStyle = {
    minWidth: '70px',
    fontSize: '12px',
    color: '#666'
  };

  const checkboxStyle = {
    marginRight: '8px'
  };

  const sliderStyle = {
    flex: 1,
    marginRight: '8px'
  };

  const colorInputStyle = {
    width: '40px',
    height: '25px',
    border: 'none',
    borderRadius: '4px',
    cursor: 'pointer'
  };

  const valueDisplayStyle = {
    minWidth: '35px',
    fontSize: '11px',
    color: '#666',
    textAlign: 'right'
  };

  return (
    <div style={sidebarStyle}>
      <div style={headerStyle}>
        <span>🎛️ Zone Controls</span>
        <button 
          onClick={handleReset}
          style={resetButtonStyle}
          title="Reset all settings to defaults"
        >
          Reset
        </button>
      </div>

      {/* NEW: Multi-Map Filter Controls */}
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
          
          {/* Map Summary */}
          <div style={{ 
            fontSize: '11px', 
            color: '#666', 
            marginTop: '5px',
            fontStyle: 'italic'
          }}>
            {availableMaps.map(map => (
              <div key={map.id}>
                Map {map.id}: {map.zones.map(z => z.zone_name).join(', ')}
              </div>
            ))}
          </div>
        </div>
      )}

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
            opacity: zone.zone_id === 422 ? 0.2 : 0.7, // Campus subtle, others prominent
            color: getDefaultColor(zone.zone_id, zone.zone_type)
          };

          return (
            <div key={zone.zone_id} style={zoneGroupStyle}>
              <div style={zoneHeaderStyle}>
                {zone.zone_name} 
                <span style={{ fontSize: '12px', color: '#888' }}>
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
                fontSize: '11px', 
                color: '#888', 
                marginTop: '8px',
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

      {/* Instructions */}
      <div style={{ 
        marginTop: '20px',
        padding: '10px',
        background: 'rgba(0, 123, 255, 0.1)',
        borderRadius: '4px',
        fontSize: '12px',
        color: '#495057'
      }}>
        <div style={{ fontWeight: 'bold', marginBottom: '5px' }}>
          💡 Multi-Map Instructions:
        </div>
        <div>• Filter zones by map if needed</div>
        <div>• All maps use unified coordinates</div>
        <div>• Toggle visibility on/off</div>
        <div>• Adjust transparency (0-100%)</div>
        <div>• Pick custom colors</div>
        <div>• Reset button restores defaults</div>
      </div>
    </div>
  );
};

export default ZoneControlsSidebar;