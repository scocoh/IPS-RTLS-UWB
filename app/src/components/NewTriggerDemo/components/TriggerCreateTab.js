/* Name: TriggerCreateTab.js */
/* Version: 0.1.4 */
/* Created: 250705 */
/* Modified: 250718 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Trigger creation tab – Added zone boundary visualization for better user guidance */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useCallback } from "react";
import { Form, Button, InputGroup, FormControl, Alert } from "react-bootstrap";
import NewTriggerViewer from "../../NewTriggerViewer/NTV_index";          // ← updated
import { triggerApi } from "../services/triggerApi";
import { zoneApi } from "../services/zoneApi";
import { getFormattedTimestamp } from "../utils/formatters";

const TriggerCreateTab = ({
  zones,
  zoneHierarchy,
  selectedZone,
  triggerDirections,
  setEventList,
  fetchTriggers,
  handleZoneChange
}) => {
  // Local state for trigger creation
  const [zoneVertices, setZoneVertices] = useState([]);
  const [zMin, setZMin] = useState(null);
  const [zMax, setZMax] = useState(null);
  const [customZMax, setCustomZMax] = useState(null);
  const [triggerName, setTriggerName] = useState("");
  const [triggerDirection, setTriggerDirection] = useState("");
  const [coordinates, setCoordinates] = useState([]);
  const [showMapForDrawing, setShowMapForDrawing] = useState(false);

  // NEW: Zone boundary visualization state
  const [showZoneBoundaries, setShowZoneBoundaries] = useState(true);
  const [zoneBoundaries, setZoneBoundaries] = useState(null);
  const [boundaryError, setBoundaryError] = useState(null);

  // Fetch zone vertices when zone changes
  const fetchZoneVertices = useCallback(async (zoneId) => {
    try {
      const { vertices, minZ, maxZ } = await zoneApi.fetchZoneVertices(zoneId);
      setZoneVertices(vertices);
      setZMin(minZ);
      setZMax(maxZ);
      setCustomZMax(maxZ);
    } catch (e) {
      console.error("Error fetching zone vertices:", e);
    }
  }, []);

  // NEW: Fetch zone boundaries for visualization
  const fetchZoneBoundaries = useCallback(async (zoneId) => {
    try {
      console.log(`🎯 Fetching zone boundaries for zone ${zoneId}`);
      setBoundaryError(null);
      
      const boundaries = await zoneApi.getZoneBoundaries(zoneId);
      console.log(`📊 Zone ${zoneId} boundaries:`, boundaries);
      
      setZoneBoundaries(boundaries);
      
      // Show coordinate ranges to user
      setEventList(prev => [...prev, 
        `Zone ${zoneId} boundaries loaded: X: ${boundaries.min_x.toFixed(2)} to ${boundaries.max_x.toFixed(2)}, ` +
        `Y: ${boundaries.min_y.toFixed(2)} to ${boundaries.max_y.toFixed(2)} on ${getFormattedTimestamp()}`
      ]);
      
    } catch (e) {
      console.error("Error fetching zone boundaries:", e);
      setBoundaryError(`Failed to load zone boundaries: ${e.message}`);
      setZoneBoundaries(null);
    }
  }, [setEventList]);

  // Handle zone change with vertex and boundary fetch
  const handleLocalZoneChange = useCallback((zoneId) => {
    handleZoneChange(zoneId);
    setCoordinates([]);
    setShowMapForDrawing(false);
    setZMin(null);
    setZMax(null);
    setCustomZMax(null);
    // NEW: Reset boundary state
    setZoneBoundaries(null);
    setBoundaryError(null);
  }, [handleZoneChange]);

  // Fetch zone data when selected zone changes
  useEffect(() => {
    if (selectedZone) {
      fetchZoneVertices(selectedZone.i_zn);
      // NEW: Fetch boundaries if visualization is enabled
      if (showZoneBoundaries) {
        fetchZoneBoundaries(selectedZone.i_zn);
      }
    }
  }, [selectedZone, fetchZoneVertices, fetchZoneBoundaries, showZoneBoundaries]);

  // NEW: Handle boundary toggle change
  const handleBoundaryToggle = useCallback((enabled) => {
    setShowZoneBoundaries(enabled);
    
    if (enabled && selectedZone && !zoneBoundaries) {
      // Fetch boundaries if not already loaded
      fetchZoneBoundaries(selectedZone.i_zn);
    } else if (!enabled) {
      // Clear any boundary errors when disabled
      setBoundaryError(null);
    }
  }, [selectedZone, zoneBoundaries, fetchZoneBoundaries]);

  // FIXED: Handle drawing complete - improved coordinate parsing for Leaflet objects
  const handleDrawComplete = useCallback((coords) => {
    try {
      console.log("🎯 Raw coords received:", coords, "Type:", typeof coords);
      
      let parsed;
      
      // Handle different coordinate formats
      if (Array.isArray(coords)) {
        // Already an array
        parsed = coords;
        console.log("✅ Coords are already an array");
      } else if (typeof coords === 'string') {
        // String that needs parsing
        try {
          parsed = JSON.parse(coords);
          console.log("✅ Parsed coords from JSON string");
        } catch (parseError) {
          console.error("❌ JSON parse error:", parseError);
          throw new Error("Invalid coordinate string format");
        }
      } else if (coords && typeof coords === 'object') {
        // Handle Leaflet layer objects (most common case)
        if (coords._latlngs && Array.isArray(coords._latlngs)) {
          // Leaflet polygon layer object
          parsed = coords._latlngs[0] || coords._latlngs; // First ring for polygons
          console.log("✅ Extracted coords from Leaflet object._latlngs");
        } else if (coords.getLatLngs && typeof coords.getLatLngs === 'function') {
          // Leaflet layer with getLatLngs method
          const latLngs = coords.getLatLngs();
          parsed = Array.isArray(latLngs[0]) ? latLngs[0] : latLngs;
          console.log("✅ Extracted coords using getLatLngs() method");
        } else if (coords.coordinates) {
          // Generic coordinates property
          parsed = coords.coordinates;
          console.log("✅ Extracted coords from object.coordinates");
        } else if (coords.latLngs) {
          // Generic latLngs property
          parsed = coords.latLngs;
          console.log("✅ Extracted coords from object.latLngs");
        } else if (coords.lat !== undefined && coords.lng !== undefined) {
          // Single coordinate object
          parsed = [coords];
          console.log("✅ Converted single coordinate object to array");
        } else {
          console.error("❌ Unknown coordinate object format:", coords);
          console.log("Available properties:", Object.keys(coords));
          throw new Error("Unknown coordinate object format");
        }
      } else {
        console.error("❌ Invalid coordinate type:", typeof coords);
        throw new Error("Invalid coordinate type");
      }

      // Validate array format
      if (!Array.isArray(parsed)) {
        console.error("❌ Parsed coords not an array:", parsed);
        throw new Error("Coordinates must be an array");
      }

      if (parsed.length < 3) {
        console.warn("⚠️ Need at least 3 points, got:", parsed.length);
        alert("Please draw a polygon with at least 3 points.");
        return;
      }

      console.log("🔍 Processing", parsed.length, "coordinate points");

      // NEW: Validate coordinates against zone boundaries if available
      if (zoneBoundaries && showZoneBoundaries) {
        console.log("🎯 Validating coordinates against zone boundaries");
        
        let allWithinBounds = true;
        let boundaryWarnings = [];
        
        for (let i = 0; i < parsed.length; i++) {
          const coord = parsed[i];
          let x, y;
          
          if (coord.lng !== undefined && coord.lat !== undefined) {
            x = Number(coord.lng);
            y = Number(coord.lat);
          } else if (coord.x !== undefined && coord.y !== undefined) {
            x = Number(coord.x);
            y = Number(coord.y);
          } else if (Array.isArray(coord) && coord.length >= 2) {
            x = Number(coord[1]); // lng/x
            y = Number(coord[0]); // lat/y
          }
          
          // Check if coordinate is within zone boundaries
          if (x < zoneBoundaries.min_x || x > zoneBoundaries.max_x ||
              y < zoneBoundaries.min_y || y > zoneBoundaries.max_y) {
            
            allWithinBounds = false;
            boundaryWarnings.push(`Point ${i + 1}: (${x.toFixed(2)}, ${y.toFixed(2)})`);
          }
        }
        
        if (!allWithinBounds) {
          const warning = `⚠️ Some coordinates are outside zone boundaries!\n\n` +
                        `Out of bounds points:\n${boundaryWarnings.join('\n')}\n\n` +
                        `Valid area:\n` +
                        `X: ${zoneBoundaries.min_x.toFixed(2)} to ${zoneBoundaries.max_x.toFixed(2)}\n` +
                        `Y: ${zoneBoundaries.min_y.toFixed(2)} to ${zoneBoundaries.max_y.toFixed(2)}\n\n` +
                        `Z coordinates will be auto-corrected during creation.`;
          
          alert(warning);
        } else {
          // Show positive feedback when all coordinates are within bounds
          setEventList(prev => [...prev, 
            `✅ All coordinates are within zone ${selectedZone.i_zn} boundaries on ${getFormattedTimestamp()}`
          ]);
        }
      }

      // Format coordinates with Z values
      const effectiveZMax = zMin === zMax && customZMax !== null ? Number(customZMax) : zMax;
      const formattedCoords = parsed.map((coord, index) => {
        // Handle different coordinate object formats
        let x, y;
        
        if (coord.lng !== undefined && coord.lat !== undefined) {
          // Leaflet format: {lat, lng}
          x = Number(coord.lng);
          y = Number(coord.lat);
        } else if (coord.x !== undefined && coord.y !== undefined) {
          // Direct x,y format
          x = Number(coord.x);
          y = Number(coord.y);
        } else if (Array.isArray(coord) && coord.length >= 2) {
          // Array format: [lat, lng] or [x, y]
          x = Number(coord[1]); // lng/x
          y = Number(coord[0]); // lat/y
        } else {
          console.error("❌ Invalid coordinate format at index", index, ":", coord);
          throw new Error(`Invalid coordinate format at index ${index}`);
        }

        if (isNaN(x) || isNaN(y)) {
          console.error("❌ Invalid numeric values at index", index, "x:", x, "y:", y);
          throw new Error(`Invalid coordinates at index ${index}: x=${x}, y=${y}`);
        }

        // Assign Z values
        let n_z = index === 0 ? zMin : (index === 1 ? effectiveZMax : zMin);
        
        const formatted = { 
          n_x: x.toFixed(6), 
          n_y: y.toFixed(6), 
          n_z: n_z 
        };
        
        console.log(`📍 Point ${index}: (${x}, ${y}) -> (${formatted.n_x}, ${formatted.n_y}, ${formatted.n_z})`);
        return formatted;
      });
      
      console.log("✅ Formatted coordinates:", formattedCoords);
      setCoordinates(formattedCoords);
      
    } catch (e) {
      console.error("❌ Error processing coordinates:", e);
      alert(`Failed to process drawn coordinates: ${e.message}`);
    }
  }, [zMin, zMax, customZMax, zoneBoundaries, showZoneBoundaries]);

  // Handle trigger creation
  const handleCreateTrigger = async () => {
    if (!triggerName || !selectedZone || !triggerDirection) {
      alert("Please complete all fields.");
      return;
    }

    if (!showMapForDrawing) {
      setShowMapForDrawing(true);
      return;
    }

    if (coordinates.length < 3) {
      alert("Please draw a polygon with at least 3 points.");
      return;
    }

    const dir = triggerDirections.find(d => d.x_dir === triggerDirection);
    if (!dir) {
      alert("Invalid direction.");
      return;
    }

    const payload = {
      name: triggerName,
      direction: dir.i_dir,
      zone_id: parseInt(selectedZone.i_zn),
      ignore: false,
      vertices: coordinates.map(({ n_x, n_y, n_z }) => ({
        x: Number(n_x),
        y: Number(n_y),
        z: Number(n_z)
      }))
    };
    
    console.log("Creating trigger in zone:", selectedZone.i_zn);
    console.log("Payload after conversion:", JSON.stringify(payload, null, 2));

    try {
      const result = await triggerApi.createTrigger(payload);
      
      // NEW: Enhanced success message with corrections info
      let successMessage = `✅ Trigger Created Successfully!\n\nTrigger ID: ${result.trigger_id}`;
      
      if (result.corrections_applied && result.corrections_applied.length > 0) {
        successMessage += `\n\n🔧 Auto-corrections applied:\n${result.corrections_applied.join('\n')}`;
      } else {
        successMessage += `\n\n✅ All coordinates were within zone boundaries.`;
      }
      
      if (result.message && result.message.includes('Auto-corrections')) {
        // Extract corrections from message if not in separate field
        const correctionMatch = result.message.match(/Auto-corrections applied: (.+)/);
        if (correctionMatch) {
          successMessage += `\n\n🔧 Auto-corrections applied:\n${correctionMatch[1]}`;
        }
      }
      
      alert(successMessage);
      
      setEventList(prev => [...prev, `Trigger ${triggerName} created on ${getFormattedTimestamp()}`]);
      setCoordinates([]);
      setShowMapForDrawing(false);
      setTriggerName("");
      setTriggerDirection("");

      const reloadSuccess = await triggerApi.retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        alert("Trigger created, but failed to reload triggers on the server. Please restart the WebSocket server or try again.");
      }

      await fetchTriggers();
    } catch (e) {
      console.error("Trigger create error:", e);
      alert(`Failed to create trigger: ${e.message}`);
    }
  };

  // Render zone options
  const renderZoneOptions = (zoneList, indentLevel = 0) => {
    return zoneList.map(zone => (
      <React.Fragment key={zone.i_zn}>
        <option value={zone.i_zn}>
          {`${"  ".repeat(indentLevel)}${indentLevel > 0 ? "- " : ""}${zone.i_zn} - ${zone.x_nm_zn} (Level ${zone.i_typ_zn})`}
        </option>
        {zone.children && zone.children.length > 0 && renderZoneOptions(zone.children, indentLevel + 1)}
      </React.Fragment>
    ));
  };

  return (
    <div>
      <h3>Create New Trigger</h3>
      <p>Create zone-based triggers by selecting a zone and drawing a polygon on the map.</p>

      {/* Debug Info */}
      <div style={{ 
        marginBottom: "15px", 
        padding: "8px", 
        backgroundColor: "#f0f8ff", 
        borderRadius: "3px",
        border: "1px solid #b3d9ff",
        fontSize: "12px"
      }}>
        <strong>🐛 Debug:</strong> Coordinates: {coordinates.length} points | 
        Z-range: {zMin} to {zMax} | 
        Drawing: {showMapForDrawing ? 'ON' : 'OFF'} | 
        Boundaries: {zoneBoundaries ? 'LOADED' : 'NOT LOADED'}
      </div>

      {/* NEW: Zone Boundary Information */}
      {zoneBoundaries && showZoneBoundaries && (
        <div style={{ 
          marginBottom: "15px", 
          padding: "10px", 
          backgroundColor: "#e8f5e8", 
          borderRadius: "5px",
          border: "1px solid #c3e6c3"
        }}>
          <h6 style={{ color: "#155724", marginBottom: "8px" }}>📐 Zone {selectedZone.i_zn} Valid Drawing Area</h6>
          <div style={{ fontSize: "14px", color: "#155724" }}>
            <div><strong>X Range:</strong> {zoneBoundaries.min_x.toFixed(2)} to {zoneBoundaries.max_x.toFixed(2)}</div>
            <div><strong>Y Range:</strong> {zoneBoundaries.min_y.toFixed(2)} to {zoneBoundaries.max_y.toFixed(2)}</div>
            <div><strong>Z Range:</strong> {zoneBoundaries.min_z.toFixed(2)} to {zoneBoundaries.max_z.toFixed(2)} (auto-corrected)</div>
            {coordinates.length > 0 && (
              <div style={{ marginTop: "8px", padding: "6px", backgroundColor: "#d4edda", borderRadius: "3px" }}>
                <strong>✅ Drawing Status:</strong> {coordinates.length} points drawn within boundaries
              </div>
            )}
          </div>
        </div>
      )}

      {/* NEW: Boundary Error Display */}
      {boundaryError && (
        <Alert variant="warning" style={{ marginBottom: "15px" }}>
          {boundaryError}
        </Alert>
      )}

      {/* Trigger Creation Form */}
      <div style={{ 
        marginBottom: "15px", 
        padding: "10px", 
        backgroundColor: "#f8f9fa", 
        borderRadius: "5px",
        border: "1px solid #dee2e6"
      }}>
        <h6>🎯 Trigger Configuration</h6>
        
        <Form.Group style={{ marginBottom: "10px" }}>
          <Form.Label>Trigger Name</Form.Label>
          <Form.Control 
            type="text" 
            value={triggerName} 
            onChange={e => setTriggerName(e.target.value)}
            placeholder="Enter trigger name"
          />
        </Form.Group>

        <Form.Group style={{ marginBottom: "10px" }}>
          <Form.Label>Select Zone</Form.Label>
          <Form.Control 
            as="select" 
            value={selectedZone?.i_zn || ""} 
            onChange={e => handleLocalZoneChange(e.target.value)}
          >
            <option value="">-- Choose Zone --</option>
            {renderZoneOptions(zoneHierarchy)}
          </Form.Control>
        </Form.Group>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px", marginBottom: "10px" }}>
          <Form.Group>
            <Form.Label>Z Min: {zMin !== null ? zMin : 'N/A'}</Form.Label>
          </Form.Group>
          
          <Form.Group>
            <Form.Label>Z Max: {zMax !== null ? zMax : 'N/A'}</Form.Label>
            {zMin !== null && zMax !== null && zMin === zMax && (
              <InputGroup className="mt-2">
                <InputGroup.Text>Custom Z Max</InputGroup.Text>
                <FormControl
                  type="number"
                  value={customZMax || ''}
                  onChange={e => setCustomZMax(e.target.value)}
                  placeholder="Enter Z Max"
                />
              </InputGroup>
            )}
          </Form.Group>
        </div>

        <Form.Group style={{ marginBottom: "10px" }}>
          <Form.Label>Direction</Form.Label>
          <Form.Control 
            as="select" 
            value={triggerDirection} 
            onChange={e => setTriggerDirection(e.target.value)}
          >
            <option value="">Select Direction</option>
            {triggerDirections.map(d => (
              <option key={d.i_dir} value={d.x_dir}>{d.x_dir}</option>
            ))}
          </Form.Control>
        </Form.Group>

        {/* NEW: Zone Boundary Visualization Toggle */}
        <Form.Group style={{ marginBottom: "10px" }}>
          <Form.Check
            type="checkbox"
            label="☑️ Show Zone Boundaries on Map"
            checked={showZoneBoundaries}
            onChange={e => handleBoundaryToggle(e.target.checked)}
          />
          <small style={{ color: "#6c757d" }}>
            Display valid coordinate area to guide trigger placement
          </small>
        </Form.Group>

        <Button 
          onClick={handleCreateTrigger}
          variant={showMapForDrawing ? "success" : "primary"}
          disabled={!triggerName || !selectedZone || !triggerDirection}
        >
          {showMapForDrawing ? "💾 Save Trigger" : "🎯 Start Drawing"}
        </Button>
      </div>

      {/* Map Drawing Area */}
      {selectedZone && (
        <div style={{ 
          marginTop: "15px", 
          padding: "10px", 
          backgroundColor: "#ffffff", 
          borderRadius: "5px",
          border: "1px solid #dee2e6"
        }}>
          <h6>🗺️ Zone Map: {selectedZone.x_nm_zn}</h6>
          
          {showMapForDrawing && (
            <div style={{ 
              padding: "8px", 
              backgroundColor: "#fff3cd", 
              borderRadius: "3px",
              marginBottom: "10px",
              border: "1px solid #ffeaa7"
            }}>
              <strong>Drawing Mode:</strong> Click on the map to draw a polygon. You need at least 3 points.
              {coordinates.length > 0 && (
                <span style={{ marginLeft: "10px", color: "#28a745" }}>
                  ✅ {coordinates.length} points drawn
                </span>
              )}
            </div>
          )}
          
          {selectedZone.i_map ? (
            <NewTriggerViewer
              key={`create-${selectedZone.i_map}-${selectedZone.i_zn}-${showMapForDrawing}-${showZoneBoundaries}`}
              mapId={selectedZone.i_map}
              zones={[selectedZone]}
              checkedZones={[selectedZone.i_zn]}
              vertices={zoneVertices}
              useLeaflet={true}
              enableDrawing={showMapForDrawing}
              onDrawComplete={handleDrawComplete}
              showExistingTriggers={false}
              existingTriggerPolygons={[]}
              tagsData={{}}
              isConnected={false}
              triggers={[]}
              // NEW: Zone boundary props
              showZoneBoundaries={showZoneBoundaries}
              zoneBoundaries={zoneBoundaries}
            />
          ) : (
            <div style={{ 
              padding: "20px", 
              textAlign: "center", 
              color: "#dc3545", 
              backgroundColor: "#f8d7da", 
              borderRadius: "4px",
              border: "1px solid #f5c6cb"
            }}>
              ⚠️ No map ID available for this zone.
            </div>
          )}
        </div>
      )}

      {/* Creation Help */}
      <div style={{ 
        marginTop: "15px", 
        padding: "10px", 
        backgroundColor: "#e7f3ff", 
        borderRadius: "5px",
        border: "1px solid #b3d9ff"
      }}>
        <h6 style={{ color: "#0066cc" }}>💡 Creation Help</h6>
        <ul style={{ fontSize: "13px", color: "#333", marginBottom: 0 }}>
          <li>Enter trigger name and select zone</li>
          <li>Choose trigger direction (OnEnter, OnExit, etc.)</li>
          <li><strong>NEW: Toggle "Show Zone Boundaries" to see valid drawing area</strong></li>
          <li>Click "Start Drawing" to enable map drawing</li>
          <li>Draw a polygon on the map (minimum 3 points)</li>
          <li>Click "Save Trigger" to create the trigger</li>
          <li><strong>Zone boundaries help prevent coordinate violations</strong></li>
          <li><strong>Z coordinates are auto-corrected to fit zone limits</strong></li>
        </ul>
      </div>
    </div>
  );
};

export default TriggerCreateTab;