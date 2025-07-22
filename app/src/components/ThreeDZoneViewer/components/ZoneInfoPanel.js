/* Name: ZoneInfoPanel.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Information panel for selected zones in 3D viewer */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const ZoneInfoPanel = ({
  selectedZone = null,
  onClose
}) => {
  if (!selectedZone) return null;

  const panelStyle = {
    position: 'absolute',
    bottom: '10px',
    left: '10px',
    background: 'rgba(255, 255, 255, 0.95)',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #ccc',
    minWidth: '250px',
    maxWidth: '400px',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
    zIndex: 1000,
    boxShadow: '0 2px 10px rgba(0,0,0,0.1)'
  };

  const headerStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: '10px',
    borderBottom: '1px solid #eee',
    paddingBottom: '10px'
  };

  const titleStyle = {
    margin: 0,
    fontSize: '16px',
    color: '#333'
  };

  const closeButtonStyle = {
    background: 'none',
    border: 'none',
    fontSize: '18px',
    cursor: 'pointer',
    color: '#666',
    padding: '0',
    marginLeft: '10px'
  };

  const rowStyle = {
    display: 'flex',
    justifyContent: 'space-between',
    marginBottom: '5px'
  };

  const labelStyle = {
    fontWeight: 'bold',
    color: '#555'
  };

  const valueStyle = {
    color: '#333'
  };

  const getZoneTypeLabel = (zoneType) => {
    const types = {
      1: 'Campus L1',
      2: 'Building L3',
      3: 'Floor L4',
      4: 'Wing L5',
      5: 'Room L6',
      10: 'Building Outside L2',
      20: 'Outdoor General',
      901: 'Virtual Subject Zone'
    };
    return types[zoneType] || `Type ${zoneType}`;
  };

  const getZoneTypeIcon = (zoneType) => {
    const icons = {
      1: '🏫',
      2: '🏢',
      3: '🏬',
      4: '🏠',
      5: '🚪',
      10: '🏗️',
      20: '🌳',
      901: '👤'
    };
    return icons[zoneType] || '📍';
  };

  return (
    <div style={panelStyle}>
      <div style={headerStyle}>
        <h4 style={titleStyle}>
          {getZoneTypeIcon(selectedZone.zone_type)} Zone Information
        </h4>
        <button
          onClick={onClose}
          style={closeButtonStyle}
          title="Close"
        >
          ✕
        </button>
      </div>

      <div style={rowStyle}>
        <span style={labelStyle}>Name:</span>
        <span style={valueStyle}>{selectedZone.zone_name}</span>
      </div>

      <div style={rowStyle}>
        <span style={labelStyle}>ID:</span>
        <span style={valueStyle}>{selectedZone.zone_id}</span>
      </div>

      <div style={rowStyle}>
        <span style={labelStyle}>Type:</span>
        <span style={valueStyle}>{getZoneTypeLabel(selectedZone.zone_type)}</span>
      </div>

      {selectedZone.parent_zone_id && (
        <div style={rowStyle}>
          <span style={labelStyle}>Parent Zone:</span>
          <span style={valueStyle}>{selectedZone.parent_zone_id}</span>
        </div>
      )}

      {selectedZone.map_id && (
        <div style={rowStyle}>
          <span style={labelStyle}>Map ID:</span>
          <span style={valueStyle}>{selectedZone.map_id}</span>
        </div>
      )}

      {selectedZone.children && selectedZone.children.length > 0 && (
        <div style={rowStyle}>
          <span style={labelStyle}>Child Zones:</span>
          <span style={valueStyle}>{selectedZone.children.length}</span>
        </div>
      )}

      {/* Region data if available */}
      {selectedZone.regions && (
        <>
          <hr style={{ margin: '10px 0', border: 'none', borderTop: '1px solid #eee' }} />
          <div style={{ fontSize: '12px', color: '#666' }}>
            <div style={rowStyle}>
              <span style={labelStyle}>Regions:</span>
              <span style={valueStyle}>{selectedZone.regions.length}</span>
            </div>
            {selectedZone.regions[0] && (
              <>
                <div style={rowStyle}>
                  <span style={labelStyle}>X Range:</span>
                  <span style={valueStyle}>
                    {selectedZone.regions[0].n_min_x?.toFixed(1)} - {selectedZone.regions[0].n_max_x?.toFixed(1)}
                  </span>
                </div>
                <div style={rowStyle}>
                  <span style={labelStyle}>Y Range:</span>
                  <span style={valueStyle}>
                    {selectedZone.regions[0].n_min_y?.toFixed(1)} - {selectedZone.regions[0].n_max_y?.toFixed(1)}
                  </span>
                </div>
                <div style={rowStyle}>
                  <span style={labelStyle}>Z Range:</span>
                  <span style={valueStyle}>
                    {selectedZone.regions[0].n_min_z?.toFixed(1)} - {selectedZone.regions[0].n_max_z?.toFixed(1)}
                  </span>
                </div>
              </>
            )}
          </div>
        </>
      )}

      <div style={{ 
        marginTop: '10px', 
        fontSize: '12px', 
        color: '#888',
        fontStyle: 'italic',
        textAlign: 'center'
      }}>
        💡 Click on zones in 3D view to see details
      </div>
    </div>
  );
};

export default ZoneInfoPanel;