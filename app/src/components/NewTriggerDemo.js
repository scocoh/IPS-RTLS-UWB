// src/components/NewTriggerDemo.js
import React, { useState, useEffect, useRef } from "react";
import { Form, Tabs, Tab, Table, Button, FormCheck } from "react-bootstrap";
import Map from "./Map"; // Import Map.js as a module
import L from "leaflet"; // Import Leaflet to manage existing triggers

const NewTriggerDemo = () => {
  const [zones, setZones] = useState([]); // All zones (parent and child)
  const [selectedZone, setSelectedZone] = useState(null); // Currently selected zone
  const [triggerName, setTriggerName] = useState("");
  const [triggerDirection, setTriggerDirection] = useState("");
  const [triggerDirections, setTriggerDirections] = useState([]);
  const [triggers, setTriggers] = useState([]); // State for triggers
  const [coordinates, setCoordinates] = useState([]); // Coordinates for drawing triggers
  const [showMapForDrawing, setShowMapForDrawing] = useState(false);
  const [eventList, setEventList] = useState([]); // Event list for triggers
  const [loading, setLoading] = useState(true); // Loading state for zones
  const [showExistingTriggers, setShowExistingTriggers] = useState(true); // Toggle for existing triggers
  const [existingTriggerPolygons, setExistingTriggerPolygons] = useState([]); // Store existing trigger polygons
  const mapInstanceRef = useRef(null); // Ref to store the Leaflet map instance
  const existingLayersRef = useRef([]); // Ref to store existing trigger layers
  const [mapBounds, setMapBounds] = useState(null); // Store map bounds for coordinate mapping
  const [fetchError, setFetchError] = useState(null); // Store fetch errors

  // Utility function to format the current timestamp as YYMMDD HHMMSS
  const getFormattedTimestamp = () => {
    const now = new Date();
    const year = now.getFullYear().toString().slice(-2); // Last 2 digits of year
    const month = String(now.getMonth() + 1).padStart(2, "0"); // Months are 0-based
    const day = String(now.getDate()).padStart(2, "0");
    const hours = String(now.getHours()).padStart(2, "0");
    const minutes = String(now.getMinutes()).padStart(2, "0");
    const seconds = String(now.getSeconds()).padStart(2, "0");
    return `${year}${month}${day} ${hours}${minutes}${seconds}`;
  };

  // Fetch all zones (parent and child)
  useEffect(() => {
    const fetchZones = async () => {
      try {
        const response = await fetch("http://192.168.210.231:8000/zonebuilder/get_parent_zones");
        const data = await response.json();
        console.log("Raw zones response:", data); // Debug log
        if (data && Array.isArray(data.zones)) {
          // Map the response properties to the expected format
          const mappedZones = data.zones.map((zone) => ({
            i_zn: zone.zone_id,
            x_nm_zn: zone.name,
            i_typ_zn: zone.level,
          }));
          setZones(mappedZones);
          // Default to the first campus zone (i_typ_zn=1)
          const campusZone = mappedZones.find((zone) => zone.i_typ_zn === 1);
          if (campusZone) {
            setSelectedZone(campusZone);
          }
        } else {
          console.error("Unexpected response format for zones:", data);
          setFetchError("Failed to fetch zones.");
        }
      } catch (error) {
        console.error("Error fetching zones:", error);
        setFetchError("Error fetching zones: " + error.message);
      }
    };

    const fetchTriggerDirections = async () => {
      try {
        const response = await fetch("http://192.168.210.231:8000/api/list_trigger_directions");
        const data = await response.json();
        setTriggerDirections(data);
      } catch (error) {
        console.error("Error fetching trigger directions:", error);
        setFetchError("Error fetching trigger directions: " + error.message);
      }
    };

    const fetchTriggers = async () => {
      try {
        const response = await fetch("http://192.168.210.231:8000/api/list_newtriggers");
        const data = await response.json();
        console.log("Fetched triggers (list_newtriggers):", data); // Debug log
        if (Array.isArray(data)) {
          setTriggers(data);
        } else {
          console.error("Triggers response is not an array:", data);
          setTriggers([]);
          setFetchError("Triggers response is not an array.");
        }
      } catch (error) {
        console.error("Error fetching triggers:", error);
        setTriggers([]); // Set to empty array on error
        setFetchError("Error fetching triggers: " + error.message);
      } finally {
        setLoading(false);
      }
    };

    fetchZones();
    fetchTriggerDirections();
    fetchTriggers();
  }, []);

  // Fetch map bounds when the selected zone changes
  useEffect(() => {
    if (!selectedZone) return;

    const fetchMapBounds = async () => {
      try {
        const response = await fetch(`/maps/get_map_data/${selectedZone.i_zn}`);
        const data = await response.json();
        console.log("Map data for bounds:", data); // Debug log
        setMapBounds(data.bounds);
      } catch (error) {
        console.error("Error fetching map bounds:", error);
        setFetchError("Error fetching map bounds: " + error.message);
      }
    };

    fetchMapBounds();
  }, [selectedZone]);

  // Fetch existing trigger polygons when the selected zone changes
  useEffect(() => {
    if (!selectedZone || !mapBounds) {
      setExistingTriggerPolygons([]);
      return;
    }

    const fetchExistingTriggers = async () => {
      const zoneTriggers = triggers.filter((trigger) => {
        console.log(`Trigger ${trigger.i_trg} zone_id: ${trigger.zone_id}, selectedZone.i_zn: ${selectedZone.i_zn}`); // Debug log
        return trigger.zone_id === selectedZone.i_zn;
      });
      console.log("Zone triggers for selected zone:", zoneTriggers); // Debug log

      const polygons = await Promise.all(
        zoneTriggers.map(async (trigger) => {
          try {
            const response = await fetch(`/api/get_trigger_details/${trigger.i_trg}`);
            const data = await response.json();
            console.log(`Trigger ${trigger.i_trg} details:`, data); // Debug log
            if (data.vertices && Array.isArray(data.vertices)) {
              const latLngs = data.vertices.map((v) => {
                // The vertices are in logical coordinates (x: -80 to 160, y: -40 to 160)
                // Map.js uses the same logical coordinate system, so we can use the coordinates directly
                const lat = v.y; // y-coordinate maps to latitude
                const lng = v.x; // x-coordinate maps to longitude
                return [lat, lng];
              });
              console.log(`Trigger ${trigger.i_trg} latLngs:`, latLngs); // Debug log
              return { id: trigger.i_trg, name: trigger.x_nm_trg, latLngs };
            }
            return null;
          } catch (error) {
            console.error(`Error fetching trigger details for ID ${trigger.i_trg}:`, error);
            return null;
          }
        })
      );
      const validPolygons = polygons.filter((p) => p !== null);
      console.log("Existing trigger polygons:", validPolygons); // Debug log
      setExistingTriggerPolygons(validPolygons);
    };

    fetchExistingTriggers();
  }, [selectedZone, triggers, mapBounds]);

  // Render existing triggers on the map
  useEffect(() => {
    if (!mapInstanceRef.current || !selectedZone || !mapBounds) return;

    const map = mapInstanceRef.current;

    // Clear existing layers
    existingLayersRef.current.forEach((layer) => map.removeLayer(layer));
    existingLayersRef.current = [];

    // Add existing triggers if toggled on
    if (showExistingTriggers) {
      existingTriggerPolygons.forEach((trigger) => {
        // Verify that latLngs are within map bounds
        const withinBounds = trigger.latLngs.every(([lat, lng]) => {
          const inBounds = lat >= mapBounds[0][0] && lat <= mapBounds[1][0] && lng >= mapBounds[0][1] && lng <= mapBounds[1][1];
          if (!inBounds) {
            console.warn(`Trigger ${trigger.id} has coordinates outside map bounds: [lat: ${lat}, lng: ${lng}]`);
          }
          return inBounds;
        });

        if (withinBounds) {
          const polygon = L.polygon(trigger.latLngs, { color: "blue" }).addTo(map);
          polygon.bindPopup(trigger.name);
          existingLayersRef.current.push(polygon);
        } else {
          console.warn(`Trigger ${trigger.id} not rendered due to out-of-bounds coordinates.`);
        }
      });
    }
  }, [showExistingTriggers, existingTriggerPolygons, mapBounds]);

  // Handle map drawing completion
  const handleDrawComplete = (coords) => {
    console.log("Drawing completed with coordinates (raw):", coords); // Debug log
    // Parse coords if it's a string (Map.js may pass a stringified array)
    let parsedCoords = coords;
    if (typeof coords === "string") {
      try {
        parsedCoords = JSON.parse(coords);
      } catch (error) {
        console.error("Error parsing coordinates:", error);
        return;
      }
    }
    if (!Array.isArray(parsedCoords)) {
      console.error("Coordinates is not an array:", parsedCoords);
      return;
    }
    setCoordinates(parsedCoords);
    console.log("Set coordinates:", parsedCoords); // Debug log
  };

  // Handle zone selection
  const handleZoneChange = (zoneId) => {
    const zone = zones.find((z) => z.i_zn === parseInt(zoneId));
    setSelectedZone(zone);
    console.log("Selected zone:", zone); // Debug log
  };

  // Handle trigger creation
  const handleCreateTrigger = async () => {
    if (!triggerName || !selectedZone || !triggerDirection) {
      alert("Please fill all required fields (Trigger Name, Zone, Direction).");
      return;
    }

    if (!showMapForDrawing) {
      setShowMapForDrawing(true);
      return;
    }

    if (coordinates.length < 3) {
      alert("Please draw the trigger on the map (click to add points, double-click to finish).");
      return;
    }

    const selectedDirectionObj = triggerDirections.find((dir) => dir.x_dir === triggerDirection);
    const directionId = selectedDirectionObj ? selectedDirectionObj.i_dir : null;

    if (!directionId) {
      alert("Invalid direction selected.");
      return;
    }

    const triggerData = {
      name: triggerName,
      direction: directionId,
      zone_id: parseInt(selectedZone.i_zn),
      ignore: true,
      vertices: coordinates.map((coord) => ({
        x: coord.n_x,
        y: coord.n_y,
        z: coord.n_z || 0,
      })),
    };

    try {
      const response = await fetch("http://192.168.210.231:8000/api/add_trigger", {
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
      const timestamp = getFormattedTimestamp();
      setEventList([...eventList, `trigger region called ${triggerName} created on ${timestamp}`]);
      setCoordinates([]); // Reset coordinates after successful creation
      setShowMapForDrawing(false);
      // Refresh the triggers list
      const triggersResponse = await fetch("http://192.168.210.231:8000/api/list_newtriggers");
      const triggersData = await triggersResponse.json();
      if (Array.isArray(triggersData)) {
        setTriggers(triggersData);
      } else {
        console.error("Triggers refresh response is not an array:", triggersData);
        setTriggers([]);
        setFetchError("Triggers refresh response is not an array.");
      }
    } catch (error) {
      console.error("Error creating trigger:", error);
      alert(`Error creating trigger: ${error.message}`);
    }
  };

  // Handle trigger deletion
  const handleDeleteTrigger = async (triggerId) => {
    if (!window.confirm(`Are you sure you want to delete trigger ID ${triggerId}?`)) {
      return;
    }

    try {
      const response = await fetch(`http://192.168.210.231:8000/api/delete_trigger/${triggerId}`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
      });
      if (!response.ok) {
        const text = await response.text();
        throw new Error(`HTTP error! status: ${response.status}, response: ${text}`);
      }
      const result = await response.json();
      alert(`Trigger ${triggerId} deleted successfully`);
      const timestamp = getFormattedTimestamp();
      setEventList([...eventList, `trigger region with ID ${triggerId} deleted on ${timestamp}`]);
      // Refresh the triggers list
      const triggersResponse = await fetch("http://192.168.210.231:8000/api/list_newtriggers");
      const triggersData = await triggersResponse.json();
      if (Array.isArray(triggersData)) {
        setTriggers(triggersData);
      } else {
        console.error("Triggers refresh response is not an array:", triggersData);
        setTriggers([]);
        setFetchError("Triggers refresh response is not an array.");
      }
    } catch (error) {
      console.error("Error deleting trigger:", error);
      alert(`Error deleting trigger: ${error.message}`);
    }
  };

  // Map direction ID to direction name
  const getDirectionName = (directionId) => {
    const direction = triggerDirections.find((dir) => dir.i_dir === directionId);
    return direction ? direction.x_dir : `Direction ${directionId}`;
  };

  // Callback to receive the Leaflet map instance from Map.js
  const handleMapCreated = (map) => {
    mapInstanceRef.current = map;
  };

  return (
    <div>
      <h2>New Trigger Demo</h2>
      {fetchError && <div style={{ color: "red", marginBottom: "10px" }}>{fetchError}</div>}
      {loading && <p>Loading...</p>}

      <Tabs defaultActiveKey="mapAndTrigger" id="new-trigger-demo-tabs">
        <Tab eventKey="mapAndTrigger" title="Map & Trigger">
          <div style={{ margin: "20px 0" }}>
            <h3>Create Trigger</h3>
            <Form.Group style={{ marginBottom: "10px" }}>
              <Form.Label>Trigger Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Trigger Name"
                value={triggerName}
                onChange={(e) => setTriggerName(e.target.value)}
              />
            </Form.Group>
            <Form.Group style={{ marginBottom: "10px" }}>
              <Form.Label>Select Zone Level</Form.Label>
              <Form.Control
                as="select"
                value={selectedZone?.i_zn || ""}
                onChange={(e) => handleZoneChange(e.target.value)}
                disabled={loading}
              >
                <option value="">Select a zone</option>
                {loading ? (
                  <option value="">Loading zones...</option>
                ) : (
                  zones.map((zone) => (
                    <option key={zone.i_zn} value={zone.i_zn}>
                      {zone.i_typ_zn === 1 ? zone.x_nm_zn : `  - ${zone.x_nm_zn}`} (Level {zone.i_typ_zn})
                    </option>
                  ))
                )}
              </Form.Control>
            </Form.Group>
            <Form.Group style={{ marginBottom: "10px" }}>
              <Form.Label>Direction</Form.Label>
              <Form.Control
                as="select"
                value={triggerDirection}
                onChange={(e) => setTriggerDirection(e.target.value)}
              >
                <option value="">Select Direction</option>
                {triggerDirections.map((direction) => (
                  <option key={direction.i_dir} value={direction.x_dir}>
                    {direction.x_dir}
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
            <Button onClick={handleCreateTrigger}>
              {showMapForDrawing ? "Save Trigger" : "Create Trigger"}
            </Button>
            {showMapForDrawing && (
              <div style={{ color: "blue", margin: "10px 0" }}>
                Select the polygon tool, click at least three vertices to form a polygon, then click 'Finish'.
              </div>
            )}
            <div style={{ color: "green", margin: "10px 0" }}>
              1. Click the 'Create Trigger' button to start drawing a trigger on the map.<br />
              2. Select the polygon tool, click at least three vertices to form a polygon, then click 'Finish'.<br />
              3. Finally, click the 'Save Trigger' button to save your trigger.
            </div>
            <FormCheck
              type="checkbox"
              label="Show Existing Triggers"
              checked={showExistingTriggers}
              onChange={(e) => setShowExistingTriggers(e.target.checked)}
              style={{ margin: "10px 0" }}
            />
          </div>

          {/* Use Map.js to render the map */}
          {loading ? (
            <p>Loading map...</p>
          ) : selectedZone ? (
            <Map
              key={selectedZone.i_zn}
              zoneId={parseInt(selectedZone.i_zn)}
              onDrawComplete={handleDrawComplete}
              triggerColor="red" // Color for the new trigger being drawn
              useLeaflet={true} // Use Leaflet rendering, as in TriggerDemo.js
              onMapCreated={handleMapCreated} // Pass callback to get map instance
            />
          ) : (
            <p>Please select a zone to display the map.</p>
          )}
        </Tab>

        <Tab eventKey="deleteTriggers" title="Delete Triggers">
          <div style={{ margin: "20px 0" }}>
            <h3>Delete Triggers</h3>
            {triggers.length === 0 ? (
              <p>No triggers available.</p>
            ) : (
              <Table striped bordered hover>
                <thead>
                  <tr>
                    <th>Trigger ID</th>
                    <th>Name</th>
                    <th>Direction</th>
                    <th>Zone</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {triggers.map((trigger) => (
                    <tr key={trigger.i_trg}>
                      <td>{trigger.i_trg}</td>
                      <td>{trigger.x_nm_trg}</td>
                      <td>{getDirectionName(trigger.i_dir)}</td>
                      <td>{trigger.zone_name || "Unknown Zone"}</td>
                      <td>
                        <Button
                          variant="danger"
                          onClick={() => handleDeleteTrigger(trigger.i_trg)}
                        >
                          Delete
                        </Button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </Table>
            )}
          </div>
        </Tab>

        <Tab eventKey="events" title="Trigger Events">
          <div style={{ margin: "20px 0" }}>
            <h3>Trigger Events</h3>
            {eventList.length === 0 ? (
              <p>No events recorded.</p>
            ) : (
              <ul>
                {eventList.map((event, index) => (
                  <li key={index}>{event}</li>
                ))}
              </ul>
            )}
          </div>
        </Tab>
      </Tabs>
    </div>
  );
};

export default NewTriggerDemo;