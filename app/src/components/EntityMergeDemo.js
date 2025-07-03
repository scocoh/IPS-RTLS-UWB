/* Name: EntityMergeDemo.js */
/* Version: 0.1.1 */
/* Created: 971201 */
/* Modified: 250703 */
/* Creator: ParcoAdmin */
/* Modified By: AI Assistant */
/* Description: JavaScript file for ParcoRTLS frontend - Updated to use centralized configuration */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components */
/* Role: Frontend */
/* Status: Active */
/* Dependent: TRUE */

// /home/parcoadmin/parco_fastapi/app/src/components/EntityMergeDemo.js
// Version: v0.1.0 - Updated to use centralized configuration instead of hardcoded IP
// Version: v0.0.9 - Refactored to use EntityMap component for Leaflet map rendering
// Version: v0.0.8 - Fixed marker creation timing, added static marker for testing, improved logging
// Version: v0.0.7 - Added default coordinates for devices and entities with missing locations
// Version: v0.0.6 - Handled 404 in fetchDevices to return empty array
// Version: v0.0.5 - Handled 404 in fetchEntitiesAndAssignments, pre-selected device types, ensured map display
// Version: v0.0.4 - Added dynamic entity_type and reason_id selection, added hierarchy display
// Version: v0.0.3 - Fixed 404 errors by adding /api/ prefix to fetch calls
// Version: v0.0.2 - Updated for device type selection, entity display, and hierarchical merging
// ParcoRTLS © 2025 — Scott Cohen, Jesse Chunn, etc.
import React, { useEffect, useRef, useState, memo } from "react";
import { Form, Button, Col, Row } from "react-bootstrap";
import EntityMap from "./EntityMap";
import { config, getApiUrl } from "../config";

