/* Name: TriggerMapTab.js */
/* Version: 0.1.0 */
/* Created: 250625 */
/* Modified: 250625 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin + Claude */
/* Description: Map & Trigger tab component for NewTriggerDemo */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/NewTriggerDemo/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

import React, { useState, useEffect, useRef, useCallback } from "react";
import { Form, Button, FormCheck, InputGroup, FormControl } from "react-bootstrap";
import NewTriggerViewer from "../../NewTriggerViewer";
import { triggerApi } from "../services/triggerApi";
import { zoneApi } from "../services/zoneApi";
import { getFormattedTimestamp, formatTagInfo } from "../utils/formatters";

const TriggerMapTab = ({
  zones,
  zoneHierarchy,
  selectedZone,
  triggers,
  triggerDirections,
  tagIdsInput,
  setTagIdsInput,
  isConnected,
  tagsData,
  sequenceNumbers,
  tagCount,
  tagRate,
  triggerEvents,
  showTriggerEvents,
  setShowTriggerEvents,
  eventList,
  setEventList,
  portableTriggerContainment,
  connectWebSocket,
  disconnectWebSocket,
  handleZoneChange,
  fetchTriggers,
  activeTab
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
  const [showExistingTriggers, setShowExistingTriggers] = useState(true);
  const [existingTriggerPolygons, setExistingTriggerPolygons] = useState([]);
  const retryIntervalRef = useRef(null);

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

  // Handle zone change with vertex fetch
  const handleLocalZoneChange = useCallback((zoneId) => {
    handleZoneChange(zoneId);
    setCoordinates([]);
    setShowMapForDrawing(false);
    setZMin(null);
    setZMax(null);
    setCustomZMax(null);
  }, [handleZoneChange]);

  // Fetch zone vertices when selected zone changes
  useEffect(() => {
    if (selectedZone) {
      fetchZoneVertices(selectedZone.i_zn);
    }
  }, [selectedZone, fetchZoneVertices]);

  // Fetch trigger polygons
  useEffect(() => {
    if (!selectedZone) return;
    
    console.log("useEffect triggered with selectedZone:", selectedZone.i_zn, "isConnected:", isConnected);
    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null);
    console.log("Zone triggers for zone", selectedZone.i_zn, ":", zoneTriggers);

    const fetchPolygons = async () => {
      console.log("Fetching polygons for triggers:", zoneTriggers);
      if (zoneTriggers.length === 0) {
        console.log("No triggers found for zone", selectedZone.i_zn);
        setExistingTriggerPolygons([]);
        return;
      }
      
      try {
        const polygons = await Promise.all(
          zoneTriggers.map(async (t) => {
            try {
              console.log(`Fetching details for trigger ID ${t.i_trg}`);
              if (t.is_portable) {
                return { 
                  id: t.i_trg, 
                  name: t.x_nm_trg, 
                  isPortable: true, 
                  pending: true, 
                  assigned_tag_id: t.assigned_tag_id, 
                  radius_ft: t.radius_ft 
                };
              } else {
                const data = await triggerApi.getTriggerDetails(t.i_trg);
                console.log(`Trigger ${t.i_trg} response from get_trigger_details:`, data);
                if (Array.isArray(data.vertices)) {
                  const latLngs = data.vertices.map(v => [v.y, v.x]);
                  return { id: t.i_trg, name: t.x_nm_trg, latLngs, isPortable: false };
                }
                console.log(`No vertices for trigger ${t.i_trg}`);
                return null;
              }
            } catch (e) {
              console.error(`Failed to fetch details for trigger ${t.i_trg}:`, e);
              return null;
            }
          })
        );
        
        const validPolygons = polygons.filter(p => p);
        console.log("Fetched polygons:", validPolygons);
        setExistingTriggerPolygons(validPolygons);
      } catch (e) {
        console.error("Failed to fetch polygons:", e);
      }
    };

    fetchPolygons();
  }, [selectedZone, triggers, isConnected]);

  // Update portable trigger polygons
  useEffect(() => {
    if (!selectedZone || !triggers || !isConnected) return;

    console.log("Updating portable polygons after WebSocket connection");
    const zoneTriggers = triggers.filter(t => t.zone_id === parseInt(selectedZone.i_zn) || t.zone_id == null);
    const portableTriggers = zoneTriggers.filter(t => t.is_portable);
    if (portableTriggers.length === 0) return;

    const updatePortablePolygons = async () => {
      const updatedPolygons = portableTriggers.map(t => {
        const tagId = t.assigned_tag_id;
        const tagData = tagsData[tagId];
        if (!tagData) {
          console.log(`No live position data for tag ${tagId} assigned to portable trigger ${t.i_trg}`);
          return null;
        }
        const radius = t.radius_ft;
        console.log(`Updating portable trigger ${t.i_trg} with center ${[tagData.y, tagData.x]} and radius ${radius}`);
        return {
          id: t.i_trg,
          name: t.x_nm_trg,
          center: [tagData.y, tagData.x],
          radius: radius,
          isPortable: true,
          assigned_tag_id: t.assigned_tag_id,
          radius_ft: t.radius_ft
        };
      });

      const validPortable = updatedPolygons.filter(p => p);
      if (validPortable.length === portableTriggers.length) {
        setExistingTriggerPolygons(prev => {
          const nonPortable = prev.filter(p => !p.isPortable || p.pending);
          console.log("Updated existingTriggerPolygons:", [...nonPortable, ...validPortable]);
          return [...nonPortable, ...validPortable];
        });
        if (retryIntervalRef.current) {
          clearInterval(retryIntervalRef.current);
          retryIntervalRef.current = null;
        }
      }
    };

    updatePortablePolygons();

    if (!retryIntervalRef.current) {
      retryIntervalRef.current = setInterval(updatePortablePolygons, 1000);
    }

    return () => {
      if (retryIntervalRef.current) {
        clearInterval(retryIntervalRef.current);
        retryIntervalRef.current = null;
      }
    };
  }, [tagsData, selectedZone, triggers, isConnected]);

  // Handle drawing complete
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
      alert(`Trigger ID: ${result.trigger_id}`);
      setEventList(prev => [...prev, `Trigger ${triggerName} created on ${getFormattedTimestamp()}`]);
      setCoordinates([]);
      setShowMapForDrawing(false);

      const reloadSuccess = await triggerApi.retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        alert("Trigger created, but failed to reload triggers on the server. Please restart the WebSocket server or try again.");
      }

      await fetchTriggers();
    } catch (e) {
      console.error("Trigger create error:", e);
      alert("Failed to create trigger.");
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

  const infoLines = formatTagInfo(tagsData, selectedZone, zones, tagCount, tagRate);

  return (
    <>
      <Form.Group>
        <Form.Label>Tag IDs to Subscribe (comma-separated, e.g., SIM1,SIM2)</Form.Label>
        <InputGroup>
          <FormControl
            type="text"
            value={tagIdsInput}
            onChange={(e) => setTagIdsInput(e.target.value)}
            placeholder="Enter Tag IDs (e.g., SIM1,SIM2)"
            disabled={isConnected}
          />
          <Button
            variant={isConnected ? "danger" : "primary"}
            onClick={() => {
              if (isConnected) {
                disconnectWebSocket();
              } else {
                connectWebSocket();
              }
            }}
            disabled={!tagIdsInput}
          >
            {isConnected ? "Disconnect" : "Connect"}
          </Button>
        </InputGroup>
      </Form.Group>

      {Object.values(tagsData).length > 0 && (
        <div style={{ marginTop: "10px", whiteSpace: "pre-wrap" }}>
          <p>{infoLines}</p>
        </div>
      )}

      <div style={{ marginTop: "10px" }}>
        <h3>Trigger Events</h3>
        <FormCheck
          type="checkbox"
          label="Show Trigger Events"
          checked={showTriggerEvents}
          onChange={(e) => setShowTriggerEvents(e.target.checked)}
          style={{ marginBottom: "10px" }}
        />
        {triggerEvents.length === 0 ? (
          <p>No trigger events recorded.</p>
        ) : (
          <div style={{ maxHeight: "200px", overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
            <ul style={{ margin: 0, padding: 0, listStyleType: "none" }}>
              {triggerEvents.map((event, index) => (
                <li key={index}>{event}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      <Form.Group>
        <Form.Label>Trigger Name</Form.Label>
        <Form.Control type="text" value={triggerName} onChange={e => setTriggerName(e.target.value)} />
      </Form.Group>

      <Form.Group>
        <Form.Label>Select Zone</Form.Label>
        <Form.Control as="select" value={selectedZone?.i_zn || ""} onChange={e => handleLocalZoneChange(e.target.value)}>
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
              useLeaflet={true}
              enableDrawing={showMapForDrawing}
              onDrawComplete={handleDrawComplete}
              showExistingTriggers={showExistingTriggers}
              existingTriggerPolygons={existingTriggerPolygons.map(p => ({
                ...p,
                isContained: p.isPortable ? Object.keys(portableTriggerContainment[p.id] || {}).some(tagId => portableTriggerContainment[p.id][tagId]) : false
              }))}
              tagsData={tagsData}
              isConnected={isConnected}
              triggers={triggers}
            />
          ) : (
            <div style={{ color: "red" }}>No map ID available for this zone.</div>
          )}
        </div>
      )}
    </>
  );
};

export default TriggerMapTab;