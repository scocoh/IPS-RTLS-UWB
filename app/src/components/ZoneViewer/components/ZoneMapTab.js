/* Name: ZoneMapTab.js */
/* Version: 0.1.6 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Map display tab component for ZoneViewer with advanced zone styling */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";
import ZoneViewerMap from "./ZoneViewerMap";

const ZoneMapTab = ({
  mapId,
  zones,
  checkedZones,
  vertices,
  useLeaflet,
  setUseLeaflet,
  selectedZone,
  selectedZoneData,
  selectedMapId,
  availableMaps,
  zoneStyle,
  setZoneStyle
}) => {
  
  if (!selectedZone) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>
        <h4>No Zone Selected</h4>
        <p>Please select a zone from the Zone Selection tab to view the map.</p>
      </div>
    );
  }

  if (!mapId) {
    return (
      <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>
        <h4>No Map Selected</h4>
        <p>Please select a map from the Zone Selection tab to view it.</p>
        {availableMaps.length > 0 && (
          <p>Available maps: {availableMaps.map(m => `Map ${m.mapId} (${m.zoneName})`).join(', ')}</p>
        )}
      </div>
    );
  }

  // Find the selected map details
  const selectedMapDetails = availableMaps.find(m => m.mapId === mapId);

  // Update zone style properties
  const updateZoneStyle = (property, value) => {
    setZoneStyle(prev => ({
      ...prev,
      [property]: value
    }));
  };

  // Preset style configurations
  const applyPreset = (preset) => {
    const presets = {
      subtle: {
        fillOpacity: 10,
        lineOpacity: 40,
        lineColor: '#ff0000',
        vertexColor: '#ff0000'
      },
      balanced: {
        fillOpacity: 30,
        lineOpacity: 70,
        lineColor: '#ff0000',
        vertexColor: '#ff0000'
      },
      strong: {
        fillOpacity: 60,
        lineOpacity: 100,
        lineColor: '#ff0000',
        vertexColor: '#ff0000'
      },
      blueprint: {
        fillOpacity: 15,
        lineOpacity: 80,
        lineColor: '#0066cc',
        vertexColor: '#0066cc'
      },
      forest: {
        fillOpacity: 25,
        lineOpacity: 75,
        lineColor: '#228b22',
        vertexColor: '#228b22'
      }
    };
    
    if (presets[preset]) {
      setZoneStyle(prev => ({ ...prev, ...presets[preset] }));
    }
  };

  return (
    <div>
      <div style={{ marginBottom: "15px", padding: "10px", backgroundColor: "#f8f9fa", borderRadius: "5px" }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", flexWrap: "wrap", gap: "10px" }}>
          <div>
            <strong>Selected Zone:</strong> {selectedZoneData?.x_nm_zn || selectedZone} | 
            <strong> Displaying Map:</strong> {mapId} {selectedMapDetails && `(${selectedMapDetails.zoneName})`} | 
            <strong> Zones Checked:</strong> {checkedZones.length} | 
            <strong> Vertices:</strong> {vertices.length}
          </div>
          
          {/* Render Options */}
          <div style={{ display: "flex", alignItems: "center", gap: "15px" }}>
            <label style={{ display: "flex", alignItems: "center", gap: "5px", cursor: "pointer" }}>
              <input 
                type="checkbox" 
                checked={useLeaflet} 
                onChange={(e) => setUseLeaflet(e.target.checked)} 
              />
              <span style={{ fontSize: "14px", fontWeight: "500" }}>Render with Leaflet</span>
            </label>
            
            <span style={{ 
              fontSize: "12px", 
              color: useLeaflet ? "#28a745" : "#6c757d",
              padding: "4px 8px",
              borderRadius: "12px",
              backgroundColor: useLeaflet ? "#d4edda" : "#e2e3e4",
              fontWeight: "500"
            }}>
              {useLeaflet ? "🗺️ Leaflet" : "📐 Canvas"}
            </span>
          </div>
        </div>
        
        {/* Advanced Zone Styling Controls */}
        <div style={{ 
          marginTop: "12px", 
          padding: "12px", 
          backgroundColor: "#ffffff", 
          borderRadius: "6px", 
          border: "1px solid #e0e0e0" 
        }}>
          <div style={{ marginBottom: "12px", borderBottom: "1px solid #eee", paddingBottom: "8px" }}>
            <h5 style={{ margin: 0, fontSize: "14px", fontWeight: "600", color: "#495057" }}>
              🎨 Zone Appearance Controls
            </h5>
          </div>

          {/* Transparency Controls */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px", marginBottom: "15px" }}>
            {/* Fill Opacity */}
            <div>
              <label style={{ fontSize: "13px", fontWeight: "500", color: "#495057", display: "block", marginBottom: "5px" }}>
                Fill Transparency:
              </label>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={zoneStyle.fillOpacity}
                  onChange={(e) => updateZoneStyle('fillOpacity', parseInt(e.target.value))}
                  style={{ flex: 1, minWidth: "80px" }}
                />
                <span style={{ fontSize: "12px", fontWeight: "500", color: "#6c757d", minWidth: "35px", textAlign: "right" }}>
                  {zoneStyle.fillOpacity}%
                </span>
              </div>
            </div>

            {/* Line Opacity */}
            <div>
              <label style={{ fontSize: "13px", fontWeight: "500", color: "#495057", display: "block", marginBottom: "5px" }}>
                Line/Vertex Transparency:
              </label>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <input
                  type="range"
                  min="0"
                  max="100"
                  value={zoneStyle.lineOpacity}
                  onChange={(e) => updateZoneStyle('lineOpacity', parseInt(e.target.value))}
                  style={{ flex: 1, minWidth: "80px" }}
                />
                <span style={{ fontSize: "12px", fontWeight: "500", color: "#6c757d", minWidth: "35px", textAlign: "right" }}>
                  {zoneStyle.lineOpacity}%
                </span>
              </div>
            </div>
          </div>

          {/* Color Controls */}
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "15px", marginBottom: "15px" }}>
            {/* Line Color */}
            <div>
              <label style={{ fontSize: "13px", fontWeight: "500", color: "#495057", display: "block", marginBottom: "5px" }}>
                Line Color:
              </label>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <input
                  type="color"
                  value={zoneStyle.lineColor}
                  onChange={(e) => updateZoneStyle('lineColor', e.target.value)}
                  style={{ width: "40px", height: "30px", border: "1px solid #ddd", borderRadius: "4px", cursor: "pointer" }}
                />
                <input
                  type="text"
                  value={zoneStyle.lineColor}
                  onChange={(e) => updateZoneStyle('lineColor', e.target.value)}
                  style={{ flex: 1, padding: "4px 8px", border: "1px solid #ddd", borderRadius: "4px", fontSize: "12px" }}
                  placeholder="#ff0000"
                />
              </div>
            </div>

            {/* Vertex Color */}
            <div>
              <label style={{ fontSize: "13px", fontWeight: "500", color: "#495057", display: "block", marginBottom: "5px" }}>
                Vertex Color:
              </label>
              <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                <input
                  type="color"
                  value={zoneStyle.vertexColor}
                  onChange={(e) => updateZoneStyle('vertexColor', e.target.value)}
                  style={{ width: "40px", height: "30px", border: "1px solid #ddd", borderRadius: "4px", cursor: "pointer" }}
                />
                <input
                  type="text"
                  value={zoneStyle.vertexColor}
                  onChange={(e) => updateZoneStyle('vertexColor', e.target.value)}
                  style={{ flex: 1, padding: "4px 8px", border: "1px solid #ddd", borderRadius: "4px", fontSize: "12px" }}
                  placeholder="#ff0000"
                />
              </div>
            </div>
          </div>

          {/* Preset Buttons */}
          <div style={{ marginBottom: "8px" }}>
            <label style={{ fontSize: "13px", fontWeight: "500", color: "#495057", display: "block", marginBottom: "8px" }}>
              Quick Presets:
            </label>
            <div style={{ display: "flex", gap: "6px", flexWrap: "wrap" }}>
              {[
                { key: 'subtle', label: 'Subtle', color: '#f8f9fa' },
                { key: 'balanced', label: 'Balanced', color: '#e9ecef' },
                { key: 'strong', label: 'Strong', color: '#dee2e6' },
                { key: 'blueprint', label: 'Blueprint', color: '#cce7ff' },
                { key: 'forest', label: 'Forest', color: '#d4f5d4' }
              ].map(preset => (
                <button
                  key={preset.key}
                  onClick={() => applyPreset(preset.key)}
                  style={{ 
                    padding: "5px 10px", 
                    fontSize: "11px", 
                    border: "1px solid #ddd", 
                    borderRadius: "4px", 
                    backgroundColor: preset.color,
                    color: "#495057",
                    cursor: "pointer",
                    transition: "all 0.2s"
                  }}
                  onMouseOver={(e) => e.target.style.transform = "translateY(-1px)"}
                  onMouseOut={(e) => e.target.style.transform = "translateY(0)"}
                >
                  {preset.label}
                </button>
              ))}
            </div>
          </div>
          
          <div style={{ fontSize: "11px", color: "#6c757d", marginTop: "8px" }}>
            💡 <strong>Fill transparency</strong> affects zone interior shading. <strong>Line transparency</strong> affects borders and vertex markers. Colors can be customized independently.
          </div>
        </div>
        
        {/* Show map selection details */}
        <div style={{ marginTop: "8px", fontSize: "12px", color: "#666", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            {selectedMapDetails ? (
              <span>🗺️ Showing map from: <strong>{selectedMapDetails.zoneName}</strong> (Zone {selectedMapDetails.zoneId})</span>
            ) : (
              <span>🗺️ Map ID: {mapId}</span>
            )}
          </div>
          
          {availableMaps.length > 1 && (
            <div>
              <span style={{ color: "#007bff" }}>
                📋 {availableMaps.length} maps available - change in Zone Selection tab
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Enhanced ZoneViewerMap with separate styling controls */}
      <ZoneViewerMap
        mapId={mapId}
        zones={zones}
        checkedZones={checkedZones}
        vertices={vertices}
        useLeaflet={useLeaflet}
        zoneStyle={zoneStyle}
      />
      
      <div style={{ marginTop: "15px", padding: "10px", backgroundColor: "#f8f9fa", borderRadius: "5px", fontSize: "12px", color: "#666" }}>
        <strong>Map Controls:</strong> Use mouse wheel to zoom, click and drag to pan. 
        {useLeaflet && " Use the +/- buttons for precise zoom control."}
        <br />
        <strong>Zone Styling:</strong> Separate controls for fill vs line transparency allow you to make zone interiors subtle while keeping borders/vertices clearly visible. Try the presets for quick styling options.
      </div>
    </div>
  );
};

export default ZoneMapTab;