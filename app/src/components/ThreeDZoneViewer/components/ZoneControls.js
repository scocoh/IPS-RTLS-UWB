/* Name: ZoneControls.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Zone visibility and type controls for 3D visualization */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const ZoneControls = ({
  showCampusZones = true,
  showBuildingZones = true,
  showFloorZones = true,
  showWingZones = true,
  showRoomZones = true,
  onToggleCampus,
  onToggleBuilding,
  onToggleFloor,
  onToggleWing,
  onToggleRoom,
  zoneStats = {}
}) => {
  const controlStyle = {
    position: 'absolute',
    top: '10px',
    right: '10px',
    background: 'rgba(255, 255, 255, 0.95)',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #ccc',
    minWidth: '200px',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
    zIndex: 1000
  };

  const checkboxStyle = {
    marginRight: '8px'
  };

  const labelStyle = {
    display: 'flex',
    alignItems: 'center',
    marginBottom: '8px',
    cursor: 'pointer'
  };

  const countStyle = {
    color: '#666',
    fontSize: '12px',
    marginLeft: 'auto'
  };

  return (
    <div style={controlStyle}>
      <h4 style={{ margin: '0 0 15px 0', fontSize: '16px', color: '#333' }}>
        🏗️ Zone Visibility
      </h4>
      
      <label style={labelStyle}>
        <input
          type="checkbox"
          checked={showCampusZones}
          onChange={onToggleCampus}
          style={checkboxStyle}
        />
        <span style={{ color: '#ff0000' }}>🏫 Campus L1</span>
        <span style={countStyle}>({zoneStats.campus || 0})</span>
      </label>

      <label style={labelStyle}>
        <input
          type="checkbox"
          checked={showBuildingZones}
          onChange={onToggleBuilding}
          style={checkboxStyle}
        />
        <span style={{ color: '#00ff00' }}>🏢 Building L2/L3</span>
        <span style={countStyle}>({zoneStats.building || 0})</span>
      </label>

      <label style={labelStyle}>
        <input
          type="checkbox"
          checked={showFloorZones}
          onChange={onToggleFloor}
          style={checkboxStyle}
        />
        <span style={{ color: '#0000ff' }}>🏬 Floor L4</span>
        <span style={countStyle}>({zoneStats.floor || 0})</span>
      </label>

      <label style={labelStyle}>
        <input
          type="checkbox"
          checked={showWingZones}
          onChange={onToggleWing}
          style={checkboxStyle}
        />
        <span style={{ color: '#ff8800' }}>🏠 Wing L5</span>
        <span style={countStyle}>({zoneStats.wing || 0})</span>
      </label>

      <label style={labelStyle}>
        <input
          type="checkbox"
          checked={showRoomZones}
          onChange={onToggleRoom}
          style={checkboxStyle}
        />
        <span style={{ color: '#8800ff' }}>🚪 Room L6</span>
        <span style={countStyle}>({zoneStats.room || 0})</span>
      </label>

      <hr style={{ margin: '15px 0 10px 0', border: 'none', borderTop: '1px solid #ddd' }} />
      
      <div style={{ fontSize: '12px', color: '#666' }}>
        <div>Total Zones: {Object.values(zoneStats).reduce((a, b) => a + b, 0)}</div>
        <div style={{ marginTop: '5px', fontStyle: 'italic' }}>
          💡 Toggle zones on/off to manage visibility
        </div>
      </div>
    </div>
  );
};

export default ZoneControls;