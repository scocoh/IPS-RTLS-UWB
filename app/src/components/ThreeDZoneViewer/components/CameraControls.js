/* Name: CameraControls.js */
/* Version: 0.1.0 */
/* Created: 250719 */
/* Modified: 250719 */
/* Creator: ParcoAdmin + Claude */
/* Modified By: ParcoAdmin + Claude */
/* Description: Camera control buttons for 3D zone viewer */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ThreeDZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from 'react';

const CameraControls = ({
  onResetView,
  onTopView,
  onFrontView,
  onSideView,
  onIsometricView,
  onFitToZones,
  onZoomIn,
  onZoomOut,
  currentView = 'custom'
}) => {
  const controlsStyle = {
    position: 'absolute',
    top: '10px',
    left: '10px',
    background: 'rgba(255, 255, 255, 0.95)',
    padding: '15px',
    borderRadius: '8px',
    border: '1px solid #ccc',
    fontFamily: 'Arial, sans-serif',
    fontSize: '14px',
    zIndex: 1000,
    minWidth: '180px'
  };

  const buttonGridStyle = {
    display: 'grid',
    gridTemplateColumns: 'repeat(2, 1fr)',
    gap: '8px',
    marginBottom: '15px'
  };

  const buttonStyle = {
    padding: '8px 12px',
    border: '1px solid #ddd',
    borderRadius: '4px',
    background: 'white',
    cursor: 'pointer',
    fontSize: '12px',
    transition: 'all 0.2s ease',
    textAlign: 'center'
  };

  const activeButtonStyle = {
    ...buttonStyle,
    background: '#007bff',
    color: 'white',
    borderColor: '#007bff'
  };

  const zoomButtonStyle = {
    ...buttonStyle,
    padding: '6px 8px',
    fontSize: '14px',
    fontWeight: 'bold'
  };

  const sectionStyle = {
    marginBottom: '15px'
  };

  const titleStyle = {
    margin: '0 0 10px 0',
    fontSize: '14px',
    fontWeight: 'bold',
    color: '#333'
  };

  const handleButtonClick = (callback, viewName = null) => {
    return () => {
      if (callback) callback();
      console.log(`📷 Camera view: ${viewName || 'action'}`);
    };
  };

  return (
    <div style={controlsStyle}>
      <h4 style={{ margin: '0 0 15px 0', fontSize: '16px', color: '#333' }}>
        📷 Camera Controls
      </h4>

      {/* View Presets */}
      <div style={sectionStyle}>
        <div style={titleStyle}>View Presets</div>
        <div style={buttonGridStyle}>
          <button
            style={currentView === 'top' ? activeButtonStyle : buttonStyle}
            onClick={handleButtonClick(onTopView, 'top')}
            title="Top-down view"
          >
            ⬇️ Top
          </button>
          <button
            style={currentView === 'front' ? activeButtonStyle : buttonStyle}
            onClick={handleButtonClick(onFrontView, 'front')}
            title="Front view"
          >
            ➡️ Front
          </button>
          <button
            style={currentView === 'side' ? activeButtonStyle : buttonStyle}
            onClick={handleButtonClick(onSideView, 'side')}
            title="Side view"
          >
            ⬅️ Side
          </button>
          <button
            style={currentView === 'isometric' ? activeButtonStyle : buttonStyle}
            onClick={handleButtonClick(onIsometricView, 'isometric')}
            title="Isometric view"
          >
            📐 ISO
          </button>
        </div>
      </div>

      {/* Navigation */}
      <div style={sectionStyle}>
        <div style={titleStyle}>Navigation</div>
        <div style={{ display: 'flex', gap: '8px', marginBottom: '8px' }}>
          <button
            style={zoomButtonStyle}
            onClick={handleButtonClick(onZoomIn)}
            title="Zoom in"
          >
            🔍+
          </button>
          <button
            style={zoomButtonStyle}
            onClick={handleButtonClick(onZoomOut)}
            title="Zoom out"
          >
            🔍-
          </button>
        </div>
        <button
          style={{ ...buttonStyle, width: '100%' }}
          onClick={handleButtonClick(onResetView, 'reset')}
          title="Reset to default view"
        >
          🏠 Reset View
        </button>
      </div>

      {/* Auto-fit */}
      <div style={sectionStyle}>
        <button
          style={{ ...buttonStyle, width: '100%', background: '#28a745', color: 'white', borderColor: '#28a745' }}
          onClick={handleButtonClick(onFitToZones)}
          title="Fit camera to show all zones"
        >
          📏 Fit to Zones
        </button>
      </div>

      {/* Instructions */}
      <div style={{
        fontSize: '11px',
        color: '#666',
        lineHeight: '1.3',
        borderTop: '1px solid #eee',
        paddingTop: '10px'
      }}>
        <div><strong>Mouse Controls:</strong></div>
        <div>• Drag: Rotate view</div>
        <div>• Wheel: Zoom in/out</div>
        <div>• Click: Select zones</div>
      </div>
    </div>
  );
};

export default CameraControls;