/* Name: ZoneSelectionTab.js */
/* Version: 0.1.2 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Zone selection tab component with BuildOutTool-style interface */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/ZoneViewer/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React from "react";

const ZoneSelectionTab = ({
  zoneTypes,
  zoneType,
  onZoneTypeChange,
  filteredZones,
  selectedZone,
  onZoneChange,
  availableMaps,
  selectedMapId,
  onMapChange,
  zones,
  checkedZones,
  onZoneToggle,
  onCheckAll,
  onDeleteZone
}) => {

  const renderZones = (zones, depth = 0) => {
    return zones.map((zone) => (
      <div key={zone.zone_id} style={{ marginLeft: `${depth * 20}px`, marginBottom: "5px" }}>
        <div style={{ display: "flex", alignItems: "center" }}>
          <input
            type="checkbox"
            checked={checkedZones.includes(zone.zone_id)}
            onChange={() => onZoneToggle(zone.zone_id)}
            style={{ marginRight: "5px" }}
          />
          <span>{zone.zone_name}</span>
          {zone.children && zone.children.length > 0 && (
            <>
              <input
                type="checkbox"
                checked={zone.children.every(child => checkedZones.includes(child.zone_id))}
                onChange={(e) => {
                  const toggleZoneAndChildren = (z) => {
                    if (e.target.checked) {
                      onZoneToggle(z.zone_id);
                    } else {
                      if (checkedZones.includes(z.zone_id)) {
                        onZoneToggle(z.zone_id);
                      }
                    }
                    if (z.children && z.children.length > 0) {
                      z.children.forEach(child => toggleZoneAndChildren(child));
                    }
                  };
                  toggleZoneAndChildren(zone);
                }}
                style={{ marginLeft: "10px", marginRight: "5px" }}
              />
              <span style={{ fontSize: "12px", color: "#666" }}>(Check All)</span>
            </>
          )}
          {zone.parent_zone_id === null && (
            <button
              onClick={() => onDeleteZone(zone.zone_id)}
              style={{ marginLeft: "10px", color: "red", border: "none", background: "none", cursor: "pointer" }}
            >
              Delete Zone
            </button>
          )}
        </div>
        {zone.children && zone.children.length > 0 && (
          renderZones(zone.children, depth + 1)
        )}
      </div>
    ));
  };

  return (
    <div>
      {/* Zone and Map Selection - Separate Dropdowns */}
      <div style={{ marginBottom: "20px", padding: "15px", border: "1px solid #ddd", borderRadius: "5px" }}>
        <div style={{ display: "flex", gap: "15px", alignItems: "end", marginBottom: "15px", flexWrap: "wrap" }}>
          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>Zone Type:</label>
            <select 
              value={zoneType} 
              onChange={(e) => onZoneTypeChange(e.target.value)}
              style={{ padding: "8px", minWidth: "150px", border: "1px solid #ccc", borderRadius: "4px" }}
            >
              <option value="">Select Zone Type</option>
              {zoneTypes.map(zt => (
                <option key={zt.zone_level} value={zt.zone_level}>{zt.zone_name}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>Zone:</label>
            <select 
              value={selectedZone} 
              onChange={(e) => onZoneChange(e.target.value)}
              style={{ padding: "8px", minWidth: "200px", border: "1px solid #ccc", borderRadius: "4px" }}
            >
              <option value="">Select Zone</option>
              {filteredZones.map(z => (
                <option key={z.i_zn} value={z.i_zn}>{z.x_nm_zn}</option>
              ))}
            </select>
          </div>

          <div>
            <label style={{ display: "block", marginBottom: "5px", fontWeight: "500" }}>Map:</label>
            <select 
              value={selectedMapId || ""} 
              onChange={(e) => onMapChange(e.target.value)}
              style={{ 
                padding: "8px", 
                minWidth: "200px", 
                border: "1px solid #ccc", 
                borderRadius: "4px",
                backgroundColor: !selectedZone ? "#f5f5f5" : "white"
              }}
              disabled={!selectedZone || availableMaps.length === 0}
            >
              <option value="">Select Map</option>
              {availableMaps.map(map => (
                <option key={map.mapId} value={map.mapId}>
                  Map {map.mapId} - {map.zoneName}
                </option>
              ))}
            </select>
          </div>
        </div>

        {/* Map Selection Info */}
        {selectedZone && (
          <div style={{ fontSize: "12px", color: "#666", marginTop: "8px" }}>
            {availableMaps.length > 0 ? (
              <span>📍 {availableMaps.length} map(s) available in this zone hierarchy</span>
            ) : (
              <span>⚠️ No maps available for the selected zone hierarchy</span>
            )}
          </div>
        )}
      </div>

      {selectedZone && zones.length > 0 && (
        <>
          <h3>Zones:</h3>
          <div style={{ marginBottom: "10px" }}>
            <input
              type="checkbox"
              checked={checkedZones.length > 0}
              onChange={(e) => onCheckAll(e.target.checked)}
              style={{ marginRight: "5px" }}
            />
            <span style={{ fontSize: "14px", color: "#666" }}>Check All Zones in Hierarchy</span>
          </div>
          <div style={{ maxHeight: "400px", overflowY: "auto", border: "1px solid #ddd", padding: "10px" }}>
            {renderZones(zones)}
          </div>
        </>
      )}

      {selectedZone && zones.length === 0 && (
        <div style={{ padding: "20px", textAlign: "center", color: "#666" }}>
          <p>No hierarchical zone data available for the selected zone.</p>
          <p>You can still view the map and edit vertices using the other tabs.</p>
        </div>
      )}
    </div>
  );
};

export default ZoneSelectionTab;