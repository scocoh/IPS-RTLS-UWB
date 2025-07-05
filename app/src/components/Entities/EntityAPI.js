/* Name: EntityAPI.js */
/* Version: 0.2.1 */
/* Created: 250704 */
/* Modified: 250704 */
/* Creator: ParcoAdmin */
/* Modified By: AI Assistant */
/* Description: Shared API calls for Entity management - extracted from EntityMergeDemo.js */
/* Location: /home/parcoadmin/parco_fastapi/app/src/components/Entities */
/* Role: Frontend API Service */
/* Status: Active */
/* Dependent: TRUE */

// /home/parcoadmin/parco_fastapi/app/src/components/Entities/EntityAPI.js
// Version: v0.2.1 - Initial creation with extracted API functions from EntityMergeDemo.js
// ParcoRTLS © 2025 — Scott Cohen, Jesse Chunn, etc.

import { getApiUrl } from "../../config";

/**
 * Shared API service for Entity management
 * Extracted from EntityMergeDemo.js to avoid code duplication
 */
export const EntityAPI = {
  /**
   * Fetch all device types
   * @returns {Promise<Array>} Array of device types
   */
  async fetchDeviceTypes() {
    try {
      const response = await fetch(getApiUrl("/api/list_device_types"));
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      const data = await response.json();
      console.log("✅ EntityAPI: Fetched device types:", data);
      return data;
    } catch (error) {
      console.error("❌ EntityAPI: Error fetching device types:", error);
      throw error;
    }
  },

  /**
   * Fetch all entity types
   * @returns {Promise<Array>} Array of entity types
   */
  async fetchEntityTypes() {
    try {
      const response = await fetch(getApiUrl("/api/list_entity_types"));
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      const data = await response.json();
      console.log("✅ EntityAPI: Fetched entity types:", data);
      return data;
    } catch (error) {
      console.error("❌ EntityAPI: Error fetching entity types:", error);
      throw error;
    }
  },

  /**
   * Fetch all assignment reasons
   * @returns {Promise<Array>} Array of assignment reasons
   */
  async fetchAssignmentReasons() {
    try {
      const response = await fetch(getApiUrl("/api/list_assignment_reasons"));
      if (!response.ok) throw new Error(`HTTP error! Status: ${response.status}`);
      const data = await response.json();
      console.log("✅ EntityAPI: Fetched assignment reasons:", data);
      return data;
    } catch (error) {
      console.error("❌ EntityAPI: Error fetching assignment reasons:", error);
      throw error;
    }
  },

  /**
   * Fetch devices by selected device types
   * @param {Array<number>} selectedDeviceTypes - Array of device type IDs
   * @returns {Promise<Array>} Array of devices
   */
  async fetchDevices(selectedDeviceTypes) {
    try {
      const devicesPromises = selectedDeviceTypes.map(async (typeId) => {
        const response = await fetch(getApiUrl(`/api/list_devices_by_type/${typeId}`));
        if (!response.ok) {
          if (response.status === 404) {
            console.log(`No devices found for type ${typeId}`);
            return [];
          }
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      });
      const allDevices = (await Promise.all(devicesPromises)).flat();
      console.log("✅ EntityAPI: Fetched devices:", allDevices);
      return allDevices;
    } catch (error) {
      console.error("❌ EntityAPI: Error fetching devices:", error);
      throw error;
    }
  },

  /**
   * Fetch all entities and their assignments
   * @returns {Promise<{entities: Array, assignments: Object}>} Entities and their assignments
   */
  async fetchEntitiesAndAssignments() {
    try {
      // Fetch all entities
      const entitiesResponse = await fetch(getApiUrl("/api/list_all_entities"));
      if (!entitiesResponse.ok) throw new Error(`HTTP error! Status: ${entitiesResponse.status}`);
      const entitiesData = await entitiesResponse.json();
      console.log("✅ EntityAPI: Fetched entities:", entitiesData);

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
      console.log("✅ EntityAPI: Fetched entity assignments:", assignments);

      return { entities: entitiesData, assignments };
    } catch (error) {
      console.error("❌ EntityAPI: Error fetching entities/assignments:", error);
      throw error;
    }
  },

  /**
   * Create a new entity
   * @param {Object} entityData - Entity data {entity_id, entity_type, entity_name}
   * @returns {Promise<Object>} Created entity response
   */
  async createEntity(entityData) {
    try {
      const response = await fetch(getApiUrl("/add_entity"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(entityData),
      });
      if (!response.ok) throw new Error(`Failed to create entity: ${response.status}`);
      const result = await response.json();
      console.log("✅ EntityAPI: Entity created:", result);
      return result;
    } catch (error) {
      console.error("❌ EntityAPI: Error creating entity:", error);
      throw error;
    }
  },

  /**
   * Assign a device to an entity
   * @param {string} deviceId - Device ID
   * @param {string} entityId - Entity ID
   * @param {string|null} parentEntityId - Parent entity ID (optional)
   * @param {number} reasonId - Assignment reason ID
   * @returns {Promise<Object>} Assignment response
   */
  async assignDeviceToEntity(deviceId, entityId, parentEntityId, reasonId) {
    try {
      const response = await fetch(getApiUrl("/api/assign_device_to_zone"), {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          device_id: deviceId,
          entity_id: entityId,
          parent_entity_id: parentEntityId,
          reason_id: reasonId,
        }),
      });
      if (!response.ok) throw new Error(`Failed to assign device: ${response.status}`);
      const result = await response.json();
      console.log(`✅ EntityAPI: Device ${deviceId} assigned to entity ${entityId}:`, result);
      return result;
    } catch (error) {
      console.error("❌ EntityAPI: Error assigning device:", error);
      throw error;
    }
  },

  /**
   * Build entity hierarchy from assignments
   * @param {Object} assignments - Entity assignments object
   * @returns {Object} Entity hierarchy mapping
   */
  buildEntityHierarchy(assignments) {
    const hierarchy = {};
    for (const [entityId, assigns] of Object.entries(assignments)) {
      hierarchy[entityId] = assigns.reduce((acc, assign) => {
        acc[assign.x_id_dev] = assign; // Map device to its assignment
        return acc;
      }, {});
    }
    console.log("✅ EntityAPI: Built entity hierarchy:", hierarchy);
    return hierarchy;
  },

  /**
   * Process devices for map display (adds default coordinates)
   * @param {Array} devices - Raw devices array
   * @param {Set} mergedDeviceIds - Set of merged device IDs to filter out
   * @returns {Array} Processed devices for map display
   */
  processDevicesForMap(devices, mergedDeviceIds) {
    return devices
      .filter(device => !mergedDeviceIds.has(device.x_id_dev))
      .map(device => ({
        ...device,
        n_moe_x: device.n_moe_x || Math.random() * 100,
        n_moe_y: device.n_moe_y || Math.random() * 100,
        n_moe_z: device.n_moe_z || 0,
      }));
  },

  /**
   * Process entities for map display (adds default coordinates and assignments)
   * @param {Array} entities - Raw entities array
   * @param {Object} assignments - Entity assignments
   * @returns {Array} Processed entities for map display
   */
  processEntitiesForMap(entities, assignments) {
    return entities.map(entity => ({
      ...entity,
      x: entity.x || Math.random() * 100 + 50,
      y: entity.y || Math.random() * 100 + 50,
      z: entity.z || 0,
      devices: assignments[entity.x_id_ent] || [],
    }));
  }
};

export default EntityAPI;