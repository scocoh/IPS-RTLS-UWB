// /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo.js
// Version: v0.10.49 - Added Clear System Events button
import React, { useState, useEffect, useRef, useCallback } from "react";
import { Form, Tabs, Tab, Table, Button, FormCheck, InputGroup, FormControl } from "react-bootstrap";
import NewTriggerViewer from "./NewTriggerViewer";
import L from "leaflet";

const NewTriggerDemo = () => {
  const [zones, setZones] = useState([]);
  const [zoneHierarchy, setZoneHierarchy] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [zoneVertices, setZoneVertices] = useState([]);
  const [zMin, setZMin] = useState(null);
  const [zMax, setZMax] = useState(null);
  const [customZMax, setCustomZMax] = useState(null);
  const [triggerName, setTriggerName] = useState("");
  const [triggerDirection, setTriggerDirection] = useState("");
  const [triggerDirections, setTriggerDirections] = useState([]);
  const [triggers, setTriggers] = useState([]);
  const [coordinates, setCoordinates] = useState([]);
  const [showMapForDrawing, setShowMapForDrawing] = useState(false);
  const [eventList, setEventList] = useState(() => {
    const savedEvents = localStorage.getItem("eventList");
    return savedEvents ? JSON.parse(savedEvents) : [];
  });
  const [loading, setLoading] = useState(true);
  const [showExistingTriggers, setShowExistingTriggers] = useState(true);
  const [existingTriggerPolygons, setExistingTriggerPolygons] = useState([]);
  const [useLeaflet, setUseLeaflet] = useState(true);
  const [fetchError, setFetchError] = useState(null);
  const [tagIdInput, setTagIdInput] = useState("SIM1");
  const [isConnected, setIsConnected] = useState(false);
  const [tagData, setTagData] = useState(null);
  const [tagCount, setTagCount] = useState(0);
  const [tagRate, setTagRate] = useState(0);
  const [tagTimestamps, setTagTimestamps] = useState([]);
  const [activeTab, setActiveTab] = useState("mapAndTrigger");
  const wsRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;
  const reconnectInterval = 5000; // 5 seconds

  useEffect(() => {
    localStorage.setItem("eventList", JSON.stringify(eventList));
  }, [eventList]);

  const getFormattedTimestamp = () => {
    const now = new Date();
    const pad = (val) => String(val).padStart(2, "0");
    return `${String(now.getFullYear()).slice(-2)}${pad(now.getMonth() + 1)}${pad(now.getDate())} ${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  };

  const fetchTriggers = async () => {
    try {
      const res = await fetch("http://192.168.210.226:8000/api/list_newtriggers");
      if (!res.ok) throw new Error(`Failed to fetch triggers: ${res.status}`);
      const data = await res.json();
      Array.isArray(data) ? setTriggers(data) : setTriggers([]);
      console.log('Fetched triggers:', data);
    } catch (e) {
      setFetchError(`Error fetching triggers: ${e.message}`);
    }
  };

  const connectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      disconnectWebSocket();
      return;
    }

    const ws = new WebSocket("ws://192.168.210.226:8001/ws/Manager1");
    wsRef.current = ws;
    reconnectAttempts.current = 0;

    ws.onopen = () => {
      console.log("WebSocket connected to Manager1");
      const subscription = {
        type: "request",
        request: "BeginStream",
        reqid: "triggerDemo1",
        params: [{ id: tagIdInput, data: "true" }],
        zone_id: selectedZone ? parseInt(selectedZone.i_zn) : 1
      };
      console.log("Subscribing with zone_id:", subscription.zone_id);
      ws.send(JSON.stringify(subscription));
      console.log("Sent subscription:", subscription);
      setIsConnected(true);
      setTagCount(0);
      setTagTimestamps([]);
      setTagRate(0);
      reconnectAttempts.current = 0; // Reset reconnect attempts on successful connection
    };

    ws.onmessage = async (event) => {
      console.log("Raw WebSocket message received:", event.data);
      let data;
      try {
        data = JSON.parse(event.data);
      } catch (e) {
        console.error("Failed to parse WebSocket message:", e);
        return;
      }
      console.log("Parsed WebSocket message:", data);
      if (data.type === "Sim" && data.gis) {
        console.log("Processing Sim message:", data);
        const newTagData = {
          id: data.gis.id,
          x: data.gis.x,
          y: data.gis.y,
          z: data.gis.z,
          sequence: data.Sequence,
          timestamp: Date.now()
        };
        setTagData(newTagData);
        setTagCount(prev => prev + 1);
        setTagTimestamps(prev => {
          const now = Date.now();
          const windowStart = now - 10000;
          const newTimestamps = [...prev, now].filter(ts => ts >= windowStart);
          if (newTimestamps.length > 1) {
            const timeSpan = (newTimestamps[newTimestamps.length - 1] - newTimestamps[0]) / 1000;
            const rate = timeSpan > 0 ? (newTimestamps.length - 1) / timeSpan : 0;
            setTagRate(rate);
          } else {
            setTagRate(0);
          }
          return newTimestamps;
        });
      } else if (data.type === "TriggerEvent" && selectedZone) {
        let trigger = triggers.find(t => t.i_trg === data.trigger_id && t.zone_id === parseInt(selectedZone.i_zn));
        if (!trigger) {
          try {
            const res = await fetch(`http://192.168.210.226:8000/api/get_trigger_details/${data.trigger_id}`);
            if (!res.ok) throw new Error(`Failed to fetch trigger details: ${res.status}`);
            const triggerData = await res.json();
            trigger = { i_trg: data.trigger_id, x_nm_trg: triggerData.name, i_dir: triggerData.direction_id, zone_id: parseInt(selectedZone.i_zn) };
            setTriggers(prev => [...prev, trigger]);
            console.log(`Fetched trigger details for ID ${data.trigger_id}:`, triggerData);
          } catch (e) {
            console.error(`Error fetching trigger details for ID ${data.trigger_id}:`, e);
            return;
          }
        }
        const eventMessage = `Tag ${data.tag_id} ${data.direction} trigger ${trigger.x_nm_trg} at ${data.timestamp}`;
        setEventList(prev => [...prev, eventMessage]);
      } else if (data.type === "HeartBeat") {
        ws.send(JSON.stringify({ type: "HeartBeat", ts: data.ts }));
        console.log("Sent heartbeat response:", data.ts);
      } else {
        console.log("Unhandled WebSocket message type:", data.type);
      }
    };

    ws.onclose = () => {
      console.log("WebSocket disconnected");
      setIsConnected(false);
      setTagRate(0);
      if (reconnectAttempts.current < maxReconnectAttempts) {
        reconnectAttempts.current += 1;
        console.log(`Attempting to reconnect (${reconnectAttempts.current}/${maxReconnectAttempts})...`);
        setTimeout(connectWebSocket, reconnectInterval);
      } else {
        console.error("Max reconnect attempts reached. Please reconnect manually.");
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setIsConnected(false);
      setTagRate(0);
    };
  };

  const disconnectWebSocket = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.close();
      console.log("WebSocket close initiated");
    }
  };

  useEffect(() => {
    const fetchZones = async () => {
      try {
        const response = await fetch("http://192.168.210.226:8000/zonebuilder/get_parent_zones_for_trigger_demo");
        console.log("Raw response status:", response.status);
        console.log("Raw response headers:", [...response.headers.entries()]);
        const text = await response.text();
        console.log("Raw response text:", text);
        if (!response.ok) throw new Error(`Failed to fetch zones: ${response.status}`);
        let data;
        try {
          data = JSON.parse(text);
        } catch (e) {
          throw new Error(`Failed to parse response as JSON: ${e.message}`);
        }
        console.log("Parsed response data:", data);

        let zonesArray;
        if (Array.isArray(data)) {
          zonesArray = data;
        } else if (data && Array.isArray(data.zones)) {
          zonesArray = data.zones;
        } else {
          throw new Error("Invalid zones response from server: Expected an array or object with zones array.");
        }

        const mappedZones = zonesArray.map(zone => ({
          i_zn: parseInt(zone.zone_id),
          x_nm_zn: zone.name,
          i_typ_zn: zone.level,
          i_map: zone.i_map || null,
          parent_zone_id: zone.parent_zone_id ? parseInt(zone.parent_zone_id) : null
        }));

        const hierarchy = [];
        const zoneMap = new Map(mappedZones.map(zone => [zone.i_zn, { ...zone, children: [] }]));
        zoneMap.forEach(zone => {
          if (zone.parent_zone_id && zoneMap.has(zone.parent_zone_id)) {
            zoneMap.get(zone.parent_zone_id).children.push(zone);
          } else {
            hierarchy.push(zone);
          }
        });

        hierarchy.sort((a, b) => a.x_nm_zn.localeCompare(b.x_nm_zn));
        const customOrder = [1, 10, 2];
        const sortChildren = (children) => {
          children.sort((a, b) => {
            const aIndex = customOrder.indexOf(a.i_typ_zn);
            const bIndex = customOrder.indexOf(b.i_typ_zn);
            if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
            if (aIndex !== -1) return -1;
            if (bIndex !== -1) return 1;
            if (a.i_typ_zn !== b.i_typ_zn) return a.i_typ_zn - b.i_typ_zn;
            return a.x_nm_zn.localeCompare(b.x_nm_zn);
          });
          children.forEach(child => sortChildren(child.children));
        };

        hierarchy.forEach(parent => sortChildren(parent.children));
        console.log("✅ Zone hierarchy:", JSON.stringify(hierarchy, null, 2));
        setZoneHierarchy(hierarchy);
        setZones(mappedZones);
        const campusZone = hierarchy.find(z => z.i_typ_zn === 1);
        if (campusZone) {
          console.log("Selected campus zone:", campusZone);
          setSelectedZone(campusZone);
        } else if (hierarchy.length > 0) {
          console.log("No campus zone found, selecting first zone:", hierarchy[0]);
          setSelectedZone(hierarchy[0]);
        }
      } catch (e) {
        setFetchError(`Error fetching zones: ${e.message}`);
      }
    };

    const fetchTriggerDirections = async () => {
      try {
        const res = await fetch("http://192.168.210.226:8000/api/list_trigger_directions");
        if (!res.ok) throw new Error(`Failed to fetch trigger directions: ${res.status}`);
        const data = await res.json();
        setTriggerDirections(data);
      } catch (e) {
        setFetchError(`Error fetching directions: ${e.message}`);
      }
    };

    fetchZones();
    fetchTriggerDirections();
    fetchTriggers();

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  useEffect(() => {
    if (!selectedZone) return;
    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn));

    const fetchPolygons = async () => {
      try {
        const polygons = await Promise.all(
          zoneTriggers.map(async (t) => {
            const res = await fetch(`http://192.168.210.226:8000/api/get_trigger_details/${t.i_trg}`);
            if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);
            const data = await res.json();
            if (Array.isArray(data.vertices)) {
              const latLngs = data.vertices.map(v => [v.y, v.x]);
              return { id: t.i_trg, name: t.x_nm_trg, latLngs };
            }
            return null;
          })
        );
        setExistingTriggerPolygons(polygons.filter(p => p));
      } catch (e) {
        console.error("Failed to fetch polygons:", e);
        setFetchError("Failed to fetch trigger polygons.");
      }
    };

    const fetchZoneVertices = async () => {
      try {
        const response = await fetch(`http://192.168.210.226:8000/zoneviewer/get_vertices_for_campus/${selectedZone.i_zn}`);
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        const vertices = data.vertices.map(vertex => ({
          i_vtx: vertex.vertex_id,
          zone_id: vertex.zone_id,
          n_x: Number(vertex.x).toFixed(6),
          n_y: Number(vertex.y).toFixed(6),
          n_z: Number(vertex.z).toFixed(6),
          n_ord: vertex.order,
        }));
        setZoneVertices(vertices);
        const zValues = vertices.map(v => Number(v.n_z));
        const minZ = Math.min(...zValues);
        const maxZ = Math.max(...zValues);
        setZMin(minZ);
        setZMax(maxZ);
        setCustomZMax(maxZ);
      } catch (e) {
        console.error("Error fetching zone vertices:", e);
      }
    };

    fetchPolygons();
    fetchZoneVertices();
  }, [selectedZone, triggers]);

  const handleDrawComplete = useCallback((coords) => {
    try {
      const parsed = Array.isArray(coords) ? coords : JSON.parse(coords);
      if (Array.isArray(parsed) && parsed.length >= 3) {
        const effectiveZMax = zMin === zMax && customZMax !== null ? Number(customZMax) : zMax;
        const formattedCoords = parsed.map((coord, index) => {
          const x = Number(coord.lng);
          const y = Number(coord.lat);
          if (isNaN(x) || isNaN(y)) throw new Error(`Invalid coordinates at index ${index}`);
          let n_z = index === 0 ? zMin : (index === 1 ? effectiveZMax : zMin);
          return { n_x: x.toFixed(6), n_y: y.toFixed(6), n_z: n_z };
        });
        console.log("Formatted coordinates:", formattedCoords);
        setCoordinates(formattedCoords);
      }
    } catch (e) {
      console.error("Error parsing draw coords:", e);
      alert("Failed to process drawn coordinates.");
    }
  }, [zMin, zMax, customZMax]);

  const handleZoneChange = (zoneId) => {
    const parsedZoneId = parseInt(zoneId);
    console.log("Selected zone ID:", parsedZoneId);
    const zone = zones.find(z => z.i_zn === parsedZoneId);
    console.log("Found zone:", zone);
    if (zone && (!selectedZone || zone.i_zn !== selectedZone.i_zn)) {
      setSelectedZone(zone);
      setCoordinates([]);
      setShowMapForDrawing(false);
      setZMin(null);
      setZMax(null);
      setCustomZMax(null);
      console.log("Updated selectedZone:", zone);
    }
  };

  const retryReloadTriggers = async (retries = 3, delay = 1000) => {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const reloadRes = await fetch("http://192.168.210.226:8001/api/reload_triggers", {
          method: "POST",
          headers: { "Content-Type": "application/json" }
        });
        if (!reloadRes.ok) throw new Error(`Failed to reload triggers: ${reloadRes.status}`);
        console.log("Successfully sent reload triggers request");
        return true;
      } catch (e) {
        console.error(`Attempt ${attempt} failed: ${e.message}`);
        if (attempt === retries) {
          console.error("All retry attempts failed.");
          return false;
        }
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
    return false;
  };

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
      const res = await fetch("http://192.168.210.226:8000/api/add_trigger", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await res.json();
      alert(`Trigger ID: ${result.trigger_id}`);
      setEventList(prev => [...prev, `Trigger ${triggerName} created on ${getFormattedTimestamp()}`]);
      setCoordinates([]);
      setShowMapForDrawing(false);

      const reloadSuccess = await retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        alert("Trigger created, but failed to reload triggers on the server. Please restart the WebSocket server or try again.");
      }

      await fetchTriggers();
    } catch (e) {
      console.error("Trigger create error:", e);
      alert("Failed to create trigger.");
    }
  };

  const handleDeleteTrigger = async (id) => {
    if (!window.confirm(`Delete trigger ID ${id}?`)) return;
    try {
      const res = await fetch(`http://192.168.210.226:8000/api/delete_trigger/${id}`, { method: "DELETE" });
      const result = await res.json();
      alert(`Deleted trigger ${id}`);
      setEventList(prev => [...prev, `Trigger ID ${id} deleted on ${getFormattedTimestamp()}`]);
      await fetchTriggers();

      const reloadSuccess = await retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        alert("Trigger deleted, but failed to reload triggers on the server. Please restart the WebSocket server or try again.");
      }
    } catch (e) {
      console.error("Delete error:", e);
      alert("Failed to delete trigger.");
    }
  };

  const getDirectionName = (id) => triggerDirections.find(d => d.i_dir === id)?.x_dir || `ID ${id}`;

  const renderZoneOptions = (zoneList, indentLevel = 0) => {
    return zoneList.map(zone => (
      <React.Fragment key={zone.i_zn}>
        <option value={zone.i_zn}>
          {`${"  ".repeat(indentLevel)}${indentLevel > 0 ? "- " : ""}${zone.x_nm_zn} (Level ${zone.i_typ_zn})`}
        </option>
        {zone.children && zone.children.length > 0 && renderZoneOptions(zone.children, indentLevel + 1)}
      </React.Fragment>
    ));
  };

  return (
    <div>
      <h2>New Trigger Demo</h2>
      <Button variant="secondary" onClick={() => { setEventList([]); localStorage.setItem("eventList", JSON.stringify([])); }}>
        Clear System Events
      </Button>
      {fetchError && <div style={{ color: "red" }}>{fetchError}</div>}
      {loading && <p>Loading...</p>}
      <Tabs 
        defaultActiveKey="mapAndTrigger" 
        onSelect={(key) => setActiveTab(key)}
      >
        <Tab eventKey="mapAndTrigger" title="Map & Trigger">
          <Form.Group>
            <Form.Label>Tag ID to Subscribe</Form.Label>
            <InputGroup>
              <FormControl
                type="text"
                value={tagIdInput}
                onChange={(e) => setTagIdInput(e.target.value)}
                placeholder="Enter Tag ID (e.g., SIM1)"
                disabled={isConnected}
              />
              <Button
                variant={isConnected ? "danger" : "primary"}
                onClick={isConnected ? disconnectWebSocket : connectWebSocket}
                disabled={!tagIdInput}
              >
                {isConnected ? "Disconnect" : "Connect"}
              </Button>
            </InputGroup>
          </Form.Group>

          {tagData && (
            <div style={{ marginTop: "10px" }}>
              <p>
                Tag {tagData.id}: X={tagData.x}, Y={tagData.y}, Z={tagData.z}, 
                Sequence={tagData.sequence}, Count={tagCount}, Tags/sec={tagRate.toFixed(2)}
              </p>
            </div>
          )}

          <Form.Group>
            <Form.Label>Trigger Name</Form.Label>
            <Form.Control type="text" value={triggerName} onChange={e => setTriggerName(e.target.value)} />
          </Form.Group>

          <Form.Group>
            <Form.Label>Select Zone</Form.Label>
            <Form.Control as="select" value={selectedZone?.i_zn || ""} onChange={e => handleZoneChange(e.target.value)}>
              <option value="">-- Choose Zone --</option>
              {renderZoneOptions(zoneHierarchy)}
            </Form.Control>
          </Form.Group>

          <Form.Group>
            <Form.Label>Z Min: {zMin !== null ? zMin : 'N/A'}</Form.Label>
          </Form.Group>

          <Form.Group>
            <Form.Label>Z Max: {zMax !== null ? zMax : 'N/A'}</Form.Label>
            {zMin !== null && zMax !== null && zMin === zMax && (
              <InputGroup className="mt-2">
                <InputGroup.Text>Modify Z Max</InputGroup.Text>
                <FormControl
                  type="number"
                  value={customZMax || ''}
                  onChange={e => setCustomZMax(e.target.value)}
                  placeholder="Enter new Z Max"
                />
              </InputGroup>
            )}
          </Form.Group>

          <Form.Group>
            <Form.Label>Direction</Form.Label>
            <Form.Control as="select" value={triggerDirection} onChange={e => setTriggerDirection(e.target.value)}>
              <option value="">Select Direction</option>
              {triggerDirections.map(d => (
                <option key={d.i_dir} value={d.x_dir}>{d.x_dir}</option>
              ))}
            </Form.Control>
          </Form.Group>

          <Button onClick={handleCreateTrigger}>{showMapForDrawing ? "Save Trigger" : "Create Trigger"}</Button>

          <FormCheck
            type="checkbox"
            label="Show Existing Triggers"
            checked={showExistingTriggers}
            onChange={e => setShowExistingTriggers(e.target.checked)}
            style={{ marginTop: "10px" }}
          />

          {selectedZone && activeTab === "mapAndTrigger" && (
            <div style={{ marginTop: "15px" }}>
              <strong>Zone Preview:</strong>
              {selectedZone.i_map ? (
                <NewTriggerViewer
                  mapId={selectedZone.i_map}
                  zones={[selectedZone]}
                  checkedZones={[selectedZone.i_zn]}
                  vertices={zoneVertices}
                  useLeaflet={useLeaflet}
                  enableDrawing={showMapForDrawing}
                  onDrawComplete={handleDrawComplete}
                  showExistingTriggers={showExistingTriggers}
                  existingTriggerPolygons={existingTriggerPolygons}
                  tagData={tagData}
                  isConnected={isConnected}
                />
              ) : (
                <div style={{ color: "red" }}>No map ID available for this zone.</div>
              )}
            </div>
          )}
        </Tab>

        <Tab eventKey="deleteTriggers" title="Delete Triggers">
          {triggers.length === 0 ? <p>No triggers found.</p> : (
            <Table striped bordered hover>
              <thead>
                <tr><th>ID</th><th>Name</th><th>Direction</th><th>Zone</th><th>Actions</th></tr>
              </thead>
              <tbody>
                {triggers.map(t => (
                  <tr key={t.i_trg}>
                    <td>{t.i_trg}</td>
                    <td>{t.x_nm_trg}</td>
                    <td>{getDirectionName(t.i_dir)}</td>
                    <td>{t.zone_name || "Unknown"}</td>
                    <td><Button variant="danger" onClick={() => handleDeleteTrigger(t.i_trg)}>Delete</Button></td>
                  </tr>
                ))}
              </tbody>
            </Table>
          )}
        </Tab>

        <Tab eventKey="events" title="System Events">
          {eventList.length === 0 ? <p>No system events recorded.</p> : (
            <ul>{eventList.map((e, i) => <li key={i}>{e}</li>)}</ul>
          )}
        </Tab>
      </Tabs>
    </div>
  );
};

export default NewTriggerDemo;