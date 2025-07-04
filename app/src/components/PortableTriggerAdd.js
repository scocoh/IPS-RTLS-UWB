/* Name: PortableTriggerAdd.js */
/* Version: 0.1.4 */
/* Created: 250607 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: ParcoAdmin */
/* Description: JavaScript file for ParcoRTLS frontend to add portable triggers */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */
/* Changelog: */
/* - 0.1.4 (250704): Replaced hardcoded IP with dynamic hostname detection */

// /home/parcoadmin/parco_fastapi/app/src/components/PortableTriggerAdd.js
// Version: 0.1.4 - Replaced hardcoded IP with dynamic hostname detection
// Version: 0.1.3 - Updated retryReloadTriggers to use port 8000, bumped from 0.1.2
// Version: 0.1.2 - Updated to call /api/add_portable_trigger, added debug logging, bumped from 0.1.1
// Previous: Added Host Tag ID real/simulated toggle, Zone first with max radius, Z Min/Max auto-fill, device type sorting, fixed fetchError syntax, bumped from 0.1.0
// Reuses: fetchZones, fetchTriggerDirections, renderZoneOptions, retryReloadTriggers from NewTriggerDemo.js
// Features: Zone (optional), Trigger Name, Host Tag ID (real/simulated), Radius (feet), Z Min (feet), Z Max (feet), Direction

import React, { useState, useEffect } from "react";
import { Form, Tabs, Tab, Button, FormControl, InputGroup } from "react-bootstrap";

