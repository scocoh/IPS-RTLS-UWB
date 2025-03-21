// # VERSION 250317 /home/parcoadmin/parco_fastapi/app/src/TriggerDemo.js 0P.10B.02
// #  
// # ParcoRTLS Middletier Services, ParcoRTLS DLL, ParcoDatabases, ParcoMessaging, and other code
// # Copyright (C) 1999 - 2025 Affiliated Commercial Services Inc.
// # Invented by Scott Cohen & Bertrand Dugal.
// # Coded by Jesse Chunn O.B.M.'24 and Michael Farnsworth and Others
// # Published at GitHub https://github.com/scocoh/IPS-RTLS-UWB
// #
// # Licensed under AGPL-3.0: https://www.gnu.org/licenses/agpl-3.0.en.html

import React, { useState, useEffect, useMemo, useCallback } from "react";
import { Tabs, Tab } from "react-bootstrap";
import Map from "./components/Map";
import "./TriggerDemo.css";

const TriggerDemo = () => {
  const [maps, setMaps] = useState([]);
  const [zones, setZones] = useState([]);
  const [triggerDirections, setTriggerDirections] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [selectedMapId, setSelectedMapId] = useState(null); // Store map_id
  const [triggerName, setTriggerName] = useState("");
  const [triggerDirection, setTriggerDirection] = useState("");
  const [topElevation, setTopElevation] = useState(8);
  const [bottomElevation, setBottomElevation] = useState(-1);
  const [triggerColor, setTriggerColor] = useState("red");
  const [eventList, setEventList] = useState([]);
  const [coordinates, setCoordinates] = useState("");
  const [parentZones, setParentZones] = useState([]);
  const [selectedParentZone, setSelectedParentZone] = useState("");
  const [vertices, setVertices] = useState([]);
  const [editedVertices, setEditedVertices] = useState({});
  const [loading, setLoading] = useState({
    maps: false,
    parentZones: false,
    triggerDirections: false,
    zones: false,
    vertices: false,
  });
  const [error, setError] = useState(null);
  const [showMapForDrawing, setShowMapForDrawing] = useState(false);
  const [useLeaflet, setUseLeaflet] = useState(false); // Toggle between Canvas and Leaflet

  // Fetch data helper
  const fetchData = async (url, setter, key, transform = (data) => data) => {
    setLoading((prev) => ({ ...prev, [key]: true }));
    try {
      const response = await fetch(url);
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
      }
      const data = await response.json();
      console.log(`${key} data:`, data);
      setter(transform(data));
      setError(null);
    } catch (error) {
      console.error(`Error fetching ${key}:`, error);
      setError(`Error fetching ${key}: ${error.message}`);
    } finally {
      setLoading((prev) => ({ ...prev, [key]: false }));
    }
  };

  // Fetch initial data
  useEffect(() => {
    fetchData("/maps/get_maps", setMaps, "maps");
    fetchData("/api/get_parent_zones", setParentZones, "parentZones", (data) => data.zones);
    fetchData("/api/list_trigger_directions", setTriggerDirections, "triggerDirections");
  }, []);

  // Flatten zones hierarchy
  const flattenZones = (zones) => {
    const result = [];
    const flatten = (zone) => {
      result.push(zone);
      if (zone.children && zone.children.length > 0) {
        zone.children.forEach(child => flatten(child));
      }
    };
    zones.forEach(zone => flatten(zone));
    return result;
  };

  // Update zones and fetch map_id when a parent zone is selected
  useEffect(() => {
    if (selectedParentZone) {
      const zoneId = parseInt(selectedParentZone);
      fetchData(`/maps/get_campus_zones/${zoneId}`, (data) => {
        const flattenedZones = flattenZones(data.zones || []);
        setZones(flattenedZones);
      }, "zones");
    }
  }, [selectedParentZone]);

  // Fetch map_id when a zone is selected
  useEffect(() => {
    if (selectedZone) {
      fetch(`/maps/get_map_data/${selectedZone}`)
        .then(response => response.json())
        .then(data => {
          setSelectedMapId(data.map_id || selectedZone); // Fallback to zoneId if map_id not provided
        })
        .catch(error => console.error("Error fetching map data:", error));
    }
  }, [selectedZone]);

  // Memoized handleCreateTrigger to prevent unnecessary re-renders
  const handleCreateTrigger = useCallback(async () => {
    if (!triggerName || !selectedZone || !triggerDirection) {
      alert("Please fill all required fields (Trigger Name, Zone, Direction).");
      return;
    }

    if (!showMapForDrawing) {
      setShowMapForDrawing(true);
      return;
    }

    console.log("Current coordinates before save:", coordinates); // Debug log
    if (!coordinates) {
      alert("Please draw the trigger on the map (click to add points, double-click to finish).");
      return;
    }

    // Find the direction ID (i_dir) from the selected direction string
    const selectedDirectionObj = triggerDirections.find(dir => dir.x_dir === triggerDirection);
    const directionId = selectedDirectionObj ? selectedDirectionObj.i_dir : null;

    if (!directionId) {
      alert("Invalid direction selected.");
      return;
    }

    const triggerData = {
      name: triggerName,
      direction: directionId,
      zone_id: parseInt(selectedZone),
      ignore: true,
      coordinates: JSON.parse(coordinates),
    };

    console.log("Sending triggerData to /api/add_trigger:", triggerData);

    try {
      const response = await fetch("/api/add_trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(triggerData),
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
      }
      const result = await response.json();
      alert(`Trigger created with ID: ${result.trigger_id}`);
      setEventList([...eventList, `${triggerName} created at ${coordinates} with ${triggerDirection} direction`]);
      setCoordinates("");
      setShowMapForDrawing(false);
    } catch (error) {
      console.error("Error creating trigger:", error);
      alert(`Error creating trigger: ${error.message}`);
    }
  }, [triggerName, selectedZone, triggerDirection, coordinates, showMapForDrawing, triggerDirections]);

  // Memoized onDrawComplete to prevent re-renders
  const handleDrawComplete = useCallback((coords) => {
    setCoordinates(coords);
  }, []);

  // Load vertices for selected zones
  const loadVerticesForSelectedZones = async () => {
    const checkedZones = Array.from(document.querySelectorAll("#zoneList input[type='checkbox']:checked"))
      .map(cb => parseInt(cb.value))
      .filter(id => !isNaN(id));
    if (checkedZones.length === 0) {
      alert("Please select at least one zone to load vertices.");
      return;
    }

    setLoading((prev) => ({ ...prev, vertices: true }));
    try {
      const vertexPromises = checkedZones.map(zoneId =>
        fetch(`/api/get_zone_vertices/${zoneId}`)
          .then(response => {
            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
            return response.json();
          })
          .then(data => data.vertices || [])
      );
      const allVertices = (await Promise.all(vertexPromises)).flat();
      if (allVertices.length === 0) {
        throw new Error("No vertices found for selected zones.");
      }
      console.log("Loaded vertices:", allVertices);
      setVertices(allVertices);
      setEditedVertices(allVertices.reduce((acc, v) => ({ ...acc, [v.i_vtx]: v }), {}));
    } catch (error) {
      console.error("Error loading vertices:", error);
      alert(`Error loading vertices: ${error.message}`);
    } finally {
      setLoading((prev) => ({ ...prev, vertices: false }));
    }
  };

  // Handle vertex changes
  const handleVertexChange = (vertexId, field, value) => {
    setEditedVertices(prev => ({
      ...prev,
      [vertexId]: { ...prev[vertexId], [field]: parseFloat(value) || 0 }
    }));
  };

  // Save all edited vertices
  const saveAllVertices = async () => {
    const updatedVertices = Object.values(editedVertices).map(v => ({
      vertex_id: v.i_vtx,
      x: v.x,
      y: v.y,
      z: v.z || 0
    }));
    if (updatedVertices.length === 0) {
      alert("No vertices to save.");
      return;
    }

    console.log("Sending vertices to /api/update_vertices:", updatedVertices); // Debug log

    try {
      const response = await fetch("/api/update_vertices", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(updatedVertices), // Send list directly
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
      }
      alert("Vertices updated successfully!");
      if (selectedZone) {
        fetchData(`/api/get_zone_vertices/${selectedZone}`, setVertices, "vertices", (data) => data.vertices || []);
      }
    } catch (error) {
      console.error("Error saving vertices:", error);
      alert(`Error saving vertices: ${error.message}`);
    }
  };

  // Use useMemo to ensure consistent rendering of direction options
  const directionOptions = useMemo(() => {
    return triggerDirections.map((direction) => (
      <option key={direction.i_dir} value={direction.x_dir}>
        {direction.x_dir}
      </option>
    ));
  }, [triggerDirections]);

  return (
    <div>
      <h1>ParcoRTLS Trigger Management</h1>
      <Tabs defaultActiveKey="mapAndTrigger" id="trigger-demo-tabs">
        <Tab eventKey="mapAndTrigger" title="Map & Trigger">
          <div className="trigger-map-section">
            {error && <div style={{ color: "red" }}>{error}</div>}
            <div className="trigger-form">
              <h3>Create Trigger</h3>
              <input
                type="text"
                placeholder="Trigger Name"
                value={triggerName}
                onChange={(e) => setTriggerName(e.target.value)}
              />
              <select value={selectedParentZone} onChange={(e) => setSelectedParentZone(e.target.value)}>
                <option value="">Select Parent Zone</option>
                {loading.parentZones ? (
                  <option value="">Loading...</option>
                ) : (
                  parentZones.map((pz) => (
                    <option key={pz.zone_id} value={pz.zone_id.toString()}>
                      {pz.name}
                    </option>
                  ))
                )}
              </select>
              <select value={triggerDirection} onChange={(e) => setTriggerDirection(e.target.value)}>
                <option value="">Select Direction</option>
                {loading.triggerDirections ? (
                  <option value="">Loading...</option>
                ) : (
                  directionOptions
                )}
              </select>
              <input
                type="number"
                placeholder="Top Elevation (Zmax)"
                value={topElevation}
                onChange={(e) => setTopElevation(Number(e.target.value))}
              />
              <input
                type="number"
                placeholder="Bottom Elevation (Zmin)"
                value={bottomElevation}
                onChange={(e) => setBottomElevation(Number(e.target.value))}
              />
              <select value={triggerColor} onChange={(e) => setTriggerColor(e.target.value)}>
                <option value="red">Red</option>
                <option value="green">Green</option>
                <option value="blue">Blue</option>
              </select>
              <label>
                Render with Leaflet:
                <input
                  type="checkbox"
                  checked={useLeaflet}
                  onChange={(e) => setUseLeaflet(e.target.checked)}
                />
              </label>
              <button onClick={handleCreateTrigger}>
                {showMapForDrawing ? "Save Trigger" : "Create Trigger"}
              </button>
            </div>
            <div className="map-selection">
              <h3>Select a Zone</h3>
              <div id="zoneList">
                {loading.zones ? (
                  <p>Loading zones...</p>
                ) : zones.length === 0 ? (
                  <p>No zones available for this parent zone.</p>
                ) : (
                  zones.map((zone) => (
                    <div key={zone.zone_id}>
                      <input
                        type="checkbox"
                        value={zone.zone_id.toString()}
                        checked={selectedZone === zone.zone_id.toString()}
                        onChange={(e) => setSelectedZone(e.target.value)}
                      />
                      <span>{zone.zone_name}</span>
                    </div>
                  ))
                )}
              </div>
              {showMapForDrawing && (
                <>
                  <div style={{ color: "blue", margin: "10px 0" }}>
                    Click to add points, double-click to finish the trigger shape.
                  </div>
                  <Map
                    key={selectedZone}
                    zoneId={parseInt(selectedZone)}
                    onDrawComplete={handleDrawComplete}
                    triggerColor={triggerColor}
                    useLeaflet={useLeaflet} // Pass the toggle state
                  />
                </>
              )}
            </div>
            <h3>Edit Trigger Vertices</h3>
            <table id="vertexTable">
              <thead>
                <tr>
                  <th>Vertex #</th>
                  <th>X Coordinate</th>
                  <th>Y Coordinate</th>
                  <th>Z Coordinate</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {Object.values(editedVertices).map((v, i) => (
                  <tr key={v.i_vtx}>
                    <td>{i + 1}</td>
                    <td>
                      <input
                        type="number"
                        value={v.x || 0}
                        onChange={(e) => handleVertexChange(v.i_vtx, "x", e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        value={v.y || 0}
                        onChange={(e) => handleVertexChange(v.i_vtx, "y", e.target.value)}
                      />
                    </td>
                    <td>
                      <input
                        type="number"
                        value={v.z || 0}
                        onChange={(e) => handleVertexChange(v.i_vtx, "z", e.target.value)}
                      />
                    </td>
                    <td>
                      <button>Save</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            <button onClick={loadVerticesForSelectedZones} disabled={loading.vertices}>
              {loading.vertices ? "Loading..." : "Load Vertices for Selected Zones"}
            </button>
            <button onClick={saveAllVertices} disabled={loading.vertices}>
              {loading.vertices ? "Saving..." : "Save All Changes"}
            </button>
          </div>
        </Tab>
      </Tabs>
    </div>
  );
};

export default TriggerDemo;