// /home/parcoadmin/parco_fastapi/app/src/components/EntityMergeDemo.js
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
        const response = await fetch("http://192.168.210.226:8000/api/list_device_types");
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
        const response = await fetch("http://192.168.210.226:8000/api/list_entity_types");
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
        const response = await fetch("http://192.168.210.226:8000/api/list_assignment_reasons");
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
          const response = await fetch(`http://192.168.210.226:8000/api/get_device_by_type/${typeId}`);
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
        const entitiesResponse = await fetch("http://192.168.210.226:8000/api/list_all_entities");
        if (!entitiesResponse.ok) throw new Error(`HTTP error! Status: ${entitiesResponse.status}`);
        const entitiesData = await entitiesResponse.json();
        console.log("✅ Fetched entities:", entitiesData);
        setEntities(entitiesData);

        // Fetch assignments for each entity
        const assignments = {};
        for (const entity of entitiesData) {
          const response = await fetch(`http://192.168.210.226:8000/api/list_device_assignments_by_entity/${entity.x_id_ent}`);
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

      const createEntityResponse = await fetch("http://192.168.210.226:8000/add_entity", {
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

      const entitiesResponse = await fetch("http://192.168.210.226:8000/api/list_all_entities");
      if (!entitiesResponse.ok) throw new Error(`HTTP error! Status: ${entitiesResponse.status}`);
      const entitiesData = await entitiesResponse.json();
      setEntities(entitiesData);

      const assignments = {};
      for (const entity of entitiesData) {
        const response = await fetch(`http://192.168.210.226:8000/api/list_device_assignments_by_entity/${entity.x_id_ent}`);
        if (!response.ok) {
          if (response.status === 404) {
            assignments[entity.x_id_ent] = [];
            continue;
          }
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        assignments[entity.x_id_ent] = await response.json();
      }
      setEntityAssignments(assignments);
      entityHierarchyRef.current = Object.fromEntries(
        Object.entries(assignments).map(([entityId, assigns]) => [
          entityId,
          assigns.reduce((acc, assign) => {
            acc[assign.x_id_dev] = assign;
            return acc;
          }, {}),
        ])
      );

      alert(`Successfully merged devices ${parentDeviceId} and ${childDeviceId} into entity ${newEntityId}`);
    } catch (error) {
      console.error("❌ Error merging devices:", error);
      setError(`Error merging devices: ${error.message}`);
    }
  };

  const assignDeviceToEntity = async (deviceId, entityId, parentEntityId = null) => {
    try {
      const formData = new FormData();
      formData.append("device_id", deviceId);
      formData.append("entity_id", entityId);
      formData.append("reason_id", selectedReasonId);

      const assignResponse = await fetch("http://192.168.210.226:8000/api/assign_device_to_zone", {
        method: "POST",
        body: formData,
      });
      if (!assignResponse.ok) throw new Error(`Failed to assign device ${deviceId}: ${assignResponse.status}`);
      const assignResult = await assignResponse.json();
      console.log(`Assigned ${deviceId} to entity ${entityId}:`, assignResult);

      mergedDevicesRef.current.add(deviceId);
    } catch (error) {
      throw new Error(`Failed to assign device ${deviceId}: ${error.message}`);
    }
  };

  const handleDeviceTypeChange = (typeId) => {
    setSelectedDeviceTypes(prev =>
      prev.includes(typeId)
        ? prev.filter(id => id !== typeId)
        : [...prev, typeId]
    );
  };

  const renderHierarchy = () => {
    const buildTree = (entityId, assignments, depth = 0) => {
      const children = assignments.filter(a => a.x_id_pnt === entityId);
      const indent = "  ".repeat(depth);
      const entityDevices = assignments.filter(a => a.x_id_ent === entityId && !a.x_id_pnt);
      const deviceList = entityDevices.map(a => `${indent}- Tag ${a.x_id_dev}`).join("\n");
      const childTrees = children.map(child => {
        const childAssignments = entityAssignments[child.x_id_ent] || [];
        return `${indent}- Child Entity ${child.x_id_ent}\n${buildTree(child.x_id_ent, childAssignments, depth + 1)}`;
      }).join("\n");
      return `${deviceList}${childTrees ? "\n" + childTrees : ""}`;
    };

    return entities.map(entity => {
      const assignments = entityAssignments[entity.x_id_ent] || [];
      if (assignments.length === 0) return null;
      return (
        <div key={entity.x_id_ent} style={{ marginBottom: "10px" }}>
          <strong>Entity {entity.x_id_ent}</strong>
          <pre style={{ fontSize: "12px", whiteSpace: "pre-wrap" }}>
            {buildTree(entity.x_id_ent, assignments)}
          </pre>
        </div>
      );
    });
  };

  return (
    <Row>
      <Col md={8}>
        <h2>Entity Merge Demo</h2>
        {error && <div style={{ color: "red" }}>{error}</div>}
        <Form.Group>
          <Form.Label>Select Device Types (Tags)</Form.Label>
          {deviceTypes.map(type => (
            <Form.Check
              key={type.i_typ_dev}
              type="checkbox"
              label={`${type.x_dsc_dev} (ID: ${type.i_typ_dev})`}
              checked={selectedDeviceTypes.includes(type.i_typ_dev)}
              onChange={() => handleDeviceTypeChange(type.i_typ_dev)}
            />
          ))}
        </Form.Group>
        <Form.Group>
          <Form.Label>Entity Type for New Entities</Form.Label>
          <Form.Control
            as="select"
            value={selectedEntityType}
            onChange={e => setSelectedEntityType(e.target.value)}
          >
            <option value="">Select Entity Type</option>
            {entityTypes.map(type => (
              <option key={type.i_typ_ent} value={type.i_typ_ent}>
                {type.x_nm_typ} (ID: {type.i_typ_ent})
              </option>
            ))}
          </Form.Control>
        </Form.Group>
        <Form.Group>
          <Form.Label>Assignment Reason for Merging</Form.Label>
          <Form.Control
            as="select"
            value={selectedReasonId}
            onChange={e => setSelectedReasonId(e.target.value)}
          >
            <option value="">Select Reason</option>
            {assignmentReasons.map(reason => (
              <option key={reason.i_rsn} value={reason.i_rsn}>
                {reason.x_rsn} (ID: {reason.i_rsn})
              </option>
            ))}
          </Form.Control>
        </Form.Group>
        <EntityMap
          devices={devices}
          entities={entities}
          entityAssignments={entityAssignments}
          entityHierarchy={entityHierarchyRef.current}
          onMerge={handleMerge}
          onAssign={assignDeviceToEntity}
        />
      </Col>
      <Col md={4}>
        <h3>Entity Hierarchy</h3>
        <div style={{ maxHeight: "600px", overflowY: "auto", border: "1px solid #ccc", padding: "10px" }}>
          {entities.length === 0 ? (
            <p>No entities found.</p>
          ) : (
            renderHierarchy()
          )}
        </div>
      </Col>
    </Row>
  );
});

export default EntityMergeDemo;