const PortableTriggerAdd = () => {
  const [zones, setZones] = useState([]);
  const [zoneHierarchy, setZoneHierarchy] = useState([]);
  const [selectedZone, setSelectedZone] = useState(null);
  const [zoneVertices, setZoneVertices] = useState([]);
  const [maxRadius, setMaxRadius] = useState(null);
  const [zMin, setZMin] = useState("");
  const [zMax, setZMax] = useState("");
  const [customZMax, setCustomZMax] = useState("");
  const [triggerName, setTriggerName] = useState("");
  const [triggerDirection, setTriggerDirection] = useState("");
  const [triggerDirections, setTriggerDirections] = useState([]);
  const [hostTagType, setHostTagType] = useState("real");
  const [hostTagId, setHostTagId] = useState("");
  const [simTagId, setSimTagId] = useState("");
  const [radius, setRadius] = useState("");
  const [devices, setDevices] = useState([]);
  const [deviceTypes, setDeviceTypes] = useState([]);
  const [selectedDeviceType, setSelectedDeviceType] = useState("");
  const [fetchError, setFetchError] = useState(null);

  // Base URL - dynamic hostname detection
  const API_BASE_URL = `http://${window.location.hostname || 'localhost'}:8000`;

  const getFormattedTimestamp = () => {
    const now = new Date();
    const pad = (val) => String(val).padStart(2, "0");
    return `${String(now.getFullYear()).slice(-2)}${pad(now.getMonth() + 1)}${pad(now.getDate())} ${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
  };

  const fetchZones = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/zonebuilder/get_parent_zones_for_trigger_demo`);
      if (!response.ok) throw new Error(`Failed to fetch zones: ${response.status}`);
      const text = await response.text();
      let data;
      try {
        data = JSON.parse(text);
      } catch (e) {
        throw new Error(`Failed to parse response as JSON: ${e.message}`);
      }
      let zonesArray = Array.isArray(data) ? data : (data.zones || []);
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
      setZoneHierarchy(hierarchy);
      setZones(mappedZones);
      const campusZone = hierarchy.find(z => z.i_typ_zn === 1);
      if (campusZone) {
        setSelectedZone(campusZone);
        await fetchZoneVertices(campusZone.i_zn);
      } else if (hierarchy.length > 0) {
        setSelectedZone(hierarchy[0]);
        await fetchZoneVertices(hierarchy[0].i_zn);
      }
    } catch (e) {
      setFetchError(`Error fetching zones: ${e.message}`);
    }
  };

  const fetchTriggerDirections = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/list_trigger_directions`);
      if (!res.ok) throw new Error(`Failed to fetch trigger directions: ${res.status}`);
      const data = await res.json();
      setTriggerDirections(data);
    } catch (e) {
      setFetchError(`Error fetching directions: ${e.message}`);
    }
  };

  const fetchDevices = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/api/get_all_devices`);
      if (!res.ok) throw new Error(`Failed to fetch devices: ${res.status}`);
      const data = await res.json();
      // TODO: Consider filtering by device types [1, 2, 4, 12, 24] (e.g., Tag, Personel Badge, Barcode Tag, CASE Cart)
      const activeDevices = data.filter(d => !d.d_srv_end);
      setDevices(activeDevices);
      const types = [...new Set(activeDevices.map(d => d.i_typ_dev))].map(i_typ_dev => ({
        i_typ_dev,
        x_dsc_dev: data.find(d => d.i_typ_dev === i_typ_dev)?.x_dsc_dev || `Type ${i_typ_dev}`
      })).sort((a, b) => a.x_dsc_dev.localeCompare(b.x_dsc_dev));
      setDeviceTypes(types);
      if (types.length > 0) setSelectedDeviceType(types[0].i_typ_dev);
    } catch (e) {
      setFetchError(`Error fetching devices: ${e.message}`);
    }
  };

  const fetchZoneVertices = async (zoneId) => {
    try {
      const response = await fetch(`${API_BASE_URL}/zoneviewer/get_vertices_for_campus/${zoneId}`);
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      const data = await response.json();
      const vertices = data.vertices.map(vertex => ({
        n_x: Number(vertex.x),
        n_y: Number(vertex.y),
        n_z: Number(vertex.z)
      }));
      setZoneVertices(vertices);
      if (vertices.length > 0) {
        const xRange = Math.max(...vertices.map(v => v.n_x)) - Math.min(...vertices.map(v => v.n_x));
        const yRange = Math.max(...vertices.map(v => v.n_y)) - Math.min(...vertices.map(v => v.n_y));
        const maxRadiusFt = Math.min(xRange, yRange) / 2;
        setMaxRadius(maxRadiusFt.toFixed(2));
        const zValues = vertices.map(v => Number(v.n_z));
        const minZ = Math.min(...zValues);
        const maxZ = Math.max(...zValues);
        setZMin(minZ.toFixed(2));
        setZMax(maxZ.toFixed(2));
        setCustomZMax(maxZ.toFixed(2));
      } else {
        setMaxRadius(null);
        setZMin("");
        setZMax("");
        setCustomZMax("");
      }
    } catch (e) {
      console.error("Error fetching zone vertices:", e);
    }
  };

  const retryReloadTriggers = async (retries = 3, delay = 1000) => {
    for (let attempt = 1; attempt <= retries; attempt++) {
      try {
        const reloadRes = await fetch(`${API_BASE_URL}/api/reload_triggers`, {
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

  const handleZoneChange = (zoneId) => {
    const parsedZoneId = parseInt(zoneId);
    const zone = zones.find(z => z.i_zn === parsedZoneId);
    if (zone && (!selectedZone || zone.i_zn !== selectedZone.i_zn)) {
      setSelectedZone(zone);
      fetchZoneVertices(zone.i_zn);
    } else if (!zone) {
      setSelectedZone(null);
      setZoneVertices([]);
      setMaxRadius(null);
      setZMin("");
      setZMax("");
      setCustomZMax("");
    }
  };

  const handleCreatePortableTrigger = async () => {
    if (!triggerName || !triggerDirection || !radius || !zMin || !zMax || (hostTagType === "real" && !hostTagId) || (hostTagType === "simulated" && !simTagId)) {
      alert("Please complete all required fields.");
      return;
    }
    const dir = triggerDirections.find(d => d.x_dir === triggerDirection);
    if (!dir) {
      alert("Invalid direction.");
      return;
    }
    const radiusFt = parseFloat(radius);
    const zMinFt = parseFloat(zMin);
    const zMaxFt = parseFloat(customZMax || zMax);
    if (zMinFt >= zMaxFt) {
      alert("Z Min must be less than Z Max.");
      return;
    }
    if (radiusFt <= 0) {
      alert("Radius must be positive.");
      return;
    }
    if (selectedZone && maxRadius && radiusFt > parseFloat(maxRadius)) {
      console.debug(`Radius ${radiusFt}ft exceeds max radius ${maxRadius}ft for zone ${selectedZone.i_zn}`);
      alert(`Radius exceeds maximum allowed (${maxRadius}ft) for the selected zone.`);
      return;
    }
    const assignedTagId = hostTagType === "real" ? hostTagId : simTagId;
    const payload = {
      name: triggerName,
      direction: dir.i_dir,
      ignore: false,
      zone_id: selectedZone ? parseInt(selectedZone.i_zn) : null,
      is_portable: true,
      assigned_tag_id: assignedTagId,
      radius_ft: radiusFt,
      z_min: zMinFt,
      z_max: zMaxFt,
      vertices: []
      // TODO: Consider adding Target Tag IDs field (x_id_trg_dev), may relate to manager subscriptions
    };
    console.debug("Creating portable trigger payload:", JSON.stringify(payload, null, 2));
    try {
      const res = await fetch(`${API_BASE_URL}/api/add_portable_trigger`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });
      console.debug(`API response status: ${res.status}`);
      const result = await res.json();
      console.debug("API response:", result);
      alert(`Trigger ID: ${result.trigger_id}`);
      setTriggerName("");
      setHostTagType("real");
      setHostTagId("");
      setSimTagId("");
      setRadius("");
      setZMin("");
      setZMax("");
      setCustomZMax("");
      setTriggerDirection("");
      setSelectedZone(null);
      setSelectedDeviceType(deviceTypes.length > 0 ? deviceTypes[0].i_typ_dev : "");
      const reloadSuccess = await retryReloadTriggers(3, 1000);
      if (!reloadSuccess) {
        alert("Trigger created, but failed to reload triggers on the server.");
      }
    } catch (e) {
      console.error("Portable trigger create error:", e);
      alert("Failed to create portable trigger.");
    }
  };

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

  useEffect(() => {
    fetchZones();
    fetchTriggerDirections();
    fetchDevices();
  }, []);

  const filteredDevices = devices
    .filter(d => d.i_typ_dev === selectedDeviceType)
    .sort((a, b) => a.x_id_dev.localeCompare(b.x_id_dev));

  return (
    <div>
      <h2>Portable Trigger Add</h2>
      {fetchError && <div style={{ color: "red" }}>{fetchError}</div>}
      <Tabs defaultActiveKey="portableTriggerAdd">
        <Tab eventKey="portableTriggerAdd" title="Portable Trigger Add">
          <Form.Group>
            <Form.Label>Select Zone (optional)</Form.Label>
            <Form.Control as="select" value={selectedZone?.i_zn || ""} onChange={e => handleZoneChange(e.target.value)}>
              <option value="">-- No Zone --</option>
              {renderZoneOptions(zoneHierarchy)}
            </Form.Control>
            {maxRadius && <p>Max Radius: {maxRadius}ft</p>}
          </Form.Group>
          <Form.Group>
            <Form.Label>Trigger Name</Form.Label>
            <Form.Control type="text" value={triggerName} onChange={e => setTriggerName(e.target.value)} />
          </Form.Group>
          <Form.Group>
            <Form.Label>Host Tag Type</Form.Label>
            <Form.Control as="select" value={hostTagType} onChange={e => setHostTagType(e.target.value)}>
              <option value="real">Real Device</option>
              <option value="simulated">Simulated Device</option>
            </Form.Control>
          </Form.Group>
          {hostTagType === "real" && (
            <>
              <Form.Group>
                <Form.Label>Device Type</Form.Label>
                <Form.Control as="select" value={selectedDeviceType} onChange={e => setSelectedDeviceType(parseInt(e.target.value))}>
                  {deviceTypes.map(t => (
                    <option key={t.i_typ_dev} value={t.i_typ_dev}>{t.x_dsc_dev}</option>
                  ))}
                </Form.Control>
              </Form.Group>
              <Form.Group>
                <Form.Label>Host Tag ID</Form.Label>
                <Form.Control as="select" value={hostTagId} onChange={e => setHostTagId(e.target.value)}>
                  <option value="">Select Host Tag</option>
                  {filteredDevices.map(d => (
                    <option key={d.x_id_dev} value={d.x_id_dev}>{`${d.x_id_dev} - ${d.x_nm_dev}`}</option>
                  ))}
                </Form.Control>
              </Form.Group>
            </>
          )}
          {hostTagType === "simulated" && (
            <Form.Group>
              <Form.Label>Simulated Tag ID</Form.Label>
              <Form.Control
                type="text"
                value={simTagId}
                onChange={e => setSimTagId(e.target.value)}
                placeholder="Enter SIM tag (e.g., SIM1)"
              />
            </Form.Group>
          )}
          <Form.Group>
            <Form.Label>Radius (feet)</Form.Label>
            <Form.Control
              type="number"
              value={radius}
              onChange={e => setRadius(e.target.value)}
              min="0.1"
              step="0.1"
              placeholder="Enter radius in feet"
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>Z Min (feet)</Form.Label>
            <Form.Control
              type="number"
              value={zMin}
              onChange={e => setZMin(e.target.value)}
              min="0"
              step="0.1"
              placeholder="Enter Z Min in feet"
            />
          </Form.Group>
          <Form.Group>
            <Form.Label>Z Max (feet)</Form.Label>
            <Form.Control
              type="number"
              value={customZMax || zMax}
              onChange={e => setCustomZMax(e.target.value)}
              min="0"
              step="0.1"
              placeholder="Enter Z Max in feet"
            />
            {zMin && (customZMax || zMax) && parseFloat(zMin) === parseFloat(customZMax || zMax) && (
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
          <Button onClick={handleCreatePortableTrigger}>Create Trigger</Button>
        </Tab>
        <Tab eventKey="deleteTriggers" title="Delete Triggers">
          <p>Reserved</p>
        </Tab>
        <Tab eventKey="events" title="System Events">
          <p>Reserved</p>
        </Tab>
      </Tabs>
    </div>
  );
};

export default PortableTriggerAdd;