const EntityMergeDemo = memo(() => {
  const [deviceTypes, setDeviceTypes] = useState([]);
  const [selectedDeviceTypes, setSelectedDeviceTypes] = useState([1, 2, 3]); // Pre-select tag types
  const [devices, setDevices] = useState([]);
  const [entities, setEntities] = useState([]);
  const [entityAssignments, setEntityAssignments] = useState({});
  const [entityTypes, setEntityTypes] = useState([]);
  const [selectedEntityType, setSelectedEntityType] = useState("");
  const [assignmentReasons, setAssignmentReasons] = useState([]);
  const [selectedReasonId, setSelectedReasonId] = useState("");
  const [error, setError] = useState(null);
  const mergedDevicesRef = useRef(new Set()); // Track merged device IDs
  const entityHierarchyRef = useRef({}); // Track entity hierarchy

  // Fetch device types, entity types, and assignment reasons on mount
  useEffect(() => {
    const fetchDeviceTypes = async () => {
      try {
        const response = await fetch(getApiUrl("/api/list_device_types"));
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        console.log("✅ Fetched device types:", data);
        setDeviceTypes(data);
        setError(null);
      } catch (error) {
        console.error("❌ Error fetching device types:", error);
        setError(`Error fetching device types: ${error.message}`);
      }
    };

    const fetchEntityTypes = async () => {
      try {
        const response = await fetch(getApiUrl("/api/list_entity_types"));
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        console.log("✅ Fetched entity types:", data);
        setEntityTypes(data);
        if (data.length > 0) setSelectedEntityType(data[0].i_typ_ent); // Default to first entity type
      } catch (error) {
        console.error("❌ Error fetching entity types:", error);
        setError(`Error fetching entity types: ${error.message}`);
      }
    };

    const fetchAssignmentReasons = async () => {
      try {
        const response = await fetch(getApiUrl("/api/list_assignment_reasons"));
        if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
        const data = await response.json();
        console.log("✅ Fetched assignment reasons:", data);
        setAssignmentReasons(data);
        const mergeReason = data.find(r => r.x_rsn.toLowerCase().includes("drag-and-drop")) || data[0];
        if (mergeReason) setSelectedReasonId(mergeReason.i_rsn); // Default to merge reason or first reason
      } catch (error) {
        console.error("❌ Error fetching assignment reasons:", error);
        setError(`Error fetching assignment reasons: ${error.message}`);
      }
    };

    fetchDeviceTypes();
    fetchEntityTypes();
    fetchAssignmentReasons();
  }, []);

  // Fetch devices based on selected device types
  useEffect(() => {
    if (selectedDeviceTypes.length === 0) {
      setDevices([]);
      return;
    }

    const fetchDevices = async () => {
      try {
        const devicesPromises = selectedDeviceTypes.map(async (typeId) => {
          const response = await fetch(getApiUrl(`/api/get_device_by_type/${typeId}`));
          if (!response.ok) {
            if (response.status === 404) {
              return []; // Treat 404 as no devices for this type
            }
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          return response.json();
        });
        const allDevices = (await Promise.all(devicesPromises)).flat();
        console.log("✅ Fetched devices:", allDevices);
        setDevices(allDevices);
        setError(null);
      } catch (error) {
        console.error("❌ Error fetching devices:", error);
        setError(`Error fetching devices: ${error.message}`);
      }
    };
    fetchDevices();
  }, [selectedDeviceTypes]);

  // Fetch entities and their assignments
  useEffect(() => {
    const fetchEntitiesAndAssignments = async () => {
      try {
        // Fetch all entities
        const entitiesResponse = await fetch(getApiUrl("/api/list_all_entities"));
        if (!entitiesResponse.ok) throw new Error(`HTTP error! Status: ${entitiesResponse.status}`);
        const entitiesData = await entitiesResponse.json();
        console.log("✅ Fetched entities:", entitiesData);
        setEntities(entitiesData);

        // Fetch assignments for each entity
        const assignments = {};
        for (const entity of entitiesData) {
          const response = await fetch(getApiUrl(`/api/list_device_assignments_by_entity/${entity.x_id_ent}`));
          if (!response.ok) {
            if (response.status === 404) {
              assignments[entity.x_id_ent] = []; // Treat 404 as no assignments
              continue;
            }
            throw new Error(`HTTP error! Status: ${response.status}`);
          }
          const assignmentData = await response.json();
          assignments[entity.x_id_ent] = assignmentData;
        }
        console.log("✅ Fetched entity assignments:", assignments);
        setEntityAssignments(assignments);

        // Build entity hierarchy
        const hierarchy = {};
        for (const [entityId, assigns] of Object.entries(assignments)) {
          hierarchy[entityId] = assigns.reduce((acc, assign) => {
            acc[assign.x_id_dev] = assign; // Map device to its assignment
            return acc;
          }, {});
        }
        entityHierarchyRef.current = hierarchy;
        console.log("Entity hierarchy:", hierarchy);
      } catch (error) {
        console.error("❌ Error fetching entities/assignments:", error);
        setError(`Error fetching entities/assignments: ${error.message}`);
      }
    };
    fetchEntitiesAndAssignments();
  }, []);

  // Handle merging two devices into a new entity
  const handleMerge = async (parentDeviceId, childDeviceId) => {
    try {
      if (!selectedEntityType || !selectedReasonId) {
        alert("Please select an entity type and assignment reason.");
        return;
      }

      const newEntityId = crypto.randomUUID();
      console.log(`Merging devices ${parentDeviceId} (parent) and ${childDeviceId} (child) into entity ${newEntityId}`);

      const createEntityResponse = await fetch(getApiUrl("/add_entity"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          entity_id: newEntityId,
          entity_type: parseInt(selectedEntityType),
          entity_name: "Merged_Entity",
        }),
      });
      if (!createEntityResponse.ok) throw new Error(`Failed to create entity: ${createEntityResponse.status}`);
      const createEntityResult = await createEntityResponse.json();
      console.log("Entity created:", createEntityResult);

      await assignDeviceToEntity(parentDeviceId, newEntityId, null);
      await assignDeviceToEntity(childDeviceId, newEntityId, null);

      const entitiesResponse = await fetch(getApiUrl("/api/list_all_entities"));
      if (!entitiesResponse.ok) throw new Error(`HTTP error! Status: ${entitiesResponse.status}`);
      const entitiesData = await entitiesResponse.json();
      setEntities(entitiesData);

      const assignments = {};
      for (const entity of entitiesData) {
        const response = await fetch(getApiUrl(`/api/list_device_assignments_by_entity/${entity.x_id_ent}`));
        if (!response.ok) {
          if (response.status === 404) {
            assignments[entity.x_id_ent] = [];
            continue;
          }
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        const data = await response.json();
        assignments[entity.x_id_ent] = data;
      }
      setEntityAssignments(assignments);

      mergedDevicesRef.current.add(parentDeviceId);
      mergedDevicesRef.current.add(childDeviceId);
      console.log(`✅ Devices ${parentDeviceId} and ${childDeviceId} merged into entity ${newEntityId}`);
    } catch (error) {
      console.error("❌ Error merging devices:", error);
      setError(`Error merging devices: ${error.message}`);
    }
  };

  // Assign a device to an entity
  const assignDeviceToEntity = async (deviceId, entityId, parentEntityId) => {
    const response = await fetch(getApiUrl("/api/assign_device_to_zone"), {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        device_id: deviceId,
        entity_id: entityId,
        parent_entity_id: parentEntityId,
        reason_id: parseInt(selectedReasonId),
      }),
    });
    if (!response.ok) throw new Error(`Failed to assign device: ${response.status}`);
    const result = await response.json();
    console.log(`Device ${deviceId} assigned to entity ${entityId}:`, result);
  };

  // Handle device type selection
  const handleDeviceTypeToggle = (typeId) => {
    setSelectedDeviceTypes(prev =>
      prev.includes(typeId) ? prev.filter(id => id !== typeId) : [...prev, typeId]
    );
  };

  // Determine map devices and entities (includes error handling)
  const mapDevices = devices
    .filter(device => !mergedDevicesRef.current.has(device.x_id_dev))
    .map(device => ({
      ...device,
      n_moe_x: device.n_moe_x || Math.random() * 100,
      n_moe_y: device.n_moe_y || Math.random() * 100,
      n_moe_z: device.n_moe_z || 0,
    }));

  const mapEntities = entities.map(entity => ({
    ...entity,
    x: entity.x || Math.random() * 100 + 50,
    y: entity.y || Math.random() * 100 + 50,
    z: entity.z || 0,
    devices: entityAssignments[entity.x_id_ent] || [],
  }));

  return (
    <div style={{ padding: "20px" }}>
      <h1>Entity Merge Demo</h1>
      {error && <div style={{ color: "red", marginBottom: "10px" }}>⚠️ {error}</div>}

      <Row style={{ marginBottom: "20px" }}>
        <Col md={6}>
          <h3>Select Device Types</h3>
          <Form>
            {deviceTypes.map(type => (
              <Form.Check
                key={type.i_typ_dev}
                type="checkbox"
                label={`${type.x_dsc_dev} (Type ${type.i_typ_dev})`}
                checked={selectedDeviceTypes.includes(type.i_typ_dev)}
                onChange={() => handleDeviceTypeToggle(type.i_typ_dev)}
              />
            ))}
          </Form>
        </Col>
        <Col md={6}>
          <h3>Merge Configuration</h3>
          <Form.Group>
            <Form.Label>Entity Type</Form.Label>
            <Form.Control
              as="select"
              value={selectedEntityType}
              onChange={(e) => setSelectedEntityType(e.target.value)}
            >
              <option value="">Select Entity Type</option>
              {entityTypes.map(type => (
                <option key={type.i_typ_ent} value={type.i_typ_ent}>
                  {type.x_dsc_ent} (Type {type.i_typ_ent})
                </option>
              ))}
            </Form.Control>
          </Form.Group>
          <Form.Group style={{ marginTop: "10px" }}>
            <Form.Label>Assignment Reason</Form.Label>
            <Form.Control
              as="select"
              value={selectedReasonId}
              onChange={(e) => setSelectedReasonId(e.target.value)}
            >
              <option value="">Select Reason</option>
              {assignmentReasons.map(reason => (
                <option key={reason.i_rsn} value={reason.i_rsn}>
                  {reason.x_rsn} (ID: {reason.i_rsn})
                </option>
              ))}
            </Form.Control>
          </Form.Group>
        </Col>
      </Row>

      <Row>
        <Col md={8}>
          <h3>Map View</h3>
          <div style={{ height: "600px", border: "1px solid #ccc" }}>
            <EntityMap
              devices={mapDevices}
              entities={mapEntities}
              onMerge={handleMerge}
              selectedEntityType={selectedEntityType}
              selectedReasonId={selectedReasonId}
            />
          </div>
        </Col>
        <Col md={4}>
          <h3>Entity Hierarchy</h3>
          <div style={{ maxHeight: "600px", overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
            {entities.length === 0 ? (
              <p>No entities created yet. Drag devices to merge them.</p>
            ) : (
              entities.map(entity => (
                <div key={entity.x_id_ent} style={{ marginBottom: "10px", padding: "5px", backgroundColor: "#f0f0f0" }}>
                  <strong>{entity.x_nm_ent || entity.x_id_ent}</strong> (Type: {entity.i_typ_ent})
                  <ul>
                    {(entityAssignments[entity.x_id_ent] || []).map(assignment => (
                      <li key={assignment.x_id_dev}>
                        Device: {assignment.x_id_dev} (Reason: {assignment.i_rsn})
                      </li>
                    ))}
                  </ul>
                </div>
              ))
            )}
          </div>
        </Col>
      </Row>

      <div style={{ marginTop: "20px" }}>
        <h3>Device List</h3>
        <p>Total Devices: {devices.length} | Unmerged: {mapDevices.length} | Merged: {mergedDevicesRef.current.size}</p>
      </div>
    </div>
  );
});

export default EntityMergeDemo;