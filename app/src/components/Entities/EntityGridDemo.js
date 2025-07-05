/* Name: EntityGridDemo.js */
/* Version: 0.2.1 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: AI Assistant */
/* Description: Main grid interface container for Entity management - structured grid approach */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/Entities */
/* Role: Frontend Container Component */
/* Status: Active */
/* Dependent: TRUE */

// /home/parcoadmin/parco_fastapi/app/src/components/Entities/EntityGridDemo.js
// Version: v0.2.1 - Initial creation with grid-based entity management interface
// ParcoRTLS © 2025 — Scott Cohen, Jesse Chunn, etc.

import React, { useEffect, useState, useCallback, useRef } from 'react';
import { Form, Button, Col, Row, Alert, Modal } from 'react-bootstrap';
import { EntityAPI } from './EntityAPI';
import EntityGridView from './EntityGridView';
import { 
  DEFAULT_ENTITY_TYPES, 
  DEFAULT_ASSIGNMENT_REASONS, 
  DEFAULT_DEVICE_TYPES,
  COMPONENT_STATES,
  ERROR_MESSAGES,
  SUCCESS_MESSAGES,
  UTILS
} from './EntityTypes';

/**
 * EntityGridDemo Component - Main container for grid-based entity management
 */
const EntityGridDemo = () => {
  // State management
  const [componentState, setComponentState] = useState(COMPONENT_STATES.LOADING);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);

  // Data states
  const [deviceTypes, setDeviceTypes] = useState(DEFAULT_DEVICE_TYPES);
  const [selectedDeviceTypes, setSelectedDeviceTypes] = useState([1, 2, 3]);
  const [devices, setDevices] = useState([]);
  const [entities, setEntities] = useState([]);
  const [entityAssignments, setEntityAssignments] = useState({});
  const [entityTypes, setEntityTypes] = useState(DEFAULT_ENTITY_TYPES);
  const [selectedEntityType, setSelectedEntityType] = useState('');
  const [assignmentReasons, setAssignmentReasons] = useState(DEFAULT_ASSIGNMENT_REASONS);
  const [selectedReasonId, setSelectedReasonId] = useState('');

  // Modal states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newEntityName, setNewEntityName] = useState('');
  const [creatingEntity, setCreatingEntity] = useState(false);

  // Refs
  const refreshTimeoutRef = useRef(null);

  // Clear messages after delay
  const clearMessages = useCallback(() => {
    setTimeout(() => {
      setError(null);
      setSuccess(null);
    }, 5000);
  }, []);

  // Load initial data
  useEffect(() => {
    const loadInitialData = async () => {
      try {
        setComponentState(COMPONENT_STATES.LOADING);
        setError(null);

        // Load all initial data in parallel
        const [deviceTypesData, entityTypesData, assignmentReasonsData] = await Promise.all([
          EntityAPI.fetchDeviceTypes().catch(() => DEFAULT_DEVICE_TYPES),
          EntityAPI.fetchEntityTypes().catch(() => DEFAULT_ENTITY_TYPES),
          EntityAPI.fetchAssignmentReasons().catch(() => DEFAULT_ASSIGNMENT_REASONS)
        ]);

        setDeviceTypes(deviceTypesData);
        setEntityTypes(entityTypesData);
        setAssignmentReasons(assignmentReasonsData);

        // Set default selections
        if (entityTypesData.length > 0 && !selectedEntityType) {
          setSelectedEntityType(entityTypesData[0].i_typ_ent.toString());
        }
        if (assignmentReasonsData.length > 0 && !selectedReasonId) {
          setSelectedReasonId(assignmentReasonsData[0].i_rsn.toString());
        }

        setComponentState(COMPONENT_STATES.READY);
      } catch (error) {
        console.error('❌ EntityGridDemo: Error loading initial data:', error);
        setError(`${ERROR_MESSAGES.FETCH_FAILED}: ${error.message}`);
        setComponentState(COMPONENT_STATES.ERROR);
      }
    };

    loadInitialData();
  }, [selectedEntityType, selectedReasonId]);

  // Load devices when device types change
  useEffect(() => {
    if (selectedDeviceTypes.length === 0 || componentState !== COMPONENT_STATES.READY) return;

    const loadDevices = async () => {
      try {
        const devicesData = await EntityAPI.fetchDevices(selectedDeviceTypes);
        setDevices(devicesData);
      } catch (error) {
        console.error('❌ EntityGridDemo: Error loading devices:', error);
        setError(`Error loading devices: ${error.message}`);
      }
    };

    loadDevices();
  }, [selectedDeviceTypes, componentState]);

  // Load entities and assignments
  useEffect(() => {
    if (componentState !== COMPONENT_STATES.READY) return;

    const loadEntitiesAndAssignments = async () => {
      try {
        const { entities: entitiesData, assignments } = await EntityAPI.fetchEntitiesAndAssignments();
        setEntities(entitiesData);
        setEntityAssignments(assignments);
      } catch (error) {
        console.error('❌ EntityGridDemo: Error loading entities:', error);
        setError(`Error loading entities: ${error.message}`);
      }
    };

    loadEntitiesAndAssignments();
  }, [componentState]);

  // Handle device type selection
  const handleDeviceTypeToggle = useCallback((typeId) => {
    setSelectedDeviceTypes(prev =>
      prev.includes(typeId) ? 
        prev.filter(id => id !== typeId) : 
        [...prev, typeId]
    );
  }, []);

  // Handle tag drop on entity
  const handleTagDrop = useCallback(async (tag, entity) => {
    if (!selectedReasonId) {
      setError('Please select an assignment reason before dropping tags');
      clearMessages();
      return;
    }

    try {
      console.log(`Assigning tag ${tag.x_id_dev} to entity ${entity.x_id_ent}`);
      
      await EntityAPI.assignDeviceToEntity(
        tag.x_id_dev,
        entity.x_id_ent,
        null,
        parseInt(selectedReasonId)
      );

      // Refresh entities and assignments
      const { entities: entitiesData, assignments } = await EntityAPI.fetchEntitiesAndAssignments();
      setEntities(entitiesData);
      setEntityAssignments(assignments);

      setSuccess(`${SUCCESS_MESSAGES.ASSIGNMENT_SUCCESS}: ${tag.x_id_dev} → ${entity.x_nm_ent || entity.x_id_ent}`);
      clearMessages();
    } catch (error) {
      console.error('❌ EntityGridDemo: Error assigning tag:', error);
      setError(`${ERROR_MESSAGES.ASSIGNMENT_FAILED}: ${error.message}`);
      clearMessages();
    }
  }, [selectedReasonId, clearMessages]);

  // Handle create entity button click
  const handleCreateEntity = useCallback(() => {
    if (!selectedEntityType) {
      setError('Please select an entity type before creating an entity');
      clearMessages();
      return;
    }
    setNewEntityName('');
    setShowCreateModal(true);
  }, [selectedEntityType, clearMessages]);

  // Handle create entity submission
  const handleCreateEntitySubmit = useCallback(async () => {
    if (!UTILS.isValidEntityName(newEntityName)) {
      setError('Please enter a valid entity name (3-50 characters)');
      clearMessages();
      return;
    }

    try {
      setCreatingEntity(true);
      
      const newEntityId = UTILS.generateEntityId();
      
      await EntityAPI.createEntity({
        entity_id: newEntityId,
        entity_type: parseInt(selectedEntityType),
        entity_name: newEntityName.trim(),
      });

      // Refresh entities and assignments
      const { entities: entitiesData, assignments } = await EntityAPI.fetchEntitiesAndAssignments();
      setEntities(entitiesData);
      setEntityAssignments(assignments);

      setSuccess(`${SUCCESS_MESSAGES.CREATION_SUCCESS}: ${newEntityName}`);
      setShowCreateModal(false);
      setNewEntityName('');
      clearMessages();
    } catch (error) {
      console.error('❌ EntityGridDemo: Error creating entity:', error);
      setError(`${ERROR_MESSAGES.CREATION_FAILED}: ${error.message}`);
      clearMessages();
    } finally {
      setCreatingEntity(false);
    }
  }, [newEntityName, selectedEntityType, clearMessages]);

  // Handle create entity modal close
  const handleCreateEntityClose = useCallback(() => {
    setShowCreateModal(false);
    setNewEntityName('');
    setCreatingEntity(false);
  }, []);

  // Auto-refresh data periodically
  useEffect(() => {
    if (componentState !== COMPONENT_STATES.READY) return;

    const refreshData = async () => {
      try {
        const { entities: entitiesData, assignments } = await EntityAPI.fetchEntitiesAndAssignments();
        setEntities(entitiesData);
        setEntityAssignments(assignments);
      } catch (error) {
        // Silent refresh failure - don't show error for background refresh
        console.warn('Background refresh failed:', error);
      }
    };

    // Refresh every 30 seconds
    refreshTimeoutRef.current = setInterval(refreshData, 30000);

    return () => {
      if (refreshTimeoutRef.current) {
        clearInterval(refreshTimeoutRef.current);
      }
    };
  }, [componentState]);

  // Render loading state
  if (componentState === COMPONENT_STATES.LOADING) {
    return (
      <div style={{ padding: '20px', textAlign: 'center' }}>
        <h1>Entity Grid Demo</h1>
        <div style={{ marginTop: '20px' }}>
          <div className="spinner-border text-primary" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
          <p style={{ marginTop: '10px' }}>Loading entity grid interface...</p>
        </div>
      </div>
    );
  }

  // Render error state
  if (componentState === COMPONENT_STATES.ERROR) {
    return (
      <div style={{ padding: '20px' }}>
        <h1>Entity Grid Demo</h1>
        <Alert variant="danger" style={{ marginTop: '20px' }}>
          <Alert.Heading>Error Loading Grid Interface</Alert.Heading>
          <p>{error || 'An unexpected error occurred while loading the grid interface.'}</p>
          <Button variant="outline-danger" onClick={() => window.location.reload()}>
            Reload Page
          </Button>
        </Alert>
      </div>
    );
  }

  return (
    <div style={{ padding: '20px' }}>
      <h1>Entity Grid Demo</h1>
      
      {/* Error and Success Messages */}
      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}
      {success && (
        <Alert variant="success" dismissible onClose={() => setSuccess(null)}>
          {success}
        </Alert>
      )}

      {/* Configuration Panel */}
      <Row style={{ marginBottom: '20px' }}>
        <Col md={4}>
          <h3>Device Types</h3>
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
        
        <Col md={4}>
          <h3>Entity Configuration</h3>
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
        </Col>
        
        <Col md={4}>
          <h3>Assignment Configuration</h3>
          <Form.Group>
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

      {/* Main Grid View */}
      <EntityGridView
        devices={devices}
        entities={entities}
        entityAssignments={entityAssignments}
        entityTypes={entityTypes}
        selectedEntityType={selectedEntityType}
        onEntityTypeChange={setSelectedEntityType}
        onTagDrop={handleTagDrop}
        onCreateEntity={handleCreateEntity}
        loading={componentState === COMPONENT_STATES.LOADING}
      />

      {/* Create Entity Modal */}
      <Modal show={showCreateModal} onHide={handleCreateEntityClose}>
        <Modal.Header closeButton>
          <Modal.Title>Create New Entity</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Form>
            <Form.Group>
              <Form.Label>Entity Name</Form.Label>
              <Form.Control
                type="text"
                placeholder="Enter entity name"
                value={newEntityName}
                onChange={(e) => setNewEntityName(e.target.value)}
                disabled={creatingEntity}
              />
              <Form.Text className="text-muted">
                3-50 characters required
              </Form.Text>
            </Form.Group>
            <Form.Group style={{ marginTop: '10px' }}>
              <Form.Label>Entity Type</Form.Label>
              <Form.Control
                as="select"
                value={selectedEntityType}
                onChange={(e) => setSelectedEntityType(e.target.value)}
                disabled={creatingEntity}
              >
                <option value="">Select Entity Type</option>
                {entityTypes.map(type => (
                  <option key={type.i_typ_ent} value={type.i_typ_ent}>
                    {type.x_dsc_ent} (Type {type.i_typ_ent})
                  </option>
                ))}
              </Form.Control>
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={handleCreateEntityClose} disabled={creatingEntity}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleCreateEntitySubmit} disabled={creatingEntity}>
            {creatingEntity ? 'Creating...' : 'Create Entity'}
          </Button>
        </Modal.Footer>
      </Modal>
    </div>
  );
};

export default EntityGridDemo;